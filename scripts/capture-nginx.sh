#!/bin/bash
set -e
BASE="/tmp/BabyBlue"
mkdir -p "$BASE/artifacts/nginx"
TS=$(date +%Y%m%d-%H%M)
tar -czf "$BASE/artifacts/nginx/nginx-$TS.tar.gz" /etc/nginx
echo "[OK] saved /etc/nginx to artifacts/nginx/nginx-$TS.tar.gz"
