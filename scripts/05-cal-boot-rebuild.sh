#!/usr/bin/env bash
set -euo pipefail

echo ">>> 05-cal-boot-rebuild: rebuild cal_boot assets for site"

# باید با روت اجرا شود
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# بارگذاری متغیرها از .env
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/${FRAPPE_USER}/frappe-bench}"
SITE_NAME="${SITE:-${SITE_NAME:-}}"

if [ -z "${SITE_NAME}" ]; then
  echo "ERROR: SITE (or SITE_NAME) not set in .env" >&2
  exit 1
fi

echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"
echo ">>> using SITE_NAME=${SITE_NAME}"

if [ ! -d "${BENCH_HOME}" ]; then
  echo "ERROR: bench dir not found: ${BENCH_HOME}" >&2
  exit 1
fi

# اجرای bench با یوزر frappe
sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -e
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"
  cd \"${BENCH_HOME}\"

  echo '>>> cleaning old pyc from cal_boot ...'
  find apps/cal_boot -name '*.pyc' -delete || true

  echo '>>> bench build --apps cal_boot ...'
  bench build --apps cal_boot

  echo '>>> clear cache for ${SITE_NAME} ...'
  bench --site \"${SITE_NAME}\" clear-cache
  bench --site \"${SITE_NAME}\" clear-website-cache

  echo '>>> bench restart ...'
  bench restart
"

echo ">>> 05-cal-boot-rebuild: DONE"
