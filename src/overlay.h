#ifndef CLEARVIEW_OVERLAY_H
#define CLEARVIEW_OVERLAY_H
#include "panel.h"

#define CV_GL_FUNCTIONS(X) \
 X(void,GetIntegerv,(unsigned,int*)) \
 X(unsigned char,IsEnabled,(unsigned)) \
 X(void,Enable,(unsigned)) X(void,Disable,(unsigned)) \
 X(void,GetBooleanv,(unsigned,unsigned char*)) \
 X(void,ColorMask,(unsigned char,unsigned char,unsigned char,unsigned char)) \
 X(void,Viewport,(int,int,int,int)) X(void,PolygonMode,(unsigned,unsigned)) \
 X(void,BlendFuncSeparate,(unsigned,unsigned,unsigned,unsigned)) \
 X(void,BlendEquationSeparate,(unsigned,unsigned)) \
 X(void,ActiveTexture,(unsigned)) X(void,BindTexture,(unsigned,unsigned)) \
 X(void,BindSampler,(unsigned,unsigned)) X(void,GenTextures,(int,unsigned*)) \
 X(void,TexParameteri,(unsigned,unsigned,int)) \
 X(void,TexImage2D,(unsigned,int,int,int,int,int,unsigned,unsigned,const void*)) \
 X(void,PixelStorei,(unsigned,int)) X(void,BindBuffer,(unsigned,unsigned)) \
 X(void,BindFramebuffer,(unsigned,unsigned)) X(void,DrawBuffer,(unsigned)) \
 X(void,GenVertexArrays,(int,unsigned*)) X(void,BindVertexArray,(unsigned)) \
 X(unsigned,CreateShader,(unsigned)) X(void,ShaderSource,(unsigned,int,const char*const*,const int*)) \
 X(void,CompileShader,(unsigned)) X(void,GetShaderiv,(unsigned,unsigned,int*)) \
 X(void,DeleteShader,(unsigned)) X(unsigned,CreateProgram,(void)) \
 X(void,AttachShader,(unsigned,unsigned)) X(void,LinkProgram,(unsigned)) \
 X(void,GetProgramiv,(unsigned,unsigned,int*)) X(void,DeleteProgram,(unsigned)) \
 X(void,UseProgram,(unsigned)) X(int,GetUniformLocation,(unsigned,const char*)) \
 X(void,Uniform1i,(int,int)) X(void,Uniform1f,(int,float)) \
 X(void,DrawArrays,(unsigned,int,int))
#define DECLARE_GL(ret,name,args) static ret (*cvgl##name)args;
CV_GL_FUNCTIONS(DECLARE_GL)
#undef DECLARE_GL
static int overlay_ready, overlay_failed, overlay_dirty=1;
static unsigned overlay_program,overlay_vao,overlay_texture;

static int overlay_load(void)
{
    if (overlay_ready) return 1;
    if (overlay_failed) return 0;
#define LOAD_GL(ret,name,args) cvgl##name=(ret (*)args)original_getproc("gl" #name); if(!cvgl##name) {overlay_failed=1; return 0;}
    CV_GL_FUNCTIONS(LOAD_GL)
#undef LOAD_GL
    overlay_ready=1;
    return 1;
}

static unsigned overlay_shader(unsigned kind,const char *source)
{
    unsigned shader=cvglCreateShader(kind);
    cvglShaderSource(shader,1,&source,NULL); cvglCompileShader(shader);
    int ok=0; cvglGetShaderiv(shader,0x8B81,&ok);
    if (!ok) { cvglDeleteShader(shader); return 0; }
    return shader;
}

static int overlay_create(void)
{
    const char *vs="#version 410 core\nout vec2 uv;\nvoid main(){vec2 p[6]=vec2[6](vec2(-1,-1),vec2(1,-1),vec2(1,1),vec2(-1,-1),vec2(1,1),vec2(-1,1));vec2 v=p[gl_VertexID];gl_Position=vec4(v,0,1);uv=vec2(v.x*.5+.5,.5-v.y*.5);}";
    const char *fs="#version 410 core\nuniform sampler2D panel;in vec2 uv;layout(location=0)out vec4 color;void main(){color=texture(panel,uv);}";
    unsigned v=overlay_shader(0x8B31,vs), f=overlay_shader(0x8B30,fs);
    if (!v || !f) { if(v)cvglDeleteShader(v); if(f)cvglDeleteShader(f); return 0; }
    overlay_program=cvglCreateProgram(); cvglAttachShader(overlay_program,v); cvglAttachShader(overlay_program,f);
    cvglLinkProgram(overlay_program); cvglDeleteShader(v); cvglDeleteShader(f);
    int ok=0; cvglGetProgramiv(overlay_program,0x8B82,&ok);
    if(!ok) {cvglDeleteProgram(overlay_program);overlay_program=0;return 0;}
    cvglGenVertexArrays(1,&overlay_vao); cvglGenTextures(1,&overlay_texture);
    return 1;
}

/* Save/restore all state touched by overlay creation, upload and drawing.
 * No GL library is linked: entry points come from the game's own SDL context. */
static void overlay_draw(int width,int height,const float fog[3],int selected,int saved)
{
    if(width<1 || height<1 || !overlay_load()) return;
    int program,vao,viewport[4],fbo,active,texture,sampler,unpack,alignment,row,skiprows,skippixels;
    int rgb_src,rgb_dst,a_src,a_dst,rgb_eq,a_eq,polygon[2];
    unsigned char mask[4];
    unsigned caps[]={0x0BE2,0x0B71,0x0B90,0x0B44,0x0C11,0x8DB9,0x8C89,0x0BF2,0x809E,0x80A0};
    unsigned char enabled[sizeof caps/sizeof caps[0]];
    cvglGetIntegerv(0x8B8D,&program);cvglGetIntegerv(0x85B5,&vao);cvglGetIntegerv(0x0BA2,viewport);
    cvglGetIntegerv(0x8CA6,&fbo);cvglGetIntegerv(0x84E0,&active);
    cvglActiveTexture(0x84C0);cvglGetIntegerv(0x8069,&texture);cvglGetIntegerv(0x8919,&sampler);
    cvglGetIntegerv(0x88EF,&unpack);cvglGetIntegerv(0x0CF5,&alignment);cvglGetIntegerv(0x0CF2,&row);
    cvglGetIntegerv(0x0CF3,&skiprows);cvglGetIntegerv(0x0CF4,&skippixels);
    cvglGetIntegerv(0x80C9,&rgb_src);cvglGetIntegerv(0x80C8,&rgb_dst);
    cvglGetIntegerv(0x80CB,&a_src);cvglGetIntegerv(0x80CA,&a_dst);
    cvglGetIntegerv(0x8009,&rgb_eq);cvglGetIntegerv(0x883D,&a_eq);
    cvglGetIntegerv(0x0B40,polygon);cvglGetBooleanv(0x0C23,mask);
    for(size_t i=0;i<sizeof caps/sizeof caps[0];++i) {enabled[i]=cvglIsEnabled(caps[i]);cvglDisable(caps[i]);}
    cvglBindFramebuffer(0x8CA9,0);
    /* Keep the window framebuffer's existing draw buffer. EGL may expose
     * GL_BACK even when GL_DOUBLEBUFFER reports false. */
    if(!overlay_program && !overlay_create()) {overlay_failed=1;record("HUD shader build failed",0);goto restore;}
    cvglBindBuffer(0x88EC,0);cvglPixelStorei(0x0CF5,4);cvglPixelStorei(0x0CF2,0);
    cvglPixelStorei(0x0CF3,0);cvglPixelStorei(0x0CF4,0);
    cvglBindTexture(0x0DE1,overlay_texture);cvglBindSampler(0,0);
    if(overlay_dirty) {
        cairo_surface_t *surface=cv_panel(fog,selected,saved);
        if(cairo_surface_status(surface)==CAIRO_STATUS_SUCCESS) {
            cvglTexImage2D(0x0DE1,0,0x8058,CV_PANEL_W,CV_PANEL_H,0,0x80E1,0x1401,cairo_image_surface_get_data(surface));
            cvglTexParameteri(0x0DE1,0x2801,0x2601);cvglTexParameteri(0x0DE1,0x2800,0x2601);
            cvglTexParameteri(0x0DE1,0x2802,0x812F);cvglTexParameteri(0x0DE1,0x2803,0x812F);
            overlay_dirty=0;
        }
        cairo_surface_destroy(surface);
    }
    float scale=fminf(1.5f,fmaxf(1.0f,height/1080.0f));
    scale=fminf(scale,fminf((width-32.0f)/CV_PANEL_W,(height-32.0f)/CV_PANEL_H));
    int w=(int)(CV_PANEL_W*scale),h=(int)(CV_PANEL_H*scale);
    cvglViewport(16,height-16-h,w,h);cvglColorMask(1,1,1,1);cvglPolygonMode(0x0408,0x1B02);
    cvglEnable(0x0BE2);cvglBlendEquationSeparate(0x8006,0x8006);cvglBlendFuncSeparate(1,0x0303,1,0x0303);
    cvglUseProgram(overlay_program);cvglUniform1i(cvglGetUniformLocation(overlay_program,"panel"),0);
    cvglBindVertexArray(overlay_vao);cvglDrawArrays(0x0004,0,6);
restore:
    cvglBindFramebuffer(0x8CA9,(unsigned)fbo);
    cvglUseProgram((unsigned)program);cvglBindVertexArray((unsigned)vao);cvglViewport(viewport[0],viewport[1],viewport[2],viewport[3]);
    cvglBindTexture(0x0DE1,(unsigned)texture);cvglBindSampler(0,(unsigned)sampler);cvglActiveTexture((unsigned)active);
    cvglBindBuffer(0x88EC,(unsigned)unpack);cvglPixelStorei(0x0CF5,alignment);cvglPixelStorei(0x0CF2,row);
    cvglPixelStorei(0x0CF3,skiprows);cvglPixelStorei(0x0CF4,skippixels);
    cvglColorMask(mask[0],mask[1],mask[2],mask[3]);cvglPolygonMode(0x0408,(unsigned)polygon[0]);
    cvglBlendEquationSeparate((unsigned)rgb_eq,(unsigned)a_eq);
    cvglBlendFuncSeparate((unsigned)rgb_src,(unsigned)rgb_dst,(unsigned)a_src,(unsigned)a_dst);
    for(size_t i=0;i<sizeof caps/sizeof caps[0];++i) {if(enabled[i])cvglEnable(caps[i]);else cvglDisable(caps[i]);}
}
#endif
