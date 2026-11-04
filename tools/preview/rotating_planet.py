#!/usr/bin/env python3
"""Independent orthographic ASCII sphere prototype, with a stationary H overlay.

Concept references (no third-party implementation copied):
https://github.com/adam-wier/globe
https://github.com/jcubic/ascii-globe
Terrain is an artistic, procedural interpretation, not Hytale map data.
"""
import argparse
import json
import math
import os
from pathlib import Path
import select
import shutil
import sys
import termios
import time
import tty
from PIL import Image, ImageEnhance, ImageFilter
from ascii_planet import CONFIG, SOURCE, OUT, in_emblem, render, square_grid, terminal_cell_ratio

TAU = math.tau
TW, TH = 720, 360


def terrain(lon, lat, u, v):
    # Continuous periodic fields: a full turn closes without a seam.
    coast = (math.sin(lon*3+0.8*math.sin(lat*5)) +
             0.48*math.cos(lon*7-lat*6) + 0.22*math.sin(lon*13+lat*11))
    grain = ((u*73856093) ^ (v*19349663)) & 0xffffffff
    grain = ((grain ^ (grain >> 16))*2246822519) & 0xffffffff
    if coast < -0.38:
        return '.:70'[grain % 4], (22, 104, 160), 'ocean'
    if lat > 0.52 + 0.12*math.sin(lon*4):
        ridge = math.sin(lon*19 + lat*23)
        color = (185, 222, 245) if ridge > -0.1 else (64, 137, 174)
        return ':70#%@'[grain % 6], color, 'snow'
    region = math.sin(lon+0.65) + 0.20*math.sin(lat*7+lon*3)
    if region > 0.52:
        fissure = abs(math.sin(lon*17+math.sin(lat*13)*1.8))
        color = (245, 86, 22) if fissure < 0.15 else (104, 86, 106)
        return '70#%@'[grain % 5], color, 'volcano'
    if lat < -0.22 + 0.19*math.sin(lon*2):
        dune = 0.5 + 0.5*math.sin(lat*35+lon*8)
        return '.:70#'[grain % 5], (int(170+55*dune), int(117+53*dune), 43), 'desert'
    river = abs(math.sin(lon*12 + lat*9 + math.sin(lat*16)*0.6)) < 0.07
    if river:
        return ':70'[grain % 3], (32, 149, 205), 'forest'
    return '70#%@'[grain % 5], (65+grain%35, 145+grain%55, 37+grain%30), 'forest'


def make_texture():
    return [[terrain((u/TW-0.5)*TAU, (0.5-v/(TH-1))*math.pi, u, v)
             for u in range(TW)] for v in range(TH)]


class Planet:
    def __init__(self, width, height, settings, texture):
        self.width, self.height, self.texture = width, height, texture
        self.cells = []
        plain, _ = render(width, height, settings)
        lines = plain.splitlines()
        with Image.open(SOURCE) as source:
            im = ImageEnhance.Color(source.convert('RGB')).enhance(settings['saturation'])
        im = im.filter(ImageFilter.GaussianBlur(settings['blur'])).resize((width,height), Image.Resampling.BOX)
        # Same globe extent as the approved image; physical aspect handled by grid.
        for y in range(height):
            row = []
            for x in range(width):
                nx, ny = (x+0.5)/width, (y+0.5)/height
                if in_emblem(nx,ny):
                    rgb = im.getpixel((x,y))
                    gain = min(settings['color_gain'], 255/max(1,max(rgb)))
                    row.append(('fixed', lines[y][x], tuple(round(c*gain) for c in rgb)))
                    continue
                # Small black halo around the letter, rather than a rectangular cutout.
                if any(in_emblem(nx+dx/width,ny+dy/height) for dx,dy in ((-1,0),(1,0),(0,-1),(0,1))):
                    row.append(None); continue
                sx, sy = (nx-0.49)/0.40, (0.49-ny)/0.40
                d = sx*sx+sy*sy
                if d > 1:
                    row.append(None); continue
                z = math.sqrt(1-d)
                lon = math.atan2(sx,z)
                lat = math.asin(max(-1,min(1,sy)))
                # Soft fixed illumination makes the spherical surface readable.
                shade = 0.48+0.52*max(0,(-0.25*sx+0.22*sy+0.94*z))
                row.append(('sphere',lon,lat,shade))
            self.cells.append(row)

    def frame(self, angle, color=True):
        rows = []
        for row in self.cells:
            output=[]; previous=None
            for cell in row:
                if cell is None:
                    output.append(' '); continue
                if cell[0]=='fixed':
                    _,ch,rgb=cell
                else:
                    _,lon,lat,shade=cell
                    u=int(((lon+angle)/TAU+0.5)*TW)%TW
                    v=min(TH-1,max(0,round((0.5-lat/math.pi)*(TH-1))))
                    ch,base,_=self.texture[v][u]
                    rgb=tuple(min(255,int(c*shade)//8*8) for c in base)
                if color and rgb!=previous:
                    output.append(f'\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m'); previous=rgb
                output.append(ch)
            rows.append(('\033[1m' if color else '')+''.join(output)+('\033[0m' if color else ''))
        return '\n'.join(rows)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    settings=json.loads(CONFIG.read_text());texture=make_texture()
    if args.check:
        globe=Planet(170,82,settings,texture)
        a=globe.frame(0,False); b=globe.frame(0.8,False)
        assert a!=b and a==globe.frame(TAU,False)
        assert set(a)<=set(' .:70#%@/\n')
        for y,row in enumerate(globe.cells):
            for x,cell in enumerate(row):
                if cell and cell[0]=='fixed':
                    assert a.splitlines()[y][x]==b.splitlines()[y][x]
        assert {item[2] for row in texture for item in row}=={'ocean','snow','forest','desert','volcano'}
        start=time.perf_counter()
        for i in range(20): globe.frame(i/20)
        print(f'PASS: rotation, 360-degree seam, fixed H, alphabet, four regions. {(time.perf_counter()-start)/20*1000:.1f} ms/frame at 170x82.')
        OUT.mkdir(exist_ok=True,parents=True)
        (OUT/'rotating-front.ansi').write_text(globe.frame(0)+'\n')
        return
    if not sys.stdin.isatty():
        parser.error('Abra no Ghostty.')
    print('CLEARVIEW | Planeta girando + H fixo\nMaximize a janela. Enter para iniciar.')
    input()
    old=termios.tcgetattr(sys.stdin)
    angle=0.;speed=TAU/60;paused=False;last_size=None;last=time.monotonic()
    try:
        tty.setcbreak(sys.stdin.fileno());sys.stdout.write('\033[?1049h\033[?25l\033[40m\033[2J')
        while True:
            begin=time.monotonic();size=shutil.get_terminal_size()
            if size!=last_size:
                ratio=terminal_cell_ratio(settings['cell_ratio'])
                width,height=square_grid(size,settings['columns'],ratio,footer=5)
                globe=Planet(width,height,settings,texture);last_size=size
                sys.stdout.write('\033[2J');last=time.monotonic()
            now=time.monotonic()
            if not paused: angle=(angle+speed*(now-last))%TAU
            last=now
            pad=' '*max(0,(size.columns-globe.width)//2)
            body='\n'.join(pad+line for line in globe.frame(angle).split('\n'))
            footer=f'  PLANETA 3D | H fixo | {globe.width}x{globe.height} | volta: {TAU/abs(speed):.0f}s'
            sys.stdout.write('\033[?2026h\033[H'+body+'\033[0m\n\033[K'+footer+
                '\n\033[K  Espaco: pausa | +/-: velocidade | D: inverter | Q: sair\n\033[K'+
                ('  PAUSADO' if paused else '  Girando')+'\033[?2026l');sys.stdout.flush()
            if select.select([sys.stdin],[],[],max(0,1/24-(time.monotonic()-begin)))[0]:
                key=os.read(sys.stdin.fileno(),32).decode(errors='ignore').lower()
                if any(c in key for c in ('q','\x03','\x04')):break
                for c in key:
                    if c==' ':paused=not paused
                    elif c in '+=':speed=math.copysign(min(abs(speed)*1.25,TAU/8),speed)
                    elif c=='-':speed=math.copysign(max(abs(speed)/1.25,TAU/300),speed)
                    elif c=='d':speed=-speed
    finally:
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old)
        sys.stdout.write('\033[?2026l\033[0m\033[?25h\033[?1049l');sys.stdout.flush()

if __name__=='__main__':main()
