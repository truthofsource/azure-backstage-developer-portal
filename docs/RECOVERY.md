# Back up and recover the portal

Backstage plugin state lives in PostgreSQL, not the workforce application's Azure SQL database. Recovery needs a consistent database snapshot, published TechDocs, protected runtime credentials, the private engineer roster, TLS state and reviewed image/configuration identities. They have different confidentiality and recovery paths.

The actual `backup-session.sh` takes a nonblocking flock, checks that the session and backend are already running, stops only the backend, runs the database backup and conditionally resumes the backend in an EXIT trap if the session remains active. It never starts a stopped session.

`backup-postgres.sh` records a database/table/row inventory, runs pg_dumpall with --no-role-passwords, compresses and checks the dump, records SHA-256 and uploads the dump/checksum/inventory with AzCopy managed identity and overwrite=false. Backups may still contain sensitive plugin/auth data even without role-password hashes. Azure storage encryption and strict access matter; these scripts are not the separate envelope-encryption wrapper.

`check-restore.sh` validates the checksum, restores to a disposable --network none PostgreSQL container and can compare the expected inventory. Its temporary trust authentication belongs only to that isolated rehearsal container. Never use it to weaken the live database. Real dump and secret material must not enter this repository.

`backup-techdocs.sh` archives a specific publication, downloads it and verifies file hashes after safe extraction. Credentials, private roster and TLS state recover separately through a protected process; their contents are not included here.

The selected backup destination has Shared Key disabled, no public containers, default-deny network rules restricted to the VM subnet, versioning, 14-day blob/container soft deletion and lifecycle expiry of base dumps after 90 days/versions after 14 days. These are copied configuration values, not a fresh cloud-policy readback. Lifecycle and soft deletion have different effects on recoverability and cost.

The timer starts only with an active stack, first after 30 minutes then every four hours. It is nonpersistent and does not wake a VM. Actual recovery point depends on the last successful off-host backup; neither the timer interval nor the dump checksum alone guarantees an RPO/RTO.

This portfolio reruns configuration/evaluator checks only. No database dump/upload/restore, host cutover or credential transfer was performed.
