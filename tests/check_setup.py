"""Verify the GUI executable and workflow ordering without claiming native UI tests."""
from pathlib import Path
import argparse,json,os,subprocess,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pwsh',required=True);args=ap.parse_args()
    version=json.loads((ROOT/'build/windows/manifest.json').read_text())['version']
    exe=ROOT/'dist'/f'ClearView-{version}-Setup.exe'
    pe=subprocess.check_output(['objdump','-p',str(exe)],text=True)
    assert 'Windows GUI' in pe and 'pei-x86-64' in pe
    data=exe.read_bytes()
    assert 'asInvoker'.encode() in data
    assert (ROOT/'build/windows/payload.zip').read_bytes() in data
    assert (ROOT/'installer/windows/setup.ps1').read_text().encode('utf-8-sig') in data
    with zipfile.ZipFile(ROOT/'build/windows/payload.zip') as z:
        assert z.testzip() is None and not any(n.endswith('.bat') for n in z.namelist())
    with tempfile.TemporaryDirectory(prefix="ClearView espaço 'test' ") as td:
        t=Path(td);engine=t/'fake engine';trace=t/'calls.jsonl';runner=t/'run.ps1';log=t/'log.txt'
        engine.write_text("#!/usr/bin/python3\nimport os,sys,json\nfrom pathlib import Path\na=sys.argv[1:]\nwith open(os.environ['CV_TRACE'],'a') as f:f.write(json.dumps(a)+'\\n')\nfail=os.environ.get('CV_FAIL','')\nif fail=='validate' and '-ValidateOnly' in a:sys.exit(7)\nif fail=='smoke' and any(x.endswith('smoke-test.ps1') for x in a):sys.exit(8)\nprint('ok')\n")
        engine.chmod(0o755)
        generator=t/'generate.ps1'
        generator.write_text('''param($Helper,$Engine,$Payload,$Client,$Log,$Runner,$Operation)
. $Helper
[IO.File]::WriteAllText($Runner,(New-ClearViewOperation -Engine $Engine -Payload $Payload -Client $Client -Log $Log -Operation $Operation))
''')
        client=str(t/"Client 'ç' $literal")
        for operation,fail,count,code in [('install','',3,0),('install','validate',1,7),('install','smoke',2,8),('remove','',1,0)]:
            trace.unlink(missing_ok=True)
            subprocess.run([args.pwsh,'-NoProfile','-File',str(generator),str(ROOT/'installer/windows/workflow.ps1'),str(engine),str(t),client,str(log),str(runner),operation],check=True)
            result=subprocess.run([args.pwsh,'-NoProfile','-File',str(runner)],env={**os.environ,'CV_TRACE':str(trace),'CV_FAIL':fail},capture_output=True,text=True)
            assert result.returncode==code,(result.returncode,result.stderr)
            calls=[json.loads(line) for line in trace.read_text().splitlines()]
            assert len(calls)==count,calls
            for call in calls:
                if '-ClientDir' in call:assert call[call.index('-ClientDir')+1]==client
            if operation=='install':assert '-ValidateOnly' in calls[0]
            else:assert '-Uninstall' in calls[0]
    print('PASS: x64 GUI executable, embedded manifest/payload, no BAT files, workflow ordering, stop on validation/graphics failure, quoted Unicode paths')
if __name__=='__main__':main()
