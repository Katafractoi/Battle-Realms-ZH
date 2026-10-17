$ErrorActionPreference = 'Stop'
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$output = Join-Path $PSScriptRoot 'BRZH-installer.exe'
& $compiler /nologo /codepage:65001 /target:exe /platform:anycpu /reference:System.Web.Extensions.dll ('/out:' + $output) (Join-Path $PSScriptRoot 'BRZH-installer.cs')
if ($LASTEXITCODE -ne 0) { throw 'installer build failed' }
