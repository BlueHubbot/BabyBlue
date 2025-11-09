#!/bin/bash
set -e
apt-get update -y
apt-get upgrade -y
apt-get install -y \
  sudo git curl ca-certificates \
  build-essential gcc g++ make \
  python3 python3-venv python3-pip python3-dev \
  libffi-dev libssl-dev zlib1g-dev \
  libjpeg-dev libxml2-dev libxslt1-dev \
  libcurl4-openssl-dev liblcms2-dev \
  libsasl2-dev libldap2-dev \
  mariadb-server mariadb-client \
  redis-server \
  nginx \
  supervisor

if ! id -u frappe >/dev/null 2>&1; then
  adduser --disabled-password --gecos "" frappe
fi

mkdir -p /home/frappe
chown -R frappe:frappe /home/frappe

if [ ! -f /etc/sudoers.d/90-frappe ]; then
  echo 'frappe ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/90-frappe
  chmod 440 /etc/sudoers.d/90-frappe
fi

systemctl enable --now supervisor || true

echo 'vm.overcommit_memory=1' > /etc/sysctl.d/99-redis.conf
sysctl --system >/dev/null 2>&1 || true

echo "[OK] prerequisites installed."
