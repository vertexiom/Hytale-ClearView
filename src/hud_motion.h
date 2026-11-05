/*
 * Copyright (C) 2026 vertexiom
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This file is part of Hytale ClearView.
 * Hytale ClearView is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version. See LICENSE for details.
 */
#ifndef CLEARVIEW_HUD_MOTION_H
#define CLEARVIEW_HUD_MOTION_H
/* Pure state machine: no allocations, worker, timers or texture rasterization.
 * Caller supplies monotonic seconds, and only calls while the HUD is visible. */
typedef struct {float value,from,target;double start;} cv_motion_channel;
typedef struct {cv_motion_channel c[6];int initialized,active;double last;} cv_motion;
static void cv_motion_step(cv_motion *m,const float fog[3],int selected,double now,int reduced)
{
    for(int i=0;i<6;++i){
        float target=i<3?fog[i]:(float)(i-3==selected);
        cv_motion_channel *c=&m->c[i];
        if(!m->initialized || reduced){c->value=c->from=c->target=target;c->start=now;}
        else if(c->target!=target){c->from=c->value;c->target=target;c->start=now;m->active=1;}
    }
    if(!m->initialized || reduced){m->initialized=1;m->active=0;m->last=now;return;}
    if(!m->active || now-m->last<1.0/30.0)return;
    m->last=now;m->active=0;
    for(int i=0;i<6;++i){
        cv_motion_channel *c=&m->c[i];
        double t=(now-c->start)/.120;
        if(t>=1)c->value=c->target;
        else if(c->value!=c->target){
            if(t<0)t=0;
            float remaining=(float)(1-t);
            c->value=c->from+(c->target-c->from)*(1-remaining*remaining*remaining);
            m->active=1;
        }
    }
}
#endif
