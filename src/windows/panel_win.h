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
#ifndef CLEARVIEW_PANEL_WIN_H
#define CLEARVIEW_PANEL_WIN_H
#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "hud_fonts.h"
typedef struct {HDC dc;HBITMAP bitmap;HGDIOBJ old;unsigned char *pixels;} cv_panel_surface;
static void cv_text_draw(cv_panel_surface *p,int x,int y,int size,int bold,const char *text,int right)
{
    static int fonts_registered;
    if(!fonts_registered){
        DWORD count=0;
        AddFontMemResourceEx((void*)cv_font_regular,sizeof cv_font_regular,NULL,&count);
        AddFontMemResourceEx((void*)cv_font_semibold,sizeof cv_font_semibold,NULL,&count);
        fonts_registered=1;
    }
    wchar_t wide[160];
    if(!MultiByteToWideChar(CP_UTF8,0,text,-1,wide,160))return;
    HFONT font=CreateFontW(-size,0,0,0,bold?FW_SEMIBOLD:FW_NORMAL,FALSE,FALSE,FALSE,
        DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,ANTIALIASED_QUALITY,DEFAULT_PITCH,L"Inter");
    HGDIOBJ old=font?SelectObject(p->dc,font):NULL;
    SetTextColor(p->dc,RGB(255,255,255));SetBkMode(p->dc,TRANSPARENT);
    SetTextAlign(p->dc,TA_BASELINE|(right?TA_RIGHT:TA_LEFT));
    TextOutW(p->dc,x,y,wide,(int)wcslen(wide));
    if(font){SelectObject(p->dc,old);DeleteObject(font);}
}
static void cv_text(cv_panel_surface *p,int x,int y,int size,int bold,const char *s){cv_text_draw(p,x,y,size,bold,s,0);}
static void cv_text_right(cv_panel_surface *p,int x,int y,int size,int bold,const char *s){cv_text_draw(p,x,y,size,bold,s,1);}
#include "../panel_layout.h"
static void cv_panel_free(cv_panel_surface *p)
{
    if(!p)return;
    if(p->dc && p->old)SelectObject(p->dc,p->old);
    if(p->bitmap)DeleteObject(p->bitmap);
    if(p->dc)DeleteDC(p->dc);
    free(p);
}
static cv_panel_surface *cv_panel(const float fog[3],int selected,int saved)
{
    cv_panel_surface *p=calloc(1,sizeof *p);if(!p)return NULL;
    BITMAPINFO info={0};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    info.bmiHeader.biWidth=CV_PANEL_W;info.bmiHeader.biHeight=-CV_PANEL_H;
    info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
    p->dc=CreateCompatibleDC(NULL);if(!p->dc){cv_panel_free(p);return NULL;}
    p->bitmap=CreateDIBSection(p->dc,&info,DIB_RGB_COLORS,(void**)&p->pixels,NULL,0);
    if(!p->bitmap){cv_panel_free(p);return NULL;}
    p->old=SelectObject(p->dc,p->bitmap);
    memset(p->pixels,0,CV_PANEL_W*CV_PANEL_H*4);
    cv_panel_text(p,fog,selected,saved);GdiFlush();
    /* GDI grayscale white-on-black coverage -> premultiplied white mask. */
    for(int i=0;i<CV_PANEL_W*CV_PANEL_H;++i)p->pixels[i*4+3]=p->pixels[i*4];
    return p;
}
static int cv_panel_ok(cv_panel_surface *p){return p && p->pixels;}
static unsigned char *cv_panel_data(cv_panel_surface *p){return p->pixels;}
#endif
