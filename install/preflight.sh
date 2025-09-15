#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || exec sudo -E bash "$0" "$@"

# Swap (۲ گیگ) برای جلوگیری از OOM در build
if ! grep -q "swapfile" /etc/fstab; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile; mkswap /swapfile; swapon /swapfile
  echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
fi

apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  sudo curl git ca-certificates lsb-release tzdata locales \
  supervisor redis-server mariadb-server mariadb-client libmariadb-dev pkg-config \
  python3-venv python3-dev pipx \
  nodejs npm yarnpkg \
  nginx certbot python3-certbot-nginx wkhtmltopdf xz-utils

# اطمینان از وجود yarn
ln -sf /usr/bin/yarnpkg /usr/local/bin/yarn

systemctl enable --now supervisor redis-server mariadb nginx

# کاربر frappe
if ! id -u frappe >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" frappe
fi

# bench via pipx (برای کاربر frappe)
su - frappe -s /bin/bash -lc 'pipx ensurepath >/dev/null 2>&1 || true; pipx install --force frappe-bench'

# تنظیم MariaDB root password (برای دسترسی بنچ از یوزر frappe)
DB_ROOT_PW="${DB_ROOT_PW:-root}"
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PW}'; FLUSH PRIVILEGES;" || true
