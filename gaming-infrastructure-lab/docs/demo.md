# Demo checklist

This document is for collecting real evidence after starting the lab. I would keep the demo short and focus on what I can explain without reading a script.

| Evidence | What to capture | Result |
| --- | --- | --- |
| Deployment | docker compose ps and dashboard showing two sites | Not recorded |
| Availability | Location B offline after stopping the agent, then online after restart | Not recorded |
| Security | Sample SSH alert, triage notes and closure | Not recorded |
| Vulnerability | Actual Trivy output, change record and rescan | Not recorded |
| Recovery | Backup command and restore-check output | Not recorded |
| AWS | Terraform validate/plan if run, with sensitive data removed | Not recorded |

Automated check results belong in GitHub Actions. Screenshots should come from the actual running environment, not a mockup. Do not include credentials, public IP addresses, cloud account IDs, employer information or real security logs.

## Three-minute walkthrough

Start by showing the architecture and explaining what is local versus optional cloud infrastructure. Show the two sites, stop one, and explain why stale heartbeats are a useful operational signal. Next, walk through the sample SSH incident and the finding lifecycle. Finish by showing the database restore result and explaining what it does and does not verify.

Before presenting the project in an interview, run each step yourself and be ready to explain the configuration, the code and what you would change for a real multi-site business.
