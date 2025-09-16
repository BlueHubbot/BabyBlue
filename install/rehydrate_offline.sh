#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT}/install/.env"

# نصب حداقل پیش‌نیازها (بدون تکیه بر اینترنت برای پایتون پکیج‌ها)
apt(){ DEBIAN_FRONTEND=noninteractive apt-get -y "$@"; }
apt update
apt install ca-certificates curl gnupg lsb-release sudo unzip tar jq \
  git locales tzdata build-essential python3 python3-venv python3-pip pipx \
  mariadb-server redis-server nginx supervisor wkhtmltopdf -y

systemctl enable --now nginx redis-server supervisor

# Assemble پارت‌ها
assemble() { base="$1"; out="$2"; parts=( "${base}".part-* ); [ -e "${parts[0]}" ] || return 0; cat "${base}".part-* > "${out}"; }
mkdir -p /opt/_rehydrate
assemble "${ROOT}/vendor/apps/frappe.tar.gz"  /opt/_rehydrate/frappe.tar.gz  || true
assemble "${ROOT}/vendor/apps/erpnext.tar.gz" /opt/_rehydrate/erpnext.tar.gz || true
assemble "${ROOT}/vendor/apps/hrms.tar.gz"    /opt/_rehydrate/hrms.tar.gz    || true
assemble "${ROOT}/vendor/sites_assets.tar.gz" /opt/_rehydrate/sites_assets.tar.gz || true

# نصب bench فقط از wheelhouse ریپو
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="${ROOT}/vendor/wheels"
pipx install "frappe-bench" --pip-args="--no-index --find-links ${ROOT}/vendor/wheels" || true

# ایجاد کاربر frappe (اگر نبود)
id -u frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
echo 'frappe ALL=(ALL) NOPASSWD:ALL' >/etc/sudoers.d/frappe

# bench init (بدون گرفتن از اینترنت)
su - frappe -c "test -d ~/frappe-bench || bench init --frappe-branch version-15 frappe-bench --skip-assets"

# جایگذاری اپ‌ها از آرشیوهای لوکال
for app in frappe erpnext hrms; do
  tgz="/opt/_rehydrate/${app}.tar.gz"
  [ -f "$tgz" ] || continue
  su - frappe -c "rm -rf ~/frappe-bench/apps/${app}; mkdir -p ~/frappe-bench/apps/${app}"
  tar -xzf "$tgz" -C /home/frappe/frappe-bench/apps/
  chown -R frappe:frappe /home/frappe/frappe-bench/apps/${app}
  # نصب editable از سورس محلی با wheelhouse ریپو
  su - frappe -c "source ~/frappe-bench/env/bin/activate && pip install -e ~/frappe-bench/apps/${app} --no-index --find-links ${ROOT}/vendor/wheels"
done

# سایت و نصب اپ‌ها
su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} version >/dev/null 2>&1 || bench new-site ${DOMAIN} --admin-password '${ADMIN_PW}' --mariadb-root-password '${DB_ROOT_PW}' --no-mariadb-socket"
su - frappe -c "cd ~/frappe-bench; bench use ${DOMAIN}; bench set-config -g default_site ${DOMAIN}; bench --site ${DOMAIN} set-config host_name https://${DOMAIN}"
su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} list-apps | grep -qi erpnext || bench --site ${DOMAIN} install-app erpnext"
if [ "${INSTALL_HRMS:-0}" = "1" ] && [ -d /home/frappe/frappe-bench/apps/hrms ]; then
  su - frappe -c "cd ~/frappe-bench; bench --site ${DOMAIN} list-apps | grep -qi hrms || bench --site ${DOMAIN} install-app hrms"
fi

# تزریق Assets بیلد‌شده (بدون نیاز به yarn/node)
if [ -f /opt/_rehydrate/sites_assets.tar.gz ]; then
  tar -xzf /opt/_rehydrate/sites_assets.tar.gz -C /home/frappe/frappe-bench/sites/
  chown -R frappe:frappe /home/frappe/frappe-bench/sites/assets
fi

# Supervisor + Nginx
ln -sf /home/frappe/frappe-bench/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf || true
supervisorctl reread || true && supervisorctl update || true

# Nginx از قالب ریپو (اگر موجود بود) یا bench
TPL="${ROOT}/assets/nginx/frappe-bench.conf.tpl"
if [ -f "$TPL" ]; then
  env DOMAIN="${DOMAIN}" envsubst '${DOMAIN}' < "$TPL" > "/etc/nginx/conf.d/frappe-bench.conf"
else
  su - frappe -c "cd ~/frappe-bench; yes | bench setup nginx"
fi
nginx -t && systemctl reload nginx

# SSL (اگر می‌خواهی تماماً از ریپو باشد، snakeoil بماند؛ در غیر اینصورت certbot)
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  true
else
  apt install -y ssl-cert
  sed -i "s|ssl_certificate .*|ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;|g" /etc/nginx/conf.d/frappe-bench.conf || true
  sed -i "s|ssl_certificate_key .*|ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;|g" /etc/nginx/conf.d/frappe-bench.conf || true
  nginx -t && systemctl reload nginx
fi

# Finalize
su - frappe -c "cd ~/frappe-bench; bench build --force || true; bench restart; bench --site ${DOMAIN} enable-scheduler || true"
echo "[✓] Offline rehydrate done for ${DOMAIN}"
