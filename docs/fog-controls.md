# Controles de neblina

O ClearView mantém os cálculos originais do Hytale e multiplica os fatores finais por intensidades configuráveis. Os valores dependem do bioma, clima, posição e ambiente definidos pelo jogo.

| Controle | Função alterada | Efeito |
| --- | --- | --- |
| Distância | `computeDistantFogFactor` | Atenuação com a distância horizontal até o horizonte. |
| Atmosfera | `computeMoodFog` | Névoa ambiental, incluindo influência de altura, densidade e clima. |
| Profundidade | `computeDepthFogFactor` | Atenuação pela distância tridimensional, quando habilitada pelo ambiente. |

0% zera o fator selecionado. 100% preserva seu valor original. Os fatores de distância e profundidade podem ser combinados pelo máximo, enquanto a atmosfera participa de outra etapa. Portanto, reduzir um controle nem sempre remove a névoa resultante dos outros.

## Visibilidade

Para enxergar montanhas e terrenos distantes, reduza primeiro **distância**. Para neblina ambiental, experimente reduzir **atmosfera**. **Profundidade** pode ser especialmente relevante debaixo d’água; não remove toda a coloração ou outros efeitos subaquáticos.

O preset **V** usa 0%, 20% e 100%, respectivamente. É um ponto de partida ajustável, não uma configuração ideal para todo cenário.

## Painel e persistência

- **F9:** abrir/fechar.
- **↑/↓:** selecionar controle.
- **←/→:** ajustar em 5%.
- **V:** visão limpa.
- **R:** original, com os três controles em 100%.
- **Escape:** fechar.

O painel funciona pelo teclado, separado das configurações gráficas nativas. As alterações são gravadas em `Client/.clearview/settings` na ordem distância, atmosfera, profundidade, com valores entre 0 e 1. O instalador preserva esse arquivo, exceto quando um novo preset é solicitado explicitamente com `--mode`.

Remover neblina não cria terrenos além da distância de renderização. As bordas dos chunks podem ficar mais visíveis.
