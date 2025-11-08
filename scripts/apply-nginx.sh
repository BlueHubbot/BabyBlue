#!/bin/bash
set -e
. ./config/env.sh
mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
envsubst '$SITE_DOMAIN $BENCH_PATH' < templates/nginx-erp.conf.tpl > /etc/nginx/sites-available/$SITE_DOMAIN.conf
envsubst '$DOCS_DOMAIN $SRV_DOCS'   < templates/nginx-docs.conf.tpl > /etc/nginx/sites-available/$DOCS_DOMAIN.conf
ln -sf /etc/nginx/sites-available/$SITE_DOMAIN.conf /etc/nginx/sites-enabled/$SITE_DOMAIN.conf
ln -sf /etc/nginx/sites-available/$DOCS_DOMAIN.conf /etc/nginx/sites-enabled/$DOCS_DOMAIN.conf
nginx -t && systemctl reload nginx
