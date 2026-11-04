#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p build
stage=$(mktemp -d build/stage.XXXXXX)
trap 'rm -rf -- "$stage"' EXIT
# Link name of the original SDL, resolved beside the proxy at runtime.
cc -shared -fPIC -x c /dev/null -Wl,-soname,libSDL3.clearview-original.so -o "$stage/original.so"
printf 'SDL3_0.0.0 { global: SDL_GL_GetProcAddress; SDL_GL_SwapWindow; SDL_PollEvent; SDL_PeepEvents; SDL_GetKeyboardState; local: *; };\n' > "$stage/exports.map"
cc -std=c11 -O2 -Wall -Wextra -Werror -fPIC -shared src/proxy.c $(pkg-config --cflags cairo) \
  -Wl,-z,defs -Wl,-soname,libSDL3.so '-Wl,-rpath,$ORIGIN' \
  -Wl,--version-script="$stage/exports.map" \
  -Wl,--no-as-needed "$stage/original.so" -Wl,--as-needed \
  -ldl -lpthread -lm $(pkg-config --libs cairo) -o "$stage/libSDL3.so"
mv -- "$stage/libSDL3.so" build/libSDL3.so
echo 'Built build/libSDL3.so'
