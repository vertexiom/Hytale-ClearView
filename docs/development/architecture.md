# Arquitetura e diagnóstico


No Linux, um proxy SDL encaminha as chamadas para a biblioteca original e intercepta o envio dos shaders ao OpenGL. O código transforma funções reconhecidas de neblina, adicionando multiplicadores controlados por uniforms. Isso mantém os parâmetros exigidos pelo cliente ativos durante a otimização do GLSL.

No Linux, o HUD é desenhado com Cairo/OpenGL; no Windows, com GDI/OpenGL, antes da apresentação do quadro. O estado gráfico alterado pelo painel é restaurado. O executável `HytaleClient` permanece intacto.

O código é independente. Aurora Shaders foi estudado como referência de arquitetura; este repositório não inclui código/shaders de Aurora/Complementary nem distribui shaders ou bibliotecas originais do Hytale.

## Diagnóstico

- `Client/.clearview/hook.log`: carregamento e transformação dos shaders.
- `Client/.clearview/settings`: intensidades de distância, atmosfera e profundidade, entre 0 e 1.
- `Client/.clearview/receipt.json`: hash de integridade do backup da SDL.

Atualizações do jogo podem alterar as assinaturas dos shaders. Fontes não reconhecidas passam sem modificação. Multiplayer ainda não foi validado.
