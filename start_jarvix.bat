@echo off
title Jarvix Agent
echo ⚡ Starting Jarvix System...

:: Check if venv exists
if not exist venv (
    echo ❌ Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit
)

:: Activate and Run
call venv\Scripts\activate
echo 🤖 Bot is active. Press Ctrl+C to stop.
python -m jarvix.agents.telegram
pause