<#
.SYNOPSIS
  One-click installer for JARVIX Desktop Assistant
  Automatically installs Python, Ollama, dependencies, and the AI model.
.EXAMPLE
  .\install.ps1
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Colors and helpers
function Write-Step { param($n, $msg) Write-Host "`n  [$n] $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  [!] $msg" -ForegroundColor Yellow }
function Write-Fail  { param($msg) Write-Host "  [X] $msg" -ForegroundColor Red }

function Test-CommandExists($cmd) {
    $null = Get-Command $cmd -ErrorAction SilentlyContinue
    return $?
}

function Test-PythonInstalled {
    $attempts = @(
        { python --version 2>&1 },
        { python3 --version 2>&1 },
        { py -3 --version 2>&1 }
    )
    foreach ($a in $attempts) {
        try {
            $v = & $a
            if ($v -match "Python 3\.(9|1[0-9])") { return $true }
        } catch {}
    }
    return $false
}

function Install-Python {
    Write-Step "1/4" "Checking for Python 3.11..."
    
    if (Test-PythonInstalled) {
        Write-Ok "Python is already installed."
        return $true
    }

    Write-Warn "Python not found. Installing via winget..."
    
    if (Test-CommandExists "winget") {
        try {
            winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
            # Refresh PATH for current session
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
            Start-Sleep -Seconds 2
            if (Test-PythonInstalled) {
                Write-Ok "Python installed successfully."
                return $true
            }
        } catch {
            Write-Warn "winget install failed: $_"
        }
    }

    Write-Warn "Installing Python from python.org..."
    $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pyInstaller = Join-Path $env:TEMP "python-3.11.9-amd64.exe"
    
    try {
        Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
        Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -Wait
        Remove-Item $pyInstaller -Force -ErrorAction SilentlyContinue
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
        Start-Sleep -Seconds 3
        if (Test-PythonInstalled) {
            Write-Ok "Python installed successfully."
            return $true
        }
    } catch {
        Write-Fail "Failed to install Python: $_"
    }

    Write-Fail "Could not install Python. Please install Python 3.11 from https://python.org and run install again."
    return $false
}

function Test-OllamaInstalled {
    return Test-CommandExists "ollama"
}

function Install-Ollama {
    Write-Step "2/4" "Checking for Ollama..."
    
    if (Test-OllamaInstalled) {
        Write-Ok "Ollama is already installed."
        return $true
    }

    Write-Warn "Ollama not found. Downloading and installing..."
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"
    $ollamaInstaller = Join-Path $env:TEMP "OllamaSetup.exe"
    
    try {
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller -UseBasicParsing
        Start-Process -FilePath $ollamaInstaller -ArgumentList "/SP-", "/VERYSILENT", "/NORESTART" -Wait
        Remove-Item $ollamaInstaller -Force -ErrorAction SilentlyContinue
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
        Start-Sleep -Seconds 5  # Give Ollama time to start
        if (Test-OllamaInstalled) {
            Write-Ok "Ollama installed successfully."
            return $true
        }
    } catch {
        Write-Fail "Failed to install Ollama: $_"
    }

    Write-Fail "Could not install Ollama. Please install from https://ollama.com and run install again."
    return $false
}

function Wait-OllamaReady {
    Write-Step "3/4" "Ensuring Ollama is running..."
    $maxAttempts = 12
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            & ollama list 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "Ollama is ready."
                return $true
            }
        } catch { }
        Write-Host "  Waiting for Ollama... ($attempt/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 5
    }
    Write-Warn "Ollama may still be starting. Setup will attempt to pull the model anyway."
    return $false
}

# ========== MAIN ==========
Clear-Host
Write-Host @"

        JARVIX ASSISTANT - ONE-CLICK INSTALLER
        ======================================
        This will install:
        - Python 3.11 (if missing)
        - Ollama AI engine (if missing)
        - Python dependencies
        - AI model (qwen2.5-coder:7b, ~4.7GB)

"@ -ForegroundColor Magenta

if (-not (Install-Python)) { exit 1 }
if (-not (Install-Ollama)) { exit 1 }
Wait-OllamaReady | Out-Null

Write-Step "4/4" "Running JARVIX setup (venv, deps, model)..."
& "$ProjectRoot\setup.bat"

Write-Host "`n  Done. Run start_jarvix.bat to launch JARVIX.`n" -ForegroundColor Green
