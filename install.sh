#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m pip install -e .
mkdir -p my-wiki/.claude/commands
cp openwiki/command_templates/*.md my-wiki/.claude/commands/

printf 'OpenWiki installed. Obsidian vault ready: my-wiki/\n'
printf 'Open my-wiki/ in Obsidian, then run /init from the Claude Code plugin.\n'
