#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$BASE_DIR/.env" ]; then
  # shellcheck disable=SC1091
  . "$BASE_DIR/.env"
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/frappe/frappe-bench}"
SITE_NAME="${SITE_NAME:-${ERP_SITE:-jib.blueapi.ir}}"

echo ">>> 05-cal-boot-rebuild: best-effort cal_boot assets + cache clear"
echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"
echo ">>> using SITE_NAME=${SITE_NAME}"

sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -e
  cd \"${BENCH_HOME}\"

  echo '>>> cleaning old __pycache__ from cal_boot ...'
  find apps/cal_boot -name '__pycache__' -type d -print0 2>/dev/null | xargs -0 rm -rf || true

  echo '>>> ensure sites/assets/cal_boot symlink ...'
  mkdir -p sites/assets
  ln -snf \"${BENCH_HOME}/apps/cal_boot/cal_boot/public\" \"${BENCH_HOME}/sites/assets/cal_boot\"

  echo '>>> bench build --apps cal_boot (non-fatal) ...'
  if ! bench build --apps cal_boot; then
    echo '!!! WARNING: bench build --apps cal_boot failed (likely esbuild quirk on this app).'
    echo '!!! Continuing because static assets are already linked.'
  fi

  echo '>>> clear cache + restart on ${SITE_NAME} ...'
  bench --site \"${SITE_NAME}\" clear-cache || true
  bench --site \"${SITE_NAME}\" clear-website-cache || true
  bench restart || true
"
