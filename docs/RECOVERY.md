# Back up and recover the portal

**Terms used here:** A managed identity lets an Azure service request access without storing a password in the application.

Backstage saves its own information in PostgreSQL, separately from the employee application’s Azure SQL database. Recovery needs a database backup, the published handbook, protected credentials, the approved-engineer list, HTTPS certificate data and the correct application version and settings. Keep these items protected and recover each through its approved process.

The actual `backup-session.sh` allows only one backup at a time. It checks that the portal is running, pauses its server, takes the database backup, then restarts the server only if the operating session is still active. It never starts a session that was already stopped.

`backup-postgres.sh` records a database/table/row inventory, runs pg_dumpall with --no-role-passwords, compresses and checks the dump, records SHA-256 and uploads the dump/checksum/inventory with AzCopy managed identity and overwrite=false. Backups may still contain sensitive plugin/auth data even without role-password hashes. Azure storage encryption and strict access matter; these scripts are not the separate envelope-encryption wrapper.

`check-restore.sh` validates the checksum, restores to a disposable --network none PostgreSQL container and can compare the expected inventory. Its temporary trust authentication belongs only to that isolated rehearsal container. Never use it to weaken the live database. Real dump and secret material must not enter this repository.

`backup-techdocs.sh` archives a specific publication, downloads it and verifies file hashes after safe extraction. Credentials, private roster and TLS state recover separately through a protected process; their contents are not included here.

The selected backup destination has Shared Key disabled, no public containers, default-deny network rules restricted to the VM subnet, versioning, 14-day blob/container soft deletion and lifecycle expiry of base dumps after 90 days/versions after 14 days. These are copied configuration values, not a fresh cloud-policy readback. Lifecycle and soft deletion have different effects on recoverability and cost.

The timer starts only with an active stack, first after 30 minutes then every four hours. It is nonpersistent and does not wake a VM. Actual recovery point depends on the last successful off-host backup; neither the timer interval nor the dump checksum alone guarantees an RPO/RTO.

This portfolio reruns configuration/evaluator checks only. No database dump/upload/restore, host cutover or credential transfer was performed.
