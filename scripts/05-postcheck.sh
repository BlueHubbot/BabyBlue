#!/usr/bin/env bash
set -euo pipefail
cd /tmp/BabyBlue
if [ -f .env ]; then
  set -o allexport
  . .env
  set +o allexport
fi

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
if [[ -n "${SITE:-}" ]]; then
  curl -kI "https://$SITE" | head -20 || true
fi
if [[ -n "${DOCS_SITE:-}" ]]; then
  curl -kI "https://$DOCS_SITE" | head -20 || true
fi

echo "=== bench list-apps ==="
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"
  cd "'"$BENCH_HOME"'"
  bench --site "'"$SITE"'" list-apps
' || true

echo "=== ownership check (frappe:frappe) ==="
find "$BENCH_HOME" -maxdepth 2 -type d -printf "%u:%g %p\n" | head -20
