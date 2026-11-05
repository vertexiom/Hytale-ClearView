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
        self.emission += dt * 55
        while self.emission >= 1:
            self.emission -= 1
            depth = self.rng.uniform(.65, 1.25)
            self.drops.append([self.rng.uniform(-30, w), 68., 110*depth, depth])
        live = []
        for d in self.drops:
            old = d[1]
            d[0] += d[2]*.24*dt
            d[1] += d[2]*dt
            hit = floor if d[1] >= floor else None
            if hit is None:
                for x, y, _ in cells:
                    if x-cw*.45 <= d[0] < x+cw and old <= y+ch*.4 and d[1] >= y:
                        hit = y
                        break
            if hit is None and d[0] < w+10:
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
        drops = self.drops or [[(i*83) % max(w, 1), 75+(i*47) % max(floor-80, 1), 0, .7] for i in range(35)]
        for x, y, _, depth in drops:
            cr.set_source_rgba(.47, .71, .85, .25+depth*.35)
            cr.move_to(x, y+ch*.75)
            cr.show_text('\\')
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
        cr.show_text('v0.1.2 · em desenvolvimento')
