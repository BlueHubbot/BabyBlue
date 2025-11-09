#!/bin/bash
set -e
BASE="/tmp/BabyBlue"
SRC_BENCH="/home/frappe/frappe-bench"
SRC_DOCS="/srv/bluedoc"
DEST="$BASE/artifacts/data"
TS=$(date +%Y%m%d-%H%M)
OUTDIR="$DEST/$TS"
mkdir -p "$OUTDIR"

echo "[*] archiving $SRC_BENCH -> $OUTDIR ..."
tar -czf "$OUTDIR/frappe-bench.tar.gz" -C /home/frappe frappe-bench
cd "$OUTDIR"
split -b 50M frappe-bench.tar.gz frappe-bench.tar.gz.
rm -f frappe-bench.tar.gz

if [ -d "$SRC_DOCS" ]; then
  echo "[*] archiving $SRC_DOCS -> $OUTDIR ..."
  tar -czf "$OUTDIR/bluedoc.tar.gz" -C /srv bluedoc
fi

echo "[OK] data captured in $OUTDIR"
