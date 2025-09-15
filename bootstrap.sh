#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL="${ROOT}/install"
[ -f "${INSTALL}/.env" ] && . "${INSTALL}/.env"
: "${DOMAIN:?export DOMAIN first}"
: "${EMAIL:?export EMAIL first}"
: "${ADMIN_PW:?export ADMIN_PW first}"
: "${DB_ROOT_PW:?export DB_ROOT_PW first}"
export DOMAIN EMAIL ADMIN_PW DB_ROOT_PW DOCS_DOMAIN INSTALL_HRMS FRAPPE_BRANCH ERPNEXT_BRANCH HRMS_BRANCH
STEPS="${STEPS:-preflight,docs,erpnext}"
IFS=',' read -r -a arr <<<"$STEPS"
for step in "${arr[@]}"; do
  case "$step" in
    preflight) bash "${INSTALL}/preflight.sh" ;;
    docs)      bash "${INSTALL}/docs.sh" ;;
    erpnext)   bash "${INSTALL}/erpnext.sh" ;;
    *) echo "Unknown step: $step"; exit 2;;
  esac
done
echo "[✓] All steps completed."
