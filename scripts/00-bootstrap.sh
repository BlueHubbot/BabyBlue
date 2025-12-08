#00-bootstrap.sh
#!/usr/bin/env bash
set -euo pipefail
cd /tmp/BabyBlue
if [ -f .env ]; then
  set -o allexport
  . .env
  set +o allexport
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [[ ! -f .env ]]; then
  echo ".env not found; copy .env.example and edit first" >&2
  exit 1
fi

set -o allexport
# shellcheck disable=SC1091
source .env
set +o allexport

export DEBIAN_FRONTEND=noninteractive

# Create frappe user if needed
if ! id -u "$FRAPPE_USER" >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" "$FRAPPE_USER"
fi

# Sudoers for frappe (service control بدون پسورد)
cat >/etc/sudoers.d/90-"$FRAPPE_USER" <<EOS
$FRAPPE_USER ALL=(ALL) NOPASSWD:/usr/bin/supervisorctl, /usr/sbin/nginx, /bin/systemctl
EOS
chmod 440 /etc/sudoers.d/90-"$FRAPPE_USER"

# پایه‌های سیستم
apt-get update
apt-get install -y \
  git curl build-essential \
  python3.11 python3.11-venv python3.11-dev \
  redis-server supervisor nginx \
  mariadb-server mariadb-client \
  certbot python3-certbot-nginx \
  libffi-dev libssl-dev wkhtmltopdf

# Node 18 + Yarn v1
if ! command -v node >/dev/null 2>&1 || ! node -v | grep -q '^v18'; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get install -y nodejs
fi

if ! command -v yarn >/dev/null 2>&1; then
  npm install -g yarn
fi

# ست‌کردن پسورد root ماریادبی (اگر قبلاً ست شده، خطا را نادیده بگیر)
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASS}'; FLUSH PRIVILEGES;" || true

systemctl enable --now mariadb redis-server supervisor nginx
