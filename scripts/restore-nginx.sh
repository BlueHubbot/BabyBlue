#!/bin/bash
set -e
BASE="/tmp/BabyBlue"
NGDIR="$BASE/artifacts/nginx"
LAST=$(ls -1 "$NGDIR" | sort | tail -n1)
if [ -z "$LAST" ]; then
  echo "no nginx snapshot found"
  exit 1
fi
tar -xzf "$NGDIR/$LAST" -C /
nginx -t && systemctl reload nginx
echo "[OK] nginx restored from $LAST"
