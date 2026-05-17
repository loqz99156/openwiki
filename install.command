#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
bash install.sh

printf '\nDone. Open my-wiki/ in Obsidian, then run /init from the Claude Code plugin.\n'
printf 'Press Enter to close this window...'
read -r _
