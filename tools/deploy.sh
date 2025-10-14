#!/usr/bin/env bash
set -Eeuo pipefail
ORG="BlueHubbot"; REPO="BabyBlue"; BRANCH="release"
[ $# -ge 4 ] || { echo "Usage: $0 --main-domain MAIN --docs-domain DOCS"; exit 2; }
mkdir -p /srv/babyblue
curl -fsSL "https://github.com/$ORG/$REPO/archive/refs/heads/$BRANCH.tar.gz" \
 | tar -xz -C /srv/babyblue --strip-components=1
exec /srv/babyblue/tools/restore.sh "$@"
