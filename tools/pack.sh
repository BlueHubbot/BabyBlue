#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "ERROR at line $LINENO"; exit 1' ERR

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS="$(date -u +%Y%m%d-%H%M)"
OUT="$ROOT/artifacts/data/$TS"
install -d "$OUT"

echo "==> SNAP: $OUT"

# 1) Bench (فقط دایرکتوری بنچ)
tar -C / -czf "$OUT/bench.tar.gz" home/frappe/frappe-bench
split --bytes=50M --numeric-suffixes=00 --suffix-length=2 --additional-suffix=.part \
  "$OUT/bench.tar.gz" "$OUT/bench.tar.gz." && rm -f "$OUT/bench.tar.gz"

# 2) DB dump (root via debian.cnf یا سوکت)
echo "[dump] DB..."
if mysql --defaults-extra-file=/etc/mysql/debian.cnf -e 'select 1' >/dev/null 2>&1; then
  mysqldump --defaults-extra-file=/etc/mysql/debian.cnf --single-transaction --routines --triggers --events --all-databases \
    | gzip -c > "$OUT/db-all.sql.gz"
else
  mysqldump -uroot --protocol=socket --single-transaction --routines --triggers --events --all-databases \
    | gzip -c > "$OUT/db-all.sql.gz"
fi

# 3) Docs (اختیاری)
[ -d /var/www/docs_en ] && tar -C / -czf "$OUT/docs_en.tar.gz"  var/www/docs_en || true
[ -d /srv/bluedoc ]     && tar -C / -czf "$OUT/docs_mirror.tar.gz" srv/bluedoc   || true

# 4) Checksums
( cd "$OUT" && sha256sum bench.tar.gz.*.part db-all.sql.gz docs_*.tar.gz 2>/dev/null > SHA256SUMS.txt )

# 5) Git add/commit/push (اختیاری؛ اگر رپو حاضر بود)
cd "$ROOT"
[ -d .git ] || git init
git branch -M release 2>/dev/null || true
[ -f .gitignore ] || cat > .gitignore <<'GIT'
*.tar.gz
!artifacts/data/*/*.tar.gz.*.part
.DS_Store
GIT
git add ".gitignore" "artifacts/data/$TS" || true
git -c user.name="Blue Deploy Bot" -c user.email="deploy@example.com" \
  commit -m "release($TS): bench parts + db + docs (+checksums)" || true

# اگر ریموت ست نیست، ست کن (HTTP)
git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/BlueHubbot/BabyBlue.git"

# اگر GITHUB_USER/GHTOKEN ست باشند → پوش
if [[ -n "${GITHUB_USER:-}" && -n "${GHTOKEN:-}" ]]; then
  git push -f "https://${GITHUB_USER}:${GHTOKEN}@github.com/BlueHubbot/BabyBlue.git" release
fi

echo "==> DONE: $OUT"
