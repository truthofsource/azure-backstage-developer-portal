#!/bin/sh
# Read Compose-mounted secret files at runtime. Never pass secret values in Compose.
set -eu
umask 077
read_secret() {
  file="/run/secrets/$1"
  [ -s "$file" ] || { echo "Missing required secret file: $1" >&2; exit 2; }
  cat "$file"
}
export BACKSTAGE_POSTGRES_PASSWORD="$(read_secret postgres_password)"
export BACKSTAGE_ENTRA_CLIENT_SECRET="$(read_secret backstage_entra_client_secret)"
export BACKSTAGE_GITHUB_APP_CLIENT_SECRET="$(read_secret github_app_client_secret)"
export BACKSTAGE_GITHUB_APP_PRIVATE_KEY="$(read_secret github_app_private_key)"
export BACKSTAGE_GITHUB_APP_WEBHOOK_SECRET="$(read_secret github_app_webhook_secret)"
export BACKSTAGE_TEMPLATES_ENABLED="${BACKSTAGE_TEMPLATES_ENABLED:-false}"
exec node packages/backend --config app-config.yaml --config app-config.production.yaml --config app-config.vm.yaml
