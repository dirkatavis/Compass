# Compass Automation One-Click Installer
# Run this from anywhere to set up Compass automation completely

Write-Host "=== Compass Automation One-Click Setup ===" -ForegroundColor Green
Write-Host ""
Write-Host "This will download and run the complete bootstrap setup." -ForegroundColor Cyan
Write-Host "Everything will be installed automatically including:" -ForegroundColor Cyan
Write-Host "  - Python 3.13 (if needed)" -ForegroundColor Yellow
Write-Host "  - Git for Windows (if needed)" -ForegroundColor Yellow  
Write-Host "  - Compass repository" -ForegroundColor Yellow
Write-Host "  - Virtual environment with dependencies" -ForegroundColor Yellow
Write-Host "  - Edge WebDriver" -ForegroundColor Yellow
Write-Host ""

$installPath = Read-Host "Installation path (press Enter for C:\Dev\Compass)"
if ([string]::IsNullOrWhiteSpace($installPath)) {
    $installPath = "C:\Dev\Compass"
}

Write-Host "Installing to: $installPath" -ForegroundColor Green

try {
    Write-Host "Downloading bootstrap script..." -ForegroundColor Cyan
    $bootstrapScript = "$env:TEMP\compass-bootstrap.ps1"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dirkatavis/Compass/main/bootstrap.ps1" -OutFile $bootstrapScript
    
    Write-Host "Running bootstrap..." -ForegroundColor Cyan
    & $bootstrapScript -InstallPath $installPath -UseWinget
    
    Write-Host ""
    Write-Host "Setup complete! Compass automation is ready." -ForegroundColor Green
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Red
} finally {
    Remove-Item $bootstrapScript -Force -ErrorAction SilentlyContinue
}