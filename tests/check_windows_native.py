# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real Windows/PowerShell backend tests in temporary directories; no game or GPU."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--powershell', required=True)
    parser.add_argument('--report', default='build/ci/windows-backend.json')
    args = parser.parse_args()
    if os.name != 'nt':
        raise SystemExit('This test requires native Windows; Linux/Wine is not a substitute.')
    results = []
    passed = False
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    try:
        version = subprocess.run([args.powershell, '-NoProfile', '-Command', '$PSVersionTable.PSVersion.ToString()'], capture_output=True, text=True, check=True)
        assert version.stdout.strip().startswith('5.1.'), version.stdout
        with tempfile.TemporaryDirectory(prefix="ClearView native espaço ' ") as tmp:
            base = Path(tmp); package = base/'package'; package.mkdir(); (package/'bin').mkdir()
            (package/'install.ps1').write_text((ROOT/'installer/windows/install.ps1').read_text(encoding='utf-8-sig'), encoding='utf-8-sig')
            binary = (ROOT/'build/windows/opengl32.dll').read_bytes()
            (package/'bin/opengl32.dll').write_bytes(binary)
            shutil.copy2(ROOT/'build/windows/manifest.json', package/'manifest.json')
            client = base/"Client ' unicode ç $literal"; client.mkdir()
            # Valid PE fixture, never executed. No Hytale download or credentials.
            shutil.copy2(ROOT/'build/windows/clearview-smoke.exe', client/'HytaleClient.exe')
            original = (client/'HytaleClient.exe').read_bytes()
            live = client/'opengl32.dll'; state = client/'.clearview'
            settings = state/'settings'; receipt = state/'windows-receipt.json'
            def run(name, *switches, success=True):
                process = subprocess.run([args.powershell, '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(package/'install.ps1'), '-ClientDir', str(client), *switches], capture_output=True, text=True, errors='replace', timeout=45)
                results.append({'case':name,'exit_code':process.returncode,'expected_success':success,'stdout':process.stdout,'stderr':process.stderr})
                assert (process.returncode == 0) == success, results[-1]
            run('validate-only', '-ValidateOnly')
            assert not live.exists() and not state.exists()
            (client/'HytaleClient.exe').rename(client/'original.exe')
            run('missing-client', success=False)
            (client/'original.exe').rename(client/'HytaleClient.exe')
            assert not live.exists() and not state.exists()
            live.write_bytes(b'foreign mod')
            run('foreign-mod', success=False); assert live.read_bytes() == b'foreign mod'
            live.unlink()
            run('install'); assert live.read_bytes() == binary
            assert json.loads(receipt.read_text(encoding='utf-8-sig'))['sha256'].lower() == hashlib.sha256(binary).hexdigest()
            settings.write_bytes(b'0.25 0.5 0.75\n')
            run('update'); assert settings.read_bytes() == b'0.25 0.5 0.75\n'
            assert list(state.glob('backup-*.dll'))
            run('preset', '-Mode', 'off'); assert settings.read_text().strip() == '1 1 1'
            (package/'bin/opengl32.dll').write_bytes(b'corrupt')
            run('tampered-package', success=False); assert live.read_bytes() == binary
            (package/'bin/opengl32.dll').write_bytes(binary)
            live.write_bytes(binary+b'changed')
            run('tampered-install-remove', '-Uninstall', success=False)
            assert live.read_bytes() == binary+b'changed'
            live.write_bytes(binary)
            run('remove', '-Uninstall'); assert not live.exists() and not receipt.exists() and settings.exists()
            assert list(state.glob('removed-*.dll'))
            settings.unlink(); receipt.mkdir()
            run('receipt-write-failure-rollback', success=False)
            assert not live.exists() and not settings.exists()
            receipt.rmdir()
            run('reinstall'); assert live.read_bytes() == binary
            run('final-remove', '-Uninstall'); assert not live.exists()
            assert (client/'HytaleClient.exe').read_bytes() == original
        passed = True
        print('PASS: native Windows PowerShell 5.1 install/update/remove, integrity, conflicts, Unicode paths, settings and rollback')
    finally:
        report.write_text(json.dumps({'passed':passed,'scope':'temporary fixture directories; no UI, OpenGL or gameplay certification','cases':results}, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
