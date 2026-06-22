#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if bash install.sh; then
  printf '\nDone. Use openwiki-init, openwiki-add, openwiki-chat, or openwiki-category from Claude Code or Codex.\n'
else
  printf '\nOpenWiki installation failed. Fix the message above, then run install.command again.\n' >&2
fi

printf 'Press Enter to close this window...'
read -r _
