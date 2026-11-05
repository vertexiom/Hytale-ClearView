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
#ifndef CLEARVIEW_PANEL_H
#define CLEARVIEW_PANEL_H
#ifdef _WIN32
#include "windows/panel_win.h"
#else
#include <cairo/cairo.h>
#include <cairo/cairo-ft.h>
#include <ft2build.h>
#include FT_FREETYPE_H
#include "hud_fonts.h"
#include <math.h>
#include <stdio.h>
typedef cairo_surface_t cv_panel_surface;
static cairo_font_face_t *cv_fonts[2];
static int cv_fonts_init(void)
{
    static FT_Library library;
    static FT_Face faces[2];
    static int attempted;
    if(attempted)return cv_fonts[0] && cv_fonts[1];
    attempted=1;
    if(FT_Init_FreeType(&library))return 0;
    if(FT_New_Memory_Face(library,cv_font_regular,sizeof cv_font_regular,0,&faces[0]) ||
       FT_New_Memory_Face(library,cv_font_semibold,sizeof cv_font_semibold,0,&faces[1]))return 0;
    for(int i=0;i<2;++i)cv_fonts[i]=cairo_ft_font_face_create_for_ft_face(faces[i],0);
    return cairo_font_face_status(cv_fonts[0])==CAIRO_STATUS_SUCCESS && cairo_font_face_status(cv_fonts[1])==CAIRO_STATUS_SUCCESS;
}
static void cv_text_draw(cv_panel_surface *p,double x,double y,int size,int bold,const char *text,int right)
{
    cairo_t *cr=cairo_create(p);
    if(cv_fonts_init())cairo_set_font_face(cr,cv_fonts[bold!=0]);
    else cairo_select_font_face(cr,"sans-serif",CAIRO_FONT_SLANT_NORMAL,bold?CAIRO_FONT_WEIGHT_BOLD:CAIRO_FONT_WEIGHT_NORMAL);
    cairo_set_font_size(cr,size);
    cairo_set_source_rgb(cr,1,1,1);
    if(right){cairo_text_extents_t ext;cairo_text_extents(cr,text,&ext);x-=ext.x_advance;}
    cairo_move_to(cr,x,y);cairo_show_text(cr,text);cairo_destroy(cr);
}
static void cv_text(cv_panel_surface *p,double x,double y,int size,int bold,const char *s){cv_text_draw(p,x,y,size,bold,s,0);}
static void cv_text_right(cv_panel_surface *p,double x,double y,int size,int bold,const char *s){cv_text_draw(p,x,y,size,bold,s,1);}
#include "panel_layout.h"
static cv_panel_surface *cv_panel(const float fog[3],int selected,int saved)
{
    cv_panel_surface *p=cairo_image_surface_create(CAIRO_FORMAT_ARGB32,CV_PANEL_W,CV_PANEL_H);
    cv_panel_text(p,fog,selected,saved);cairo_surface_flush(p);return p;
}
static int cv_panel_ok(cv_panel_surface *p){return p && cairo_surface_status(p)==CAIRO_STATUS_SUCCESS;}
static unsigned char *cv_panel_data(cv_panel_surface *p){return cairo_image_surface_get_data(p);}
static void cv_panel_free(cv_panel_surface *p){if(p)cairo_surface_destroy(p);}
#endif
#endif
