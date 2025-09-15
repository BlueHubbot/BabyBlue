#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root"; exit 1; }

DOMAIN="${DOMAIN:?set DOMAIN}"        # مثلا blue.nawpa.ir
EMAIL="${EMAIL:-admin@${DOMAIN#*.}}"
ADMIN_PW="${ADMIN_PW:-adminpass123}"
DB_ROOT_PW="${DB_ROOT_PW:-root}"

BENCH_HOME="/home/frappe/frappe-bench"
B="/home/frappe/.local/bin/bench"

export NODE_OPTIONS="--max-old-space-size=4096"

# bench init (اگر نیست)
if [ ! -d "$BENCH_HOME" ]; then
  su - frappe -s /bin/bash -lc "mkdir -p ~/; $B init --skip-redis-config-generation frappe-bench"
fi

cd "$BENCH_HOME"

# اپ‌ها
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B get-app --branch version-15 erpnext https://github.com/frappe/erpnext.git || true"
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B get-app --branch version-15 hrms https://github.com/frappe/hrms || true"

# سایت
if [ ! -d "$BENCH_HOME/sites/$DOMAIN" ]; then
  su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B new-site $DOMAIN --mariadb-root-username root --mariadb-root-password '$DB_ROOT_PW' --admin-password '$ADMIN_PW' --no-migrate"
fi

# نصب اپ‌ها روی سایت
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B --site '$DOMAIN' install-app erpnext || true"
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B --site '$DOMAIN' install-app hrms || true"

# ریکاوری (اختیاری)
RESTORE_DIR="/home/frappe/restore"
DB_URL="${DB_URL:-}"; PUB_URL="${PUB_URL:-}"; PRIV_URL="${PRIV_URL:-}"; BACKUP_PASS="${BACKUP_PASS:-}"
if [ -n "$DB_URL" ]; then
  install -d -o frappe -g frappe "$RESTORE_DIR"
  su - frappe -s /bin/bash -lc "cd $RESTORE_DIR && curl -fsSL '$DB_URL' -o db.enc && openssl enc -d -aes-256-cbc -pbkdf2 -in db.enc -out db.sql.gz -pass env:BACKUP_PASS"
  [ -n "$PUB_URL" ]  && su - frappe -s /bin/bash -lc "cd $RESTORE_DIR && curl -fsSL '$PUB_URL'  -o files.enc && openssl enc -d -aes-256-cbc -pbkdf2 -in files.enc -out files.tar -pass env:BACKUP_PASS" || true
  [ -n "$PRIV_URL" ] && su - frappe -s /bin/bash -lc "cd $RESTORE_DIR && curl -fsSL '$PRIV_URL' -o pfiles.enc && openssl enc -d -aes-256-cbc -pbkdf2 -in pfiles.enc -out pfiles.tar -pass env:BACKUP_PASS" || true
  su - frappe -s /bin/bash -lc "cd $BENCH_HOME && BACKUP_PASS='$BACKUP_PASS' $B --site '$DOMAIN' restore $RESTORE_DIR/db.sql.gz --force"
fi

# build و migrate
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B build --apps erpnext hrms"
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B --site '$DOMAIN' migrate"

# کانفیگ سایت
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B --site '$DOMAIN' set-config host_name https://$DOMAIN && $B --site '$DOMAIN' enable-scheduler && $B --site '$DOMAIN' clear-cache && $B --site '$DOMAIN' clear-website-cache"

# Nginx + Supervisor (بدون فرمت لاگ main)
su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B setup supervisor"
install -m 0644 "$BENCH_HOME/config/supervisor.conf" /etc/supervisor/conf.d/frappe-bench.conf
supervisorctl reread; supervisorctl update || true

su - frappe -s /bin/bash -lc "cd $BENCH_HOME && $B setup nginx"
sed -i 's/ access_log \([^;]*\) main;/ access_log \1;/' "$BENCH_HOME/config/nginx.conf" || true
install -m 0644 "$BENCH_HOME/config/nginx.conf" /etc/nginx/conf.d/frappe-bench.conf
nginx -t && systemctl reload nginx

# HTTPS
if command -v certbot >/dev/null 2>&1; then
  certbot --nginx -d "$DOMAIN" -m "$EMAIL" -n --agree-tos --redirect || true
  nginx -t && systemctl reload nginx || true
fi

# logrotate
cat >/etc/logrotate.d/frappe-bench <<'LR'
/home/frappe/frappe-bench/logs/*.log {
  daily
  rotate 14
  missingok
  notifempty
  compress
  delaycompress
  copytruncate
}
LR
chmod 0644 /etc/logrotate.d/frappe-bench

# ری‌استارت سرویس‌های بنچ
supervisorctl restart all || true

echo "OK: ERPNext at https://${DOMAIN}"
