#!/usr/bin/env bash
# Use only fixed Compose files; environment values are never evaluated as shell.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
env_file=/etc/backstage/vm.env
python3 "$script_dir/preflight.py" "$env_file"
args=(--env-file "$env_file" -f "$script_dir/compose.yaml")
enabled="$(python3 - "$script_dir" "$env_file" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from preflight import load_env
print(load_env(Path(sys.argv[2])).get('BACKSTAGE_TEMPLATES_ENABLED', 'false'))
PY
)"
if [[ "$enabled" == true ]]; then args+=(-f "$script_dir/compose.templates.yaml"); fi
case "${1:-}" in
  validate) docker compose "${args[@]}" config --quiet ;;
  start) docker compose "${args[@]}" up --detach --no-build --pull never --wait --wait-timeout 180 ;;
  stop) docker compose "${args[@]}" down --timeout 30 ;;
  *) echo 'Use validate, start or stop.' >&2; exit 2 ;;
esac
