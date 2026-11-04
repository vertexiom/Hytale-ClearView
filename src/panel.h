#ifndef CLEARVIEW_PANEL_H
#define CLEARVIEW_PANEL_H
#ifdef _WIN32
#include "windows/panel_win.h"
#else
#include <cairo/cairo.h>
#include <math.h>
#include <stdio.h>
#define CV_PANEL_W 460
#define CV_PANEL_H 414

static void cv_text(cairo_t *cr, double x, double y, double size,
                    double r, double g, double b, const char *text)
{
    cairo_set_source_rgb(cr,r,g,b);
    cairo_set_font_size(cr,size);
    cairo_move_to(cr,x,y);
    cairo_show_text(cr,text);
}

/* Also used by the preview test; UI text never contains implementation details. */
static cairo_surface_t *cv_panel(const float fog[3], int selected, int saved)
{
    cairo_surface_t *surface=cairo_image_surface_create(CAIRO_FORMAT_ARGB32,CV_PANEL_W,CV_PANEL_H);
    cairo_t *cr=cairo_create(surface);
    cairo_set_source_rgba(cr,0.035,0.052,0.075,0.97);
    cairo_paint(cr);
    cairo_set_source_rgb(cr,0.32,0.85,0.72);
    cairo_rectangle(cr,0,0,CV_PANEL_W,3); cairo_fill(cr);
    cairo_select_font_face(cr,"DejaVu Sans",CAIRO_FONT_SLANT_NORMAL,CAIRO_FONT_WEIGHT_BOLD);
    cv_text(cr,24,37,21,0.94,0.97,1,"ClearView");
    cairo_select_font_face(cr,"DejaVu Sans",CAIRO_FONT_SLANT_NORMAL,CAIRO_FONT_WEIGHT_NORMAL);
    cv_text(cr,24,61,12,0.60,0.69,0.78,"Controle de neblina");
    cv_text(cr,339,36,11,0.60,0.69,0.78,"F9  fechar");
    const char *labels[]={"Distância", "Atmosfera", "Profundidade"};
    const char *hints[]={"Horizonte e terrenos distantes", "Névoa de clima e ambiente", "Visão em profundidade, incluindo água"};
    for (int i=0;i<3;++i) {
        double y=94+i*83;
        if (i==selected) {
            cairo_set_source_rgb(cr,0.075,0.13,0.16);
            cairo_rectangle(cr,14,y-18,432,76); cairo_fill(cr);
        }
        cv_text(cr,25,y,15,0.90,0.94,0.98,labels[i]);
        char percent[24]; snprintf(percent,sizeof percent,"%.0f%%",fog[i]*100);
        cv_text(cr,388,y,15,0.40,0.91,0.78,percent);
        cairo_set_source_rgb(cr,0.17,0.23,0.28);
        cairo_rectangle(cr,25,y+13,410,5); cairo_fill(cr);
        cairo_set_source_rgb(cr,0.32,0.85,0.72);
        cairo_rectangle(cr,25,y+13,410*fog[i],5); cairo_fill(cr);
        cairo_arc(cr,25+410*fog[i],y+15.5,5,0,6.2831853); cairo_fill(cr);
        cv_text(cr,25,y+40,11,0.59,0.68,0.76,hints[i]);
    }
    cv_text(cr,24,337,11,0.69,0.76,0.83,"0% sem neblina  ·  100% original do jogo");
    cv_text(cr,24,361,11,0.85,0.90,0.95,"↑ ↓ selecionar     ← → ajustar em 5%");
    cv_text(cr,24,384,11,0.66,0.75,0.81,"V  visão limpa     R  restaurar original     Esc  fechar");
    cv_text(cr,24,404,10,saved?0.38:1.0,saved?0.72:0.50,saved?0.62:0.45,
            saved?"Ajustes salvos automaticamente":"Não foi possível salvar; ajustes valem nesta sessão");
    cairo_destroy(cr); cairo_surface_flush(surface);
    return surface;
}
typedef cairo_surface_t cv_panel_surface;
static int cv_panel_ok(cv_panel_surface *p) {return cairo_surface_status(p)==CAIRO_STATUS_SUCCESS;}
static unsigned char *cv_panel_data(cv_panel_surface *p) {return cairo_image_surface_get_data(p);}
static void cv_panel_free(cv_panel_surface *p) {cairo_surface_destroy(p);}
#endif /* platform */
#endif
