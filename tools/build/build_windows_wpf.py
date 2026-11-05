# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Package the WPF installer locally. Requires .NET 10 SDK and existing Windows payload build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dotnet',default='dotnet')
    parser.add_argument('--payload-only',action='store_true')
    args=parser.parse_args()
    build=ROOT/'build/windows'; manifest=json.loads((build/'manifest.json').read_text(encoding="utf-8"))
    if manifest['version']!='0.1.3':raise SystemExit('Build the Windows v0.1.3 payload first.')
    expected={'opengl32.dll','clearview-smoke.exe'}
    if set(manifest['files'])!=expected:raise SystemExit('Unexpected payload manifest')
    for name in expected:
        if hashlib.sha256((build/name).read_bytes()).hexdigest()!=manifest['files'][name]:
            raise SystemExit('Payload hash mismatch: '+name)
    with zipfile.ZipFile(build/'wpf-payload.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in ('install.ps1','smoke-test.ps1','workflow.ps1'):
            archive.writestr(name,(ROOT/'installer/windows'/name).read_text(encoding='utf-8-sig').encode('utf-8-sig'))
        archive.writestr('wpf-runner.ps1',(ROOT/'installer/windows/wpf/wpf-runner.ps1').read_text(encoding="utf-8-sig").encode('utf-8-sig'))
        archive.write(build/'manifest.json','manifest.json')
        for name in sorted(expected):archive.write(build/name,'bin/'+name)
    if args.payload_only:return
    dotnet=shutil.which(args.dotnet)
    if not dotnet:raise SystemExit('Pass --dotnet /path/to/dotnet (.NET 10 SDK)')
    env={**os.environ,'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_NOLOGO':'1'}
    project=ROOT/'installer/windows/wpf/ClearView.Setup.csproj'
    subprocess.run([dotnet,'restore',str(project),'-r','win-x64'],check=True,env=env)
    assets=json.loads((project.parent/'obj/project.assets.json').read_text(encoding="utf-8"))
    runtime=ET.parse(project).getroot().findtext('.//RuntimeFrameworkVersion')
    notices=[(ROOT/'assets/fonts/LICENSES.txt').read_text(encoding='utf-8')]
    for package in ('microsoft.netcore.app.runtime.win-x64','microsoft.windowsdesktop.app.runtime.win-x64'):
        directory=next((Path(folder)/package/runtime for folder in assets['packageFolders'] if (Path(folder)/package/runtime).is_dir()),None)
        if directory is None:raise SystemExit('Missing runtime license package: '+package)
        license_files=[p for p in directory.iterdir() if p.name.upper() in ('LICENSE','LICENSE.TXT','THIRD-PARTY-NOTICES.TXT')]
        if not any(p.name.upper().startswith('LICENSE') for p in license_files):raise SystemExit('Missing runtime license: '+package)
        for path in sorted(license_files):notices.append(package+' '+runtime+' / '+path.name+'\n\n'+path.read_text(encoding='utf-8-sig'))
    (build/'wpf-third-party.txt').write_text('\n\n'.join(notices),encoding='utf-8')
    output=ROOT/'dist/windows-wpf'
    subprocess.run([dotnet,'publish',str(ROOT/'installer/windows/wpf/ClearView.Setup.csproj'),'-c','Release','-r','win-x64','--self-contained','true','-o',str(output)],check=True,env=env)
    release=ROOT/'dist/ClearView-0.1.3-Setup.exe'
    shutil.copy2(output/'ClearView-WPF-Setup.exe',release)
    print('Release installer:',release)
    print('Preview without game writes: ClearView-WPF-Setup.exe --preview')
    print('Native Windows validation remains pending; see release notes.')

if __name__=='__main__':main()
