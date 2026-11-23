"""A simulated gaming location reports a heartbeat every five seconds."""
import json
import os
import time
import urllib.request

while True:
    body = json.dumps({"site_id": os.environ["SITE_ID"],
                       "detail": "Simulated game service heartbeat"}).encode()
    req = urllib.request.Request("http://api:8080/api/heartbeat", data=body,
                                headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            print(os.environ["SITE_ID"], response.status, flush=True)
    except OSError as exc:
        print("Heartbeat failed:", type(exc).__name__, flush=True)
    time.sleep(5)
