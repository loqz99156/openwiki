#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

printf 'OpenWiki one-click installer\n'
printf 'Checking Python environment...\n'

if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3 was not found. Install Python 3.10+ first, then run this installer again.\n' >&2
  exit 1
fi

if ! python3 - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
then
  printf 'OpenWiki requires Python 3.10 or newer.\n' >&2
  python3 --version >&2 || true
  exit 1
fi

if ! python3 -m pip --version >/dev/null 2>&1; then
  printf 'pip was not found for python3. Install/enable pip, then run this installer again.\n' >&2
  exit 1
fi

printf 'Installing OpenWiki Python package and dependencies...\n'
python3 -m pip install -e .

printf 'Verifying Python dependencies...\n'
python3 - <<'PY'
import importlib.util
import sys

required = {
    "pageindex": "pageindex",
    "markitdown": "markitdown",
    "pymupdf": "pymupdf",
    "click": "click",
    "watchdog": "watchdog",
    "litellm": "litellm",
    "pyyaml": "yaml",
    "python-dotenv": "dotenv",
    "json-repair": "json_repair",
}

missing = [name for name, module in required.items() if importlib.util.find_spec(module) is None]
if missing:
    print("Missing Python dependencies: " + ", ".join(missing), file=sys.stderr)
    raise SystemExit(1)
PY

if command -v qmd >/dev/null 2>&1; then
  printf 'qmd already installed.\n'
elif command -v npm >/dev/null 2>&1; then
  printf 'Installing required qmd retrieval helper...\n'
  if npm install -g @tobilu/qmd; then
    printf 'qmd installed.\n'
  else
    printf 'qmd installation failed. OpenWiki requires qmd.\n' >&2
    printf 'Fix npm/qmd installation, then run this installer again.\n' >&2
    exit 1
  fi
else
  printf 'npm not found. OpenWiki requires qmd, and qmd is installed through npm.\n' >&2
  printf 'Install Node.js/npm first, then run this installer again.\n' >&2
  exit 1
fi

if ! command -v qmd >/dev/null 2>&1; then
  printf 'qmd verification failed. qmd is not on PATH after installation.\n' >&2
  exit 1
fi

mkdir -p my-wiki/.codex/skills my-wiki/.claude/skills
for skill_dir in openwiki/skill_templates/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  name="$(basename "$skill_dir")"
  rm -rf "my-wiki/.codex/skills/$name" "my-wiki/.claude/skills/$name"
  cp -R "$skill_dir" my-wiki/.codex/skills/
  cp -R "$skill_dir" my-wiki/.claude/skills/
done

printf 'OpenWiki installed. Obsidian vault ready: my-wiki/\n'
printf 'Open my-wiki/ in Obsidian, then use openwiki-init, openwiki-add, openwiki-chat, or openwiki-category from Claude Code or Codex.\n'
