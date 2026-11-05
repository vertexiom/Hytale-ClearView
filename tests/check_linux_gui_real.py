# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Exercise real GTK subprocess install/update/remove, only in a temporary client."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer/linux/gui'))
from app import Gtk, GLib
from real import RealWindow

tmp=tempfile.TemporaryDirectory()
client=Path(tmp.name)
(client/'HytaleClient').write_bytes(b'fixture')
(client/'libSDL3.so').write_bytes(b'original fixture')
app=Gtk.Application(application_id='io.github.vertexiom.ClearView.RealTest')
errors=[]
phase=0

def activate(_):
    global window
    window=RealWindow(app);window.select(client);window.present()
    window.show('location');window.begin('install')
    assert window.request_close()
    GLib.timeout_add(50,poll)

def poll():
    global phase
    try:
        if window.state.screen=='progress':return GLib.SOURCE_CONTINUE
        assert window.state.screen!='error',window.message
        settings=client/'.clearview/settings'
        if phase==0:
            assert window.result['operation']=='install'
            settings.write_text('0.12 0.34 0.56\n')
            phase=1;window.show('location');window.begin('install')
        elif phase==1:
            assert window.result['operation']=='update'
            assert settings.read_text()=='0.12 0.34 0.56\n'
            phase=2;window.show('remove');window.begin('remove')
        elif phase==2:
            assert window.state.screen=='removed'
            assert (client/'libSDL3.so').read_bytes()==b'original fixture'
            phase=3;window.show('remove');window.begin('remove')
            # Expected error in next poll.
            GLib.timeout_add(50,check_error)
            return GLib.SOURCE_REMOVE
    except Exception as exc:
        errors.append(str(exc));app.quit();return GLib.SOURCE_REMOVE
    return GLib.SOURCE_CONTINUE

def check_error():
    if window.state.screen=='progress':return GLib.SOURCE_CONTINUE
    if window.state.screen!='error':errors.append('Expected not-installed error')
    window.report();window.close_dialog()
    print('PASS: real GTK subprocess install, update, settings preservation, removal and error reporting')
    window.rain.set_paused(True);app.quit();return GLib.SOURCE_REMOVE

def timeout():
    errors.append('Timed out');app.quit();return GLib.SOURCE_REMOVE
app.connect('activate',activate)
GLib.timeout_add_seconds(30,timeout)
app.run([sys.argv[0]])
tmp.cleanup()
if errors:raise SystemExit('\n'.join(errors))
