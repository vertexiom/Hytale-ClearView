# Changelog

## v0.1.3 — em desenvolvimento / unreleased

- HUD redesenhado com cartões arredondados, paleta azul, fonte Inter embutida, teclas de atalho e barras sem marcadores de mouse.
- Transições de seleção e barras de 120 ms, limitadas a 30 Hz, com textos em cache e opção de movimento reduzido.
- Código da v0.1.3 promovido para `main`; os pacotes da release pública permanecem na v0.1.2.
- A v0.1.2 permanece como versão estável.

## v0.1.2 — estável / stable

Declarada estável pelo mantenedor em 2026-11-05, após confirmação de uso no Linux e Windows. Próximo ciclo de desenvolvimento: v0.1.3, na branch `staging`.

### Instaladores Linux e Windows

- Novo instalador Windows em C# + WPF: visual V2, etapas, seleção do destino, progresso real, falhas com relatório local e conclusão. Atualização e remoção usam o backend existente.
- EXE x64 único com runtime .NET incluído; ícone de planeta, fontes Inter/JetBrains Mono, chuva com cache dos caracteres e opção de pausa. Licença e avisos de terceiros acessíveis sem internet.
- Modo `--preview` opcional demonstra as telas sem alterar o jogo; execução normal permite instalação real.
- Compilação, integridade do pacote e testes automatizados da ponte PowerShell aprovados. O mantenedor posteriormente confirmou o funcionamento no Windows real. Isso não constitui certificação de todas as versões do Windows ou combinações de hardware.
- Instalador Windows v0.1.1 permanece disponível e inalterado.
- Linux: decoração da janela sem CSS global, registro do nome/ícone no desktop e pacote público atualizado.

- Chuva ASCII distribuída por toda a área do painel, com entrada pelo topo e pela lateral, maior densidade e mistura de gotas que atravessam ou colidem com o texto.
- Identificação do instalador ajustada para `Linux · v0.1.2`.

- Ícone temporário do instalador substituído pelo planeta ASCII, com transparência externa e paleta adaptada ao launcher.

### Instalador Linux por pasta

- Distribuição Linux por pasta com mod pré-compilado: `bash install.sh` abre diretamente a GUI. Dependências ausentes são informadas antes de abrir; CLI disponível com `--cli`.
- Ícone de planeta aplicado ao instalador; `.deb` preservado como alternativa, deixando de ser o fluxo prioritário.

- Pacote `.deb` local amd64 com GUI, mod compilado, dependências e entrada no menu de aplicativos. O usuário final não precisa compilar o mod.
- Pacote verificado fora do checkout; instalação/remoção/reinstalação do aplicativo verificadas nesta máquina Ubuntu. Outros sistemas Linux ainda precisam de validação.

- GUI Linux real em Python + GTK 4: visual V2, chuva ASCII/Cairo, seleção nativa/Flatpak, instalação, atualização, remoção, progresso por etapas e relatório local. Modo `--demo` separado.
- Backend Linux com verificação do pacote, bloqueio por destino, gravações atômicas, recuperação de falhas e preservação dos ajustes nas atualizações.
- Fluxo real da GUI verificado em pastas temporárias, incluindo atualização, remoção e erros. Falha de gravação simulada com recuperação dos arquivos anteriores.
- Atualização real realizada na instalação Linux Flatpak do mantenedor; pacote, backup e ajustes conferidos. Dependências verificadas no runtime GNOME 49. O mantenedor confirmou F9 no jogo e o ciclo completo de instalação, remoção e reinstalação.

- V2 do instalador aprovada como referência visual: 17 telas estáticas no Pencil, com tema escuro, cantos arredondados e assinatura ClearView / Vertexiom.
- Prévia interativa offline com chuva ASCII animada, pausa e respeito à preferência de movimento reduzido.
- Simulações de instalação, atualização, seleção de destino, duas instalações, jogo aberto, falhas com relatório fictício e remoção.
- Fluxos da prévia verificados no navegador do Pencil; isso não valida instalação real nem compatibilidade Windows.
- Prévia V1, exportações da V2 e contexto de retomada preservados localmente para desenvolvimento.
- A release pública v0.1.1 permanece disponível e inalterada.

Os protótipos e estudos de design são mantidos localmente; não são necessários para executar o instalador.

## v0.1.1 — testes no Windows e melhorias no instalador

- Instalação com indicação de progresso, confirmação de conclusão e botão para finalizar.
- Verificação da presença do Hytale antes da instalação e recuperação da janela do instalador já aberto.
- Correção da leitura do resultado do teste gráfico, evitando informar falha quando o teste terminou com sucesso.
- Versão testada com sucesso em uma máquina Windows 11 do mantenedor.
- Testada também por **Lazan, membro do MUP**, na máquina dele com **Windows 10**.

Esses testes foram relatados pelos participantes. O projeto continua em desenvolvimento inicial e a validação de compatibilidade permanece em andamento.

## v0.1.0 — primeira versão pública

### Instalação gráfica no Windows

- Um único executável Windows com Instalar/Atualizar, Localizar e Remover.
- Detecção da pasta do Hytale e verificações de instalação e gráficos automáticas.
- Operações em segundo plano, sem terminal; mensagens de erro e relatório local.
- Pacote para jogadores sem BAT, ZIP ou arquivos de checksum separados.
- Compilação e fluxo automatizado verificados no Linux; teste da interface em Windows real ainda pendente.

### Recursos iniciais

- Requisito mínimo alinhado ao Hytale: Windows 10 1809; diagnóstico inclui CPU/RAM/discos.
- Verificação do contexto OpenGL 4.1 com registro de GPU/GLSL e passagem dos shaders originais se incompatível.
- Windows 10 x64 definido como P0; Windows 11 x64 como P1.
- Proxy OpenGL/WGL com HUD F9 renderizado por GDI/OpenGL.
- Núcleo GLSL compartilhado com Linux.
- Instalação/remoção PowerShell 5.1, preservação de configurações e verificação de integridade.
- Teste gráfico isolado e coleta de diagnóstico local.
- Compilação cruzada e ZIP local sem publicação automática.

Projeto em versão inicial, com validação e compatibilidade em andamento. Consulte [os registros técnicos](docs/development/windows.md).

## Histórico interno — protótipo do HUD

- Painel independente aberto com **F9**.
- Controles separados de distância, atmosfera e profundidade, entre 0% e 100%.
- Ajustes ao vivo em passos de 5%, com salvamento automático.
- Presets de visão limpa e restauração do efeito original.
- Renderização do HUD com Cairo/OpenGL e restauração do estado gráfico.
- Testes de entrada de teclado, persistência, intensidade renderizada na GPU e compatibilidade com o runtime Flatpak.
- Instalador `install.sh`, documentação técnica e normalização de arquivos de texto.

O HUD foi validado em testes locais; falta validação integrada dentro do Hytale. Esses registros antecedem a primeira versão pública.

## Histórico interno — primeiro protótipo

- Proxy SDL para o cliente Linux nativo, preservando o executável do jogo.
- Remoção seletiva de neblina com presets de distância, atmosfera e profundidade.
- Instalação e remoção com backup e verificação SHA-256 da SDL original.
- Correção da otimização que removia o parâmetro `uPosition` exigido pelo TextProgram.
- Inicialização e uso confirmados no Hytale 0.7.5 com o preset de distância.
