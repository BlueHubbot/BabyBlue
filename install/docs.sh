#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Run as root"; exit 1; }

DOCS_DOMAIN="${DOCS_DOMAIN:?set DOCS_DOMAIN}"
EMAIL="${EMAIL:-admin@${DOCS_DOMAIN#*.}}"
DOCROOT="/var/www/docs"
BASE="https://docs.erpnext.com"

apt-get update -y
apt-get install -y nginx curl || true

mkdir -p "$DOCROOT"
curl -fsSL "${BASE}/" -o "$DOCROOT/index.html"

# کشیدن CSS/JS های صفحه اصلی
grep -oE 'href="/[^"]+\.css[^"]*"|src="/[^"]+\.js[^"]*"' "$DOCROOT/index.html" \
| cut -d'"' -f2 | sed 's|\?.*$||' | sort -u | while read -r p; do
  mkdir -p "$(dirname "$DOCROOT$p")"
  curl -fsSL "${BASE}${p}" -o "$DOCROOT$p" || true
done

# اسکریپت خارجی Frappe Cloud (لوکال)
mkdir -p "$DOCROOT/frappecloud.com/js"
curl -fsSL https://frappecloud.com/js/script.js -o "$DOCROOT/frappecloud.com/js/script.js" || true
sed -i 's#//frappecloud.com/js/script.js#/frappecloud.com/js/script.js#g' "$DOCROOT/index.html"

chown -R www-data:www-data "$DOCROOT"

# سرور Nginx برای docs + fallback به docs.erpnext.com
cat > /etc/nginx/conf.d/docs.conf <<NGX
server {
    server_name ${DOCS_DOMAIN};
    root ${DOCROOT};
    index index.html;

    location / {
        try_files \$uri \$uri/ @mirror_fallback;
        add_header Cache-Control "public, max-age=300";
        expires 5m;
    }
    location @mirror_fallback {
        proxy_set_header Host docs.erpnext.com;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_pass https://docs.erpnext.com;
    }

    access_log /var/log/nginx/docs.access.log;
    error_log  /var/log/nginx/docs.error.log;

    listen 80;
}
NGX

nginx -t && systemctl reload nginx

# HTTPS
if command -v certbot >/dev/null 2>&1; then
  certbot --nginx -d "$DOCS_DOMAIN" -m "$EMAIL" -n --agree-tos --redirect || true
  nginx -t && systemctl reload nginx || true
fi

echo "OK: docs at https://${DOCS_DOMAIN}"
