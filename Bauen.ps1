$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$destination = Join-Path $PSScriptRoot 'dist\Bewerbungskatapult.xpi'
$temporary = Join-Path $PSScriptRoot ('dist\build-' + [Guid]::NewGuid().ToString('N') + '.zip')
[IO.Compression.ZipFile]::CreateFromDirectory((Join-Path $PSScriptRoot 'addon'), $temporary)
Move-Item -LiteralPath $temporary -Destination $destination -Force
Write-Host $destination
