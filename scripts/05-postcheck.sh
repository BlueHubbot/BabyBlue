#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [[ ! -f .env ]]; then
  echo ".env not found; copy .env.example and edit first" >&2
  exit 1
fi

set -o allexport
# shellcheck disable=SC1091
source .env
set +o allexport

echo "=== supervisor status ==="
supervisorctl status || true

echo "=== nginx test ==="
nginx -t || true

echo "=== HTTP(S) checks ==="
curl -kIs "http://$SITE"       | head -1 || true
curl -kIs "https://$SITE"      | head -1 || true
curl -kIs "https://$SITE/assets/js/frappe.min.js" | head -1 || true

if [[ -n "${DOCS_SITE:-}" ]]; then
  curl -kIs "https://$DOCS_SITE" | head -1 || true
fi

echo "=== bench list-apps ==="
sudo -u "$FRAPPE_USER" -H bash -lc "
  export PATH=\"\$HOME/.local/bin:\$PATH\"
  cd \"$BENCH_HOME\"
  bench --site \"$SITE\" list-apps
" || true

echo "=== ownership check (frappe:frappe) ==="
find "$BENCH_HOME" -maxdepth 2 -type d -printf '%u:%g %p\n' | head -20
