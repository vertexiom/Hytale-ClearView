function Quote-PS([string]$Value) { return "'" + $Value.Replace("'", "''") + "'" }
function New-ClearViewOperation([string]$Engine,[string]$Payload,[string]$Client,[string]$Log,[string]$Operation) {
    $invoke='& '+(Quote-PS $Engine)+' -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File '
    $backend=$invoke+(Quote-PS (Join-Path $Payload 'install.ps1'))+' -ClientDir '+(Quote-PS $Client)
    $commands=@()
    if($Operation -eq 'install') {
        $commands+=$backend+' -ValidateOnly'
        $commands+=$invoke+(Quote-PS (Join-Path $Payload 'smoke-test.ps1'))
        $commands+=$backend
    } elseif($Operation -eq 'remove') { $commands+=$backend+' -Uninstall' }
    else { throw 'Operacao invalida.' }
    $body='$ErrorActionPreference = ''Stop'''+"`r`n"
    foreach($command in $commands) {
        $body+=$command+' >> '+(Quote-PS $Log)+' 2>&1'+"`r`n"+'if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }'+"`r`n"
    }
    return $body+'exit 0'
}
