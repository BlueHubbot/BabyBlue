#07-nginx-overlay.sh
#!/usr/bin/env bash
set -euo pipefail

cd /tmp/BabyBlue

# .env باید شامل SITE و DOCS_SITE باشد
if [ -f .env ]; then
  set -o allexport
  . .env
  set +o allexport
fi

: "${SITE:?SITE not set in .env}"
: "${DOCS_SITE:?DOCS_SITE not set in .env}"

NGINX_ROOT="/etc/nginx"
ART_ROOT="${PWD}/artifacts/nginx"

# دامین‌های قدیمی روی سرور سورس
OLD_SITE_HOST="baba.bluehesab.ir"
OLD_DOCS_SITE_HOST="docs.bluehesab.ir"

echo ">>> 07-nginx-overlay: SITE=${SITE}  DOCS_SITE=${DOCS_SITE}"

# --- 1) کپی همه include ها، snippets و conf.d از ریپو ---

echo ">>> copying root includes -> ${NGINX_ROOT}"
cp -a "${ART_ROOT}/root/." "${NGINX_ROOT}/"

echo ">>> copying snippets -> ${NGINX_ROOT}/snippets"
mkdir -p "${NGINX_ROOT}/snippets"
cp -a "${ART_ROOT}/snippets/." "${NGINX_ROOT}/snippets/" 2>/dev/null || true

echo ">>> copying conf.d -> ${NGINX_ROOT}/conf.d"
mkdir -p "${NGINX_ROOT}/conf.d"
cp -a "${ART_ROOT}/conf.d/." "${NGINX_ROOT}/conf.d/" 2>/dev/null || true

# --- 2) فقط دو فایل دامنه‌محور: docs_langredir_server.inc و blueapi_inline.conf ---

for f in docs_langredir_server.inc blueapi_inline.conf; do
  target="${NGINX_ROOT}/${f}"
  if [ -f "${target}" ]; then
    echo ">>> patching domains in ${target}"
    sed -i \
      -e "s/${OLD_SITE_HOST}/${SITE}/g" \
      -e "s/${OLD_DOCS_SITE_HOST}/${DOCS_SITE}/g" \
      "${target}"
  else
    echo "WARN: ${target} not found, skipping"
  fi
done

# --- 3) رندر vhostهای ERP و Docs از تمپلیت‌های erp-baby.conf و bluedoc.conf ---

TPL_DIR="${ART_ROOT}/templates"
ERP_TPL="${TPL_DIR}/erp-baby.conf"
DOCS_TPL="${TPL_DIR}/bluedoc.conf"

ERP_OUT="${NGINX_ROOT}/sites-available/erp-${SITE}.conf"
DOCS_OUT="${NGINX_ROOT}/sites-available/docs-${DOCS_SITE}.conf"

mkdir -p "${NGINX_ROOT}/sites-available" "${NGINX_ROOT}/sites-enabled"

echo ">>> rendering ERP vhost -> ${ERP_OUT}"
sed \
  -e "s/${OLD_SITE_HOST}/${SITE}/g" \
  -e "s/${OLD_DOCS_SITE_HOST}/${DOCS_SITE}/g" \
  "${ERP_TPL}" > "${ERP_OUT}"

echo ">>> rendering DOCS vhost -> ${DOCS_OUT}"
sed \
  -e "s/${OLD_SITE_HOST}/${SITE}/g" \
  -e "s/${OLD_DOCS_SITE_HOST}/${DOCS_SITE}/g" \
  "${DOCS_TPL}" > "${DOCS_OUT}"

ln -sfn "${ERP_OUT}"  "${NGINX_ROOT}/sites-enabled/erp-${SITE}.conf"
ln -sfn "${DOCS_OUT}" "${NGINX_ROOT}/sites-enabled/docs-${DOCS_SITE}.conf"

# --- 4) تست و ری‌لود nginx ---

echo ">>> nginx -t"
nginx -t

echo ">>> systemctl reload nginx"
systemctl reload nginx

echo ">>> 07-nginx-overlay: DONE"
