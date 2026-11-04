# Changelog

## Em desenvolvimento — 0.2

- Painel independente aberto com **F9**.
- Controles separados de distância, atmosfera e profundidade, entre 0% e 100%.
- Ajustes ao vivo em passos de 5%, com salvamento automático.
- Presets de visão limpa e restauração do efeito original.
- Renderização do HUD com Cairo/OpenGL e restauração do estado gráfico.
- Testes de entrada de teclado, persistência, intensidade renderizada na GPU e compatibilidade com o runtime Flatpak.
- Instalador `install.sh`, documentação técnica e normalização de arquivos de texto.

O HUD foi validado em testes locais; falta validação integrada dentro do Hytale. Ainda não há release distribuída.

## Protótipo funcional — 0.1

- Proxy SDL para o cliente Linux nativo, preservando o executável do jogo.
- Remoção seletiva de neblina com presets de distância, atmosfera e profundidade.
- Instalação e remoção com backup e verificação SHA-256 da SDL original.
- Correção da otimização que removia o parâmetro `uPosition` exigido pelo TextProgram.
- Inicialização e uso confirmados no Hytale 0.7.5 com o preset de distância.
