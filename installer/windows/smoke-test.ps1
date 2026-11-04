#requires -version 5.1
$ErrorActionPreference = 'Stop'
$temp = $null
try {
    if ($env:OS -ne 'Windows_NT') { throw 'Execute no Windows 10/11.' }
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
    foreach ($name in @('opengl32.dll','clearview-smoke.exe')) {
        $source = Join-Path (Join-Path $PSScriptRoot 'bin') $name
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $manifest.files.$name) { throw "Verificacao do pacote falhou: $name" }
    }
    $temp = Join-Path ([IO.Path]::GetTempPath()) ('ClearView teste ' + [Guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'bin\opengl32.dll') -Destination $temp
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'bin\clearview-smoke.exe') -Destination $temp
    $out = Join-Path $PSScriptRoot ('smoke-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    [IO.Directory]::CreateDirectory($out) | Out-Null
    $exe = Join-Path $temp 'clearview-smoke.exe'
    $dll = Join-Path $temp 'opengl32.dll'
    $stdout = Join-Path $out 'result.txt'
    $stderr = Join-Path $out 'error.txt'
    $process = Start-Process -FilePath $exe -ArgumentList ('"'+$dll+'"') -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    try {
        if (-not $process.WaitForExit(60000)) {
            $process.Kill(); $process.WaitForExit()
            throw 'O teste grafico nao respondeu em 60 segundos. Nenhum arquivo do jogo foi alterado. Atualize o driver ou envie o relatorio ao suporte.'
        }
        $process.WaitForExit()
        $code = $process.ExitCode
        if (Test-Path -LiteralPath $stdout) { Get-Content -LiteralPath $stdout | Write-Output }
        if (Test-Path -LiteralPath $stderr) { Get-Content -LiteralPath $stderr | Write-Output }
    } finally { $process.Dispose() }
    $log = Join-Path $temp '.clearview\hook.log'
    if (Test-Path -LiteralPath $log) { Copy-Item -LiteralPath $log -Destination $out }
    Write-Host "Resultado salvo em: $out"
    if ($code -ne 0) { throw "Smoke test falhou (codigo $code). Envie o resultado antes de instalar no jogo." }
    Write-Host 'Teste isolado aprovado. Ainda falta validar o Hytale real. Nenhum arquivo do jogo foi alterado.'
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
finally { if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force } }
