#!/usr/bin/env bash
# Run on the commissioned VM as the Docker-owning administrator. The VM's
# system-assigned identity must have the exact-repository Reader assignment.
set -euo pipefail
umask 077

env_file="${1:-/etc/backstage/vm.env}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for executable in python3 az docker; do
  command -v "$executable" >/dev/null || { echo "Missing $executable" >&2; exit 2; }
done

python3 "$script_dir/preflight.py" "$env_file"
az login --identity --output none
az acr login --name examplehubregistry001 --only-show-errors
docker compose --env-file "$env_file" -f "$script_dir/compose.yaml" config --quiet
docker compose --env-file "$env_file" -f "$script_dir/compose.yaml" pull --quiet

# File-backed Compose secrets preserve host ownership. Determine the reviewed
# image's PostgreSQL UID without starting a server or exposing a network.
postgres_image="$(python3 - "$env_file" "$script_dir" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
from preflight import load_env
print(load_env(Path(sys.argv[1]))['BACKSTAGE_POSTGRES_IMAGE'])
PY
)"
secret_dir="$(python3 - "$env_file" "$script_dir" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
from preflight import load_env
print(load_env(Path(sys.argv[1]))['BACKSTAGE_SECRET_DIR'])
PY
)"
postgres_uid="$(docker run --rm --network none --entrypoint id "$postgres_image" -u postgres)"
[[ "$postgres_uid" =~ ^[0-9]+$ ]] && [[ "$postgres_uid" -ne 0 ]] || { echo 'Invalid PostgreSQL UID' >&2; exit 2; }
chown "$postgres_uid:1000" "$secret_dir/postgres_password"
chmod 0640 "$secret_dir/postgres_password"
chown "$postgres_uid:$postgres_uid" "$secret_dir/postgres_admin_password"
chmod 0600 "$secret_dir/postgres_admin_password"
python3 "$script_dir/preflight.py" "$env_file"
echo 'Reviewed digest-pinned images are cached; the service can now start with --pull never.'
