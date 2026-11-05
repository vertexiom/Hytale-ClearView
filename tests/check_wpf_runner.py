# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Exercise the WPF bridge and existing workflow with harmless child-process fixtures."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pwsh',required=True);args=parser.parse_args()
    args.pwsh=shutil.which(args.pwsh) or args.pwsh
    with zipfile.ZipFile(ROOT/'build/windows/wpf-payload.zip') as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={'install.ps1','smoke-test.ps1','workflow.ps1','wpf-runner.ps1','manifest.json','bin/opengl32.dll','bin/clearview-smoke.exe'}
        for name in ('install.ps1','smoke-test.ps1','workflow.ps1','wpf-runner.ps1'):
            assert archive.read(name).startswith(b'\xef\xbb\xbf'),name
    with tempfile.TemporaryDirectory(prefix="ClearView WPF espaço ' ") as tmp:
        base=Path(tmp);trace=base/'calls.jsonl';client=str(base/"Hytale ' destino $literal")
        (base/'workflow.ps1').write_text((ROOT/'installer/windows/workflow.ps1').read_text(encoding='utf-8-sig'),encoding='utf-8-sig')
        fixture = r"""param([string]$ClientDir,[switch]$ValidateOnly,[switch]$Uninstall)
$ErrorActionPreference = 'Stop'
$stage = if ($PSCommandPath.EndsWith('smoke-test.ps1')) { 'smoke' } elseif ($ValidateOnly) { 'validate' } elseif ($Uninstall) { 'remove' } else { 'install' }
$record = @{stage=$stage; client=$ClientDir} | ConvertTo-Json -Compress
[IO.File]::AppendAllText($env:CV_TRACE,$record + "`n",(New-Object Text.UTF8Encoding($false)))
if ($env:CV_FAIL -eq $stage) { switch ($stage) { 'validate' {exit 7}; 'smoke' {exit 8}; 'install' {exit 9}; 'remove' {exit 10} } }
Write-Output 'fixture passed'
exit 0
"""
        for name in ('install.ps1','smoke-test.ps1'):
            (base/name).write_text(fixture,encoding='utf-8-sig')
        for operation,failure,count,code in [('install','',3,0),('install','validate',1,7),('install','smoke',2,8),('install','install',3,9),('remove','',1,0),('remove','remove',1,10)]:
            log=base/(operation+'-'+failure+'.log');trace.unlink(missing_ok=True)
            command=[args.pwsh,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'installer/windows/wpf/wpf-runner.ps1'),'-Engine',str(Path(args.pwsh).resolve()),'-Payload',str(base),'-Client',client,'-Log',str(log),'-Operation',operation]
            run=subprocess.run(command,env={**os.environ,'CV_TRACE':str(trace),'CV_FAIL':failure},capture_output=True,text=True,errors="replace",timeout=60)
            assert run.returncode==code,(run.returncode,run.stdout,run.stderr,log.read_bytes() if log.exists() else "no log")
            calls=[json.loads(line) for line in trace.read_text(encoding="utf-8-sig").splitlines()];assert len(calls)==count
            for call in calls:
                if call['stage'] != 'smoke':assert call['client']==client
            expected=['validate','smoke','install'] if operation=='install' else ['remove']
            assert [call['stage'] for call in calls]==expected[:count]
            assert Path(str(log)+'.stage').read_text().strip()==('complete' if code==0 else str(count))
    print('PASS: WPF payload/BOM, bridge stages, stop on failure, exit codes, completion marker and Unicode/quoted paths')
    print('Engine tested:',args.pwsh)
    print('Does not validate WPF rendering or Hytale gameplay.')

if __name__=='__main__':main()
