#02-provision-site.sh
#!/usr/bin/env bash
set -euo pipefail

# همیشه از روت ریپو اجرا شو
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# .env حتما باید وجود داشته باشد
if [[ ! -f .env ]]; then
  echo ".env not found; copy .env.example and edit first" >&2
  exit 1
fi

set -o allexport
# shellcheck disable=SC1091
source .env
set +o allexport

# متغیرهای پایه (با پیش‌فرض برای FRAPPE_USER/BENCH_HOME)
: "${FRAPPE_USER:=frappe}"
: "${BENCH_HOME:=/home/${FRAPPE_USER}/frappe-bench}"
: "${SITE:?SITE not set in .env}"
: "${DB_NAME:?DB_NAME not set in .env}"
: "${DB_PASS:?DB_PASS not set in .env}"
: "${DB_ROOT_USER:?DB_ROOT_USER not set in .env}"
: "${DB_ROOT_PASS:?DB_ROOT_PASS not set in .env}"
: "${ADMIN_PASS:?ADMIN_PASS not set in .env}"
: "${ENCRYPTION_KEY:?ENCRYPTION_KEY not set in .env}"

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
  ENC_KEY_ENV="'"$ENCRYPTION_KEY"'"

  cd "$BENCH_HOME_ENV"

  if [[ ! -d "sites/$SITE_ENV" ]]; then
    bench new-site "$SITE_ENV" \
      --db-name "$DB_NAME_ENV" --db-password "$DB_PASS_ENV" \
      --mariadb-root-username "$DB_ROOT_USER_ENV" --mariadb-root-password "$DB_ROOT_PASS_ENV" \
      --admin-password "$ADMIN_PASS_ENV" --no-mariadb-socket
  fi

  # اعمال encryption_key روی site_config.json
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
# 3) ریستور DB + فایل‌ها + نصب اپ‌ها + migrate/build/cache
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

  # اولویت با offline/db/initial.sql.gz، بعد artifacts/data/site-database.sql.gz
  DB_DUMP_1="$REPO_DIR_ENV/offline/db/initial.sql.gz"
  DB_DUMP_2="$REPO_DIR_ENV/artifacts/data/site-database.sql.gz"
  DB_DUMP=""

  if [[ -f "$DB_DUMP_1" ]]; then
    DB_DUMP="$DB_DUMP_1"
  elif [[ -f "$DB_DUMP_2" ]]; then
    DB_DUMP="$DB_DUMP_2"
  fi

  if [[ -n "$DB_DUMP" ]]; then
    echo ">>> restoring database from $DB_DUMP ..."
    bench --site "$SITE_ENV" restore "$DB_DUMP" \
      --db-root-username "$DB_ROOT_USER_ENV" --db-root-password "$DB_ROOT_PASS_ENV" \
      --force --admin-password "$ADMIN_PASS_ENV"
  else
    echo ">>> WARNING: no DB dump found (offline/db/initial.sql.gz یا artifacts/data/site-database.sql.gz). Skipping restore." >&2
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

  echo ">>> ensuring local apps (erpnext, hrms, cal_boot, blue_jdate) are present in bench ..."

  # کمک‌تابع: پیدا کردن ریشهٔ واقعی پکیج (جایی که pyproject.toml یا setup.py هست)
  find_project_root() {
    local base="$1"
    if [[ -f "$base/pyproject.toml" || -f "$base/setup.py" ]]; then
      echo "$base"
      return 0
    fi
    local d
    for d in "$base"/*; do
      if [[ -d "$d" && ( -f "$d/pyproject.toml" || -f "$d/setup.py" ) ]]; then
        echo "$d"
        return 0
      fi
    done
    return 1
  }

  ensure_local_app() {
    local app_name="$1"
    local src_dir="$REPO_DIR_ENV/artifacts/apps/$app_name"
    local dst_dir="$BENCH_HOME_ENV/apps/$app_name"
    local project_root=""

    # 1) اگر از قبل در apps/ هست، استفاده‌اش کن
    if [[ -d "$dst_dir" ]]; then
      echo "  - app '\''$app_name'\'' already exists in apps/, trying to use it"
      if project_root="$(find_project_root "$dst_dir")"; then
        echo "  - pip install -e $project_root"
        "$BENCH_HOME_ENV/env/bin/pip" install --quiet --upgrade -e "$project_root"
        return 0
      fi
      echo "  - WARNING: no setup.py/pyproject.toml found for $app_name under $dst_dir"
    fi

    # 2) تلاش برای کپی از artifacts اگر ساختار درست باشد
    if [[ -d "$src_dir" ]]; then
      echo "  - copying $src_dir -> $dst_dir"
      rm -rf "$dst_dir"
      cp -a "$src_dir" "$dst_dir"

      if project_root="$(find_project_root "$dst_dir")"; then
        echo "  - pip install -e $project_root"
        "$BENCH_HOME_ENV/env/bin/pip" install --quiet --upgrade -e "$project_root"
        return 0
      fi

      echo "  - WARNING: artifacts for $app_name do not contain setup.py/pyproject.toml"
    else
      echo "  - WARNING: artifacts/apps/$app_name not found"
    fi

    # 3) فallback آنلاین برای erpnext و hrms
    if [[ "$app_name" == "erpnext" ]]; then
      echo "  - falling back to bench get-app erpnext from GitHub (online)..."
      rm -rf "$dst_dir"
      bench get-app --branch version-15 https://github.com/frappe/erpnext
      return 0
    elif [[ "$app_name" == "hrms" ]]; then
      echo "  - falling back to bench get-app hrms from GitHub (online)..."
      rm -rf "$dst_dir"
      bench get-app --branch version-15 https://github.com/frappe/hrms
      return 0
    else
      echo "  - ERROR: cannot install local app '\''$app_name'\''; no valid local project and no online fallback." >&2
      return 1
    fi
  }

  apps=(erpnext hrms cal_boot blue_jdate)
  for app_name in "${apps[@]}"; do
    ensure_local_app "$app_name"
  done


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
supervisorctl reread || true
supervisorctl update || true

########################################
# 5) دسترسی nginx به assets
########################################
chmod 755 "/home/$FRAPPE_USER"
chmod -R o+rX "$BENCH_HOME/sites/assets"

echo ">>> 02-provision-site: DONE"
