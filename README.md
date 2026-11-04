# Hytale ClearView

Mod experimental para o cliente nativo Linux do Hytale, com um painel para controlar separadamente a intensidade de três tipos de neblina. Mantém a iluminação original do jogo.

## Controles

| Tecla | Ação |
| --- | --- |
| **F9** | Abrir/fechar o painel |
| ↑ / ↓ | Selecionar o tipo de neblina |
| ← / → | Ajustar em passos de 5% |
| V | Visão limpa: distância 0%, atmosfera 20%, profundidade 100% |
| R | Restaurar os três controles a 100% |
| Escape | Fechar o painel |

0% remove aquele efeito; 100% preserva a intensidade original definida pelo jogo. Os controles funcionam ao vivo e são salvos automaticamente. O painel é independente das configurações gráficas nativas e usa teclado.

- **Distância:** neblina no horizonte e em terrenos distantes.
- **Atmosfera:** névoa de clima, altura e ambiente.
- **Profundidade:** atenuação pela distância 3D, conforme o ambiente, incluindo água.

O jogo combina esses fatores; remover um não elimina necessariamente os outros. O mod não aumenta a distância de renderização e não remove partículas, nuvens ou toda a coloração subaquática.

[Histórico de mudanças](CHANGELOG.md) · [Controles de neblina](docs/fog-controls.md) · [Validação e diagnóstico](docs/validation.md)

## Estado

A versão anterior, que removia a neblina de distância sem HUD, foi confirmada em uso no Hytale 0.7.5. A versão com HUD passou por testes locais de renderização OpenGL, preservação dos parâmetros dos shaders, intensidade independente, entrada de teclado e persistência. **O HUD ainda aguarda validação integrada dentro do jogo.**

## Requisitos

- Linux x86_64 e cliente nativo Hytale com SDL3/OpenGL.
- Python 3, compilador C (`cc`), `pkg-config` e desenvolvimento Cairo.
- No Ubuntu, as dependências de compilação incluem `build-essential`, `pkg-config` e `libcairo2-dev`.

Instalações nativas e Flatpak são detectadas. Se ambas existirem, informe `--client-dir`. Não instalar sobre outro proxy SDL, como Aurora.

## Instalar ou atualizar

Feche o Hytale completamente e, nesta pasta, execute:

```bash
./install.sh
```

Abra o jogo pelo launcher normal. A instalação preserva os ajustes já salvos. Na primeira instalação, o padrão é distância 0%, atmosfera 100%, profundidade 100%.

Para escolher explicitamente um preset inicial:

```bash
./install.sh --mode distance
```

| Preset | Distância | Atmosfera | Profundidade |
| --- | --- | --- | --- |
| `distance` | 0% | 100% | 100% |
| `atmosphere` | 0% | 0% | 100% |
| `all` | 0% | 0% | 0% |
| `off` | 100% | 100% | 100% |

`off` mantém o painel disponível. Usar `--mode` redefine os três sliders para o preset escolhido.

Cliente em outro caminho:

```bash
./install.sh --client-dir "/caminho/Client"
```

## Remover

Com o jogo fechado:

```bash
./install.sh --uninstall
```

O instalador restaura `libSDL3.clearview-original.so` para `libSDL3.so` após verificar o hash do backup. Configurações e log permanecem em `Client/.clearview/`.

Se uma atualização substituir a SDL e deixar o backup antigo, o instalador interrompe a reinstalação para permitir revisão dos arquivos. Não descarta o backup automaticamente.

## Funcionamento

Um proxy SDL encaminha as chamadas para a biblioteca original e intercepta o envio dos shaders ao OpenGL. O código transforma funções reconhecidas de neblina, adicionando multiplicadores controlados por uniforms. Isso mantém os parâmetros exigidos pelo cliente ativos durante a otimização do GLSL.

O HUD é desenhado com Cairo/OpenGL antes da apresentação do quadro. O estado gráfico alterado pelo painel é restaurado. O executável `HytaleClient` permanece intacto.

O código é independente. Aurora Shaders foi estudado como referência de arquitetura; este repositório não inclui código/shaders de Aurora/Complementary nem distribui shaders ou bibliotecas originais do Hytale.

## Diagnóstico

- `Client/.clearview/hook.log`: carregamento e transformação dos shaders.
- `Client/.clearview/settings`: intensidades de distância, atmosfera e profundidade, entre 0 e 1.
- `Client/.clearview/receipt.json`: hash de integridade do backup da SDL.

Atualizações do jogo podem alterar as assinaturas dos shaders. Fontes não reconhecidas passam sem modificação. Multiplayer ainda não foi validado.

## Desenvolvimento e testes

```bash
bash build.sh
python3 tests/check.py
python3 tests/check_hud.py
python3 tests/check_gl.py /caminho/dos/shaders-extraidos-localmente
```

`check.py` usa um cliente simulado em uma pasta temporária; não modifica a instalação real. Verifica encaminhamento SDL, segmentos GLSL, uniforms, teclas, persistência e restauração exata da biblioteca original.

`check_hud.py` requer Pillow e EGL/OpenGL. Renderiza o painel, verifica restauração do estado gráfico e gera `build/hud-preview.png`.

`check_gl.py` requer EGL/OpenGL e shaders extraídos localmente da sua própria instalação. Testa a interface dos programas Text/BasicFog e renderiza os fatores de neblina para conferir valores intermediários. Esses shaders não são distribuídos neste repositório.

## Branches

- `main`: base principal do projeto.
- `staging`: desenvolvimento e validação antes de integrar à `main`.
