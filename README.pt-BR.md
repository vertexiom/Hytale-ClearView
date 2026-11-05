<h1 align="center">Hytale ClearView</h1>

**Branch de desenvolvimento:** staging prepara a v0.1.3. Os downloads abaixo são da versão estável v0.1.2.

<p align="center">
  <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (Brasil)</a>
</p>

**O ClearView é um mod para controlar a neblina do Hytale, preservando a iluminação original do jogo.** Abra o painel com **F9** e ajuste a intensidade da neblina do seu jeito.

O projeto tem como finalidade a personalização visual, sem o intuito de servir como ferramenta de trapaça ou de contornar as regras do jogo ou dos servidores.

> **Aviso sobre multiplayer:** Antes de usar o ClearView em qualquer servidor multiplayer, consulte a equipe de administradores e confirme se o mod é permitido. Se não for permitido, não o utilize nesse servidor.

**Hytale ClearView v0.1.2 é a versão estável atual.** Atualizações do Hytale podem exigir ajustes no mod.


O [Aurora Shaders](https://github.com/Kristijan1001/Hytale-Aurora-Shaders) foi usado como referência para entender o funcionamento dos shaders e desenvolver o ClearView, que tem código independente.

Estou desenvolvendo esse mod porque meu amigo Lazan é o inimigo número 1 das névoas do Hytale.

## Download

- **Linux v0.1.2:** [ClearView-0.1.2-linux-x64.tar.gz](https://github.com/vertexiom/Hytale-ClearView/releases/download/v0.1.2/ClearView-0.1.2-linux-x64.tar.gz)
- **Windows v0.1.2:** [ClearView-0.1.2-Setup.exe](https://github.com/vertexiom/Hytale-ClearView/releases/download/v0.1.2/ClearView-0.1.2-Setup.exe).

## O que você pode ajustar

- **Distância:** neblina que esconde o horizonte e terrenos distantes.
- **Atmosfera:** névoa de clima, altura e ambiente.
- **Profundidade:** neblina relacionada à distância no ambiente, incluindo água.

Cada controle vai de **0%** (remove aquele efeito) a **100%** (intensidade original). Os ajustes são salvos automaticamente. O mod não aumenta a distância de renderização nem garante mais FPS.

## Compatibilidade

- Windows 10 x64 1809 ou superior e Windows 11.
- Linux x86_64, incluindo o launcher Flatpak.
- Hytale instalado e funcionando, com driver gráfico compatível com OpenGL 4.1.

O ClearView não substitui os [requisitos do Hytale](https://hytale.com/news/2025/12/hytale-hardware-requirements). A compatibilidade com diferentes computadores e multiplayer ainda está em avaliação.

## Instalar no Windows

1. Baixe e abra **ClearView-0.1.2-Setup.exe**.
2. Feche o Hytale e clique em **Continuar**. Confira a pasta do jogo; se necessário, clique em **Procurar…** e selecione `HytaleClient.exe`.
3. Clique em **Instalar**, aguarde a conclusão e clique em **Concluir**. Uma instalação existente será atualizada automaticamente.
4. Abra o jogo pelo launcher, entre num mundo e pressione **F9**.

As verificações são automáticas. Não precisa extrair arquivos, usar terminal, instalar Python ou executar scripts. Para remover, abra o mesmo instalador, escolha **Já usa o ClearView? Remover instalação**, confirme a pasta e clique em **Remover**. Os ajustes existentes são preservados ao atualizar.

## Instalar no Linux

Baixe **ClearView-0.1.2-linux-x64.tar.gz** e extraia a pasta inteira. Feche o Hytale, abra um terminal dentro dessa pasta e execute:

```bash
bash install.sh
```

A interface abre diretamente. Clique em **Continuar**, confira a pasta do jogo e clique em **Instalar**. Aguarde a conclusão e abra o Hytale pelo launcher normal. No jogo, pressione **F9**.

O mod já vem compilado: não precisa de compilador nem loja de aplicativos. Execute sem `sudo`. Se o script informar que faltam dependências da interface, no Ubuntu/Debian instale:

```bash
sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0
```

Depois execute `bash install.sh` novamente. Para atualizar ou remover o mod, feche o jogo e abra o mesmo instalador. Apagar a pasta do instalador não remove o mod.

O pacote Linux x64 requer glibc 2.38 ou superior e as dependências GTK/Python do sistema indicadas acima.

## Controles

| Tecla | Ação |
| --- | --- |
| **F9** | Abrir/fechar o painel |
| ↑ / ↓ | Selecionar a neblina |
| ← / → | Diminuir/aumentar em 5% |
| V | Distância 0%, atmosfera 20%, profundidade 100% |
| R | Restaurar todas as neblinas para 100% |
| Esc | Fechar o painel |

O painel usa teclado e é separado das configurações gráficas do jogo.

## Se algo não funcionar

- **F9 não abre:** confirme que instalou esta versão com o jogo fechado e reinicie o Hytale.
- **Outro mod de shaders instalado:** remova-o antes de instalar o ClearView; não instale por cima do Aurora ou de outro mod que use a mesma biblioteca.
- **Problema ao iniciar:** desinstale o ClearView com o jogo fechado. No Windows, abra o instalador e clique em **Remover**.
- **Se algo não funcionar, me mande uma mensagem no Discord: `tallmannzera`.**

## Sobre o projeto

O repositório não inclui código/shaders de Aurora/Complementary nem arquivos originais do Hytale.

Quer contribuir ou entender o código? Veja o **[guia de desenvolvimento](docs/development/README.md)** e as [orientações para contribuir](CONTRIBUTING.md).

[Histórico de mudanças](CHANGELOG.md)

## Licença e créditos

O código-fonte original do ClearView é licenciado sob a **GNU GPL v3.0 ou posterior** ([GPL-3.0-or-later](LICENSE)). Copyright © 2026 [vertexiom](https://github.com/vertexiom).

Projeto original: [Hytale ClearView](https://github.com/vertexiom/Hytale-ClearView). Se este trabalho inspirar sua implementação, agradecemos o crédito e um link; isso é um pedido, não uma condição adicional da licença.

Componentes de terceiros mantêm suas próprias licenças. Esta licença do código não concede direitos sobre a marca Hytale ou artes de terceiros, incluindo a referência usada no ícone temporário do planeta.
