# Bloco Livre — Loop Builder→Critic (4 rodadas)

Pipeline: builder (eu) → APK nativo Canvas → screenshots multi-ângulo no
RustyDroid (runtime Android em Rust) → critic agente AAA brutal (score 0-10).

## Evolução
| Rodada | Score | Veredito | Foco |
|---|---|---|---|
| R1 | 6.2 | GOOD INDIE | base: 4 skins, partículas, allClear |
| R2 | 6.0 | GOOD INDIE | claims vapor; critic desconfiou |
| R3 | 6.5 | GOOD INDIE | wells +63%/+101%, pixel skin real, bandeja fix |
| R4 | 7.0 | GOOD INDIE | dead band ocupado, danger ativo, AO real |

## O que está CONFIRMADO no jogo (medido pelo critic)
- 4 skins de renderização distinta: Clássico (candy 3D), Neon (tubo+glow),
  Gema (facetada), Pixel (cinza neutro #4A4E58, bordas duras sem AA)
- Células vazias legíveis: +63%/+101% de luminância, paridade xadrez,
  sombra interna + rim light (wells usinadas)
- Danger state visível: wells aquecem, borda vira quente a 78% de ocupação
- Bandeja com clipRect (peça 1×5 nunca transborda), escala por área
- Faixa de streak ocupando o antigo dead-band (49→423 cores únicas medidas)
- Confete na zona do tabuleiro (banido do HUD), flash, faixa de celebração
- Numerais PONTOS/RECORDE na mesma altura de caixa
- AO dependente de vizinho (sombra de contato 2.3× mais forte)
- Motor: 24/24 testes, vmDemo bit-idêntico à JVM no RustyDroid

## Issues em aberto para a próxima rodada (do critic R4)
1. CRITICAL: frame de "payoff" da limpeza perfeita (board deve aparecer
   VAZIO no still; timing do demoCelebrate dispara antes do layout)
2. HIGH: danger em meia força (borda só neutraliza, wells só no topo)
3. HIGH: star ring ainda fantasma (emitido mas não fotogênico)
4. MEDIUM: hierarquia de numerais (PONTOS deve dominar RECORDE)
5. MEDIUM: AO renderizado 1.24× (autor 2.3×) — aumentar contraste
6. MEDIUM: skin Clássica (flagship) é a mais apagada — subir range tonal

## Arquivos
- BlocoLivre.apk — o jogo (Java/Canvas puro, 0 permissões, assinado)
- bloco_screenshot_*.png — 6 telas (clássico/neon/gema/pixel/perigo/celebração)
- RELATORIO_TESTE_RUSTYDROID.md — teste completo do runtime
