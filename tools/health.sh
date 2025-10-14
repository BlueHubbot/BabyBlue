#!/usr/bin/env bash
set -euo pipefail
echo "== supervisor =="; supervisorctl status || true
echo "== ports =="; ss -ltnp | egrep ':80|:443|:8000|:9000' || true
echo "== nginx -t =="; nginx -t || true
