#!/usr/bin/env bash
set -euo pipefail
OUT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/vendor"
mkdir -p "$OUT"
# کل bench (بدون لاگ‌ها و پرایوت‌ها)
tar --exclude='frappe-bench/logs' --exclude='frappe-bench/sites/*/private/*' -czf "$OUT/bench_tree.tar.gz" -C /home/frappe frappe-bench
split -b 95M -d "$OUT/bench_tree.tar.gz" "$OUT/bench_tree.tar.gz.part-"; rm -f "$OUT/bench_tree.tar.gz"
# venv بنچ (pipx) برای اجرای bench بدون اینترنت
tar -czf "$OUT/bench_venv.tar.gz" -C /home/frappe/.local/pipx/venvs frappe-bench
split -b 95M -d "$OUT/bench_venv.tar.gz" "$OUT/bench_venv.tar.gz.part-"; rm -f "$OUT/bench_venv.tar.gz"
