$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

Write-Host "OpenWiki one-click installer"
Write-Host "Checking Python environment..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python was not found. Install Python 3.10+ first, then run this installer again."
    exit 1
}

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Error "OpenWiki requires Python 3.10 or newer."
    python --version
    exit 1
}

python -m pip --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip was not found for Python. Install/enable pip, then run this installer again."
    exit 1
}

Write-Host "Installing OpenWiki Python package and dependencies..."
python -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Error "OpenWiki Python package installation failed."
    exit $LASTEXITCODE
}

Write-Host "Verifying Python dependencies..."
$verifyPython = @'
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
'@
$verifyPython | python -
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python dependency verification failed."
    exit $LASTEXITCODE
}

if (Get-Command qmd -ErrorAction SilentlyContinue) {
    Write-Host "qmd already installed."
}
elseif (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Installing required qmd retrieval helper..."
    npm install -g @tobilu/qmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "qmd installed."
    }
    else {
        Write-Error "qmd installation failed. OpenWiki requires qmd. Fix npm/qmd installation, then run this installer again."
        exit 1
    }
}
else {
    Write-Error "npm not found. OpenWiki requires qmd, and qmd is installed through npm. Install Node.js/npm first, then run this installer again."
    exit 1
}

if (-not (Get-Command qmd -ErrorAction SilentlyContinue)) {
    Write-Error "qmd verification failed. qmd is not on PATH after installation."
    exit 1
}

New-Item -ItemType Directory -Force -Path "my-wiki/.codex/skills" | Out-Null
New-Item -ItemType Directory -Force -Path "my-wiki/.claude/skills" | Out-Null
Get-ChildItem -Path "openwiki/skill_templates" -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName "SKILL.md")) {
        $name = $_.Name
        Remove-Item -Recurse -Force "my-wiki/.codex/skills/$name" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "my-wiki/.claude/skills/$name" -ErrorAction SilentlyContinue
        Copy-Item -Recurse -Path $_.FullName -Destination "my-wiki/.codex/skills/" -Force
        Copy-Item -Recurse -Path $_.FullName -Destination "my-wiki/.claude/skills/" -Force
    }
}

Write-Host "OpenWiki installed. Obsidian vault ready: my-wiki/"
Write-Host "Open my-wiki/ in Obsidian, then use openwiki-init, openwiki-add, openwiki-chat, or openwiki-category from Claude Code or Codex."
