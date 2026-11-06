# Selected Backstage VM infrastructure

Actual selected source covers hub network reservations, an optional key-only Ubuntu 24.04 VM with system-assigned identity, HTTPS-only NSG entry, daily shutdown, registry reader limited to the selected image repository and optional identity-authorized Blob backup destination. The bootstrap installs guest tools; it does not start or configure a working portal by itself.

This public root is a curated reference. It changes naming, the bootstrap relative path and default network activation, and narrows the services group to the selected VM profile. It omits the real remote backend, commissioned input file and managed-service/vault alternatives. Never apply these default-Off inputs to the existing live state: they could propose removal of resources managed there.

```bash
terraform init -backend=false -input=false
terraform fmt -check -recursive
terraform validate
terraform test
```

The tests use mocked AzureRM/AzAPI providers, a fictional subscription and a nonfunctional SSH reference string. They do not authenticate, create keys or deploy Azure resources. Two cases check default-Off resources and the selected key-only VM/registry-condition/shutdown constraints.

Backup network access uses default Deny plus the VM subnet's Microsoft.Storage service endpoint. It is not private-endpoint routing. Container-scoped data contributor grants are distinct from network reachability. The optional backup retains the source's 14-day soft deletion and 90-day base-dump lifecycle. No data, grants, DNS or paid resources are commissioned by the portfolio.
