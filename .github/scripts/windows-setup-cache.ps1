$cachePath = "$env:RUNNER_TEMP\octave-installer"
New-Item -Path $cachePath -ItemType Directory -Force
echo "Cache path: $cachePath"
$maxAttempts = 3
$version = $null
for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
  if ($attempt -gt 1) {
    Write-Host "Attempt $attempt/${maxAttempts}: refreshing winget sources..."
    winget source update 2>$null
    Start-Sleep -Seconds 5
  }
  $version = winget show --id GNU.Octave -e --accept-source-agreements 2>$null |
    Where-Object { $_ -match "^Version:" } |
    Select-Object -First 1 |
    ForEach-Object { ($_ -replace "^Version:\s*", "").Trim() }
  if ($version) { break }
  Write-Host "Attempt $attempt/${maxAttempts} failed to get Octave version."
}
if (-not $version) {
  throw "Failed to determine Octave version from winget after $maxAttempts attempts"
}
echo "Octave version: $version"
"OCTAVE_CACHE_PATH=$cachePath" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
"OCTAVE_VERSION=$version" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
