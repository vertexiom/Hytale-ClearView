# Contribuindo com o ClearView

**Português (Brasil)** | [English](CONTRIBUTING.en.md)

Comece pelo [guia de desenvolvimento](docs/development/README.md). Ele reúne arquitetura, compilação, testes e limitações conhecidas.

Envie alterações para `staging`, descrevendo o problema, a solução e como testou. Informe sistema operacional, GPU, driver e versão do Hytale em relatos de falha. Não envie credenciais, mundos pessoais, bibliotecas ou shaders originais do jogo.

Ao alterar instruções para jogadores, atualize os dois idiomas do README. Mantenha comandos, nomes dos downloads, controles e compatibilidade consistentes. Use os nomes reais dos botões do instalador para que o jogador consiga seguir as instruções.

Publicações na `staging`, na `main` ou nas Releases exigem confirmação prévia do mantenedor. Prepare e valide as alterações localmente antes de solicitar essa confirmação.

Protótipos visuais, HTML de prévia, estudos ASCII, capturas de experimentos e notas de sessão devem permanecer locais. Versione apenas código e recursos do produto, ferramentas de build, testes automatizados e documentação de manutenção. Ícones usados pelo aplicativo ficam em `assets/icons/`.

Contribuições ao código original devem ser compatíveis com GPL-3.0-or-later. Preserve avisos de terceiros e identifique a origem e a licença de código ou recursos adicionados. Antes de distribuir binários, inclua LICENSE e os avisos das dependências, e disponibilize o código-fonte correspondente completo conforme a GPL, incluindo scripts de compilação e instalação. Não presuma que imagens de referência permitem redistribuição.

O workflow de GitHub Actions e os testes da integração Windows são exclusivos da `staging`: não publicar esses arquivos nem suas alterações na `main`. Ao promover correções de produto, selecione somente os commits/trechos de produção; não faça merge integral de staging em main.
