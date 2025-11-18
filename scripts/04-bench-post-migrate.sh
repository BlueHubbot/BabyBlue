#!/usr/bin/env bash
set -euo pipefail

echo ">>> 04-bench-post-migrate: migrate + build + cache clear + restart"

# باید با روت اجرا شود
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# 1) بارگذاری متغیرها از .env (اگر هست)
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/${FRAPPE_USER}/frappe-bench}"

if [ ! -d "${BENCH_HOME}" ]; then
  echo "ERROR: bench dir not found: ${BENCH_HOME}" >&2
  exit 1
fi

# 2) تعیین SITE_NAME (نام سایت Frappe)
SITE_NAME="${SITE_NAME:-}"

# اگر صریح در .env نبود، از متغیرهای دیگر حدس بزن
if [ -z "${SITE_NAME}" ]; then
  for v in ERP_SITE ERP_SITE_NAME ERP_FQDN ERP_DOMAIN PRIMARY_SITE; do
    eval "val=\${$v:-}"
    if [ -n "${val}" ]; then
      SITE_NAME="${val}"
      break
    fi
  done
fi

# اگر هنوز خالی است، از currentsite.txt بخوان
if [ -z "${SITE_NAME}" ] && [ -f "${BENCH_HOME}/sites/currentsite.txt" ]; then
  SITE_NAME="$(<"${BENCH_HOME}/sites/currentsite.txt")"
fi

if [ -z "${SITE_NAME}" ]; then
  echo "ERROR: SITE_NAME is not set and could not be inferred" >&2
  exit 1
fi

echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"
echo ">>> using SITE_NAME=${SITE_NAME}"

# 3) migrate + build + cache clear + restart با یوزر frappe
sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -e
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"
  cd \"${BENCH_HOME}\"

  echo '>>> bench migrate ...'
  bench --site \"${SITE_NAME}\" migrate

  echo '>>> bench build (all apps) ...'
  bench build

  echo '>>> clear cache ...'
  bench --site \"${SITE_NAME}\" clear-cache
  bench --site \"${SITE_NAME}\" clear-website-cache

  echo '>>> bench restart ...'
  bench restart
"

echo ">>> 04-bench-post-migrate: DONE"
