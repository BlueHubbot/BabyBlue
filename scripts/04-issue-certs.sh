#04-issue-certs.sh
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

DOMAINS=(-d "$SITE")
if [[ -n "${DOCS_SITE:-}" ]]; then
  DOMAINS+=(-d "$DOCS_SITE")
fi

certbot --nginx --non-interactive --agree-tos -m "$SSL_EMAIL" "${DOMAINS[@]}" --redirect

nginx -t
systemctl reload nginx
