#requires -version 5.1
[CmdletBinding()]
param(
    [string]$ClientDir,
    [ValidateSet('distance','atmosphere','all','off')][string]$Mode,
    [switch]$Uninstall,
    [switch]$ValidateOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-GameStopped {
    if (Get-Process -Name HytaleClient -ErrorAction SilentlyContinue) {
        throw 'Feche o Hytale completamente antes de continuar. O launcher pode ficar aberto.'
    }
}
function Assert-PE64([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 64 -or $bytes[0] -ne 77 -or $bytes[1] -ne 90) { throw "Arquivo PE invalido: $Path" }
    $pe = [BitConverter]::ToInt32($bytes, 60)
    if ($pe -lt 64 -or $pe -gt ($bytes.Length - 26)) { throw "Cabecalho PE invalido: $Path" }
    if ([BitConverter]::ToUInt32($bytes,$pe) -ne 17744 -or [BitConverter]::ToUInt16($bytes,$pe+4) -ne 34404 -or [BitConverter]::ToUInt16($bytes,$pe+24) -ne 523) {
        throw 'O ClearView requer Hytale e DLL Windows x64 (64 bits).'
    }
}
function Test-Owned([string]$Path) {
    if (-not [IO.File]::Exists($Path)) { return $false }
    return [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($Path)).Contains('HYTALE_CLEARVIEW_WINDOWS_PROXY_V1')
}
function Assert-Regular([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        $item = Get-Item -LiteralPath $Path -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Link/junction nao suportado neste caminho: $Path" }
    }
}
function Write-Atomic([string]$Path,[byte[]]$Bytes) {
    $temp = $Path + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $backup = $temp + '.previous'
    try {
        [IO.File]::WriteAllBytes($temp,$Bytes)
        if ([IO.File]::Exists($Path)) { [IO.File]::Replace($temp,$Path,$backup) }
        else { [IO.File]::Move($temp,$Path) }
    } finally {
        if ([IO.File]::Exists($temp)) { [IO.File]::Delete($temp) }
        if ([IO.File]::Exists($backup)) { [IO.File]::Delete($backup) }
    }
}

try {
    if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem) { throw 'Este instalador requer Windows 10/11 de 64 bits.' }
    $os = Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    if ([int]$os.CurrentBuildNumber -lt 17763) { throw 'O Hytale requer Windows 10 versao 1809 (build 17763) ou superior, ou Windows 11.' }
    Assert-GameStopped
    if (-not $ClientDir) {
        $candidates = @(
            (Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'Hytale\install\release\package\game\latest\Client'),
            (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Hytale\install\release\package\game\latest\Client')
        ) | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'HytaleClient.exe') } | Select-Object -Unique
        if (@($candidates).Count -eq 1) { $ClientDir = @($candidates)[0] }
        else {
            Add-Type -AssemblyName System.Windows.Forms
            $picker = New-Object System.Windows.Forms.OpenFileDialog
            $picker.Title = 'Selecione HytaleClient.exe na pasta Client do jogo'
            $picker.Filter = 'Cliente Hytale|HytaleClient.exe'
            try {
                if ($picker.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) { throw 'Selecao cancelada; nenhum arquivo do jogo foi alterado.' }
                $ClientDir = [IO.Path]::GetDirectoryName($picker.FileName)
            } finally { $picker.Dispose() }
        }
    }
    $ClientDir = [IO.Path]::GetFullPath($ClientDir)
    $exe = Join-Path $ClientDir 'HytaleClient.exe'
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "HytaleClient.exe nao encontrado em: $ClientDir" }
    Assert-PE64 $exe
    $live = Join-Path $ClientDir 'opengl32.dll'
    $state = Join-Path $ClientDir '.clearview'
    $receipt = Join-Path $state 'windows-receipt.json'
    $settings = Join-Path $state 'settings'
    foreach ($path in @($ClientDir,$live,$state,$receipt,$settings)) { Assert-Regular $path }

    if ($Uninstall) {
        if (-not (Test-Path -LiteralPath $live)) { Write-Host 'ClearView nao esta instalado neste cliente.'; exit 0 }
        if (-not (Test-Owned $live)) { throw 'A opengl32.dll existente nao pertence ao ClearView. Nenhum arquivo foi removido.' }
        if (-not (Test-Path -LiteralPath $receipt)) { throw 'Recibo ausente. Remocao automatica interrompida para revisao.' }
        $installed = Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
        if ($installed.product -ne 'Hytale ClearView' -or (Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash -ne $installed.sha256) {
            throw 'A DLL mudou desde a instalacao. Remocao automatica interrompida para revisao.'
        }
        if ($ValidateOnly) { Write-Host "Remocao validada: $live"; exit 0 }
        Assert-GameStopped
        $removed = Join-Path $state ('removed-' + [Guid]::NewGuid().ToString('N') + '.dll')
        [IO.File]::Move($live,$removed)
        Remove-Item -LiteralPath $receipt
        Write-Host 'ClearView removido. Abra o Hytale normalmente.'
        Write-Host "Configuracoes, log e copia de recuperacao preservados em: $state"
        exit 0
    }

    $source = Join-Path $PSScriptRoot 'bin\opengl32.dll'
    $manifestPath = Join-Path $PSScriptRoot 'manifest.json'
    if (-not (Test-Path -LiteralPath $source) -or -not (Test-Path -LiteralPath $manifestPath)) {
        throw 'Pacote incompleto. Extraia o ZIP completo antes de executar Install.bat.'
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.product -ne 'Hytale ClearView' -or $manifest.architecture -ne 'x64') { throw 'Manifesto de pacote invalido.' }
    Assert-PE64 $source
    $expected = [string]$manifest.files.'opengl32.dll'
    if ($expected -notmatch '^[0-9a-fA-F]{64}$' -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $expected -or -not (Test-Owned $source)) {
        throw 'A verificacao SHA-256 do pacote falhou. Extraia novamente o pacote original.'
    }
    if (Test-Path -LiteralPath $live) {
        if (-not (Test-Owned $live)) { throw 'Outra opengl32.dll ja existe (possivelmente Aurora/ReShade). Remova o outro mod antes de instalar ClearView.' }
        if (-not (Test-Path -LiteralPath $receipt)) { throw 'ClearView sem recibo: revise a instalacao anterior antes de atualizar.' }
        $installed = Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
        if ($installed.product -ne 'Hytale ClearView' -or (Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash -ne $installed.sha256) {
            throw 'A DLL instalada foi alterada. Atualizacao interrompida para revisao.'
        }
    }
    if ($ValidateOnly) { Write-Host "Pacote e destino validados: $ClientDir"; exit 0 }
    Assert-GameStopped
    [IO.Directory]::CreateDirectory($state) | Out-Null
    $oldDll = if ([IO.File]::Exists($live)) { [IO.File]::ReadAllBytes($live) } else { $null }
    $oldReceipt = if ([IO.File]::Exists($receipt)) { [IO.File]::ReadAllBytes($receipt) } else { $null }
    $oldSettings = if ([IO.File]::Exists($settings)) { [IO.File]::ReadAllBytes($settings) } else { $null }
    $dllWritten = $false
    try {
        if ($null -ne $oldDll) {
            $recovery = Join-Path $state ('backup-' + [Guid]::NewGuid().ToString('N') + '.dll')
            [IO.File]::WriteAllBytes($recovery,$oldDll)
        }
        if ($Mode -or $null -eq $oldSettings) {
            if (-not $Mode) { $Mode = 'distance' }
            $values = @{distance='0 1 1';atmosphere='0 0 1';all='0 0 0';off='1 1 1'}
            Write-Atomic $settings ([Text.Encoding]::ASCII.GetBytes($values[$Mode] + "`n"))
        }
        Write-Atomic $live ([IO.File]::ReadAllBytes($source)); $dllWritten = $true
        if ((Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash -ne $expected) { throw 'Verificacao da DLL instalada falhou.' }
        $data = @{product='Hytale ClearView';version=$manifest.version;sha256=$expected;installed_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json
        Write-Atomic $receipt ([Text.Encoding]::UTF8.GetBytes($data))
    } catch {
        $failure = $_
        if ($dllWritten) {
            if ($null -ne $oldDll) { Write-Atomic $live $oldDll } elseif ([IO.File]::Exists($live)) { [IO.File]::Delete($live) }
        }
        if ($null -ne $oldReceipt) { Write-Atomic $receipt $oldReceipt } elseif ([IO.File]::Exists($receipt)) { [IO.File]::Delete($receipt) }
        if ($null -ne $oldSettings) { Write-Atomic $settings $oldSettings } elseif ([IO.File]::Exists($settings)) { [IO.File]::Delete($settings) }
        throw $failure
    }
    Write-Host "ClearView $($manifest.version) instalado em: $ClientDir"
    Write-Host 'Abra pelo launcher normal. F9 abre o painel; setas ajustam; V visao limpa; R original.'
    Write-Host 'Esta e uma previa para validacao no Windows 10, ainda nao uma versao estavel.'
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
