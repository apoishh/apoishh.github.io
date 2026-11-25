@echo off
title APOISHH website
cd /d "%~dp0"
echo.
echo   APOISHH website - preview at http://localhost:8080
echo   Drop photos into the photos folders or edit js\config.js.
echo   When changes are ready you'll be asked: Publish to GitHub now?
echo   Type  y + Enter  to publish,  n  to wait,  p + Enter  to publish anytime.
echo   Close this window when you're done.
echo.
python serve.py
pause
