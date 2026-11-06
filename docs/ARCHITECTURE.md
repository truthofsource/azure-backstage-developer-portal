# Architecture and placement

**Terms used here:** A private endpoint gives a supported service an address on a private network; access permissions still apply.

The implemented developer portal is an engineering service, separate from the workforce business platform. A hub-hosted Azure Linux VM runs four services locked to exact container builds: Caddy, OAuth2 Proxy, Backstage and PostgreSQL. The Azure NSG publishes HTTPS 443; the Compose database network is internal and has no database host-port mapping.

| Boundary | Implementation | Does not imply |
| --- | --- | --- |
| Edge | Trusted TLS at Caddy, forward authentication at OAuth2 Proxy | Direct anonymous backend access |
| Human identity | Separate ingress/backend Entra applications and catalog User identity mapping | Business employee access to engineering tooling |
| Portal data | PostgreSQL plugin databases on persistent host volume | The business application's Azure SQL database |
| Handbook | Externally built TechDocs, read-only publication mount | Building arbitrary documentation in the serving container |
| Registry | VM service identity with read access limited to the selected image repository | Registry-wide push or repository writer |
| Backups | Managed-identity Blob access; subnet service endpoint, default Deny | Private endpoint or encrypted client-side archive wrapper |

The selected Terraform retains hub VNet reservations that originated with alternative Container Apps/PostgreSQL plans. Those delegated subnets do not create managed services. The public root omits managed-service/vault resources and makes network/VM/backup activation default Off. The live adopted root must keep its actual commissioned inputs; never substitute this example root into its state.

The runtime Compose definition is operational source. The offline viewer is a separate Python/HTML reference and does not enforce or emulate Backstage authentication. It never starts the Compose services.
