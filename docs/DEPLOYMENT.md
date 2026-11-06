# Build, release and rollback

The implemented Backstage workspace uses its own lockfile and Node/Yarn dependency graph; it is separate from the business frontend. The selected source declares Backstage 1.55.0. Its Dockerfile uses the same digest-pinned Node 24 base in dependency and runtime stages, builds native modules in the dependency stage, copies the prepared backend bundle and starts Node as the nonroot node user. Package managers and native build tooling stay out of the final runtime stage where practical.

The public Dockerfile expects full workspace files: Yarn metadata, the lockfile, app configuration and backend skeleton/bundle archives. This repository is a curated reference, not a complete independently buildable Backstage monorepo. Running docker build on this subset will not create that application. Do not replace missing inputs with unrelated latest packages and call the result the same image.

In the complete source workspace, the controlled sequence is:

```bash
yarn install --immutable
yarn tsc
yarn build:backend
docker build -f packages/backend/Dockerfile -t "$REVIEWED_BUILD_TAG" .
trivy image --severity HIGH,CRITICAL "$REVIEWED_BUILD_TAG"
```

These are command examples for the full workspace, not actions performed for this project. Registry publication and host replacement require the selected image digest, scan evidence, backup and an authorized operating session. Actual vulnerability counts change with source and database; this project does not assert that a historical scan clears current dependencies.

On the reviewed host: validate protected inputs, authenticate registry reads with its existing managed identity, pull the reviewed image references, start only the selected stack and verify HTTPS/sign-in/catalog/handbook. Preserve previous image and configuration identity for rollback. A new source commit, tag or completed build does not establish the deployed binding.

Rollback restores the previous selected image while preserving compatible database and publication state. A database schema migration may require a separately rehearsed recovery plan; changing the image alone cannot reverse every schema change. Capture a backup before upgrade and preserve protected credentials separately.

Default templates remain Off and no writer key is included. No Azure service, image, identity or setting was changed to create this portfolio.
