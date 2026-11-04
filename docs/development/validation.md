# Validação e diagnóstico

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
