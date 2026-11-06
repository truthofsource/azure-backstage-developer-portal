# Catalog and engineering handbook

The catalog describes the system, API/frontend, workers, identity, storage, SQL and observability resources. A Location points to individual entities. Components name owners and dependencies so an engineer can move from a service to its operating context. Metadata is maintained in source and must be reviewed; a catalog entry does not query live health.

The copied catalog uses JSON-compatible YAML to keep the offline inspector dependency-free. Its source links use an example platform repository, not a promise that those paths exist publicly. The public seed omits the private handbook entity because the corresponding private documentation tree is not published here. No employee User roster is included.

The real VM profile sets TechDocs builder to external and publisher to local. A separate publication process builds the handbook and serves it through a read-only persistent mount. Publication source identity and file hashes matter: a documentation commit is not proof that the serving host has it. Safe publication directories and retained immutable versions support rollback.

The backup helper archives one exact source publication, downloads it again and checks archive and individual file hashes. Protected secrets and the private roster are not bundled into that handbook archive.

For larger usage, Backstage recommends building documentation in CI and storing generated output in controlled external storage. This is a possible evolution of the VM profile, not a claim that its optional Azure storage/private endpoint is deployed. [Official TechDocs architecture](https://backstage.io/docs/features/techdocs/architecture/).
