package com.blocolivre;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;

import com.blocolivre.game.GameView;
import com.blocolivre.game.SaveStore;
import com.blocolivre.game.Skins;

/**
 * Bloco Livre — o anti-Block-Blast: mesmo prazer de jogo, zero anúncios,
 * zero rede (nem permissão INTERNET no manifest), zero manipulação.
 * HUD desenhado no próprio canvas do jogo (tipografia e skin unificadas).
 */
public final class MainActivity extends Activity implements GameView.Listener {

    private GameView view;
    private SaveStore store;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        store = new SaveStore(this);
        view = new GameView(this, store);
        view.setPhotoFreeze(false);
        view.setListener(this);

        android.widget.FrameLayout root = new android.widget.FrameLayout(this);
        root.setBackgroundColor(0xFF0E1420);
        root.addView(view, new android.widget.FrameLayout.LayoutParams(
                android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
                android.widget.FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);
        keepScreenOn(true);
    }

    private void keepScreenOn(boolean on) {
        Window w = getWindow();
        if (on) w.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        else w.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    // ---------------------------------------------------------------- estado
    @Override
    public void onStateChanged() { /* HUD é desenhado no canvas do GameView */ }

    @Override
    public void onFooterButton(int which) {
        switch (which) {
            case 0: confirmNewGame(); break;
            case 1:
                view.cycleSkin();
                flash("Skin: " + view.skinName());
                break;
            case 2:
                if (!view.swapTray()) flash("Nada a trocar agora.");
                break;
            case 3: showAbout(); break;
        }
    }

    @Override
    public void onGameOver(long score, long best, boolean newBest) {
        runOnUiThread(() -> new AlertDialog.Builder(this)
                .setTitle(newBest ? "Novo recorde!" : "Fim de jogo")
                .setMessage("Pontuação: " + score + "\nRecorde: " + best
                        + "\n\nPeças colocadas nesta partida: " + view.model().piecesPlaced()
                        + "\nLimpezas perfeitas: " + view.model().perfectClears()
                        + "\n\nO jogo acabou pelo tabuleiro — não por uma mão armada.\n"
                        + "Nenhum anúncio a assistir, nada a comprar.")
                .setPositiveButton("Jogar de novo", (d, w) -> { view.newGame(); })
                .setNeutralButton("Continuar sem anúncio", (d, w) -> {
                    if (view.model().reviveBudget > 0) {
                        if (view.model().revive()) {
                            view.invalidate(); flash("Bandeja trocada (" + view.model().reviveBudget + " restantes)");
                        } else flash("Sem troca possível: o tabuleiro não tem mais jogada.");
                    } else flash("Trocas esgotadas nesta partida.");
                })
                .setNegativeButton("Fechar", null)
                .show());
    }

    private void confirmNewGame() {
        new AlertDialog.Builder(this)
                .setTitle("Novo jogo?")
                .setMessage("A partida atual será perdida (o recorde fica).")
                .setPositiveButton("Começar", (d, w) -> { view.newGame(); })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void showAbout() {
        new AlertDialog.Builder(this)
                .setTitle("Bloco Livre")
                .setMessage("Um quebra-cabeça de blocos 8×8, gratuito, SEM anúncios e 100% offline.\n\n"
                        + "Este jogo não tem código de rede — nem a permissão INTERNET existe nele. "
                        + "O sorteio das peças é uniforme e independente: nenhuma regra arma mãos "
                        + "insolúveis perto do seu recorde (nada de 'quebra-cabeça letal').\n\n"
                        + "Regras: arraste as peças da bandeja para o tabuleiro; linhas e colunas "
                        + "completas são limpas. Combos consecutivos valem bônus. Limpe o tabuleiro "
                        + "por completo e ganhe +300 — e a skin do jogo muda. 'Trocar bandeja' "
                        + "(máx. 3 por partida) substitui as peças — sem assistir a nada.\n\n"
                        + "Skins: " + listSkins() + " (também no botão SKIN).\n\n"
                        + "Inspiração: o clássico gênero de blocos. Nome, arte e código são próprios.")
                .setPositiveButton("OK", null)
                .show();
    }

    private String listSkins() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Skins.count(); i++) {
            if (i > 0) sb.append(" · ");
            sb.append(Skins.NAMES[i]);
        }
        return sb.toString();
    }

    private void flash(String msg) {
        android.widget.Toast.makeText(this, msg, android.widget.Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onPause() {
        super.onPause();
        view.persist();
    }

    @Override
    protected void onStop() {
        super.onStop();
        view.persist();
    }
}
