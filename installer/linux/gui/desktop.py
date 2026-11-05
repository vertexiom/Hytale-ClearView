# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Register the folder installer's identity with the user's desktop, without root."""
from pathlib import Path
import tempfile
from gi.repository import GLib

APP_ID = 'io.github.vertexiom.ClearView'

def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
        temporary = Path(file.name)
        file.write(data)
    try:
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)

def quote_exec(value):
    if '\n' in value or '\r' in value:
        raise ValueError('Unsupported newline in launcher path')
    value = value.replace('%', '%%')
    for char in ('\\', '"', '`', '$'):
        value = value.replace(char, '\\' + char)
    return '"' + value + '"'

def register(root, data_home=None):
    root = Path(root).resolve()
    source = root/'assets/icons'/f'{APP_ID}.png'
    # System packages already provide their desktop entry and icon.
    if not source.is_file():
        return
    data = Path(data_home or GLib.get_user_data_dir())
    icon = data/'icons'/f'{APP_ID}.png'
    # Preserve the original PNG; the desktop scales it to the requested size.
    atomic_write(icon, source.read_bytes())
    entry = GLib.KeyFile()
    fields = {
        'Type': 'Application', 'Name': 'ClearView Installer',
        'Exec': '/usr/bin/python3 ' + quote_exec(str(root/'installer/linux/gui/app.py')),
        'Icon': str(icon), 'StartupWMClass': APP_ID,
        'Terminal': 'false', 'StartupNotify': 'true', 'Categories': 'Game;',
        'Comment': 'Install, update or remove ClearView',
    }
    for key, value in fields.items():
        entry.set_string('Desktop Entry', key, value)
    atomic_write(data/'applications'/f'{APP_ID}.desktop', entry.to_data()[0].encode())
