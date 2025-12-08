#!/usr/bin/env bash
set -euo pipefail

echo ">>> 04-bench-post-migrate: migrate + (optional) build + cache clear + restart"

# باید با روت اجرا شود
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# ۱) بارگذاری متغیرها از .env (اگر هست)
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/${FRAPPE_USER}/frappe-bench}"
SKIP_BENCH_BUILD="${SKIP_BENCH_BUILD:-0}"

# ۲) تشخیص SITE_NAME
SITE_NAME="${SITE_NAME:-}"

# اولویت با SITE در .env
if [ -n "${SITE:-}" ]; then
  SITE_NAME="${SITE}"
fi

# اگر هنوز خالی است، از currentsite.txt بخوان
if [ -z "${SITE_NAME}" ]; then
  CFILE="${BENCH_HOME}/sites/currentsite.txt"
  if [ -f "${CFILE}" ]; then
    SITE_NAME="$(head -n1 "${CFILE}" | tr -d '[:space:]')"
  fi
fi

if [ -z "${SITE_NAME}" ]; then
  echo "ERROR: SITE / SITE_NAME not set and currentsite.txt not found" >&2
  exit 1
fi

echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"
echo ">>> using SITE_NAME=${SITE_NAME}"
echo ">>> SKIP_BENCH_BUILD=${SKIP_BENCH_BUILD}"

# ۳) چک پیش‌نیازهای مسیر
if [ ! -d "${BENCH_HOME}" ]; then
  echo "ERROR: bench dir not found: ${BENCH_HOME}" >&2
  exit 1
fi

if [ ! -d "${BENCH_HOME}/sites/${SITE_NAME}" ]; then
  echo "ERROR: site dir not found: ${BENCH_HOME}/sites/${SITE_NAME}" >&2
  exit 1
fi

# ۴) مطمئن شو مسیرهای لاگ وجود دارند
mkdir -p \
  "${BENCH_HOME}/logs" \
  "${BENCH_HOME}/sites/${SITE_NAME}/logs"

chown -R "${FRAPPE_USER}:${FRAPPE_USER}" \
  "${BENCH_HOME}/logs" \
  "${BENCH_HOME}/sites/${SITE_NAME}/logs"

# ۵) اجرای migrate + (اختیاری) build + cache clear + restart به‌عنوان یوزر frappe
sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -e
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"
  cd \"${BENCH_HOME}\"

  echo '>>> bench --site ${SITE_NAME} migrate ...'
  bench --site \"${SITE_NAME}\" migrate

  if [ \"${SKIP_BENCH_BUILD}\" = \"1\" ]; then
    echo '>>> SKIP_BENCH_BUILD=1 → skipping bench build (using prebuilt assets from artifacts)'
  else
    echo '>>> bench build (all apps, including hrms/cal_boot if present) ...'
    if ! bench build; then
      echo '!!! WARNING: bench build failed (likely HRMS frontend OOM or cal_boot esbuild).' >&2
      echo '!!! WARNING: Continuing with existing assets.' >&2
    fi
  fi

  echo '>>> bench --site ${SITE_NAME} clear-cache ...'
  bench --site \"${SITE_NAME}\" clear-cache

  echo '>>> bench --site ${SITE_NAME} clear-website-cache ...'
  bench --site \"${SITE_NAME}\" clear-website-cache

  echo '>>> bench restart ...'
  bench restart
"

echo ">>> 04-bench-post-migrate: DONE"
