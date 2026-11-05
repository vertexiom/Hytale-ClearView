# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""GTK integration smoke test. Requires a graphical session; never touches game files."""
import sys
import traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer/linux/gui'))
from app import Gtk, Gdk, GLib, Window, HERE
from model import SCENARIOS, FLATPAK

app=Gtk.Application(application_id='io.github.vertexiom.ClearView.Test')
failed=[]
window=None

def guard(fn):
    def wrapped(*args):
        try:fn(*args)
        except Exception:
            failed.append(traceback.format_exc());app.quit()
        return GLib.SOURCE_REMOVE
    return wrapped

def activate(_):
    global window
    provider=Gtk.CssProvider();provider.load_from_path(str(HERE/'style.css'))
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    window=Window(app);window.present()
    GLib.timeout_add(200,guard(check_widgets))

def check_widgets():
    w=window
    assert w.get_titlebar() is None, "Window decoration must remain managed by GTK/the desktop"
    assert w.get_child().has_css_class("clearview-ui")
    for scenario in SCENARIOS:
        w.scenarios.set_selected(list(SCENARIOS).index(scenario));w.show('location')
        assert w.state.scenario==scenario
        if scenario in ('missing','multiple','running'):assert w.primary is None
    w.scenarios.set_selected(list(SCENARIOS).index('missing'));w.show('location')
    w.browse();assert w.dialog is not None
    body=w.dialog.get_child();choice=body.get_first_child().get_next_sibling().get_next_sibling()
    choice.set_selected(1)
    row=body.get_last_child();row.get_last_child().emit('clicked')
    assert w.dialog is None and w.state.path==FLATPAK and w.primary
    w.scenarios.set_selected(list(SCENARIOS).index('graphics'));w.show('error');w.report()
    assert w.dialog and 'demonstração' in w.dialog.get_title()
    w.close_dialog();assert w.dialog is None
    w.rain.set_paused(True);assert w.rain.tick_id==0
    w.rain.set_paused(False);assert w.rain.tick_id!=0
    w.scenarios.set_selected(0);w.show('location');w.primary.emit('clicked')
    assert w.state.screen=='progress' and w.request_close() is True
    assert 'precisa terminar' in w.status.get_text()
    GLib.timeout_add(6800,guard(after_install))

def after_install():
    w=window
    assert w.state.screen=='complete', w.state.screen
    assert w.timer==0 and w.pulse_timer==0
    w.show('location');w.begin('install');w.reset()
    GLib.timeout_add(1900,guard(after_reset))

def after_reset():
    assert window.state.screen=='welcome'
    assert window.timer==0 and window.pulse_timer==0
    print('PASS: GTK scenarios, selection dialog, report, rain pause, completion, close blocking and reset timers')
    window.rain.set_paused(True);app.quit()

app.connect('activate',activate)
app.run([sys.argv[0]])
if failed:
    print('\n'.join(failed),file=sys.stderr)
    raise SystemExit(1)
