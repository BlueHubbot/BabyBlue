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

# این اسکریپت روی سرور مقصد اجرا می‌شود

sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  SITE_ENV="'"$SITE"'"
  DB_NAME_ENV="'"$DB_NAME"'"
  DB_PASS_ENV="'"$DB_PASS"'"
  DB_ROOT_USER_ENV="'"$DB_ROOT_USER"'"
  DB_ROOT_PASS_ENV="'"$DB_ROOT_PASS"'"
  ADMIN_PASS_ENV="'"$ADMIN_PASS"'"
  ENC_KEY_ENV="'"$ENCRYPTION_KEY"'"
  REPO_DIR_ENV="'"$REPO_DIR"'"

  cd "$BENCH_HOME_ENV"

  # ساخت سایت خالی اگر وجود ندارد
  if [ ! -d "sites/$SITE_ENV" ]; then
    bench new-site "$SITE_ENV" \
      --db-name "$DB_NAME_ENV" --db-password "$DB_PASS_ENV" \
      --mariadb-root-username "$DB_ROOT_USER_ENV" --mariadb-root-password "$DB_ROOT_PASS_ENV" \
      --admin-password "$ADMIN_PASS_ENV" --no-mariadb-socket
  fi

  # اعمال encryption_key در site_config
  python3 - "$BENCH_HOME_ENV" "$SITE_ENV" "$ENC_KEY_ENV" <<PY
import json, sys, os
bench, site, enc = sys.argv[1], sys.argv[2], sys.argv[3]
path = os.path.join(bench, "sites", site, "site_config.json")
with open(path) as f:
    data = json.load(f)
data["encryption_key"] = enc
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY

  # ریستور DB اسنپ‌شات
  DB_DUMP = os.path.join(REPO_DIR_ENV, "artifacts", "data", "site-database.sql.gz")
PY
'
# اصلاح بخش بالا: پایتون تمام شد، ادامه در bash root برای restore واقعی:

sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  SITE_ENV="'"$SITE"'"
  DB_ROOT_USER_ENV="'"$DB_ROOT_USER"'"
  DB_ROOT_PASS_ENV="'"$DB_ROOT_PASS"'"
  ADMIN_PASS_ENV="'"$ADMIN_PASS"'"
  REPO_DIR_ENV="'"$REPO_DIR"'"

  cd "$BENCH_HOME_ENV"

  DB_DUMP="$REPO_DIR_ENV/artifacts/data/site-database.sql.gz"
  if [ -f "$DB_DUMP" ]; then
    bench --site "$SITE_ENV" restore "$DB_DUMP" \
      --db-root-username "$DB_ROOT_USER_ENV" --db-root-password "$DB_ROOT_PASS_ENV" \
      --force --admin-password "$ADMIN_PASS_ENV"
  fi

  # ریستور فایل‌ها (public/private)
  PUB_TAR="$REPO_DIR_ENV/artifacts/data/site-public-files.tar"
  PRIV_TAR="$REPO_DIR_ENV/artifacts/data/site-private-files.tar"

  if [ -f "$PUB_TAR" ]; then
    tar xf "$PUB_TAR" -C "$BENCH_HOME_ENV/sites"
  fi
  if [ -f "$PRIV_TAR" ]; then
    tar xf "$PRIV_TAR" -C "$BENCH_HOME_ENV/sites"
  fi

  bench --site "$SITE_ENV" migrate
  bench build
  bench clear-cache
  bench clear-website-cache
'
