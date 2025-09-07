# scan_project.ps1
# Generates/overwrites project_index.txt with all defs/classes.

$projectPath = "C:\temp\Python"
$outputFile  = Join-Path $projectPath "project_index.txt"

Get-ChildItem $projectPath -Recurse -Filter *.py |
  Where-Object { $_.FullName -notmatch "__pycache__|\.pytest_cache" } |
  Select-String -Pattern '^(def|class) ' |
  ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" } |
  Out-File $outputFile -Encoding utf8

Write-Host "Project index created at $outputFile (overwritten if existed)."
