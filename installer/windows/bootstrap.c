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
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#include <windows.h>
#include <objbase.h>
#include <stdio.h>
#include "payload.h"

static int write_file(const wchar_t *path,const unsigned char *data,DWORD size)
{
    HANDLE file=CreateFileW(path,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE)return 0;
    DWORD written=0;BOOL ok=WriteFile(file,data,size,&written,NULL);CloseHandle(file);
    return ok && written==size;
}
int WINAPI wWinMain(HINSTANCE instance,HINSTANCE previous,PWSTR arguments,int show)
{
    (void)instance;(void)previous;(void)arguments;(void)show;
    HANDLE mutex=CreateMutexW(NULL,FALSE,L"Local\\HytaleClearViewInstaller");
    if(!mutex)goto failure;
    if(GetLastError()==ERROR_ALREADY_EXISTS){
        HWND window=NULL;
        for(int attempt=0;attempt<20 && !window;++attempt){
            window=FindWindowW(NULL,L"Hytale ClearView");
            if(!window)Sleep(100);
        }
        if(window){ShowWindow(window,SW_RESTORE);SetForegroundWindow(window);}
        HANDLE activate=OpenEventW(EVENT_MODIFY_STATE,FALSE,L"Local\\HytaleClearViewInstallerActivate");
        if(activate){SetEvent(activate);CloseHandle(activate);}
        if(!window && !activate)MessageBoxW(NULL,L"O instalador ainda esta iniciando. Aguarde alguns segundos e abra novamente para trazer a janela para frente.",L"ClearView",MB_OK|MB_ICONINFORMATION);
        CloseHandle(mutex);return 0;
    }
    wchar_t temp[MAX_PATH],folder[MAX_PATH],guid_text[40],gui[MAX_PATH],zip[MAX_PATH];
    wchar_t engine[MAX_PATH],command[MAX_PATH*3];GUID guid;
    DWORD n=GetTempPathW(MAX_PATH,temp);
    if(!n || n>=MAX_PATH || FAILED(CoCreateGuid(&guid)) || !StringFromGUID2(&guid,guid_text,40))goto failure;
    if(swprintf(folder,MAX_PATH,L"%lsClearView-%ls",temp,guid_text)<0 || !CreateDirectoryW(folder,NULL))goto failure;
    if(swprintf(gui,MAX_PATH,L"%ls\\setup.ps1",folder)<0 || swprintf(zip,MAX_PATH,L"%ls\\payload.zip",folder)<0)goto failure;
    if(!write_file(gui,gui_script,sizeof gui_script) || !write_file(zip,package_zip,sizeof package_zip))goto cleanup_failure;
    n=GetSystemDirectoryW(engine,MAX_PATH);
    if(!n || n>=MAX_PATH || n+wcslen(L"\\WindowsPowerShell\\v1.0\\powershell.exe")>=MAX_PATH)goto cleanup_failure;
    wcscat(engine,L"\\WindowsPowerShell\\v1.0\\powershell.exe");
    if(swprintf(command,MAX_PATH*3,L"\"%ls\" -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File \"%ls\"",engine,gui)<0)goto cleanup_failure;
    STARTUPINFOW startup={0};PROCESS_INFORMATION process={0};startup.cb=sizeof startup;
    startup.dwFlags=STARTF_USESHOWWINDOW;startup.wShowWindow=SW_SHOWNORMAL;
    if(!CreateProcessW(engine,command,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,folder,&startup,&process))goto cleanup_failure;
    WaitForSingleObject(process.hProcess,INFINITE);
    DWORD code=1;GetExitCodeProcess(process.hProcess,&code);CloseHandle(process.hThread);CloseHandle(process.hProcess);
    DeleteFileW(gui);DeleteFileW(zip);RemoveDirectoryW(folder);
    CloseHandle(mutex);
    if(code){MessageBoxW(NULL,L"Nao foi possivel concluir o instalador. Tente abrir novamente. Se persistir, envie uma mensagem no Discord: tallmannzera.",L"ClearView",MB_OK|MB_ICONERROR);}
    return (int)code;
cleanup_failure:
    DeleteFileW(gui);DeleteFileW(zip);RemoveDirectoryW(folder);
failure:
    MessageBoxW(NULL,L"Nao foi possivel abrir o instalador. Verifique o espaco livre e a permissao para gravar na pasta temporaria do Windows.",L"ClearView",MB_OK|MB_ICONERROR);
    return 1;
}
