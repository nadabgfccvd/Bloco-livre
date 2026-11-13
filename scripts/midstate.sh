#!/usr/bin/env bash
# Roda o motor até um estado de meio de jogo e imprime o serializado p/ preview.
set -euo pipefail
cd /home/z/my-project/app/src/com/blocolivre/core
cat > /tmp/MidState.java <<'EOF'
package com.blocolivre.core;
public class MidState {
    public static void main(String[] a) {
        GameModel g = new GameModel(20261112L);
        // ~12 jogadas de bot guloso: tabuleiro parcial, bandeja com peças
        for (int i = 0; i < 12 && !g.isOver(); i++) EngineTest.botStep(g);
        System.out.println(g.serialize());
    }
}
EOF
java -jar /home/z/my-project/tools/ecj.jar -8 -d /tmp/jvmout /tmp/MidState.java GameModel.java Piece.java EngineTest.java 2>&1 | grep -E 'ERROR' || true
java -cp /tmp/jvmout com.blocolivre.core.MidState > /tmp/midstate.txt
wc -c /tmp/midstate.txt
