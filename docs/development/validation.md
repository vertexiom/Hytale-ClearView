# Validação e diagnóstico

Hardware, sistema, driver, Hytale e ferramentas estão registrados no [ambiente de testes](test-environment.md).

## O que foi verificado

- A versão 0.1 iniciou e foi confirmada pelo usuário no Hytale 0.7.5.
- O HUD 0.2 foi renderizado em contexto EGL/OpenGL na NVIDIA RTX 5070.
- O desenho e o redesenho do HUD preservaram o estado gráfico verificado pelo teste, sem erros OpenGL.
- Os programas Text e BasicFog mantiveram seus uniforms e atributos após a transformação.
- Fatores de neblina renderizados confirmaram intensidades independentes, incluindo valores intermediários.
- Eventos, estado de teclado em cache, persistência e atualização de uniforms foram verificados com um cliente simulado.
- A instalação/restauração preservou exatamente os bytes da biblioteca original no teste isolado.
- As dependências da biblioteca com HUD resolveram no runtime Flatpak usado pelo cliente.

**Pendente:** teste integrado do HUD 0.2 dentro do Hytale, comportamento em diferentes mundos/condições e multiplayer. Os testes anteriores não equivalem a essa validação.

## Executar testes

```bash
python3 tests/check.py
python3 tests/check_hud.py
python3 tests/check_gl.py /caminho/dos/shaders-extraidos-localmente
```

O primeiro teste usa uma pasta temporária e uma implementação SDL simulada. Os outros exigem EGL/OpenGL; a prévia também requer Pillow. As fontes GLSL do jogo não são distribuídas e devem vir da própria instalação.

## Erro de inicialização corrigido

O primeiro protótipo usava retorno constante para zerar a neblina. O compilador eliminava `uPosition`, exigido pelo TextProgram, e o cliente encerrava com `Could not find uniform uPosition`.

Os controles atuais usam uniforms dinâmicos, preservando a dependência dos parâmetros originais durante a otimização. `check_gl.py` reproduz o comportamento antigo e verifica a interface corrigida.

## Logs e recuperação

Consulte `Client/.clearview/hook.log` e o log do cliente em `UserData/Logs/`. Uma mensagem de transformação do shader não garante sucesso de compilação/link nem qualidade visual.

Para restaurar a biblioteca original, feche o jogo e execute:

```bash
./install.sh --uninstall
```

Se o jogo atualizar a SDL e deixar um backup antigo, o instalador interrompe a reinstalação para revisão. Não exclua o backup nem restaure uma versão antiga sobre uma biblioteca nova sem verificar os arquivos.

## Hardware e compatibilidade

Referência consultada em 4 de novembro de 2026. Windows 10 x64 1809+ é P0; Windows 11 é P1. A matriz de GPUs no Windows ainda precisa de validação nativa.

O [Hytale](https://hytale.com/news/2025/12/hytale-hardware-requirements) lista i5-7500/Ryzen 3 1200, 8 GB de RAM com GPU dedicada, GTX série 900 e OpenGL 4.1, visando 1080p/30 FPS no preset baixo. O mod não reduz esses requisitos nem garante ganho de FPS.

GPUs anteriores à referência oficial, como a GTX 660, devem ser tratadas como experimentais. A [ficha NVIDIA](https://www.nvidia.com/en-us/geforce/graphics-cards/geforce-gtx-660/specifications/) informa OpenGL 4.3 e 2 GB na placa de referência, mas é necessário verificar o driver real. O [suporte Kepler](https://nvidia.custhelp.com/app/answers/detail/a_id/5202) é legado. Não bloquear por nome de GPU nem usar a estimativa WMI de VRAM como aprovação de compatibilidade.

O proxy Windows registra GPU/OpenGL/GLSL. Sem OpenGL 4.1, encaminha os shaders originais e não ativa o HUD. Funções GLSL desconhecidas também passam sem transformação. Isso não substitui recuperação após falha de compilação/linkedição, ainda pendente.

O ClearView não acrescenta os efeitos pesados de iluminação, reflexos e nuvens do [Aurora](https://github.com/Kristijan1001/Hytale-Aurora-Shaders#performance). O HUD só desenha quando aberto e só atualiza a textura quando necessário; o custo de interceptação e atualização de uniforms precisa ser medido.

## Pendências e medição

- Implementar recuperação para shaders alterados que falhem na compilação/linkedição, preservando a fonte original e o erro.
- Validar instalação, remoção, F9, persistência, Alt+Tab, janela/fullscreen e pelo menos 30 minutos de jogo em Windows 10; repetir no Windows 11.
- Comparar a mesma cena/resolução/distância no jogo original, com neblinas em 100%, com preset de visibilidade e com HUD aberto/fechado. Registrar FPS e tempos de quadro, incluindo picos. Custo abaixo de 5% com HUD fechado é uma meta proposta, não um resultado medido.
- Otimizar uniforms/locks apenas com base no perfil medido; avaliar opção de desativar o HUD para diagnóstico.
- Registrar versão do Hytale, GPU, driver e resultados; repetir após atualizações. Uma máquina aprovada não certifica toda a família de GPUs.

Confirme que o Hytale original funciona antes de investigar o mod. O roteiro Windows detalhado está em [windows.md](windows.md).
