#!/usr/bin/env bash
set -Eeuo pipefail
ERP_DOMAIN="${ERP_DOMAIN:-}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"
ADMIN_PASS="${ADMIN_PASS:-}"
apt-get update -y
apt-get install -y curl xz-utils git
"$(cd "$(dirname "$0")" && pwd)/restore.sh"
echo "OK: base restored. Next: ERPNext/MkDocs install from artifacts (to be added)."
