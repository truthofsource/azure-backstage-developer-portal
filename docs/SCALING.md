# Strengths, weaknesses and scaling tradeoffs

| Choice | Strength | Weakness / tradeoff |
| --- | --- | --- |
| Backstage catalog + TechDocs | One discovery path across services, owners and operating guidance | Metadata and documentation publication require ownership and maintenance |
| Single VM / Compose | Small, understandable on-demand footprint | Single group of components that can fail together, OS/container patching and interrupted access when deallocated |
| Two Entra layers | Admission and backend identity decisions remain separate | More redirects, sessions and configuration to operate |
| Read-only handbook mount | Serving backend cannot rewrite the publication | Requires an external publication/rollback process |
| Evidence states | Refuses false deployment certainty | Missing source evidence produces Unknown and needs follow-up |
| Quiesced database backup | Reduces inconsistent plugin writes during dump | Brief backend outage; cadence depends on active sessions |
| Managed-identity backup | Avoids account-key/SAS distribution | Identity scope and subnet reachability must both work |

Measure concurrent engineers, catalog ingestion/search latency, PostgreSQL I/O/size, backend memory, documentation fetch latency, backup duration and restore time before increasing capacity. A larger VM can relieve measured pressure but retains the group of components that can fail together.

At sustained usage, evaluate managed PostgreSQL, multiple backend instances and external controlled TechDocs storage. Coordinate plugin migrations, session/signing keys, durable task handling, catalog synchronization and database connection limits. Review proxy/SSO behavior under a load balancer and test denied access and recovery again. The source's managed alternatives are design options, not commissioned capacity.

Separate growth in service metadata from growth in employee/business records: the engineering portal should not become a duplicate HR database. Keep reader/writer identities and new plugin permissions narrowly scoped.

Estimate compute runtime, disks, static IP, registry, backup versions/retention, logging and network costs. Deallocation saves compute but retains other charges. RPO follows actual successful backups; RTO must come from a timed restore and sign-in rehearsal, not an architecture diagram.
