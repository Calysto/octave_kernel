$installer = Get-ChildItem $env:OCTAVE_CACHE_PATH -Filter "*.exe" | Select-Object -First 1
Start-Process -FilePath $installer.FullName -ArgumentList "/S" -Wait -NoNewWindow
$octaveRoot = Get-ChildItem "$env:LOCALAPPDATA\Programs\GNU Octave" -Directory |
  Select-Object -First 1 -ExpandProperty FullName
$octaveBin = "$octaveRoot\mingw64\bin"
echo "Octave bin: $octaveBin"
echo "$octaveBin" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
($octaveBin -replace '\\', '/' -replace '^C:', '/c') >> $env:GITHUB_PATH
