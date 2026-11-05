#!/usr/bin/env python3
"""Linux installer backend. GUI and CLI share validation and rollback."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[2]
VERSION = '0.1.2'
MARKER = b'HYTALE_CLEARVIEW_PROXY_V1'
PRESETS = {'off': '1 1 1', 'distance': '0 1 1', 'atmosphere': '0 0 1', 'all': '0 0 0'}

class InstallError(RuntimeError):
    def __init__(self, message, code='validation'):
        super().__init__(message)
        self.code = code

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def owned(path):
    return path.is_file() and MARKER in path.read_bytes()

def discover():
    bases = [Path.home()/'.var/app/com.hypixel.HytaleLauncher/data/Hytale',
             Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'Hytale']
    return list(dict.fromkeys(p.resolve() for base in bases
        if (p := base/'install/release/package/game/latest/Client').is_dir()
        and (p/'HytaleClient').is_file()))

def stopped(client):
    target = client/'HytaleClient'
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            exe = os.readlink(proc/'exe')
        except (OSError, PermissionError):
            continue
        # Refuse any Hytale client: it may run in a Flatpak mount namespace.
        if Path(exe.removesuffix(' (deleted)')).name == 'HytaleClient' or exe == str(target):
            raise InstallError('Feche o Hytale antes de instalar, atualizar ou remover.', 'running')

def atomic_write(path, data, permissions=0o644):
    fd, name = tempfile.mkstemp(prefix='.clearview-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), permissions)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        Path(name).unlink(missing_ok=True)

def regular(path, required=False):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise InstallError(f'Arquivo inesperado ou link simbólico: {path.name}. Operação interrompida.')
    if required and not path.is_file():
        raise InstallError(f'Arquivo necessário ausente: {path.name}.')

def validate(client):
    client = Path(client).expanduser().resolve(strict=True)
    if not client.is_dir(): raise InstallError('Selecione a pasta Client do Hytale.')
    regular(client/'HytaleClient', True)
    live, backup, state = client/'libSDL3.so', client/'libSDL3.clearview-original.so', client/'.clearview'
    regular(live, True); regular(backup)
    if state.is_symlink() or (state.exists() and not state.is_dir()):
        raise InstallError('A pasta .clearview é um link ou não é um diretório.')
    for name in ('receipt.json','settings','mode'): regular(state/name)
    stopped(client)
    if (client/'libSDL3.aurora-original.so').exists():
        raise InstallError('Aurora detectado. Remova o outro mod antes de instalar ClearView.', 'conflict')
    installed = owned(live)
    if installed:
        regular(backup, True); regular(state/'receipt.json', True)
        try:
            receipt = json.loads((state/'receipt.json').read_text())
            expected = receipt['original_sha256']
        except (ValueError, TypeError, KeyError) as exc:
            raise InstallError('Recibo do backup inválido. Restauração automática interrompida.') from exc
        if digest(backup) != expected:
            raise InstallError('O backup da SDL foi alterado. Operação interrompida.')
    elif backup.exists() or (state/'receipt.json').exists():
        raise InstallError('A biblioteca do jogo mudou desde a instalação. Preserve o backup e revise antes de continuar.', 'conflict')
    return client, installed

@contextmanager
def locked(client):
    fd = os.open(client, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise InstallError('Outra operação do ClearView está em andamento nesta pasta.', 'busy') from exc
        yield
    finally: os.close(fd)

def payload_bytes(payload):
    payload = Path(payload)
    regular(payload, True)
    regular(payload.with_name('linux-manifest.json'), True)
    data = payload.read_bytes()
    try:
        manifest = json.loads(payload.with_name('linux-manifest.json').read_text())
        valid = manifest['sha256'] == hashlib.sha256(data).hexdigest() and manifest['version'] == VERSION
    except (ValueError, TypeError, KeyError) as exc:
        raise InstallError('Manifesto do pacote inválido.', 'package') from exc
    if not valid or MARKER not in data or data[:5] != b'\x7fELF\x02' or data[18:20] != b'\x3e\x00':
        raise InstallError('Pacote Linux x64 ausente, incompatível ou alterado. Gere novamente o pacote.', 'package')
    return data

def transact(client, installed, data, mode, uninstall=False):
    live, backup, state = client/'libSDL3.so', client/'libSDL3.clearview-original.so', client/'.clearview'
    paths = [live, backup, state/'receipt.json', state/'mode', state/'settings']
    before = {p: (p.read_bytes(), stat.S_IMODE(p.stat().st_mode)) if p.exists() else None for p in paths}
    had_state = state.exists()
    changed = []
    def write(p, content, permissions=0o644):
        # Record before entering atomic_write, which may fail after replacement.
        changed.append(p); atomic_write(p, content, permissions)
    try:
        state.mkdir(exist_ok=True)
        if uninstall:
            write(live, before[backup][0], before[backup][1])
            if digest(live) != hashlib.sha256(before[backup][0]).hexdigest():
                raise InstallError('A restauração não passou na verificação final.')
            for p in (state/'receipt.json', backup):
                changed.append(p); p.unlink()
        else:
            selected = mode or ((state/'mode').read_text().strip() if (state/'mode').exists() else 'distance')
            if selected not in PRESETS: raise InstallError('Modo de neblina inválido.')
            if not installed: write(backup, before[live][0], before[live][1])
            original_hash = digest(backup)
            write(state/'receipt.json', (json.dumps({'original_sha256':original_hash,
                'version':VERSION,'installed_sha256':hashlib.sha256(data).hexdigest()},indent=2)+'\n').encode())
            if mode is not None or not (state/'mode').exists():write(state/'mode',(selected+'\n').encode())
            if mode is not None or not (state/'settings').exists():write(state/'settings',(PRESETS[selected]+'\n').encode())
            # Last mutation: original remains live until metadata and backup are ready.
            write(live,data,before[live][1])
            if digest(live) != hashlib.sha256(data).hexdigest() or digest(backup) != original_hash:
                raise InstallError('Os arquivos instalados não passaram na verificação final.')
    except Exception as exc:
        failures=[]
        for p in dict.fromkeys(reversed(changed)):
            try:
                old=before[p]
                if old is None:p.unlink(missing_ok=True)
                else:atomic_write(p,old[0],old[1])
            except OSError: failures.append(p.name)
        if not had_state:
            try:state.rmdir()
            except OSError:pass
        if failures:
            raise InstallError('Falha na operação e na recuperação de: '+', '.join(failures)+'. Não abra o jogo; consulte o relatório.', 'recovery') from exc
        raise InstallError(f'Operação cancelada; os arquivos anteriores foram restaurados. Motivo: {exc}', 'rolled_back') from exc

def perform(client, payload=None, mode=None, uninstall=False, progress=lambda *_:None):
    client = Path(client).expanduser().resolve(strict=True)
    with locked(client):
        progress(0,'Verificando instalação e backup' if uninstall else 'Verificando arquivos do jogo')
        client, installed = validate(client)
        if uninstall and not installed:
            raise InstallError('ClearView não está instalado nesta pasta; nada foi alterado.', 'not_installed')
        progress(1,'Conferindo restauração' if uninstall else 'Verificando integridade do pacote Linux')
        data = None if uninstall else payload_bytes(payload)
        # Repeat process/backup checks immediately before modifying anything.
        validate(client)
        progress(2,'Restaurando arquivos originais' if uninstall else 'Instalando e conferindo arquivos')
        transact(client, installed, data, mode, uninstall)
        return {'operation':'remove' if uninstall else 'update' if installed else 'install',
                'client':str(client),'version':VERSION,'settings_preserved':mode is None}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--client-dir',type=Path)
    ap.add_argument('--mode',choices=PRESETS)
    ap.add_argument('--uninstall',action='store_true')
    ap.add_argument('--payload',type=Path,help='Use precompiled payload (no build on target)')
    ap.add_argument('--validate-only',action='store_true')
    ap.add_argument('--json',action='store_true',help='Structured GUI events on stdout')
    args=ap.parse_args()
    def emit(kind,**values):
        if args.json: print(json.dumps({'event':kind,**values},ensure_ascii=False),flush=True)
        elif kind=='progress':print(values['message'],flush=True)
        elif kind=='complete':print('ClearView '+('removido' if args.uninstall else 'instalado')+f": {values['client']}")
        elif kind=='error':print('ClearView: '+values['message'],flush=True)
    try:
        candidates=[args.client_dir] if args.client_dir else discover()
        if len(candidates)!=1:raise InstallError('Selecione o HytaleClient: nenhuma instalação encontrada ou há mais de uma.')
        client,installed=validate(candidates[0])
        if args.validate_only:
            emit('validated',client=str(client),installed=installed);return 0
        payload=args.payload
        if not args.uninstall and payload is None:
            # Legacy developer CLI: the real GUI always supplies the packaged payload.
            subprocess.run(['bash',str(ROOT/'tools/build/build_linux.sh')],check=True,stdout=subprocess.DEVNULL if args.json else None)
            payload=ROOT/'build/libSDL3.so'
        result=perform(client,payload,args.mode,args.uninstall,lambda n,m:emit('progress',stage=n,message=m))
        emit('complete',**result);return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        emit('error',code=getattr(exc,'code','io'),message=str(exc));return 1

if __name__=='__main__':raise SystemExit(main())
