#!/bin/bash
set -e

# از همون جاهایی که قبلاً گفتیم
BENCH_SRC="/home/frappe/frappe-bench"
DOCS_SRC="/srv/bluedoc"
BASE="/tmp/BabyBlue"
OUT="$BASE/artifacts/data"

TS=$(date +%Y%m%d-%H%M)
DEST="$OUT/$TS"

mkdir -p "$DEST"

# 1) بنچ
if [ -d "$BENCH_SRC" ]; then
  echo "[*] packing $BENCH_SRC ..."
  tar -czf "$DEST/frappe-bench.tar.gz" -C /home/frappe frappe-bench
  # اگه خواستی تقسیمش کنی برای گیت:
  split -b 50M "$DEST/frappe-bench.tar.gz" "$DEST/frappe-bench.tar.gz."
  rm -f "$DEST/frappe-bench.tar.gz"
fi

# 2) داکس
if [ -d "$DOCS_SRC" ]; then
  echo "[*] packing $DOCS_SRC ..."
  tar -czf "$DEST/bluedoc.tar.gz" -C /srv bluedoc
fi

echo "[OK] data captured into $DEST"
echo "=> git add artifacts/data/$TS && git commit -m \"data $TS\" && git push"
