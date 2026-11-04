"""Link actual Text/BasicFog shaders and verify their required interfaces survive.
Usage: python3 tests/check_gl.py /path/to/locally-extracted-game-shaders
No game shader sources are bundled here. Requires EGL and OpenGL.
"""
import ctypes as C
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = Path(sys.argv[1])
P, I, U = C.c_void_p, C.c_int, C.c_uint

def fn(lib, name, restype, args):
    f = getattr(lib, name)
    f.restype, f.argtypes = restype, args
    return f

egl = C.CDLL('libEGL.so.1')
gl = C.CDLL('libGL.so.1')
display = fn(egl, 'eglGetPlatformDisplay', P, [U, P, C.POINTER(C.c_ssize_t)])(0x31DD, None, None)
major, minor = I(), I()
assert fn(egl, 'eglInitialize', U, [P, C.POINTER(I), C.POINTER(I)])(display, C.byref(major), C.byref(minor))
assert fn(egl, 'eglBindAPI', U, [U])(0x30A2)
attrs = (I*7)(0x3040, 8, 0x3033, 1, 0x3024, 8, 0x3038)
config, count = P(), I()
assert fn(egl, 'eglChooseConfig', U, [P, C.POINTER(I), C.POINTER(P), I, C.POINTER(I)])(display, attrs, C.byref(config), 1, C.byref(count)) and count.value
context_attrs = (I*7)(0x3098, 4, 0x30FB, 1, 0x30FD, 1, 0x3038)
context = fn(egl, 'eglCreateContext', P, [P, P, P, C.POINTER(I)])(display, config, None, context_attrs)
assert context and fn(egl, 'eglMakeCurrent', U, [P, P, P, P])(display, None, None, context)
print('Renderer:', fn(gl, 'glGetString', C.c_char_p, [U])(0x1F01).decode())
create_shader = fn(gl, 'glCreateShader', U, [U])
source_shader = fn(gl, 'glShaderSource', None, [U, I, C.POINTER(C.c_char_p), C.POINTER(I)])
compile_shader = fn(gl, 'glCompileShader', None, [U])
shader_iv = fn(gl, 'glGetShaderiv', None, [U, U, C.POINTER(I)])
shader_log = fn(gl, 'glGetShaderInfoLog', None, [U, I, C.POINTER(I), P])
create_program = fn(gl, 'glCreateProgram', U, [])
attach_shader = fn(gl, 'glAttachShader', None, [U, U])
link_program = fn(gl, 'glLinkProgram', None, [U])
program_iv = fn(gl, 'glGetProgramiv', None, [U, U, C.POINTER(I)])
program_log = fn(gl, 'glGetProgramInfoLog', None, [U, I, C.POINTER(I), P])
active_uniform = fn(gl, 'glGetActiveUniform', None, [U, U, I, C.POINTER(I), C.POINTER(I), C.POINTER(U), P])
active_attribute = fn(gl, 'glGetActiveAttrib', None, [U, U, I, C.POINTER(I), C.POINTER(I), C.POINTER(U), P])
location = fn(gl, 'glGetUniformLocation', I, [U, C.c_char_p])
get_uniform = fn(gl, 'glGetUniformfv', None, [U, I, C.POINTER(C.c_float)])

def expand(text):
    return re.sub(r'#include\s*"([^\"]+)"', lambda m: expand((SOURCES/m[1]).read_text()), text)

def link(vs, fs):
    program = create_program()
    for kind, text in [(0x8B31, vs), (0x8B30, fs)]:
        shader = create_shader(kind)
        data = C.c_char_p(text.encode())
        source_shader(shader, 1, C.byref(data), None)
        compile_shader(shader)
        ok = I()
        shader_iv(shader, 0x8B81, C.byref(ok))
        if not ok.value:
            log = C.create_string_buffer(16000)
            shader_log(shader, len(log), None, log)
            raise AssertionError(log.value.decode())
        attach_shader(program, shader)
        fn(gl, 'glDeleteShader', None, [U])(shader)
    link_program(program)
    ok = I()
    program_iv(program, 0x8B82, C.byref(ok))
    if not ok.value:
        log = C.create_string_buffer(16000)
        program_log(program, len(log), None, log)
        raise AssertionError(log.value.decode())
    return program

def interface(program, enum, getter):
    count = I()
    program_iv(program, enum, C.byref(count))
    output = set()
    for i in range(count.value):
        name = C.create_string_buffer(1024)
        length, size, kind = I(), I(), U()
        getter(program, i, len(name), C.byref(length), C.byref(size), C.byref(kind), name)
        output.add((name.value.decode(), size.value, kind.value))
    return output

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    (temp/'bridge.c').write_text('#include "patch.h"\nchar *patch(const char*s,int m,int*n){return cv_patch(s,m,n);}\nvoid release(char*s){free(s);}\n')
    subprocess.run(['cc', '-shared', '-fPIC', '-I'+str(ROOT/'src'), str(temp/'bridge.c'), '-o', str(temp/'bridge.so')], check=True)
    bridge = C.CDLL(str(temp/'bridge.so'))
    bridge.patch.argtypes = [C.c_char_p, I, C.POINTER(I)]
    bridge.patch.restype = P
    bridge.release.argtypes = [P]
    for name in ['Text', 'BasicFog']:
        vs = expand((SOURCES/(name+'VS.glsl')).read_text())
        fs = expand((SOURCES/(name+'FS.glsl')).read_text())
        baseline = link(vs, fs)
        uniforms = interface(baseline, 0x8B86, active_uniform)
        attributes = interface(baseline, 0x8B89, active_attribute)
        if name == 'Text':
            assert location(baseline, b'uPosition') >= 0
            # Demonstrate that the old constant return reproduces the crash.
            broken = fs.replace('float computeDistantFogFactor(vec3 positionFromCamera, vec4 fogParams)\n{', 'float computeDistantFogFactor(vec3 positionFromCamera, vec4 fogParams)\n{\nreturn 0.0;')
            old = link(vs, broken)
            assert location(old, b'uPosition') == -1
            print('Reproduced old bug: TextProgram.uPosition eliminated')
        for mode in [1, 2, 3]:
            changes = I()
            result = bridge.patch(fs.encode(), mode, C.byref(changes))
            assert result and changes.value == mode
            patched = C.string_at(result).decode()
            bridge.release(result)
            program = link(vs, patched)
            assert uniforms <= interface(program, 0x8B86, active_uniform), 'Required uniforms removed'
            assert attributes <= interface(program, 0x8B89, active_attribute), 'Required attributes removed'
            loc = location(program, b'cvOriginalDistanceFog')
            assert loc >= 0
            default = C.c_float(-1)
            get_uniform(program, loc, C.byref(default))
            assert default.value == 1, 'Unconfigured shader must retain original fog'
            print('PASS:', name, 'mode', mode, '- original uniforms/attributes preserved; safe original-fog defaults')
    # Render real fog functions into a floating-point pixel. Verify each slider
    # changes only its own factor, including intermediate 50% values.
    fog = expand((SOURCES/'Fog_inc.glsl').read_text())
    full = '#version 410 core\n' + fog + """
layout(location=0) out vec4 result;
void main() {
    float mood=0.0; vec3 color=vec3(1.0);
    computeMoodFog(vec3(50.0),vec3(0.0),0.01,0.1,vec3(0.2),
                   vec3(0.0),false,1.0,0.0,0.0,1.0,color,mood);
    result=vec4(computeDistantFogFactor(vec3(50.0),vec4(1,100,10,1)),
                mood,computeDepthFogFactor(vec3(50.0),vec4(1,100,10,1)),1);
}
"""
    changes=I(); result=bridge.patch(full.encode(),3,C.byref(changes))
    assert result and changes.value==3
    fragment=C.string_at(result).decode();bridge.release(result)
    vertex='#version 410 core\nvoid main(){vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));gl_Position=vec4(p[gl_VertexID],0,1);}'
    program=link(vertex,fragment)
    fn(gl,'glUseProgram',None,[U])(program)
    texture,fb,vao=U(),U(),U()
    fn(gl,'glGenTextures',None,[I,C.POINTER(U)])(1,C.byref(texture))
    fn(gl,'glBindTexture',None,[U,U])(0x0DE1,texture)
    fn(gl,'glTexImage2D',None,[U,I,I,I,I,I,U,U,P])(0x0DE1,0,0x8814,1,1,0,0x1908,0x1406,None)
    fn(gl,'glGenFramebuffers',None,[I,C.POINTER(U)])(1,C.byref(fb))
    fn(gl,'glBindFramebuffer',None,[U,U])(0x8D40,fb)
    fn(gl,'glFramebufferTexture2D',None,[U,U,U,U,I])(0x8D40,0x8CE0,0x0DE1,texture,0)
    assert fn(gl,'glCheckFramebufferStatus',U,[U])(0x8D40)==0x8CD5
    fn(gl,'glGenVertexArrays',None,[I,C.POINTER(U)])(1,C.byref(vao))
    fn(gl,'glBindVertexArray',None,[U])(vao)
    fn(gl,'glViewport',None,[I]*4)(0,0,1,1)
    uniform=fn(gl,'glUniform1f',None,[I,C.c_float])
    locations=[location(program,name) for name in [b'cvOriginalDistanceFog',b'cvOriginalMoodFog',b'cvOriginalDepthFog']]
    assert all(x>=0 for x in locations)
    def render(values):
        for loc,value in zip(locations,values): uniform(loc,value)
        fn(gl,'glDrawArrays',None,[U,I,I])(0x0004,0,3)
        pixel=(C.c_float*4)()
        fn(gl,'glReadPixels',None,[I,I,I,I,U,U,P])(0,0,1,1,0x1908,0x1406,pixel)
        return list(pixel)[:3]
    original=render([1,1,1])
    assert all(x>0 for x in original),original
    for values in [[0,0,0],[.5,.5,.5],[0,.2,1],[.75,1,.25]]:
        actual=render(values)
        expected=[a*b for a,b in zip(original,values)]
        assert all(abs(a-b)<.00001 for a,b in zip(actual,expected)), (actual,expected)
    print('PASS: rendered fog factors match independent 0%, 20%, 25%, 50%, 75%, 100% controls')
print('PASS: GPU program-link regression tests')
