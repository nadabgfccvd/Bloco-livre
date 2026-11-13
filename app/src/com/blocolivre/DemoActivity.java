package com.blocolivre;

import android.app.Activity;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;

import com.blocolivre.core.GameModel;
import com.blocolivre.core.Piece;
import com.blocolivre.game.GameView;
import com.blocolivre.game.SaveStore;

/**
 * DemoActivity — vitrine de arte do Bloco Livre (não aparece no launcher).
 * Cenas controladas por seed para a crítica visual: mid-game com o tabuleiro
 * ocupado e cores mistas, troféu HUD, bandeja com peças distintas e, ao tocar
 * "Cena: limpeza perfeita", a celebração completa com a troca de skin.
 *
 * Usada para fotografar o jogo em vários ângulos/zooms sem jogar manualmente.
 */
public class DemoActivity extends Activity {

    private GameView view;
    private SaveStore store;
    private boolean demoMode = true;
    private String scene = "mid";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        store = new SaveStore(this);
        view = new GameView(this, store);
        view.setListener(null);

        // override das subclasses-foto: skin/cena forçadas
        int forcedSkin = forcedSkin();
        if (forcedSkin >= 0) view.setSkin(forcedSkin);

        String forcedScene = forcedScene();
        if ("hero".equals(forcedScene)) { seedMidGame(view, 20261113L); view.setPhotoFreeze(false); }
        else if ("clear".equals(forcedScene)) seedNearClear(view);
        else if ("full".equals(forcedScene)) seedFullBoard(view);
        else seedMidGame(view, 20261112L);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(0xFF0E1420);

        FrameLayout boardArea = new FrameLayout(this);
        boardArea.addView(view, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        root.addView(boardArea, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        // controles da demo (hero shot os omite; setContentView SEMPRE roda)
        LinearLayout foot = new LinearLayout(this);
        foot.setOrientation(LinearLayout.HORIZONTAL);
        foot.setGravity(Gravity.CENTER);
        foot.setPadding(dp(8), dp(6), dp(8), dp(10));
        Button bMid = dbtn("Cena: partida");
        Button bFull = dbtn("Cena: cheia");
        Button bClear = dbtn("Cena: limpeza");
        Button bSkin = dbtn("Skin " + (view.skinIndex() + 1) + "/4");
        Button bLaunch = dbtn("Modo real");
        bMid.setOnClickListener(v -> { seedMidGame(view, 20261112L); scene = "mid"; });
        bFull.setOnClickListener(v -> { seedFullBoard(view); scene = "full"; });
        bClear.setOnClickListener(v -> { seedNearClear(view); scene = "clear"; });
        bSkin.setOnClickListener(v -> { view.cycleSkin(); bSkin.setText("Skin " + (view.skinIndex() + 1) + "/4"); });
        bLaunch.setOnClickListener(v -> { demoMode = false; });
        LinearLayout.LayoutParams fp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        foot.addView(bMid, fp);
        foot.addView(bFull, fp);
        foot.addView(bClear, fp);
        foot.addView(bSkin, fp);
        foot.addView(bLaunch, fp);
        if (showControls()) root.addView(foot);

        setContentView(root);
        // still de fotografia: congela o relógio no clímax (celebração imortal)
        view.setPhotoFreeze(true);
        // efeitos no PRIMEIRO layout (boardLeft/cell valem 0 no onCreate!):
        // callback determinístico — independe de fila de mensagens do runner.
        view.setOnFirstLayout(this::onSceneReady);
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    /** Override das subclasses-foto (padrão: nenhuma skin forçada). */
    protected int forcedSkin() { return -1; }

    /** Override das subclasses-foto (padrão: cena mid-game). */
    protected String forcedScene() { return "mid"; }
    protected boolean showControls() { return true; }

    /** Acesso da subclasse-foto à view criada. */
    protected GameView view() { return view; }

    /** Chamado após a cena estar montada — subclasses podem disparar efeitos. */
    protected void onSceneReady() { }

    private Button dbtn(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextColor(0xFFEAF0F8);
        b.setAllCaps(false);
        b.setTextSize(12);
        b.setBackgroundColor(0xFF23304A);
        b.setPadding(dp(6), dp(5), dp(6), dp(5));
        return b;
    }

    /** Constrói uma partida crível de mid-game diretamente no modelo (determinístico). */
    private void seedMidGame(GameView gv, long seed) {
        GameModel m = new GameModel(seed);
        // joga como bot guloso até ter peças no tabuleiro e variedade de cor
        int guard = 0;
        while (!m.isOver() && guard++ < 60) {
            boolean placed = false;
            for (int t = 0; t < GameModel.TRAY && !placed; t++) {
                Piece p = m.trayPiece(t);
                if (p == null) continue;
                for (int y = GameModel.H - 1; y >= 0 && !placed; y--)
                    for (int x = 0; x < GameModel.W && !placed; x++)
                        if (m.canPlace(p, x, y)) { m.place(t, x, y); placed = true; }
            }
            if (!placed) break;
            if (m.score() > 900 && hasVariety(m)) break;
        }
        setModelAndView(gv, m);
    }

    /** Tabuleiro a 78% ocupado — tensão máxima, tint de perigo ATIVO. */
    private void seedFullBoard(GameView gv) {
        GameModel m = new GameModel(777L);
        // preenche 6 linhas completas + metade da 7ª (50/64 ≈ 78%) por cima,
        // com cores variadas reais da paleta (via setCellForDemo)
        int v = 3;
        for (int y = 0; y < 6; y++)
            for (int x = 0; x < 8; x++) m.setCellForDemo(x, y, (v++ % 7) + 1);
        for (int x = 0; x < 4; x++) m.setCellForDemo(x, 6, (v++ % 7) + 1);   // 52/64 = 81%
        setModelAndView(gv, m);
    }

    /** Cena de LIMPEZA PERFEITA: fecha a última célula de 2 linhas, esvazia
     *  o tabuleiro de verdade e dispara a celebração (fotografia honesta). */
    private void seedNearClear(GameView gv) {
        GameModel m = new GameModel(31337L);
        // 2 linhas completas exceto (7,7) e (7,6)
        int v = 1;
        for (int y = 6; y <= 7; y++)
            for (int x = 0; x < 7; x++) m.setCellForDemo(x, y, (v++ % 7) + 1);
        // singleton na bandeja (força id 0)
        m.forceTrayForDemo(0, 0, 1);
        // coloca fechando as duas linhas simultaneamente (coluna 7)
        for (int y = 6; y <= 7; y++) m.setCellForDemo(7, y, 4);
        setModelAndView(gv, m);
    }

    private boolean hasVariety(GameModel m) {
        int[] cnt = new int[8];
        for (int y = 0; y < GameModel.H; y++)
            for (int x = 0; x < GameModel.W; x++) cnt[m.cell(x, y)]++;
        int kinds = 0;
        for (int k = 1; k <= 7; k++) if (cnt[k] > 0) kinds++;
        return kinds >= 4;
    }

    private void setModelAndView(GameView gv, GameModel m) {
        gv.adoptModel(m);
        gv.invalidate();
    }

    @SuppressWarnings("unused")
    private void unusedCanvas(Canvas c, Paint p) { p.setColor(Color.WHITE); }
}
