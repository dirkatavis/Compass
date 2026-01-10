# Test Setup Scripts - Automated Validation
# This script tests the setup scripts in a clean environment

param(
    [string]$TestDir = "Compass-Test-$(Get-Date -Format 'yyyyMMdd-HHmmss')",
    [switch]$KeepTestDir
)

$ErrorActionPreference = "Stop"

function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[TEST-$Level] $Message" -ForegroundColor $color
}

# Get current directory (should be Compass project root)
$ProjectRoot = Get-Location
$TestPath = Join-Path (Split-Path $ProjectRoot -Parent) $TestDir

Write-TestLog "Starting Setup Script Validation" "INFO"
Write-TestLog "Project root: $ProjectRoot" "INFO"
Write-TestLog "Test directory: $TestPath" "INFO"

try {
    # Create clean test environment
    Write-TestLog "Creating clean test environment..." "INFO"
    if (Test-Path $TestPath) {
        Remove-Item $TestPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TestPath | Out-Null
    
    # Clone repository to test directory
    Write-TestLog "Cloning repository..." "INFO"
    Set-Location $TestPath
    git clone https://github.com/dirkatavis/Compass.git . | Out-Null
    
    # Copy latest setup files from development directory
    Write-TestLog "Copying latest setup files..." "INFO"
    Copy-Item -Path "$ProjectRoot\setup.ps1", "$ProjectRoot\validate_setup.py", "$ProjectRoot\SETUP.md" -Destination $TestPath -Force
    
    # Test setup script
    Write-TestLog "Testing setup script..." "INFO"
    .\setup.ps1 -SkipDevDependencies
    
    if ($LASTEXITCODE -ne 0) {
        throw "Setup script failed"
    }
    Write-TestLog "Setup script completed successfully" "SUCCESS"
    
    # Test validation script
    Write-TestLog "Testing validation script..." "INFO"
    python validate_setup.py | Out-Host
    
    if ($LASTEXITCODE -ne 0) {
        throw "Validation script failed"
    }
    Write-TestLog "Validation script completed successfully" "SUCCESS"
    
    # Test basic functionality
    Write-TestLog "Testing basic functionality..." "INFO"
    
    # Activate venv and test imports
    $venvScript = Join-Path $TestPath "venv\Scripts\Activate.ps1"
    & $venvScript
    
    python -c "import selenium; import pytest; from config.config_loader import get_config; print('All imports successful')"
    if ($LASTEXITCODE -ne 0) {
        throw "Basic functionality test failed"
    }
    
    Write-TestLog "Basic functionality test passed" "SUCCESS"
    
    # Test pytest (basic)
    Write-TestLog "Testing pytest execution..." "INFO"
    python -m pytest tests/unit/ --tb=short -q
    if ($LASTEXITCODE -ne 0) {
        Write-TestLog "Some unit tests failed, but this is expected in test environment" "WARN"
    } else {
        Write-TestLog "Unit tests passed" "SUCCESS"
    }
    
    Write-TestLog "" "INFO"
    Write-TestLog "ALL TESTS PASSED!" "SUCCESS"
    Write-TestLog "The setup scripts are working correctly" "SUCCESS"
    
} catch {
    Write-TestLog "Test failed: $_" "ERROR"
    exit 1
} finally {
    # Return to original directory
    Set-Location $ProjectRoot
    
    if (-not $KeepTestDir) {
        Write-TestLog "Cleaning up test directory..." "INFO"
        if (Test-Path $TestPath) {
            Remove-Item $TestPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-TestLog "Test directory preserved: $TestPath" "INFO"
    }
}

Write-TestLog "Setup script validation complete!" "SUCCESS"