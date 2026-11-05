"""Validate and exercise an extracted package without installing it or touching Hytale."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
deb=Path(sys.argv[1]) if len(sys.argv)>1 else root/'dist/clearview-installer_0.1.2-1_amd64.deb'
with tempfile.TemporaryDirectory(prefix='clearview-package-test-') as tmp:
    base=Path(tmp);tree=base/'extracted'
    subprocess.run(['dpkg-deb','-R',str(deb),str(tree)],check=True)
    assert not any((tree/'DEBIAN'/name).exists() for name in ('preinst','postinst','prerm','postrm'))
    assert not list(tree.rglob('libSDL3.clearview-original.so'))
    for line in (tree/'DEBIAN/md5sums').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.md5((tree/name).read_bytes()).hexdigest()==digest,name
    app=tree/'usr/lib/clearview';client=base/'fake client with spaces';client.mkdir()
    (client/'HytaleClient').write_bytes(b'fixture')
    original=b'original SDL fixture';(client/'libSDL3.so').write_bytes(original)
    command=['/usr/bin/python3',str(app/'installer/linux/install.py'),'--client-dir',str(client),'--payload',str(app/'build/libSDL3.so'),'--json']
    def execute(*extra):
        result=subprocess.run(command+list(extra),cwd=base,text=True,capture_output=True,check=True)
        events=[json.loads(line) for line in result.stdout.splitlines()]
        assert events[-1]['event']=='complete',events
        return events[-1]
    assert execute()['operation']=='install'
    (client/'.clearview/settings').write_text('0.1 0.2 0.3\n')
    assert execute()['operation']=='update'
    assert (client/'.clearview/settings').read_text()=='0.1 0.2 0.3\n'
    assert execute('--uninstall')['operation']=='remove'
    assert (client/'libSDL3.so').read_bytes()==original
    print('PASS: packaged manifest/files, no game libraries or maintainer scripts, install/update/remove outside checkout')
