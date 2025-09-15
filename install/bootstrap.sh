#!/usr/bin/env bash
set -euo pipefail
[ "$(id -u)" -eq 0 ] || exec sudo -E bash "$0" "$@"

# 1) الزامات سیستم (Supervisor/Redis/Nginx/bench/pipx/…)
bash "$(dirname "$0")/preflight.sh"

# 2) مستندات: اگر DOCS_DOMAIN ست شده باشد، بساز/تنظیم کن
if [ -n "${DOCS_DOMAIN:-}" ]; then
  bash "$(dirname "$0")/docs.sh"
else
  echo "SKIP docs (set DOCS_DOMAIN to enable)"
fi

echo "Preflight + Docs done. Next step: add full ERPNext install/restore steps here."
