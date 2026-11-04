#ifndef CLEARVIEW_PATCH_H
#define CLEARVIEW_PATCH_H
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/* Transform only recognized function definitions. Never ship game sources.
 * Uniform scaling preserves the original program interface at link time. */
static char *cv_function(const char *source, const char *signature,
                         const char *uniform, int mood)
{
    const char *start = strstr(source, signature);
    if (!start || strstr(start + strlen(signature), signature)) return NULL;
    const char *brace = strchr(start + strlen(signature), '{');
    const char *semi = strchr(start + strlen(signature), ';');
    if (!brace || (semi && semi < brace)) return NULL;
    const char *end = brace + 1;
    int depth = 1;
    while (*end && depth) {
        if (*end == '{') ++depth;
        if (*end == '}') --depth;
        if (depth) ++end;
    }
    if (depth) return NULL;
    const char *target = end;
    size_t removed = 0;
    const char *original = "return fogFactor;";
    if (!mood) {
        target = strstr(brace, original);
        if (!target || target >= end) return NULL;
        const char *another = strstr(target + strlen(original), original);
        if (another && another < end) return NULL;
        removed = strlen(original);
    }
    char declaration[128], replacement[200];
    /* Default 1 is fail-open: original fog if a program is not yet configured. */
    snprintf(declaration, sizeof declaration, "uniform float %s = 1.0;\n", uniform);
    snprintf(replacement, sizeof replacement, mood ?
        "\n/* CLEARVIEW_PATCH atmosphere */ fogThicknessFactor *= %s;\n" :
        "/* CLEARVIEW_PATCH distance/depth */ return fogFactor * %s;", uniform);
    size_t head = (size_t)(start-source), at = (size_t)(target-source);
    size_t decl = strlen(declaration), repl = strlen(replacement), len = strlen(source);
    char *result = malloc(len + decl + repl - removed + 1);
    if (!result) return NULL;
    memcpy(result, source, head);
    memcpy(result+head, declaration, decl);
    memcpy(result+head+decl, source+head, at-head);
    memcpy(result+at+decl, replacement, repl);
    memcpy(result+at+decl+repl, target+removed, len-at-removed+1);
    return result;
}

static char *cv_patch(const char *source, int mode, int *changes)
{
    *changes = 0;
    if (mode < 1 || mode > 3 || !strstr(source,"FOG_INCLUDE") || strstr(source,"CLEARVIEW_PATCH")) return NULL;
    const char *signatures[] = {
        "float computeDistantFogFactor(vec3 positionFromCamera, vec4 fogParams)",
        "void computeMoodFog(vec3 positionFromCamera, vec3 cameraPosition,",
        "float computeDepthFogFactor(vec3 positionFromCamera, vec4 fogParams)"
    };
    const char *uniforms[] = {"cvOriginalDistanceFog", "cvOriginalMoodFog", "cvOriginalDepthFog"};
    char *current = NULL;
    for (int i=0; i<mode; ++i) {
        char *next = cv_function(current ? current : source, signatures[i], uniforms[i], i==1);
        if (!next) { free(current); *changes=0; return NULL; }
        free(current); current=next; ++*changes;
    }
    return current;
}
#endif
