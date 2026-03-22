$cachePath = "$env:RUNNER_TEMP\octave-installer"
New-Item -Path $cachePath -ItemType Directory -Force
$version = winget show --id GNU.Octave -e |
  Where-Object { $_ -match "^Version:" } |
  Select-Object -First 1 |
  ForEach-Object { ($_ -replace "^Version:\s*", "").Trim() }
"OCTAVE_CACHE_PATH=$cachePath" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
"OCTAVE_VERSION=$version" | Out-File -FilePath $env:GITHUB_ENV -Encoding Utf8 -Append
