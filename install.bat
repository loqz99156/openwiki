@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
echo.
echo Done. Open my-wiki\ in Obsidian, then run /init from the Claude Code plugin.
pause
