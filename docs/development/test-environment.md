# Ambiente de testes

Registro coletado em **4 de novembro de 2026**, para o ClearView **v0.1.0**. Código de referência antes deste registro: `503494e`. Este documento descreve o ambiente de desenvolvimento e validação; não representa os requisitos mínimos do mod nem certifica outras máquinas.

## Hardware e sistema Linux

| Componente | Ambiente observado |
| --- | --- |
| CPU | Intel Core i9-12900KF, 16 núcleos e 24 processadores lógicos |
| RAM reconhecida pelo sistema | Aproximadamente 61,5 GiB |
| GPU | NVIDIA GeForce RTX 5070 |
| Memória da GPU reportada pelo driver | 12.227 MiB |
| Sistema | Ubuntu 26.04.1 LTS (Resolute Raccoon), x86_64 |
| Kernel | 7.0.0-38-generic |
| Driver NVIDIA | 595.99.02 |
| glibc do sistema | 2.43 — pacote 2.43-2ubuntu2.4 |

## Hytale e ambiente de execução

| Componente | Versão / identificação |
| --- | --- |
| Pacote Hytale | 0.7.5, confirmado pelo servidor integrado no log da sessão; revisão `4f7cd77adb4da3434c247b6d2acb4486c391e976` |
| Distribuição | Canal `release`, cliente Linux pelo launcher oficial Flatpak |
| Launcher | `com.hypixel.HytaleLauncher`, branch `master`, x86_64 |
| Build Flatpak do launcher | `28bf1aa58fc8eb8d436ba553ef471ef2e51a06e0bc433df204e85b61435fd1b6` |
| Runtime do launcher/jogo | `org.gnome.Platform/x86_64/49` |
| glibc dentro do runtime | 2.42 |
| Flatpak no sistema | 1.16.6 — pacote 1.16.6-1 |
| SDL original do cliente | 3.2.26, consultada por `SDL_GetVersion` na biblioteca original preservada |
| Contexto OpenGL reportado pelo Hytale | 4.1.0 NVIDIA 595.99.02 |
| Renderizador reportado pelo Hytale | NVIDIA GeForce RTX 5070/PCIe/SSE2 |

A identificação do jogo e do contexto gráfico foi extraída do log da sessão de 4 de novembro de 2026, às 03:29. A versão do pacote foi observada no servidor integrado; não foi obtida de um campo separado de versão do executável cliente. OpenGL 4.1 é o contexto reportado nessa sessão, não uma afirmação sobre a versão máxima suportada pela GPU.

## Compilação e testes no host

| Ferramenta / biblioteca | Versão |
| --- | --- |
| Compilador C | GCC 15.2.0 — Ubuntu 15.2.0-16ubuntu1 |
| Python | 3.14.4 |
| Cairo | 1.18.4 — pacote libcairo2 1.18.4-3 |
| Pillow | 12.1.1 |
| Carregadores EGL/OpenGL do sistema | libegl1, libgl1 e libglvnd0: 1.7.0-3 |
| Zig para gerar binários Windows x64 | 0.15.2 |
| PowerShell usado nos testes simulados | 7.6.9, executado no Linux |

As versões dos carregadores EGL/OpenGL acima são versões de pacotes, não versões da API gráfica. O instalador Windows é destinado ao Windows PowerShell 5.1; testar sua lógica com PowerShell 7.6.9 no Linux não substitui essa validação nativa.

## Alcance da validação

- O primeiro protótipo foi confirmado em execução no Hytale Linux.
- Os testes locais validaram transformação GLSL, interfaces dos shaders, controles, persistência, desenho do HUD e restauração do estado OpenGL.
- Os testes de instalação usam um cliente simulado e verificam atualização, integridade e recuperação, sem modificar a instalação real.
- O instalador e o proxy Windows foram compilados neste ambiente. Os testes nativos posteriores estão registrados abaixo.
- O HUD integrado no jogo, diferentes GPUs e multiplayer exigem registro próprio de validação; a presença do hardware nesta tabela não significa aprovação desses cenários.

O roteiro e os resultados estão em [Validação e diagnóstico](validation.md). Ao testar outra máquina, registrar data, commit do ClearView, sistema/kernel, GPU/driver, versão do Hytale, ambiente nativo ou Flatpak, cenário executado e resultado. Atualizar este registro quando o ambiente mudar, preservando em resultados específicos as versões usadas em cada teste.

Não incluir nome de usuário, hostname, números de série, endereços de rede, credenciais ou logs completos neste documento público.

## Testes Windows — v0.1.1

Em 4 de novembro de 2026, o mantenedor confirmou o funcionamento da versão após teste em uma de suas máquinas Windows. Lazan, membro do MUP, também testou a versão na própria máquina com Windows 11. As especificações dessas máquinas não são publicadas neste registro.

Registro baseado no retorno dos participantes; não representa aprovação de toda a matriz de hardware nem de todos os cenários do roteiro de testes.
