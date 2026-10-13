param([string]$LibreOffice = 'C:\Program Files\LibreOffice\program')
$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$pythonPath = Join-Path $LibreOffice 'python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'LibreOffice mit enthaltenem Python wurde nicht gefunden.' }
$nativeDir = Join-Path $projectDir 'native'
$launcherPath = Join-Path $nativeDir 'host.cmd'
$hostPath = Join-Path $nativeDir 'host.py'
$launcher = '@echo off' + "`r`n" + '"' + $pythonPath + '" "' + $hostPath + '"' + "`r`n"
[IO.File]::WriteAllText($launcherPath, $launcher, [Text.Encoding]::Default)
$manifestPath = Join-Path $nativeDir 'de.bewerbungskatapult.json'
$manifest = @{name='de.bewerbungskatapult';description='Lokale PDF-Erstellung mit LibreOffice';path=$launcherPath;type='stdio';allowed_extensions=@('bewerbungskatapult@application-catapult.local')}
[IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
$regPath = 'HKCU:\Software\Mozilla\NativeMessagingHosts\de.bewerbungskatapult'
New-Item -Path $regPath -Force | Out-Null
Set-Item -Path $regPath -Value $manifestPath
Write-Host 'Lokales Hilfsprogramm eingerichtet. In Thunderbird dist\Bewerbungskatapult.xpi als Add-on aus Datei installieren.'
