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
    with zipfile.ZipFile(ROOT/'build/windows/wpf-payload.zip') as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={'install.ps1','smoke-test.ps1','workflow.ps1','wpf-runner.ps1','manifest.json','bin/opengl32.dll','bin/clearview-smoke.exe'}
        for name in ('install.ps1','smoke-test.ps1','workflow.ps1','wpf-runner.ps1'):
            assert archive.read(name).startswith(b'\xef\xbb\xbf'),name
    with tempfile.TemporaryDirectory(prefix="ClearView WPF espaço ' ") as tmp:
        base=Path(tmp);trace=base/'calls.jsonl';engine=base/'fake engine';client=str(base/"Hytale ' destino")
        shutil.copy2(ROOT/'installer/windows/workflow.ps1',base/'workflow.ps1')
        engine.write_text("#!/usr/bin/python3\nimport os,sys,json\nfrom pathlib import Path\na=sys.argv[1:]\nwith open(os.environ['CV_TRACE'],'a') as f:f.write(json.dumps(a)+'\\n')\nfailure=os.environ.get('CV_FAIL','')\nif failure=='validate' and '-ValidateOnly' in a:sys.exit(7)\nif failure=='smoke' and any(v.endswith('smoke-test.ps1') for v in a):sys.exit(8)\nif failure=='install' and any(v.endswith('install.ps1') for v in a) and '-ValidateOnly' not in a:sys.exit(9)\nprint('ok')\n")
        engine.chmod(0o755)
        for operation,failure,count,code in [('install','',3,0),('install','validate',1,7),('install','smoke',2,8),('install','install',3,9),('remove','',1,0)]:
            log=base/(operation+'-'+failure+'.log');trace.unlink(missing_ok=True)
            command=[args.pwsh,'-NoProfile','-File',str(ROOT/'installer/windows/wpf/wpf-runner.ps1'),'-Engine',str(engine),'-Payload',str(base),'-Client',client,'-Log',str(log),'-Operation',operation]
            run=subprocess.run(command,env={**os.environ,'CV_TRACE':str(trace),'CV_FAIL':failure},capture_output=True,text=True,timeout=30)
            assert run.returncode==code,(run.returncode,run.stdout,run.stderr,log.read_text() if log.exists() else "no log")
            calls=[json.loads(line) for line in trace.read_text().splitlines()];assert len(calls)==count
            for call in calls:
                if '-ClientDir' in call:assert call[call.index('-ClientDir')+1]==client
            assert Path(str(log)+'.stage').read_text().strip()==('complete' if code==0 else str(count))
    print('PASS: WPF payload/BOM, bridge stages, stop on failure, exit codes, completion marker and Unicode/quoted paths')
    print('Does not validate Windows PowerShell 5.1, WPF rendering or Hytale gameplay.')

if __name__=='__main__':main()
