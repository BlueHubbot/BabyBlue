#!/usr/bin/env bash
set -Eeuo pipefail

usage(){ echo "Usage: $0 --main-domain MAIN --docs-domain DOCS"; exit 2; }
MAIN=""; DOCS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --main-domain) MAIN="$2"; shift 2;;
    --docs-domain) DOCS="$2"; shift 2;;
    *) usage;;
  esac
done
[ -n "$MAIN" ] && [ -n "$DOCS" ] || usage

# 0) پیش‌نیاز سرویس‌ها
systemctl enable --now mariadb redis-server nginx supervisor 2>/dev/null || true

# 1) آخرین اسنپ‌شات
SNAP="$(ls -d /srv/babyblue/artifacts/data/* 2>/dev/null | sort | tail -n1 || true)"
[ -n "$SNAP" ] || { echo "[ERR] No snapshot under /srv/babyblue/artifacts/data"; exit 1; }

# اگر bench.tar.gz تکه‌تکه است → بساز
if [ ! -f "$SNAP/bench.tar.gz" ] && ls "$SNAP"/bench.tar.gz.*.part >/dev/null 2>&1; then
  cat "$SNAP"/bench.tar.gz.*.part > "$SNAP/bench.tar.gz"
fi
[ -f "$SNAP/bench.tar.gz" ] || { echo "[ERR] bench.tar.gz missing"; exit 1; }

# 2) ریستور بنچ
tar -C / -xzf "$SNAP/bench.tar.gz"

# 3) کاربر و bench shim
id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
install -d -m 755 /home/frappe/.local/bin
cat >/home/frappe/.local/bin/bench <<'B'
#!/usr/bin/env bash
exec /home/frappe/frappe-bench/env/bin/python -m frappe.utils.bench_helper "$@"
B
chmod +x /home/frappe/.local/bin/bench
chown -R frappe:frappe /home/frappe

# 4) سایت و دامنه‌ها
SITE_DIR="/home/frappe/frappe-bench/sites"
SITE="baby.bluenet.click"
echo "$SITE" > "$SITE_DIR/currentsite.txt"
[ -e "$SITE_DIR/$MAIN" ] || ln -s "$SITE" "$SITE_DIR/$MAIN"
chown -h frappe:frappe "$SITE_DIR/$MAIN" || true
# host_name
if [ -f "$SITE_DIR/$SITE/site_config.json" ]; then
  sed -i "s#https://baby\.bluenet\.click#https://$MAIN#g" "$SITE_DIR/$SITE/site_config.json"
fi

# 5) Nginx vhosts (اگر نبودند، بساز)
ERP_V=/etc/nginx/sites-enabled/erp-baby.conf
DOC_V=/etc/nginx/sites-enabled/bluedoc.conf

if [ ! -f "$ERP_V" ]; then
cat >"$ERP_V" <<NG
server {
    server_name $MAIN;
    access_log /var/log/nginx/erp_access.log main;
    error_log  /var/log/nginx/erp_error.log;
    location /assets {
        try_files \$uri =404;
        root /home/frappe/frappe-bench/sites;
    }
    location / { try_files \$uri @webserver; }
    location @webserver {
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Origin \$scheme://\$http_host;
        proxy_set_header X-Use-X-Accel-Redirect true;
        proxy_set_header X-Frappe-Site-Name $SITE;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 120s;
        proxy_pass http://127.0.0.1:8000;
    }
    location /socket.io {
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Frappe-Site-Name $SITE;
        proxy_read_timeout 120s;
        proxy_pass http://127.0.0.1:9000/socket.io;
    }
    listen 80;
}
NG
fi

# Docs root
install -d /var/www/docs_en
# اگر آرتیفکت docs هست، ریستور کن
if [ -f "$SNAP/docs_en.tar.gz" ]; then
  tar -C / -xzf "$SNAP/docs_en.tar.gz"
else
  [ -f /var/www/docs_en/index.html ] || echo "Docs placeholder" >/var/www/docs_en/index.html
fi

if [ ! -f "$DOC_V" ]; then
cat >"$DOC_V" <<NG
server {
    listen 80;
    server_name $DOCS;
    root /var/www/docs_en;
    index index.html;
    location = / { try_files /index.html =404; }
    location / { try_files \$uri \$uri/ /index.html; }
    location ^~ /assets/ { access_log off; try_files \$uri =404; add_header Cache-Control "public, max-age=31536000, immutable"; }
    location = /service-worker.js { return 410; }
}
NG
fi

# 6) Supervisor link و ریستارت
ln -sfn /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf
systemctl restart supervisor
sleep 2

# 7) Nginx test + HTTPS (اگر امکانش هست)
nginx -t && systemctl reload nginx

if command -v certbot >/dev/null 2>&1; then
  certbot --nginx -n --agree-tos --register-unsafely-without-email -d "$MAIN" -d "$DOCS" || true
  nginx -t && systemctl reload nginx
fi

# 8) چک‌ها
echo "== PORTS =="; ss -ltnp | egrep ':80|:443|:8000|:9000' || true
echo "== SUPERVISOR =="; supervisorctl status || true
echo "== CURL =="
echo -n "ERP  : "; curl -sI "https://$MAIN" | head -n1 || true
echo -n "DOCS : "; curl -sI "https://$DOCS" | head -n1 || true
echo "[restore] done."
