#!/usr/bin/env bash
set -euo pipefail

echo ">>> 03-supervisor: configure supervisor for frappe bench"

# باید با روت اجرا شود
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# بارگذاری متغیرها از .env (اگر موجود است)
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

FRAPPE_USER="${FRAPPE_USER:-frappe}"
BENCH_HOME="${BENCH_HOME:-/home/${FRAPPE_USER}/frappe-bench}"

echo ">>> using FRAPPE_USER=${FRAPPE_USER}"
echo ">>> using BENCH_HOME=${BENCH_HOME}"

if [ ! -d "${BENCH_HOME}" ]; then
  echo "ERROR: bench dir not found: ${BENCH_HOME}" >&2
  exit 1
fi

# 1) تولید/آپدیت supervisor.conf با یوزر frappe
echo ">>> running: bench setup supervisor --yes (as ${FRAPPE_USER})"
sudo -u "${FRAPPE_USER}" -H bash -lc "
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"
  cd \"${BENCH_HOME}\"
  bench setup supervisor --yes
"

# 2) لینک به /etc/supervisor/conf.d
echo ">>> linking ${BENCH_HOME}/config/supervisor.conf -> /etc/supervisor/conf.d/frappe-bench.conf"
mkdir -p /etc/supervisor/conf.d
ln -sfn \"${BENCH_HOME}/config/supervisor.conf\" /etc/supervisor/conf.d/frappe-bench.conf

# 3) اطمینان از فعال بودن سرویس supervisor
echo ">>> enabling and restarting supervisor service"
systemctl enable --now supervisor >/dev/null 2>&1 || systemctl restart supervisor

# 4) نمایش وضعیت پروسس‌های bench زیر supervisor
echo "=== supervisor status (if any) ==="
if supervisorctl status >/dev/null 2>&1; then
  supervisorctl status
else
  echo "WARN: supervisorctl could not connect to /var/run/supervisor.sock"
fi

echo ">>> 03-supervisor: DONE"
