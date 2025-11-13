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

# این اسکریپت باید روی سرور مقصد اجرا شود

# نصب bench برای کاربر frappe اگر وجود ندارد
if ! sudo -u "$FRAPPE_USER" -H bash -lc 'command -v bench >/dev/null 2>&1'; then
  sudo -u "$FRAPPE_USER" -H bash -lc '
    export PATH="$HOME/.local/bin:$PATH"
    pip3 install --user "frappe-bench==5.*"
  '
fi

# init bench اگر BENCH_HOME وجود ندارد
sudo -u "$FRAPPE_USER" -H bash -lc '
  export PATH="$HOME/.local/bin:$PATH"
  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  PARENT_DIR="$(dirname "$BENCH_HOME_ENV")"
  BENCH_NAME="$(basename "$BENCH_HOME_ENV")"

  mkdir -p "$PARENT_DIR"
  cd "$PARENT_DIR"

  if [ ! -d "$BENCH_NAME" ]; then
    bench init --python python3.11 --frappe-branch version-15 "$BENCH_NAME"
  fi

  cd "$BENCH_HOME_ENV"
  mkdir -p apps
'

# استخراج سورس اپ‌ها از artifacts/data روی سرور مقصد
sudo -u "$FRAPPE_USER" -H bash -lc '
  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  cd "$BENCH_HOME_ENV"
  mkdir -p apps

  REPO_DIR_ENV="'"$REPO_DIR"'"

  for app in frappe erpnext hrms cal_boot; do
    TAR="$REPO_DIR_ENV/artifacts/data/app-$app.tar.gz"
    if [ -f "$TAR" ]; then
      tar xzf "$TAR" -C apps
    fi
  done

  bench setup requirements
'
