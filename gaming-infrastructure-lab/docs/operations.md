# Linux and daily operations

This is how I would approach the host and container side of the lab. The local demo can also run on Docker Desktop, so Ubuntu is not required for the first walkthrough.

## Ubuntu host preparation

Use an Ubuntu 24.04 VM that belongs to you. Take a VM snapshot before experimenting with firewall rules or SSH settings. Use the official Docker installation guide for Ubuntu to install Docker Engine and the Compose plugin:

https://docs.docker.com/engine/install/ubuntu/

```bash
sudo apt update
apt list --upgradable
sudo apt upgrade
sudo systemctl status docker
docker version
docker compose version
```

Keep the console accessible before changing SSH. Review `ss -tulpn`, `sudo ufw status`, and `sudo sshd -T`. Disable unnecessary services and use SSH keys on a real remote host. Do not disable password authentication until key login has been tested. Do not publish the lab dashboard or MySQL to a public interface.

## Container checks

```bash
docker compose ps
docker compose logs --tail=50 api
docker compose logs --tail=50 db
docker compose logs --tail=20 site-b
docker stats --no-stream
docker compose exec api id
```

If an application stops, check the affected container logs first. Verify the database health, DNS resolution between services, resource usage and the last configuration change. Restart only the affected service when practical.

## Patch and restart procedure

1. Review available updates and the affected service. Record the reason and expected impact.
2. Create a database backup and confirm a rollback path.
3. On the lab host, apply approved OS updates and schedule any required restart. For containers, review upstream image updates before pulling and rebuilding.
4. Check health, heartbeat and application functionality. Run the smoke test before closing the change.

This is a manual change workflow, not an automated fleet patching system.

## Zabbix and Wazuh extension

The local dashboard currently uses its own heartbeat endpoint. In a larger lab I would install Zabbix Agent 2 on each Ubuntu host, monitor CPU, disk, memory and service availability, and add triggers for unreachable hosts and low disk space. I would install Wazuh agents and forward local authentication logs into a Wazuh manager for security monitoring. These integrations have not been deployed here. Follow the official installation guides for the release you choose:

- https://www.zabbix.com/documentation/current/en/manual/installation
- https://documentation.wazuh.com/current/installation-guide/index.html

For DNS problems, check `resolvectl status`, then verify the expected name with `getent hosts <hostname>` before changing DNS. Inside Compose, the API uses service discovery for the database.
