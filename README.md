# Hytale ClearView

Controle a neblina do Hytale sem mudar a iluminação original do jogo. Abra o painel com **F9** e ajuste a visibilidade do seu jeito.

**v0.1.0 — versão inicial.** O projeto está em desenvolvimento, com validação e compatibilidade em andamento. Atualizações do Hytale podem exigir ajustes no mod.

## Download

**[Baixar o ClearView v0.1.0](https://github.com/vertexiom/Hytale-ClearView/releases/tag/v0.1.0)**

- **Windows:** baixe `ClearView-0.1.0-x64.zip`.
- **Linux:** baixe `ClearView-0.1.0-linux-source.tar.gz` e siga as instruções abaixo.

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

1. Extraia o ZIP completo para uma pasta sua.
2. Execute `Smoke Test.bat` para verificar o carregamento e os controles. Se falhar, guarde a pasta de resultado e relate o problema antes de instalar.
3. Feche o Hytale e execute `Install.bat`.
4. Abra o jogo pelo launcher, entre num mundo e pressione **F9**.

Não precisa de compilador ou Python. Para remover, feche o jogo e execute `Uninstall.bat`.

## Instalar no Linux

Extraia o pacote. A instalação compila o mod e precisa de Python 3, compilador C, pkg-config e Cairo. No Ubuntu, instale as dependências:

```bash
sudo apt install python3 build-essential pkg-config libcairo2-dev
```

Com o Hytale fechado, abra um terminal na pasta extraída:

```bash
bash install.sh
```

Depois abra pelo launcher normal. Para remover, com o jogo fechado:

```bash
bash install.sh --uninstall
```

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
- **Problema ao iniciar:** desinstale o ClearView com o jogo fechado. No Windows, execute `Diagnostics.bat` para gerar um diagnóstico local; nada é enviado automaticamente.
- **Ainda precisa de ajuda?** [Abra um relato](https://github.com/vertexiom/Hytale-ClearView/issues) com sistema, GPU e descrição do problema.

## Sobre o projeto

Código independente, com Aurora Shaders como referência de arquitetura. Não inclui código/shaders de Aurora/Complementary nem arquivos originais do Hytale.

Quer contribuir ou entender o código? Veja o **[guia de desenvolvimento](docs/development/README.md)** e as [orientações para contribuir](CONTRIBUTING.md).

[Histórico de mudanças](CHANGELOG.md)
