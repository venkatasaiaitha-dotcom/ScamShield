@echo off
title ScamShield AI Safety Agent
echo =======================================================
echo    🛡️ ScamShield — AI-Powered Scam Detection Agent
echo    Detect. Understand. Stay Safe.
echo =======================================================
echo.
echo Starting ScamShield Protection Agent on http://127.0.0.1:8000 ...
echo.
cd /d "%~dp0"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
