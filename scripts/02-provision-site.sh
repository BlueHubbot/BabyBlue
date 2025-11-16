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

########################################
# 1) common_site_config.json (db_host + redis روی 6379)
########################################
echo ">>> creating / updating common_site_config.json (db_host + redis)..."
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  cd "$BENCH_HOME_ENV"

  python3 - <<PY
import json, os
bench = os.getcwd()
path = os.path.join(bench, "sites", "common_site_config.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
data = {}
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)
data.setdefault("db_host", "127.0.0.1")
data["redis_cache"]    = "redis://127.0.0.1:6379"
data["redis_queue"]    = "redis://127.0.0.1:6379"
data["redis_socketio"] = "redis://127.0.0.1:6379"
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY
'

########################################
# 2) ساخت سایت (اگر وجود ندارد) + encryption_key
########################################
echo ">>> creating site (if missing)..."
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  SITE_ENV="'"$SITE"'"
  DB_NAME_ENV="'"$DB_NAME"'"
  DB_PASS_ENV="'"$DB_PASS"'"
  DB_ROOT_USER_ENV="'"$DB_ROOT_USER"'"
  DB_ROOT_PASS_ENV="'"$DB_ROOT_PASS"'"
  ADMIN_PASS_ENV="'"$ADMIN_PASS"'"
  ENC_KEY_ENV="'"$ENCRYPTION_KEY"'"  # فقط برای وضوح

  cd "$BENCH_HOME_ENV"

  if [[ ! -d "sites/$SITE_ENV" ]]; then
    bench new-site "$SITE_ENV" \
      --db-name "$DB_NAME_ENV" --db-password "$DB_PASS_ENV" \
      --mariadb-root-username "$DB_ROOT_USER_ENV" --mariadb-root-password "$DB_ROOT_PASS_ENV" \
      --admin-password "$ADMIN_PASS_ENV" --no-mariadb-socket
  fi

  # اعمال encryption_key
  python3 - <<PY
import json, os
bench = r"'"$BENCH_HOME"'"
site  = r"'"$SITE"'"
enc   = r"'"$ENCRYPTION_KEY"'"
path = os.path.join(bench, "sites", site, "site_config.json")
with open(path) as f:
    data = json.load(f)
data["encryption_key"] = enc
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY
'

########################################
# 3) ریستور DB + فایل‌ها + اطمینان از وجود اپ‌ها + migrate/build/cache
########################################
echo ">>> restoring DB + files (if artifacts present) ..."
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  SITE_ENV="'"$SITE"'"
  DB_ROOT_USER_ENV="'"$DB_ROOT_USER"'"
  DB_ROOT_PASS_ENV="'"$DB_ROOT_PASS"'"
  ADMIN_PASS_ENV="'"$ADMIN_PASS"'"
  REPO_DIR_ENV="'"$REPO_DIR"'"

  cd "$BENCH_HOME_ENV"

  DB_DUMP="$REPO_DIR_ENV/artifacts/data/site-database.sql.gz"
  if [[ -f "$DB_DUMP" ]]; then
    echo ">>> restoring database from $DB_DUMP ..."
    bench --site "$SITE_ENV" restore "$DB_DUMP" \
      --db-root-username "$DB_ROOT_USER_ENV" --db-root-password "$DB_ROOT_PASS_ENV" \
      --force --admin-password "$ADMIN_PASS_ENV"
  fi

  PUB_TAR="$REPO_DIR_ENV/artifacts/data/site-public-files.tar"
  PRIV_TAR="$REPO_DIR_ENV/artifacts/data/site-private-files.tar"

  if [[ -f "$PUB_TAR" ]]; then
    echo ">>> restoring public files ..."
    tar xf "$PUB_TAR" -C "$BENCH_HOME_ENV/sites"
  fi
  if [[ -f "$PRIV_TAR" ]]; then
    echo ">>> restoring private files ..."
    tar xf "$PRIV_TAR" -C "$BENCH_HOME_ENV/sites"
  fi

  # اطمینان از وجود اپ‌های لوکال (erpnext, hrms, cal_boot) بدون bench get-app
  APPS_ARTIFACTS_ENV="$REPO_DIR_ENV/artifacts/apps"

  ensure_local_app() {
    local app="$1"
    local src="$APPS_ARTIFACTS_ENV/$app"

    if [[ ! -d "$src" ]]; then
      echo ">>> WARN: local app source not found: $src (skipping $app)" >&2
      return
    fi

    if [[ ! -d "$BENCH_HOME_ENV/apps/$app" ]]; then
      echo ">>> copying app '$app' into bench/apps ..."
      mkdir -p "$BENCH_HOME_ENV/apps/$app"
      cp -a "$src/." "$BENCH_HOME_ENV/apps/$app/"
    else
      echo ">>> app '$app' already present in bench/apps"
    fi

    # مطمئن شو پکیج پایتون اپ در env نصب/در دسترس است
    "$BENCH_HOME_ENV/env/bin/python" -m pip install --quiet -e "$BENCH_HOME_ENV/apps/$app" || true
  }

  echo ">>> ensuring local apps (erpnext, hrms, cal_boot) are present in bench ..."
  ensure_local_app erpnext
  ensure_local_app hrms
  ensure_local_app cal_boot

  echo ">>> migrate + build + clear cache ..."
  bench --site "$SITE_ENV" migrate
  bench build
  bench clear-cache
  bench clear-website-cache

  echo ">>> enable scheduler ..."
  bench --site "$SITE_ENV" set-config enable_scheduler 1
  bench --site "$SITE_ENV" enable-scheduler
'

########################################
# 4) supervisor برای bench
########################################
echo ">>> setting up supervisor for bench ..."
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"
  cd "'"$BENCH_HOME"'"
  bench setup supervisor --yes
'

ln -sfn "$BENCH_HOME/config/supervisor.conf" /etc/supervisor/conf.d/frappe-bench.conf
supervisorctl reread
supervisorctl update

########################################
# 5) دسترسی nginx به assets
########################################
chmod 755 "/home/$FRAPPE_USER"
chmod -R o+rX "$BENCH_HOME/sites/assets"
