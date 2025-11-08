#!/bin/bash
set -e

apt update
apt -y upgrade
apt -y install build-essential gcc g++ make \
  python3 python3-venv python3-pip python3-dev \
  libmariadb-dev libmariadb-dev-compat \
  libffi-dev libssl-dev libjpeg-dev libxml2-dev libxslt1-dev \
  libcurl4-openssl-dev liblcms2-dev libsasl2-dev libldap2-dev zlib1g-dev \
  mariadb-server mariadb-client redis-server nginx supervisor \
  git certbot python3-certbot-nginx

# NodeJS 18 + yarn
curl -sL https://deb.nodesource.com/setup_18.x | bash -
apt -y install nodejs
npm install -g yarn
