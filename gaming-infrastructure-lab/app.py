"""Local-only operations dashboard. All incident and store data is simulated."""
import os
from contextlib import contextmanager
from flask import Flask, jsonify, request, send_from_directory
import pymysql
from waitress import serve

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
SITE_NAMES = {"site-a": "Gaming Location A", "site-b": "Gaming Location B"}
SEVERITIES = {"low", "medium", "high", "critical"}
SCHEMA = [
    """CREATE TABLE IF NOT EXISTS sites (
        id VARCHAR(24) PRIMARY KEY, name VARCHAR(80) NOT NULL,
        last_seen DATETIME NULL, detail VARCHAR(120) NOT NULL DEFAULT 'No heartbeat'
    )""",
    """CREATE TABLE IF NOT EXISTS alerts (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(100) NOT NULL, summary VARCHAR(240) NOT NULL,
        severity VARCHAR(10) NOT NULL, state VARCHAR(12) NOT NULL DEFAULT 'open',
        notes TEXT NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS findings (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        asset VARCHAR(100) NOT NULL, summary VARCHAR(240) NOT NULL,
        severity VARCHAR(10) NOT NULL, state VARCHAR(12) NOT NULL DEFAULT 'open',
        remediation TEXT NOT NULL, verification TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )"""
]

@contextmanager
def db():
    connection = pymysql.connect(
        host=os.environ["DB_HOST"], user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"], database=os.environ["DB_NAME"],
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5, read_timeout=10, write_timeout=10,
        init_command="SET time_zone = '+00:00'"
    )
    try:
        with connection.cursor() as cur:
            yield cur
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def initialize():
    with db() as cur:
        for stmt in SCHEMA:
            cur.execute(stmt)
        for site_id, name in SITE_NAMES.items():
            cur.execute("INSERT IGNORE INTO sites (id,name) VALUES (%s,%s)", (site_id,name))

def payload():
    obj = request.get_json(silent=True)
    if not isinstance(obj, dict):
        raise ValueError("JSON object required")
    return obj

def field(obj, key, length):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > length:
        raise ValueError(f"{key} must be non-empty text up to {length} characters")
    return value.strip()

def severity(obj):
    val = field(obj, "severity", 10)
    if val not in SEVERITIES:
        raise ValueError("Invalid severity")
    return val

@app.errorhandler(ValueError)
def bad_input(exc):
    return jsonify(error=str(exc)), 400

@app.errorhandler(pymysql.MySQLError)
def database_error(exc):
    app.logger.error("Database operation failed: %s", type(exc).__name__)
    return jsonify(error="Database temporarily unavailable"), 503

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/health")
def health():
    with db() as cur:
        cur.execute("SELECT 1")
    return jsonify(status="ok")

@app.get("/api/status")
def status():
    with db() as cur:
        cur.execute("""SELECT id,name,detail,last_seen,
            TIMESTAMPDIFF(SECOND,last_seen,UTC_TIMESTAMP()) AS age_seconds
            FROM sites ORDER BY id""")
        sites = cur.fetchall()
        for site in sites:
            age = site["age_seconds"]
            site["status"] = "online" if age is not None and 0 <= age <= 20 else "offline"
            site["last_seen"] = site["last_seen"].isoformat() + "Z" if site["last_seen"] else None
        cur.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")
        alerts = cur.fetchall()
        cur.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 100")
        findings = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS n FROM alerts WHERE state <> 'closed'")
        open_alerts = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM findings WHERE state <> 'verified'")
        open_findings = cur.fetchone()["n"]
    for row in alerts + findings:
        row["created_at"] = row["created_at"].isoformat() + "Z"
    return jsonify(sites=sites, alerts=alerts, findings=findings,
                   open_alerts=open_alerts, open_findings=open_findings, simulated=True)

@app.post("/api/heartbeat")
def heartbeat():
    obj = payload()
    site = field(obj, "site_id", 24)
    detail = field(obj, "detail", 120)
    if site not in SITE_NAMES:
        raise ValueError("Unknown site")
    with db() as cur:
        cur.execute("UPDATE sites SET last_seen=UTC_TIMESTAMP(), detail=%s WHERE id=%s", (detail,site))
    return jsonify(status="accepted")

@app.post("/api/alerts")
def create_alert():
    obj = payload()
    values = (field(obj,"source",100), field(obj,"summary",240), severity(obj), "open", "")
    with db() as cur:
        cur.execute("INSERT INTO alerts (source,summary,severity,state,notes) VALUES (%s,%s,%s,%s,%s)", values)
        item = cur.lastrowid
    return jsonify(id=item), 201

@app.patch("/api/alerts/<int:item>")
def triage(item):
    obj = payload()
    state = field(obj,"state",12)
    notes = field(obj,"notes",2000)
    with db() as cur:
        cur.execute("SELECT state,severity,notes FROM alerts WHERE id=%s FOR UPDATE", (item,))
        row = cur.fetchone()
        if not row:
            return jsonify(error="Alert not found"), 404
        if (row["state"], state) not in {("open","triaged"),("triaged","closed")}:
            raise ValueError("Use open -> triaged -> closed")
        level = severity(obj) if "severity" in obj else row["severity"]
        history = (row["notes"] + "\n" if row["notes"] else "") + f"{state} ({level}): {notes}"
        cur.execute("UPDATE alerts SET state=%s,severity=%s,notes=%s WHERE id=%s",(state,level,history,item))
    return jsonify(status=state)

@app.post("/api/findings")
def create_finding():
    obj = payload()
    vals = (field(obj,"asset",100), field(obj,"summary",240), severity(obj),"open","","")
    with db() as cur:
        cur.execute("INSERT INTO findings (asset,summary,severity,state,remediation,verification) VALUES (%s,%s,%s,%s,%s,%s)",vals)
        item = cur.lastrowid
    return jsonify(id=item),201

@app.patch("/api/findings/<int:item>")
def update_finding(item):
    obj = payload()
    state = field(obj,"state",12)
    with db() as cur:
        cur.execute("SELECT state FROM findings WHERE id=%s FOR UPDATE",(item,))
        row = cur.fetchone()
        if not row:
            return jsonify(error="Finding not found"),404
        if row["state"] == "open" and state == "remediated":
            cur.execute("UPDATE findings SET state=%s,remediation=%s WHERE id=%s",
                        (state,field(obj,"remediation",2000),item))
        elif row["state"] == "remediated" and state == "verified":
            cur.execute("UPDATE findings SET state=%s,verification=%s WHERE id=%s",
                        (state,field(obj,"verification",2000),item))
        else:
            raise ValueError("Use open -> remediated -> verified")
    return jsonify(status=state)

if __name__ == "__main__":
    initialize()
    serve(app, host="0.0.0.0", port=8080, threads=4)
