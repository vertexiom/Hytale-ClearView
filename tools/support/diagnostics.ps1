# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
#requires -version 5.1
[CmdletBinding()]
param([string]$ClientDir)
$ErrorActionPreference = 'Stop'
try {
    if ($env:OS -ne 'Windows_NT') { throw 'Execute no Windows.' }
    if (-not $ClientDir) { $ClientDir = Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'Hytale\install\release\package\game\latest\Client' }
    $out = Join-Path $PSScriptRoot ('diagnostics-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    [IO.Directory]::CreateDirectory($out) | Out-Null
    $os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture
    $gpus = Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,DriverDate,AdapterRAM
    $cpu = Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
    $computer = Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
    $drives = Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,FileSystem,Size,FreeSpace
    @{os=$os;gpu=@($gpus);cpu=@($cpu);ram_bytes=$computer.TotalPhysicalMemory;disks=@($drives);vram_note='WMI AdapterRAM is approximate, can overflow on some GPUs, and is not used as an eligibility check';powershell=$PSVersionTable.PSVersion.ToString();client_found=(Test-Path -LiteralPath (Join-Path $ClientDir 'HytaleClient.exe'))} |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $out 'system.json') -Encoding UTF8
    foreach ($name in @('hook.log','settings','windows-receipt.json')) {
        $path = Join-Path (Join-Path $ClientDir '.clearview') $name
        if (Test-Path -LiteralPath $path -PathType Leaf) { Copy-Item -LiteralPath $path -Destination (Join-Path $out $name) }
    }
    $dll = Join-Path $ClientDir 'opengl32.dll'
    if (Test-Path -LiteralPath $dll) { (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash | Set-Content -LiteralPath (Join-Path $out 'installed-sha256.txt') }
    Write-Host "Diagnostico local salvo em: $out"
    Write-Host 'Nenhum arquivo foi enviado. Compartilhe essa pasta com o desenvolvedor para investigar.'
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
