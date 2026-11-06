# Commands and expected results

## Local reference (Python 3.12)

```bash
python -B -m unittest discover -s reference/releases -v
python -B -m unittest discover -s tests -v
python -B scripts/demo.py
python -B scripts/preview.py
```

Open http://127.0.0.1:8136; Ctrl+C stops the loopback-only viewer. Nine original evaluator tests and five new public-reference tests should pass. The demo emits four explicit evidence states and does not authenticate anywhere.

## Linux file-permission checks

```bash
python -B -m unittest discover -s runtime/vm -v
```

Ten original tests run on Linux; on Windows the suite explicitly skips because POSIX chmod checks differ. For the local validation, an existing Python 3.12 Linux image was used with network none and a read-only project mount. In your own environment, select and verify the image first; do not equate a mutable convenience tag with an immutable deployment reference.

## Compose contract (Docker CLI + Compose v2)

```bash
python -B runtime/vm/check-compose.py
```

This executes docker compose config using fictional values. It verifies only Caddy exposes 443, PostgreSQL is internal and the optional writer overlay adds a separate key without exposing it to other services. It does not start the stack, require real secret files or pull example images. Docker must be on PATH; use the locally installed executable's directory if necessary.

## Terraform reference

```bash
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra validate
terraform -chdir=infra test
```

Provider initialization downloads/verifies plugins. Mock tests call no Azure API. Do not apply this root to existing state: default-Off public inputs are different from the live commissioned root.

## Reviewed Linux host only — examples, not run by this portfolio

```bash
sudo python3 /opt/backstage/vm/preflight.py /etc/backstage/vm.env
sudo systemctl start backstage-stack.service
sudo systemctl status backstage-stack.service --no-pager
sudo systemctl list-timers backstage-backup.timer
sudo systemctl stop backstage-stack.service
```

Service files and protected inputs must already be installed through the owning runbook. Never run the bootstrap or restore helpers against an arbitrary production host. Backup destination/image variables must be selected privately; do not use the fictional targets in the reference as deployment values.
