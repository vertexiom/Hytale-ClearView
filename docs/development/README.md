# Desenvolvimento

Documentação para quem deseja estudar ou contribuir com o ClearView.

- [GUI Linux GTK 4: execução e dependências](../../installer/linux/gui/LEIA-ME.txt)
- [Arquitetura e diagnóstico](architecture.md)
- [Validação e testes](validation.md)
- [Ambiente de testes: hardware, sistema e ferramentas](test-environment.md)
- [Implementação Windows e critérios P0/P1](windows.md)

## Compilação Linux

Requer Python 3, compilador C, pkg-config e Cairo e FreeType de desenvolvimento. As fontes Inter distribuídas com o projeto são embutidas no mod; não dependem das fontes instaladas pelo jogador.

```bash
bash tools/build/build_linux.sh
python3 tests/check.py
python3 tests/check_hud.py
python3 tests/check_gl.py /caminho/dos/shaders-extraidos-localmente
```

Os testes gráficos requerem EGL/OpenGL; o teste do HUD também usa Pillow. Nunca inclua shaders ou bibliotecas do jogo nos commits.

## Fluxo de trabalho

`staging` recebe desenvolvimento e validação. `main` reúne as versões publicadas. A primeira versão pública é **v0.1.0**; as numerações anteriores nos registros de protótipos eram internas.

## Organização do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `assets/icons/` | Ícones usados pelo aplicativo e pelos pacotes |
| `src/` | Código do shader, proxies e painel |
| `tests/` | Testes de instalação, gráficos e integração |
| `docs/development/` | Arquitetura, validação e instruções para contribuir |
| `installer/linux/` | Implementação do instalador Linux |
| `installer/windows/` | Interface e implementação do instalador Windows |
| `tools/build/` | Compilação, geração de exports e empacotamento |
| `tools/support/` | Coleta de diagnóstico para desenvolvimento/suporte |
| `install.sh` | Entrada simples para instalar no Linux |

`build/` e `dist/` são saídas locais geradas, ignoradas pelo Git. Os downloads para jogadores ficam na Release; não versionar binários no código-fonte.

Protótipos HTML/Pencil, capturas de experimentos, estudos ASCII e notas de sessão ficam apenas na máquina de desenvolvimento, fora do versionamento. O repositório mantém código, recursos usados pelo produto, ferramentas de build, testes automatizados e documentação necessária para manutenção.

## HUD v0.1.3

O painel usa uma textura de cobertura para os textos, atualizada somente por entrada/estado sujo. Cores, cartões e barras são compostos no mesmo desenho OpenGL. As transições de seleção e barras usam ease-out de 120 ms, com atualizações visuais limitadas a 30 Hz; o último quadro pode ocorrer até um intervalo depois. O valor da neblina e o número exibido mudam imediatamente.

Não há thread ou timer de animação. Fechar o painel ou perder foco cancela o movimento; reabrir mostra o estado atual. Com o painel parado não se interpola nem rasteriza novamente; desenhar o HUD visível ainda tem custo. Defina `CLEARVIEW_REDUCED_MOTION=1` no ambiente do launcher do jogo para desativar as transições. No Windows, a preferência de animações da área de cliente também é lida ao abrir o HUD pela primeira vez.
