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
#define WIN32_LEAN_AND_MEAN
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0a00
#endif
#include <windows.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <wchar.h>
#include "../patch.h"
#include "exports_table.h"

#define CV_PATH_CAP 32768
static HMODULE self_module,system_gl;
static INIT_ONCE init_once=INIT_ONCE_STATIC_INIT;
static CRITICAL_SECTION state_lock;
static wchar_t directory[CV_PATH_CAP];
static float fog_amount[3]={0,1,1};
static int panel_open,selected_fog,settings_saved=1;
static HWND game_window;
static WNDPROC previous_proc;
static HGLRC overlay_context;
static bool captured_keys[256];
static PROC (WINAPI *system_getproc)(LPCSTR);
static HGLRC (WINAPI *system_context)(void);
static BOOL (WINAPI *system_swap)(HDC);
static BOOL (WINAPI *system_delete)(HGLRC);
typedef void (*Proc)(void);
typedef Proc (*GetProc)(const char *);
typedef void (*ShaderSource)(unsigned,int,const char*const*,const int*);
/* Ownership is checked by the installer before replacing/removing a DLL. */
__attribute__((used)) static const char owner[]="HYTALE_CLEARVIEW_WINDOWS_PROXY_V1";

static int path_for(wchar_t *out,const wchar_t *name)
{
    if(!directory[0])return 0;
    int n=swprintf(out,CV_PATH_CAP,L"%ls\\.clearview\\%ls",directory,name);
    return n>0 && n<CV_PATH_CAP;
}
static void record(const char *message,int value)
{
    wchar_t path[CV_PATH_CAP];if(!path_for(path,L"hook.log"))return;
    FILE *f=_wfopen(path,L"a");
    if(f){SYSTEMTIME t;GetLocalTime(&t);fprintf(f,"%04u-%02u-%02u %02u:%02u:%02u ClearView: %s (%d)\n",
        t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,message,value);fclose(f);}
}
static Proc win_getproc(const char *name)
{
    if(!name || !system_gl)return NULL;
    PROC p=system_getproc?system_getproc(name):NULL;
    if(!p || (uintptr_t)p<=3 || (uintptr_t)p==UINTPTR_MAX)p=GetProcAddress(system_gl,name);
    return (Proc)p;
}
static GetProc original_getproc=win_getproc;
#include "../overlay.h"

static void save_settings(void)
{
    wchar_t path[CV_PATH_CAP],temp[CV_PATH_CAP];settings_saved=0;overlay_dirty=1;
    if(!path_for(path,L"settings"))return;
    int n=swprintf(temp,CV_PATH_CAP,L"%ls.%lu.%llu.tmp",path,(unsigned long)GetCurrentProcessId(),(unsigned long long)GetTickCount64());
    if(n<=0 || n>=CV_PATH_CAP)return;
    HANDLE file=CreateFileW(temp,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE)return;
    char data[100];int bytes=snprintf(data,sizeof data,"%.3f %.3f %.3f\n",fog_amount[0],fog_amount[1],fog_amount[2]);
    DWORD written=0;BOOL ok=WriteFile(file,data,(DWORD)bytes,&written,NULL) && written==(DWORD)bytes;
    if(ok)ok=FlushFileBuffers(file);CloseHandle(file);
    if(ok && MoveFileExW(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))settings_saved=1;
    else DeleteFileW(temp);
}
__declspec(noreturn) static void missing_export(void)
{
    record("required system OpenGL export unavailable",0);
    RaiseException(ERROR_PROC_NOT_FOUND,EXCEPTION_NONCONTINUABLE,0,NULL);
    TerminateProcess(GetCurrentProcess(),ERROR_PROC_NOT_FOUND);
    __builtin_unreachable();
}
static BOOL CALLBACK initialize(PINIT_ONCE once,PVOID parameter,PVOID *context)
{
    (void)once;(void)parameter;(void)context;
    InitializeCriticalSection(&state_lock);
    DWORD length=GetModuleFileNameW(self_module,directory,CV_PATH_CAP);
    if(!length || length>=CV_PATH_CAP)directory[0]=0;
    wchar_t *slash=wcsrchr(directory,L'\\');if(slash)*slash=0;else directory[0]=0;
    wchar_t path[CV_PATH_CAP];
    if(directory[0] && swprintf(path,CV_PATH_CAP,L"%ls\\.clearview",directory)>0)CreateDirectoryW(path,NULL);
    UINT size=GetSystemDirectoryW(path,CV_PATH_CAP);
    if(size && size+14<CV_PATH_CAP){wcscat(path,L"\\opengl32.dll");system_gl=LoadLibraryExW(path,NULL,LOAD_LIBRARY_SEARCH_SYSTEM32);}
    for(unsigned i=0;i<CV_EXPORT_COUNT;++i){
        cv_export_targets[i]=system_gl?(void*)GetProcAddress(system_gl,cv_export_names[i]):NULL;
        if(!cv_export_targets[i])cv_export_targets[i]=(void*)missing_export;
    }
    if(system_gl){
        system_getproc=(PROC(WINAPI*)(LPCSTR))GetProcAddress(system_gl,"wglGetProcAddress");
        system_swap=(BOOL(WINAPI*)(HDC))GetProcAddress(system_gl,"wglSwapBuffers");
        system_context=(HGLRC(WINAPI*)(void))GetProcAddress(system_gl,"wglGetCurrentContext");
        system_delete=(BOOL(WINAPI*)(HGLRC))GetProcAddress(system_gl,"wglDeleteContext");
    }
    if(path_for(path,L"settings")){
        FILE *file=_wfopen(path,L"r");
        if(file){float a,b,c;
            if(fscanf(file,"%f %f %f",&a,&b,&c)==3 && isfinite(a) && isfinite(b) && isfinite(c) &&
                a>=0 && a<=1 && b>=0 && b<=1 && c>=0 && c<=1){fog_amount[0]=a;fog_amount[1]=b;fog_amount[2]=c;}
            fclose(file);
        }
    }
    record(system_gl?"Windows x64 preview loaded; F9 opens HUD":"ERROR loading system OpenGL",0);
    return TRUE;
}
void cv_win_initialize(void)
{
    if(!InitOnceExecuteOnce(&init_once,initialize,NULL,NULL))missing_export();
}
static void read_amounts(float out[3])
{
    EnterCriticalSection(&state_lock);memcpy(out,fog_amount,sizeof fog_amount);LeaveCriticalSection(&state_lock);
}
#define CV_RUNTIME_INIT() cv_win_initialize()
#define CV_THREAD_LOCAL _Thread_local
#define CV_READ_AMOUNTS(out) read_amounts(out)
#include "../runtime.h"

static _Thread_local HGLRC dispatch_context;
static _Thread_local int graphics_supported;
static void check_context(void)
{
    HGLRC context=system_context?system_context():NULL;
    if(context!=dispatch_context){
        memset(programs,0,sizeof programs);real_use=NULL;real_link=NULL;real_delete=NULL;real_location=NULL;real_uniform=NULL;
        dispatch_context=context;graphics_supported=0;
        if(context){
            const unsigned char *(*getstring)(unsigned)=(const unsigned char*(*)(unsigned))original_getproc("glGetString");
            if(getstring){
                const char *version=(const char*)getstring(0x1F02);
                const char *renderer=(const char*)getstring(0x1F01);
                const char *vendor=(const char*)getstring(0x1F00);
                int major=0,minor=0;
                if(version)sscanf(version,"%d.%d",&major,&minor);
                const char *glsl=major>=2?(const char*)getstring(0x8B8C):NULL;
                char message[1024];
                snprintf(message,sizeof message,"GPU=%s; vendor=%s; OpenGL=%s; GLSL=%s",
                         renderer?renderer:"unknown",vendor?vendor:"unknown",version?version:"unknown",glsl?glsl:"unknown");
                record(message,0);
                graphics_supported=major>4 || (major==4 && minor>=1);
            }
            if(!graphics_supported)record("OpenGL 4.1 not available; ClearView leaves shaders unchanged and HUD disabled",0);
        }
    }
}
static void win_shader_source(unsigned shader,int count,const char*const*source,const int*lengths)
{
    check_context();
    if(graphics_supported)patched_source(shader,count,source,lengths);
    else {
        ShaderSource real=(ShaderSource)original_getproc("glShaderSource");
        if(real)real(shader,count,source,lengths);
    }
}
static void win_use(unsigned program){
    check_context();
    if(graphics_supported)use_program(program);
    else {void(*real)(unsigned)=(void(*)(unsigned))original_getproc("glUseProgram");if(real)real(program);}
}
static void win_link(unsigned program){check_context();link_program(program);}
static void win_delete(unsigned program){check_context();delete_program(program);}

static LRESULT CALLBACK panel_proc(HWND window,UINT message,WPARAM key,LPARAM info)
{
    if(message==WM_KILLFOCUS){EnterCriticalSection(&state_lock);panel_open=0;memset(captured_keys,0,sizeof captured_keys);LeaveCriticalSection(&state_lock);}
    if((message==WM_KEYDOWN || message==WM_KEYUP) && key<256){
        int consumed=0,changed=0;
        EnterCriticalSection(&state_lock);
        if(message==WM_KEYUP){consumed=captured_keys[key];captured_keys[key]=false;}
        else if(key==VK_F9){if(!(info&(1LL<<30)))panel_open=!panel_open;consumed=1;overlay_dirty=1;}
        else if(panel_open){
            consumed=1;
            switch(key){
            case VK_ESCAPE:panel_open=0;break;
            case VK_UP:selected_fog=(selected_fog+2)%3;break;
            case VK_DOWN:selected_fog=(selected_fog+1)%3;break;
            case VK_LEFT:fog_amount[selected_fog]=fmaxf(0,fog_amount[selected_fog]-.05f);changed=1;break;
            case VK_RIGHT:fog_amount[selected_fog]=fminf(1,fog_amount[selected_fog]+.05f);changed=1;break;
            case 'V':fog_amount[0]=0;fog_amount[1]=.2f;fog_amount[2]=1;changed=1;break;
            case 'R':fog_amount[0]=fog_amount[1]=fog_amount[2]=1;changed=1;break;
            default:consumed=0;break;
            }
            if(consumed)overlay_dirty=1;
        }
        if(message==WM_KEYDOWN && consumed)captured_keys[key]=true;
        if(changed)save_settings();
        LeaveCriticalSection(&state_lock);
        if(consumed)return 0;
    }
    if(message==WM_CHAR){
        EnterCriticalSection(&state_lock);int swallow=panel_open && (key=='v'||key=='V'||key=='r'||key=='R');LeaveCriticalSection(&state_lock);
        if(swallow)return 0;
    }
    WNDPROC next=previous_proc;
    if(message==WM_NCDESTROY && window==game_window){
        SetWindowLongPtrW(window,GWLP_WNDPROC,(LONG_PTR)next);game_window=NULL;previous_proc=NULL;panel_open=0;
    }
    return next?CallWindowProcW(next,window,message,key,info):DefWindowProcW(window,message,key,info);
}
PROC WINAPI cv_wglGetProcAddress(LPCSTR name)
{
    cv_win_initialize();Proc result=original_getproc(name);
    if(result && name){
        if(!strcmp(name,"glShaderSource"))return (PROC)win_shader_source;
        if(!strcmp(name,"glUseProgram"))return (PROC)win_use;
        if(!strcmp(name,"glLinkProgram"))return (PROC)win_link;
        if(!strcmp(name,"glDeleteProgram"))return (PROC)win_delete;
    }
    return (PROC)result;
}
BOOL WINAPI cv_wglSwapBuffers(HDC dc)
{
    cv_win_initialize();if(!system_swap)return FALSE;
    check_context();
    if(!graphics_supported)return system_swap(dc);
    HWND window=WindowFromDC(dc);
    if(window && (!game_window || !IsWindow(game_window))){
        SetLastError(0);
        WNDPROC old=(WNDPROC)SetWindowLongPtrW(window,GWLP_WNDPROC,(LONG_PTR)panel_proc);
        if(old){previous_proc=old;game_window=window;record("presentation hook and F9 input active",0);}
        else record("could not attach HUD keyboard handler",(int)GetLastError());
    }
    if(window==game_window){
        EnterCriticalSection(&state_lock);
        if(panel_open){
            HGLRC context=system_context?system_context():NULL;
            if(context!=overlay_context){overlay_context=context;overlay_ready=overlay_failed=0;overlay_dirty=1;overlay_program=overlay_vao=overlay_texture=0;}
            RECT rect;if(context && GetClientRect(window,&rect))overlay_draw(rect.right,rect.bottom,fog_amount,selected_fog,settings_saved);
        }
        LeaveCriticalSection(&state_lock);
    }
    return system_swap(dc);
}
BOOL WINAPI cv_wglDeleteContext(HGLRC context)
{
    cv_win_initialize();if(!system_delete)return FALSE;
    BOOL result=system_delete(context);
    if(result){
        if(dispatch_context==context){dispatch_context=NULL;memset(programs,0,sizeof programs);real_use=NULL;real_link=NULL;real_delete=NULL;real_location=NULL;real_uniform=NULL;}
        EnterCriticalSection(&state_lock);
        if(overlay_context==context){overlay_context=NULL;overlay_program=overlay_vao=overlay_texture=0;overlay_ready=overlay_failed=0;overlay_dirty=1;}
        LeaveCriticalSection(&state_lock);
    }
    return result;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID reserved)
{
    (void)reserved;
    if(reason==DLL_PROCESS_ATTACH)self_module=module;
    /* No DLL loads, UI, synchronization or file I/O under loader lock. */
    return TRUE;
}
