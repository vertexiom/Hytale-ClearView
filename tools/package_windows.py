"""Build a local test ZIP from verified compiled artifacts. Does not publish anything."""
from pathlib import Path
import hashlib
import json
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    build=ROOT/'build/windows'
    manifest=json.loads((build/'manifest.json').read_text())
    for name,expected in manifest['files'].items():
        if name not in ['opengl32.dll','clearview-smoke.exe']:raise ValueError('Unexpected artifact')
        assert hashlib.sha256((build/name).read_bytes()).hexdigest()==expected, name+' hash mismatch'
    name='ClearView-'+manifest['version']+'-x64'
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    archive=out/(name+'.zip')
    files=['Install.bat','Uninstall.bat','Diagnostics.bat','Smoke Test.bat','install.ps1','diagnostics.ps1','smoke-test.ps1']
    guide='''HYTALE CLEARVIEW - WINDOWS x64 - VERSAO INICIAL v0.1.0

Windows 10 x64 1809+ = P0. Windows 11 = P1. OpenGL 4.1 necessario.
Projeto em versao inicial. Validacao e compatibilidade em andamento.

1. Extraia TODO o ZIP para uma pasta sua.
2. Execute Smoke Test.bat. Se falhar, envie a pasta smoke-* antes de instalar.
3. Feche o Hytale e execute Install.bat.
4. Abra o Hytale pelo launcher normal. F9 abre o painel.
5. Setas cima/baixo selecionam; esquerda/direita ajustam em 5%.
   0% remove a neblina; 100% e o original do jogo.
   V = visao limpa; R = original; Esc fecha o painel.
6. Para remover, feche o jogo e execute Uninstall.bat.
7. Para investigar um problema, execute Diagnostics.bat.

Nao precisa de Python ou compilador para usar este pacote.
Nao instale junto de outro mod que use opengl32.dll no cliente.
Detalhes, caminhos personalizados e roteiro de teste: docs/development/windows.md.
'''
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for file in files:z.write(ROOT/file,name+'/'+file)
        z.write(build/'manifest.json',name+'/manifest.json')
        for file in manifest['files']:z.write(build/file,name+'/bin/'+file)
        z.write(ROOT/'docs/development/windows.md',name+'/docs/development/windows.md')
        z.write(ROOT/'docs/development/hardware-compatibility.md',name+'/docs/development/hardware-compatibility.md')
        z.writestr(name+'/LEIA-ME.txt',guide.replace('\n','\r\n'))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any('/.git/' in n or 'HytaleClient' in n or n.endswith('.so') for n in z.namelist())
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n')
    print(archive)
    print('SHA256:',digest)
if __name__=='__main__':main()
