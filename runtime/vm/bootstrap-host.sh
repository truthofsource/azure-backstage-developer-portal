#!/usr/bin/env bash
# Secret-free Ubuntu 24.04 guest preparation. This never starts Backstage.
set -euo pipefail
umask 077
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg python3 docker.io docker-compose-v2
install -d -m 0755 /etc/apt/keyrings
curl --fail --silent --show-error --location https://packages.microsoft.com/keys/microsoft.asc \
  --output /etc/apt/keyrings/microsoft.asc
gpg --batch --yes --dearmor --output /etc/apt/keyrings/microsoft.gpg /etc/apt/keyrings/microsoft.asc
chmod 0644 /etc/apt/keyrings/microsoft.gpg
printf '%s\n' 'deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ noble main' \
  > /etc/apt/sources.list.d/azure-cli.list
apt-get update
apt-get install -y --no-install-recommends azure-cli
timedatectl set-timezone America/Chicago
install -d -m 0700 /etc/backstage /etc/backstage/secrets
install -d -m 0755 /opt/backstage/vm
install -d -m 0750 /var/lib/backstage
systemctl enable --now docker
docker compose version
az version --query '"azure-cli"' -o tsv
printf '%s\n' 'Host tools prepared; Backstage service and containers remain uninstalled.'
