# Instalador Windows WPF

Implementação inicial em C# + WPF (.NET 10), com tema V2, chuva ASCII, navegação por etapas e integração ao backend PowerShell existente. Publicado na v0.1.2; validação nativa Windows ainda pendente.

## Compilar

Gere primeiro o payload Windows com `tools/build/build_windows.py`. Depois, na raiz:

```bash
python3 tools/build/build_windows_wpf.py --dotnet /caminho/do/dotnet
```

Requer .NET SDK 10 e o payload com hashes válidos em `build/windows/`. O projeto habilita compilação com destino Windows a partir do Linux; isso não permite executar a GUI WPF no Linux.

Saída para distribuição: `dist/ClearView-0.1.2-Setup.exe` (cópia do build em `dist/windows-wpf/ClearView-WPF-Setup.exe`). O EXE contém runtime .NET, GUI e payload. Componentes nativos podem ser extraídos pelo runtime ao iniciar. Não usa navegador nem baixa o mod durante a instalação. Recompilar com atualizações de segurança do runtime ao distribuir novas versões.

## Executar no Windows

Para explorar o visual sem alterar o jogo, execute no PowerShell:

```powershell
.\ClearView-WPF-Setup.exe --preview
```

Sem `--preview`, abre o fluxo real. A instalação só inicia ao selecionar o destino e clicar em Instalar. Feche o Hytale antes de instalar, atualizar ou remover. O instalador usa a conta normal do usuário e Windows PowerShell 5.1 do sistema.

A interface permanece em português nesta implementação. A release v0.1.1 permanece inalterada.

## Próximo teste manual

Comece no Windows 10 com `--preview`: percorra as quatro etapas, abra Licença, feche com Esc e navegue com Tab/Enter em escala 100% e 150%. Depois execute sem `--preview`, com o jogo fechado, e valide instalação → F9 no jogo → fechamento do jogo → atualização → remoção. Confirme que uma segunda instância ativa a primeira. Registre falhas com o relatório local. Não considere o fluxo nativo validado apenas por compilação ou execução no Wine.

## Integração

- `MainWindow.xaml` e recursos em `App.xaml`: layout e tokens. Licença GPL completa embutida, acessível sem internet. Foco por etapa e nome acessível do campo de destino; seleção de múltiplos destinos preserva os controles.
- Fontes Inter/JetBrains Mono incorporadas a partir de `assets/fonts/`, com seus avisos originais. O build reúne as licenças dos pacotes de runtime restaurados; o diálogo Licença mostra todos os avisos.
- `RainView.cs`: desenho em um único elemento WPF; partículas limitadas, gotas pelo topo/lateral, colisões e pausa; respeita `ClientAreaAnimation` e suspende ao minimizar.
- `InstallerService.cs`: payload embutido, integridade, subprocesso sem console, progresso por arquivo de etapa, logs e limpeza temporária.
- `wpf-runner.ps1`: usa `New-ClearViewOperation` de `workflow.ps1`, preservando validação → teste gráfico → instalação.
- A remoção usa o mesmo backend e não exige novo teste gráfico.
- Sucesso exige código de saída zero e marcador `complete`; animação não determina progresso.
- O fechamento é bloqueado durante a operação. Mutex/evento compartilham os nomes do instalador anterior para evitar duas instâncias.

Logs: `%LOCALAPPDATA%\ClearView\Logs`. A pasta temporária do payload é exclusiva por operação e removida ao terminar quando possível; os logs persistem.

## Verificar

```bash
python3 tests/check_wpf_runner.py --pwsh /caminho/do/pwsh
```

Esse teste usa processos simulados e caminhos com espaços/apóstrofos; verifica interrupção por falha em cada etapa e conclusão. O mesmo teste é portátil entre PowerShell no Linux e Windows PowerShell 5.1. Para o fluxo nativo automatizado, veja [GitHub Actions](../../../docs/development/windows.md#github-actions). A aprovação no Linux não substitui a execução Windows.

Pendências nativas: abertura offline sem runtime .NET previamente instalado, Win10 primeiro/Win11 depois, DPI 100–200%, teclado/leitor de tela, múltiplos monitores, renderização por software/GPU antiga, custo da chuva, instância única, instalação/atualização/remoção reais e recuperação. A compatibilidade 1809 anunciada pelo backend precisa ser revalidada com este runtime. Assinatura Authenticode permanece separada na P2.
