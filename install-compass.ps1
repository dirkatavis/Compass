# Compass Automation Installer (single entrypoint)
#
# Because -InstallPath and -Branch are mandatory, prefer the scriptblock form
# (Invoke-Expression cannot accept parameters):
#
#   $url = "https://raw.githubusercontent.com/dirkatavis/Compass/feature/DriverAutoUpdate/install-compass.ps1"
#   & ([scriptblock]::Create((iwr -useb $url).Content)) -InstallPath "C:\Dev\Compass" -Branch "feature/DriverAutoUpdate"

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstallPath,
    [string]$RepoOwner = 'dirkatavis',
    [string]$RepoName = 'Compass',
    [Parameter(Mandatory)]
    [string]$Branch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Install {
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

function Ensure-Directory {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Download-ZipRepo {
    param(
        [Parameter(Mandatory)][string]$Owner,
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string]$BranchName,
        [Parameter(Mandatory)][string]$Destination
    )

    $zipUrl = "https://github.com/$Owner/$Repo/archive/refs/heads/$BranchName.zip"
    $tmp = Join-Path $env:TEMP ("$Repo-$BranchName-" + [Guid]::NewGuid().ToString('N'))
    Ensure-Directory $tmp

    $zipPath = Join-Path $tmp 'repo.zip'
    Write-Install "Downloading $zipUrl"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

    $extractPath = Join-Path $tmp 'extract'
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

    # GitHub zips extract into <repo>-<branch> folder
    $inner = Get-ChildItem -Path $extractPath | Where-Object { $_.PSIsContainer } | Select-Object -First 1
    if (-not $inner) { throw 'Failed to locate extracted repo folder' }

    Ensure-Directory $Destination
    Copy-Item -Path (Join-Path $inner.FullName '*') -Destination $Destination -Recurse -Force

    Remove-Item -Recurse -Force $tmp
}

Write-Install "Installing Compass to: $InstallPath"

if (Test-Path $InstallPath -PathType Container) {
    $existing = Get-ChildItem -LiteralPath $InstallPath -Force -ErrorAction SilentlyContinue
    if ($existing -and $existing.Count -gt 0) {
        throw "InstallPath already exists and is not empty: $InstallPath"
    }
} else {
    Ensure-Directory $InstallPath
}

$repoUrl = "https://github.com/$RepoOwner/$RepoName.git"

if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Install "Cloning $repoUrl (branch: $Branch)"
    git clone --depth 1 --branch $Branch $repoUrl $InstallPath
} else {
    Write-Install 'git not found; falling back to downloading ZIP from GitHub' 'WARN'
    Download-ZipRepo -Owner $RepoOwner -Repo $RepoName -BranchName $Branch -Destination $InstallPath
}

$setupScript = Join-Path $InstallPath 'setup.ps1'
if (-not (Test-Path $setupScript)) {
    throw "setup.ps1 not found in $InstallPath (branch '$Branch' may not include setup scripts)"
}

Write-Install 'Running setup.ps1...'
Push-Location $InstallPath
try {
    & $setupScript
} finally {
    Pop-Location
}

Write-Install 'Install complete' 'SUCCESS'
