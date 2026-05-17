@echo off
chcp 65001 >nul
title JW Command Nexus - Cursiv-v2.1.5
echo.
echo  ========================================================
echo   JW COMMAND NEXUS — JWFrontierEvoCore v1.0
echo   Cursiv-v2.1.5 ^| http://localhost:7861
echo  ========================================================
echo.
echo  Starting Nexus panel...
echo  Open your browser at: http://localhost:7861
echo.
echo  Tip: Keep Cursiv (port 8501) running in another window.
echo  The Nexus reads live from .cursiv/ shared state.
echo.

cd /d "%~dp0"
python -m cursiv_v215.ui.nexus_app

pause
