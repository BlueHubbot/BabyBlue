#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_ROOT="${DOCS_ROOT:-/var/www/docs}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"
PARTS=(${ROOT}/assets/docs/docs_static.tar.gz.part-*)
if [ -e "${PARTS[0]}" ]; then
  install -d "$DOCS_ROOT"
  tmp="$(mktemp -u)"; cat "${ROOT}"/assets/docs/docs_static.tar.gz.part-* > "${tmp}.tar.gz"
  tar -xzf "${tmp}.tar.gz" -C "$DOCS_ROOT"; rm -f "${tmp}.tar.gz"
  chown -R www-data:www-data "$DOCS_ROOT"
fi
if [ -n "$DOCS_DOMAIN" ]; then
  export DOCS_ROOT DOCS_DOMAIN
  envsubst '${DOCS_DOMAIN} ${DOCS_ROOT}' < "${ROOT}/install/nginx/docs.tpl" > "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf"
  ln -sf "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf" "/etc/nginx/sites-enabled/docs-${DOCS_DOMAIN}.conf"
  nginx -t && systemctl reload nginx || true
  certbot --nginx -d "$DOCS_DOMAIN" -m "${EMAIL:-admin@example.com}" --agree-tos --redirect -n || true
  nginx -t && systemctl reload nginx || true
fi
echo "[✓] docs OK"
