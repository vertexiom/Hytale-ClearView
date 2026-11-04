"""Render the actual overlay on EGL, inspect pixels, verify GL state restoration."""
import ctypes as C
from pathlib import Path
import subprocess
import tempfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
P,I,U=C.c_void_p,C.c_int,C.c_uint

def fn(lib,name,ret,args):
    f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f

egl=C.CDLL('libEGL.so.1');gl=C.CDLL('libGL.so.1')
d=fn(egl,'eglGetPlatformDisplay',P,[U,P,C.POINTER(C.c_ssize_t)])(0x31DD,None,None)
a,b=I(),I()
assert fn(egl,'eglInitialize',U,[P,C.POINTER(I),C.POINTER(I)])(d,C.byref(a),C.byref(b))
assert fn(egl,'eglBindAPI',U,[U])(0x30A2)
attrs=(I*7)(0x3040,8,0x3033,1,0x3024,8,0x3038);cfg=P();n=I()
assert fn(egl,'eglChooseConfig',U,[P,C.POINTER(I),C.POINTER(P),I,C.POINTER(I)])(d,attrs,C.byref(cfg),1,C.byref(n)) and n.value
ca=(I*7)(0x3098,4,0x30FB,1,0x30FD,1,0x3038)
ctx=fn(egl,'eglCreateContext',P,[P,P,P,C.POINTER(I)])(d,cfg,None,ca)
pa=(I*5)(0x3057,800,0x3056,600,0x3038)
surface=fn(egl,'eglCreatePbufferSurface',P,[P,P,C.POINTER(I)])(d,cfg,pa)
assert ctx and surface and fn(egl,'eglMakeCurrent',U,[P,P,P,P])(d,surface,surface,ctx)
DEBUG=C.CFUNCTYPE(None,U,U,U,U,I,P,P)
@DEBUG
def debug(source,kind,ident,severity,length,message,user):
    if kind==0x824C: print('GL ERROR:',C.string_at(message,length).decode())
fn(gl,'glEnable',None,[U])(0x92E0)
fn(gl,'glEnable',None,[U])(0x8242)
fn(gl,'glDebugMessageCallback',None,[DEBUG,P])(debug,None)
clearcolor=fn(gl,'glClearColor',None,[C.c_float]*4);clear=fn(gl,'glClear',None,[U])
clearcolor(.10,.15,.21,1);clear(0x4000)
# Set deliberately non-default state, which the HUD must restore.
fn(gl,'glViewport',None,[I]*4)(3,5,777,555)
fn(gl,'glEnable',None,[U])(0x0C11)
fn(gl,'glEnable',None,[U])(0x0B71)
fn(gl,'glScissor',None,[I]*4)(7,11,100,100)
fn(gl,'glActiveTexture',None,[U])(0x84C3)
fn(gl,'glPixelStorei',None,[U,I])(0x0CF2,9)
fn(gl,'glPixelStorei',None,[U,I])(0x0CF3,2)
fn(gl,'glPixelStorei',None,[U,I])(0x0CF4,3)
fn(gl,'glColorMask',None,[C.c_ubyte]*4)(1,0,1,0)
geti=fn(gl,'glGetIntegerv',None,[U,C.POINTER(I)])
isenabled=fn(gl,'glIsEnabled',C.c_ubyte,[U])
def state():
    out={}
    for enum,size in [(0x0BA2,4),(0x0C23,4),(0x84E0,1),(0x0CF2,1),(0x0CF3,1),(0x0CF4,1),(0x8B8D,1),(0x85B5,1),(0x0C01,1),(0x8CA6,1),(0x8009,1)]:
        value=(I*size)();geti(enum,value);out[enum]=list(value)
    out['caps']=[isenabled(e) for e in [0x0C11,0x0B71,0x0BE2,0x0B44]]
    return out
before=state()
with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    (temp/'bridge.c').write_text('''
#include <dlfcn.h>
#include <stdio.h>
typedef void (*Proc)(void);
typedef Proc (*GetProc)(const char*);
static GetProc original_getproc;
static void record(const char *s,int i){fprintf(stderr,"%s: %d\\n",s,i);}
#include "overlay.h"
int draw(void){
 void *gl=dlopen("libGL.so.1",RTLD_NOW|RTLD_LOCAL);
 original_getproc=(GetProc)dlsym(gl,"glXGetProcAddressARB");
 float fog[3]={0,.2,1};overlay_draw(800,600,fog,1,1);
 return overlay_failed || !overlay_program;
}
''')
    flags=subprocess.check_output(['pkg-config','--cflags','--libs','cairo'],text=True).split()
    subprocess.run(['cc','-std=c11','-shared','-fPIC','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),str(temp/'bridge.c'),'-o',str(temp/'bridge.so'),'-ldl','-lm',*flags],check=True)
    bridge=C.CDLL(str(temp/'bridge.so'));bridge.draw.restype=I
    assert bridge.draw()==0,'Overlay failed to build'
    assert state()==before, (before,state())
    # Draw cached panel too: both initialization and reuse must preserve state.
    assert bridge.draw()==0 and state()==before
    error=fn(gl,'glGetError',U,[])()
    assert error==0,hex(error)
    data=(C.c_ubyte*(800*600*4))()
    fn(gl,'glReadPixels',None,[I,I,I,I,U,U,P])(0,0,800,600,0x1908,0x1401,data)
    image=Image.frombytes('RGBA',(800,600),bytes(data)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    assert image.getpixel((30,30))!=image.getpixel((700,500)), 'HUD pixels not rendered'
    (ROOT/'build').mkdir(exist_ok=True)
    image.save(ROOT/'build/hud-preview.png')
    print('PASS: real OpenGL HUD rendering, cached redraw, GL state restoration, no GL errors.')
    print(ROOT/'build/hud-preview.png')
