#!/usr/bin/env python3
"""Install/uninstall the ClearView SDL proxy without modifying HytaleClient."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MARKER = b"HYTALE_CLEARVIEW_PROXY_V1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned(path):
    return path.is_file() and MARKER in path.read_bytes()


def stopped(client):
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if (proc / 'exe').resolve() == client / 'HytaleClient':
                raise RuntimeError('Feche o Hytale antes de instalar, configurar ou remover.')
        except (OSError, PermissionError):
            pass


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(prefix='.clearview-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-dir', type=Path)
    parser.add_argument('--mode', choices=['off', 'distance', 'atmosphere', 'all'])
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    candidates = [Path.home() / '.var/app/com.hypixel.HytaleLauncher/data/Hytale',
                  Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'Hytale']
    candidates = [p / 'install/release/package/game/latest/Client' for p in candidates]
    if args.client_dir:
        candidates = [args.client_dir.expanduser()]
    found = [p.resolve() for p in candidates if (p / 'HytaleClient').is_file()]
    if len(found) != 1:
        raise RuntimeError('Informe --client-dir: nenhum cliente encontrado ou há mais de um.')
    client = found[0]
    stopped(client)
    live = client / 'libSDL3.so'
    backup = client / 'libSDL3.clearview-original.so'
    state = client / '.clearview'
    receipt = state / 'receipt.json'
    if args.uninstall:
        if not owned(live):
            print('ClearView não está ativo. Biblioteca atual preservada.')
            return
        if not backup.is_file() or not receipt.is_file():
            raise RuntimeError('Backup/recibo ausente; restauração automática interrompida.')
        if digest(backup) != json.loads(receipt.read_text())['original_sha256']:
            raise RuntimeError('Backup SDL mudou; restauração automática interrompida.')
        os.replace(backup, live)
        receipt.unlink()
        print('ClearView removido; SDL original restaurada. Configuração/log mantidos em .clearview.')
        return
    if live.is_symlink() or not live.is_file():
        raise RuntimeError('libSDL3.so ausente ou é um link; instalação interrompida.')
    if (client / 'libSDL3.aurora-original.so').exists():
        raise RuntimeError('Aurora detectado. Desinstale-o antes de instalar ClearView.')
    if owned(live):
        if not backup.is_file() or not receipt.is_file():
            raise RuntimeError('Instalação incompleta: backup ou recibo ausente.')
        if digest(backup) != json.loads(receipt.read_text())['original_sha256']:
            raise RuntimeError('Backup alterado; instalação interrompida.')
    elif backup.exists():
        raise RuntimeError('SDL mudou desde a instalação. Preserve o backup e revise antes de reinstalar.')
    subprocess.run(['bash', str(ROOT / 'tools/build/build_linux.sh')], check=True)
    state.mkdir(exist_ok=True)
    mode_path = state / 'mode'
    mode = args.mode or (mode_path.read_text().strip() if mode_path.exists() else 'distance')
    if mode not in ['off', 'distance', 'atmosphere', 'all']:
        raise RuntimeError('Modo inválido.')
    if not owned(live):
        # Keep the live library in place until the proxy is fully ready.
        shutil.copy2(live, backup)
        atomic_write(receipt, (json.dumps({'original_sha256': digest(backup)}, indent=2) + '\n').encode())
    atomic_write(mode_path, (mode + '\n').encode())
    settings = state / 'settings'
    if args.mode or not settings.exists():
        presets = {'off': '1 1 1', 'distance': '0 1 1', 'atmosphere': '0 0 1', 'all': '0 0 0'}
        atomic_write(settings, (presets[mode] + '\n').encode())
    atomic_write(live, (ROOT / 'build/libSDL3.so').read_bytes())
    print(f'ClearView instalado: {client}\nModo: {mode}. Inicie pelo launcher normal.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f'ClearView: {exc}')
