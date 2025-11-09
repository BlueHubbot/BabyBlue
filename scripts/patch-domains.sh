#!/bin/bash
set -e

if [ $# -lt 2 ]; then
  echo "Usage: $0 OLD_DOMAIN NEW_DOMAIN"
  exit 1
fi

OLD="$1"
NEW="$2"

# جاهایی که معمولا دامین توشونه
TARGETS="
/etc/nginx
/home/frappe/frappe-bench/sites
/etc/letsencrypt/renewal
"

for path in $TARGETS; do
  if [ -d "$path" ]; then
    echo "[*] patching in $path ..."
    # از sed با in-place بکاپ کوچیک استفاده کن
    grep -R -l "$OLD" "$path" 2>/dev/null | while read f; do
      sed -i.bak "s/$OLD/$NEW/g" "$f"
    done
  fi
done

echo "[OK] domain replaced: $OLD -> $NEW"
echo "now run: nginx -t && systemctl reload nginx"
