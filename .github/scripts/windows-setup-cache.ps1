$cachePath = "$env:RUNNER_TEMP\octave-installer"
New-Item -Path $cachePath -ItemType Directory -Force
echo "Cache path: $cachePath"
$version = winget show --id GNU.Octave -e --accept-source-agreements 2>$null |
  Where-Object { $_ -match "^Version:" } |
  Select-Object -First 1 |
  ForEach-Object { ($_ -replace "^Version:\s*", "").Trim() }
if (-not $version) {
  throw "Failed to determine Octave version from winget"
}
echo "Octave version: $version"
"OCTAVE_CACHE_PATH=$cachePath" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
"OCTAVE_VERSION=$version" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
