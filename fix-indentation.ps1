# fix-indentation.ps1
param([switch]$WhatIf)

Set-Location C:\temp\Python
$exclude = '\\(__pycache__|\.venv|\.pytest_cache|\.vscode)\\'

# UTF-8 without BOM for writes
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

Get-ChildItem -Recurse -Filter *.py -File |
Where-Object { $_.FullName -notmatch $exclude } |
ForEach-Object {
	try {
		# Robust read (handles most encodings; avoids Get-Content -Raw quirks)
		$text = [System.IO.File]::ReadAllText($_.FullName)
		if ([string]::IsNullOrEmpty($text)) {
			Write-Warning "Skipped (empty or unreadable): $($_.FullName)"
			return
		}

		# Replace LEADING tabs with 4 spaces per tab (safe for tabs inside strings)
		$fixed = [regex]::Replace(
			$text,
			'(?m)^(?>\t+)',
			{ param($m) (' ' * (4 * $m.Value.Length)) }
		)

		if ($fixed -ne $text) {
			if ($WhatIf) {
				Write-Host "[DRY-RUN] Would fix:" $_.FullName
			} else {
				[System.IO.File]::WriteAllText($_.FullName, $fixed, $Utf8NoBom)
				Write-Host "Fixed indentation in:" $_.FullName
			}
		} else {
			# No leading tabs found
			# Write-Host "No change:" $_.FullName
		}
	}
	catch {
		Write-Warning "Skipped (error): $($_.FullName) → $($_.Exception.Message)"
	}
}
