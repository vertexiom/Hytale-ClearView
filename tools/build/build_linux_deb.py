#!/usr/bin/env python3
# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Build a local amd64 GTK installer package; never include game files."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.1.2'

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def main():
    if subprocess.check_output(['dpkg','--print-architecture'],text=True).strip() != 'amd64':
        raise SystemExit('Build requires an amd64 Debian/Ubuntu host.')
    run('bash', str(ROOT/'tools/build/build_linux.sh'))
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='clearview-deb-') as tmp:
        work=Path(tmp); package=work/'debian/clearview-installer'; app=package/'usr/lib/clearview'
        control=package/'DEBIAN';control.mkdir(parents=True)
        def copy(source, target):
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        for name in ('app.py','model.py','rain.py','real.py','style.css','run.sh'):
            copy(ROOT/'installer/linux/gui'/name,app/'installer/linux/gui'/name)
        copy(ROOT/'installer/linux/install.py',app/'installer/linux/install.py')
        for name in ('libSDL3.so','linux-manifest.json'):
            copy(ROOT/'build'/name,app/'build'/name)
        manifest=json.loads((app/'build/linux-manifest.json').read_text())
        assert manifest['version']==VERSION
        assert manifest['sha256']==hashlib.sha256((app/'build/libSDL3.so').read_bytes()).hexdigest()
        copy(ROOT/'assets/icons/io.github.vertexiom.ClearView.png',package/'usr/share/pixmaps/io.github.vertexiom.ClearView.png')
        desktop='io.github.vertexiom.ClearView.desktop'
        copy(ROOT/'installer/linux/package'/desktop,package/'usr/share/applications'/desktop)
        run('desktop-file-validate',str(package/'usr/share/applications'/desktop))
        entry=package/'usr/bin/clearview-installer';entry.parent.mkdir(parents=True)
        entry.write_text('#!/bin/sh\nexec /usr/bin/python3 /usr/lib/clearview/installer/linux/gui/app.py "$@"\n')
        entry.chmod(0o755)
        copy(ROOT/'installer/linux/gui/LEIA-ME.txt',package/'usr/share/doc/clearview-installer/README')
        # The original SDL belongs to the game, not to a Debian package.
        # A link-only stub lets shlibdeps resolve that private dependency.
        (work/'debian').mkdir(exist_ok=True)
        (work/'debian/control').write_text('Source: clearview-installer\nSection: games\nPriority: optional\nMaintainer: Vertexiom <vertexiom@users.noreply.github.com>\n\nPackage: clearview-installer\nArchitecture: amd64\nDescription: ClearView installer\n')
        run('cc','-shared','-fPIC','-x','c','/dev/null','-Wl,-soname,libSDL3.clearview-original.so','-o',str(work/'libSDL3.clearview-original.so'))
        deps=subprocess.check_output(['dpkg-shlibdeps','-O','--ignore-missing-info','-l'+str(work),'-e'+str(app/'build/libSDL3.so')],cwd=work,text=True).strip()
        deps=deps.removeprefix('shlibs:Depends=')
        if not deps or 'libc6' not in deps or 'libcairo2' not in deps:
            raise SystemExit('Could not determine payload runtime dependencies: '+deps)
        # Control directory was created before dependency scanning.
        size=sum(p.stat().st_size for p in package.rglob('*') if p.is_file())
        (control/'control').write_text(f'''Package: clearview-installer
Version: {VERSION}-1
Architecture: amd64
Maintainer: Vertexiom <vertexiom@users.noreply.github.com>
Section: games
Priority: optional
Depends: python3 (>= 3.10), python3-gi, python3-gi-cairo, python3-cairo, gir1.2-gtk-4.0 (>= 4.6), {deps}
Installed-Size: {(size+1023)//1024}
Homepage: https://github.com/vertexiom/Hytale-ClearView
Description: Graphical installer for the ClearView Hytale fog mod
 Installs, updates and removes ClearView using a GTK 4 interface.
 Includes a precompiled mod. Hytale must be installed separately.
 Removing this package removes the installer, not the mod in the game.
''')
        entries=[]
        for p in sorted(package.rglob('*')):
            if p.is_file() and control not in p.parents:
                entries.append(f'{hashlib.md5(p.read_bytes()).hexdigest()}  {p.relative_to(package)}')
        (control/'md5sums').write_text('\n'.join(entries)+'\n')
        output=dist/f'clearview-installer_{VERSION}-1_amd64.deb'
        run('dpkg-deb','--root-owner-group','--build',str(package),str(output))
        print(output)

if __name__=='__main__':main()
