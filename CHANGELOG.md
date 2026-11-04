# Changelog

## v0.1.1 — instalador gráfico

- Um único executável Windows com Instalar/Atualizar, Localizar e Remover.
- Detecção da pasta do Hytale e verificações de instalação e gráficos automáticas.
- Operações em segundo plano, sem terminal; mensagens de erro e relatório local.
- Pacote para jogadores sem BAT, ZIP ou arquivos de checksum separados.
- Compilação e fluxo automatizado verificados no Linux; teste da interface em Windows real ainda pendente.

## v0.1.0 — primeira versão pública

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
