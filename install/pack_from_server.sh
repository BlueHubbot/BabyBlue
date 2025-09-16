#!/usr/bin/env bash
set -euo pipefail

BENCH_HOME=${BENCH_HOME:-/home/frappe/frappe-bench}
OUT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 0) اطلاعات نسخه‌ها
BENCH_VER="$(su - frappe -c "python3 - <<'PY'\nimport pkg_resources\nprint(pkg_resources.get_distribution('frappe-bench').version)\nPY" 2>/dev/null || echo "5")"
echo "[info] bench version: ${BENCH_VER}"

# 1) بسته‌بندی کد اپ‌ها (frappe/erpnext/hrms) از bench فعلی
mkdir -p "${OUT_ROOT}/vendor/apps"
tar -czf "${OUT_ROOT}/vendor/apps/frappe.tar.gz"  -C "${BENCH_HOME}/apps" frappe
tar -czf "${OUT_ROOT}/vendor/apps/erpnext.tar.gz" -C "${BENCH_HOME}/apps" erpnext
if [ -d "${BENCH_HOME}/apps/hrms" ]; then
  tar -czf "${OUT_ROOT}/vendor/apps/hrms.tar.gz" -C "${BENCH_HOME}/apps" hrms
fi

# 2) Wheelhouse آفلاین پایتون (شامل bench و کل نیازمندی‌های محیط)
mkdir -p "${OUT_ROOT}/vendor/wheels"
REQ_FILE="$(mktemp)"
su - frappe -c "source ${BENCH_HOME}/env/bin/activate && pip freeze" > "${REQ_FILE}" || true
# bench هم اضافه شود تا pipx بدون اینترنت نصب کند
echo "frappe-bench==${BENCH_VER}" >> "${REQ_FILE}"
pip download --dest "${OUT_ROOT}/vendor/wheels" -r "${REQ_FILE}"
rm -f "${REQ_FILE}"

# 3) Assets بیلد‌شده (برای حذف نیاز به node/yarn در مقصد)
tar -czf "${OUT_ROOT}/vendor/sites_assets.tar.gz" -C "${BENCH_HOME}/sites" assets

# 4) Nginx فعلی را به قالب تبدیل کن (دامنه را placeholder کن)
NG_SRC="/etc/nginx/conf.d/frappe-bench.conf"
if [ -f "${NG_SRC}" ]; then
  sed -e 's/server_name \([^;]*\);/server_name ${DOMAIN};/g' \
      -e 's|/etc/letsencrypt/live/[^/]*/|/etc/letsencrypt/live/${DOMAIN}/|g' \
      < "${NG_SRC}" > "${OUT_ROOT}/assets/nginx/frappe-bench.conf.tpl" || true
fi

# 5) Split به پارت‌های <95MB جهت Git
split95(){ f="$1"; [ -f "$f" ] || return 0; dir="$(dirname "$f")"; base="$(basename "$f")"; (cd "$dir" && split -b 95M -d "$base" "$base.part-"); rm -f "$f"; }
split95 "${OUT_ROOT}/vendor/apps/frappe.tar.gz"
split95 "${OUT_ROOT}/vendor/apps/erpnext.tar.gz"
split95 "${OUT_ROOT}/vendor/apps/hrms.tar.gz" || true
split95 "${OUT_ROOT}/vendor/sites_assets.tar.gz"

echo "[✓] packed: apps(w/parts) + wheels + built assets + nginx tpl"
