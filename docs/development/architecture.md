# Arquitetura e diagnóstico

No Linux, um proxy SDL encaminha as chamadas para a biblioteca original e intercepta o envio dos shaders ao OpenGL. O código transforma funções reconhecidas de neblina, adicionando multiplicadores controlados por uniforms. Isso mantém os parâmetros exigidos pelo cliente ativos durante a otimização do GLSL.

No Linux, o HUD é desenhado com Cairo/OpenGL; no Windows, com GDI/OpenGL, antes da apresentação do quadro. O estado gráfico alterado pelo painel é restaurado. O executável `HytaleClient` permanece intacto.

O código é independente. Aurora Shaders foi estudado como referência de arquitetura; este repositório não inclui código/shaders de Aurora/Complementary nem distribui shaders ou bibliotecas originais do Hytale.

## Diagnóstico

- `Client/.clearview/hook.log`: carregamento e transformação dos shaders.
- `Client/.clearview/settings`: intensidades de distância, atmosfera e profundidade, entre 0 e 1.
- `Client/.clearview/receipt.json`: hash de integridade do backup da SDL.

Atualizações do jogo podem alterar as assinaturas dos shaders. Fontes não reconhecidas passam sem modificação. Multiplayer ainda não foi validado.

## Cálculos de neblina

O ClearView mantém os cálculos originais do Hytale e multiplica os fatores finais por intensidades configuráveis. Os valores dependem do bioma, clima, posição e ambiente definidos pelo jogo.

| Controle | Função alterada | Efeito |
| --- | --- | --- |
| Distância | `computeDistantFogFactor` | Atenuação com a distância horizontal até o horizonte. |
| Atmosfera | `computeMoodFog` | Névoa ambiental, incluindo influência de altura, densidade e clima. |
| Profundidade | `computeDepthFogFactor` | Atenuação pela distância tridimensional, quando habilitada pelo ambiente. |

0% zera o fator selecionado. 100% preserva seu valor original. Os fatores de distância e profundidade podem ser combinados pelo máximo, enquanto a atmosfera participa de outra etapa. Portanto, reduzir um controle nem sempre remove a névoa resultante dos outros.


As intensidades ficam em `Client/.clearview/settings`, na ordem distância, atmosfera e profundidade. Os instaladores preservam esses valores, salvo quando um preset é solicitado explicitamente. Remover neblina não aumenta a distância de renderização; as bordas dos chunks podem ficar mais visíveis. Os controles de teclado estão no [README](../../README.md#controles).
