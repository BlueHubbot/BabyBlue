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

ERP_CONF="/etc/nginx/sites-available/erp-${SITE}.conf"
ERP_LINK="/etc/nginx/sites-enabled/erp-${SITE}.conf"

python3 - <<PY
import os
repo = os.environ["REPO_DIR"]
site = os.environ["SITE"]
tpl_path = os.path.join(repo, "templates", "nginx", "erp.conf.j2")
out_path = os.environ["ERP_CONF"]

with open(tpl_path) as f:
    txt = f.read()

txt = txt.replace("{{ site_domain }}", site).replace("{{ site_name }}", site)

with open(out_path, "w") as f:
    f.write(txt)
PY

ln -sfn "$ERP_CONF" "$ERP_LINK"

if [[ -n "${DOCS_SITE:-}" ]]; then
  DOCS_CONF="/etc/nginx/sites-available/docs-${DOCS_SITE}.conf"
  DOCS_LINK="/etc/nginx/sites-enabled/docs-${DOCS_SITE}.conf"

  python3 - <<PY
import os
repo = os.environ["REPO_DIR"]
docs_domain = os.environ["DOCS_SITE"]
docs_root = os.environ["DOCS_ROOT"]
tpl_path = os.path.join(repo, "templates", "nginx", "docs.conf.j2")
out_path = os.environ["DOCS_CONF"]

with open(tpl_path) as f:
    txt = f.read()

txt = (txt
       .replace("{{ docs_domain }}", docs_domain)
       .replace("{{ docs_root }}", docs_root))

with open(out_path, "w") as f:
    f.write(txt)
PY

  ln -sfn "$DOCS_CONF" "$DOCS_LINK"
fi

if [[ -e /etc/nginx/sites-enabled/default ]]; then
  rm -f /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl reload nginx
