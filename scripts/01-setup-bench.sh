#01-setup-bench.sh
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

# این اسکریپت باید روی سرور مقصد و به‌صورت روت اجرا شود.

########################################
# 1) نصب bench در venv اختصاصی یوزر frappe
########################################
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/.local/bin:$PATH"

  # ساخت venv اگر وجود ندارد
  if [[ ! -d "$HOME/bench-venv" ]]; then
    python3 -m venv "$HOME/bench-venv"
  fi

  "$HOME/bench-venv/bin/pip" install --upgrade pip

  if ! "$HOME/bench-venv/bin/bench" --help >/dev/null 2>&1; then
    "$HOME/bench-venv/bin/pip" install "frappe-bench==5.*"
  fi

  # هویت git برای commitهای داخلی apps
  if ! git config --global user.name >/dev/null 2>&1; then
    git config --global user.name "frappe"
  fi
  if ! git config --global user.email >/dev/null 2>&1; then
    git config --global user.email "frappe@example.com"
  fi
'

########################################
# 2) bench init اگر BENCH_HOME وجود ندارد
########################################
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  PARENT_DIR="$(dirname "$BENCH_HOME_ENV")"
  BENCH_NAME="$(basename "$BENCH_HOME_ENV")"

  mkdir -p "$PARENT_DIR"
  cd "$PARENT_DIR"

  if [[ ! -d "$BENCH_NAME" ]]; then
    bench init --python python3.11 --frappe-branch version-15 "$BENCH_NAME"
  fi
'

########################################
# 3) استخراج appها، git init، و setup requirements
########################################
sudo -u "$FRAPPE_USER" -H bash -lc '
  set -euo pipefail
  export PATH="$HOME/bench-venv/bin:$HOME/.local/bin:$PATH"

  BENCH_HOME_ENV="'"$BENCH_HOME"'"
  REPO_DIR_ENV="'"$REPO_DIR"'"

  cd "$BENCH_HOME_ENV"
  mkdir -p apps


  # --- configure git identity for frappe user (needed for git init + commit) ---
  sudo -u "$FRAPPE_USER" -H git config --global user.name "frappe"
  sudo -u "$FRAPPE_USER" -H git config --global user.email "frappe@localhost"
  # ------------------------------------------------------------------------------


  for app in frappe erpnext hrms cal_boot; do
    TAR="$REPO_DIR_ENV/artifacts/data/app-$app.tar.gz"
    if [[ -f "$TAR" ]]; then
      rm -rf "apps/$app"
      tar xzf "$TAR" -C apps

      if [[ -d "apps/$app" ]]; then
        echo "Initializing git repo for $app"
        cd "apps/$app"
        if [[ ! -d .git ]]; then
          git init
          git add .
          git commit -m "Snapshot import for $app" || true
        fi
        cd "$BENCH_HOME_ENV"
      fi
    fi
  done

  # apps.txt مطابق سرور مبدا
  cat > "sites/apps.txt" <<EOT
frappe
erpnext
hrms
cal_boot
blue_jdate
EOT

  bench setup requirements
'
