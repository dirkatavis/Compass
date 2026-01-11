# Convenience bootstrap for running setup in an existing repo checkout.
# Usage: .\bootstrap.ps1

[CmdletBinding()]
param(
    [switch]$RecreateVenv,
    [switch]$SkipValidate,
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$setup = Join-Path $ProjectRoot 'setup.ps1'

if (-not (Test-Path $setup)) {
    throw "setup.ps1 not found at $setup"
}

& $setup -RecreateVenv:$RecreateVenv -SkipValidate:$SkipValidate -SkipInstall:$SkipInstall
