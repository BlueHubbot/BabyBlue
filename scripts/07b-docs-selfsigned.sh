#!/usr/bin/env bash
set -euo pipefail

cd /tmp/BabyBlue

if [ -f .env ]; then
  set -o allexport
  . .env
  set +o allexport
fi

: "${DOCS_SITE:?DOCS_SITE not set in .env}"

CERT_DIR="/etc/letsencrypt/live/${DOCS_SITE}"

echo ">>> 07b-docs-selfsigned: creating 1-day self-signed cert for ${DOCS_SITE}"

mkdir -p "${CERT_DIR}"

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "${CERT_DIR}/privkey.pem" \
  -out "${CERT_DIR}/fullchain.pem" \
  -subj "/CN=${DOCS_SITE}" \
  -days 1

echo ">>> nginx -t"
nginx -t

echo ">>> systemctl reload nginx"
systemctl reload nginx

echo ">>> 07b-docs-selfsigned: DONE"
