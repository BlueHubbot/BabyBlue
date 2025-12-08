#!/usr/bin/env bash
#
# 05-cal-boot-rebuild.sh
#
# هدف:
# - اطمینان از وجود symlink پایدار برای assets اپ cal_boot
# - تلاش برای bench build --apps cal_boot (غیر کشنده / non-fatal)
# - clear-cache / clear-website-cache / bench restart برای سایت هدف
# - بدون نیاز به دستکاری دستی PATH بیرونی، همه چیز زیر کاربر frappe

set -euo pipefail

echo ">>> 05-cal-boot-rebuild: best-effort cal_boot assets + cache clear"

# -----------------------------
# ۱) ورودی‌ها و مقادیر پیش‌فرض
# -----------------------------

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/frappe/frappe-bench}"

SITE_NAME="${SITE_NAME:-}"
: "${SITE_NAME:=${SITE:-}}"

if [[ -z "${SITE_NAME}" && -f ".env" ]]; then
  SITE_NAME="$(grep -E '^SITE=' .env | tail -n1 | cut -d= -f2- | tr -d '\"' || true)"
fi

if [[ -z "${SITE_NAME}" ]]; then
  echo "ERROR: SITE_NAME is not set and could not be inferred (env SITE_NAME / SITE یا .env)" >&2
  exit 1
fi

echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"
echo ">>> using SITE_NAME=${SITE_NAME}"

# -----------------------------
# ۲) sanity check مسیر bench
# -----------------------------

if [[ ! -d "${BENCH_HOME}" ]]; then
  echo "ERROR: BENCH_HOME=${BENCH_HOME} does not exist. Nothing to do." >&2
  exit 1
fi

CAL_BOOT_APP_PATH="${BENCH_HOME}/apps/cal_boot/cal_boot"
CAL_BOOT_PUBLIC_PATH="${CAL_BOOT_APP_PATH}/public"

if [[ ! -d "${CAL_BOOT_APP_PATH}" ]]; then
  echo "WARNING: cal_boot app (${CAL_BOOT_APP_PATH}) not found. Skipping cal_boot rebuild." >&2
  exit 0
fi

# -----------------------------
# ۳) اجرای کارها زیر کاربر frappe
# -----------------------------

sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -e

  # bench را در PATH قرار بده
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"

  cd \"${BENCH_HOME}\"

  echo '>>> cleaning old __pycache__ from cal_boot ...'
  find \"apps/cal_boot\" -name '__pycache__' -type d -prune -exec rm -rf {} + || true

  echo '>>> ensure sites/assets/cal_boot symlink ...'
  mkdir -p \"sites/assets\"
  if [[ -d \"${CAL_BOOT_PUBLIC_PATH}\" ]]; then
    if [[ -L \"sites/assets/cal_boot\" || -e \"sites/assets/cal_boot\" ]]; then
      rm -rf \"sites/assets/cal_boot\"
    fi
    ln -s \"${CAL_BOOT_PUBLIC_PATH}\" \"sites/assets/cal_boot\"
  else
    echo 'WARNING: cal_boot public path not found: ${CAL_BOOT_PUBLIC_PATH}' >&2
  fi

  echo '>>> bench build --apps cal_boot (non-fatal, best-effort) ...'
  if ! bench build --apps cal_boot; then
    echo '!!! WARNING: bench build --apps cal_boot failed (likely esbuild quirk on this app).' >&2
    echo '!!! WARNING: Continuing because static assets are already linked via symlink.' >&2
  fi

  echo '>>> clear cache + restart on ${SITE_NAME} ...'
  bench --site \"${SITE_NAME}\" clear-cache || echo 'WARN: clear-cache failed' >&2
  bench --site \"${SITE_NAME}\" clear-website-cache || echo 'WARN: clear-website-cache failed' >&2
  bench restart || echo 'WARN: bench restart failed' >&2
"

echo ">>> 05-cal-boot-rebuild: done."
