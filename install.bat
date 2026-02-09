@echo off
chcp 65001 >nul
cd /d "%~dp0"
title JARVIX - One-Click Installer

:: Run the PowerShell installer (bypass execution policy for users who haven't run scripts before)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if errorlevel 1 (
    echo.
    echo  If you see "cannot be loaded because running scripts is disabled":
    echo  Open PowerShell as Administrator and run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo  Then run install.bat again.
    echo.
    pause
    exit /b 1
)

pause
