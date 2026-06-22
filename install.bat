@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
  echo.
  echo OpenWiki installation failed. Fix the message above, then run install.bat again.
  pause
  exit /b 1
)
echo.
echo Done. Use openwiki-init, openwiki-add, openwiki-chat, or openwiki-category from Claude Code or Codex.
pause
