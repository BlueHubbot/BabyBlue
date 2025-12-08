#03-supervisor.sh
#!/usr/bin/env bash
set -euo pipefail

echo ">>> 03-supervisor: configure supervisor for frappe bench"

# 0) باید با روت اجرا شود
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: this script must be run as root" >&2
  exit 1
fi

# 1) بارگذاری متغیرها از .env (اگر موجود است)
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

# 2) مطمئن شو supervisor نصب است (اگر نباشد، نصب می‌کنیم)
if ! command -v supervisorctl >/dev/null 2>&1; then
  echo ">>> installing supervisor package (apt-get)..."
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y supervisor
fi

# 3) تولید/آپدیت supervisor.conf با یوزر frappe
echo ">>> running: bench setup supervisor --yes (as ${FRAPPE_USER})"
sudo -u "${FRAPPE_USER}" -H bash -lc "
  set -euo pipefail
  export PATH=\"\$HOME/bench-venv/bin:\$HOME/.local/bin:\$PATH\"
  cd \"${BENCH_HOME}\"
  bench setup supervisor --yes
"

# 4) لینک به /etc/supervisor/conf.d
echo ">>> linking ${BENCH_HOME}/config/supervisor.conf -> /etc/supervisor/conf.d/frappe-bench.conf"
mkdir -p /etc/supervisor/conf.d
ln -sfn "${BENCH_HOME}/config/supervisor.conf" /etc/supervisor/conf.d/frappe-bench.conf

# 5) فعال و راه‌اندازی سرویس supervisor
echo ">>> enabling and restarting supervisor service"
systemctl enable supervisor >/dev/null 2>&1 || true
systemctl restart supervisor

# 6) sync کانفیگ‌ها و بالا آوردن پروسه‌های bench
echo ">>> supervisorctl reread / update / restart all"
supervisorctl reread || true
supervisorctl update || true
supervisorctl restart all || true

echo "=== supervisor status (if any) ==="
if supervisorctl status >/dev/null 2>&1; then
  supervisorctl status
else
  echo "WARN: supervisorctl could not connect to /var/run/supervisor.sock"
fi

echo ">>> 03-supervisor: DONE"
