#!/usr/bin/env python3
"""Clear View rain study, reusing TTE 0.15.0 Thunderstorm rain/pooling/motion.

Upstream: ChrisBuilds/terminaltexteffects (MIT, copyright ChrisBuilds 2023).
No planet files changed. Local additions: FIGlet scene, collisions and splashes.
"""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[2]
PYTHON=ROOT/'build/ascii-preview/tte-venv/bin/python'
if Path(sys.prefix).resolve()!=PYTHON.parent.parent.resolve():
    os.execv(str(PYTHON), [str(PYTHON), __file__, *sys.argv[1:]])
import math
import argparse
import random
import select
import shutil
import termios
import time
import tty
from pyfiglet import Figlet
import terminaltexteffects as tte
from terminaltexteffects.effects.effect_thunderstorm import Thunderstorm, ThunderstormIterator


def make_scene(width,height):
    font='big' if width>=65 else 'small'
    banner=Figlet(font=font,width=300).renderText('Clear View').rstrip().splitlines()
    if max(map(len,banner))>width-4:
        banner=['Clear View']
    top=max(1,(height-len(banner))//2)
    left=max(0,(width-max(map(len,banner)))//2)
    grid=[[' ']*width for _ in range(height)]
    for y,line in enumerate(banner):
        for x,ch in enumerate(line):
            if ch!=' ':grid[top+y][left+x]=ch
    # ASCII ground, with standing water texture below it.
    for x in range(width):
        grid[height-4][x]='_'
        grid[height-2][x]='.' if x%7==0 else ' '
        grid[height-1][x]=':' if x%13==0 else ' '
    return '\n'.join(''.join(row) for row in grid)


class RainIterator(ThunderstormIterator):
    def build(self):
        self.surfaces={}
        self.splash_active=[];self.splash_pool=[];self.impacts=0
        self.emission_clock=0.0;self.velocities={}
        for char in self.terminal.get_characters():
            self.surfaces[(char.input_coord.column,char.input_coord.row)]=char
            is_floor=char.input_symbol in ('_', '.', ':') and char.input_coord.row<=4
            char.animation.set_appearance(char.input_symbol,colors=tte.ColorPair(fg=tte.Color('39718b' if is_floor else 'c3e8f5')))
            self.terminal.set_character_visibility(char,is_visible=True)
            char.layer=2
        # Direct upstream reuse: creation, randomized fall paths and pooling.
        self.build_raindrop_characters(450)
        for drop in self.rain_drops:
            drop.animation.set_appearance(drop.input_symbol,colors=tte.ColorPair(fg=tte.Color('6295b7')))
            self.terminal.set_character_visibility(drop,is_visible=False)

    def splash(self,coord):
        self.impacts+=1
        for dx in (-1,1):
            particle=self.splash_pool.pop() if self.splash_pool else self.terminal.add_character('.',coord)
            particle.layer=3
            particle.motion.set_coordinate(tte.Coord(coord.column+dx,coord.row+1))
            particle.animation.set_appearance("'",colors=tte.ColorPair(fg=tte.Color('9bd3ed')))
            self.terminal.set_character_visibility(particle,is_visible=True)
            self.splash_active.append([particle,0.0,coord,dx])

    def __next__(self):
        return self.advance(1/60)

    def advance(self, dt):
        # Upstream emission stays at its original 30 Hz; movement uses seconds.
        dt=max(0.0,min(dt,0.05))
        self.emission_clock+=dt
        old_active=set(self.active_characters)
        while self.emission_clock>=1/30:
            # Three upstream emission batches per tick for heavier rain.
            for _ in range(3):
                self.delay=0
                self.rain()
            self.emission_clock-=1/30
        for drop in self.active_characters-old_active:
            depth=random.choice((0.65, 1.0, 1.25))
            self.velocities[drop]=drop.motion.query_path('fall').speed*30*depth
            drop.animation.set_appearance(chr(92),
                colors=tte.ColorPair(fg=tte.Color('37516c' if depth<0.8 else '608fae' if depth==1 else '8abbd2')))
        drops=list(self.active_characters)
        for drop in drops:
            drop.motion.query_path('fall').speed=max(0.001,self.velocities.get(drop,24)*dt)
        before={drop:drop.motion.current_coord for drop in drops}
        for drop in drops:self.terminal.set_character_visibility(drop,is_visible=True)
        self.update()  # Upstream motion and completion callbacks.
        for drop in drops:
            a=before[drop];b=drop.motion.current_coord
            steps=max(abs(b.row-a.row),abs(b.column-a.column),1)
            hit=None
            for i in range(1,steps+1):
                coord=tte.Coord(round(a.column+(b.column-a.column)*i/steps),round(a.row+(b.row-a.row)*i/steps))
                if (coord.column,coord.row) in self.surfaces:
                    hit=coord;break
            if hit:
                drop.motion.deactivate_path();self.active_characters.discard(drop)
                self.terminal.set_character_visibility(drop,is_visible=False)
                if drop not in self.rain_drops:self.return_raindrop_to_pool(drop)
                self.splash(hit)
            elif drop not in self.active_characters:
                self.terminal.set_character_visibility(drop,is_visible=False)
        alive=[]
        for particle,age,origin,dx in self.splash_active:
            age+=dt
            life=0.42
            if age>=life:
                self.terminal.set_character_visibility(particle,is_visible=False)
                self.splash_pool.append(particle)
            else:
                progress=age/life
                fade=1-progress
                rgb=tuple(int(c*fade) for c in (142,200,226))
                tint=''.join(f'{c:02x}' for c in rgb)
                particle.animation.set_appearance("'" if progress<0.5 else '.', colors=tte.ColorPair(fg=tte.Color(tint)))
                particle.motion.set_coordinate(tte.Coord(origin.column+dx*round(1+3*progress),
                    origin.row+round(2.0*math.sin(math.pi*progress))))
                alive.append([particle,age,origin,dx])
        self.splash_active=alive
        return self.frame


class ClearViewRain(Thunderstorm):
    @property
    def _iterator_cls(self):return RainIterator


def create(width,height):
    effect=ClearViewRain(make_scene(width,height))
    effect.terminal_config.canvas_width=width;effect.terminal_config.canvas_height=height
    effect.terminal_config.ignore_terminal_dimensions=True
    effect.terminal_config.frame_rate=0
    effect.effect_config.raindrop_symbols=(chr(92),)
    return iter(effect)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        random.seed(4);effect=create(90,32);start=time.perf_counter()
        frames=[next(effect) for _ in range(440)]
        assert effect.impacts>0 and frames[0]!=frames[-1]
        assert make_scene(90,32).isascii()
        assert all(ch.is_visible for ch in effect.surfaces.values())
        print(f'PASS: upstream rain, {effect.impacts} impacts, fixed text/ground; {(time.perf_counter()-start)/440*1000:.1f} ms/frame.')
        return
    print('CLEAR VIEW | Chuva ASCII - motor TerminalTextEffects 0.15.0\nEnter para iniciar. Espaco pausa; Q sai.')
    input();old=termios.tcgetattr(sys.stdin);last_size=None;paused=False;last_tick=time.monotonic()
    try:
        tty.setcbreak(sys.stdin.fileno());sys.stdout.write('\033[?1049h\033[?25l\033[40m\033[2J')
        while True:
            begin=time.monotonic();size=shutil.get_terminal_size()
            if size!=last_size:
                width=max(10,min(160,size.columns-4));height=max(12,size.lines-3)
                effect=create(width,height);last_size=size;sys.stdout.write('\033[2J');frame=next(effect);last_tick=time.monotonic()
            now=time.monotonic();dt=now-last_tick;last_tick=now
            if not paused:frame=effect.advance(dt)
            pad=' '*max(0,(size.columns-width)//2)
            lines=frame.splitlines()
            sys.stdout.write('\033[?2026h\033[H'+'\n'.join(pad+line for line in lines)+
                '\033[0m\n\033[K  CLEAR VIEW | Chuva TTE 60 FPS (alvo) | Espaco: pausa | Q: sair\033[?2026l')
            sys.stdout.flush()
            if select.select([sys.stdin],[],[],max(0,1/60-(time.monotonic()-begin)))[0]:
                key=os.read(sys.stdin.fileno(),32).decode(errors='ignore').lower()
                if any(c in key for c in ('q','\x03','\x04')):break
                if ' ' in key:paused=not paused
    finally:
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old)
        sys.stdout.write('\033[?2026l\033[0m\033[?25h\033[?1049l');sys.stdout.flush()

if __name__=='__main__':main()
