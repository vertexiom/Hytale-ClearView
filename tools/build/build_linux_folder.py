#!/usr/bin/env python3
# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Create the self-contained project folder (system GTK/Python still required)."""
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
ROOT=Path(__file__).resolve().parents[2]
NAME='ClearView-0.1.2-linux-x64'

def main():
    subprocess.run(['bash',str(ROOT/'tools/build/build_linux.sh')],check=True)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='clearview-folder-') as tmp:
        folder=Path(tmp)/NAME
        def copy(src,dst):
            target=folder/dst;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/src,target)
        copy('LICENSE','LICENSE')
        copy('install.sh','install.sh')
        copy('installer/linux/install.py','installer/linux/install.py')
        for name in ('desktop.py','app.py','real.py','model.py','rain.py','style.css','run.sh'):
            copy('installer/linux/gui/'+name,'installer/linux/gui/'+name)
        for name in ('libSDL3.so','linux-manifest.json'):
            copy('build/'+name,'build/'+name)
        copy('assets/icons/io.github.vertexiom.ClearView.png','assets/icons/io.github.vertexiom.ClearView.png')
        copy('installer/linux/package/FOLDER-README.txt','README.txt')
        archive=dist/(NAME+'.tar.gz')
        with tarfile.open(archive,'w:gz') as out:out.add(folder,arcname=NAME)
        # Replace only this generated package directory, never the repository.
        target=dist/NAME
        if target.exists():shutil.rmtree(target)
        shutil.copytree(folder,target)
        print('Pasta:',target)
        print('Arquivo para compartilhar:',archive)

if __name__=='__main__':main()
