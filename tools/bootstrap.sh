#!/usr/bin/env bash
set -Eeuo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade
apt-get -y install \
  ca-certificates curl xz-utils gnupg lsb-release \
  build-essential gcc g++ make git \
  python3 python3-venv python3-pip python3-dev python3-setuptools \
  libffi-dev libssl-dev libjpeg-dev libxml2-dev libxslt1-dev \
  libcurl4-openssl-dev liblcms2-dev libsasl2-dev libldap2-dev zlib1g-dev \
  libmariadb-dev libmariadb-dev-compat \
  mariadb-server mariadb-client \
  redis-server nginx supervisor \
  certbot python3-certbot-nginx

# Node 18 + yarn
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get -y install nodejs
fi
if ! command -v yarn >/dev/null 2>&1; then
  npm install -g yarn
fi

# تنظیمات لازم سیستم
sysctl -w vm.overcommit_memory=1
grep -q '^vm.overcommit_memory' /etc/sysctl.conf || echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
redis-cli -p 11000 CONFIG SET stop-writes-on-bgsave-error no >/dev/null 2>&1 || true
redis-cli -p 13000 CONFIG SET stop-writes-on-bgsave-error no >/dev/null 2>&1 || true

systemctl enable --now mariadb redis-server nginx supervisor
echo "[bootstrap] done."
