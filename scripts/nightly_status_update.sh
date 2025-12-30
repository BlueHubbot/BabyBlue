#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

TZNAME="${TZNAME:-Europe/Paris}"
TODAY="$(TZ="$TZNAME" date +%F)"

# schema tag discovery:
# prefer tag (git describe) so schema_version == tag; fallback to VERSION
SCHEMA_TAG="${1:-}"
if [ -z "$SCHEMA_TAG" ]; then
  SCHEMA_TAG="$(git describe --tags --abbrev=0 2>/dev/null || true)"
  if [ -z "$SCHEMA_TAG" ]; then
    if [ -f "artifacts/apps/blue_hesab/VERSION" ]; then
      SCHEMA_TAG="$(tr -d ' \t\r\n' < artifacts/apps/blue_hesab/VERSION)"
    elif [ -f "apps/blue_hesab/VERSION" ]; then
      SCHEMA_TAG="$(tr -d ' \t\r\n' < apps/blue_hesab/VERSION)"
    fi
  fi
fi
[ -z "$SCHEMA_TAG" ] && SCHEMA_TAG="UNKNOWN"

SHORT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
GEN_BUILD="${SCHEMA_TAG}@${SHORT_SHA}"

mkdir -p status/daily

# 1) daily file: create if missing (never overwrite)
DAILY="status/daily/${TODAY}.md"
if [ ! -f "$DAILY" ]; then
  tmp="$(mktemp)"
  cat >"$tmp" <<EOT
# Daily Delta — ${TODAY}

## Done today

## Progress

## Blocked

## CHANGELOG
### Unreleased
- (fill)

### ${TODAY}
- (fill)

## Next session (Tomorrow)
1)
2)
3)
EOT
  mv "$tmp" "$DAILY"
fi

# 2) index: ensure exists + add today's entry once
INDEX="status/index.md"
if [ ! -f "$INDEX" ]; then
  tmp="$(mktemp)"
  cat >"$tmp" <<'EOT'
# Status — Daily Index

- **Master Roadmap / Spec:** `../README.md`
- **Current Status:** `../STATUS.md`

## Daily Logs
EOT
  mv "$tmp" "$INDEX"
fi

ENTRY="- ${TODAY} → \`daily/${TODAY}.md\`"
if ! grep -Fqx -- "$ENTRY" "$INDEX"; then
  tmp="$(mktemp)"
  awk -v entry="$ENTRY" '
    BEGIN{done=0}
    {print}
    $0=="## Daily Logs" && done==0 { print entry; done=1 }
  ' "$INDEX" >"$tmp"
  mv "$tmp" "$INDEX"
fi

# 3) STATUS.md: update only 4 lines (no overwrite of the rest)
STATUS="STATUS.md"
if [ ! -f "$STATUS" ]; then
  tmp="$(mktemp)"
  cat >"$tmp" <<EOT
# BlueHesab — STATUS (nightly/baba)

> **Master Roadmap / Spec:** \`README.md\`
> **Daily Logs:** \`status/daily/\`
> **Legal Board:** \`roadmaps/LEGAL_STATUS_BOARD.md\`
> **Releases (immutable per tag):** \`releases/\`

## Current Baseline
- Date (local): **${TODAY}**
- Repo: \`BlueHubbot/BabyBlue\`
- Branch: \`nightly/baba\`
- Current schema_version (tag): **${SCHEMA_TAG}**
- generator_build: **${GEN_BUILD}**

## Today (Latest Daily Delta)
- 📌 **Today log:** \`status/daily/${TODAY}.md\`
EOT
  mv "$tmp" "$STATUS"
else
  sed -i -E 's#^- Date \(local\): \*\*.*\*\*#- Date (local): **'"$TODAY"'**#m' "$STATUS" || true
  sed -i -E 's#^- Current schema_version \(tag\): \*\*.*\*\*#- Current schema_version (tag): **'"$SCHEMA_TAG"'**#m' "$STATUS" || true
  sed -i -E 's#^- generator_build: \*\*.*\*\*#- generator_build: **'"$GEN_BUILD"'**#m' "$STATUS" || true
  sed -i -E 's#^- 📌 \*\*Today log:\*\* `status/daily/.*`#- 📌 **Today log:** `status/daily/'"$TODAY"'.md`#m' "$STATUS" || true
fi

echo "OK: STATUS updated (tag=${SCHEMA_TAG}, build=${GEN_BUILD}, daily=${DAILY})"
