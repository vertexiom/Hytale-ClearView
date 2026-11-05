/* Copyright (C) 2026 vertexiom
 * SPDX-License-Identifier: GPL-3.0-or-later
 * Process-exit fixture only: does not load OpenGL or access a game.
 */
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    puts("OpenGL: fixture (no graphics test performed)");
    const char *failure = getenv("CV_FAIL");
    if (failure && *failure) {
        fputs("FAIL: synthetic failure\n", stderr);
        return 7;
    }
    puts("PASS: WGL forwarding, synthetic fixture");
    return 0;
}
