# Windows: P0 e P1

> **Interface Windows V2 pendente:** o design foi aprovado em protótipos locais, mas ainda não foi integrado ao EXE. Os metadados de build usam 0.1.2; o download público Windows permanece na v0.1.1. As seções abaixo descrevem o instalador existente. Acompanhe a integração na [issue P1](https://github.com/vertexiom/Hytale-ClearView/issues/2).


## Prioridades e estado

| Plataforma | Prioridade | Estado |
| --- | --- | --- |
| Windows 10 x64 1809+ | **P0** | Teste relatado por Lazan, membro do MUP, na v0.1.1; roteiro completo ainda em andamento. |
| Windows 11 x64 | **P1** | Teste relatado pelo mantenedor na v0.1.1; roteiro completo ainda em andamento. |
| Linux x86_64 | Regressão | Testes existentes passam após compartilhar o núcleo GLSL. |

O projeto está em sua versão inicial, **v0.1.1**, com validação em andamento. Compilar uma DLL para Windows a partir do Linux não comprova funcionamento no Hytale/Windows.

## Para quem vai testar

1. Abra `ClearView-0.1.1-Setup.exe` com o Hytale fechado.
2. Confirme a pasta detectada ou use **Localizar** para selecionar `HytaleClient.exe`.
3. Clique em **Instalar / Atualizar**. Acompanhe a barra por etapas: validação do destino, teste gráfico isolado e instalação. O teste gráfico tem limite de 60 segundos e ocorre antes de alterar o jogo.
4. Aguarde **Instalação concluída**, clique em **Concluir** e abra o jogo pelo launcher normal. Entre num mundo e pressione **F9**.
5. Para remover, abra o mesmo executável e clique em **Remover**.

Requisitos: Windows 10 x64 1809+ e OpenGL 4.1. O usuário não instala compiladores ou runtimes adicionais. O instalador usa Windows PowerShell 5.1 e Windows Forms presentes no sistema. A execução não muda a política global de scripts nem exige administrador automaticamente.

Sem o Hytale instalado, a instalação fica desabilitada e a interface orienta a instalar o jogo pelo launcher. **Verificar novamente** repete a detecção. O ClearView não baixa o jogo. Abrir novamente o executável tenta restaurar a janela existente. A conclusão exige sucesso do processo e uma marca final gravada após todas as etapas; a barra representa etapas, não porcentagem de bytes copiados.

## Implementação do instalador

`installer/windows/bootstrap.c` é um executável GUI x64 com manifesto `asInvoker`. Extrai a interface e um payload próprio para uma pasta temporária exclusiva, executa o PowerShell do diretório do sistema sem console e limpa os arquivos ao sair normalmente.

`installer/windows/setup.ps1` fornece a interface. O trabalho ocorre em processo separado para manter a janela responsiva. O fechamento é bloqueado durante a operação para evitar interromper uma gravação. `installer/windows/workflow.ps1` monta a sequência validação → teste gráfico → instalação e interrompe na primeira falha. A remoção usa as verificações do backend, sem exigir aprovação no teste gráfico.

`installer/windows/install.ps1` continua como backend de arquivos, com verificação de integridade, conflitos e recuperação. A UI passa caminhos por argumentos devidamente escapados. O teste gráfico usa fontes sintéticas próprias; fontes do jogo não são distribuídas.

Os relatórios persistem em `%LOCALAPPDATA%/ClearView/Logs` e podem ser abertos em **Ver relatório**. Nada é transmitido. O executável ainda não tem assinatura Authenticode; a reputação/avisos do Windows dependem do ambiente. Não instruir o jogador a desativar proteções do sistema.

A interface foi compilada e analisada sintaticamente no Linux. Sua apresentação, DPI e comportamento nativo ainda precisam ser verificados em Windows real. Consulte a [análise de hardware](validation.md#hardware-e-compatibilidade).

## Controles

- **F9:** abrir/fechar o painel.
- **↑/↓:** selecionar distância, atmosfera ou profundidade.
- **←/→:** ajustar em 5%, de 0% a 100%.
- **V:** distância 0%, atmosfera 20%, profundidade 100%.
- **R:** original: os três valores em 100%.
- **Escape:** fechar.

Os valores são salvos em `Client/.clearview/settings`. O painel funciona pelo teclado.

## Instalação personalizada

Para desenvolvimento, estes comandos se aplicam ao payload já extraído em `build/windows/payload.zip`, que reúne o backend, o manifesto e a DLL. Extraia esse arquivo e abra o PowerShell na pasta resultante:

```powershell
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client'
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client' -ValidateOnly
.\install.ps1 -ClientDir 'D:\Jogos\Hytale\Client' -Uninstall
```

`-Mode distance`, `atmosphere`, `all` ou `off` aplica os mesmos presets iniciais do Linux. Sem `-Mode`, os ajustes existentes são preservados.

O instalador não altera `HytaleClient.exe`, não grava em System32 e não sobrescreve uma `opengl32.dll` de outro mod. Se houver Aurora, ReShade ou outra DLL nesse local, desinstale o outro mod primeiro. O instalador aplica a política de scripts somente aos seus processos de PowerShell.

## Diagnóstico

Para diagnóstico técnico adicional, execute `tools/support/diagnostics.ps1` do código-fonte. Ele reúne versão do Windows, CPU, RAM, GPU, driver, espaço em discos, versão do PowerShell, hash da DLL, configuração e log do ClearView em uma pasta local. Não transmite dados.

Para caminho personalizado:

```powershell
.\tools\support\diagnostics.ps1 -ClientDir 'D:\Jogos\Hytale\Client'
```

No log do ClearView, procure:

- `Windows x64 preview loaded`: DLL carregada.
- `patched fog functions`: transformação GLSL reconhecida.
- `presentation hook and F9 input active`: integração de apresentação e teclado ativa.

Se o Hytale não abrir, use **Remover** no instalador e envie o diagnóstico. O log de cliente em `UserData/Logs` pode ser necessário depois; ele não é coletado automaticamente.

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
python3 tools/build/build_windows.py --zig /caminho/zig
python3 tests/check_windows.py --pwsh /caminho/pwsh
python3 tools/build/package_windows.py --zig /caminho/zig
python3 tests/check_setup.py --pwsh /caminho/pwsh
python3 tests/check_smoke_runner.py --pwsh /caminho/pwsh
```

Os testes do instalador usam PowerShell oficial com detecção de Windows/processo simulada. Eles validam a lógica e operações de arquivo, mas não substituem Windows PowerShell 5.1 nem uma máquina Windows real.

O executável `clearview-smoke.exe` é compilado aqui e é executado automaticamente pelo instalador no Windows. O teste usa uma pasta temporária e um shader sintético próprio, sem distribuir fontes do Hytale.

## Resultado gráfico e falhas do instalador

Uma linha informativa `OpenGL: ...` não indica falha. A classificação usa a etapa interrompida e os resultados explícitos do teste. O runner registra o código de saída de cada etapa e captura erros antes de parar. O teste gráfico usa `System.Diagnostics.Process` com captura assíncrona de stdout/stderr e código de saída explícito, sem depender do objeto retornado por `Start-Process -PassThru`.

`check_smoke_runner.py` cobre sucesso e falha de processos rápidos e a classificação de um relatório com OpenGL e PASS. Executa no Linux com processos substitutos; não comprova a execução no Windows PowerShell 5.1 nem dentro do Hytale.
