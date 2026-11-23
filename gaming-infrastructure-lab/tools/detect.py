"""Parse timestamped synthetic SSH failures; no blocking or external traffic."""
from collections import defaultdict, deque
from datetime import datetime
import ipaddress
import re

FAILED = re.compile(r"Failed password for (?:invalid user )?\S+ from (\S+) port \d+")

def detect(lines, threshold=5, window_seconds=300):
    """Return one alert per burst of failed logins from an IP in the time window."""
    if threshold < 1 or window_seconds < 1:
        raise ValueError("Positive threshold and window required")
    events = []
    for line in lines:
        match = FAILED.search(line)
        if not match:
            continue
        try:
            stamp = datetime.fromisoformat(line.split()[0].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                continue
            addr = str(ipaddress.ip_address(match.group(1)))
        except (ValueError, IndexError):
            continue
        events.append((stamp.timestamp(), addr))
    events.sort()
    history = defaultdict(deque)
    alerts = []
    for ts, addr in events:
        q = history[addr]
        while q and ts - q[0] > window_seconds:
            q.popleft()
        q.append(ts)
        if len(q) == threshold:
            alerts.append({"source": "Synthetic SSH log", "severity": "high",
                           "summary": f"{threshold} failed SSH logins from {addr} within {window_seconds}s"})
    return alerts
