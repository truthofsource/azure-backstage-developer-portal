#!/usr/bin/env bash
# Back up one immutable technical publication, never the secrets or roster.
set -euo pipefail
umask 077
[[ $# -eq 1 && "$1" =~ ^[a-f0-9]{40}$ ]] || { echo 'Exact published source SHA required' >&2; exit 2; }
: "${BACKSTAGE_BACKUP_CONTAINER_URL:?Set reviewed backup container URL}"
[[ "$BACKSTAGE_BACKUP_CONTAINER_URL" =~ ^https://[a-z0-9]{3,24}\.blob\.core\.windows\.net/database-backups$ ]] || { echo 'Exact private backup container required' >&2; exit 2; }
release_root=/var/lib/backstage/techdocs/default/component/.releases
test -f "$release_root/$1/publication.json"
work_dir=$(mktemp -d)
trap 'rm -rf -- "$work_dir"' EXIT
name="techdocs-$1-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tar -C "$release_root" -czf "$work_dir/$name" "$1"
(cd "$work_dir" && sha256sum "$name" > "$name.sha256")
azcopy login --identity >/dev/null
azcopy copy "$work_dir/$name" "$BACKSTAGE_BACKUP_CONTAINER_URL/$name" --from-to LocalBlob --overwrite=false --output-level=quiet
azcopy copy "$work_dir/$name.sha256" "$BACKSTAGE_BACKUP_CONTAINER_URL/$name.sha256" --from-to LocalBlob --overwrite=false --output-level=quiet
install -d -m 0700 "$work_dir/readback"
azcopy copy "$BACKSTAGE_BACKUP_CONTAINER_URL/$name" "$work_dir/readback/$name" --from-to BlobLocal --overwrite=false --output-level=quiet
azcopy copy "$BACKSTAGE_BACKUP_CONTAINER_URL/$name.sha256" "$work_dir/readback/$name.sha256" --from-to BlobLocal --overwrite=false --output-level=quiet
(cd "$work_dir/readback" && sha256sum -c "$name.sha256")
python3 - "$work_dir/readback/$name" "$work_dir/restored" "$1" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
import tarfile
target = Path(sys.argv[2])
target.mkdir(mode=0o700)
with tarfile.open(sys.argv[1]) as archive:
    for member in archive.getmembers():
        if not (member.isfile() or member.isdir()) or Path(member.name).parts[0] != sys.argv[3]:
            raise SystemExit('Unexpected archive member; restore refused')
    archive.extractall(target, filter='data')
release = target / sys.argv[3]
publication = json.loads((release / 'publication.json').read_text())
if publication.get('source_sha') != sys.argv[3]:
    raise SystemExit('Publication identity differs')
for name, expected in publication['files'].items():
    file = release / name
    if not file.resolve().is_relative_to(release.resolve()) or file.is_symlink():
        raise SystemExit('Unsafe publication path')
    if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
        raise SystemExit('Publication file checksum differs')
print('Downloaded handbook restored with all publication file hashes matching.')
PY
echo "Uploaded and restored $name"
