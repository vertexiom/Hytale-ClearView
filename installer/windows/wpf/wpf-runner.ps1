# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
#requires -version 5.1
param(
    [Parameter(Mandatory=$true)][string]$Engine,
    [Parameter(Mandatory=$true)][string]$Payload,
    [Parameter(Mandatory=$true)][string]$Client,
    [Parameter(Mandatory=$true)][string]$Log,
    [Parameter(Mandatory=$true)][ValidateSet('install','remove')][string]$Operation
)
$ErrorActionPreference = 'Stop'
try {
    . (Join-Path $Payload 'workflow.ps1')
    $body = New-ClearViewOperation -Engine $Engine -Payload $Payload -Client $Client -Log $Log -Operation $Operation
    $runner = Join-Path $Payload 'wpf-operation.ps1'
    [IO.File]::WriteAllText($runner, $body, (New-Object Text.UTF8Encoding($true)))
    $hostEngine = (Get-Process -Id $PID).Path
    & $hostEngine -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $runner
    if ($null -eq $LASTEXITCODE) { exit 1 }
    exit $LASTEXITCODE
} catch {
    Add-Content -LiteralPath $Log -Value ($_ | Out-String)
    exit 1
}
