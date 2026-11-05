# ClearView — contexto para retomar a v0.1.2

Atualizado em 4 de novembro de 2026. Leia este documento antes de continuar.

## Estado atual e decisão aprovada

O usuário escolheu a **V2 do Claude Opus 5.5** como base visual do novo instalador. Ela tem 17 telas estáticas no Pencil e foi implementada como uma prévia interativa HTML, com chuva ASCII animada. **Essa interface ainda não foi integrada ao EXE.**

- Repositório: <https://github.com/vertexiom/Hytale-ClearView>.
- Branch de trabalho: `staging`; desenvolvimento da **v0.1.2**.
- Versão pública mantida: **v0.1.1**, em `main` e na release existente.
- O usuário autorizou publicar este checkpoint **somente na staging**. Não atualizar main, tags, releases ou assets da v0.1.1.
- Antes de novas publicações, pedir autorização. Esta autorização não é permanente.
- Não tocar nos projetos/documentos Rota ou fellowbot.

## GUI Linux real — Python + GTK 4

O usuário escolheu Python + GTK 4 no Linux. Windows terá implementação independente; Tauri não foi adotado e não há migração para Rust.

`./installer/linux/gui/run.sh` agora abre o instalador **real**. Detecta instalação nativa/Flatpak e permite escolher HytaleClient. Instala, atualiza e remove via subprocesso de `installer/linux/install.py`, com progresso por etapas reais, relatório local e conclusão condicionada ao resultado do processo. A chuva ASCII/Cairo permanece animada. `--demo` mantém os cenários fictícios separados.

O backend verifica jogo fechado, pacote/manifesto x64, backup e conflitos; usa bloqueio por destino, gravações atômicas e recuperação de erros. Atualizações preservam ajustes; remoção restaura o original. Não garante recuperação de queda de energia nem executa teste gráfico do Hytale.

Em 04/11/2026, a GUI realizou uma **atualização real** na instalação Flatpak desta máquina. Hash do mod conferido contra o pacote; backup original e bytes dos ajustes preservados. Dependências conferidas dentro de org.gnome.Platform 49. Cópia de recuperação e captura estão em `build/linux-gui/` (ignoradas). Logs em `$XDG_STATE_HOME/clearview/logs` ou `~/.local/state/clearview/logs`. **O usuário confirmou F9 no jogo e o ciclo instalar → remover (mod ausente no jogo) → reinstalar (mod funcional).** Relato limitado a esta máquina Linux.

Nesta máquina foi instalado somente `python3-gi-cairo`, que faltava. Leia `installer/linux/gui/LEIA-ME.txt` para dependências e testes. O build local gera `build/libSDL3.so` e `linux-manifest.json`; a GUI não compila nem baixa durante a instalação. O pacote local `dist/clearview-installer_0.1.2-1_amd64.deb` contém GUI e mod compilado. Build: `python3 tools/build/build_linux_deb.py`. Instala em `/usr/lib/clearview`, com comando `clearview-installer` e atalho no menu. APT instala dependências; a GUI roda como usuário normal. Remover o pacote não remove o mod do jogo: usar a remoção dentro da GUI antes.

O pacote foi instalado, removido e reinstalado nesta máquina; a GUI abre fora do checkout e o payload extraído passou em instalação/atualização/remoção num cliente temporário. Binários permanecem ignorados, sem release pública. Build atual amd64 exige libc6 >= 2.38; não afirmar compatibilidade com todas as distros. Não redistribui SDL original ou shaders do jogo.

O usuário autorizou este trabalho e publicação somente na staging. Main e release v0.1.1 não devem mudar. Pedir nova autorização para publicações posteriores.

## Como ver o trabalho

1. Abra [design/installer/interactive.html](design/installer/interactive.html) no navegador. Funciona com `file://`, offline, sem servidor e sem dependências novas.
2. Use o seletor de cenários acima da janela. A faixa Laboratório permite mudar condições fictícias para experimentar recuperação de erros.
3. No Pencil, abra **RnD_ClearView_exec_v001**. A série aprovada se chama **Opus V2**.

| Referência | Estado |
| --- | --- |
| [interactive.html](design/installer/interactive.html) | Prévia navegável V2 atual, com chuva animada |
| [interactive-v1.html](design/installer/interactive-v1.html) | Prévia anterior preservada para comparação |
| [COMO-ABRIR.txt](design/installer/COMO-ABRIR.txt) | Uso e limitações da prévia |
| [v2/static.html](design/installer/v2/static.html) | Exportação estática das 17 telas aprovadas |
| [v2/screens/](design/installer/v2/screens/) | Capturas das telas V2 |
| [preview.html](design/installer/preview.html), `export.pdf`, `screens/` | Exportações antigas das sete telas iniciais; não são a V2 |
| [BRIEFING-CLAUDE.txt](design/installer/BRIEFING-CLAUDE.txt) | Briefing histórico que originou o estudo do Claude |
| [fluxo-v0.1.2.txt](design/installer/fluxo-v0.1.2.txt) | Especificação atual resumida |
| [tools/preview/](tools/preview/) | Estudos anteriores em terminal; chuva Python/TTE e planeta |
| [assets/concepts/](assets/concepts/) | Conceitos anteriores; preservar, não usar como identidade atual |

O documento editável `.pen` está no armazenamento local do Pencil, não dentro deste repositório. As exportações acima preservam a referência visual, mas não substituem o documento editável. Não apagar/mover esse documento. Use ferramentas do Pencil para ler/editar `.pen`; não tratar como JSON comum. Os registros locais do Claude estão em `build/claude-design/` (ignorados pelo Git).

## Projeto e público

ClearView controla a neblina de distância, atmosfera e profundidade do Hytale, preservando sua iluminação original. **F9** abre o HUD. Aurora Shaders foi referência de arquitetura; não redistribuir seus shaders nem arquivos originais do jogo.

O instalador é para jogadores sem conhecimentos de desenvolvimento: um EXE gráfico, com indicação do destino, progresso real, conclusão clara e recuperação compreensível. **Windows 10 é P0, Windows 11 é P1.** O usuário validou a v0.1.1 no Windows 11; Lazan, membro do MUP, no Windows 10. Não publicar specs dessas máquinas. Esses relatos não validam automaticamente a v0.1.2.

Suporte: Discord **tallmannzera**. O projeto inteiro está em desenvolvimento inicial; não apresentar só o Windows como uma “prévia”. READMEs em inglês e português. A documentação técnica fica separada da apresentação para jogadores. Regra explícita do usuário: nunca incluir relatos de testes, participantes, máquinas ou status de validação nos READMEs principais (inglês e português). Manter esses registros no changelog/documentação técnica; a introdução pode informar que o projeto está em desenvolvimento inicial.

## Direção visual aprovada

- Assinatura **CLEARVIEW / VERTEXIOM**; nunca `ClearView / Hytale` como marca conjunta.
- Texto **Clear View em ASCII**, chuva diagonal `\`, colisões no texto/chão e respingos suaves. O planeta e os logos H ficaram arquivados.
- No Pencil, chuva estática; na prévia interativa, animada, com pausa e respeito a movimento reduzido.
- Fundo escuro; cantos arredondados; nada de fundo branco.
- Conteúdo `#1B2838`; título/rodapé `#151E2A`; lateral `#071018`.
- Texto `#E6EDF5`, secundário `#A8B9CB`; azul `#8DD2F4` nas ações; verde `#85D8AF` no sucesso; âmbar `#F0C782` nos avisos e remoção. Nunca depender apenas da cor.
- Janela desktop de referência 960 × 626; lateral 340; título 42; corpo 510; rodapé 72. Raio da janela 22, botões 14, campos 12, painel de sucesso 18 px.
- Inter/Segoe UI para interface, JetBrains Mono em peso forte para ASCII. Voltar à esquerda; ações principais à direita.
- O pacote já vem no EXE: a interface mostra **verificação e instalação**, não download fictício.

## Telas da V2 no Pencil

Cabeçalho `xD1BN` em y=7788; telas começam em y=8014. Quadro comparativo `azTCk`; componentes independentes V2 em `kxBCT`. As séries anteriores devem permanecer intactas.

| Tela | ID |
| --- | --- |
| Boas-vindas | `V8i9J` |
| Local / Atualizar | `ZMG55` / `XiD3f` |
| Verificação / Compatibilidade | `t6b2ka` / `c4Rvz` |
| Fechamento bloqueado / Instalação | `xf5Sw` / `p1KBoc` |
| Conclusão | `f4vvYZ` |
| Pasta ausente / Duas instalações | `vcGSG` / `WOx5S` |
| Jogo aberto | `R6ZgoJ` |
| Falha gráfica / Outro mod / Falha na cópia | `W68ZT7` / `HMCTf` / `l5CyX` |
| Confirmar remoção / Removendo / Concluída | `pwV7e` / `z9V4oq` / `tPqNj` |

## O que a prévia faz, e o que ela não faz

A prévia simula instalação, atualização, seleção de `HytaleClient.exe`, ausência do jogo, duas instalações, jogo aberto, três tipos de falha, relatório fictício, remoção e conclusão. Reiniciar/trocar cenário cancela timers. Fechar durante operação mostra aviso. A seleção e os relatórios não acessam arquivos reais. Nenhum download, teste gráfico ou alteração do Hytale acontece.

O Claude relatou testes via DOM/CDP no browser do Pencil: fluxos acima, recuperação/repetição, foco ao fechar diálogos, largura 390 px, desktop, movimento reduzido e ausência de recursos externos. Parte das interações foi programática; Esc foi testado com eventos sintéticos. Isso **não equivale a testes do EXE no Windows**.

## Implementação existente e pendências

O EXE atual usa `installer/windows/bootstrap.c`, `setup.ps1` (Windows Forms), `workflow.ps1` e `install.ps1`. Preservar verificações de integridade/conflitos, jogo fechado, backups, recuperação, logs, ativação da janela existente e a sequência validar → testar gráficos → instalar. Só mostrar sucesso após o worker realmente concluir.

Os metadados de build já estão em 0.1.2 (`tools/build/build_windows.py`, `setup.rc`, `setup.manifest`). Um pacote local com esse número pode existir em `dist/`, **ainda com a interface antiga**. Não confundir versão do arquivo com implementação da V2 e não distribuir como novo instalador pronto.

Ainda precisam ser implementados/confirmados no EXE: layout V2, animação eficiente, duas instalações, identificação de atualização, estados inline de jogo aberto e falhas, botão Abrir relatório e foco/teclado/DPI. O backend já tem funções de segurança que precisam ser conectadas corretamente; não substituí-las por comportamento da simulação.

A referência de 626 px exige teste em telas pequenas/escala 125% no Windows 10. Não escolher tecnologia nova nem introduzir dependências só por semelhança com HTML: o protótipo é referência visual, não decisão de stack.

## Próxima sessão

1. Ler este contexto e conferir `git status`/branch antes de editar.
2. Abrir a prévia V2 e conferir se há novos ajustes do usuário.
3. Planejar a integração do visual V2 no instalador existente, preservando o backend. A GUI Linux já instala de verdade; o Windows ainda precisa da integração visual.
4. Implementar e testar progressivamente a UI nativa, incluindo caminhos Unicode/espaços, erro/recuperação, logs, seleção de destino e segurança da remoção.
5. Validar no Windows 10 primeiro, depois 11: teclado, DPI, responsividade, consumo da chuva e instalação real com Hytale fechado.
6. Pedir autorização antes de nova publicação. Não promover para main nem criar release apenas porque o protótipo passou.

## Outros assuntos ainda abertos

- Assinatura Authenticode/SignPath e avisos do SmartScreen: não resolvidos; não orientar a desativar proteções.
- Regras de servidores/Hytale: o usuário iria consultar admins e suporte. Não garantir ausência de ban; nenhuma mudança de limite de neblina foi decidida.
- Revisar a licença do projeto e de fontes/dependências antes de distribuição. Usar Pencil não determina a licença do código. A licença MIT do TerminalTextEffects está em `tools/preview/third-party/`; não assumir que cobre todo o projeto.
