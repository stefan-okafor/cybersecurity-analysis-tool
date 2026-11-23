# Cybersecurity Analysis Tool

A Python cybersecurity project focused on basic vulnerability assessment, authentication log analysis and security issue tracking.

The purpose of this project was to practice identifying potentially insecure network services, reviewing failed login attempts and documenting security findings. I also used the project to work with GitHub feature branches and a Freshworks ticketing workflow.

## Project features

| Tool | What it does |
| --- | --- |
| Vulnerability scanner | Checks five common TCP ports on the local machine and flags open services that may need a security review. |
| Log analyzer | Reviews sample authentication events and identifies IP addresses with repeated failed login attempts. |
| Issue tracking | Documents the Freshworks ticket lifecycle, feature branches, code review and issue resolution. |
| Security guidelines | Documents rules for handling credentials, reviewing changes and tracking commits. |

## Requirements

- Python 3
- A terminal or command prompt

Both scripts use Python's standard library. No additional packages are required.

## Getting started

```bash
git clone https://github.com/stefan-okafor/cybersecurity-analysis-tool.git
cd cybersecurity-analysis-tool
```

### 1. Vulnerability assessment

```bash
python vuln_scanner.py
```

The scanner connects to localhost (127.0.0.1) and checks whether the following TCP ports accept connections.

| Port | Common service | Priority if open |
| --- | --- | --- |
| 21 | FTP | HIGH |
| 22 | SSH | INFO |
| 23 | Telnet | HIGH |
| 80 | HTTP | HIGH |
| 443 | HTTPS | INFO |

FTP, Telnet and HTTP are flagged for review because they can carry unencrypted traffic. SSH and HTTPS are recorded for information.

The script returns a list containing the port, service label and severity for each successful connection. These are basic review priorities, not confirmed vulnerabilities. An open port does not prove which service is running or whether it is vulnerable. An unsuccessful connection also does not always mean the port is closed.

### 2. Authentication log analysis

```bash
python log_analyzer.py
```

The analyzer uses regular expressions to extract IPv4 addresses and login outcomes from sample log entries. It counts failed logins by source IP and flags addresses with three or more failures.

The included sample data contains eight authentication events. One address, 203.0.113.45, has five failed login attempts and is expected to be flagged for investigation.

The script reports the number of log lines processed, the flagged IP addresses and whether further action is required. It uses sample data by default and does not automatically collect live logs, block IP addresses or change firewall rules.

## Project workflow

The project documentation describes a process for managing changes through Freshworks and GitHub:

1. Record the issue and its priority in Freshworks.
2. Work on the change in a feature branch.
3. Reference the ticket in the commit and submit the change for review.
4. Close the ticket after the change has been reviewed and merged.

See [Issue Tracking](ISSUE_TRACKING.md) for the documented workflow and ticket history, and [Security Guidelines](SECURITY_GUIDELINES.md) for the project's version control rules.

## Repository structure

```text
cybersecurity-analysis-tool/
|-- README.md
|-- vuln_scanner.py
|-- log_analyzer.py
|-- ISSUE_TRACKING.md
`-- SECURITY_GUIDELINES.md
```

## Scope and limitations

This is a small security assessment project, not a full vulnerability scanner or a production intrusion detection system. It does not perform CVE matching, service version detection or automated remediation. Repeated authentication failures are an indicator that needs further investigation, not proof of an attack.

Only run security checks against systems you own or have permission to assess. Do not commit real authentication logs, passwords, API keys or private keys.

