# Compass Automation Setup Script (PowerShell)
# 
# This script automatically configures the development environment for the Compass automation project.
# It creates a virtual environment, installs dependencies, and validates the setup.
#
# Usage:
#   .\setup.ps1
#
# Requirements:
#   - PowerShell 5.1+ or PowerShell Core 7+
#   - Python 3.8+ installed and in PATH

param(
    [switch]$SkipDevDependencies,
    [switch]$Verbose
)

# Set strict mode and stop on errors
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$Green = if ($Host.UI.SupportsVirtualTerminal) { "`e[92m" } else { "" }
$Red = if ($Host.UI.SupportsVirtualTerminal) { "`e[91m" } else { "" }
$Yellow = if ($Host.UI.SupportsVirtualTerminal) { "`e[93m" } else { "" }
$Blue = if ($Host.UI.SupportsVirtualTerminal) { "`e[94m" } else { "" }
$Reset = if ($Host.UI.SupportsVirtualTerminal) { "`e[0m" } else { "" }

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $color = switch ($Level) {
        "SUCCESS" { $Green }
        "ERROR" { $Red }
        "WARN" { $Yellow }
        "INFO" { $Blue }
        default { "" }
    }
    
    Write-Host "${color}[${Level}]${Reset} $Message"
}

# Get project root directory
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot "venv"

Write-Log "Starting Compass Automation Setup..." "INFO"
Write-Log "Project root: $ProjectRoot" "INFO"

try {
    # Check Python version
    Write-Log "Checking Python installation..." "INFO"
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python is not installed or not in PATH. Please install Python 3.8+ and add it to your PATH."
    }
    
    # Parse version
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            throw "Python 3.8+ required, found $major.$minor"
        }
        
        Write-Log "✓ $pythonVersion found" "SUCCESS"
    } else {
        throw "Could not determine Python version"
    }
    
    # Create virtual environment
    Write-Log "Setting up virtual environment..." "INFO"
    if (Test-Path $VenvPath) {
        Write-Log "✓ Virtual environment already exists" "SUCCESS"
    } else {
        Write-Log "Creating virtual environment..." "INFO"
        python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Log "✓ Virtual environment created" "SUCCESS"
    }
    
    # Set executable paths
    $PythonExe = Join-Path $VenvPath "Scripts\python.exe"
    $PipExe = Join-Path $VenvPath "Scripts\pip.exe"
    
    # Upgrade pip
    Write-Log "Upgrading pip..." "INFO"
    & $PipExe install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip"
    }
    Write-Log "✓ pip upgraded" "SUCCESS"
    
    # Install core dependencies
    Write-Log "Installing core dependencies..." "INFO"
    $coreDeps = @(
        "selenium>=4.0.0",
        "pytest>=7.0.0",
        "pytest-html"
    )
    
    foreach ($dep in $coreDeps) {
        Write-Log "Installing $dep..." "INFO"
        & $PipExe install $dep
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install $dep"
        }
    }
    Write-Log "✓ Core dependencies installed" "SUCCESS"
    
    # Install development dependencies (optional)
    if (-not $SkipDevDependencies) {
        $installDev = Read-Host "Install development dependencies (flake8, black, isort)? [y/N]"
        if ($installDev -in @('y', 'Y', 'yes', 'Yes')) {
            $devDeps = @("flake8", "black", "isort")
            
            foreach ($dep in $devDeps) {
                Write-Log "Installing $dep..." "INFO"
                & $PipExe install $dep
                if ($LASTEXITCODE -ne 0) {
                    Write-Log "Warning: Failed to install $dep" "WARN"
                }
            }
            Write-Log "✓ Development dependencies installed" "SUCCESS"
        }
    }
    
    # Check for msedgedriver.exe
    Write-Log "Checking for msedgedriver.exe..." "INFO"
    $driverPath = Join-Path $ProjectRoot "msedgedriver.exe"
    if (Test-Path $driverPath) {
        Write-Log "✓ msedgedriver.exe found" "SUCCESS"
    } else {
        Write-Log "⚠ msedgedriver.exe not found in project root" "WARN"
        Write-Log "Please download the correct version from:" "WARN"
        Write-Log "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/" "WARN"
        Write-Log "Place it in: $ProjectRoot" "WARN"
    }
    
    # Create sample config files
    Write-Log "Checking configuration files..." "INFO"
    $configDir = Join-Path $ProjectRoot "config"
    $configFile = Join-Path $configDir "config.json"
    
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    if (Test-Path $configFile) {
        Write-Log "✓ config.json already exists" "SUCCESS"
    } else {
        $sampleConfig = @{
            username = "your.email@company.com"
            password = "YourPassword123!"
            login_id = "YOUR_ID"
            delay_seconds = 2
            mva_entry_delay_seconds = 5
            credentials = @{
                sso_email = "your.email@company.com"
            }
            logging = @{
                level = "INFO"
                format = "[%(levelname)s] [compass.automation] [%(asctime)s] %(message)s"
            }
        } | ConvertTo-Json -Depth 3
        
        $sampleConfig | Out-File -FilePath $configFile -Encoding UTF8
        Write-Log "✓ Sample config.json created - PLEASE UPDATE WITH YOUR CREDENTIALS" "WARN"
    }
    
    # Create sample data files
    Write-Log "Checking data files..." "INFO"
    $dataDir = Join-Path $ProjectRoot "data"
    $mvaFile = Join-Path $dataDir "mva.csv"
    
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    }
    
    if (Test-Path $mvaFile) {
        Write-Log "✓ mva.csv already exists" "SUCCESS"
    } else {
        $sampleData = @"
MVA
12345
67890
"@
        $sampleData | Out-File -FilePath $mvaFile -Encoding UTF8
        Write-Log "✓ Sample mva.csv created - ADD YOUR MVA NUMBERS" "WARN"
    }
    
    # Validate project structure
    Write-Log "Validating project structure..." "INFO"
    $requiredDirs = @("config", "core", "data", "flows", "pages", "tests", "utils")
    $missingDirs = @()
    
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $ProjectRoot $dir
        if (-not (Test-Path $dirPath)) {
            $missingDirs += $dir
        }
    }
    
    if ($missingDirs.Count -gt 0) {
        Write-Log "⚠ Missing directories: $($missingDirs -join ', ')" "WARN"
    } else {
        Write-Log "✓ Project structure validated" "SUCCESS"
    }
    
    # Run basic tests
    Write-Log "Running basic environment tests..." "INFO"
    
    $testScript = @'
import sys
print("Testing basic imports...")

try:
    import selenium
    print("✓ Selenium import successful")
except ImportError as e:
    print(f"✗ Selenium import failed: {e}")
    sys.exit(1)

try:
    import pytest
    print("✓ Pytest import successful")
except ImportError as e:
    print(f"✗ Pytest import failed: {e}")
    sys.exit(1)

try:
    from config.config_loader import get_config
    print("✓ Config loader import successful")
except ImportError as e:
    print(f"✗ Config loader import failed: {e}")
    sys.exit(1)

print("✓ All basic tests passed!")
'@
    
    $tempFile = New-TemporaryFile
    $testScript | Out-File -FilePath $tempFile.FullName -Encoding UTF8
    
    try {
        Push-Location $ProjectRoot
        & $PythonExe $tempFile.FullName
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✓ Basic environment tests passed" "SUCCESS"
        } else {
            throw "Basic tests failed"
        }
    } finally {
        Pop-Location
        Remove-Item $tempFile.FullName -Force -ErrorAction SilentlyContinue
    }
    
    # Generate requirements.txt
    Write-Log "Generating requirements.txt..." "INFO"
    $requirementsFile = Join-Path $ProjectRoot "requirements.txt"
    
    try {
        & $PipExe freeze | Out-File -FilePath $requirementsFile -Encoding UTF8
        Write-Log "✓ requirements.txt generated" "SUCCESS"
    } catch {
        Write-Log "⚠ Could not generate requirements.txt: $_" "WARN"
    }
    
    # Print next steps
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "SETUP COMPLETE! Next Steps:" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Activate virtual environment:" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Update configuration files:" -ForegroundColor Cyan
    Write-Host "   - config\config.json (add your credentials)" -ForegroundColor Yellow
    Write-Host "   - data\mva.csv (add your MVA numbers)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Ensure msedgedriver.exe is in project root" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Run tests:" -ForegroundColor Cyan
    Write-Host "   pytest -v tests\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "5. Run standalone:" -ForegroundColor Cyan
    Write-Host "   python run_compass.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For more info, see: Markdown_Files\README.md" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Green
    
    Write-Log "✓ Setup completed successfully!" "SUCCESS"
    
} catch {
    Write-Log "✗ Setup failed: $_" "ERROR"
    exit 1
}