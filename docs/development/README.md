# Desenvolvimento

Documentação para quem deseja estudar ou contribuir com o ClearView.

- [GUI Linux GTK 4: execução e dependências](../../installer/linux/gui/LEIA-ME.txt)
- [Contexto da v0.1.2 e próxima sessão](../../CONTEXTO-v0.1.2.md)
- [Prévia interativa do instalador V2](../../design/installer/interactive.html)
- [Arquitetura e diagnóstico](architecture.md)
- [Validação e testes](validation.md)
- [Ambiente de testes: hardware, sistema e ferramentas](test-environment.md)
- [Implementação Windows e critérios P0/P1](windows.md)

## Compilação Linux

Requer Python 3, compilador C, pkg-config e Cairo de desenvolvimento.

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
| `design/installer/` | Estudos visuais, exportações Pencil e prévia HTML V2 |
| `tools/preview/` | Estudos ASCII de terminal |
| `src/` | Código do shader, proxies e painel |
| `tests/` | Testes de instalação, gráficos e integração |
| `docs/development/` | Arquitetura, validação e instruções para contribuir |
| `installer/linux/` | Implementação do instalador Linux |
| `installer/windows/` | Interface e implementação do instalador Windows |
| `tools/build/` | Compilação, geração de exports e empacotamento |
| `tools/support/` | Coleta de diagnóstico para desenvolvimento/suporte |
| `install.sh` | Entrada simples para instalar no Linux |

`build/` e `dist/` são saídas locais geradas, ignoradas pelo Git. Os downloads para jogadores ficam na Release; não versionar binários no código-fonte.
