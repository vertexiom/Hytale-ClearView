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
#ifndef CLEARVIEW_PANEL_LAYOUT_H
#define CLEARVIEW_PANEL_LAYOUT_H
#define CV_PANEL_W 460
#define CV_PANEL_H 474
/* Baselines and coordinates mirror the approved 460 x 474 keyboard-only HUD.
 * Render white coverage; the compositor applies semantic colors. */
static void cv_panel_text(cv_panel_surface *p,const float fog[3],int selected,int saved)
{
    cv_text(p,34,40,20,1,"ClearView");
    cv_text(p,34,59,12,0,"Controle de neblina");
    cv_text(p,350,37,11,1,"F9"); cv_text(p,378,38,12,0,"fechar");
    const char *labels[]={"Distância","Atmosfera","Profundidade"};
    const char *hints[]={"Horizonte e terrenos distantes","Névoa de clima e ambiente","Visão em profundidade, incluindo água"};
    for(int i=0;i<3;++i){
        int y=100+i*86;
        cv_text(p,34,y,15,i==selected,labels[i]);
        char percent[24];snprintf(percent,sizeof percent,"%.0f%%",fog[i]*100);
        cv_text_right(p,426,y,15,i==selected,percent);
        cv_text(p,34,y+38,12,0,hints[i]);
    }
    cv_text(p,34,352,12,0,"0% sem neblina  ·  100% original do jogo");
    cv_text(p,40,394,11,1,"↑"); cv_text(p,63,394,11,1,"↓");
    cv_text(p,88,395,12,0,"selecionar");
    cv_text(p,178,394,11,1,"←"); cv_text(p,202,394,11,1,"→");
    cv_text(p,229,395,12,0,"ajustar em 5%");
    cv_text(p,40,423,11,1,"V"); cv_text(p,63,424,12,0,"visão limpa");
    cv_text(p,157,423,11,1,"R"); cv_text(p,181,424,12,0,"restaurar original");
    cv_text(p,318,423,11,1,"Esc"); cv_text(p,351,424,12,0,"fechar");
    cv_text(p,47,454,saved?11:10,0,saved?"Ajustes salvos automaticamente":"Não foi possível salvar; ajustes valem nesta sessão");
}
#endif
