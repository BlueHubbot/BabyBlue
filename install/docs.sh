#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_ROOT="${DOCS_ROOT:-/var/www/docs}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"
TARBALL="${ROOT}/assets/docs/docs_static.tar.gz"
[ -f "$TARBALL" ] || { echo "[!] missing assets/docs/docs_static.tar.gz"; exit 3; }
install -d "$DOCS_ROOT"
tar -xzf "$TARBALL" -C "$DOCS_ROOT"
chown -R www-data:www-data "$DOCS_ROOT"
if [ -n "$DOCS_DOMAIN" ]; then
  export DOCS_ROOT DOCS_DOMAIN
  envsubst '${DOCS_DOMAIN} ${DOCS_ROOT}' < "${ROOT}/install/nginx/docs.tpl" > "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf"
  ln -sf "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf" "/etc/nginx/sites-enabled/docs-${DOCS_DOMAIN}.conf"
fi
nginx -t && systemctl reload nginx || true
echo "[✓] docs OK"
