# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Cairo ASCII rain. Time-based, bounded particles, no dependency on TTE."""
import random
import gi
gi.require_version('Gtk', '4.0')
gi.require_foreign('cairo')
from gi.repository import Gtk
import cairo

BANNER = [
    '  ___ _               __   ___            ',
    r' / __| |___ __ _ _ _  \ \ / (_)_____ __ __',
    r"| (__| / -_) _` | '_|  \ V /| / -_) V  V /",
    r' \___|_\___\__,_|_|     \_/ |_\___|\_/\_/ ',
]

# Most rain travels behind the lettering; only the foreground layer hits it.
TEXT_COLLISION_FRACTION = 0.45

class Rain(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(300, 420)
        self.set_hexpand(False)
        self.set_vexpand(True)
        self.set_draw_func(self.draw)
        self.rng = random.Random()
        self.drops, self.splashes = [], []
        self.elapsed = self.emission = 0
        self.field_size = None
        self.tick_id = 0
        self.last_time = None
        self.paused = False
        self.settings = Gtk.Settings.get_default()
        self.settings.connect('notify::gtk-enable-animations', self.settings_changed)
        self.settings_changed()

    def settings_changed(self, *_):
        self.set_paused(not self.settings.get_property('gtk-enable-animations'))

    def set_paused(self, paused):
        self.paused = paused
        if paused and self.tick_id:
            self.remove_tick_callback(self.tick_id)
            self.tick_id = 0
        elif not paused and not self.tick_id:
            self.last_time = None
            self.tick_id = self.add_tick_callback(self.tick)
        self.queue_draw()

    def geometry(self, w, h):
        cw = (w - 28) / 43
        ch = cw * 1.95
        floor = h - 80
        top = (68 + floor - len(BANNER) * ch) / 2
        cells = [(14 + x*cw, top + y*ch, c) for y, line in enumerate(BANNER)
                 for x, c in enumerate(line) if c != ' ']
        return cw, ch, floor, cells

    def new_drop(self, x, y):
        depth = self.rng.uniform(.65, 1.25)
        return [x, y, 110*depth, depth,
                self.rng.random() < TEXT_COLLISION_FRACTION]

    def fill_field(self, w, h, floor):
        if self.field_size == (w, h):
            return
        self.field_size = (w, h)
        self.emission = 0
        self.splashes = []
        # Start with rain across the whole panel, not an empty lower half.
        columns = max(1, int((w-24)/14))
        rows = max(1, int((floor-60)/19))
        self.drops = [self.new_drop(
            12+(x+self.rng.random())*(w-24)/columns,
            60+(y+self.rng.random())*(floor-60)/rows)
            for y in range(rows) for x in range(columns)][:1800]

    def tick(self, _, clock):
        now = clock.get_frame_time() / 1e6
        dt = min(now - self.last_time, .04) if self.last_time is not None else 0
        self.last_time = now
        if not self.get_mapped():
            return True
        w, h = self.get_width(), self.get_height()
        if w < 1 or h < 1:
            return True
        cw, ch, floor, cells = self.geometry(w, h)
        self.fill_field(w, h, floor)
        width, height = max(1, w-24), max(1, floor-60)
        # Diagonal rain enters from the top AND left edge. Top-only emission
        # leaves a dry wedge on the lower left as the wind carries drops right.
        side_weight = .24 * height
        self.emission += dt * 90 * (width + side_weight) / 276
        while self.emission >= 1:
            self.emission -= 1
            if len(self.drops) >= 1800:
                continue
            if self.rng.random() < width / (width + side_weight):
                x, y = self.rng.uniform(12, w-12), 60.
            else:
                x, y = 12., self.rng.uniform(60, floor)
            self.drops.append(self.new_drop(x, y))
        live = []
        for d in self.drops:
            old = d[1]
            d[0] += d[2]*.24*dt
            d[1] += d[2]*dt
            hit = floor if d[1] >= floor else None
            if hit is None and d[4]:
                for x, y, _ in cells:
                    if x-cw*.45 <= d[0] < x+cw and old <= y+ch*.4 and d[1] >= y:
                        hit = y
                        break
            if hit is None and d[0] < w-12:
                live.append(d)
            elif hit is not None:
                for sign in (-1, 1):
                    self.splashes.append([d[0], hit, sign*self.rng.uniform(12, 28), -30., .45])
        self.drops = live
        for p in self.splashes:
            p[4] -= dt
            p[0] += p[2]*dt
            p[1] += p[3]*dt
            p[3] += 150*dt
        self.splashes = [p for p in self.splashes if p[4] > 0][-200:]
        self.queue_draw()
        return True

    def draw(self, _, cr, w, h):
        cr.set_source_rgb(7/255, 16/255, 24/255)
        cr.paint()
        cw, ch, floor, cells = self.geometry(w, h)
        cr.select_font_face('JetBrains Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(cw * 1.65)
        self.fill_field(w, h, floor)
        cr.save()
        cr.rectangle(12, 60, max(1, w-24), max(1, floor-60))
        cr.clip()
        for x, y, _, depth, _ in self.drops:
            cr.set_source_rgba(.47, .71, .85, .25+depth*.35)
            cr.move_to(x, y+ch*.75)
            cr.show_text('\\')
        cr.restore()
        cr.set_source_rgb(.82, .93, .98)
        for x, y, c in cells:
            cr.move_to(x, y+ch*.75)
            cr.show_text(c)
        cr.set_source_rgb(.32, .49, .58)
        for x in range(12, w-12, max(1, round(cw))):
            cr.move_to(x, floor+ch*.75)
            cr.show_text('_')
        for x, y, _, _, life in self.splashes:
            cr.set_source_rgba(.66, .85, .94, life/.45)
            cr.move_to(x, y+ch*.75)
            cr.show_text("'" if life > .3 else '.')
        cr.select_font_face('sans-serif', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(11)
        cr.set_source_rgb(.55, .65, .72)
        cr.move_to(25, 35)
        cr.show_text('C L E A R V I E W  /  V E R T E X I O M')
        cr.move_to(25, h-25)
        cr.show_text('v0.1.3 · em desenvolvimento')
