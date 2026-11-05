# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Inspect PE imports/exports and exercise installer I/O with mocked Windows detection.
Does not claim native Windows validation. Requires portable pwsh for installer tests.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pwsh',required=True);args=parser.parse_args()
    binary=ROOT/'build/windows/opengl32.dll'
    info=subprocess.check_output(['objdump','-p',str(binary)],text=True)
    assert 'pei-x86-64' in info and 'PE32+' in info
    imports=re.findall(r'DLL Name: (\S+)',info)
    assert all(n.lower() in {'user32.dll','gdi32.dll','kernel32.dll'} or n.lower().startswith('api-ms-win-crt-') for n in imports),imports
    export_section=info.split('[Ordinal/Name Pointer] Table',1)[1].split('The Function Table',1)[0]
    actual={line.split()[-1] for line in export_section.splitlines() if re.match(r'\s*\[\s*\d+\]',line)}
    expected={line for line in (ROOT/'src/windows/exports.txt').read_text().splitlines() if line and not line.startswith('#')}
    assert expected<=actual,expected-actual
    print('PASS: PE x64;',len(expected),'OpenGL exports; system-only DLL dependencies')
    with tempfile.TemporaryDirectory(prefix='clearview-installer-') as td:
        temp=Path(td);package=temp/'package';package.mkdir();(package/'bin').mkdir()
        for name in ['install.ps1','smoke-test.ps1']:shutil.copy2(ROOT/'installer/windows'/name,package/name)
        shutil.copy2(ROOT/'tools/support/diagnostics.ps1',package/'diagnostics.ps1')
        shutil.copy2(ROOT/'installer/windows/setup.ps1',package/'setup.ps1')
        shutil.copy2(ROOT/'installer/windows/workflow.ps1',package/'workflow.ps1')
        for name in ['opengl32.dll','clearview-smoke.exe']:shutil.copy2(ROOT/'build/windows'/name,package/'bin'/name)
        shutil.copy2(ROOT/'build/windows/manifest.json',package/'manifest.json')
        # Parse every PowerShell file using the official parser before executing I/O tests.
        check=temp/'parse.ps1';check.write_text('''param([string]$Root)
$bad=$false
Get-ChildItem -LiteralPath $Root -Filter *.ps1 | ForEach-Object {
 $tokens=$null;$errors=$null
 [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors) | Out-Null
 if($errors.Count){$errors | Format-List | Out-String | Write-Host;$bad=$true}
}
if($bad){exit 1}
''')
        subprocess.run([args.pwsh,'-NoLogo','-NoProfile','-File',str(check),str(package)],check=True)
        wrapper=temp/'run.ps1';wrapper.write_text('''param([string]$Script,[string]$Client,[string]$Operation,[string]$Preset,[string]$Running)
$env:OS='Windows_NT'
function Get-ItemProperty {param([string]$LiteralPath) [pscustomobject]@{CurrentBuildNumber=$(if($Running -eq 'old-os'){'10240'}else{'19045'})}}
function Get-Process {param([string]$Name,[string]$ErrorAction) if($Running -eq 'yes'){[pscustomobject]@{Id=123}}}
$options=@{ClientDir=$Client}
if($Operation -eq 'remove'){$options.Uninstall=$true}
if($Operation -eq 'validate'){$options.ValidateOnly=$true}
if($Preset){$options.Mode=$Preset}
& $Script @options
exit $LASTEXITCODE
''')
        client=temp/'Client espaço';client.mkdir();shutil.copy2(package/'bin/clearview-smoke.exe',client/'HytaleClient.exe')
        original_exe=(client/'HytaleClient.exe').read_bytes()
        def run(operation='',preset='',running='',ok=True):
            result=subprocess.run([args.pwsh,'-NoLogo','-NoProfile','-File',str(wrapper),str(package/'install.ps1'),str(client),operation,preset,running],capture_output=True,text=True)
            if ok and result.returncode:raise AssertionError(result.stdout+result.stderr)
            if not ok and not result.returncode:raise AssertionError('Expected refusal: '+result.stdout)
        run('validate');assert not (client/'.clearview').exists()
        (client/'HytaleClient.exe').rename(client/'client-backup.exe')
        try:
            run(ok=False)
            assert not (client/'opengl32.dll').exists() and not (client/'.clearview').exists()
        finally:
            (client/'client-backup.exe').rename(client/'HytaleClient.exe')
        run(running='old-os',ok=False);assert not (client/'opengl32.dll').exists()
        run(running='yes',ok=False);assert not (client/'opengl32.dll').exists()
        # Unknown mod must never be overwritten.
        (client/'opengl32.dll').write_bytes(b'foreign mod');run(ok=False)
        assert (client/'opengl32.dll').read_bytes()==b'foreign mod'
        (client/'opengl32.dll').unlink()
        run();assert (client/'opengl32.dll').read_bytes()==binary.read_bytes()
        settings=client/'.clearview/settings';settings.write_text('0.25 0.5 0.75\n')
        run();assert settings.read_text()=='0.25 0.5 0.75\n'
        run(preset='off');assert settings.read_text().strip()=='1 1 1'
        installed=(client/'opengl32.dll').read_bytes()
        # Damaged package must leave current installation untouched.
        (package/'bin/opengl32.dll').write_bytes(b'corrupt package');run(ok=False)
        assert (client/'opengl32.dll').read_bytes()==installed
        shutil.copy2(binary,package/'bin/opengl32.dll')
        # Altered installed DLL must not be silently deleted.
        (client/'opengl32.dll').write_bytes(installed+b'altered');run('remove',ok=False)
        assert (client/'opengl32.dll').exists()
        (client/'opengl32.dll').write_bytes(installed)
        run('remove');assert not (client/'opengl32.dll').exists() and settings.exists()
        # Simulate a receipt write failure. Newly installed DLL/settings must roll back.
        settings.unlink();(client/'.clearview/windows-receipt.json').mkdir()
        run(ok=False);assert not (client/'opengl32.dll').exists() and not settings.exists()
        assert (client/'HytaleClient.exe').read_bytes()==original_exe
        print('PASS: PowerShell syntax; mocked installer install/update/remove, spaces/Unicode, running-game refusal, conflict protection, checksum failures, rollback and settings preservation')
if __name__=='__main__':main()
