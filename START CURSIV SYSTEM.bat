@echo off
setlocal enabledelayedexpansion
title JWFrontierEvoCore — System Launcher
color 07
cd /d "%~dp0"

echo.
echo  ================================================================
echo   JWFrontierEvoCore v1.0  ^|  Cursiv-v2.1.5
echo   Sovereign Agent Temple  ^|  Full System Launcher
echo  ================================================================
echo.
echo  Components:
echo    [1] Cursiv Sacred UI    ^|  http://localhost:8501
echo    [2] JW Main Chat        ^|  http://localhost:7860
echo    [3] JW Command Nexus    ^|  http://localhost:7861
echo.
echo  ================================================================
echo.

:: ═══════════════════════════════════════════════════════════════════
::  PHASE 1 — PYTHON CHECK
:: ═══════════════════════════════════════════════════════════════════

echo  [PHASE 1/3] Checking Python...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found.
    echo.
    echo  Install Python 3.11+ from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  Python %PYVER% found.

:: Check version is at least 3.11
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if !PY_MAJOR! LSS 3 (
    echo  [ERROR] Python 3.11+ required. Found: %PYVER%
    pause
    exit /b 1
)
if !PY_MAJOR! EQU 3 if !PY_MINOR! LSS 11 (
    echo  [WARNING] Python 3.11+ recommended. Found: %PYVER%
    echo  Continuing anyway — some features may not work.
)

echo.

:: ═══════════════════════════════════════════════════════════════════
::  PHASE 2 — INSTALL DEPENDENCIES
:: ═══════════════════════════════════════════════════════════════════

echo  [PHASE 2/3] Installing / verifying dependencies...
echo.

:: Upgrade pip silently
echo   Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Core — numpy 2.x first (required for Gradio on Python 3.13)
echo   numpy ^>^=2.0 ...
python -m pip install "numpy>=2.0" --quiet

:: Streamlit
echo   streamlit ^>^=1.32.0 ...
python -m pip install "streamlit>=1.32.0" --quiet

:: Gradio
echo   gradio ^>^=4.44.0 ...
python -m pip install "gradio>=4.44.0" --quiet

:: Install the Cursiv package itself (editable)
echo   cursiv-v2.1.5 (editable install) ...
python -m pip install -e . --quiet 2>nul

:: Optional — report Ollama status
echo.
echo   Checking Ollama (optional, for local inference)...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo   Ollama found. Local inference available.
    set OLLAMA_FOUND=1
) else (
    echo   Ollama not found. Using xAI Grok or paste key in Chat UI.
    echo   Install from: https://ollama.com  then run: ollama pull mistral
    set OLLAMA_FOUND=0
)

echo.
echo  All dependencies verified.
echo.

:: ═══════════════════════════════════════════════════════════════════
::  PHASE 3 — LAUNCH ALL COMPONENTS
:: ═══════════════════════════════════════════════════════════════════

echo  [PHASE 3/3] Launching system components...
echo.

:: Create .cursiv directory for shared state
if not exist ".cursiv" mkdir ".cursiv"

:: ── Window 1: JW Main Chat (Gradio port 7860) ──────────────────────
echo   Starting JW Main Chat        (port 7860)...
start "JW Main Chat — Port 7860" cmd /k ^
    "title JW Main Chat ^| JWFrontierEvoCore && color 07 && cd /d "%~dp0" && echo. && echo  JW MAIN CHAT — http://localhost:7860 && echo. && python -m cursiv_v215.ui.chat_app"

:: Brief pause so ports don't race
timeout /t 2 /nobreak >nul

:: ── Window 2: JW Command Nexus (Gradio port 7861) ──────────────────
echo   Starting JW Command Nexus    (port 7861)...
start "JW Command Nexus — Port 7861" cmd /k ^
    "title JW Command Nexus ^| Port 7861 && color 07 && cd /d "%~dp0" && echo. && echo  JW COMMAND NEXUS — http://localhost:7861 && echo. && python -m cursiv_v215.ui.nexus_app"

timeout /t 2 /nobreak >nul

:: ── Window 3: Cursiv Sacred UI (Streamlit port 8501) ───────────────
echo   Starting Cursiv Sacred UI    (port 8501)...
start "Cursiv Sacred UI — Port 8501" cmd /k ^
    "title Cursiv Sacred UI ^| Port 8501 && color 07 && cd /d "%~dp0" && echo. && echo  CURSIV SACRED UI — http://localhost:8501 && echo. && python -m streamlit run cursiv_v215/ui/app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false"

:: ── Window 4 (optional): Ollama local inference ────────────────────
if %OLLAMA_FOUND% equ 1 (
    echo   Starting Ollama local model  (mistral)...
    start "Ollama — Local Inference" cmd /k "title Ollama ^| Local Inference && ollama run mistral"
    timeout /t 2 /nobreak >nul
)

:: ── Window 5 (optional): Conversation Watcher background ───────────
echo   Starting conversation watcher (training data collector)...
start "Cursiv Watcher — Training Collector" cmd /k ^
    "title Cursiv Watcher ^| Training Collector && color 07 && cd /d "%~dp0" && echo. && echo  CONVERSATION WATCHER — collecting training examples && echo  Quality threshold: 0.65  Poll interval: 15s && echo. && python -m cursiv_v215.training.watcher"

echo.

:: ═══════════════════════════════════════════════════════════════════
::  OPEN BROWSERS
:: ═══════════════════════════════════════════════════════════════════

echo  Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo  Opening browser tabs...
echo.

:: Open all three in browser with staggered delays
start "" "http://localhost:7860"
timeout /t 1 /nobreak >nul
start "" "http://localhost:7861"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8501"

:: ═══════════════════════════════════════════════════════════════════
::  DONE
:: ═══════════════════════════════════════════════════════════════════

echo.
echo  ================================================================
echo.
echo   SYSTEM ONLINE
echo.
echo   JW Main Chat     http://localhost:7860  [RUNNING]
echo   JW Command Nexus http://localhost:7861  [RUNNING]
echo   Cursiv Sacred UI http://localhost:8501  [RUNNING]
if %OLLAMA_FOUND% equ 1 (
echo   Ollama Mistral   local inference        [RUNNING]
)
echo   Training Watcher background collector   [RUNNING]
echo.
echo  ================================================================
echo.
echo   HOW TO USE:
echo   1. Paste your xAI API key in the Chat window (port 7860)
echo   2. Open the Nexus (port 7861) alongside to repurpose agents
echo   3. Use the Sacred UI (port 8501) to create and evolve agents
echo   4. Training Watcher auto-collects good exchanges in background
echo.
echo   To stop the system: close all component windows individually
echo   or press Ctrl+C in each window.
echo.
echo  ================================================================
echo.
echo  This launcher window can now be closed.
echo.
pause
