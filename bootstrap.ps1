# Compass Automation Bootstrap Script
# Automates ALL preliminary requirements and setup
#
# This script will:
# - Check and install Python if needed
# - Check and install Git if needed  
# - Create recommended folder structure
# - Clone the repository
# - Run the main setup script
# - Download Edge WebDriver automatically

param(
    [string]$InstallPath = "C:\Dev\Compass",
    [switch]$UseWinget,
    [switch]$SkipSoftwareInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Enhanced logging with colors
function Write-Bootstrap {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "STEP" { "Magenta" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Python {
    param([bool]$UseUserInstall = $false)
    
    Write-Bootstrap "Installing Python..." "STEP"
    
    if ($UseWinget) {
        # Try winget first (Windows 10 1709+ / Windows 11)
        try {
            $wingetArgs = @("install", "Python.Python.3.13", "--accept-source-agreements", "--accept-package-agreements")
            if ($UseUserInstall) {
                $wingetArgs += "--scope", "user"
                Write-Bootstrap "Installing Python for current user only..." "INFO"
            }
            winget @wingetArgs
            Write-Bootstrap "Python installed via winget" "SUCCESS"
            return $true
        } catch {
            Write-Bootstrap "Winget failed, trying manual download..." "WARN"
        }
    }
    
    # Manual download and install
    $pythonUrl = "https://www.python.org/ftp/python/3.13.10/python-3.13.10-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    Write-Bootstrap "Downloading Python from python.org..." "INFO"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    if ($UseUserInstall) {
        Write-Bootstrap "Installing Python for current user (no admin required)..." "INFO"
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0", "InstallLauncherAllUsers=0" -Wait
    } else {
        Write-Bootstrap "Installing Python system-wide..." "INFO"
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
    }
    
    Remove-Item $pythonInstaller -Force -ErrorAction SilentlyContinue
    
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    return $true
}

function Install-Git {
    param([bool]$UseUserInstall = $false)
    
    Write-Bootstrap "Installing Git..." "STEP"
    
    if ($UseWinget) {
        try {
            $wingetArgs = @("install", "Git.Git", "--accept-source-agreements", "--accept-package-agreements")
            if ($UseUserInstall) {
                $wingetArgs += "--scope", "user"
                Write-Bootstrap "Installing Git for current user only..." "INFO"
            }
            winget @wingetArgs
            Write-Bootstrap "Git installed via winget" "SUCCESS"
            return $true
        } catch {
            Write-Bootstrap "Winget failed, trying manual download..." "WARN"
        }
    }
    
    # Manual download and install
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe"
    $gitInstaller = "$env:TEMP\git-installer.exe"
    
    Write-Bootstrap "Downloading Git for Windows..." "INFO"
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller
    
    if ($UseUserInstall) {
        Write-Bootstrap "Installing Git for current user (no admin required)..." "INFO"
        # Create a custom INF file for user-only installation
        $gitInf = @"
[Setup]
Lang=default
Dir=C:\Users\$env:USERNAME\AppData\Local\Programs\Git
Group=Git
NoIcons=0
SetupType=default
Components=ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh,consolefont,autoupdate
Tasks=
EditorOption=VIM
CustomEditorPath=
DefaultBranchOption=main
PathOption=Cmd
SSHOption=OpenSSH
TortoiseOption=false
CURLOption=OpenSSL
CRLFOption=CRLFAlways
BashCompletionOption=true
BashTerminalOption=ConHost
GitPullBehaviorOption=Merge
UseCredentialManager=Enabled
PerformanceTweaksFSCache=Enabled
EnableSymlinks=Disabled
EnablePseudoConsoleSupport=Disabled
"@
        $gitInf | Out-File "$env:TEMP\git-user-install.inf" -Encoding UTF8
        Start-Process -FilePath $gitInstaller -ArgumentList "/LOADINF=$env:TEMP\git-user-install.inf", "/VERYSILENT", "/NORESTART" -Wait
        Remove-Item "$env:TEMP\git-user-install.inf" -Force -ErrorAction SilentlyContinue
    } else {
        Write-Bootstrap "Installing Git system-wide..." "INFO"
        Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS" -Wait
    }
    
    Remove-Item $gitInstaller -Force -ErrorAction SilentlyContinue
    
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    return $true
}

function Get-EdgeVersion {
    try {
        $edgePath = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
        if (-not (Test-Path $edgePath)) {
            $edgePath = "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
        }
        
        if (Test-Path $edgePath) {
            $version = (Get-ItemProperty $edgePath).VersionInfo.ProductVersion
            return $version.Split('.')[0..2] -join '.'
        }
    } catch {
        Write-Bootstrap "Could not detect Edge version automatically" "WARN"
    }
    return $null
}

function Download-EdgeDriver {
    param([string]$ProjectPath)
    
    Write-Bootstrap "Downloading Edge WebDriver..." "STEP"
    
    $edgeVersion = Get-EdgeVersion
    if (-not $edgeVersion) {
        Write-Bootstrap "Could not detect Edge version. Please download msedgedriver.exe manually." "WARN"
        Write-Bootstrap "Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/" "INFO"
        return $false
    }
    
    Write-Bootstrap "Detected Edge version: $edgeVersion" "INFO"
    
    try {
        # Get latest driver version for this Edge version
        $driverUrl = "https://msedgedriver.azureedge.net/$edgeVersion/edgedriver_win64.zip"
        $driverZip = "$env:TEMP\edgedriver.zip"
        $driverExtract = "$env:TEMP\edgedriver"
        
        Invoke-WebRequest -Uri $driverUrl -OutFile $driverZip
        Expand-Archive -Path $driverZip -DestinationPath $driverExtract -Force
        
        $driverExe = Get-ChildItem -Path $driverExtract -Name "msedgedriver.exe" -Recurse
        if ($driverExe) {
            Copy-Item -Path (Join-Path $driverExtract $driverExe[0].Name) -Destination (Join-Path $ProjectPath "msedgedriver.exe") -Force
            Write-Bootstrap "Edge WebDriver downloaded and installed" "SUCCESS"
            return $true
        }
        
    } catch {
        Write-Bootstrap "Failed to download Edge WebDriver automatically: $_" "WARN"
        Write-Bootstrap "Please download manually from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/" "INFO"
        return $false
    } finally {
        Remove-Item $driverZip -Force -ErrorAction SilentlyContinue
        Remove-Item $driverExtract -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    return $false
}

# Main bootstrap process
Write-Bootstrap "Starting Compass Automation Bootstrap..." "STEP"
Write-Bootstrap "This will set up everything needed for Compass automation" "INFO"
Write-Bootstrap "Target installation path: $InstallPath" "INFO"

# Check admin rights for software installation
$hasAdminRights = Test-AdminRights

if (-not $SkipSoftwareInstall) {
    if (-not $hasAdminRights) {
        Write-Bootstrap "No administrator rights detected" "WARN"
        Write-Bootstrap "Options for software installation:" "INFO"
        Write-Bootstrap "1. Continue with user-level installation (recommended)" "INFO"
        Write-Bootstrap "2. Skip software installation and install manually" "INFO"
        Write-Bootstrap "3. Exit and run as Administrator" "INFO"
        
        $choice = Read-Host "Choose option [1/2/3]"
        switch ($choice) {
            "2" { 
                $SkipSoftwareInstall = $true
                Write-Bootstrap "Will skip automatic software installation" "INFO"
            }
            "3" {
                Write-Bootstrap "Please run PowerShell as Administrator and try again" "INFO"
                exit 0
            }
            default {
                Write-Bootstrap "Continuing with user-level installation..." "INFO"
                $useUserInstall = $true
            }
        }
    } else {
        Write-Bootstrap "Administrator rights detected" "SUCCESS"
        $useUserInstall = $false
    }
}

try {
    # Step 1: Check/Install Python
    Write-Bootstrap "=== Step 1: Python Setup ===" "STEP"
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Bootstrap "Found: $pythonVersion" "SUCCESS"
        } else {
            throw "Python not found"
        }
    } catch {
        if ($SkipSoftwareInstall) {
            Write-Bootstrap "Python not found. Please install Python 3.8+ manually" "ERROR"
            Write-Bootstrap "Download from: https://www.python.org/downloads/" "INFO"
            Write-Bootstrap "During installation, check 'Add Python to PATH'" "INFO"
            exit 1
        } else {
            Install-Python -UseUserInstall $useUserInstall
        }
    }
    
    # Step 2: Check/Install Git
    Write-Bootstrap "=== Step 2: Git Setup ===" "STEP"
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Bootstrap "Found: $gitVersion" "SUCCESS"
        } else {
            throw "Git not found"
        }
    } catch {
        if ($SkipSoftwareInstall) {
            Write-Bootstrap "Git not found. Please install Git manually" "ERROR"
            Write-Bootstrap "Download from: https://git-scm.com/download/win" "INFO"
            exit 1
        } else {
            Install-Git -UseUserInstall $useUserInstall
        }
    }
    
    # Step 3: Create folder structure and clone repository
    Write-Bootstrap "=== Step 3: Repository Setup ===" "STEP"
    
    if (Test-Path $InstallPath) {
        Write-Bootstrap "Directory already exists: $InstallPath" "WARN"
        $continue = Read-Host "Continue and overwrite? [y/N]"
        if ($continue -notmatch "^[yY]") {
            exit 1
        }
        Remove-Item $InstallPath -Recurse -Force
    }
    
    Write-Bootstrap "Creating directory: $InstallPath" "INFO"
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    
    Write-Bootstrap "Cloning Compass repository (feature branch)..." "INFO"
    Set-Location $InstallPath
    git clone -b feature/setup_script https://github.com/dirkatavis/Compass.git . | Out-Host
    
    if ($LASTEXITCODE -ne 0) {
        throw "Git clone failed"
    }
    Write-Bootstrap "Repository cloned successfully" "SUCCESS"
    
    # Step 4: Download Edge WebDriver
    Write-Bootstrap "=== Step 4: WebDriver Setup ===" "STEP"
    Download-EdgeDriver -ProjectPath $InstallPath
    
    # Step 5: Run main setup
    Write-Bootstrap "=== Step 5: Environment Setup ===" "STEP"
    Write-Bootstrap "Running main setup script..." "INFO"
    .\setup.ps1 -SkipDevDependencies
    
    if ($LASTEXITCODE -ne 0) {
        throw "Setup script failed"
    }
    
    # Step 6: Final validation
    Write-Bootstrap "=== Step 6: Validation ===" "STEP"
    Write-Bootstrap "Running environment validation..." "INFO"
    python validate_setup.py | Out-Host
    
    Write-Bootstrap "" "INFO"
    Write-Bootstrap "========================================" "SUCCESS"
    Write-Bootstrap "BOOTSTRAP COMPLETE!" "SUCCESS"
    Write-Bootstrap "========================================" "SUCCESS"
    Write-Bootstrap "" "INFO"
    Write-Bootstrap "Compass automation is ready to use!" "INFO"
    Write-Bootstrap "Project location: $InstallPath" "INFO"
    Write-Bootstrap "" "INFO"
    Write-Bootstrap "Next steps:" "INFO"
    Write-Bootstrap "1. cd '$InstallPath'" "INFO"
    Write-Bootstrap "2. .\venv\Scripts\Activate.ps1" "INFO"
    Write-Bootstrap "3. Edit config\config.json with your credentials" "INFO"
    Write-Bootstrap "4. Edit data\mva.csv with your MVA numbers" "INFO"
    Write-Bootstrap "5. python run_compass.py" "INFO"
    Write-Bootstrap "" "INFO"
    
} catch {
    Write-Bootstrap "Bootstrap failed: $_" "ERROR"
    Write-Bootstrap "Check the error above and try running individual steps manually" "ERROR"
    exit 1
}