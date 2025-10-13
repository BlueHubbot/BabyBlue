#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APT_DIR="$ROOT/artifacts/apt"
POOL="$APT_DIR/pool"
mkdir -p "$POOL" "$ROOT/inventory/apt"
shopt -s nullglob
cp -n /var/cache/apt/archives/*.deb "$POOL"/ || true
( cd "$APT_DIR" && dpkg-scanpackages -m pool > Packages && gzip -f9 < Packages > Packages.gz )
chmod -R a+rX "$APT_DIR"
dpkg-query -W -f='${binary:Package}\t${Version}\n' | sort > "$ROOT/inventory/apt/installed.tsv"
echo "snapshot ready -> $APT_DIR and inventory/apt/installed.tsv"
