#!/usr/bin/env bash
set -euo pipefail
: "${DOMAIN:?}"; : "${EMAIL:?}"; : "${DB_ROOT_PW:?}"
apt(){ DEBIAN_FRONTEND=noninteractive apt-get -y "$@"; }
apt update
apt install curl wget ca-certificates gnupg lsb-release software-properties-common sudo unzip tar jq \
  git locales tzdata build-essential python3 python3-venv python3-pip pipx python3-dev gettext-base \
  libffi-dev libssl-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev \
  libpq-dev libmariadb-dev mariadb-server redis-server nginx certbot python3-certbot-nginx wkhtmltopdf

# swap 2G
if ! swapon --show | grep -q '^'; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile; mkswap /swapfile >/dev/null; swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Node 18 + yarn
if ! command -v node >/dev/null || ! node -v | grep -q '^v18'; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash - >/dev/null
  apt install nodejs
fi
npm -g ls yarn >/dev/null 2>&1 || npm i -g yarn >/dev/null

# user frappe + pipx dirs
id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
usermod -aG sudo frappe || true
echo 'frappe ALL=(ALL) NOPASSWD:ALL' >/etc/sudoers.d/frappe
install -d -o frappe -g frappe /home/frappe/.local/bin
install -d -o frappe -g frappe /home/frappe/.local/pipx
for f in /home/frappe/.profile /home/frappe/.bashrc; do
  grep -q '.local/bin' "$f" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$f"
  grep -q 'PIPX_HOME' "$f" || {
    echo 'export PIPX_HOME="$HOME/.local/pipx"' >> "$f"
    echo 'export PIPX_BIN_DIR="$HOME/.local/bin"' >> "$f"
  }
done
chown -R frappe:frappe /home/frappe
su - frappe -c 'pipx ensurepath >/dev/null 2>&1 || true'
su - frappe -c 'pipx list | grep -q frappe-bench || pipx install frappe-bench >/dev/null'

# MariaDB + root pw
cat >/etc/mysql/mariadb.conf.d/99-erpnext.cnf <<'CNF'
[mysqld]
character-set-server = utf8mb4
collation-server     = utf8mb4_unicode_ci
innodb-file-per-table = 1
max_allowed_packet = 64M
sql-mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
CNF
systemctl restart mariadb
mysql -uroot -e "SELECT 1" >/dev/null 2>&1 && \
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PW}'; FLUSH PRIVILEGES;" || true

# nginx + redis
sed -i 's/^\s*log_format\smain/# &/g' /etc/nginx/nginx.conf || true
rm -f /etc/nginx/sites-enabled/default || true
nginx -t >/dev/null && systemctl enable --now nginx
systemctl enable --now redis-server

echo "[✓] preflight OK"
