#!/usr/bin/env bash
set -euo pipefail

cd /tmp/BabyBlue
if [ -f .env ]; then
  set -o allexport
  . .env
  set +o allexport
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/frappe/frappe-bench}"

SRC_SRV_BLUEDOC="${SRC_SRV_BLUEDOC:-artifacts/srv-bluedoc}"
SRC_VAR_WWW_HTML="${SRC_VAR_WWW_HTML:-artifacts/var-www-html}"
SRC_BENCH_ASSETS="${SRC_BENCH_ASSETS:-artifacts/bench-assets}"
SRC_SITE_ASSETS="${SRC_SITE_ASSETS:-artifacts/site-assets}"

echo ">>> 06-sync-assets: sync docs + www + bench assets"

sync_dir() {
  local src="$1" dst="$2" label="$3" owner="$4"
  if [ ! -d "$src" ]; then
    echo ">>> SKIP ${label}: source dir '$src' not found"
    return 0
  fi
  echo ">>> SYNC ${label}: $src -> $dst"
  mkdir -p "$dst"
  rsync -a --delete "$src"/ "$dst"/
  chown -R "$owner" "$dst"
}

# 1) /srv/bluedoc  (Docs)
sync_dir "$SRC_SRV_BLUEDOC" "/srv/bluedoc" "srv-bluedoc" "root:root"

# 2) /var/www/html (default web root)
sync_dir "$SRC_VAR_WWW_HTML" "/var/www/html" "var-www-html" "root:root"

# 3) BENCH_HOME/assets  (build شده‌های bench)
sync_dir "$SRC_BENCH_ASSETS" "$BENCH_HOME/assets" "bench-assets" "${FRAPPE_USER}:${FRAPPE_USER}"

# 4) BENCH_HOME/sites/assets  (manifest + blueapi_*.js و غیره)
sync_dir "$SRC_SITE_ASSETS" "$BENCH_HOME/sites/assets" "site-assets" "${FRAPPE_USER}:${FRAPPE_USER}"

echo ">>> 06-sync-assets: nginx reload"
if nginx -t; then
  systemctl reload nginx || echo "!!! nginx reload failed, check service"
else
  echo "!!! nginx config test failed, NOT reloading"
fi

echo ">>> 06-sync-assets: DONE"
