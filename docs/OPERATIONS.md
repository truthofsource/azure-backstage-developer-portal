# Operations and troubleshooting

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version.

## Intentional engineering session

Start the reviewed VM deliberately, validate protected inputs, pull image references tied to exact builds, start the stack and verify the engineer's actual catalog/handbook access. At closeout, run the backup procedure, stop the stack and verify VM deallocation. Do not confuse an OS shutdown with Azure deallocation. The daily shutdown schedule does not start the VM, make the service highly available or eliminate disk/IP/registry/storage charges.

## Troubleshooting

| Symptom | Check first | Meaning |
| --- | --- | --- |
| Site unavailable | VM power, stack status, edge 443 and certificate | A deallocated engineering portal can be intentional |
| Sign-in loops | Ingress and backend redirect URIs, separate app IDs and cookie state | Two identity layers can fail independently |
| Signed in but denied | Entra assignment/group, exact catalog User annotation and approved engineer ref | Catalog ownership is not permission |
| Empty catalog | Registered Location targets, reader installation scope and backend ingestion errors | A Git link alone does not register an entity |
| Handbook not found | Published entity path, safe symlink/publication layout, current file hashes | Source merge is not hosted publication |
| Release Unknown | Authenticated run, same-run receipt and check of the currently saved result | Do not guess from the latest successful build |
| Release Conflict | Source/digest/target/run binding | Preserve evidence; do not replace it with a green label |
| Backend native-module error | Build/runtime Node and Linux ABI; selected lockfile | A host-built Windows module is not a Linux runtime module |
| Backup timer silent | Active stack, timer state and last success | It never starts a stopped VM |
| Restore differs | Dump/checksum/inventory/image identity and credential recreation | A downloaded file is not a successful recovery |

## ClickOps reference

Use Azure Portal → Virtual machines → the reviewed engineering host to inspect power state, Networking/NSG and Identity. Use the shared registry's repository view to compare selected digests, not tags alone. On the exact backup account, inspect Networking, Containers, Data protection and IAM at the intended scope. These are navigation examples; do not change cloud settings for this local reference.

Use Entra App registrations and Enterprise applications to inspect the two redirect/application roles and engineering assignment. Do not paste secrets, employee records or private roster entries into screenshots. In the portal itself, verify catalog, Docs and release observation times separately. Read-only inspections are different from template execution or host deployment.
