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
    $start = New-Object Diagnostics.ProcessStartInfo
    $start.FileName = $exe
    $start.Arguments = '"'+$dll+'"'
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $start
    try {
        if (-not $process.Start()) { throw 'Nao foi possivel iniciar o teste grafico.' }
        $outputTask = $process.StandardOutput.ReadToEndAsync()
        $errorTask = $process.StandardError.ReadToEndAsync()
        $timedOut = -not $process.WaitForExit(60000)
        if ($timedOut) { $process.Kill() }
        $process.WaitForExit()
        $code = $process.ExitCode
        $outputText = $outputTask.GetAwaiter().GetResult()
        $errorText = $errorTask.GetAwaiter().GetResult()
        [IO.File]::WriteAllText($stdout,$outputText)
        [IO.File]::WriteAllText($stderr,$errorText)
        Write-Output $outputText
        if ($errorText) { Write-Output $errorText }
        if ($timedOut) { throw 'O teste grafico nao respondeu em 60 segundos. Nenhum arquivo do jogo foi alterado.' }
        if ($null -eq $code) { throw 'Nao foi possivel obter o resultado do processo de teste. A instalacao nao foi iniciada.' }
        Write-Host "Processo de teste encerrado com codigo: $code"
    } finally { $process.Dispose() }
    $log = Join-Path $temp '.clearview\hook.log'
    if (Test-Path -LiteralPath $log) { Copy-Item -LiteralPath $log -Destination $out }
    Write-Host "Resultado salvo em: $out"
    if ($code -ne 0) { throw "Smoke test falhou (codigo $code). Envie o resultado antes de instalar no jogo." }
    Write-Host 'Teste isolado aprovado. Ainda falta validar o Hytale real. Nenhum arquivo do jogo foi alterado.'
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
finally { if ($temp -and (Test-Path -LiteralPath $temp)) { Remove-Item -LiteralPath $temp -Recurse -Force } }
