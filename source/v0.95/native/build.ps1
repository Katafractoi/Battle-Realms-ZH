$ErrorActionPreference = 'Stop'
# Run from an x64 Native Tools Command Prompt for Visual Studio.
Push-Location $PSScriptRoot
try {
    & cl.exe /nologo /LD /O2 /MT blast.c blast_buffer_wrapper.c /Fe:blast_buffer_wrapper.dll
    if ($LASTEXITCODE -ne 0) { throw 'blast decoder build failed' }
} finally { Pop-Location }
