package com.blocolivre;

/**
 * Alvo de fotografia: cena LIMPEZA PERFEITA (tabuleiro prestes a limpar) (seed determinística), skin padrão.
 */
public final class ShotSceneClear extends DemoActivity {
    @Override protected String forcedScene() { return "clear"; }
    @Override protected void onSceneReady() { view().demoCelebrate(); }
}
