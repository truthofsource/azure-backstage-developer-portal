# Engineering Strengths and Practical Value

The value of this Backstage implementation comes from joining useful engineering information with controlled access and recoverable operations. The public project includes actual implementation source, a fictional local viewer and clearly bounded tests. Those evidence types support different claims.

## 1. Ownership is part of service discovery

A component entry identifies its owner and dependencies, rather than offering only a bookmark. An engineer investigating a worker can move from that component to the surrounding API, identity, storage and operational context. This helps route questions and plan changes without guessing who owns the affected system.

The public catalog contains 16 entities. Its checks cover valid Location targets, unique references and component ownership. Entries still require review and maintenance; catalog metadata does not grant access or prove live health.

**Evidence:** [actual catalog](../catalog/), [catalog checks](../tests/test_catalog.py), [catalog and handbook guide](CATALOG-AND-TECHDOCS.md).

## 2. The handbook has a controlled publication path

TechDocs places operating guidance beside the service catalog. The actual VM profile serves externally built documentation through a read-only mount. This keeps document generation separate from the serving process and gives publication its own version and rollback boundary.

The handbook backup identifies one publication, retrieves the archive again and checks file hashes. That is stronger than assuming an upload completed correctly. The public repository does not include the private handbook or prove a fresh hosted publication.

**Evidence:** [production configuration](../reference/config/app-config.production.yaml), [TechDocs backup](../runtime/vm/backup-techdocs.sh).

## 3. Admission, identity and permissions are separate controls

The HTTPS edge delegates admission to OAuth2 Proxy and an engineering-group gate. Backstage uses a different Entra application to map the signed-in user to a known catalog identity. The hosted permission policy then checks approved engineer references and permitted operations.

Approved reads do not become general catalog-write or deployment permission. Software-template actions require an explicit switch, listed maintainer, approved action IDs and own-task conditions. A separate writer identity/key is absent from default mounts. This limits what an ordinary portal session can do, while keeping a reviewed extension path available.

More identity layers also mean more configuration and sessions to operate. These controls must be checked together in a real sign-in test; the offline viewer does not enforce or emulate them.

**Evidence:** [identity guide](IDENTITY.md), [permission policy](../reference/backend/permissionPolicy.ts), [default Compose](../runtime/vm/compose.yaml), [optional writer overlay](../runtime/vm/compose.templates.yaml).

## 4. Release information says what the evidence actually proves

The evaluator compares a selected source and artifact, the publication receipt from that run and a fresh observation of what is currently deployed. This makes the portal useful during release and rollback work: engineers can distinguish “the build passed” from “this artifact is running.”

Its four states preserve uncertainty. Verified requires agreement; Unknown means evidence is insufficient; Conflict identifies disagreement; Stale means the observation is too old. Nine original evaluator tests and the local demonstration exercise these decisions. The evaluator itself does not authenticate or fetch evidence; its trusted reader must do that separately.

**Evidence:** [release guide](RELEASE-EVIDENCE.md), [evaluator](../reference/releases/evaluate.py), [tests](../reference/releases/test_evaluate.py).

## 5. Backups lead toward a testable recovery process

The session wrapper allows one backup at a time and pauses backend writes during the database dump. The database helper records an inventory and checksum, uploads through managed identity and refuses to overwrite the retained object. The restore helper checks the checksum and can compare the inventory inside a disposable PostgreSQL container with no network.

Handbook publications have a separate archive verification path. Credentials, the private engineer roster and TLS state must be recovered through their protected process. Keeping those dependencies explicit is essential: a database dump alone is not a recovered portal.

This public project checked code and configuration; it did not create a new backup, perform a live restore or measure RTO/RPO. Consistent backups require a brief backend pause, and actual recovery points depend on successful off-host copies.

**Evidence:** [recovery guide](RECOVERY.md), [session wrapper](../runtime/vm/backup-session.sh), [database backup](../runtime/vm/backup-postgres.sh), [isolated restore helper](../runtime/vm/check-restore.sh).

## 6. Startup catches avoidable configuration mistakes

The runtime checks selected image digests, distinct identity applications and protected input files before starting the stack. PostgreSQL has no published host port, and only the HTTPS edge exposes a port. The VM identity pulls approved images and writes backups without distributing a storage account key.

These are specific controls, not a complete security certification. A pinned image still needs current vulnerability review, protected files still need secret lifecycle management, and private container networks do not remove every host-level risk.

**Evidence:** [preflight](../runtime/vm/preflight.py), [Compose contract](../runtime/vm/check-compose.py), [architecture](ARCHITECTURE.md), [deployment](DEPLOYMENT.md).

## 7. Cost controls fit the usage pattern

A single VM and Compose stack provide an understandable footprint for intentional engineering sessions. The backup timer runs only during an active stack and does not wake the VM. The operating procedure ends with backup, stop and deallocation.

Deallocation stops compute billing while disks, static IP, registry and backup storage can still cost money. The VM remains one failure domain. Sustained use may justify managed PostgreSQL, external TechDocs storage and multiple backends after measuring demand and rehearsing the resulting access/recovery paths.

**Evidence:** [operations](OPERATIONS.md), [backup timer](../runtime/vm/backstage-backup.timer.example), [Terraform](../infra/README.md), [growth and tradeoffs](SCALING.md).

## What this demonstrates

The project shows platform engineering beyond installing a portal: service ownership, usable operating guidance, separate identity boundaries, cautious release information, deliberate recovery and a usage-based operating model. The implementation remains honest about its single-VM limits and the difference between source tests, local reference screenshots and live acceptance.
