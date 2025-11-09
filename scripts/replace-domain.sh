#!/bin/bash
set -e
OLD="$1"
NEW="$2"
if [ -z "$OLD" ] || [ -z "$NEW" ]; then
  echo "usage: $0 old.domain new.domain"
  exit 1
fi

# nginx
for f in /etc/nginx/sites-available/* /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*; do
  [ -f "$f" ] || continue
  sed -i "s/$OLD/$NEW/g" "$f"
done

# frappe sites
if [ -d /home/frappe/frappe-bench/sites ]; then
  sed -i "s/$OLD/$NEW/g" /home/frappe/frappe-bench/sites/currentsite.txt 2>/dev/null || true
  for s in /home/frappe/frappe-bench/sites/*/site_config.json; do
    [ -f "$s" ] || continue
    sed -i "s/$OLD/$NEW/g" "$s"
  done
fi

nginx -t && systemctl reload nginx
echo "[OK] replaced $OLD -> $NEW"
