@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cd /d "%~dp0"
title ⚡ JARVIX AI ASSISTANT - INTELLIGENT SETUP SYSTEM
color 0D

cls
echo.
echo.
echo.
color 0D
echo.
echo.
echo            ╔════════════════════════════════════════════════════════════╗
echo            ║                                                            ║
echo            ║         ██╗ █████╗ ██████╗ ██╗   ██╗██╗██╗  ██╗          ║
echo            ║         ██║██╔══██╗██╔══██╗██║   ██║██║╚██╗██╔╝          ║
echo            ║         ██║███████║██████╔╝██║   ██║██║ ╚███╔╝           ║
echo            ║    ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║ ██╔██╗           ║
echo            ║    ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║██╔╝ ██╗          ║
echo            ║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚═╝  ╚═╝          ║
echo            ║                                                            ║
echo            ║    ════════════════════════════════════════════════════    ║
echo            ║                                                            ║
echo            ║            ⚡  A R T I F I C I A L   B R A I N  ⚡         ║
echo            ║                                                            ║
echo            ║              「 Next-Gen AI Assistant v2.0 」              ║
echo            ║                                                            ║
echo            ║    ════════════════════════════════════════════════════    ║
echo            ║                                                            ║
echo            ║              [ S Y S T E M   R E A D Y ]                  ║
echo            ║                                                            ║
echo            ╚════════════════════════════════════════════════════════════╝
echo.
echo                         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
echo.
echo.
color 0B
echo          ┌────────────────────────────────────────────────────────────┐
echo          │    🧠 NEURAL NETWORK INITIALIZATION SEQUENCE ACTIVE 🧠     │
echo          └────────────────────────────────────────────────────────────┘
echo.
timeout /t 1 /nobreak >nul

:: ════════════════════ STEP 1 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  🔍 PHASE [1/6] → Python Runtime Detection              ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.

:: Initialize PYTHON_CMD to empty
set "PYTHON_CMD="

:: Try python command directly first (most common on Windows)
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    color 0A
    echo             ✓ Python detected via direct command
    color 0B
    goto :FoundPython
)

:: Try py launcher with 3.11
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3.11"
    color 0A
    echo             ✓ Python 3.11 detected via launcher
    color 0B
    goto :FoundPython
)

:: Try py launcher with any Python 3
py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
    color 0A
    echo             ✓ Python 3.x detected via launcher
    color 0B
    goto :FoundPython
)

:: Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python3"
    color 0A
    echo             ✓ Python3 detected via direct command
    color 0B
    goto :FoundPython
)

color 0C
echo.
echo             ✗ CRITICAL ERROR: Python runtime not found!
echo             ℹ Install Python 3.11 from https://python.org
echo             ℹ Check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:FoundPython
timeout /t 1 /nobreak >nul
echo.

:: ════════════════════ STEP 2 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  🏗️  PHASE [2/6] → Virtual Environment Construction      ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.

if exist venv (
    color 0E
    echo             ⚠ Removing previous environment...
    color 0B
    rmdir /s /q venv
)

echo             ► Building isolated Python environment...
%PYTHON_CMD% -m venv venv

if errorlevel 1 (
    color 0C
    echo             ✗ Environment creation failed
    pause
    exit /b 1
)
color 0A
echo             ✓ Virtual environment ready
color 0B
timeout /t 1 /nobreak >nul
echo.

:: ════════════════════ STEP 3 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  📦 PHASE [3/6] → Neural Dependencies Installation       ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.
echo             ► Activating environment...
call venv\Scripts\activate
echo             ► Upgrading pip package manager...
python -m pip install --upgrade pip --quiet
echo             ► Installing required libraries...
echo.
pip install -e .

if errorlevel 1 (
    color 0C
    echo.
    echo             ✗ Installation failed - Check internet connection
    pause
    exit /b 1
)
color 0A
echo.
echo             ✓ All dependencies installed successfully
color 0B
timeout /t 1 /nobreak >nul
echo.

:: ════════════════════ STEP 4 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  🧠 PHASE [4/6] → AI Core Verification (Ollama)          ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.
set "OLLAMA_RETRY=0"
:CheckOllama
ollama list >nul 2>&1
if errorlevel 1 (
    color 0E
    echo             ⚠ Waiting for Ollama service...
    color 0B
    timeout /t 5 /nobreak >nul
    set /a OLLAMA_RETRY+=1
    if defined OLLAMA_RETRY if !OLLAMA_RETRY! LSS 6 goto CheckOllama
    color 0C
    echo             ✗ Ollama not responding
    echo             ℹ Ensure Ollama is running (check system tray)
    pause
    exit /b 1
)
ollama list | findstr /i "qwen2.5-coder:7b" >nul
if errorlevel 1 (
    color 0D
    echo             ⚠ Downloading AI Neural Model...
    echo             ℹ Size: ~4.7GB │ Time: 5-15 minutes
    echo             ► qwen2.5-coder:7b
    echo.
    color 0B
    ollama pull qwen2.5-coder:7b
    color 0A
    echo.
    echo             ✓ AI Model downloaded and initialized
    color 0B
) else (
    color 0A
    echo             ✓ AI Model verified and operational
    color 0B
)
timeout /t 1 /nobreak >nul
echo.

:: ════════════════════ STEP 5 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  ⚙️  PHASE [5/6] → Silent Launch Configuration           ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.

if not exist .env (
    (
        echo TELEGRAM_TOKEN=PASTE_TOKEN_HERE
        echo MODEL_NAME=qwen2.5-coder:7b
    ) > .env
    color 0E
    echo             ⚠ Configuration file created
    echo             ℹ Add your Telegram token to .env
    color 0B
)

:: Create the VBS launcher script
(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.Run chr^(34^) ^& "%~dp0start_jarvix.bat" ^& chr^(34^), 0
    echo Set WshShell = Nothing
) > run_silent.vbs

color 0A
echo             ✓ Silent launcher created
color 0B
timeout /t 1 /nobreak >nul
echo.

:: ════════════════════ STEP 6 ════════════════════
color 0E
echo          ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
color 0F
echo          ┃  🚀 PHASE [6/6] → Windows Auto-Start Integration        ┃
color 0E
echo          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
color 0B
echo.

:: Get the Windows Startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Remove old startup entries if they exist
if exist "%STARTUP_FOLDER%\PikachuAgent.lnk" (
    echo             ► Cleaning legacy entries...
    del "%STARTUP_FOLDER%\PikachuAgent.lnk" >nul 2>&1
)

if exist "%STARTUP_FOLDER%\Pikachu.lnk" (
    del "%STARTUP_FOLDER%\Pikachu.lnk" >nul 2>&1
)

if exist "%STARTUP_FOLDER%\run_silent.vbs" (
    del "%STARTUP_FOLDER%\run_silent.vbs" >nul 2>&1
)

:: Create a VBS script to generate the shortcut
echo             ► Configuring Windows startup...

:: This VBS script will create a proper Windows shortcut
(
    echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
    echo Set oShellLink = WshShell.CreateShortcut^("%STARTUP_FOLDER%\JarvixAssistant.lnk"^)
    echo oShellLink.TargetPath = "%~dp0run_silent.vbs"
    echo oShellLink.WorkingDirectory = "%~dp0"
    echo oShellLink.Description = "Jarvix Desktop Assistant - Auto Start"
    echo oShellLink.IconLocation = "shell32.dll,137"
    echo oShellLink.Save
) > create_startup_shortcut.vbs

:: Execute the VBS script to create the shortcut
cscript //nologo create_startup_shortcut.vbs

:: Clean up the temporary VBS script
del create_startup_shortcut.vbs

:: Verify the shortcut was created
if exist "%STARTUP_FOLDER%\JarvixAssistant.lnk" (
    color 0A
    echo             ✓ Auto-start enabled
    echo             ✓ Will launch on system boot
    color 0B
) else (
    color 0E
    echo             ⚠ Auto-start setup failed
    echo             ℹ Manual copy required to: %STARTUP_FOLDER%
    color 0B
)

timeout /t 1 /nobreak >nul
echo.
echo.
color 0A
echo.
echo                ╔══════════════════════════════════════════════════════╗
echo                ║                                                      ║
echo                ║          ✨ SETUP COMPLETE — ALL SYSTEMS GO ✨       ║
echo                ║                                                      ║
echo                ║             JARVIX AI IS READY TO ASSIST             ║
echo                ║                                                      ║
echo                ╚══════════════════════════════════════════════════════╝
echo.
color 0D
echo          ┌────────────────────────────────────────────────────────────┐
echo          │  📋 FINAL STEPS TO ACTIVATE JARVIX                         │
echo          ├────────────────────────────────────────────────────────────┤
color 0F
echo          │                                                            │
echo          │  1️⃣  Configure Telegram Token                             │
color 0B
echo          │      → Open .env file                                     │
echo          │      → Paste your TELEGRAM_TOKEN                          │
color 0F
echo          │                                                            │
echo          │  2️⃣  Launch Jarvix AI                                      │
color 0B
echo          │      → Double-click: run_silent.vbs                       │
echo          │      → Or restart Windows (auto-start enabled)            │
color 0F
echo          │                                                            │
echo          │  3️⃣  Disable Auto-Start (Optional)                         │
color 0B
echo          │      → Delete: JarvixAssistant.lnk                        │
echo          │      → From: %STARTUP_FOLDER%
color 0D
echo          │                                                            │
echo          └────────────────────────────────────────────────────────────┘
echo.
color 0B
pause