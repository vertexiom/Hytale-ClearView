# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic tests of native HUD timing, retargeting and reduced motion."""
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=r'''
#include <assert.h>
#include <math.h>
#include "hud_motion.h"
int main(void){
 cv_motion m={0};float fog[3]={.75f,1,1};
 cv_motion_step(&m,fog,0,1,0);
 assert(!m.active && m.c[0].value==.75f && m.c[3].value==1);
 fog[0]=0;cv_motion_step(&m,fog,1,1.001,0);
 assert(m.active && m.c[0].value==.75f); /* logic immediate, visual capped */
 cv_motion_step(&m,fog,1,1.020,0);assert(m.c[0].value==.75f);
 cv_motion_step(&m,fog,1,1.040,0);
 assert(m.c[0].value>0 && m.c[0].value<.75f);
 assert(m.c[3].value>0 && m.c[4].value>0);
 float displayed=m.c[0].value;
 fog[0]=1;cv_motion_step(&m,fog,2,1.041,0);
 assert(m.c[0].from==displayed && m.c[0].target==1);
 double start=m.c[0].start;
 cv_motion_step(&m,fog,2,1.050,0);assert(m.c[0].start==start);
 cv_motion_step(&m,fog,2,1.200,0);
 assert(!m.active && m.c[0].value==1 && m.c[5].value==1 && m.c[3].value==0);
 double idle=m.last;cv_motion_step(&m,fog,2,99,0);assert(m.last==idle);
 fog[2]=0;cv_motion_step(&m,fog,0,100,1);
 assert(!m.active && m.c[2].value==0 && m.c[3].value==1);
 m.initialized=m.active=0;fog[0]=.2f;cv_motion_step(&m,fog,1,101,0);
 assert(!m.active && m.c[0].value==.2f && m.c[4].value==1);
 return 0;
}
'''
with tempfile.TemporaryDirectory() as temp:
    source=Path(temp)/'motion.c';binary=Path(temp)/'motion';source.write_text(SOURCE)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),str(source),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('PASS: 120 ms transitions, 30 Hz cap, retargeting, idle, reopen and reduced motion.')
