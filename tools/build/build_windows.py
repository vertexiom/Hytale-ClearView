"""Cross-compile a Windows 10+ x64 build without changing the game installation."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from gen_windows_exports import generate
ROOT=Path(__file__).resolve().parents[2]
VERSION='0.1.1'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--zig',default=os.environ.get('ZIG','zig'));args=parser.parse_args()
    zig=shutil.which(args.zig)
    if not zig: raise SystemExit('Zig is required. Pass --zig /path/to/zig (tested with 0.15.2).')
    out=ROOT/'build/windows';out.mkdir(parents=True,exist_ok=True)
    generate(out)
    command=[zig,'cc','-target','x86_64-windows-gnu','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-cast-function-type-mismatch',
             '-shared','-I'+str(out),
             str(ROOT/'src/windows/proxy_win.c'),str(out/'exports.S'),str(out/'opengl32.def'),
             '-luser32','-lgdi32','-lkernel32','-o',str(out/'opengl32.dll')]
    subprocess.run(command,check=True)
    subprocess.run([zig,'cc','-target','x86_64-windows-gnu','-std=c11','-O2','-Wall','-Wextra','-Werror',
                    '-Wno-cast-function-type-mismatch',str(ROOT/'tests/windows_smoke.c'),
                    '-luser32','-lgdi32','-lshell32','-o',str(out/'clearview-smoke.exe')],check=True)
    manifest={'product' :'Hytale ClearView','version':VERSION,'architecture':'x64','minimum_os':'Windows 10 1809 (build 17763)',
              'validation':'initial-release-validation-in-progress',
              'files':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['opengl32.dll','clearview-smoke.exe']}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out/'opengl32.dll')
if __name__=='__main__':main()
