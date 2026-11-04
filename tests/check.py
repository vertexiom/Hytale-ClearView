"""Integration test: SDL forwarding, GLSL segments and install/restore cycle.

Uses a fake client in a temporary directory; never modifies the real game.
Run: python3 tests/check.py
"""
import ctypes as C
import hashlib
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MOCK = r'''
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
static char captured[4096];
void fake_source(unsigned s, int n, const char *const *parts, const int *lengths) {
    (void)s;
    size_t pos = 0;
    for (int i=0; i<n; ++i) {
        size_t len = lengths && lengths[i]>=0 ? (size_t)lengths[i] : strlen(parts[i]);
        if (pos+len >= sizeof captured) abort();
        memcpy(captured+pos,parts[i],len); pos+=len;
    }
    captured[pos]=0;
}
static float values[3];
void fake_use(unsigned p) {(void)p;}
void fake_link(unsigned p) {(void)p;}
int fake_location(unsigned p,const char *name) {
    (void)p;
    if(!strcmp(name,"cvOriginalDistanceFog")) return 0;
    if(!strcmp(name,"cvOriginalMoodFog")) return 1;
    if(!strcmp(name,"cvOriginalDepthFog")) return 2;
    return -1;
}
void fake_uniform(int loc,float value) {if(loc>=0 && loc<3)values[loc]=value;}
float mock_value(int i) {return values[i];}
void *SDL_GL_GetProcAddress(const char *name) {
    if(!strcmp(name,"glShaderSource"))return (void*)fake_source;
    if(!strcmp(name,"glUseProgram"))return (void*)fake_use;
    if(!strcmp(name,"glLinkProgram") || !strcmp(name,"glDeleteProgram"))return (void*)fake_link;
    if(!strcmp(name,"glGetUniformLocation"))return (void*)fake_location;
    if(!strcmp(name,"glUniform1f"))return (void*)fake_uniform;
    return NULL;
}
static unsigned char queued[128];static int pending;static bool keys[512];
const bool *SDL_GetKeyboardState(int *n){if(n)*n=512;return keys;}
void mock_key(int scan,int down) {
    memset(queued,0,sizeof queued);
    uint32_t type=down?0x300:0x301;
    memcpy(queued,&type,4);memcpy(queued+24,&scan,4);queued[36]=(unsigned char)down;pending=1;
}
bool SDL_PollEvent(void *event) {
    if(!pending)return false;
    if(event){memcpy(event,queued,128);pending=0;int scan;memcpy(&scan,queued+24,4);if(scan>=0 && scan<512)keys[scan]=queued[36];}
    return true;
}
const char *mock_captured(void) {return captured;}
int SDL_GetVersion(void) {return 3000000;}
'''

with tempfile.TemporaryDirectory(prefix='clearview-test-') as directory:
    client = Path(directory)
    (client / 'HytaleClient').write_bytes(b'fake executable, must remain unchanged')
    (client / 'mock.c').write_text(MOCK)
    original = client / 'libSDL3.so'
    subprocess.run(['cc', '-shared', '-fPIC', str(client/'mock.c'), '-o', str(original)], check=True)
    original_data = original.read_bytes()
    args = ['bash', str(ROOT/'install.sh'), '--client-dir', str(client)]
    subprocess.run(args + ['--mode', 'distance'], check=True)
    proxy = C.CDLL(str(original), mode=C.RTLD_LOCAL)
    proxy.SDL_GetVersion.restype = C.c_int
    assert proxy.SDL_GetVersion() == 3000000, 'Unwrapped SDL export did not forward'
    proxy.SDL_GL_GetProcAddress.argtypes = [C.c_char_p]
    proxy.SDL_GL_GetProcAddress.restype = C.c_void_p
    addr = proxy.SDL_GL_GetProcAddress(b'glShaderSource')
    assert addr
    call = C.CFUNCTYPE(None, C.c_uint, C.c_int, C.POINTER(C.c_char_p), C.POINTER(C.c_int))(addr)
    proxy.mock_captured.restype = C.c_char_p
    fixture = (b'#define FOG_INCLUDE\n'
               b'float computeDistantFogFactor(vec3 positionFromCamera, vec4 fogParams) { float fogFactor=1; return fogFactor; }\n'
               b'void computeMoodFog(vec3 positionFromCamera, vec3 cameraPosition, inout float fogThicknessFactor) { fogThicknessFactor=1; }\n'
               b'float computeDepthFogFactor(vec3 positionFromCamera, vec4 fogParams) { float fogFactor=1; return fogFactor; }\n')
    segments = (C.c_char_p*2)(fixture[:30], fixture[30:] + b'IGNORED')
    lengths = (C.c_int*2)(30, len(fixture)-30)
    call(1, 2, segments, lengths)
    result = proxy.mock_captured()
    assert b'CLEARVIEW_PATCH distance' in result
    assert b'IGNORED' not in result
    unchanged = b'void main() {}'
    call(2, 1, (C.c_char_p*1)(unchanged), None)
    assert proxy.mock_captured() == unchanged
    assert not proxy.SDL_GL_GetProcAddress(b'not_supported')
    use_addr = proxy.SDL_GL_GetProcAddress(b'glUseProgram')
    use = C.CFUNCTYPE(None,C.c_uint)(use_addr)
    proxy.mock_value.argtypes = [C.c_int]
    proxy.mock_value.restype = C.c_float
    use(7)
    assert [proxy.mock_value(i) for i in range(3)] == [0,1,1]
    proxy.mock_key.argtypes = [C.c_int,C.c_int]
    proxy.SDL_PollEvent.argtypes = [C.c_void_p]
    proxy.SDL_PollEvent.restype = C.c_bool
    proxy.SDL_GetKeyboardState.argtypes=[C.POINTER(C.c_int)]
    proxy.SDL_GetKeyboardState.restype=C.POINTER(C.c_bool)
    cached_keyboard=proxy.SDL_GetKeyboardState(None)
    event = C.create_string_buffer(128)
    def key(scan):
        for down in [1,0]:
            proxy.mock_key(scan,down)
            assert not proxy.SDL_PollEvent(event), 'HUD key leaked to game'
    # Home remains available to the game and does not open the HUD.
    proxy.mock_key(74,1)
    assert proxy.SDL_PollEvent(event), 'Home was unexpectedly captured'
    proxy.mock_key(74,0)
    assert proxy.SDL_PollEvent(event)
    key(66) # F9
    key(81) # select atmosphere
    key(80) # reduce to 95%
    use(7)
    assert abs(proxy.mock_value(1)-.95)<.00001
    assert proxy.mock_value(0)==0 and proxy.mock_value(2)==1
    saved = list(map(float,(client/'.clearview/settings').read_text().split()))
    assert saved==[0,.95,1]
    key(21) # R, original
    use(7)
    assert [proxy.mock_value(i) for i in range(3)] == [1,1,1]
    key(25) # V, visibility preset
    use(7)
    assert abs(proxy.mock_value(1)-.2)<.00001
    key(41) # close
    proxy.mock_key(80,1)
    assert proxy.SDL_PollEvent(event), 'Closed HUD consumed a game key'
    assert cached_keyboard[80], 'Cached keyboard pointer did not update'
    proxy.mock_key(80,0)
    assert proxy.SDL_PollEvent(event)
    assert not cached_keyboard[80], 'Cached key got stuck'
    # A second install must retain the original backup.
    subprocess.run(args + ['--mode', 'off'], check=True)
    assert (client/'libSDL3.clearview-original.so').read_bytes() == original_data
    subprocess.run(args + ['--uninstall'], check=True)
    assert original.read_bytes() == original_data
    assert (client/'HytaleClient').read_bytes() == b'fake executable, must remain unchanged'
    assert not (client/'libSDL3.clearview-original.so').exists()
    print('PASS: SDL forwarding, segmented GLSL, explicit lengths, unchanged shaders, live uniforms, HUD key capture, persisted settings, reinstall and byte-exact restore.')
