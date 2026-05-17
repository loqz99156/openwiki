$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

python -m pip install -e .
New-Item -ItemType Directory -Force -Path "my-wiki/.claude/commands" | Out-Null
Copy-Item -Path "openwiki/command_templates/*.md" -Destination "my-wiki/.claude/commands/" -Force

Write-Host "OpenWiki installed. Obsidian vault ready: my-wiki/"
Write-Host "Open my-wiki/ in Obsidian, then run /init from the Claude Code plugin."
