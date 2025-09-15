#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || exec sudo -E bash "$0" "$@"

# متغیرهای موردنیاز:
# DOMAIN=example.com DOCS_DOMAIN=docs.example.com EMAIL=you@example.com ADMIN_PW=**** DB_ROOT_PW=****
# (اختیاری برای ریکاوری) DB_URL=... PUB_URL=... PRIV_URL=... BACKUP_PASS=...

bash "$(dirname "$0")/preflight.sh"
if [ -n "${DOCS_DOMAIN:-}" ]; then bash "$(dirname "$0")/docs.sh"; fi
bash "$(dirname "$0")/erpnext.sh"

echo "✅ Done."
