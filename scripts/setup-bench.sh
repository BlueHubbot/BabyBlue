#!/bin/bash
set -e
. ./config/env.sh

# اگر کاربر frappe نیستیم، خارج شو
if [ "$(id -un)" != "$FRAPPE_USER" ]; then
  echo "run as $FRAPPE_USER"
  exit 1
fi

cd /home/$FRAPPE_USER
[ -d "$BENCH_PATH" ] || bench init "$(basename $BENCH_PATH)" --frappe-branch version-14
cd "$BENCH_PATH"

bench new-site "$SITE_DOMAIN" --mariadb-root-username dbadmin --mariadb-root-password "$DB_ROOT_PW" --admin-password "$ADMIN_PW"
bench --site "$SITE_DOMAIN" install-app erpnext
