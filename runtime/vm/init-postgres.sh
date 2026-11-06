#!/bin/sh
# First boot only: separate bootstrap administration from the app login.
set -eu
runtime_password="$(cat /run/secrets/postgres_password)"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 --set=runtime_password="$runtime_password" <<'SQL'
CREATE ROLE backstage WITH LOGIN PASSWORD :'runtime_password' CREATEDB NOSUPERUSER NOCREATEROLE NOREPLICATION;
ALTER DATABASE backstage OWNER TO backstage;
SQL
