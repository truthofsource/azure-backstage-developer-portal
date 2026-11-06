#!/usr/bin/env bash
# Quiesce only the backend, never start a stopped engineering session.
set -euo pipefail
umask 077
exec 9>/run/lock/backstage-backup.lock
flock -n 9 || { echo 'Backup already running.' >&2; exit 1; }
systemctl is-active --quiet backstage-stack.service || exit 0
running="$(docker inspect backstage-portal --format '{{.State.Running}}')"
[[ "$running" == true ]] || { echo 'Backend not running; backup skipped.'; exit 0; }
resume() {
  if systemctl is-active --quiet backstage-stack.service; then
    docker start backstage-portal >/dev/null
  fi
}
trap resume EXIT
docker stop --time 30 backstage-portal >/dev/null
bash /opt/backstage/vm/backup-postgres.sh
echo 'Session backup completed; backend resume is conditional on an active session.'
