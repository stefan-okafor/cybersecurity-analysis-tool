# Backup and recovery

The database backup is a logical MySQL dump. The script stores it locally along with a SHA-256 checksum. No credentials or backups are committed to GitHub.

## Backup

```bash
python tools/lab.py backup
```

The script prints the path to the SQL file inside backups/. Keep the database volume in place. For a production backup strategy I would also consider encryption, access restrictions, off-site copies, retention, point-in-time recovery and scheduled restore exercises.

## Verify a restore

```bash
python tools/lab.py restore-check backups/<filename>.sql
```

Use the actual filename from the backup command. Keep alert and finding records unchanged during the backup/restore check. The script validates the saved checksum, creates a disposable MySQL database with a random lab-specific name, imports the dump, compares table counts, and removes the disposable database afterward. The live gaming database is not dropped or overwritten.

Matching counts do not prove every value is correct. A production restore exercise should also compare selected records, run application acceptance tests, record elapsed time and check the recovery objectives.

## Availability exercise

Stop only one heartbeat agent with `docker compose stop site-b`. Check that the dashboard marks it offline after its heartbeat becomes stale. Start it with `docker compose start site-b` and verify that it returns to online.

## Recovery targets

For this lab, the proposed target is a recovery within 15 minutes and a backup no older than 24 hours. These are design targets, not measured results. Record actual backup/restore duration and test outcomes before reporting that the targets were achieved.
