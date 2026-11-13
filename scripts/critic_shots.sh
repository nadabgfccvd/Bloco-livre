#!/bin/bash
# Bateria de screenshots do critic: cenas × skins × zooms.
set -euo pipefail
RD=/home/z/my-project/tools/RustyDroid/target/release/rd
APK=/home/z/my-project/download/BlocoLivre.apk
OUT=/home/z/my-project/critic_shots/r1
rm -rf "$OUT" && mkdir -p "$OUT"

# 1. MainActivity skin clássica
"$RD" app shot "$APK" --out "$OUT/01_main_classic.png" >/dev/null
# 2-5. cenas mid-game nas 4 skins
for n in 0 1 2 3; do
  "$RD" app shot "$APK" --activity "Lcom/blocolivre/ShotSkin${n};" --out "$OUT/0$((n+2))_skin${n}.png" >/dev/null
done
# 6. tabuleiro cheio
"$RD" app shot "$APK" --activity 'Lcom/blocolivre/ShotSceneFull;' --out "$OUT/06_full.png" >/dev/null
# 7. limpeza perfeita
"$RD" app shot "$APK" --activity 'Lcom/blocolivre/ShotSceneClear;' --out "$OUT/07_clear.png" >/dev/null
ls -la "$OUT"
