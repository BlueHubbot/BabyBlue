#!/usr/bin/env bash
set -euo pipefail
RED=$(printf '\033[31m'); GRN=$(printf '\033[32m'); YEL=$(printf '\033[33m'); NC=$(printf '\033[0m')
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; source "$ROOT/install/.env" || { echo "missing install/.env"; exit 1; }
ok(){ echo -e "${GRN}[✓]${NC} $*"; }; warn(){ echo -e "${YEL}[!]${NC} $*"; }; fail(){ echo -e "${RED}[✗]${NC} $*"; EXIT=1; }
EXIT=0

# سرویس‌ها
systemctl is-active --quiet supervisor && ok "supervisor active" || fail "supervisor inactive"
systemctl is-active --quiet nginx && ok "nginx active" || fail "nginx inactive"
systemctl is-active --quiet redis-server && ok "redis active" || fail "redis inactive"

# سایت
su - frappe -c "cd ~/frappe-bench && bench --site ${DOMAIN} version" >/dev/null 2>&1 && ok "site exists: $DOMAIN" || fail "site missing: $DOMAIN"
su - frappe -c "cd ~/frappe-bench && bench use ${DOMAIN} && bench set-config -g default_site ${DOMAIN}" >/dev/null 2>&1 || warn "default_site not set"

# nginx
grep -R "server_name ${DOMAIN}" -n /etc/nginx >/dev/null 2>&1 && ok "nginx server_name ${DOMAIN}" || fail "nginx missing server_name ${DOMAIN}"
nginx -t >/dev/null 2>&1 && ok "nginx config valid" || fail "nginx config invalid"

# TLS
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  CN=$(openssl x509 -noout -subject -in "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" | sed -n 's/.*CN = //p')
  [ "$CN" = "$DOMAIN" ] && ok "TLS CN=${CN}" || warn "TLS CN=${CN} != ${DOMAIN}"
else warn "No LE cert for ${DOMAIN}"; fi

# بک‌اندها
curl -fsSIk -H "Host: ${DOMAIN}" http://127.0.0.1:8000 >/dev/null && ok "gunicorn :8000 up" || fail "gunicorn :8000 down"
curl -fsSIk https://${DOMAIN} >/dev/null && ok "HTTPS ${DOMAIN} up" || fail "HTTPS ${DOMAIN} down"

# داکس
if [ -n "${DOCS_DOMAIN:-}" ]; then
  curl -fsSIk https://${DOCS_DOMAIN} >/dev/null && ok "Docs HTTPS ${DOCS_DOMAIN} up" || warn "Docs HTTPS ${DOCS_DOMAIN} down"
fi
exit $EXIT
