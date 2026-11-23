# Security operations

The goal is to work an alert from the first notification through investigation, escalation and closure. All records used by the dashboard are synthetic. The detector reads only the sample log and does not block addresses or touch firewall rules.

## SSH alert exercise

Run `python tools/lab.py demo`. The detector looks for five failed SSH password attempts from the same address within five minutes. The address in the fixture is reserved for documentation. It raises a high-severity sample alert. The threshold is a simple starting point and is not a full intrusion detection system.

In the dashboard, open the alert and record:
- What happened and which asset or account may be affected.
- Whether the evidence indicates repeated failures, a successful login, or another possible cause.
- The assessed severity, the first containment decision and who owns the system.

For a real incident I would preserve relevant logs, confirm the source, identify affected accounts, notify the system owner and follow the approved containment process. I would avoid blocking addresses or disabling accounts without checking potential service impact and authorization. Close the sample alert after documenting the outcome.

A real Ubuntu authentication investigation might use `sudo journalctl -u ssh --since "1 hour ago"` or the available authentication log. Do not copy actual account names, IP addresses or corporate logs into this public repository.

## Vulnerability workflow

1. Find the affected package, image or asset and record the severity and source.
2. Check whether the vulnerability applies to the running version and whether the service is reachable.
3. Plan a patch or configuration change, back up data and establish a rollback path.
4. Apply the approved change and record what changed.
5. Rescan or otherwise verify that the finding was resolved before marking it verified.

The dashboard enforces the sequence open, remediated, verified. The sample finding is a workflow demonstration, not evidence of a real scan.

## Optional Trivy image scan

Install Trivy from its official guide: https://trivy.dev/latest/getting-started/installation/

```bash
docker compose build api
docker compose images
trivy image --severity HIGH,CRITICAL mysql:8.4
```

Use the actual API image listed by Compose for an additional scan. Record real scanner output locally, including the image digest, scan date, CVE, severity and fixed version if available. Do not report the scan as clean unless the output supports it. Update the image, rebuild and rescan to verify remediation.

## Access review

Review users and privileges for the application database, the host and AWS IAM separately. The application account is not the MySQL root account. The database is not exposed to the host network. The local API has no user authentication, so it must remain localhost-only and must not be deployed as a public service. Production use would require authentication, authorization, TLS, audit logging, secrets management and alert integrations.

Microsoft 365 Defender and Purview alerts are not connected here. The same triage process can be adapted to those sources using approved enterprise tooling.
