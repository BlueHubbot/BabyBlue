#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APT_DIR="$ROOT/artifacts/apt"
LIST=/etc/apt/sources.list.d/babyblue-offline.list
if [[ -f "$APT_DIR/Packages.gz" || -f "$APT_DIR/Packages" ]]; then
  echo "deb [trusted=yes] file:$APT_DIR ./" > "$LIST"
  apt-get -o Dir::Etc::sourcelist="$LIST" -o Dir::Etc::sourceparts='-' update
fi
if [[ -f "$ROOT/inventory/apt/installed.tsv" ]]; then
  awk '{print $1"="$2}' "$ROOT/inventory/apt/installed.tsv" \
  | xargs -r -n200 apt-get -o Dir::Etc::sourcelist="$LIST" -o Dir::Etc::sourceparts='-' \
      install -y --allow-downgrades --no-install-recommends
fi
