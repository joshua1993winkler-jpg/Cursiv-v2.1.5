@echo off
setlocal enabledelayedexpansion
title Cursiv v2.1.5 — Setup ^& Launch
color 07
cls

echo.
echo  ╔═══════════════════════════════════════════════╗
echo  ║     CURSIV v2.1.5 — SETUP ^& LAUNCH           ║
echo  ║     Black . Rose Gold . Glowing Lapis Eye     ║
echo  ╚═══════════════════════════════════════════════╝
echo.

:: ── Check Python ─────────────────────────────────────────────────────────────
echo  [1/5] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found.
    echo.
    echo  Install Python 3.11+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] %PYVER%

:: ── Check pip ────────────────────────────────────────────────────────────────
echo  [2/5] Checking pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] pip not found. Reinstall Python with pip included.
    pause
    exit /b 1
)
echo  [OK] pip found

:: ── Upgrade pip silently ──────────────────────────────────────────────────────
echo  [3/5] Upgrading pip...
python -m pip install --upgrade pip -q
echo  [OK] pip up to date

:: ── Install requirements ──────────────────────────────────────────────────────
echo  [4/5] Installing requirements...
echo.
cd /d "%~dp0"

python -m pip install -e . -q
if %errorlevel% neq 0 (
    echo  [WARN] editable install had issues — trying requirements.txt directly...
    python -m pip install -r requirements.txt -q
    if %errorlevel% neq 0 (
        echo  [ERROR] Could not install requirements. Check your internet connection.
        pause
        exit /b 1
    )
)

:: Install streamlit explicitly in case pyproject.toml install missed it
python -m pip install streamlit -q
echo  [OK] All requirements installed

:: ── Check Ollama (optional, non-blocking) ────────────────────────────────────
echo.
echo  [5/5] Checking optional services...
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Ollama found — local sovereign LLM available
) else (
    echo  [INFO] Ollama not found — will use xAI/OpenAI/embedded fallback
    echo         To enable local sovereign mode: https://ollama.com/download
)

:: Check for API keys in environment
if defined XAI_API_KEY (
    echo  [OK] XAI_API_KEY detected
) else (
    echo  [INFO] XAI_API_KEY not set — xAI Grok unavailable
)
if defined OPENAI_API_KEY (
    echo  [OK] OPENAI_API_KEY detected
) else (
    echo  [INFO] OPENAI_API_KEY not set — OpenAI unavailable
)
echo  [OK] Embedded symbolic fallback always available ^(no API needed^)

:: ── Launch ────────────────────────────────────────────────────────────────────
echo.
echo  ════════════════════════════════════════════════
echo  Setup complete. Launching the Sacred UI...
echo  ════════════════════════════════════════════════
echo.
echo  Opening at: http://localhost:8501
echo  Press Ctrl+C in this window to stop the server.
echo.

python -m streamlit run cursiv_v215/ui/app.py ^
    --server.port 8501 ^
    --server.headless false ^
    --browser.gatherUsageStats false ^
    --server.fileWatcherType none

echo.
echo  Server stopped.
pause
