@echo off
title JW Main Chat — JWFrontierEvoCore
echo.
echo  ========================================================
echo   JW MAIN CHAT — JWFrontierEvoCore v1.0
echo   Cursiv-v2.1.5 ^| http://localhost:7860
echo  ========================================================
echo.
echo  Starting main chat interface...
echo  Open your browser at: http://localhost:7860
echo.
echo  To enable xAI Grok intelligence:
echo    Paste your xAI API key into the key slot in the UI.
echo.
echo  Run alongside the Nexus for full control:
echo    Launch Nexus.bat  ^|  http://localhost:7861
echo.
echo  To use local Ollama instead of xAI:
echo    ollama run mistral   (in a separate terminal)
echo.

cd /d "%~dp0"
python -m cursiv_v215.ui.chat_app

pause
