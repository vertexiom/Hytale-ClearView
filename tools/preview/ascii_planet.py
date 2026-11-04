#!/usr/bin/env python3
"""Local, live ANSI/ASCII study. Does not install or alter the game."""
import fcntl
import struct
import re
import argparse
import json
import math
from pathlib import Path
import select
import shutil
import sys
import termios
import time
import tty
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_suffix('.json')
SOURCE = ROOT / 'assets/concepts/clearview-ascii-planet-zones-v1.png'
OUT = ROOT / 'build/ascii-preview'

def terminal_cell_ratio(fallback=0.48):
    """Measure cell width/height; equal cell counts are not square pixels."""
    if not sys.stdin.isatty():
        return fallback
    fd = sys.stdin.fileno()
    rows, cols, xpixels, ypixels = struct.unpack(
        'HHHH', fcntl.ioctl(fd, termios.TIOCGWINSZ, bytes(8)))
    if rows and cols and xpixels and ypixels:
        return (xpixels / cols) / (ypixels / rows)
    previous = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        sys.stdout.write('\033[16t')
        sys.stdout.flush()
        response = ''
        deadline = time.monotonic() + 0.3
        while time.monotonic() < deadline:
            if select.select([sys.stdin], [], [], max(0, deadline-time.monotonic()))[0]:
                import os
                response += os.read(fd, 128).decode('ascii', errors='ignore')
                match = re.search(r'\x1b\[6;(\d+);(\d+)t', response)
                if match:
                    height, width = map(int, match.groups())
                    if width and height:
                        return width / height
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, previous)
    return fallback


def square_grid(size, preferred, ratio, footer=5):
    width = max(1, min(preferred, size.columns-2, int(max(1, size.lines-footer)/ratio)))
    return width, max(1, round(width*ratio))


def inside_polygon(x, y, points):
    inside = False
    previous = points[-1]
    for current in points:
        ax, ay = previous
        bx, by = current
        if (ay > y) != (by > y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
            inside = not inside
        previous = current
    return inside


def in_emblem(x, y):
    # Normalized outline of the approved H, independent of terminal size.
    left = [(0.305,0.277),(0.365,0.258),(0.39,0.24),(0.412,0.26),
            (0.47,0.278),(0.428,0.343),(0.428,0.60),(0.464,0.665),
            (0.415,0.68),(0.39,0.704),(0.363,0.68),(0.302,0.668),
            (0.341,0.60),(0.341,0.343)]
    right = [(1-x,y) for x,y in left]
    cross = [(0.41,0.445),(0.47,0.445),(0.49,0.42),(0.515,0.445),
             (0.59,0.445),(0.60,0.48),(0.52,0.505),(0.49,0.518),
             (0.465,0.497),(0.40,0.48)]
    return any(inside_polygon(x,y,polygon) for polygon in (left,right,cross))


def render(columns, rows, settings):
    # Area sampling extracts shapes/colors rather than attempting OCR of AI glyphs.
    with Image.open(SOURCE) as source:
        im = source.convert('RGB')
    im = ImageEnhance.Color(im).enhance(settings['saturation'])
    im = im.filter(ImageFilter.GaussianBlur(settings['blur']))
    im = im.resize((columns, rows), Image.Resampling.BOX)
    plain, colored = [], []
    for y in range(rows):
        p, c = [], []
        for x in range(columns):
            r, g, b = im.getpixel((x, y))
            brightness = max(r, g, b) / 255
            if brightness < settings['black_threshold']:
                p.append(' '); c.append(' '); continue
            # Reference-inspired ASCII ramp; biome identity remains in the colors.
            alphabet = settings.get('characters', '.:70#%@')
            level = brightness ** settings['density_gamma']
            # Stable variation within density bands avoids horizontal stripes.
            pools = ('.:::', '::7', ':#0', '##%', '#%%@', '#%@@')
            pool = ''.join(ch for ch in pools[min(5, int(level * 6))] if ch in alphabet) or alphabet
            seed = ((x * 73856093) ^ (y * 19349663)) & 0xffffffff
            seed = ((seed ^ (seed >> 16)) * 2246822519) & 0xffffffff
            ch = pool[seed % len(pool)]
            if len(p) >= 2 and p[-1] == p[-2] == ch:
                alternatives = [symbol for symbol in pool if symbol != ch]
                if alternatives:
                    ch = alternatives[(seed >> 8) % len(alternatives)]
            nx, ny = (x + 0.5) / columns, (y + 0.5) / rows
            if in_emblem(nx, ny):
                edge = any(not in_emblem(nx+dx/columns, ny+dy/rows)
                           for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
                ch = '/' if edge else '#%@'[(seed >> 8) % 3]
            scale = min(settings['color_gain'], 255 / max(r, g, b, 1))
            rgb = tuple(round(v * scale) for v in (r, g, b))
            p.append(ch)
            c.append(f'\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{ch}')
        plain.append(''.join(p))
        colored.append('\033[1m' + ''.join(c) + '\033[0m')
    return '\n'.join(plain), '\n'.join(colored)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    settings = json.loads(CONFIG.read_text())
    def export():
        text, ansi = render(settings['columns'], round(settings['columns'] * settings['cell_ratio']), settings)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT/'planet.txt').write_text(text+'\n')
        (OUT/'planet.ansi').write_text(ansi+'\n')
        return text
    if args.export:
        export(); print(OUT); return
    if not sys.stdin.isatty():
        parser.error('Use a terminal, or --export.')
    old = termios.tcgetattr(sys.stdin)
    previous = None
    live_ratio = settings['cell_ratio']
    status = 'Previa local - nenhuma alteracao no instalador'
    try:
        tty.setcbreak(sys.stdin.fileno())
        sys.stdout.write('\033[?1049h\033[?25l\033[40m\033[2J')
        while True:
            size = shutil.get_terminal_size()
            signature = (size, CONFIG.stat().st_mtime_ns, SOURCE.stat().st_mtime_ns, settings['columns'])
            if signature != previous:
                settings = json.loads(CONFIG.read_text())
                live_ratio = terminal_cell_ratio(settings['cell_ratio'])
                width, height = square_grid(size, settings['columns'], live_ratio)
                _, ansi = render(width, height, settings)
                pad = ' ' * max(0, (size.columns-width)//2)
                frame = '\n'.join(pad+line for line in ansi.split('\n'))
                sys.stdout.write('\033[H\033[2J'+frame+'\033[0m\n')
                sys.stdout.write(f'  CLEARVIEW | ASCII real + cores ANSI | {width}x{height} | celula {live_ratio:.3f}\n')
                sys.stdout.write('  [+/-] detalhe  [S] salvar TXT/ANSI  [R] atualizar  [Q] sair\n')
                sys.stdout.write('  '+status)
                sys.stdout.flush()
                previous = signature
            if select.select([sys.stdin], [], [], 0.25)[0]:
                key = sys.stdin.read(1).lower()
                if key in ('q', '\x03', '\x04'): break
                if key in ('+', '=', '-'):
                    settings['columns'] = max(50, min(300, settings['columns'] + (-10 if key == '-' else 10)))
                    CONFIG.write_text(json.dumps(settings, indent=2)+'\n')
                elif key == 's':
                    export(); status = 'Salvo em build/ascii-preview/planet.txt e planet.ansi'
                previous = None
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        sys.stdout.write('\033[0m\033[?25h\033[?1049l'); sys.stdout.flush()

if __name__ == '__main__':
    main()
