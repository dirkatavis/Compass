# Compass Automation Setup Script
# Runs inside an existing repo checkout.

[CmdletBinding()]
param(
    [switch]$RecreateVenv,
    [switch]$SkipValidate,
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Setup {
    param(
        [Parameter(Mandatory)] [string]$Message,
        [ValidateSet('INFO','SUCCESS','WARN','ERROR')] [string]$Level = 'INFO'
    )

    $color = switch ($Level) {
        'SUCCESS' { 'Green' }
        'ERROR'   { 'Red' }
        'WARN'    { 'Yellow' }
        default   { 'Cyan' }
    }

    Write-Host "[$Level] $Message" -ForegroundColor $color
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot 'venv'
$RequirementsPath = Join-Path $ProjectRoot 'requirements.txt'

Write-Setup "Project root: $ProjectRoot"

# Prefer 'py' launcher if available (more reliable on Windows), else fall back to 'python'
$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = 'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = 'python'
} else {
    throw "Python not found. Install Python 3.13+ and ensure 'py' or 'python' is on PATH."
}

if ($RecreateVenv -and (Test-Path $VenvPath)) {
    Write-Setup "Removing existing venv at $VenvPath" 'WARN'
    Remove-Item -Recurse -Force $VenvPath
}

if (-not (Test-Path $VenvPath)) {
    Write-Setup 'Creating virtual environment (venv/)...'
    if ($PythonCmd -eq 'py') {
        & py -3 -m venv $VenvPath
    } else {
        & python -m venv $VenvPath
    }
    Write-Setup 'Virtual environment created' 'SUCCESS'
} else {
    Write-Setup 'Virtual environment already exists' 'SUCCESS'
}

$PythonExe = Join-Path $VenvPath 'Scripts\python.exe'
$PipExe = Join-Path $VenvPath 'Scripts\pip.exe'

Write-Setup 'Upgrading pip...'
& $PythonExe -m pip install --upgrade pip | Out-Null
Write-Setup 'pip upgraded' 'SUCCESS'

if (-not $SkipInstall) {
    if (Test-Path $RequirementsPath) {
        Write-Setup "Installing dependencies from $RequirementsPath..."
        & $PythonExe -m pip install -r $RequirementsPath
        Write-Setup 'Dependencies installed' 'SUCCESS'
    } else {
        Write-Setup 'requirements.txt not found; installing minimal deps...' 'WARN'
        & $PythonExe -m pip install selenium pytest pytest-html webdriver-manager
        Write-Setup 'Minimal dependencies installed' 'SUCCESS'
    }
} else {
    Write-Setup 'Skipping dependency installation (SkipInstall)' 'WARN'
}

if (-not $SkipValidate) {
    $Validator = Join-Path $ProjectRoot 'validate_setup.py'
    if (Test-Path $Validator) {
        Write-Setup 'Running environment validation...'
        & $PythonExe $Validator
    } else {
        Write-Setup 'validate_setup.py missing; running quick import check...' 'WARN'
        & $PythonExe -c "import selenium, pytest; from core import driver_manager; print('OK')"
    }
}

Write-Setup 'SETUP COMPLETE' 'SUCCESS'
Write-Setup "Activate venv: .\venv\Scripts\Activate.ps1"
Write-Setup "Run tests: pytest -q -s tests/test_mva_complaints_tab_fixed.py"
Write-Setup "Run script: python run_compass.py"
