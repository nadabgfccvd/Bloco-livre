package com.blocolivre;

import android.os.Bundle;

/**
 * Alvo de fotografia: hero shot do launcher (jogo em andamento, skin padrão).
 */
public final class ShotHero extends DemoActivity {
    @Override protected String forcedScene() { return "hero"; }
    @Override protected boolean showControls() { return false; }
}
