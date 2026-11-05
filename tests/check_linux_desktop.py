# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check desktop identity registration without touching the user's desktop."""
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'installer/linux/gui'))
from desktop import APP_ID, register
from gi.repository import Gio, GLib

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)/'ClearView space " quote $ % slash\\'
    source = root/'assets/icons'/f'{APP_ID}.png'
    source.parent.mkdir(parents=True)
    source.write_bytes(b'first icon')
    data = Path(directory)/'user-data'
    register(root, data)
    path = data/'applications'/f'{APP_ID}.desktop'
    subprocess.run(['desktop-file-validate',str(path)],check=True)
    entry = GLib.KeyFile();entry.load_from_file(str(path),GLib.KeyFileFlags.NONE)
    assert entry.get_string('Desktop Entry','StartupWMClass') == APP_ID
    assert entry.get_string('Desktop Entry','Icon') == str(data/'icons'/f'{APP_ID}.png')
    assert Gio.DesktopAppInfo.new_from_filename(str(path)) is not None
    source.write_bytes(b'new planet')
    register(root,data)
    assert (data/'icons'/f'{APP_ID}.png').read_bytes()==b'new planet'
print('PASS: desktop entry validation, special paths, identity, icon replacement')
