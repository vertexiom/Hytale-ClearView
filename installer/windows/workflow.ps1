# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
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
    $stage=0
    foreach($command in $commands) {
        $stage++
        $body+='Set-Content -LiteralPath '+(Quote-PS ($Log+'.stage'))+' -Value '+$stage+"`r`n"
        $body+='try { $LASTEXITCODE = $null; $ErrorActionPreference = ''Continue'''+"`r`n"
        $body+=$command+' >> '+(Quote-PS $Log)+' 2>&1'+"`r`n"
        $body+='$stageExit = $LASTEXITCODE } finally { $ErrorActionPreference = ''Stop'' }'+"`r`n"
        $body+='if ($null -eq $stageExit) { $stageExit = 1 }'+"`r`n"
        $body+='Add-Content -LiteralPath '+(Quote-PS $Log)+' -Value (''Etapa '+$stage+' - codigo de saida: '' + $stageExit)'+"`r`n"
        $body+='if ($stageExit -ne 0) { exit $stageExit }'+"`r`n"
    }
    $body+='Set-Content -LiteralPath '+(Quote-PS ($Log+'.stage'))+' -Value complete'+"`r`n"
    return $body+'exit 0'
}

function Get-ClearViewFailureReason([string]$Report,[string]$Stage) {
    if ($Report -match 'Feche o Hytale') { return 'Feche o Hytale e tente novamente.' }
    if ($Report -match 'Outra opengl32|Aurora/ReShade') { return 'Remova o outro mod de shaders antes de instalar o ClearView.' }
    if ($Report -match 'nao respondeu') { return 'O teste gráfico não respondeu. A instalação foi interrompida antes de alterar o jogo. Envie o relatório ao suporte.' }
    if ($Report -match '(?m)^(FAIL:|Smoke test falhou)' -and $Report -notmatch 'PASS: WGL forwarding') {
        return 'O teste gráfico não passou. Envie o relatório para identificar a falha antes de instalar.'
    }
    if ($Stage -eq '2' -and $Report -match 'PASS: WGL forwarding') {
        return 'O teste gráfico passou, mas o instalador não conseguiu concluir essa etapa. Envie o relatório ao suporte.'
    }
    if ($Report -match '1809|64 bits|64 bit') { return 'Este instalador requer Windows 10 1809 ou superior, de 64 bits.' }
    if ($Stage -eq '3') { return 'A verificação gráfica passou, mas não foi possível instalar os arquivos. Consulte o relatório.' }
    return 'Não foi possível concluir. Clique em Ver relatório para obter ajuda.'
}
