#define _POSIX_C_SOURCE 200809L
#include <unistd.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    char path[PATH_MAX];
    ssize_t n = readlink("/proc/self/exe", path, sizeof(path)-1);
    if (n < 0 || n >= (ssize_t)sizeof(path)-1) return 1;
    path[n] = 0;
    char *slash = strrchr(path, '/');
    if (!slash) return 1;
    *slash = 0;
    if (chdir(path) != 0) return 1;
    execl("/usr/bin/ghostty", "ghostty", "--title=ClearView - Chuva",
          "--font-family=JetBrains Mono", "--font-family-bold=JetBrains Mono",
          "--font-style=ExtraBold", "--font-style-bold=ExtraBold",
          "--font-size=10", "--background=000000", "--foreground=ffffff",
          "--window-width=170", "--window-height=68", "-e",
          "/usr/bin/python3", "rain_text.py", (char *)0);
    perror("Nao foi possivel abrir o Ghostty");
    return 1;
}
