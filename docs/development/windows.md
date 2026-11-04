# Windows: P0 e P1

## Prioridades e estado

| Plataforma | Prioridade | Estado |
| --- | --- | --- |
| Windows 10 x64 1809+ | **P0** | Compilado; aguarda teste nativo e gameplay. |
| Windows 11 x64 | **P1** | Usa o mesmo pacote; aguarda validação após P0. |
| Linux x86_64 | Regressão | Testes existentes passam após compartilhar o núcleo GLSL. |

O projeto está em sua versão inicial, **v0.1.0**, com validação em andamento. Compilar uma DLL para Windows a partir do Linux não comprova funcionamento no Hytale/Windows.

## Para quem vai testar

1. Extraia o ZIP completo para uma pasta sua, com permissão de escrita. Não execute de dentro do ZIP.
2. Execute `Smoke Test.bat`. Ele abre um contexto gráfico isolado, verifica a DLL e os controles e salva o resultado em uma pasta `smoke-*`. Não altera o Hytale.
3. Se o teste falhar, envie essa pasta ao desenvolvedor antes de instalar no jogo.
4. Feche o Hytale completamente. O launcher pode continuar aberto.
5. Execute `Install.bat`. O instalador tenta localizar o cliente; se necessário, selecione `HytaleClient.exe`.
6. Abra pelo launcher normal. Entre num mundo e pressione **F9**.
7. Ajuste cada controle com as setas. Feche/reabra o jogo para verificar que os valores persistem.
8. Para remover, feche o jogo e execute `Uninstall.bat`.

O jogador não precisa de Python, Zig, Visual Studio, Cairo ou privilégios de administrador. O pacote usa APIs e runtime C do Windows 10+. O driver gráfico precisa oferecer o OpenGL usado pelo Hytale.

Requisitos: Windows 10 x64 1809 (build 17763) ou superior e OpenGL 4.1. O log registra GPU, fornecedor e versões reais de OpenGL/GLSL. Sem OpenGL 4.1, o proxy encaminha os shaders originais e desativa o HUD; isso não torna o próprio Hytale compatível com essa máquina. Consulte a [análise de hardware e limites](hardware-compatibility.md).

## Controles

- **F9:** abrir/fechar o painel.
- **↑/↓:** selecionar distância, atmosfera ou profundidade.
- **←/→:** ajustar em 5%, de 0% a 100%.
- **V:** distância 0%, atmosfera 20%, profundidade 100%.
- **R:** original: os três valores em 100%.
- **Escape:** fechar.

Os valores são salvos em `Client/.clearview/settings`. O painel funciona pelo teclado.

## Instalação personalizada

No PowerShell, dentro da pasta do pacote:

```powershell
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client'
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client' -ValidateOnly
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client' -Uninstall
```

`-Mode distance`, `atmosphere`, `all` ou `off` aplica os mesmos presets iniciais do Linux. Sem `-Mode`, os ajustes existentes são preservados.

O instalador não altera `HytaleClient.exe`, não grava em System32 e não sobrescreve uma `opengl32.dll` de outro mod. Se houver Aurora, ReShade ou outra DLL nesse local, desinstale o outro mod primeiro. A execução do BAT aplica a política de scripts somente àquele processo de PowerShell.

## Diagnóstico

Execute `Diagnostics.bat`. Ele reúne versão do Windows, CPU, RAM, GPU, driver, espaço em discos, versão do PowerShell, hash da DLL, configuração e log do ClearView em uma pasta local. Não transmite dados.

Para caminho personalizado:

```powershell
.\diagnostics.ps1 -ClientDir 'D:\Jogos\Hytale\Client'
```

No log do ClearView, procure:

- `Windows x64 preview loaded`: DLL carregada.
- `patched fog functions`: transformação GLSL reconhecida.
- `presentation hook and F9 input active`: integração de apresentação e teclado ativa.

Se o Hytale não abrir, use `Uninstall.bat` e envie o diagnóstico. O log de cliente em `UserData/Logs` pode ser necessário depois; ele não é coletado automaticamente.

## Critérios P0: Windows 10

Registrar modelo de GPU, driver, build do Windows, versão do Hytale e origem do launcher.

- [ ] Smoke test nativo aprovado no computador alvo.
- [ ] Instalação e remoção sem privilégio de administrador.
- [ ] Cliente inicia pelo launcher e entra num mundo sem erros de shader.
- [ ] F9 abre/fecha; Home não abre o ClearView.
- [ ] Três controles independentes em 0%, 50% e 100%.
- [ ] Verificação de horizonte, névoa de ambiente e profundidade/água.
- [ ] Teclas do painel não acionam ações indevidas do jogo.
- [ ] Valores persistem após reiniciar.
- [ ] Janela, fullscreen, Alt+Tab e redimensionamento sem travamentos.
- [ ] Pelo menos 30 minutos de gameplay, sem erros novos no log.
- [ ] Reinstalação preserva configurações; remoção devolve o visual original.

Uma aprovação em uma GPU não certifica todas as GPUs/driver. Primeiro validar a máquina do amigo; depois ampliar a matriz NVIDIA/AMD/Intel conforme os testadores disponíveis. Repetir os critérios no Windows 11 como P1. Multiplayer permanece não validado.

## Arquitetura

A DLL `opengl32.dll` funciona como proxy local. Encaminha 368 exports da API OpenGL do Windows para a DLL original obtida por caminho absoluto no diretório do sistema. A inicialização pesada ocorre fora de `DllMain`.

O núcleo de transformação GLSL e atualização de uniforms é compartilhado com Linux. O Windows usa WGL para interceptar shaders/apresentação e GDI para rasterizar o painel, sem distribuir Cairo. Configurações usam caminhos Unicode e gravação por substituição. Os caches de programa são por thread e reinicializados ao mudar o contexto WGL.

O instalador verifica arquitetura x64, propriedade/hash da DLL, existência de conflitos e processo do jogo fechado. Atualizações guardam a DLL anterior em `.clearview`; a remoção também preserva uma cópia para recuperação.

## Compilar e testar a partir do Linux

Requer Python 3 e Zig (verificado com 0.15.2):

```bash
python3 tools/build_windows.py --zig /caminho/zig
python3 tests/check_windows.py --pwsh /caminho/pwsh
python3 tools/package_windows.py
```

Os testes do instalador usam PowerShell oficial com detecção de Windows/processo simulada. Eles validam a lógica e operações de arquivo, mas não substituem Windows PowerShell 5.1 nem uma máquina Windows real.

O executável `clearview-smoke.exe` é compilado aqui e deve ser executado no Windows via `Smoke Test.bat`. O teste usa uma pasta temporária e um shader sintético próprio, sem distribuir fontes do Hytale.
