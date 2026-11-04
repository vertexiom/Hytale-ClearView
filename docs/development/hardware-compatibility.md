# Hardware e robustez

Pesquisa em 4 de novembro de 2026. Windows 10 é P0; Windows 11 é P1. A GTX 660 informada pelo testador ainda precisa ser confirmada. Nenhuma GPU foi validada no Windows real com esta prévia.

## Referência oficial e GTX 660

O Hytale lista Windows 10 x64 1809+, i5-7500/Ryzen 3 1200, 8 GB de RAM com GPU dedicada, GTX série 900 e OpenGL 4.1. A meta mínima publicada é 1080p/30 FPS no preset baixo. Singleplayer executa também o servidor e exige atenção a CPU/RAM. Fonte: [requisitos oficiais](https://hytale.com/news/2025/12/hytale-hardware-requirements).

A GTX 660 está fora da referência mínima de GPU dedicada. A [ficha da NVIDIA](https://www.nvidia.com/en-us/geforce/graphics-cards/geforce-gtx-660/specifications/) informa OpenGL 4.3 e 2 GB na placa de referência, com possíveis diferenças entre fabricantes. Isso não comprova a versão efetivamente oferecida pelo driver instalado, nem desempenho suficiente no jogo. A [política de suporte Kepler](https://nvidia.custhelp.com/app/answers/detail/a_id/5202) encerrou melhorias Game Ready em 2021 e previa atualizações críticas de segurança até setembro de 2024. Não presumir que um driver atual para RTX sirva nessa placa.

Decisão: GTX 660 permanece experimental. Confirmar que o Hytale original funciona antes de investigar o mod. Não bloquear por nome de GPU nem usar a estimativa WMI de VRAM como critério de aprovação.

## O que aproveitar do Aurora

O [Aurora](https://github.com/Kristijan1001/Hytale-Aurora-Shaders#performance) combina efeitos como nuvens volumétricas, reflexos e iluminação por raios; seu README identifica custos e descreve retorno ao shader original em falhas de compilação. Aproveitar a ideia de recuperação e diagnóstico. O ClearView mantém apenas controles de neblina e HUD, sem incorporar esses efeitos ou exigir RTX/DLSS.

O HUD atual só desenha quando aberto e só atualiza sua textura quando necessário. O ajuste de neblina ainda envolve interceptação de programas e atualização de uniforms; seu custo precisa ser medido. Neblina em 0% não é promessa de mais FPS e não aumenta a distância de renderização.

## Implementado na v0.1.0

- Instalador exige Windows 10 build 17763 ou superior; teste simulado verifica recusa de build anterior.
- Contexto Windows registra GPU, fornecedor, OpenGL e GLSL reais. Sem OpenGL 4.1, encaminha shaders originais e não ativa o HUD. Essa proteção não contorna os requisitos do jogo.
- Diagnóstico local inclui CPU, RAM, GPU/driver e espaço em disco; não envia arquivos automaticamente. VRAM por WMI é apenas estimativa.
- Proteções existentes: hashes, recusa de DLL de outro mod, instalação com jogo fechado, recuperação em falha de instalação e remoção reversível.
- Transformação GLSL desconhecida permanece inalterada. Isso ainda não equivale a recuperação após falha de compilação/linkedição.

## Pendências para estabilidade P0

1. Implementar recuperação após erro de compilação/linkedição de um shader alterado, preservando fonte original e log do erro. Hoje isso ainda não existe.
2. Validar em Windows 10 nativo: teste isolado, instalação, F9, persistência, Alt+Tab, mudança de janela e pelo menos 30 minutos de jogo. Repetir no Windows 11 depois.
3. Medir na mesma cena/resolução/distância: jogo original, mod com neblinas em 100%, preset de visibilidade com HUD fechado e aberto. Registrar FPS e tempos de quadro, incluindo picos. Meta proposta: custo com HUD fechado abaixo de 5%; não é um resultado já obtido.
4. Se houver custo relevante, reduzir atualizações redundantes de uniforms e contenção de locks com base no perfil medido. Considerar opção de desativar apenas o HUD para diagnóstico.
5. Registrar versão do cliente, driver e resultados por GPU; repetir após atualizações do Hytale. Uma máquina aprovada não certifica toda a família de GPUs.

Para o primeiro teste da GTX 660, usar o preset baixo do jogo; experimentar 720p se necessário e manter a mesma configuração ao comparar. Se o jogo original já falhar, resolver isso primeiro. Enviar o diagnóstico e o resultado do teste isolado antes de atribuir o problema ao shader.
