#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT}/install/.env"

apt-get update -y && apt-get install -y ca-certificates curl sudo tar python3 python3-venv python3-pip pipx \
  mariadb-server redis-server nginx supervisor wkhtmltopdf

systemctl enable --now nginx redis-server supervisor

# assemble split archives
assemble(){ base="$1"; out="$2"; parts=( "${base}".part-* ); [ -e "${parts[0]}" ] || return 0; cat "${base}".part-* > "${out}"; }
mkdir -p /opt/_rehydrate
assemble "${ROOT}/vendor/apps/frappe.tar.gz"  /opt/_rehydrate/frappe.tar.gz  || true
assemble "${ROOT}/vendor/apps/erpnext.tar.gz" /opt/_rehydrate/erpnext.tar.gz || true
assemble "${ROOT}/vendor/apps/hrms.tar.gz"    /opt/_rehydrate/hrms.tar.gz    || true
assemble "${ROOT}/vendor/sites_assets.tar.gz" /opt/_rehydrate/sites_assets.tar.gz || true

# wheels
WHEELS_APPS="${ROOT}/vendor/wheels/apps"
WHEELS_BENCH="${ROOT}/vendor/wheels/bench"

# user
id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
echo 'frappe ALL=(ALL) NOPASSWD:ALL' >/etc/sudoers.d/frappe

# bench from wheelhouse (pipx)
export PIP_NO_INDEX=1
pipx install frappe-bench --pip-args="--no-index --find-links ${WHEELS_BENCH}" || true

# init bench (no net)
su - frappe -c "test -d ~/frappe-bench || bench init --frappe-branch version-15 frappe-bench --skip-assets"

# unpack apps + install editable from local, wheels from repo
for app in frappe erpnext hrms; do
  tgz="/opt/_rehydrate/${app}.tar.gz"; [ -f "$tgz" ] || continue
  su - frappe -c "rm -rf ~/frappe-bench/apps/${app}; mkdir -p ~/frappe-bench/apps/${app}"
  tar -xzf "$tgz" -C /home/frappe/frappe-bench/apps/
  chown -R frappe:frappe /home/frappe/frappe-bench/apps/${app}
  su - frappe -c "source ~/frappe-bench/env/bin/activate && pip install -e ~/frappe-bench/apps/${app} --no-index --find-links ${WHEELS_APPS}"
done

# site ensure
su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} version >/dev/null 2>&1 || bench new-site ${DOMAIN} --admin-password '${ADMIN_PW}' --mariadb-root-password '${DB_ROOT_PW}' --no-mariadb-socket"
su - frappe -c "cd ~/frappe-bench; bench use ${DOMAIN}; bench set-config -g default_site ${DOMAIN}; bench --site ${DOMAIN} set-config host_name https://${DOMAIN}"

# install apps
su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} list-apps | grep -qi erpnext || bench --site ${DOMAIN} install-app erpnext"
if [ "${INSTALL_HRMS:-0}" = "1" ] && [ -d /home/frappe/frappe-bench/apps/hrms ]; then
  su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} list-apps | grep -qi hrms || bench --site ${DOMAIN} install-app hrms"
fi

# inject built assets (optional)
[ -f /opt/_rehydrate/sites_assets.tar.gz ] && tar -xzf /opt/_rehydrate/sites_assets.tar.gz -C /home/frappe/frappe-bench/sites/ && chown -R frappe:frappe /home/frappe/frappe-bench/sites/assets

# supervisor + nginx from repo tpl or bench
ln -sf /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf || true
supervisorctl reread || true && supervisorctl update || true

TPL="${ROOT}/assets/nginx/frappe-bench.conf.tpl"
if [ -f "$TPL" ]; then
  env DOMAIN="${DOMAIN}" envsubst '${DOMAIN}' < "$TPL" > "/etc/nginx/conf.d/frappe-bench.conf"
else
  su - frappe -c "cd ~/frappe-bench; yes | bench setup nginx"
fi
nginx -t && systemctl reload nginx
bash "$ROOT/install/ssl_auto.sh" || true

# TLS fallback (pure repo path = snakeoil; real cert = جداگانه)
apt-get install -y ssl-cert
sed -i "s|ssl_certificate .*|ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;|g" /etc/nginx/conf.d/frappe-bench.conf || true
sed -i "s|ssl_certificate_key .*|ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;|g" /etc/nginx/conf.d/frappe-bench.conf || true
nginx -t && systemctl reload nginx
bash "$ROOT/install/ssl_auto.sh" || true

# finalize
su - frappe -c "cd ~/frappe-bench; bench build --force || true; bench restart; bench --site ${DOMAIN} enable-scheduler || true"
echo "[✓] Offline rehydrate done for ${DOMAIN}"
