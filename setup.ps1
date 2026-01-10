# Compass Automation Setup Script (PowerShell)
# Simple, tested version for environment setup

param(
    [switch]$SkipDevDependencies
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Setup {
    param([string]$Message, [string]$Level = "INFO")
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$Level] $Message" -ForegroundColor $color
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot "venv"

Write-Setup "Starting Compass Automation Setup..." "INFO"
Write-Setup "Project root: $ProjectRoot" "INFO"

try {
    # Check Python
    Write-Setup "Checking Python installation..." "INFO"
    $pythonCheck = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found. Install Python 3.8+ and add to PATH."
    }
    Write-Setup "Found: $pythonCheck" "SUCCESS"
    
    # Create virtual environment
    Write-Setup "Setting up virtual environment..." "INFO"
    if (Test-Path $VenvPath) {
        Write-Setup "Virtual environment already exists" "SUCCESS"
    } else {
        python -m venv $VenvPath
        Write-Setup "Virtual environment created" "SUCCESS"
    }
    
    $PythonExe = Join-Path $VenvPath "Scripts\python.exe"
    $PipExe = Join-Path $VenvPath "Scripts\pip.exe"
    
    # Upgrade pip
    Write-Setup "Upgrading pip..." "INFO"
    & $PipExe install --upgrade pip | Out-Null
    Write-Setup "Pip upgraded" "SUCCESS"
    
    # Install core dependencies
    Write-Setup "Installing core dependencies..." "INFO"
    $coreDeps = @("selenium>=4.0.0", "pytest>=7.0.0", "pytest-html")
    
    foreach ($dep in $coreDeps) {
        Write-Setup "Installing $dep..." "INFO"
        & $PipExe install $dep | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install $dep"
        }
    }
    Write-Setup "Core dependencies installed" "SUCCESS"
    
    # Optional dev dependencies
    if (-not $SkipDevDependencies) {
        $installDev = Read-Host "Install development dependencies (flake8, black, isort)? [y/N]"
        if ($installDev -match "^[yY]") {
            $devDeps = @("flake8", "black", "isort")
            foreach ($dep in $devDeps) {
                Write-Setup "Installing $dep..." "INFO"
                & $PipExe install $dep | Out-Null
            }
            Write-Setup "Development dependencies installed" "SUCCESS"
        }
    }
    
    # Check msedgedriver
    $driverPath = Join-Path $ProjectRoot "msedgedriver.exe"
    if (Test-Path $driverPath) {
        Write-Setup "msedgedriver.exe found" "SUCCESS"
    } else {
        Write-Setup "msedgedriver.exe not found - download from Microsoft Edge WebDriver site" "WARN"
    }
    
    # Create config directory and files
    $configDir = Join-Path $ProjectRoot "config"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir | Out-Null
    }
    
    $configFile = Join-Path $configDir "config.json"
    if (-not (Test-Path $configFile)) {
        $sampleConfig = @{
            username = "your.email@company.com"
            password = "YourPassword123!"
            login_id = "YOUR_ID"
            delay_seconds = 2
            mva_entry_delay_seconds = 5
        } | ConvertTo-Json -Depth 3
        
        $sampleConfig | Out-File -FilePath $configFile -Encoding UTF8
        Write-Setup "Sample config.json created - UPDATE WITH YOUR CREDENTIALS" "WARN"
    }
    
    # Create data directory and files
    $dataDir = Join-Path $ProjectRoot "data"
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir | Out-Null
    }
    
    $mvaFile = Join-Path $dataDir "mva.csv"
    if (-not (Test-Path $mvaFile)) {
        "MVA`n12345`n67890" | Out-File -FilePath $mvaFile -Encoding UTF8
        Write-Setup "Sample mva.csv created - ADD YOUR MVA NUMBERS" "WARN"
    }
    
    # Test basic imports
    Write-Setup "Testing environment..." "INFO"
    & $PythonExe -c "import selenium, pytest; print('Environment test passed')" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Setup "Environment test passed" "SUCCESS"
    } else {
        Write-Setup "Environment test failed" "ERROR"
    }
    
    # Generate requirements.txt
    & $PipExe freeze | Out-File -FilePath (Join-Path $ProjectRoot "requirements.txt") -Encoding UTF8
    
    Write-Setup "" "INFO"
    Write-Setup "SETUP COMPLETE!" "SUCCESS"
    Write-Setup "" "INFO"
    Write-Setup "Next steps:" "INFO"
    Write-Setup "1. Activate environment: .\venv\Scripts\Activate.ps1" "INFO"
    Write-Setup "2. Update config/config.json with your credentials" "INFO"
    Write-Setup "3. Update data/mva.csv with your MVA numbers" "INFO"
    Write-Setup "4. Run validation: python validate_setup.py" "INFO"
    
} catch {
    Write-Setup "Setup failed: $_" "ERROR"
    exit 1
}