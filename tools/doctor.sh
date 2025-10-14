#!/usr/bin/env bash
set -euo pipefail
echo "---- nginx -T ----"; nginx -T 2>&1 | sed -n '1,200p' || true
echo "---- logs (tail) ----"
tail -n 100 /home/frappe/frappe-bench/logs/*.log 2>/dev/null || true
