"""Integration test. Requires the local Compose environment."""
import time
from urllib.error import HTTPError
from lab import api, backup, restore_check
from detect import detect
from pathlib import Path

def wait_online():
    for _ in range(30):
        try:
            data=api("/api/status")
            if len(data["sites"])==2 and all(s["status"]=="online" for s in data["sites"]):
                return
        except OSError:
            pass
        time.sleep(2)
    raise RuntimeError("Locations did not come online")

def run():
    assert api("/api/health")["status"]=="ok"
    wait_online()
    fixture=Path(__file__).parent/"fixtures/auth.log"
    events=detect(fixture.read_text().splitlines())
    assert len(events)==1
    alert=api("/api/alerts","POST",events[0])["id"]
    api(f"/api/alerts/{alert}","PATCH",{"state":"triaged","severity":"high",
        "notes":"Synthetic test. Would verify the source and escalate to the system owner."})
    api(f"/api/alerts/{alert}","PATCH",{"state":"closed","notes":"Synthetic exercise complete."})
    finding=api("/api/findings","POST",{"asset":"smoke-test","summary":"Sample update","severity":"medium"})["id"]
    try:
        api(f"/api/findings/{finding}","PATCH",{"state":"verified","verification":"invalid shortcut"})
    except HTTPError as exc:
        assert exc.code==400
    else:
        raise AssertionError("Unexpected verification before remediation")
    api(f"/api/findings/{finding}","PATCH",{"state":"remediated","remediation":"Synthetic change record"})
    api(f"/api/findings/{finding}","PATCH",{"state":"verified","verification":"Synthetic rescan record"})
    data=api("/api/status")
    assert next(a for a in data["alerts"] if a["id"]==alert)["state"]=="closed"
    assert next(a for a in data["findings"] if a["id"]==finding)["state"]=="verified"
    restore_check(backup())
    print("PASS: health, heartbeat, alert state transitions, finding verification and database restore")

if __name__=="__main__":
    run()
