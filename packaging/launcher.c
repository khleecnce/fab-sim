/* FabSim Studio.app 실행기 — Resources/run.sh 를 실행한다.
   macOS LaunchServices는 셸 스크립트를 CFBundleExecutable로 거부한다(Error -10669).
   그래서 얇은 네이티브 바이너리를 두고 여기서 스크립트를 exec 한다. */
#include <stdio.h>
#include <unistd.h>
#include <libgen.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include <mach-o/dyld.h>

int main(int argc, char **argv) {
    char exe[PATH_MAX]; uint32_t sz = sizeof(exe);
    if (_NSGetExecutablePath(exe, &sz) != 0) return 1;
    char *macos = dirname(exe);                 /* Contents/MacOS */
    char contents[PATH_MAX];
    snprintf(contents, sizeof(contents), "%s", macos);
    char *c = dirname(contents);                /* Contents */
    char script[PATH_MAX];
    snprintf(script, sizeof(script), "%s/Resources/run.sh", c);
    execl("/bin/bash", "bash", script, (char *)NULL);
    return 1;
}
