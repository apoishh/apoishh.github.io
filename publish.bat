@echo off
rem Publish the site to GitHub right now (no waiting).
cd /d "%~dp0"
python git_sync.py --now
echo.
echo The live site updates 1-2 minutes after "Published". Press Ctrl+F5 on the site to see it.
pause
