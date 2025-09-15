#!/usr/bin/env bash
set -euo pipefail
: "${DOMAIN:?}"; : "${EMAIL:?}"; : "${ADMIN_PW:?}"; : "${DB_ROOT_PW:?}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"
FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-15}"
ERPNEXT_BRANCH="${ERPNEXT_BRANCH:-version-15}"
HRMS_BRANCH="${HRMS_BRANCH:-version-15}"
INSTALL_HRMS="${INSTALL_HRMS:-0}"
as_frappe(){ su - frappe -c "$*"; }
if [ ! -d /home/frappe/frappe-bench ]; then
  as_frappe "bench init --frappe-branch ${FRAPPE_BRANCH} frappe-bench"
fi
as_frappe "cd ~/frappe-bench && (bench ls-apps | grep -qi erpnext || bench get-app --branch ${ERPNEXT_BRANCH} erpnext)"
if [ "$INSTALL_HRMS" = "1" ]; then
  as_frappe "cd ~/frappe-bench && (bench ls-apps | grep -qi hrms || bench get-app --branch ${HRMS_BRANCH} hrms)"
fi
if ! as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} version" >/dev/null 2>&1; then
  as_frappe "cd ~/frappe-bench && bench new-site ${DOMAIN} --admin-password '${ADMIN_PW}' --mariadb-root-password '${DB_ROOT_PW}' --no-mariadb-socket"
fi
as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} list-apps | grep -qi erpnext || bench --site ${DOMAIN} install-app erpnext"
if [ "$INSTALL_HRMS" = "1" ]; then
  as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} list-apps | grep -qi hrms || bench --site ${DOMAIN} install-app hrms"
fi
as_frappe "cd ~/frappe-bench && bench build"
sudo -H bash -lc 'export PATH=/home/frappe/.local/bin:$PATH; cd /home/frappe/frappe-bench; bench setup production frappe'
systemctl enable --now supervisor nginx
certbot --nginx -d "${DOMAIN}" -m "${EMAIL}" --agree-tos --redirect -n || true
if [ -n "${DOCS_DOMAIN}" ]; then
  certbot --nginx -d "${DOCS_DOMAIN}" -m "${EMAIL}" --agree-tos --redirect -n || true
  sed -i '/server_name .*'"${DOCS_DOMAIN}"'.*/a \\tadd_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;' \
    "/etc/nginx/sites-available/docs-${DOCS_DOMAIN}.conf" || true
fi
nginx -t && systemctl reload nginx
if [ -n "${DB_URL:-}" ] || [ -n "${PUB_URL:-}" ] || [ -n "${PRIV_URL:-}" ]; then
  install -d -o frappe -g frappe /home/frappe/restore
  [ -n "${DB_URL:-}"  ] && curl -fsSL "$DB_URL"  -o /home/frappe/restore/db.sql.gz
  [ -n "${PUB_URL:-}" ] && curl -fsSL "$PUB_URL" -o /home/frappe/restore/public_files.tar.gz
  [ -n "${PRIV_URL:-}" ] && curl -fsSL "$PRIV_URL" -o /home/frappe/restore/private_files.tar.gz
  chown -R frappe:frappe /home/frappe/restore
  if [ -n "${BACKUP_PASS:-}" ]; then
    for f in /home/frappe/restore/*.enc 2>/dev/null; do [ -e "$f" ] || break
      openssl enc -d -aes-256-cbc -pbkdf2 -in "$f" -out "${f%.enc}" -pass pass:"$BACKUP_PASS"; rm -f "$f"
    done
  fi
  as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} restore /home/frappe/restore/db.sql.gz --mariadb-root-password '${DB_ROOT_PW}' --force" || true
  as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} migrate" || true
  [ -f /home/frappe/restore/public_files.tar.gz ]  && as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} import-files /home/frappe/restore/public_files.tar.gz"
  [ -f /home/frappe/restore/private_files.tar.gz ] && as_frappe "cd ~/frappe-bench && bench --site ${DOMAIN} import-files /home/frappe/restore/private_files.tar.gz --private"
fi
echo "[✓] erpnext OK"
