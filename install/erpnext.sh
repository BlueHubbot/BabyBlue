#!/usr/bin/env bash
set -euo pipefail
: "${DOMAIN:?}"; : "${EMAIL:?}"; : "${ADMIN_PW:?}"; : "${DB_ROOT_PW:?}"
DOCS_DOMAIN="${DOCS_DOMAIN:-}"; FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-15}"; ERPNEXT_BRANCH="${ERPNEXT_BRANCH:-version-15}"
HRMS_BRANCH="${HRMS_BRANCH:-version-15}"; INSTALL_HRMS="${INSTALL_HRMS:-0}"
as_f(){ su - frappe -c "$*"; }

# bench init
[ -d /home/frappe/frappe-bench ] || as_f "bench init --frappe-branch ${FRAPPE_BRANCH} frappe-bench"

# get-apps (skip if dir exists)
as_f "cd ~/frappe-bench && [ ! -d apps/erpnext ] && bench get-app --branch ${ERPNEXT_BRANCH} erpnext || true"
[ "$INSTALL_HRMS" = "1" ] && as_f "cd ~/frappe-bench && [ ! -d apps/hrms ] && bench get-app --branch ${HRMS_BRANCH} hrms || true"

# site ensure + default
as_f "cd ~/frappe-bench && bench --site ${DOMAIN} version" >/dev/null 2>&1 \
|| as_f "cd ~/frappe-bench && bench new-site ${DOMAIN} --admin-password '${ADMIN_PW}' --mariadb-root-password '${DB_ROOT_PW}' --no-mariadb-socket"
as_f "cd ~/frappe-bench && bench use ${DOMAIN}"
as_f "cd ~/frappe-bench && bench set-config -g default_site ${DOMAIN}"

# install apps
as_f "cd ~/frappe-bench && bench --site ${DOMAIN} list-apps | grep -qi erpnext || bench --site ${DOMAIN} install-app erpnext"
[ "$INSTALL_HRMS" = "1" ] && as_f "cd ~/frappe-bench && bench --site ${DOMAIN} list-apps | grep -qi hrms || bench --site ${DOMAIN} install-app hrms"

# build + caches
as_f "cd ~/frappe-bench && yarn --version >/dev/null 2>&1 || npm i -g yarn >/dev/null || true"
as_f "cd ~/frappe-bench && bench build --force && bench clear-cache && bench clear-website-cache"

# production (non-interactive) + fallbacks
su - frappe -c 'pipx runpip frappe-bench install -U "ansible==12.*"' || true
sudo -H bash -lc 'export PATH=/home/frappe/.local/bin:$PATH; cd /home/frappe/frappe-bench; yes | bench setup production frappe || true; bench setup supervisor || true; bench setup nginx || true'
ln -sf /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf || true
systemctl enable --now supervisor nginx || true
supervisorctl reread || true && supervisorctl update || true

# host_name + SSL
as_f "cd ~/frappe-bench && bench --site ${DOMAIN} set-config host_name https://${DOMAIN}"
sudo certbot --nginx -d "${DOMAIN}" -m "${EMAIL}" --agree-tos --redirect -n || true
[ -n "${DOCS_DOMAIN}" ] && sudo certbot --nginx -d "${DOCS_DOMAIN}" -m "${EMAIL}" --agree-tos --redirect -n || true
sudo nginx -t && sudo systemctl reload nginx || true

# finalize
as_f "cd ~/frappe-bench && bench --site ${DOMAIN} enable-scheduler" || true
as_f "cd ~/frappe-bench && bench restart"
echo "[✓] erpnext OK"
bash install/selftest.sh || true
cat "$ROOT/install/nginx/upstreams.tpl" > /etc/nginx/conf.d/frappe-bench-upstreams.conf || true
