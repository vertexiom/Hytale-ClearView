#ifndef CLEARVIEW_PANEL_WIN_H
#define CLEARVIEW_PANEL_WIN_H
#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#define CV_PANEL_W 460
#define CV_PANEL_H 414

typedef struct {HDC dc;HBITMAP bitmap;HGDIOBJ old;unsigned char *pixels;} cv_panel_surface;
static void cv_rect(HDC dc,int x,int y,int w,int h,COLORREF color)
{
    RECT r={x,y,x+w,y+h};HBRUSH brush=CreateSolidBrush(color);
    if(brush){FillRect(dc,&r,brush);DeleteObject(brush);}
}
static void cv_text_win(HDC dc,int x,int y,int size,COLORREF color,const wchar_t *text,int bold)
{
    HFONT font=CreateFontW(-size,0,0,0,bold?FW_BOLD:FW_NORMAL,FALSE,FALSE,FALSE,
                          DEFAULT_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,
                          ANTIALIASED_QUALITY,DEFAULT_PITCH,L"Segoe UI");
    HGDIOBJ old=font?SelectObject(dc,font):NULL;
    SetTextColor(dc,color);SetBkMode(dc,TRANSPARENT);
    TextOutW(dc,x,y-size,text,(int)wcslen(text));
    if(font){SelectObject(dc,old);DeleteObject(font);}
}
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
    p->dc=CreateCompatibleDC(NULL);
    if(!p->dc){cv_panel_free(p);return NULL;}
    p->bitmap=CreateDIBSection(p->dc,&info,DIB_RGB_COLORS,(void**)&p->pixels,NULL,0);
    if(!p->bitmap){cv_panel_free(p);return NULL;}
    p->old=SelectObject(p->dc,p->bitmap);
    cv_rect(p->dc,0,0,CV_PANEL_W,CV_PANEL_H,RGB(9,13,19));
    cv_rect(p->dc,0,0,CV_PANEL_W,3,RGB(82,217,184));
    cv_text_win(p->dc,24,37,21,RGB(240,247,255),L"ClearView",1);
    cv_text_win(p->dc,24,61,12,RGB(153,176,199),L"Controle de neblina",0);
    cv_text_win(p->dc,339,36,11,RGB(153,176,199),L"F9  fechar",0);
    const wchar_t *labels[]={L"Distância",L"Atmosfera",L"Profundidade"};
    const wchar_t *hints[]={L"Horizonte e terrenos distantes",L"Névoa de clima e ambiente",L"Visão em profundidade, incluindo água"};
    for(int i=0;i<3;++i){
        int y=94+i*83;
        if(i==selected)cv_rect(p->dc,14,y-18,432,76,RGB(19,33,41));
        cv_text_win(p->dc,25,y,15,RGB(230,240,250),labels[i],0);
        wchar_t percent[24];swprintf(percent,24,L"%.0f%%",fog[i]*100);
        cv_text_win(p->dc,388,y,15,RGB(102,232,199),percent,0);
        cv_rect(p->dc,25,y+13,410,5,RGB(43,59,71));
        cv_rect(p->dc,25,y+13,(int)(410*fog[i]),5,RGB(82,217,184));
        int knob=25+(int)(410*fog[i]);
        cv_rect(p->dc,knob-3,y+10,7,11,RGB(82,217,184));
        cv_text_win(p->dc,25,y+40,11,RGB(150,173,194),hints[i],0);
    }
    cv_text_win(p->dc,24,337,11,RGB(176,194,212),L"0% sem neblina  ·  100% original do jogo",0);
    cv_text_win(p->dc,24,361,11,RGB(217,230,242),L"↑ ↓ selecionar     ← → ajustar em 5%",0);
    cv_text_win(p->dc,24,384,11,RGB(168,191,207),L"V  visão limpa     R  restaurar original     Esc  fechar",0);
    cv_text_win(p->dc,24,404,10,saved?RGB(97,184,158):RGB(255,128,115),
                saved?L"Ajustes salvos automaticamente":L"Não foi possível salvar; ajustes valem nesta sessão",0);
    GdiFlush();
    for(int i=0;i<CV_PANEL_W*CV_PANEL_H;++i)p->pixels[i*4+3]=255;
    return p;
}
static int cv_panel_ok(cv_panel_surface *p){return p && p->pixels;}
static unsigned char *cv_panel_data(cv_panel_surface *p){return p->pixels;}
#endif
