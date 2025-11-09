#!/bin/bash
set -e
BASE="/tmp/BabyBlue"
ART="$BASE/artifacts/data"
LATEST=$(ls -1 "$ART" | sort | tail -n1)

if [ -z "$LATEST" ]; then
  echo "no artifacts in $ART"
  exit 1
fi

if ! id -u frappe >/dev/null 2>&1; then
  echo "user frappe missing, run install-prereqs first"
  exit 1
fi

SRC="$ART/$LATEST"

if ls "$SRC"/frappe-bench.tar.gz.* >/dev/null 2>&1; then
  cat "$SRC"/frappe-bench.tar.gz.* > /tmp/frappe-bench.tar.gz
  mkdir -p /home/frappe
  tar -xzf /tmp/frappe-bench.tar.gz -C /home/frappe
  chown -R frappe:frappe /home/frappe/frappe-bench
fi

if [ -f "$SRC/bluedoc.tar.gz" ]; then
  mkdir -p /srv
  tar -xzf "$SRC/bluedoc.tar.gz" -C /srv
fi

echo "[OK] offline restore done from $SRC"
