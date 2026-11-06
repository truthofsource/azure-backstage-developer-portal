# Build, release and rollback

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. A managed identity lets an Azure service request access without storing a password in the application.

Backstage has its own recorded package versions, separate from the employee website. The selected source uses Backstage 1.55.0. The container build uses the same exact Node 24 base for preparation and the final application. It builds operating-system-specific packages during preparation, copies the finished server and runs it as the lower-permission node user. Build tools are kept out of the final container where practical.

The Dockerfile needs the complete application files, its recorded package versions, settings and prepared server archives. This public project contains selected examples rather than the full Backstage application. Building only these files will not produce that application. Using unrelated newer packages would produce a different build.

In the complete source workspace, the controlled sequence is:

```bash
yarn install --immutable
yarn tsc
yarn build:backend
docker build -f packages/backend/Dockerfile -t "$REVIEWED_BUILD_TAG" .
trivy image --severity HIGH,CRITICAL "$REVIEWED_BUILD_TAG"
```

These commands show how the complete application is built; they were not run for this project. A real image release needs the exact build fingerprint, scan results, a backup and permission to update the server. Findings change as software and scanner data change, so an old scan does not clear today’s packages.

On the approved server, check the protected settings, use its Azure service identity to download the selected images, and start the intended services. Then check HTTPS, sign-in, the service list and the handbook. Save the previous image and settings for recovery. A new code commit, image label or successful build does not prove that the server is running it.

Rollback restores the previous selected image while preserving compatible database and publication state. A database schema migration may require a separately rehearsed recovery plan; changing the image alone cannot reverse every schema change. Capture a backup before upgrade and preserve protected credentials separately.

Default templates remain Off and no writer key is included. No Azure service, image, identity or setting was changed to create this portfolio.
