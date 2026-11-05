# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check branded GTK controls against a user-priority theme, without game writes."""
import sys
import tempfile
import traceback
from pathlib import Path
import cairo
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'installer/linux/gui'))
from app import Gtk, Gdk, GLib, install_styles

app = Gtk.Application(application_id='io.github.vertexiom.ClearView.StyleTest')
errors = []


def rgb(widget):
    color = widget.get_style_context().get_color()
    return tuple(round(v * 255) for v in (color.red, color.green, color.blue))


def activate(app):
    global window, primary, link, outside, theme
    theme = Gtk.CssProvider()
    theme.load_from_data(b'button { background: #ff00ff; color: #ff0000; border-radius: 0; } button.link label { color: #ff0000; text-decoration: underline; }')
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), theme, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    install_styles(Gdk.Display.get_default())
    window = Gtk.ApplicationWindow(application=app)
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    branded = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    branded.add_css_class('clearview-ui')
    primary = Gtk.Button(label='Continuar'); primary.add_css_class('primary')
    link = Gtk.Button(label='Remover instalação'); link.add_css_class('link')
    outside = Gtk.Button(label='Native control outside branded content')
    branded.append(primary); branded.append(link)
    root.append(branded); root.append(outside)
    window.set_child(root); window.present(); outside.grab_focus()
    GLib.timeout_add(500, check)


def check():
    try:
        assert rgb(primary.get_child()) == (9, 33, 50), rgb(primary.get_child())
        assert rgb(link.get_child()) == (141, 210, 244), rgb(link.get_child())
        assert rgb(outside.get_child()) == (255, 0, 0), 'Application styling leaked outside content'
        snapshot = Gtk.Snapshot()
        Gtk.WidgetPaintable.new(primary).snapshot(snapshot, primary.get_width(), primary.get_height())
        texture = window.get_renderer().render_texture(snapshot.to_node(), None)
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / 'button.png'); texture.save_to_png(path)
            surface = cairo.ImageSurface.create_from_png(path)
            data = bytes(surface.get_data()); stride = surface.get_stride()
            def pixel(x, y):
                b, g, r, a = data[y*stride+x*4:y*stride+x*4+4]
                return r, g, b, a
            # The top centre is filled blue; the rounded corner is transparent.
            assert pixel(surface.get_width()//2, 5) == (141, 210, 244, 255)
            assert pixel(1, 1)[3] == 0, 'Rounded corner lost to theme'
        print('PASS: primary fill/text, blue link, rounded corner and native-style isolation with a user GTK theme')
    except Exception:
        errors.append(traceback.format_exc())
    finally:
        app.quit()
    return GLib.SOURCE_REMOVE


app.connect('activate', activate)
app.run([])
if errors:
    raise SystemExit('\n'.join(errors))
