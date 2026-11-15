# Build your own from scratch: Azure Backstage Developer Portal

Your own local Backstage portal with a catalog component and a TechDocs page you authored.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

## Prerequisites

A Unix-like development environment/WSL, a Node/Yarn release supported by the selected Backstage generator, build tools and Git. The starter is a development portal, not a secured production VM installation. The Docker-based TechDocs configuration below additionally needs a reachable Linux Docker engine; an installed CLI alone is insufficient.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

## Create your project folder

Choose a new folder name. These first commands create a blank project; an optional `git init` gives it its own history. Create parent directories in your editor when a later step introduces a nested file.

```bash
mkdir my-azure-backstage-developer-portal
cd my-azure-backstage-developer-portal
git init
```

Create `.gitignore` before saving credentials or build outputs:

```gitignore
.venv/
node_modules/
.env
.env.*
local.settings.json
credentials.json
token.json
*.pem
*.key
*.tfstate*
*.tfplan
.terraform/
private*/
captures/
backups/
batch.json
reports/
out/
app-config.local.yaml
```

The source/file snippets are a starting implementation you type or paste into the named files. Replace `YOUR_*`, names, regions and addresses only with values from your own lab; do not place real client/employee records in a test project. Keep your terminal in this project root unless a step explicitly changes directory.

Before a first commit, set your own repository-local author with `git config user.name "YOUR_NAME"` and `git config user.email "YOUR_PUBLIC_COMMIT_EMAIL"`. Review `git status --short` and the staged diff before publishing; ignored local files are not a substitute for reviewing what you upload.

## Step 1 — Generate your own portal

**Where:** A parent folder on your workstation.

Run the official Backstage app generator and choose your own app name, such as my-engineering-portal. Record the generator/package versions and keep the generated lockfile.

```bash
npx @backstage/create-app@latest
```

**Check before continuing:** A new application folder is created, independently of this portfolio repository.

## Step 2 — Start and inspect the generated app

**Where:** Your generated portal folder.

Install the generated dependencies with its documented Yarn version, then start it. Open the local URL printed by the process, normally localhost:3000, and confirm the backend is also running.

```bash
cd my-engineering-portal
yarn install
yarn start
```

**Check before continuing:** You can see your own development catalog.

## Step 3 — Define a component you own

**Where:** my-engineering-portal/catalog-info.yaml.

Create a catalog entity with your own owner and service name. The example owner group must also exist in your catalog, or you should replace it with a valid existing owner.

Create **`catalog-info.yaml`** with the following contents:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: my-operations-api
  description: My independently built operations API
  annotations:
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: experimental
  owner: group:default/my-platform-team
```

**Check before continuing:** The component has a meaningful owner, lifecycle and documentation annotation.

## Step 4 — Create the owner and documentation

**Where:** Your portal files.

Create team.yaml below, mkdocs.yml below and docs/index.md with your own service purpose, startup steps and recovery owner. This is operational documentation, not just a link to a repository.

Create **`team.yaml`** with the following contents:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: my-platform-team
spec:
  type: team
  children: []
```

Create **`mkdocs.yml`** with the following contents:

```yaml
site_name: My operations API
nav:
  - Home: index.md
plugins:
  - techdocs-core
```

Create **`docs/index.md`** with the following contents:

```markdown
# My operations API

Owner: my-platform-team

## Start
Record your own startup procedure here.

## Recover
Record the tested recovery procedure and escalation contact.
```

**Check before continuing:** The owner and documentation source exist.

## Step 5 — Register the files and build docs

**Where:** app-config.local.yaml and Backstage catalog.

Merge the file locations and development TechDocs settings below into app-config.local.yaml, replacing the placeholders with absolute paths and retaining other generated settings. Confirm Docker Client and Server are available, stop/restart yarn start after the configuration change, then open your component and its Docs tab.

Create **`app-config.local.yaml (merge into the generated file)`** with the following contents:

```yaml
catalog:
  locations:
    - type: file
      target: /YOUR_ABSOLUTE_PROJECT_PATH/catalog-info.yaml
    - type: file
      target: /YOUR_ABSOLUTE_PROJECT_PATH/team.yaml
techdocs:
  builder: local
  generator:
    runIn: docker
  publisher:
    type: local
```

```bash
docker version
# In the original portal terminal, press Ctrl+C to stop its previous run.
# From your generated app folder, restart it with the merged configuration:
yarn start
```

The generator may pull its TechDocs builder image; record that image/version for your lab. Local builder/publisher settings are a development choice and do not establish hosted access control or durable published-doc storage.

Keep only one catalog key and one techdocs key at the YAML top level; merge their nested settings rather than appending duplicate keys. If configuration parsing fails, correct that file before restarting instead of changing unrelated permissions.

**Check before continuing:** Your component is owned and the handbook page renders; a catalog entry alone is not TechDocs proof.

## Step 6 — Verify boundaries before hosting

**Where:** Your test notes.

Check a missing owner/document path and record the actual error and recovery. Before moving to a VM, separately configure Entra sign-in, restricted engineer access, HTTPS, persistent database, secrets, backup and a tested restore path.

**Check before continuing:** The local portal works and the outstanding production requirements are explicit.

## Step 7 — Close the local build

**Where:** Your terminal.

Stop Yarn with Ctrl+C and retain your app source/lockfile and screenshots of the entity and docs. Keep OAuth credentials, private rosters and environment files out of Git.

**Check before continuing:** You have built your own catalog/documentation portal rather than running another person's checkout.

## Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. The architecture diagram explains the design; record your own results rather than treating it as execution evidence.

## Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

## Official implementation references

- [backstage.io — npx-create-app](https://backstage.io/docs/golden-path/create-app/npx-create-app/)
- [backstage.io — descriptor-format](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [backstage.io — creating-and-publishing](https://backstage.io/docs/features/techdocs/creating-and-publishing/)
- [backstage.io — configuration](https://backstage.io/docs/features/techdocs/configuration/)
- [backstage.io — getting-started](https://backstage.io/docs/features/techdocs/getting-started/)

The walkthrough layout follows the prerequisites → creation/configuration → test → verification → troubleshooting → cleanup pattern of the [Splunk project reference](https://github.com/davidharris6/splunk-siem-log-analysis). Its Splunk-specific settings are not copied into unrelated projects.
