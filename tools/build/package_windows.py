# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Build a single graphical Windows installer. No publication or game changes."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[2]

def byte_array(name, data):
    return 'static const unsigned char '+name+'[] = {\n'+',\n'.join(','.join(str(b) for b in data[i:i+24]) for i in range(0,len(data),24))+'\n};\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--zig',default=os.environ.get('ZIG','zig'));args=parser.parse_args()
    zig=shutil.which(args.zig)
    if not zig:raise SystemExit('Pass --zig /path/to/zig')
    build=ROOT/'build/windows'
    manifest=json.loads((build/'manifest.json').read_text())
    for name,expected in manifest['files'].items():
        if name not in ['opengl32.dll','clearview-smoke.exe']:raise ValueError('Unexpected artifact')
        assert hashlib.sha256((build/name).read_bytes()).hexdigest()==expected,name+' hash mismatch'
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in ['install.ps1','smoke-test.ps1']:
            # Windows PowerShell 5.1 requires a BOM for non-ASCII UTF-8.
            archive.writestr(name,(ROOT/'installer/windows'/name).read_text(encoding='utf-8-sig').encode('utf-8-sig'))
        archive.writestr('workflow.ps1',(ROOT/'installer/windows/workflow.ps1').read_text().encode('utf-8-sig'))
        archive.write(build/'manifest.json','manifest.json')
        for name in manifest['files']:archive.write(build/name,'bin/'+name)
    data=buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={'install.ps1','smoke-test.ps1','workflow.ps1','manifest.json','bin/opengl32.dll','bin/clearview-smoke.exe'}
    (build/'payload.zip').write_bytes(data)
    gui=(ROOT/'installer/windows/setup.ps1').read_text(encoding='utf-8-sig').encode('utf-8-sig')
    (build/'payload.h').write_text(byte_array('package_zip',data)+byte_array('gui_script',gui))
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    target=out/('ClearView-'+manifest['version']+'-Setup.exe')
    subprocess.run([zig,'rc','/fo',str(build/'setup.res'),'--',str(ROOT/'installer/windows/setup.rc')],cwd=ROOT/'installer/windows',check=True)
    subprocess.run([zig,'cc','-target','x86_64-windows-gnu','-std=c11','-O2','-Wall','-Wextra','-Werror',
                    '-municode','-Wl,--subsystem,windows','-I'+str(build),str(ROOT/'installer/windows/bootstrap.c'),str(build/'setup.res'),
                    '-lole32','-luser32','-lkernel32','-o',str(target)],check=True)
    print(target)
    print('Internal verification SHA256:',hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
