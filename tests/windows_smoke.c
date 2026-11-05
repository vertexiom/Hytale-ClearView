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
/* Native Windows smoke test. No game files are modified. Run with DLL path.
 * Validates actual system forwarding, GLSL patching, live uniforms and F9 HUD. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

static int fail(const char *what){fprintf(stderr,"FAIL: %s (Win32 %lu)\n",what,(unsigned long)GetLastError());return 1;}
#define REQUIRE(x,message) do{if(!(x))return fail(message);}while(0)
#define LOAD(ret,name,args) ret (*name)args=(ret(*)args)getproc(#name);REQUIRE(name,#name)
static const char *vs="#version 410 core\nvoid main(){vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));gl_Position=vec4(p[gl_VertexID],0,1);}";
/* Own synthetic fixture, not copied from game resources. */
static const char *fs="#version 410 core\n#define FOG_INCLUDE\n"
"float computeDistantFogFactor(vec3 positionFromCamera, vec4 fogParams){float fogFactor=positionFromCamera.x*fogParams.x;return fogFactor;}\n"
"float computeDepthFogFactor(vec3 positionFromCamera, vec4 fogParams){float fogFactor=positionFromCamera.y*fogParams.y;return fogFactor;}\n"
"void computeMoodFog(vec3 positionFromCamera, vec3 cameraPosition,inout float fogThicknessFactor){fogThicknessFactor=positionFromCamera.z+cameraPosition.z;}\n"
"layout(location=0)out vec4 color;void main(){float mood=0;computeMoodFog(vec3(.5),vec3(0),mood);color=vec4(computeDistantFogFactor(vec3(.5),vec4(1)),mood,computeDepthFogFactor(vec3(.5),vec4(1)),1);}";
int main(void)
{
    int argc=0;wchar_t **argv=CommandLineToArgvW(GetCommandLineW(),&argc);
    if(argc!=2){fprintf(stderr,"Usage: clearview-smoke.exe FULL_PATH_TO_OPENGL32_DLL\n");return 2;}
    HMODULE proxy=LoadLibraryW(argv[1]);LocalFree(argv);REQUIRE(proxy,"load proxy DLL");
    PROC (WINAPI *getproc)(LPCSTR)=(PROC(WINAPI*)(LPCSTR))GetProcAddress(proxy,"wglGetProcAddress");
    HGLRC (WINAPI *create)(HDC)=(HGLRC(WINAPI*)(HDC))GetProcAddress(proxy,"wglCreateContext");
    BOOL (WINAPI *make)(HDC,HGLRC)=(BOOL(WINAPI*)(HDC,HGLRC))GetProcAddress(proxy,"wglMakeCurrent");
    BOOL (WINAPI *swap)(HDC)=(BOOL(WINAPI*)(HDC))GetProcAddress(proxy,"wglSwapBuffers");
    BOOL (WINAPI *remove_context)(HGLRC)=(BOOL(WINAPI*)(HGLRC))GetProcAddress(proxy,"wglDeleteContext");
    REQUIRE(getproc&&create&&make&&swap&&remove_context,"export dispatch");
    WNDCLASSW wc={0};wc.lpfnWndProc=DefWindowProcW;wc.hInstance=GetModuleHandleW(NULL);wc.lpszClassName=L"ClearViewSmoke";wc.style=CS_OWNDC;
    REQUIRE(RegisterClassW(&wc),"register test window");
    HWND window=CreateWindowW(wc.lpszClassName,L"ClearView smoke",WS_OVERLAPPEDWINDOW,0,0,800,600,NULL,NULL,wc.hInstance,NULL);
    REQUIRE(window,"create hidden test window");HDC dc=GetDC(window);REQUIRE(dc,"get DC");
    PIXELFORMATDESCRIPTOR pixel={0};pixel.nSize=sizeof pixel;pixel.nVersion=1;
    pixel.dwFlags=PFD_DRAW_TO_WINDOW|PFD_SUPPORT_OPENGL|PFD_DOUBLEBUFFER;pixel.iPixelType=PFD_TYPE_RGBA;pixel.cColorBits=32;pixel.cDepthBits=24;
    int format=ChoosePixelFormat(dc,&pixel);REQUIRE(format&&SetPixelFormat(dc,format,&pixel),"pixel format");
    HGLRC context=create(dc);REQUIRE(context&&make(dc,context),"forwarded WGL context creation");
    LOAD(const unsigned char*,glGetString,(unsigned));
    const char *renderer=(const char*)glGetString(0x1F01),*version=(const char*)glGetString(0x1F02);
    REQUIRE(renderer&&version,"GPU/driver identification");
    printf("Renderer: %s\nOpenGL: %s\n",renderer,version);
    int major=0,minor=0;
    REQUIRE(sscanf(version,"%d.%d",&major,&minor)==2 && (major>4 || (major==4 && minor>=1)),
            "OpenGL 4.1 is required by Hytale/ClearView; verify the installed GPU driver");
    LOAD(unsigned,glCreateShader,(unsigned));LOAD(void,glShaderSource,(unsigned,int,const char*const*,const int*));
    LOAD(void,glCompileShader,(unsigned));LOAD(void,glGetShaderiv,(unsigned,unsigned,int*));
    LOAD(void,glGetShaderInfoLog,(unsigned,int,int*,char*));
    LOAD(unsigned,glCreateProgram,(void));LOAD(void,glAttachShader,(unsigned,unsigned));
    LOAD(void,glLinkProgram,(unsigned));LOAD(void,glGetProgramiv,(unsigned,unsigned,int*));
    LOAD(void,glUseProgram,(unsigned));LOAD(int,glGetUniformLocation,(unsigned,const char*));
    LOAD(void,glGetUniformfv,(unsigned,int,float*));LOAD(unsigned,glGetError,(void));
    LOAD(void,glClearColor,(float,float,float,float));LOAD(void,glClear,(unsigned));
    /* Float argument forwarding passes through the generated x64 stub. */
    void (*direct_clear)(float,float,float,float)=(void(*)(float,float,float,float))GetProcAddress(proxy,"glClearColor");
    LOAD(void,glGetFloatv,(unsigned,float*));REQUIRE(direct_clear,"direct float forwarding export");
    direct_clear(.2f,.4f,.6f,.8f);float clear_value[4];glGetFloatv(0x0C22,clear_value);
    REQUIRE(fabsf(clear_value[0]-.2f)<.0001f && fabsf(clear_value[3]-.8f)<.0001f,"x64 float forwarding ABI");
    unsigned program=glCreateProgram();const char *sources[]={vs,fs};
    for(int i=0;i<2;++i){
        unsigned shader=glCreateShader(i?0x8B30:0x8B31);glShaderSource(shader,1,&sources[i],NULL);glCompileShader(shader);
        int ok=0;glGetShaderiv(shader,0x8B81,&ok);
        if(!ok){char log[4096];glGetShaderInfoLog(shader,sizeof log,NULL,log);fprintf(stderr,"%s\n",log);return fail("shader compilation");}
        glAttachShader(program,shader);
    }
    glLinkProgram(program);int linked=0;glGetProgramiv(program,0x8B82,&linked);REQUIRE(linked,"link patched program");
    glUseProgram(program);const char *names[]={"cvOriginalDistanceFog","cvOriginalMoodFog","cvOriginalDepthFog"};
    int locations[3];float values[3];
    for(int i=0;i<3;++i){locations[i]=glGetUniformLocation(program,names[i]);REQUIRE(locations[i]>=0,"all three fog controls are active");glGetUniformfv(program,locations[i],&values[i]);}
    printf("Initial fog controls: %.2f %.2f %.2f\n",values[0],values[1],values[2]);
    glClearColor(.1f,.15f,.2f,1);glClear(0x4000);REQUIRE(swap(dc),"presentation wrapper");
    SendMessageW(window,WM_KEYDOWN,VK_F9,0);SendMessageW(window,WM_KEYUP,VK_F9,0);
    SendMessageW(window,WM_KEYDOWN,'R',0);SendMessageW(window,WM_KEYUP,'R',0);
    glUseProgram(program);
    for(int i=0;i<3;++i){glGetUniformfv(program,locations[i],&values[i]);REQUIRE(fabsf(values[i]-1)<.001f,"R preset updates live uniforms");}
    SendMessageW(window,WM_KEYDOWN,VK_DOWN,0);SendMessageW(window,WM_KEYUP,VK_DOWN,0);
    SendMessageW(window,WM_KEYDOWN,VK_LEFT,0);SendMessageW(window,WM_KEYUP,VK_LEFT,0);
    glUseProgram(program);glGetUniformfv(program,locations[1],&values[1]);REQUIRE(fabsf(values[1]-.95f)<.001f,"independent slider control");
    REQUIRE(swap(dc),"HUD presentation");REQUIRE(glGetError()==0,"HUD preserves a valid GL state");
    SendMessageW(window,WM_KEYDOWN,VK_F9,0);SendMessageW(window,WM_KEYUP,VK_F9,0);
    REQUIRE(make(NULL,NULL)&&remove_context(context),"context cleanup");
    DestroyWindow(window);
    puts("PASS: WGL forwarding, x64 ABI, shader controls, F9 input and HUD. This does NOT certify Hytale gameplay.");
    return 0;
}
