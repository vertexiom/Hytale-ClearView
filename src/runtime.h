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
#ifndef CLEARVIEW_RUNTIME_H
#define CLEARVIEW_RUNTIME_H
/* Shared source transformation and per-thread OpenGL program dispatch. */
static void patched_source(unsigned int shader, int count,
                           const char *const *strings, const int *lengths)
{
    CV_RUNTIME_INIT();
    ShaderSource real_source = original_getproc ? (ShaderSource)original_getproc("glShaderSource") : NULL;
    if (!real_source) { record("ERROR resolving glShaderSource", 0); return; }
    if (count <= 0 || !strings) goto unchanged;
    size_t total = 0;
    for (int i = 0; i < count; ++i) {
        if (!strings[i]) goto unchanged;
        size_t n = lengths && lengths[i] >= 0 ? (size_t)lengths[i] : strlen(strings[i]);
        if (n > 16 * 1024 * 1024 || total > 16 * 1024 * 1024 - n) goto unchanged;
        total += n;
    }
    char *joined = malloc(total + 1);
    if (!joined) goto unchanged;
    size_t pos = 0;
    for (int i = 0; i < count; ++i) {
        size_t n = lengths && lengths[i] >= 0 ? (size_t)lengths[i] : strlen(strings[i]);
        memcpy(joined + pos, strings[i], n); pos += n;
    }
    joined[total] = 0;
    /* Embedded NULs are not safe to transform using string operations. */
    if (strlen(joined) != total) { free(joined); goto unchanged; }
    int changes;
    char *modified = cv_patch(joined, 3, &changes);
    if (!modified && strstr(joined, "float computeDistantFogFactor("))
        record("fog source did not match; left unchanged", (int)shader);
    free(joined);
    if (modified) {
        const char *source = modified;
        real_source(shader, 1, &source, NULL);
        record("patched fog functions", changes);
        free(modified);
        return;
    }
unchanged:
    real_source(shader, count, strings, lengths);
}

/* Uniform locations are per program; invalidate on link/delete and handle reuse. */
static CV_THREAD_LOCAL struct { unsigned program; int valid,locations[3]; } programs[4096];
static CV_THREAD_LOCAL void (*real_use)(unsigned);
static CV_THREAD_LOCAL void (*real_link)(unsigned);
static CV_THREAD_LOCAL void (*real_delete)(unsigned);
static CV_THREAD_LOCAL int (*real_location)(unsigned,const char*);
static CV_THREAD_LOCAL void (*real_uniform)(int,float);
static int fog_api(void)
{
    if(!real_use) real_use=(void(*)(unsigned))original_getproc("glUseProgram");
    if(!real_location) real_location=(int(*)(unsigned,const char*))original_getproc("glGetUniformLocation");
    if(!real_uniform) real_uniform=(void(*)(int,float))original_getproc("glUniform1f");
    return real_use && real_location && real_uniform;
}
static void use_program(unsigned program)
{
    if(!fog_api()) { if(real_use)real_use(program);return; }
    real_use(program);
    if(!program) return;
    unsigned slot=program%4096;
    if(!programs[slot].valid || programs[slot].program!=program) {
        programs[slot].program=program;programs[slot].valid=1;
        const char *names[]={"cvOriginalDistanceFog","cvOriginalMoodFog","cvOriginalDepthFog"};
        for(int i=0;i<3;++i) programs[slot].locations[i]=real_location(program,names[i]);
    }
    float amounts[3];
    CV_READ_AMOUNTS(amounts);
    for(int i=0;i<3;++i) if(programs[slot].locations[i]>=0) real_uniform(programs[slot].locations[i],amounts[i]);
}
static void link_program(unsigned program)
{
    programs[program%4096].valid=0;
    if(!real_link)real_link=(void(*)(unsigned))original_getproc("glLinkProgram");
    if(real_link)real_link(program);
}
static void delete_program(unsigned program)
{
    programs[program%4096].valid=0;
    if(!real_delete)real_delete=(void(*)(unsigned))original_getproc("glDeleteProgram");
    if(real_delete)real_delete(program);
}


#endif
