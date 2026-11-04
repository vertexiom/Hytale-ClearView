#define _GNU_SOURCE
#include <dlfcn.h>
#include <limits.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <unistd.h>
#include "patch.h"

typedef void (*Proc)(void);
typedef Proc (*GetProc)(const char *);
typedef void (*ShaderSource)(unsigned int, int, const char *const *, const int *);
static GetProc original_getproc;
static pthread_once_t init_once = PTHREAD_ONCE_INIT;
static char directory[PATH_MAX];
static int mode = 1;
static float fog_amount[3] = {0,1,1};
static int panel_open, selected_fog, settings_saved=1;
static bool captured_keys[512];
static bool keyboard_copy[512];
static void *original_library;
static bool (*real_poll)(void*);
static int (*real_peep)(void*,int,int,unsigned,unsigned);
static const bool *(*real_keyboard)(int*);
static bool (*real_swap)(void*);
static bool (*real_window_size)(void*,int*,int*);
static void *(*real_keyboard_focus)(void);
/* Installer recognizes only libraries containing this ownership marker. */
__attribute__((used)) static const char owner[] = "HYTALE_CLEARVIEW_PROXY_V1";

static void record(const char *message, int value)
{
    char path[PATH_MAX];
    if (snprintf(path, sizeof path, "%s/.clearview/hook.log", directory) >= (int)sizeof path) return;
    FILE *f = fopen(path, "a");
    if (f) { fprintf(f, "ClearView: %s (%d)\n", message, value); fclose(f); }
}

#include "overlay.h"

static void save_settings(void)
{
    char path[PATH_MAX],temp[PATH_MAX];
    settings_saved=0;
    if(snprintf(path,sizeof path,"%s/.clearview/settings",directory)>=(int)sizeof path) return;
    if(snprintf(temp,sizeof temp,"%s/.clearview/settings.XXXXXX",directory)>=(int)sizeof temp) return;
    int fd=mkstemp(temp);
    if(fd<0) return;
    FILE *f=fdopen(fd,"w");
    if(!f) {close(fd);unlink(temp);return;}
    int ok=fprintf(f,"%.3f %.3f %.3f\n",fog_amount[0],fog_amount[1],fog_amount[2])>0;
    if(fclose(f)!=0) ok=0;
    if(ok && rename(temp,path)==0) settings_saved=1;
    unlink(temp);
    overlay_dirty=1;
}

static void initialize(void)
{
    Dl_info info;
    if (!dladdr((void *)initialize, &info) || !info.dli_fname) return;
    if (!realpath(info.dli_fname, directory)) return;
    char *slash = strrchr(directory, '/');
    if (!slash) return;
    *slash = 0;
    char path[PATH_MAX];
    if (snprintf(path, sizeof path, "%s/libSDL3.clearview-original.so", directory) >= (int)sizeof path) return;
    original_library = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (original_library) {
        original_getproc=(GetProc)dlsym(original_library,"SDL_GL_GetProcAddress");
        real_poll=(bool(*)(void*))dlsym(original_library,"SDL_PollEvent");
        real_peep=(int(*)(void*,int,int,unsigned,unsigned))dlsym(original_library,"SDL_PeepEvents");
        real_keyboard=(const bool*(*)(int*))dlsym(original_library,"SDL_GetKeyboardState");
        real_swap=(bool(*)(void*))dlsym(original_library,"SDL_GL_SwapWindow");
        real_window_size=(bool(*)(void*,int*,int*))dlsym(original_library,"SDL_GetWindowSizeInPixels");
        real_keyboard_focus=(void*(*)(void))dlsym(original_library,"SDL_GetKeyboardFocus");
    }
    if (snprintf(path, sizeof path, "%s/.clearview/mode", directory) >= (int)sizeof path) return;
    FILE *f = fopen(path, "r");
    if (f) {
        char setting[32] = {0};
        if (fscanf(f, "%31s", setting) == 1) {
            if (!strcmp(setting, "off")) mode = 0;
            else if (!strcmp(setting, "distance")) mode = 1;
            else if (!strcmp(setting, "atmosphere")) mode = 2;
            else if (!strcmp(setting, "all")) mode = 3;
            else { mode = 0; record("invalid mode; disabled", 0); }
        }
        fclose(f);
    }
    for(int i=0;i<3;++i) fog_amount[i]=(mode && i<mode)?0.0f:1.0f;
    if(snprintf(path,sizeof path,"%s/.clearview/settings",directory)<(int)sizeof path) {
        f=fopen(path,"r");
        if(f) {
            float a,b,c;
            if(fscanf(f,"%f %f %f",&a,&b,&c)==3 && isfinite(a) && isfinite(b) && isfinite(c) &&
               a>=0 && a<=1 && b>=0 && b<=1 && c>=0 && c<=1) {
                fog_amount[0]=a;fog_amount[1]=b;fog_amount[2]=c;
            }
            fclose(f);
        }
    }
    record(original_getproc ? "HUD version loaded; initial mode" : "ERROR resolving SDL; mode", mode);
}

#define CV_RUNTIME_INIT() pthread_once(&init_once,initialize)
#define CV_THREAD_LOCAL _Thread_local
#define CV_READ_AMOUNTS(out) memcpy((out),fog_amount,sizeof fog_amount)
#include "runtime.h"

/* SDL 3.2 keyboard-event ABI. SDL_Event is a 128-byte union.
 * API layout: https://wiki.libsdl.org/SDL3/SDL_KeyboardEvent */
struct cv_key_event {
    uint32_t type,reserved; uint64_t timestamp; uint32_t window,keyboard;
    int32_t scan; uint32_t key; uint16_t modifiers,raw; bool down,repeat;
};
static int filter_event(const void *event)
{
    uint32_t type; memcpy(&type,event,sizeof type);
    if(type!=0x300 && type!=0x301) return 0;
    struct cv_key_event key; memcpy(&key,event,sizeof key);
    int scan=key.scan;
    if(scan<0 || scan>=512) return 0;
    if(type==0x301) {
        int captured=captured_keys[scan];captured_keys[scan]=false;return captured;
    }
    if(scan==66) { /* F9 (SDL_SCANCODE_F9) */
        if(!key.repeat) { panel_open=!panel_open;overlay_dirty=1; }
        captured_keys[scan]=true;return 1;
    }
    if(!panel_open) return 0;
    int changed=0;
    switch(scan) {
    case 41: panel_open=0;break; /* Escape */
    case 82: selected_fog=(selected_fog+2)%3;break;
    case 81: selected_fog=(selected_fog+1)%3;break;
    case 80: fog_amount[selected_fog]=fmaxf(0,fog_amount[selected_fog]-.05f);changed=1;break;
    case 79: fog_amount[selected_fog]=fminf(1,fog_amount[selected_fog]+.05f);changed=1;break;
    case 25: fog_amount[0]=0;fog_amount[1]=.2f;fog_amount[2]=1;changed=1;break; /* V */
    case 21: fog_amount[0]=fog_amount[1]=fog_amount[2]=1;changed=1;break; /* R */
    default: return 0;
    }
    captured_keys[scan]=true;overlay_dirty=1;
    if(changed) save_settings();
    return 1;
}

/* SDL consumers may cache this pointer. Refresh the stable array after event
 * pumping as well as on explicit reads; otherwise controls can get stuck. */
static void refresh_keyboard(void)
{
    if(!real_keyboard)return;
    int count=0;const bool *keys=real_keyboard(&count);
    if(!keys || count<0 || count>512)return;
    memcpy(keyboard_copy,keys,(size_t)count*sizeof(bool));
    for(int i=0;i<count;++i)
        if(captured_keys[i] || i==66 || (panel_open && (i==41 || i==21 || i==25 || (i>=79 && i<=82))))
            keyboard_copy[i]=false;
}

__attribute__((visibility("default"))) bool SDL_PollEvent(void *event)
{
    pthread_once(&init_once,initialize);
    if(!real_poll) return false;
    if(!event) {bool found=real_poll(event);refresh_keyboard();return found;}
    while(real_poll(event)) {
        int consumed=filter_event(event);refresh_keyboard();
        if(!consumed)return true;
    }
    refresh_keyboard();return false;
}
__attribute__((visibility("default"))) int SDL_PeepEvents(void *events,int count,int action,unsigned first,unsigned last)
{
    pthread_once(&init_once,initialize);
    if(!real_peep) return -1;
    int n=real_peep(events,count,action,first,last);
    if(action!=2 || !events || n<=0) {refresh_keyboard();return n;}
    int kept=0;
    for(int i=0;i<n;++i) {
        unsigned char *event=(unsigned char*)events+128*i;
        if(!filter_event(event)) {if(kept!=i)memmove((unsigned char*)events+128*kept,event,128);++kept;}
    }
    refresh_keyboard();return kept;
}
__attribute__((visibility("default"))) const bool *SDL_GetKeyboardState(int *count)
{
    pthread_once(&init_once,initialize);
    if(!real_keyboard) return NULL;
    int n=0;const bool *keys=real_keyboard(&n);
    if(count)*count=n;
    if(!keys || n>512 || n<0)return keys;
    refresh_keyboard();return keyboard_copy;
}
__attribute__((visibility("default"))) bool SDL_GL_SwapWindow(void *window)
{
    pthread_once(&init_once,initialize);
    if(!real_swap) return false;
    refresh_keyboard();
    if(real_keyboard_focus && real_keyboard_focus()!=window) panel_open=0;
    if(panel_open && real_window_size) {
        int w=0,h=0;
        if(real_window_size(window,&w,&h)) overlay_draw(w,h,fog_amount,selected_fog,settings_saved);
    }
    return real_swap(window);
}

__attribute__((visibility("default"))) Proc SDL_GL_GetProcAddress(const char *name)
{
    pthread_once(&init_once, initialize);
    if (!original_getproc) return NULL;
    Proc result = original_getproc(name);
    if(result && name) {
        if(!strcmp(name,"glShaderSource"))return (Proc)patched_source;
        if(!strcmp(name,"glUseProgram"))return (Proc)use_program;
        if(!strcmp(name,"glLinkProgram"))return (Proc)link_program;
        if(!strcmp(name,"glDeleteProgram"))return (Proc)delete_program;
    }
    return result;
}
