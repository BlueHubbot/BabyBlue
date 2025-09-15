#!/usr/bin/env bash
set -Eeuo pipefail

# ===== args =====
SITE=""; EMAIL=""; DOCS_SUB=""
ADMIN_PW="${ADMIN_PW:-adminpass123}"
DB_ROOT_PW="${DB_ROOT_PW:-$(openssl rand -base64 18 | tr -dc 'A-Za-z0-9' | head -c 16)}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) SITE="$2"; shift 2;;
    --email) EMAIL="$2"; shift 2;;
    --docs-subdomain) DOCS_SUB="$2"; shift 2;;
    --admin-pass) ADMIN_PW="$2"; shift 2;;
    --db-root-pass) DB_ROOT_PW="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

[[ -n "$SITE" ]] || { echo "Usage: $0 --domain example.com [--email you@domain] [--docs-subdomain docs.example.com] [--admin-pass ...] [--db-root-pass ...]"; exit 1; }
[[ $EUID -eq 0 ]] || { echo "Run as root"; exit 1; }

echo "==> Domain: $SITE"
[[ -n "$EMAIL" ]] && echo "==> Email : $EMAIL"
[[ -n "$DOCS_SUB" ]] && echo "==> Docs  : $DOCS_SUB"
echo "==> DB root pw: $DB_ROOT_PW"
echo "==> Admin pw  : $ADMIN_PW"

# ===== deps =====
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
  git curl sudo ca-certificates gnupg lsb-release xz-utils \
  python3-venv python3-dev pipx pkg-config \
  mariadb-server mariadb-client libmariadb-dev \
  redis-server supervisor nginx \
  nodejs npm wkhtmltopdf certbot python3-certbot-nginx

# Yarn (v1)
npm i -g yarn@1 >/dev/null 2>&1 || true

# ===== system users =====
id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
usermod -aG sudo frappe || true

# ===== bench via pipx =====
su - frappe -s /bin/bash -lc 'pipx ensurepath >/dev/null 2>&1 || true; pipx install --force frappe-bench >/dev/null'
BENCH_BIN="/home/frappe/.local/bin/bench"

# ===== init bench =====
su - frappe -s /bin/bash -lc "
  set -e
  [[ -d /home/frappe/frappe-bench ]] || ${BENCH_BIN} init --skip-assets --frappe-branch version-15 /home/frappe/frappe-bench
  cd /home/frappe/frappe-bench
  ${BENCH_BIN} get-app --branch version-15 erpnext
  ${BENCH_BIN} get-app --branch version-15 hrms
"

# ===== MariaDB root password (switch from unix_socket if needed) =====
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PW}'; FLUSH PRIVILEGES;" || true

# ===== create site =====
su - frappe -s /bin/bash -lc "
  set -e
  cd /home/frappe/frappe-bench
  if [[ ! -d sites/${SITE} ]]; then
    ${BENCH_BIN} new-site '${SITE}' --db-root-password '${DB_ROOT_PW}' --admin-password '${ADMIN_PW}' --no-mariadb-socket || ${BENCH_BIN} new-site '${SITE}' --db-root-password '${DB_ROOT_PW}' --admin-password '${ADMIN_PW}'
  fi
  ${BENCH_BIN} --site '${SITE}' install-app erpnext
  ${BENCH_BIN} --site '${SITE}' install-app hrms
  ${BENCH_BIN} --site '${SITE}' set-config host_name 'https://${SITE}'
  ${BENCH_BIN} --site '${SITE}' enable-scheduler
"

# ===== build assets (avoid OOM) =====
su - frappe -s /bin/bash -lc "
  export NODE_OPTIONS=--max-old-space-size=2048
  cd /home/frappe/frappe-bench
  yarn install --check-files || true
  ${BENCH_BIN} build
"

# ===== supervisor/nginx =====
su - frappe -s /bin/bash -lc "cd /home/frappe/frappe-bench && yes | ${BENCH_BIN} setup supervisor"
ln -sf /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf

su - frappe -s /bin/bash -lc "cd /home/frappe/frappe-bench && ${BENCH_BIN} setup nginx"
cp -f /home/frappe/frappe-bench/config/nginx.conf /etc/nginx/conf.d/frappe-bench.conf
# fix 'main' log format if distro lacks it
sed -i -E 's/(access_log\s+[^;]+)\s+main;/\1;/' /etc/nginx/conf.d/frappe-bench.conf || true

# optional docs server (static)
if [[ -n "$DOCS_SUB" ]]; then
  mkdir -p /var/www/docs
  chown -R www-data:www-data /var/www/docs
  cat >/etc/nginx/conf.d/docs.conf <<DOCS
server {
    server_name ${DOCS_SUB};
    root /var/www/docs;
    index index.html;
    location / { try_files \$uri \$uri/ /index.html; add_header Cache-Control "public, max-age=300"; expires 5m; }
    access_log /var/log/nginx/docs.access.log;
    error_log  /var/log/nginx/docs.error.log;
    listen 443 ssl;
    listen [::]:443 ssl;
    ssl_certificate     /etc/letsencrypt/live/${DOCS_SUB}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOCS_SUB}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
server {
    listen 80; listen [::]:80;
    server_name ${DOCS_SUB};
    return 301 https://\$host\$request_uri;
}
DOCS
fi

systemctl enable --now redis-server supervisor nginx
supervisorctl reread || true; supervisorctl update || true
supervisorctl start all || true

nginx -t
systemctl reload nginx

# ===== TLS =====
if [[ -n "$EMAIL" ]]; then
  certbot --nginx -d "${SITE}" -m "${EMAIL}" -n --agree-tos --redirect || true
  if [[ -n "$DOCS_SUB" ]]; then
    certbot --nginx -d "${DOCS_SUB}" -m "${EMAIL}" -n --agree-tos --redirect || true
  fi
fi
nginx -t && systemctl reload nginx

# ===== finalize =====
su - frappe -s /bin/bash -lc "
  cd /home/frappe/frappe-bench
  ${BENCH_BIN} --site '${SITE}' clear-cache
  ${BENCH_BIN} --site '${SITE}' clear-website-cache
  ${BENCH_BIN} restart
"

echo "------------------------------------------------------------"
echo " ✅ Done. Login: https://${SITE}  (Administrator / ${ADMIN_PW})"
[[ -n "$DOCS_SUB" ]] && echo " ✅ Docs : https://${DOCS_SUB}"
echo "------------------------------------------------------------"
