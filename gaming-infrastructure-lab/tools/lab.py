"""Local lab helper. Never run these commands against a production database."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import urllib.request
from datetime import datetime, timezone
from uuid import uuid4
from detect import detect

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
BACKUPS = ROOT / "backups"
TABLES = ("sites", "alerts", "findings")
BASE = "http://127.0.0.1:8080"

def compose(*args, input_bytes=None):
    return subprocess.run(["docker","compose",*args],cwd=ROOT,input=input_bytes,
                          stdout=subprocess.PIPE,check=True).stdout

def root_sql(sql):
    return compose("exec","-T","db","sh","-c",
        'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql -uroot -N -B -e "$1"',
        "mysql",sql).decode().strip()

def initialize():
    try:
        with ENV.open("x", encoding="utf-8") as handle:
            handle.write("MYSQL_PASSWORD=" + secrets.token_hex(24) + "\nMYSQL_ROOT_PASSWORD=" + secrets.token_hex(32) + "\n")
        print("Created .env with local random passwords")
    except FileExistsError:
        print(".env already exists; did not replace it")

def api(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(BASE + path, data=body, method=method,
                                 headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)

def demo():
    events = detect((ROOT/"tools/fixtures/auth.log").read_text().splitlines())
    for event in events:
        print("Added alert:", api("/api/alerts","POST",event)["id"])
    print("Added sample finding:",api("/api/findings","POST",{
        "asset":"lab-ubuntu (simulated)","summary":"Sample finding: pending package security update",
        "severity":"medium"})["id"])
    print("Sample records only. No scanner or containment action was executed.")

def backup():
    BACKUPS.mkdir(exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target=BACKUPS/f"gaming-{stamp}-{uuid4().hex[:6]}.sql"
    dump=compose("exec","-T","db","sh","-c",
        'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysqldump -uroot --single-transaction --no-tablespaces --set-gtid-purged=OFF gaming')
    if not dump.strip():
        raise RuntimeError("Empty backup")
    target.write_bytes(dump)
    target.with_suffix(".sha256").write_text(hashlib.sha256(dump).hexdigest()+"\n")
    print(target.relative_to(ROOT))
    return target

def counts(database):
    return {table:int(root_sql(f"SELECT COUNT(*) FROM {database}.{table}")) for table in TABLES}

def restore_check(path):
    target=Path(path)
    if not target.is_absolute():
        target=ROOT/target
    if target.resolve().parent != BACKUPS.resolve() or target.suffix != ".sql":
        raise ValueError("Use a backup generated in the lab backups directory")
    dump=target.read_bytes()
    expected=target.with_suffix(".sha256").read_text().strip()
    if hashlib.sha256(dump).hexdigest()!=expected:
        raise ValueError("Backup checksum mismatch")
    name="gaming_restore_"+uuid4().hex[:12]
    root_sql(f"CREATE DATABASE {name}")
    try:
        compose("exec","-T","db","sh","-c",
            'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql -uroot "$1"',
            "mysql", name, input_bytes=dump)
        restored=counts(name)
        live=counts("gaming")
        print("Restored table counts:",restored)
        print("Current source counts:",live)
        if restored!=live:
            raise RuntimeError("Counts differ; retry from a fresh backup with records unchanged")
        print("PASS: backup checksum, restore and expected table counts")
    finally:
        root_sql(f"DROP DATABASE {name}")

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="command",required=True)
    for cmd in ("init","demo","backup"):
        sub.add_parser(cmd)
    sub.add_parser("restore-check").add_argument("file")
    args=parser.parse_args()
    if args.command=="restore-check":
        restore_check(args.file)
    else:
        {"init":initialize,"demo":demo,"backup":backup}[args.command]()

if __name__=="__main__":
    main()
