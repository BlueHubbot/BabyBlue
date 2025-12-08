#03-nginx-render.sh
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

ERP_CONF="/etc/nginx/sites-available/erp-${SITE}.conf"
ERP_LINK="/etc/nginx/sites-enabled/erp-${SITE}.conf"

# رندر vhost اصلی ERP
python3 - "$REPO_DIR" "$SITE" "$ERP_CONF" <<'PY'
import sys, os
repo, site, out_path = sys.argv[1:]
tpl_path = os.path.join(repo, "templates", "nginx", "erp.conf.j2")
with open(tpl_path) as f:
    txt = f.read()
txt = txt.replace("{{ site_domain }}", site).replace("{{ site_name }}", site)
with open(out_path, "w") as f:
    f.write(txt)
PY

ln -sfn "$ERP_CONF" "$ERP_LINK"

# رندر vhost داکس اگر تعریف شده باشد
if [[ -n "${DOCS_SITE:-}" ]]; then
  DOCS_CONF="/etc/nginx/sites-available/docs-${DOCS_SITE}.conf"
  DOCS_LINK="/etc/nginx/sites-enabled/docs-${DOCS_SITE}.conf"

  python3 - "$REPO_DIR" "$DOCS_SITE" "$DOCS_ROOT" "$DOCS_CONF" <<'PY'
import sys, os
repo, docs_domain, docs_root, out_path = sys.argv[1:]
tpl_path = os.path.join(repo, "templates", "nginx", "docs.conf.j2")
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

# حذف default برای جلوگیری از conflict
if [[ -e /etc/nginx/sites-enabled/default ]]; then
  rm -f /etc/nginx/sites-enabled/default
fi



# --- fix permissions for nginx to read assets ---
chmod 755 /home/frappe
chmod -R o+rX /home/frappe/frappe-bench/sites/assets

# --- test and reload nginx ---
nginx -t && systemctl reload nginx

