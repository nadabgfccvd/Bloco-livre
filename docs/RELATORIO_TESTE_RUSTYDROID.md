# Teste do RustyDroid com o Bloco Livre

**Data:** 12/11/2026 · **RustyDroid:** commit master do repo nadabgfccvd/RustyDroid,
versão 0.9.0 · **Rust:** 1.100.0 (MSRV 1.97 ✓) · **APK:** BlocoLivre.apk
(Java puro, Canvas, minSdk 21, target 34, 0 permissões)

## Veredito: FUNCIONA — com 3 ressalvas honestas

O RustyDroid cumpre o que promete para este jogo: parseou o APK real, bootou
a Activity, executou o DEX do app e renderizou a UI de verdade em PNG. O
motor de jogo inteiro roda **bit-idêntico à JVM** no runtime. O que não
funciona tem explicação rastreável no próprio registro de cobertura do
projeto (nada é silencioso — todo gap vem com erro JSON estruturado).

## O que foi testado e o resultado

### 1. Build da ferramenta — OK
`cargo build -p rd-cli --release` compilou sem erros em 5m20s (binário
17 MB). Requisitos: só Rust estável (nenhuma dependência de sistema).

### 2. `rd inspect` — OK
Leu o APK real e imprimiu: pacote `com.blocolivre v1.0`, label resolvido de
`resources.arsc` ("Bloco Livre"), SDKs (min 21 · target 34), assinaturas
(v1+v2+v3), 16 entradas ZIP, 1 dex, e — o teste que importava —
**"permissions (0 declaradas)"**: confirmou de forma independente que o
jogo não pede nenhuma permissão. Activity launcher detectada com filtro
correto.

### 3. `rd app dump` — OK (após adaptação do jogo)
Na 1ª tentativa: erro `NOT_FOUND: AudioAttributes$Builder.<init>` — o
slice `android.media` do runtime é "partial" (só camada de metadados, sem
SoundPool; está no `data/api-coverage.toml` do projeto). Como o erro é
lançado na resolução do método, try/catch Java não captura. Resolvi com
**reflexão pura** (`Class.forName` falha *dentro* do guest, capturável):
classe `AudioCompat` que carrega sons/vibração sem link estático de
bytecode para `android.media.*`. Em aparelho real: som normal; em runtime
sem mídia: jogo mudo e funcional. No caminho também tropecei em
`Class.newInstance()` (não implementado) — troquei para
`getDeclaredConstructor().newInstance()`.

Depois disso o dump XML (uiautomator) mostrou a árvore real: LinearLayout
raiz → HUD (score "0", "sem combo", "RECORDE" "0") → FrameLayout →
`com.blocolivre.game.GameView` → rodapé com 3 botões ("Novo jogo",
"Trocar bandeja", "?") com bounds.

### 4. `rd app shot` — OK
PNG 720×1440 determinístico (53 KB) com o jogo renderizado de verdade.
Validei por análise de pixel: tabuleiro 8×8 com casas vazias (#232F3E),
3 peças coloridas na bandeja (laranja 255,183,77 · azul 79,195,247 ·
amarelo), cores exatas da paleta do jogo. Screenshots anexados
(`rustydroid_tela_inicial.png`, `rustydroid_bandeja.png`).

### 5. `rd vm exec` — OK, o teste mais forte
Executei `GameModel.vmDemo(long)` — uma partida completa de bot dentro do
DEX (RNG, colocação, limpeza de linhas/colunas, pontuação, combos,
swapTray, fim de jogo) — no RustyDroid e na JVM de referência:

| seed | RustyDroid | JVM |
|---|---|---|
| 20261112 | 216;14;2 | 216;14;2 |
| 42 | 304;16;3 | 304;16;3 |
| 7 | 480;22;5 | 480;22;5 |
| 999 | 45;11;0 | 45;11;0 |
| 12345 | 1048;31;11 | 1048;31;11 |

**5/5 idênticos** (score;peças;linhas). O intérprete Dalvik do RustyDroid
executa o motor do jogo com semântica correta — inclusive `java.util.Random`
(RNG do jogo), que é o que garante a honestidade do sorteio.

### 6. `rd app run` com toques — PARCIAL
`tap` nos botões do rodapé aciona listeners (`listener acionado: true`) —
os cliques chegam ao app. Porém o **drag de peça não funciona** e o
AlertDialog não aparece no dump. Causa raiz (rastreada com `RD_FW_DEBUG=1`):
o layout do marco M3 não implementa **weights de LinearLayout** — a árvore
inteira mede 144px de altura (cada view fica com sua altura mínima), então
toques abaixo de y=144 não passam no hit-test, e o GameView nunca recebe o
DOWN/MOVE/UP do arraste. Não é bug do jogo: no aparelho real o peso 1.0
estica o tabuleiro para a tela toda. Os eventos de swipe do runtime
(swipe v1) também estão documentados como "partial" (só-relatório).

## Limitações encontradas (resumo)

| # | Gap | Onde está documentado | Efeito no jogo |
|---|---|---|---|
| 1 | `android.media` sem SoundPool/AudioAttributes | `data/api-coverage.toml` (partial) | Sons não tocam — contornado no APK por reflexão (degradação graciosa) |
| 2 | `Class.newInstance()` ausente | erro JSON NOT_FOUND | Contornado com `getDeclaredConstructor().newInstance()` |
| 3 | Layout LinearLayout sem weights (M3) | trace RD_FW_DEBUG (árvore 144px) | Toque/arraste no tabuleiro não alcança o GameView no headless |
| 4 | AlertDialog.Builder.show() não materializa janela no dump | — | Diálogos do jogo não aparecem (botões respondem) |

Nenhum deles é falha do APK: em aparelho Android real tudo funciona
(o APK já havia passado em compilação limpa, 13/13 testes de motor e
verificação de assinatura).

## Como reproduzir

```bash
git clone https://github.com/nadabgfccvd/RustyDroid && cd RustyDroid
cargo build -p rd-cli --release

APK=/caminho/para/BlocoLivre.apk
./target/release/rd inspect $APK
./target/release/rd app dump $APK
./target/release/rd app shot $APK --out tela.png
./target/release/rd vm exec --class 'Lcom/blocolivre/core/GameModel;' \
    --method vmDemo --sig '(J)Ljava/lang/String;' --args 42L $APK
# → 304;16;3 (idêntico à JVM)
```

## Nota para o desenvolvimento do RustyDroid

O jogo acabou servindo de caso de teste útil: APK de Java puro com Canvas
customizado (sem Jetpack), reflexão, anonymous inner classes e lambdas
(InvokeDynamic/desugaring d8) — tudo executou. Os dois pontos de maior
impacto para jogos casuais seriam: weights de LinearLayout no layout M3
(sem isso, qualquer tela "match_parent com peso" fica minúscula e o input
não alcança a área do jogo) e o pipeline `android.media` para SoundPool
(áudio é parte essencial do feedback de jogo). O contrato de erros JSON
estruturados com `suggestion` é excelente para debug — continue assim.
