#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "ERROR at line $LINENO"; exit 1' ERR

MAIN=""
DOCS=""
SNAP_ARG="${SNAPSHOT:-}"
ISSUE_CERT="${ISSUE_CERT:-0}"

usage(){ echo "Usage: $0 --main-domain <MAIN> [--docs-domain <DOCS>] [--snapshot <path>] [--issue-cert 0|1]"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --main-domain) MAIN="$2"; shift 2;;
    --docs-domain) DOCS="${2:-}"; shift 2;;
    --snapshot)    SNAP_ARG="$2"; shift 2;;
    --issue-cert)  ISSUE_CERT="$2"; shift 2;;
    -h|--help)     usage; exit 0;;
    --) shift; break;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done
[[ -n "$MAIN" ]] || { echo "ERR: --main-domain is required"; usage; exit 2; }

pick_latest_dir() { local base="$1"; [[ -d "$base" ]] || return 1; ls -1d "$base"/* 2>/dev/null | sort | tail -n1 || true; }

SNAP=""
if [[ -n "$SNAP_ARG" ]]; then SNAP="$SNAP_ARG"; else
  for B in /srv/babyblue/artifacts/data "$(pwd)/artifacts/data" "$(cd "$(dirname "$0")/.." && pwd)/artifacts/data"; do
    d="$(pick_latest_dir "$B" || true)"; [[ -n "$d" ]] && SNAP="$d" && break
  done
fi
[[ -n "$SNAP" ]] || { echo "ERR: no snapshot found"; exit 1; }

if [[ ! -f "$SNAP/bench.tar.gz" ]] && ls "$SNAP"/bench.tar.gz.*.part >/dev/null 2>&1; then
  cat "$SNAP"/bench.tar.gz.*.part > "$SNAP/bench.tar.gz"
fi
[[ -f "$SNAP/bench.tar.gz" ]] || { echo "ERR: $SNAP/bench.tar.gz missing"; exit 1; }

tar -C / -xzf "$SNAP/bench.tar.gz"

id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
install -d -m 755 /home/frappe/.local/bin
cat >/home/frappe/.local/bin/bench <<'BCH'
#!/usr/bin/env bash
exec /home/frappe/frappe-bench/env/bin/python -m frappe.utils.bench_helper "$@"
BCH
chmod +x /home/frappe/.local/bin/bench
chown -R frappe:frappe /home/frappe

ln -sfn /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf
sed -ri 's@^(directory=)/home/frappe/frappe-bench$@\1/home/frappe/frappe-bench/sites@' /home/frappe/frappe-bench/config/supervisor.conf || true

systemctl enable --now mariadb redis-server nginx supervisor 2>/dev/null || true
systemctl restart supervisor
sleep 1
supervisorctl reread || true
supervisorctl update  || true

SITE_DIR="baby.bluenet.click"
echo "$SITE_DIR" >/home/frappe/frappe-bench/sites/currentsite.txt
[[ -e "/home/frappe/frappe-bench/sites/$MAIN" ]] || ln -s "$SITE_DIR" "/home/frappe/frappe-bench/sites/$MAIN" || true
chown -h frappe:frappe "/home/frappe/frappe-bench/sites/$MAIN" || true
sed -i "s#https://baby\.bluenet\.click#https://$MAIN#g" "/home/frappe/frappe-bench/sites/$SITE_DIR/site_config.json" || true

if command -v jq >/dev/null 2>&1; then
  DB_NAME="$(jq -r '.db_name' "/home/frappe/frappe-bench/sites/$SITE_DIR/site_config.json")"
else
  DB_NAME=""
fi
if [[ -n "${DB_NAME:-}" ]]; then
  if ! mysql -NBe "SHOW DATABASES LIKE '${DB_NAME}'" | grep -q "${DB_NAME}"; then
    [[ -f "$SNAP/db-all.sql.gz" ]] && zcat "$SNAP/db-all.sql.gz" | mysql
  fi
fi

[[ -f /etc/nginx/sites-enabled/erp-baby.conf ]] && sed -i "s/baby\.bluenet\.click/$MAIN/g" /etc/nginx/sites-enabled/erp-baby.conf
if [[ -n "$DOCS" && -f /etc/nginx/sites-enabled/bluedoc.conf ]]; then
  sed -i "s/docs\.bluenet\.click/$DOCS/g" /etc/nginx/sites-enabled/bluedoc.conf
fi

install -d /var/www/docs_en
[[ -f "$SNAP/docs_en.tar.gz" ]] && tar -C / -xzf "$SNAP/docs_en.tar.gz"
install -d /srv/bluedoc
[[ -f "$SNAP/docs_mirror.tar.gz" ]] && tar -C / -xzf "$SNAP/docs_mirror.tar.gz"

sed -ri 's@^\s*include\s+/etc/nginx/snippets/bluedocs_mirror\.conf;@# &@' /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default 2>/dev/null || true

if [[ "${ISSUE_CERT}" == "1" ]]; then
  certbot --nginx -n --agree-tos --register-unsafely-without-email -d "$MAIN" $( [[ -n "$DOCS" ]] && printf ' -d %s' "$DOCS" ) || true
fi

nginx -t && systemctl reload nginx
systemctl restart supervisor
sleep 1

echo "== CURL TESTS =="
curl -sI "https://$MAIN" | head -n1 || true
[[ -n "$DOCS" ]] && curl -sI "https://$DOCS" | head -n1 || true
echo "DONE (snapshot: $SNAP)"
