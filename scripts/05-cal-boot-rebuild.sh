#!/usr/bin/env bash
#
# 05-cal-boot-rebuild.sh
#
# هدف:
# - اطمینان از وجود symlink پایدار برای assets اپ cal_boot
# - اجرای bench build --apps cal_boot (الان EXPECT می‌کنیم موفق شود)
# - clear-cache / clear-website-cache / bench restart برای سایت هدف

set -euo pipefail

echo ">>> 05-cal-boot-rebuild: cal_boot assets + build + cache clear"

# -----------------------------
# ۱) ورودی‌ها و مقادیر پیش‌فرض
# -----------------------------

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/frappe/frappe-bench}"

SITE_NAME="${SITE_NAME:-}"
: "${SITE_NAME:=${SITE:-}}"

# اگر از مسیر ریپو اجرا می‌شود و .env هست، از آن SITE را بخوان
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

  echo '>>> bench build --apps cal_boot ...'
  bench build --apps cal_boot

  echo '>>> clear cache + restart on ${SITE_NAME} ...'
  bench --site \"${SITE_NAME}\" clear-cache
  bench --site \"${SITE_NAME}\" clear-website-cache
  bench restart
"

echo ">>> 05-cal-boot-rebuild: done."
