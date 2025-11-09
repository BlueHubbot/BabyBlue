#!/bin/bash
set -e
. ./config/env.sh

LATEST_DIR=$(ls -1d artifacts/data/* | sort | tail -1)

# برگردوندن بنچ
cat $LATEST_DIR/frappe-bench.tar.gz.* > /tmp/frappe-bench.tar.gz
mkdir -p /home/$FRAPPE_USER
tar -xzf /tmp/frappe-bench.tar.gz -C /
chown -R $FRAPPE_USER:$FRAPPE_USER /home/$FRAPPE_USER/frappe-bench

# برگردوندن داکس
mkdir -p /srv
tar -xzf $LATEST_DIR/bluedoc.tar.gz -C /
