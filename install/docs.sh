#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_ROOT="${DOCS_ROOT:-/var/www/docs}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"
PARTS=(${ROOT}/assets/docs/docs_static.tar.gz.part-*)
[ -e "${PARTS[0]}" ] || { echo "[!] missing parts: assets/docs/docs_static.tar.gz.part-*"; exit 3; }

install -d "$DOCS_ROOT"
tmp="$(mktemp -u)"; cat "${ROOT}"/assets/docs/docs_static.tar.gz.part-* > "${tmp}.tar.gz"
tar -xzf "${tmp}.tar.gz" -C "$DOCS_ROOT"; rm -f "${tmp}.tar.gz"
chown -R www-data:www-data "$DOCS_ROOT"

if [ -n "$DOCS_DOMAIN" ]; then
  export DOCS_ROOT DOCS_DOMAIN
  envsubst '${DOCS_DOMAIN} ${DOCS_ROOT}' < "${ROOT}/install/nginx/docs.tpl" > "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf"
  ln -sf "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf" "/etc/nginx/sites-enabled/docs-${DOCS_DOMAIN}.conf"
fi

nginx -t && systemctl reload nginx || true
echo "[✓] docs OK"
