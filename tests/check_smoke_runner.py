"""Exercise smoke-process exit handling with tiny native stand-ins, not a real GPU."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pwsh',required=True);args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="clearview smoke espaço '") as td:
        p=Path(td);(p/'bin').mkdir()
        shutil.copy2(ROOT/'installer/windows/smoke-test.ps1',p/'smoke-test.ps1')
        (p/'bin/opengl32.dll').write_bytes(b'fixture')
        exe=p/'bin/clearview-smoke.exe'
        exe.write_text("#!/usr/bin/python3\nimport os,sys\nprint('OpenGL: fixture')\nif os.environ.get('CV_FAIL'):\n print('FAIL: synthetic failure',file=sys.stderr);sys.exit(7)\nprint('PASS: WGL forwarding, synthetic fixture')\n")
        exe.chmod(0o755)
        (p/'manifest.json').write_text(json.dumps({'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (p/'bin').iterdir()}}))
        for failure in ['', 'yes']:
            r=subprocess.run([args.pwsh,'-NoProfile','-File',str(p/'smoke-test.ps1')],env={**os.environ,'OS':'Windows_NT','CV_FAIL':failure},capture_output=True,text=True,timeout=20)
            assert (r.returncode==0)==(not failure),(r.stdout,r.stderr)
            assert ('Teste isolado aprovado.' in r.stdout)==(not failure),(r.stdout,r.stderr)
            assert 'codigo: '+('7' if failure else '0') in r.stdout,r.stdout
        test=p/'reason.ps1'
        test.write_text('''param($Helper)
. $Helper
$report="OpenGL: 4.6.0 NVIDIA`nPASS: WGL forwarding, x64 ABI, shader controls, F9 input and HUD."
$r=Get-ClearViewFailureReason -Report $report -Stage '2'
if($r -notmatch 'teste gráfico passou'){throw $r}
$r=Get-ClearViewFailureReason -Report $report -Stage '3'
if($r -notmatch 'instalar os arquivos'){throw $r}
$r=Get-ClearViewFailureReason -Report 'FAIL: OpenGL context unavailable' -Stage '2'
if($r -notmatch 'teste gráfico não passou'){throw $r}
''')
        subprocess.run([args.pwsh,'-NoProfile','-File',str(test),str(ROOT/'installer/windows/workflow.ps1')],check=True)
    print('PASS: fast child process success/failure, exit codes, no false OpenGL failure from PASS output')
if __name__=='__main__':main()
