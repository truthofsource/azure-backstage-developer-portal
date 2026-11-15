# Backstage Developer Portal on Azure

**Give engineers one place to find systems, their owners, operating instructions and release information.**

[Business problem](#the-business-problem) · [Solution](#the-solution) · [Engineering strengths](#engineering-strengths) · [What was built](#what-was-built) · [Proof it works](#proof-it-works) · [Commands](docs/COMMANDS.md) · [Step by step](#step-by-step)

![Local catalog reference](docs/images/01-catalog.png)

## The Business Problem

Operating the platform involves more than its employee-facing website. Engineers also need to understand background workers, storage, integrations, deployment records and recovery procedures. When that information is spread across repository folders and operating notes, answering a basic question such as who owns a service can require several searches.

That becomes more costly during an incident or handoff: the operator needs the correct instructions and release evidence while the affected service may already be unavailable. Outdated or hard-to-find guidance can lead to a wrong recovery step. The engineering portal itself also holds operational information and needs protected access and a recoverable configuration.

The business need was one engineering entry point connecting services to their owners, handbook pages and release records, with its own access and recovery boundaries.

## The Solution

I built an internal engineering portal using Backstage. It brings together a service directory, an engineering handbook and release information. Approved engineers sign in through Microsoft.

**Business outcome:** Engineers can move from a system's name to its owner, instructions and release records in one place. The portal runs separately from the employee application and has its own backup and access controls.

## Tools Used and What They Do

| Tool or service | What it does | Where it fits |
| --- | --- | --- |
| Backstage and TechDocs | Provide the service catalog and engineering handbook. | Actual engineering portal; the Python preview is a separate offline example. |
| Docker Compose | Run the portal and its supporting services together. | Actual VM stack definition, not started by the local viewer. |
| Caddy | Serve HTTPS at the front of the portal. | Actual ingress service. |
| OAuth2 Proxy and Microsoft Entra ID | Check ingress sign-in and map the engineer to an approved identity. | Ingress and Backstage identity checks are separate layers. |
| PostgreSQL | Keep portal/plugin data on persistent storage. | Actual portal database; distinct from the business application’s Azure SQL. |
| GitHub Apps | Read approved catalog/release sources and keep proposal-writing authority separate. | Actual scoped integrations; repository read access is not repository write access. |
| Yarn and Corepack | Select the package manager used when building Backstage. | Build-time utilities; not authentication controls. |
| pg_dumpall, gzip and SHA-256 utilities | Create the database dump, compress it and record a file fingerprint. | Actual backup helpers; the saved inventory adds a separate comparison. |
| AzCopy | Upload protected backup material using managed identity. | Operational utility; no backup upload occurs in the offline preview. |

Terraform describes selected host/network boundaries. GitHub Actions supports build and verification processes, while the public manual-only workflow runs reference checks rather than operating the live portal.

## Step by Step

Your own local Backstage portal with a catalog component and a TechDocs page you authored.

[Open the standalone build guide](docs/BUILD-YOUR-OWN.md) or follow the same complete instructions below.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

### Prerequisites

A Unix-like development environment/WSL, a Node/Yarn release supported by the selected Backstage generator, build tools and Git. The starter is a development portal, not a secured production VM installation.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

### Create your project folder

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

### Step 1 — Generate your own portal

**Where:** A parent folder on your workstation.

Run the official Backstage app generator and choose your own app name, such as my-engineering-portal. Record the generator/package versions and keep the generated lockfile.

```bash
npx @backstage/create-app@latest
```

**Check before continuing:** A new application folder is created, independently of this portfolio repository.

### Step 2 — Start and inspect the generated app

**Where:** Your generated portal folder.

Install the generated dependencies with its documented Yarn version, then start it. Open the local URL printed by the process, normally localhost:3000, and confirm the backend is also running.

```bash
cd my-engineering-portal
yarn install
yarn start
```

**Check before continuing:** You can see your own development catalog.

### Step 3 — Define a component you own

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

### Step 4 — Create the owner and documentation

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

### Step 5 — Register the files and build docs

**Where:** app-config.local.yaml and Backstage catalog.

Merge the file locations below into app-config.local.yaml, replacing the placeholders with absolute paths to your own files and retaining other generated settings. Configure the local TechDocs builder and its Docker/MkDocs prerequisites, then open the entity and its Docs tab.

Create **`app-config.local.yaml (merge into the generated file)`** with the following contents:

```yaml
catalog:
  locations:
    - type: file
      target: /YOUR_ABSOLUTE_PROJECT_PATH/catalog-info.yaml
    - type: file
      target: /YOUR_ABSOLUTE_PROJECT_PATH/team.yaml
```

**Check before continuing:** Your component is owned and the handbook page renders; a catalog entry alone is not TechDocs proof.

### Step 6 — Verify boundaries before hosting

**Where:** Your test notes.

Check a missing owner/document path and record the actual error and recovery. Before moving to a VM, separately configure Entra sign-in, restricted engineer access, HTTPS, persistent database, secrets, backup and a tested restore path.

**Check before continuing:** The local portal works and the outstanding production requirements are explicit.

### Step 7 — Close the local build

**Where:** Your terminal.

Stop Yarn with Ctrl+C and retain your app source/lockfile and screenshots of the entity and docs. Keep OAuth credentials, private rosters and environment files out of Git.

**Check before continuing:** You have built your own catalog/documentation portal rather than running another person's checkout.

### Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. Existing portfolio images are references, not evidence that you performed these steps.

### Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

### Official implementation references

- [backstage.io — npx-create-app](https://backstage.io/docs/golden-path/create-app/npx-create-app/)
- [backstage.io — descriptor-format](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [backstage.io — creating-and-publishing](https://backstage.io/docs/features/techdocs/creating-and-publishing/)

The walkthrough layout follows the prerequisites → creation/configuration → test → verification → troubleshooting → cleanup pattern of the [Splunk project reference](https://github.com/davidharris6/splunk-siem-log-analysis). Its Splunk-specific settings are not copied into unrelated projects.

<details>
<summary>Reference: how the existing platform implementation operates</summary>

A short walkthrough of the process, with technical instructions and evidence limits in the sections below.

1. **Sign in to the portal (Entra and OAuth2 Proxy)** — An approved engineer signs in through Microsoft. The portal separately checks which actions that person may perform.

2. **Find the system and its owner (Backstage and TechDocs)** — The service directory connects each system to its responsible team and related services. The engineer can then open its operating instructions.

3. **Review release information** — The portal compares release records with a recent observation of what is running. Missing, conflicting or old information stays visibly uncertain.

4. **Protect the portal itself (Backup helpers and AzCopy)** — The operating process saves and checks backups before ending an engineering session. A separate restore test checks whether the required records and settings can be recovered.

</details>

## Engineering Strengths

| Capability | Why it matters | Details |
| --- | --- | --- |
| A directory of systems and owners | Helps engineers find the responsible team and related services. | [Service directory](catalog/) |
| Instructions beside each service | Makes operating guidance easier to find. | [Handbook](docs/CATALOG-AND-TECHDOCS.md) |
| Separate access checks | Distinguishes signing in from permission to read or change something. | [Access guide](docs/IDENTITY.md) |
| Honest release status | Shows when records are missing, conflicting or too old to trust. | [Release guide](docs/RELEASE-EVIDENCE.md) |
| Checked backups | Supports recovery beyond merely uploading a backup file. | [Recovery guide](docs/RECOVERY.md) |
| Planned operating sessions | Keeps occasional engineering use separate from an always-running service. | [Operations](docs/OPERATIONS.md) |

### Actual implementation and public reference

The repository includes selected implementation code and a small local demonstration. The demonstration is not the full Backstage application; its example systems and release records are fictional.

## Architecture

```mermaid
flowchart LR
  Engineer[Approved engineer] --> SignIn[Microsoft sign-in]
  SignIn --> Portal[Engineering portal]
  Portal --> Directory[Systems and owners]
  Portal --> Handbook[Operating instructions]
  Portal --> Release[Release information]
  Portal --> Database[Portal database]
  Database --> Backup[Protected backup copies]
  Handbook --> Backup
```

The deployed design uses one virtual server. A server failure can interrupt the portal, so backup and recovery remain important.

## What Was Built

- A directory connecting systems to their owners and dependencies.
- A handbook published separately from the portal that displays it.
- Microsoft sign-in and application permission checks.
- Release checks that compare the intended version with current deployment records.
- Startup checks, database backups and tools for testing recovery.
- Related Azure setup code and operating instructions.

[Technical design](docs/ARCHITECTURE.md) and [source records](docs/SOURCE-MAP.md) explain the included implementation.

## Proof It Works

Recorded checks included **nine release-status tests**, **ten startup tests on Linux**, **five directory checks** and **two infrastructure cases using simulated Azure responses**.

The local viewer displayed 16 service-directory entries and all four release states: Verified, Unknown, Conflict and Stale. Its navigation and mobile layout were also checked.

These results concern the included examples and selected code. They are separate from a new live sign-in, deployment or recovery rehearsal. [Full validation record](docs/VALIDATION.md).

<details>
<summary>For engineers: detailed results, examples and commands</summary>

### 1. Refuse incomplete or conflicting release evidence

```bash
python -B -m unittest discover -s reference/releases -v
python -B scripts/demo.py
```

**Look for:** nine original evaluator tests pass; the demonstration produces Verified, Unknown, Conflict and Stale for four fictional scenarios. A successful Actions run or historical pin alone never establishes a current deployment.

![Release-evidence reference](docs/images/02-evidence.png)

### 2. Check startup and network boundaries

```bash
python -B -m unittest discover -s runtime/vm -v
python -B runtime/vm/check-compose.py
```

Run the protected-file tests on Linux; they are skipped on Windows because its file-permission rules differ. The Compose checks read the settings without starting containers or downloading images. The ten original startup tests and the Compose checks cover exact image versions, separate sign-in apps, protected files, the private database connection and the optional separate publishing key.

### 3. Validate the public catalog and selected infrastructure

```bash
python -B -m unittest discover -s tests -v
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra validate
terraform -chdir=infra test
```

**Look for:** every catalog Location target exists, component ownership and unique references are present, and the mock Terraform tests preserve default-Off infrastructure and the selected VM constraints. No Azure plan/apply occurs.

### 4. Open the offline reference

```bash
python -B scripts/preview.py
```

Open [the local reference viewer](http://127.0.0.1:8136). Switch between Service catalog, Release evidence and Operating model. Ctrl+C stops it. The screenshots are genuine local captures of this reference, not screenshots of the live Backstage portal. [Validation and scope](docs/VALIDATION.md).

</details>

## Release and Recovery Process

1. Build and test the chosen version.
2. Check its software security findings and use that exact version for release.
3. Check the server settings before starting the portal.
4. Confirm approved sign-in, service listings, handbook access and database health.
5. Save and verify backups, and test restoration separately.
6. End the engineering session and release the server's compute allocation.

[Deployment steps](docs/DEPLOYMENT.md) and [recovery steps](docs/RECOVERY.md) provide the technical instructions.

## Security and Operational Boundaries

Signing in does not automatically grant permission to change services or publish software. The service directory also describes ownership; it does not itself grant access.

The local demonstration does not connect to the employee database or run a production deployment. Restoring the portal requires its configuration and protected credentials as well as the database backup.

## Scaling, Costs and Tradeoffs

One server is straightforward to operate for occasional engineering sessions, but it does not provide continuous availability during a server failure. Backups also require brief pauses to database writes.

Releasing the server's compute allocation stops that compute charge. Retained disks, addresses and storage can still cost money. For sustained use, measure response times and the number of engineers before considering more servers or managed database services. [Growth options](docs/SCALING.md).

## Troubleshooting Lessons

A successful backup command could intentionally skip a stopped session. Fresh backup evidence, database readiness and completed guest-script phases needed separate verification. [Read the incident, evidence and verification](docs/LESSONS-LEARNED.md).

## Project Guides

| Guide | What it explains |
| --- | --- |
| [Engineering strengths](docs/ENGINEERING-STRENGTHS.md) | Practical value and evidence behind the main design choices |
| [Architecture](docs/ARCHITECTURE.md) | Portal, business application and infrastructure boundaries |
| [Identity and permissions](docs/IDENTITY.md) | Two Entra layers, engineer policy and separate writer |
| [Catalog and TechDocs](docs/CATALOG-AND-TECHDOCS.md) | Ownership, publication and read-only serving |
| [Release evidence](docs/RELEASE-EVIDENCE.md) | Verified, Unknown, Conflict and Stale |
| [Deployment](docs/DEPLOYMENT.md) | Build, digest, host readiness check and rollback |
| [Backup and recovery](docs/RECOVERY.md) | Database, handbook and separately protected secrets |
| [Operations](docs/OPERATIONS.md) | Session lifecycle, troubleshooting and ClickOps |
| [Commands](docs/COMMANDS.md) | Local checks and controlled-host command examples |
| [Source map](docs/SOURCE-MAP.md) | Actual files and public adaptations |
| [Validation](docs/VALIDATION.md) | Observed local results and untested boundaries |
| [Terraform](infra/README.md) | Selected VM/backup reference and disabled defaults |
| [Scaling](docs/SCALING.md) | Strengths, weaknesses, growth and costs |

This repository has a manual-only validation workflow and no deployment credentials. Creating the portfolio did not start an Azure VM, change employee systems or consume hosted Actions minutes.
