#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/install/.env"

apt-get update -y && apt-get install -y certbot python3-certbot-nginx ssl-cert
mkdir -p /var/www/letsencrypt

# ACME 80-block برای هر دامنه (idempotent)
mk_acme() {
  local D="$1"
  [ -n "$D" ] || return 0
  cat >/etc/nginx/sites-available/${D}-acme.conf <<NG
server {
  listen 80;
  server_name ${D};
  location ^~ /.well-known/acme-challenge/ { root /var/www/letsencrypt; default_type "text/plain"; try_files \$uri =404; }
  location / { return 301 https://\$host\$request_uri; }
}
NG
  ln -sf /etc/nginx/sites-available/${D}-acme.conf /etc/nginx/sites-enabled/${D}-acme.conf
}
mk_acme "$DOMAIN"
[ -n "${DOCS_DOMAIN:-}" ] && mk_acme "$DOCS_DOMAIN" || true
nginx -t && systemctl reload nginx

# اگر قبلاً LE داریم و >20 روز مونده، رد شو
has_valid_cert () {
  local D="$1" F="/etc/letsencrypt/live/${D}/fullchain.pem"
  [ -f "$F" ] || return 1
  local exp epoch_now epoch_end days_left
  exp="$(openssl x509 -in "$F" -noout -enddate | cut -d= -f2)"
  epoch_now="$(date -u +%s)"
  epoch_end="$(date -ud "$exp" +%s || echo 0)"
  days_left=$(( (epoch_end-epoch_now)/86400 ))
  [ "$days_left" -gt 20 ]
}

issue_cert () {
  local D="$1"
  has_valid_cert "$D" && { echo "[✓] cert exists & valid for $D"; return 0; }
  certbot certonly --webroot -w /var/www/letsencrypt -d "$D" -m "$EMAIL" --agree-tos -n || true
}

issue_cert "$DOMAIN"
[ -n "${DOCS_DOMAIN:-}" ] && issue_cert "$DOCS_DOMAIN" || true

# سوئیچ Nginx از snakeoil → LE (اگر صادر شد)
switch_le () {
  local D="$1"
  local PEM="/etc/letsencrypt/live/${D}/fullchain.pem"
  local KEY="/etc/letsencrypt/live/${D}/privkey.pem"
  [ -f "$PEM" ] || return 0
  # فایل‌های nginx که server_name D دارند را پچ کن
  grep -R "server_name[[:space:]]\+${D};" -l /etc/nginx 2>/dev/null | while read -r f; do
    sed -i "s|ssl_certificate .*|ssl_certificate ${PEM};|g" "$f" || true
    sed -i "s|ssl_certificate_key .*|ssl_certificate_key ${KEY};|g" "$f" || true
  done
}
switch_le "$DOMAIN"
[ -n "${DOCS_DOMAIN:-}" ] && switch_le "$DOCS_DOMAIN" || true

nginx -t && systemctl reload nginx
echo "[✓] SSL auto: done (domain(s): ${DOMAIN}${DOCS_DOMAIN:+, ${DOCS_DOMAIN}})"
