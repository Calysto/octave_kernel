$installer = Get-ChildItem $env:OCTAVE_CACHE_PATH -Filter "*.exe" | Select-Object -First 1
Start-Process -FilePath $installer.FullName -ArgumentList "/S" -Wait -NoNewWindow

$searchPaths = @(
  "$env:LOCALAPPDATA\Programs",
  "$env:ProgramFiles\GNU Octave",
  "$env:ProgramFiles\Octave",
  "C:\Octave"
)
$octaveExe = $null
foreach ($path in $searchPaths) {
  $octaveExe = Get-ChildItem $path -Recurse -Filter "octave.exe" -ErrorAction SilentlyContinue |
    Select-Object -First 1
  if ($octaveExe) { break }
}
if (-not $octaveExe) {
  throw "Could not find octave.exe after installation"
}
$octaveBin = $octaveExe.DirectoryName
echo "Octave bin: $octaveBin"
echo "$octaveBin" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
($octaveBin -replace '\\', '/' -replace '^C:', '/c') >> $env:GITHUB_PATH
