#!/usr/bin/env bash
set -Eeuo pipefail
BRANCH="${BRANCH:-clean}"
RAW="https://raw.githubusercontent.com/BlueHubbot/BabyBlue/${BRANCH}/install/full.sh"
if [[ -f "$(dirname "$0")/full.sh" ]]; then
  exec bash "$(dirname "$0")/full.sh" "$@"
else
  curl -fsSL "$RAW" | bash -s -- "$@"
fi
