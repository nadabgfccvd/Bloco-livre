package com.blocolivre.game;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;

import android.view.MotionEvent;
import android.view.View;

import com.blocolivre.core.GameModel;
import com.blocolivre.core.Piece;

import java.util.ArrayList;
import java.util.List;

/**
 * Tela do jogo v2: grade 8×8 + bandeja de 3, desenhada com o sistema de
 * skins (troca na LIMPEZA PERFEITA), partículas físicas, HUD tipográfico
 * em canvas e fundo com profundidade. 100% Canvas puro, zero dependências.
 */
@SuppressLint("ViewConstructor")
public class GameView extends View {

    private GameModel model;
    private final SaveStore store;
    private final AudioCompat audio;

    // ---- skin ativa (muda na limpeza perfeita; persistida)
    private int skinIndex = 0;
    private Skins.Skin skin = Skins.byIndex(0);

    // layout
    private float boardLeft, boardTop, cell;
    private float trayY, trayCell;
    private final RectF boardRect = new RectF();

    // arraste
    private int dragTray = -1;
    private Piece dragPiece;
    private float dragX, dragY, dragOffX, dragOffY;
    private boolean dragging = false;

    // efeitos
    private final ParticleSystem particles = ParticleSystem.create();
    private float popT = 0;               // animação de limpeza (0..1)
    private List<int[]> lastCleared;
    private long lastClearTime;
    private String toast = "";
    private float toastT = 0;
    private float celebrateT = 0;         // celebração ALL CLEAR (0..1)
    private int celebrateFrom = -1, celebrateTo = -1;
    private float hudPulse = 0;           // pulso do score ao pontuar
    private float bgPhase = 0;            // deriva lenta do fundo
    private int placedFlashCells = 0;     // highlight das células recém-postas
    private java.util.List<int[]> placedCells = new java.util.ArrayList<>();
    private float placedT = 0;

    // publicação de estado p/ a Activity
    public interface Listener {
        void onStateChanged();
        void onGameOver(long score, long best, boolean newBest);
        /** Toque num botão-canvas do rodapé: 0=novo jogo · 1=skin · 2=bandeja · 3=sobre. */
        void onFooterButton(int which);
    }
    private Listener listener;

    public GameView(Context ctx, SaveStore store) {
        super(ctx);
        this.store = store;
        this.model = store.load();
        this.skinIndex = store.loadSkin();
        this.skin = Skins.byIndex(skinIndex);
        int[] rawIds = { com.blocolivre.R.raw.place, com.blocolivre.R.raw.clear,
                com.blocolivre.R.raw.combo, com.blocolivre.R.raw.over, com.blocolivre.R.raw.bad };
        this.audio = AudioCompat.create(ctx, rawIds);

        setOnTouchListener(touchListener);
        post(this::replayUiState);
    }

    public void setListener(Listener l) { this.listener = l; }
    public int skinIndex() { return skinIndex; }
    public String skinName() { return Skins.NAMES[skinIndex % Skins.count()]; }

    /** Cicla a skin manualmente (menu). A salva é a última escolhida. */
    public void cycleSkin() {
        setSkin((skinIndex + 1) % Skins.count());
    }

    public void setSkin(int i) {
        this.skinIndex = i % Skins.count();
        this.skin = Skins.byIndex(skinIndex);
        store.saveSkin(skinIndex);
        invalidate();
    }

    private void replayUiState() { if (listener != null) listener.onStateChanged(); }

    // ------------------------------------------------------------ layout
    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        computeLayout(w, h);
    }

    private void computeLayout(int w, int h) {
        float pad = Math.max(8f, w * 0.03f);
        float topReserve = h * 0.125f;      // wordmark + HUD
        float bottomReserve = h * 0.135f;   // streak + botões + crédito
        float availW = w - pad * 2;
        float availH = h - topReserve - bottomReserve;
        float cellW = availW / 8f;
        float cellH = availH / (8f + 2.0f);
        cell = Math.min(cellW, cellH);
        float boardSize = cell * 8;
        boardLeft = (w - boardSize) / 2;
        boardTop = topReserve + pad * 0.5f;
        boardRect.set(boardLeft, boardTop, boardLeft + boardSize, boardTop + boardSize);
        // bandeja colada ao tabuleiro (gap de 0.55 célula)
        trayY = boardTop + boardSize + cell * 0.55f + cell * 0.72f;
        trayCell = cell * 0.82f;            // +20% vs antes
        float halfPanel = trayCell * 2.05f;
        float panelBottom = trayY + halfPanel;
        btnRowY = h - bottomReserve + h * 0.030f;
        // faixa de streak no CENTRO do gap real (painel_fim .. botões) — nunca dentro do painel
        streakY = panelBottom + (btnRowY - panelBottom) / 2f + cell * 0.08f;
        creditY = h - pad * 0.6f;
    }

    private float btnRowY, creditY, streakY;

    // ------------------------------------------------------------ desenho
    private final Paint pA = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint pB = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint pShadowDrop = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint[] pBlock = { pA, pB };
    private final Paint pGhost = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint pText = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF scratch = new RectF();
    private final Path pathScratch = new Path();

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        long frameStart = android.os.SystemClock.elapsedRealtime();
        drawBackground(canvas);
        drawDangerTint(canvas);
        drawCelebrationBack(canvas);      // radiância OURO atrás do board (payoff honesto)
        drawHud(canvas);
        drawBoard(canvas);
        drawTray(canvas);
        drawStreak(canvas);
        drawParticlesAndFloaters(canvas);
        if (dragging && dragPiece != null) drawDrag(canvas);
        drawCelebrationCrown(canvas);     // coroa de estrelas SOBRE o board vazio
        drawCelebration(canvas);
        drawToast(canvas);
        drawFooter(canvas);
        // anima enquanto houver efeito ativo OU perigo respirando
        if (particles.busy() || popT > 0 || toastT > 0 || celebrateT > 0
                || hudPulse > 0 || placedT > 0 || dragging || dangerFrac >= 0.55f) {
            tick();
            postInvalidate();
        }
        lastFrameMs = android.os.SystemClock.elapsedRealtime() - frameStart;
    }

    private long lastFrameMs = 16;
    private float timeScale = 1f;

    private void tick() {
        if (photoFreeze) return;               // still: tempo congelado no clímax
        particles.tick();
        if (popT > 0 && popT < 1) {
            popT = Math.min(1f, popT + 0.075f);
            if (popT >= 1) { popT = 0; lastCleared = null; }
        }
        if (celebrateT > 0) celebrateT = Math.max(0f, celebrateT - 0.006f);
        if (hudPulse > 0) hudPulse = Math.max(0f, hudPulse - 0.02f);
        if (placedT > 0) placedT = Math.max(0f, placedT - 0.02f);
        if (toastT > 0) toastT = Math.max(0f, toastT - 0.008f);
        bgPhase += 0.0015f;
    }

    // ------------------------------------------------------------ fundo
    private void drawBackground(Canvas canvas) {
        canvas.drawColor(skin.bg());
        float w = getWidth(), h = getHeight();
        // vinheta de 4 cantos (mais escura que o bg) — profundidade de estúdio
        pA.setAlpha(255);
        int vg = dim(skin.bg(), 0.35f);
        pA.setColor(vg);
        int steps = 5;
        for (int i = 0; i < steps; i++) {
            float shrink = 0.10f + i * 0.05f;
            float inset = Math.min(w, h) * 0.06f * (steps - i);
            // anel retangular cada vez mais claro p/ dentro (gradiente discreto)
            pA.setColor(dim(skin.bg(), 0.35f - 0.07f * i));
            scratch.set(0, 0, w, h);
            canvas.drawRect(scratch, pA);
            // recorta retângulo interno mais claro por cima
            pA.setColor(dim(skin.bg(), 0.28f - 0.07f * i));
            scratch.set(inset, inset, w - inset, h - inset);
            canvas.drawRect(scratch, pA);
            if (scratch.width() <= 0 || scratch.height() <= 0) break;
            if (shrink > 1f) break;
        }
        // núcleo claro central atrás do tabuleiro (luz de estúdio por trás)
        pA.setColor(dim(skin.boardBg(), -0.18f));
        canvas.drawCircle(w / 2f, boardTop + 4 * cell, w * 0.62f, pA);
        pA.setColor(dim(skin.boardBg(), -0.06f));
        canvas.drawCircle(w / 2f, boardTop + 4 * cell, w * 0.40f, pA);
    }

    /** Radiância OURO + coroa de estrelas no tabuleiro vazio (payoff da limpeza). */
    private void drawCelebrationBack(Canvas canvas) {
        if (celebrateT <= 0) return;
        float cx = boardLeft + 4 * cell, cy = boardTop + 4 * cell;
        // OURO FIXO — nunca o accent da skin (que pode ser ciano/roxo)
        final int G1 = 0xFFFFE08A, G2 = 0xFFFFF7D8;
        // halo dourado por trás do tabuleiro (3 camadas quentes)
        pA.setColor(withAlpha(G1, 96));
        canvas.drawCircle(cx, cy, cell * 6.4f, pA);
        pA.setColor(withAlpha(G1, 72));
        canvas.drawCircle(cx, cy, cell * 5.6f, pA);
        pA.setColor(withAlpha(G2, 60));
        canvas.drawCircle(cx, cy, cell * 4.8f, pA);
        // raios de glória alternados (tamanhos pares/ímpares) — em cima do halo,
        // ATRÁS do board: só as pontas aparecem fora do tabuleiro
        for (int i = 0; i < 12; i++) {
            float ang = (i / 12f) * (float) Math.PI * 2f + 0.13f;
            float len = (i % 2 == 0) ? 6.9f : 5.6f;
            pA.setColor(withAlpha(G1, 110));
            cvSave(canvas);
            canvas.rotate(ang * 57.2958f, cx, cy);
            scratch.set(cx - cell * 0.30f, cy - cell * len, cx + cell * 0.30f, cy - cell * 4.2f);
            canvas.drawRect(scratch, pA);
            canvas.restore();
        }
    }

    /** Coroa de estrelas douradas DENTRO do tabuleiro vazio (desenhada sobre
     *  os wells) — o exclamation point do payoff, sempre visível no still. */
    private void drawCelebrationCrown(Canvas canvas) {
        if (celebrateT <= 0) return;
        float cx = boardLeft + 4 * cell, cy = boardTop + 4 * cell;
        float rx = 3.0f * cell, ry = 2.6f * cell;         // dentro do board 8×8
        for (int i = 0; i < 12; i++) {
            float ang = (i / 12f) * (float) Math.PI * 2f - (float) Math.PI / 2f;
            float sx = cx + (float) Math.cos(ang) * rx;
            float sy = cy + (float) Math.sin(ang) * ry;
            drawStar(canvas, sx, sy, cell * (0.30f + 0.09f * (i % 3)));
        }
        // estrela-mor central acima do banner
        drawStar(canvas, cx, cy - cell * 1.85f, cell * 0.42f);
    }

    /** Tint de perigo quando o tabuleiro enche — pulsa devagar (respiração). */
    private void drawDangerTint(Canvas canvas) {
        int filled = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                if (model.cell(x, y) != 0) filled++;
        dangerFrac = filled / 64f;
        if (dangerFrac < 0.55f) return;
        float k = (dangerFrac - 0.55f) / 0.45f;        // 0..1
        // respiração: 0.75..1.0 (1 ciclo ~2.6s)
        float breath = 0.75f + 0.25f * (float) Math.sin(dangerPhase);
        int a = (int) (90 * k * breath);
        if (a <= 0) return;
        canvas.drawColor(0x20FF5252 & 0x00FFFFFF | (a << 24));
        // véu quente POR CIMA do tabuleiro (blocos também esquentam)
        int scd = canvas.save();
        canvas.clipRect(boardRect);
        canvas.drawColor(0x28B05038 & 0x00FFFFFF | ((int) (70 * k) << 24));
        canvas.restoreToCount(scd);
        // glow quente ATRÁS do tabuleiro (medo preenche a tela, não murmura)
        float bcx = boardLeft + 4 * cell, bcy = boardTop + 4 * cell;
        pA.setColor(withAlpha(0xFF8A3A30, (int) (46 * k)));
        canvas.drawCircle(bcx, bcy, cell * 6.4f, pA);
        pA.setColor(withAlpha(0xFFB05038, (int) (30 * k)));
        canvas.drawCircle(bcx, bcy, cell * 5.2f, pA);
        dangerPhase += 0.014f;
    }

    private float dangerFrac = 0f;
    private float dangerPhase = 0f;
    private boolean photoFreeze = false;

    /** Congela o relógio interno (celebração/partículas) — só p/ stills da demo. */
    public void setPhotoFreeze(boolean b) { photoFreeze = b; }

    // ------------------------------------------------------------ HUD
    private void drawHud(Canvas canvas) {
        float w = getWidth();
        float pad = Math.max(8f, w * 0.03f);
        // WORDMARK — identidade no topo, tracking largo, peso bold
        pText.setTextAlign(Paint.Align.CENTER);
        pText.setFakeBoldText(true);
        pText.setLetterSpacing(0.22f);
        pText.setColor(skin.hudTitle());
        pText.setTextSize(cell * 0.40f);
        canvas.drawText("BLOCO LIVRE", w / 2f, boardTop - cell * 1.62f, pText);
        pText.setLetterSpacing(0f);
        // sub-linha editorial
        pText.setFakeBoldText(false);
        pText.setTextSize(cell * 0.20f);
        pText.setColor(skin.hudSub());
        canvas.drawText("quebra-cabeça de blocos · sem anúncios · offline", w / 2f, boardTop - cell * 1.34f, pText);

        // SCORE (esquerda) — pulsa ao pontuar
        float pulse = 1f + 0.10f * hudPulse;
        pText.setTextAlign(Paint.Align.LEFT);
        pText.setColor(skin.hudSub());
        pText.setTextSize(cell * 0.28f);
        pText.setFakeBoldText(true);
        pText.setTextSize(cell * 0.24f);
        canvas.drawText("PONTOS", pad, boardTop - cell * 0.78f, pText);
        pText.setColor(skin.hudTitle());
        pText.setTextSize(cell * (0.62f * pulse));
        canvas.drawText(String.valueOf(model.score()), pad, boardTop - cell * 0.14f, pText);
        // combo embaixo
        pText.setFakeBoldText(false);
        pText.setTextSize(cell * 0.24f);
        if (model.combo() >= 2) {
            pText.setColor(skin.hudAccent());
            canvas.drawText("combo x" + model.combo() + "  ·  máx x" + model.comboBest(), pad, boardTop + cell * 0.20f, pText);
        } else {
            pText.setColor(skin.hudSub());
            canvas.drawText("sem combo ativo", pad, boardTop + cell * 0.20f, pText);
        }
        // RECORDE (direita) com troféu — mesma família/tamanho do PONTOS
        pText.setTextAlign(Paint.Align.RIGHT);
        pText.setFakeBoldText(true);
        pText.setTextSize(cell * 0.28f);
        pText.setColor(skin.hudSub());
        pText.setTextSize(cell * 0.19f);
        canvas.drawText("RECORDE", w - pad - cell * 0.92f, boardTop - cell * 0.78f, pText);
        pText.setColor(skin.hudAccent());
        pText.setTextSize(cell * 0.40f);
        canvas.drawText(String.valueOf(model.best()), w - pad - cell * 0.92f, boardTop - cell * 0.30f, pText);
        drawTrophy(canvas, w - pad - cell * 0.44f, boardTop - cell * 0.52f, cell * 0.26f);
        // limpezas perfeitas
        pText.setFakeBoldText(false);
        pText.setTextSize(cell * 0.22f);
        if (model.perfectClears() > 0) {
            pText.setColor(skin.hudAccent());
            canvas.drawText("★ limpezas perfeitas: " + model.perfectClears(), w - pad - cell * 0.92f, boardTop + cell * 0.20f, pText);
        } else {
            pText.setColor(skin.hudSub());
            canvas.drawText("skin: " + skinName(), w - pad - cell * 0.92f, boardTop + cell * 0.20f, pText);
        }
        pText.setTextAlign(Paint.Align.LEFT);
    }

    private void drawTrophy(Canvas cv, float cx, float cy, float r) {
        // troféu minimalista: taça + base, traço 2px
        pB.setColor(skin.hudAccent());
        pB.setStyle(Paint.Style.STROKE);
        pB.setStrokeWidth(Math.max(1.6f, r * 0.16f));
        pathScratch.reset();
        // taça
        pathScratch.moveTo(cx - r * 0.55f, cy - r);
        pathScratch.lineTo(cx + r * 0.55f, cy - r);
        pathScratch.lineTo(cx + r * 0.38f, cy - r * 0.05f);
        pathScratch.quadTo(cx, cy + r * 0.32f, cx - r * 0.38f, cy - r * 0.05f);
        pathScratch.close();
        cv.drawPath(pathScratch, pB);
        // haste + base
        cv.drawLine(cx, cy + r * 0.1f, cx, cy + r * 0.45f, pB);
        cv.drawLine(cx - r * 0.5f, cy + r, cx + r * 0.5f, cy + r, pB);
        cv.drawLine(cx - r * 0.3f, cy + r * 0.45f, cx + r * 0.3f, cy + r * 0.45f, pB);
        pB.setStyle(Paint.Style.FILL);
    }

    // ------------------------------------------------------------ tabuleiro
    private void drawBoard(Canvas canvas) {
        // SOMBRA PROJETADA do painel (luz vem de cima → sombra desloca p/ baixo)
        float sh = cell * 0.30f;
        pShadowDrop.setColor(0x44000000);
        for (int i = 3; i >= 1; i--) {
            float off = sh * i / 3f;
            scratch.set(boardRect.left - off * 0.4f, boardRect.top + off,
                    boardRect.right + off * 0.4f, boardRect.bottom + off * 1.15f);
            canvas.drawRoundRect(scratch, cell * 0.3f, cell * 0.3f, pShadowDrop);
        }
        // moldura: camada externa (borda luminosa de cima — luz de estúdio)
        float fr = cell * 0.12f;
        scratch.set(boardRect.left - fr, boardRect.top - fr,
                boardRect.right + fr, boardRect.bottom + fr);
        pA.setColor(dim(skin.boardBorder(), -0.35f));   // topo claro
        canvas.drawRoundRect(scratch, cell * 0.32f, cell * 0.32f, pA);
        // camada de baixo da moldura mais escura (bisel)
        scratch.set(boardRect.left - fr * 0.6f, boardRect.top - fr * 0.5f,
                boardRect.right + fr * 0.6f, boardRect.bottom + fr * 0.7f);
        pA.setColor(dim(skin.boardBorder(), 0.25f));
        canvas.drawRoundRect(scratch, cell * 0.30f, cell * 0.30f, pA);
        // corpo
        pA.setColor(skin.boardBg());
        canvas.drawRoundRect(boardRect, cell * 0.24f, cell * 0.24f, pA);
        // borda aquece com o perigo (vermelho sobe junto com o tint)
        int borderCol = skin.boardBorder();
        if (dangerFrac >= 0.55f) {
            float k = Math.min(1f, (dangerFrac - 0.55f) / 0.25f);
            borderCol = blend(borderCol, 0xFFC24A42, 0.85f * k);
        }
        pA.setColor(borderCol);
        pA.setStyle(Paint.Style.STROKE);
        pA.setStrokeWidth(Math.max(2f, cell * 0.05f));
        canvas.drawRoundRect(boardRect, cell * 0.24f, cell * 0.24f, pA);
        pA.setStyle(Paint.Style.FILL);

        // casas vazias — "wells usinadas": paridade xadrez + sombra interna
        // no topo (luz de cima) + rim light fino embaixo (rebatimento)
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++) {
                int v = model.cell(x, y);
                float l = boardLeft + x * cell + cell * 0.055f;
                float t = boardTop + y * cell + cell * 0.055f;
                float s = cell * 0.89f;
                boolean popping = isPopping(x, y);
                if (popping) {
                    pA.setColor(0xFFFFFFFF);
                    float grow = s * (0.18f * popT);
                    canvas.drawRoundRect(l - grow, t - grow, l + s + grow, t + s + grow, s * 0.18f, s * 0.18f, pA);
                } else if (v == 0) {
                    int base = ((x + y) % 2 == 0) ? skin.cellEmpty() : dim(skin.cellEmpty(), 0.18f);
        if (dangerFrac >= 0.55f) {
            float dk = Math.min(1f, (dangerFrac - 0.55f) / 0.25f);   // força total já aos 80%
            base = blend(base, 0xFF7A3038, 0.45f * dk);   // wells aquecem no perigo
        }
                    // AO dependente de vizinho: well sob bloco recebe sombra de contato EXTRA
                    boolean shadedAbove = y > 0 && model.cell(x, y - 1) != 0;
                    pA.setColor(base);
                    canvas.drawRoundRect(l, t, l + s, t + s, s * 0.20f, s * 0.20f, pA);
                    // sombra interna do topo (luz vem de cima) + AO de contato se há bloco acima
                    pA.setColor(shadedAbove ? 0x8C000000 : 0x3D000000);
                    float shH = shadedAbove ? 0.40f : 0.26f;
                    scratch.set(l + s * 0.06f, t + s * 0.03f, l + s * 0.94f, t + s * shH);
                    canvas.drawRoundRect(scratch, s * 0.10f, s * 0.10f, pA);
                    // rim light embaixo (luz rebatida da borda inferior)
                    pA.setColor(withAlpha(skin.hudTitle(), 28));
                    scratch.set(l + s * 0.06f, t + s * 0.80f, l + s * 0.94f, t + s * 0.97f);
                    canvas.drawRoundRect(scratch, s * 0.10f, s * 0.10f, pA);
                } else {
                    boolean flash = isPlacedCell(x, y);
                    if (flash) {
                        float g = s * (0.16f * (1f - placedT));
                        skin.block(canvas, l - g, t - g, s + 2 * g, skin.palette()[v], pBlock);
                    } else {
                        skin.block(canvas, l, t, s, skin.palette()[v], pBlock);
                    }
                    // AO: bloco com vizinho OCUPADO acima ganha sombra curta
                    // tingida pela cor DELE ( contato entre blocos empilhados)
                    if (y > 0 && model.cell(x, y - 1) != 0) {
                        int above = skin.palette()[model.cell(x, y - 1)];
                        int tinted = tintShadow(above);
                        pA.setColor(withAlpha(tinted, 190));
                        scratch.set(l, t, l + s, t + s * 0.20f);
                        canvas.drawRoundRect(scratch, s * 0.08f, s * 0.08f, pA);
                    }
                }
            }
        // fantasma da posição de soltura (outline + fill translúcido)
        if (dragging && dragPiece != null && ghostValid) {
            int[] pal = skin.palette();
            int col = pal[dragPiece.color];
            for (int k = 0; k < dragPiece.cells.length; k += 2) {
                int x = ghostX + dragPiece.cells[k], y = ghostY + dragPiece.cells[k + 1];
                float l = boardLeft + x * cell + cell * 0.07f;
                float t = boardTop + y * cell + cell * 0.07f;
                float s = cell * 0.86f;
                pGhost.setColor(col);
                pGhost.setAlpha(56);
                canvas.drawRoundRect(l, t, l + s, t + s, s * 0.20f, s * 0.20f, pGhost);
                pGhost.setAlpha(200);
                pGhost.setStyle(Paint.Style.STROKE);
                pGhost.setStrokeWidth(Math.max(2f, s * 0.07f));
                canvas.drawRoundRect(l, t, l + s, t + s, s * 0.20f, s * 0.20f, pGhost);
                pGhost.setStyle(Paint.Style.FILL);
                pGhost.setAlpha(255);
            }
        }
    }

    private boolean isPopping(int x, int y) {
        if (lastCleared == null || popT <= 0 || popT >= 1) return false;
        for (int[] c : lastCleared) if (c[0] == x && c[1] == y) return true;
        return false;
    }

    private boolean isPlacedCell(int x, int y) {
        if (placedT <= 0 || placedCells.isEmpty()) return false;
        for (int[] c : placedCells) if (c[0] == x && c[1] == y) return true;
        return false;
    }

    // ------------------------------------------------------------ bandeja
    private void drawTray(Canvas canvas) {
        float w = getWidth();
        if (celebrateT > 0) { drawTrayDimmed(canvas); return; }
        drawTrayNormal(canvas);
    }

    private void drawTrayNormal(Canvas canvas) {
        // painel da bandeja colado ao tabuleiro
        float w = getWidth();
        float halfPanel = trayCell * 2.05f;
        // sombra + corpo
        float sh = cell * 0.12f;
        pShadowDrop.setColor(0x30000000);
        scratch.set(w * 0.05f + sh * 0.3f, trayY - halfPanel + sh,
                w * 0.95f + sh * 0.3f, trayY + halfPanel + sh);
        canvas.drawRoundRect(scratch, cell * 0.3f, cell * 0.3f, pShadowDrop);
        scratch.set(w * 0.05f, trayY - halfPanel, w * 0.95f, trayY + halfPanel);
        int trayCol = dim(skin.boardBg(), -0.02f);
        if (dangerFrac >= 0.55f) trayCol = blend(trayCol, 0xFF8A3A30,
                0.38f * Math.min(1f, (dangerFrac - 0.55f) / 0.45f));
        pA.setColor(trayCol);
        canvas.drawRoundRect(scratch, cell * 0.28f, cell * 0.28f, pA);

        // clip: nada da bandeja vaza do painel (peças 1×5 incluídas)
        int sc = canvas.save();
        canvas.clipRect(w * 0.06f, trayY - halfPanel + 2f, w * 0.94f, trayY + halfPanel - 2f);

        for (int i = 0; i < 3; i++) {
            Piece pc = model.trayPiece(i);
            float cx = trayCenterX(i);
            if (dragging && dragTray == i) continue;
            if (pc == null) {
                pA.setColor(skin.cellEmpty());
                float s2 = trayCell;
                canvas.drawRoundRect(cx - s2 / 2, trayY - s2 / 2, cx + s2 / 2, trayY + s2 / 2, s2 * 0.2f, s2 * 0.2f, pA);
                continue;
            }
            // escala por área: peças largas/altas encolhem p/ caber no slot
            float maxDim = Math.max(pc.w, pc.h);
            float area = (pc.w * pc.h);
            float scf = 1f;
            if (maxDim >= 4) scf = 0.72f;
            else if (maxDim >= 3) scf = 0.86f;
            if (area >= 9) scf *= 0.90f;
            float sc2 = trayCell * scf;
            float off = (pc.w - 1) * sc2 / 2f;
            for (int k = 0; k < pc.cells.length; k += 2) {
                float l = cx - off + pc.cells[k] * sc2;
                float t = trayY - (pc.h - 1) * sc2 / 2f + pc.cells[k + 1] * sc2;
                skin.block(canvas, l, t, sc2, skin.palette()[pc.color], pBlock);
            }
        }
        canvas.restoreToCount(sc);
    }

    /** Bandeja escurecida durante o clímax (foco único no payoff). */
    private void drawTrayDimmed(Canvas canvas) {
        // versão normal + véu escuro 55%
        drawTrayNormal(canvas);
        int sc = canvas.save();
        canvas.clipRect(0, trayY - trayCell * 2.1f, getWidth(), trayY + trayCell * 2.1f);
        pA.setColor(withAlpha(0xFF0E0A06, 152));
        canvas.drawRect(0, trayY - trayCell * 2.1f, getWidth(), trayY + trayCell * 2.1f, pA);
        canvas.restoreToCount(sc);
    }

    private float trayCenterX(int i) {
        float w = getWidth();
        return w / 2 + (i - 1) * (w / 3.4f);
    }

    private void drawDrag(Canvas canvas) {
        float sc = cell;
        float offx = dragX - dragOffX * sc;
        float offy = dragY - dragOffY * sc;
        for (int k = 0; k < dragPiece.cells.length; k += 2) {
            float l = offx + dragPiece.cells[k] * sc;
            float t = offy + dragPiece.cells[k + 1] * sc;
            skin.block(canvas, l, t, sc, skin.palette()[dragPiece.color], pBlock);
        }
    }

    // ------------------------------------------------------------ partículas/flutuantes
    private void drawParticlesAndFloaters(Canvas canvas) {
        // partículas confinadas abaixo do HUD (nunca cobrem wordmark/pontuação)
        int sc = canvas.save();
        canvas.clipRect(0, boardTop - cell * 0.30f, getWidth(), getHeight());
        particles.draw(canvas);
        canvas.restoreToCount(sc);
        long now = System.currentTimeMillis();
        for (int i = floaters.size() - 1; i >= 0; i--) {
            Floater e = floaters.get(i);
            float dt = (now - e.t0) / 900f;
            if (dt >= 1) { floaters.remove(i); continue; }
            pText.setColor(Color.WHITE);
            pText.setAlpha((int) (255 * (1 - dt)));
            pText.setFakeBoldText(true);
            pText.setTextSize(cell * (e.big ? 0.95f : 0.55f));
            float ty = e.y - dt * cell * 1.5f;
            pText.setTextAlign(Paint.Align.CENTER);
            canvas.drawText(e.text, e.x, ty, pText);
            pText.setTextAlign(Paint.Align.LEFT);
        }
    }

    // ------------------------------------------------------------ celebração ALL CLEAR
    private void drawCelebration(Canvas canvas) {
        if (celebrateT <= 0) return;
        float t = 1f - celebrateT;                     // 0→1 progresso
        float w = getWidth(), h = getHeight();
        // flash de tela suave
        int flashA = (int) (72 * Math.max(0f, celebrateT - 0.55f) / 0.45f);
        if (flashA > 0) {
            pA.setColor((0xFFFFFF) | (flashA << 24));
            canvas.drawColor(pA.getColor());
        }
        // ---- PAYOFF FRAME: banner OURO central simétrico sobre o board vazio
        float cx = boardLeft + 4 * cell, cy = boardTop + 4 * cell;
        cvSave(canvas);
        float slide = (t - 0.5f) * w * 1.4f;
        canvas.rotate(-6f, cx, cy);
        // underlay escuro SIMÉTRICO centrado no board (mata compete-foco)
        pB.setColor(withAlpha(0xFF1A1208, 232));
        scratch.set(cx - w * 0.36f, cy - cell * 1.34f, cx + w * 0.36f, cy + cell * 0.98f);
        canvas.drawRect(scratch, pB);
        // faixa OURO grossa + filete branco
        pB.setColor(0xFFF6C445);
        pB.setAlpha(238);
        scratch.set(cx - w * 0.36f + slide * 0.6f * 0f, cy - cell * 1.26f, cx + w * 0.36f, cy - cell * 0.90f);
        canvas.drawRect(scratch, pB);
        pB.setColor(withAlpha(0xFFFFFFFF, 90));
        scratch.set(cx - w * 0.36f, cy - cell * 0.90f, cx + w * 0.36f, cy - cell * 0.86f);
        canvas.drawRect(scratch, pB);
        pB.setAlpha(255);
        // texto display com sombra dura
        pText.setTextAlign(Paint.Align.CENTER);
        pText.setFakeBoldText(true);
        pText.setLetterSpacing(0.10f);
        pText.setColor(0xE6221808);
        canvas.drawText("LIMPEZA PERFEITA!", cx + 3, cy + cell * 0.17f, pText);
        pText.setColor(Color.WHITE);
        pText.setTextSize(cell * 0.95f);
        canvas.drawText("LIMPEZA PERFEITA!", cx, cy + cell * 0.14f, pText);
        pText.setTextSize(cell * 0.42f);
        pText.setLetterSpacing(0.16f);
        pText.setColor(withAlpha(0xFFFFF3C8, 245));
        canvas.drawText("NOVA SKIN · " + Skins.NAMES[celebrateTo].toUpperCase(), cx, cy + cell * 0.72f, pText);
        pText.setLetterSpacing(0f);
        pText.setTextAlign(Paint.Align.LEFT);
        pText.setFakeBoldText(false);
        pB.setAlpha(255);
        canvas.restore();
    }

    static int dim(int color, float f) {
        int r = (color >> 16) & 0xFF, g = (color >> 8) & 0xFF, b = color & 0xFF;
        float k = 1f - f;
        r = Math.max(0, Math.min(255, (int) (r * k)));
        g = Math.max(0, Math.min(255, (int) (g * k)));
        b = Math.max(0, Math.min(255, (int) (b * k)));
        return 0xFF000000 | (r << 16) | (g << 8) | b;
    }

    static int withAlpha(int color, int alpha) {
        return (color & 0x00FFFFFF) | (alpha << 24);
    }

    /** Sombra "tingida": versão escura e levemente dessaturada da cor de origem. */
    static int tintShadow(int color) {
        int r = (color >> 16) & 0xFF, g = (color >> 8) & 0xFF, b = color & 0xFF;
        r = (int) (r * 0.38f); g = (int) (g * 0.34f); b = (int) (b * 0.42f);
        return 0xFF000000 | (r << 16) | (g << 8) | b;
    }

    static int blend(int a, int b, float k) {
        int ar = (a >> 16) & 0xFF, ag = (a >> 8) & 0xFF, ab = a & 0xFF;
        int br = (b >> 16) & 0xFF, bg = (b >> 8) & 0xFF, bb = b & 0xFF;
        int r = (int) (ar + (br - ar) * k);
        int g = (int) (ag + (bg - ag) * k);
        int bl = (int) (ab + (bb - ab) * k);
        return 0xFF000000 | (r << 16) | (g << 8) | bl;
    }

    private void cvSave(Canvas c) { c.save(); }

    private void drawToast(Canvas canvas) {
        if (toastT <= 0) return;
        float w = getWidth();
        pText.setColor(Color.WHITE);
        pText.setAlpha((int) Math.max(0, Math.min(255, toastT * 255)));
        pText.setTextSize(cell * 0.5f);
        pText.setTextAlign(Paint.Align.CENTER);
        canvas.drawText(toast, w / 2f, boardTop - cell * 0.4f, pText);
        pText.setTextAlign(Paint.Align.LEFT);
    }

    // ------------------------------------------------------------ streak
    /** Faixa viva entre bandeja e rodapé: pips de combo + troféus de limpeza
     *  perfeita + mini-estatísticas — mata o dead band com informação real. */
    private void drawStreak(Canvas canvas) {
        float w = getWidth();
        float pad = Math.max(8f, w * 0.05f);
        float midY = streakY;
        // pips de combo (histórico): 5 slots, acesos = combo atual
        pText.setTextAlign(Paint.Align.LEFT);
        pText.setFakeBoldText(true);
        pText.setTextSize(cell * 0.22f);
        pText.setColor(skin.hudSub());
        canvas.drawText("COMBO", pad, midY + cell * 0.08f, pText);
        float pipX = pad + cell * 1.15f;
        float pipR = cell * 0.115f;
        for (int i = 0; i < 5; i++) {
            boolean lit = i < Math.min(5, model.combo());
            pA.setColor(lit ? skin.hudAccent() : skin.cellEmpty());
            canvas.drawCircle(pipX + i * pipR * 2.6f, midY, pipR * (lit ? 1f : 0.8f), pA);
        }
        // mini-estatísticas à direita: peças · limpezas
        pText.setTextAlign(Paint.Align.RIGHT);
        pText.setFakeBoldText(false);
        pText.setTextSize(cell * 0.20f);
        pText.setColor(skin.hudSub());
        canvas.drawText("peças " + model.piecesPlaced() + "   ·   linhas " + model.linesCleared(),
                w - pad, midY + cell * 0.07f, pText);
        pText.setTextAlign(Paint.Align.LEFT);
        pText.setFakeBoldText(false);
        // estrelas de limpeza perfeita (acima do combo)
        if (model.perfectClears() > 0) {
            for (int i = 0; i < Math.min(3, model.perfectClears()); i++)
                drawStar(canvas, pad + cell * 1.15f + (5 + i * 2) * pipR * 2.6f / 2f, midY, pipR * 1.3f);
        }
    }

    private void drawStar(Canvas cv, float cx, float cy, float r) {
        pB.setColor(0xFFFFF176);
        pathScratch.reset();
        for (int k = 0; k < 8; k++) {
            float ang = k * (float) Math.PI / 4f - (float) Math.PI / 2f;
            float rr = (k % 2 == 0) ? r : r * 0.42f;
            float px = cx + (float) Math.cos(ang) * rr;
            float py = cy + (float) Math.sin(ang) * rr;
            if (k == 0) pathScratch.moveTo(px, py); else pathScratch.lineTo(px, py);
        }
        pathScratch.close();
        cv.drawPath(pathScratch, pB);
    }
    private static final String[] BTN_LABELS = { "NOVO JOGO", "SKIN", "BANDEJA", "SOBRE" };

    private void drawFooter(Canvas canvas) {
        float w = getWidth();
        float pad = Math.max(8f, w * 0.03f);
        float rowW = w - pad * 2;
        float btnW = (rowW - pad * 0.6f * 3f) / 4f;
        float btnH = cell * 0.62f;
        float labelSize = Math.min(cell * 0.21f, btnH * 0.34f);
        for (int i = 0; i < 4; i++) {
            float l = pad + i * (btnW + pad * 0.6f);
            float t = btnRowY;
            // sombra
            pShadowDrop.setColor(0x2E000000);
            scratch.set(l + 2f, t + 3f, l + btnW, t + btnH + 3f);
            canvas.drawRoundRect(scratch, btnH * 0.35f, btnH * 0.35f, pShadowDrop);
            // corpo (bisel: topo claro, base escura)
            pA.setColor(dim(skin.footerBtn(), -0.30f));
            scratch.set(l, t, l + btnW - 2f, t + btnH);
            canvas.drawRoundRect(scratch, btnH * 0.35f, btnH * 0.35f, pA);
            pA.setColor(dim(skin.footerBtn(), 0.22f));
            scratch.set(l, t + btnH * 0.55f, l + btnW - 2f, t + btnH - 2f);
            canvas.drawRoundRect(scratch, btnH * 0.3f, btnH * 0.3f, pA);
            // rótulo
            pText.setTextAlign(Paint.Align.CENTER);
            pText.setFakeBoldText(true);
            pText.setLetterSpacing(0.06f);
            pText.setTextSize(labelSize);
            pText.setColor(skin.hudTitle());
            canvas.drawText(BTN_LABELS[i], l + (btnW - 2f) / 2f, t + btnH * 0.62f, pText);
            pText.setLetterSpacing(0f);
            pText.setFakeBoldText(false);
            pText.setTextAlign(Paint.Align.LEFT);
        }
        // crédito editorial
        pText.setTextAlign(Paint.Align.CENTER);
        pText.setTextSize(cell * 0.17f);
        pText.setColor(skin.hudSub());
        canvas.drawText("Bloco Livre · jogo livre de anúncios · 100% offline", w / 2f, creditY, pText);
        pText.setTextAlign(Paint.Align.LEFT);
    }

    /** Hit-test dos botões-canvas do rodapé. Retorna 0..3 ou -1. */
    private int footerButtonAt(float x, float y) {
        float w = getWidth();
        float pad = Math.max(8f, w * 0.03f);
        float rowW = w - pad * 2;
        float btnW = (rowW - pad * 0.6f * 3f) / 4f;
        float btnH = cell * 0.62f;
        if (y < btnRowY || y > btnRowY + btnH) return -1;
        for (int i = 0; i < 4; i++) {
            float l = pad + i * (btnW + pad * 0.6f);
            if (x >= l && x <= l + btnW) return i;
        }
        return -1;
    }

    // ------------------------------------------------------------ toque
    private final OnTouchListener touchListener = new OnTouchListener() {
        @Override
        public boolean onTouch(View v, MotionEvent ev) {
            switch (ev.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    beginDrag(ev);
                    return true;
                case MotionEvent.ACTION_MOVE:
                    if (dragging) { dragX = ev.getX(); dragY = ev.getY(); updateGhost(); invalidate(); }
                    return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    if (dragging) { endDrag(); }
                    return true;
            }
            return true;
        }
    };

    private void beginDrag(MotionEvent ev) {
        if (model.isOver()) return;
        dragX = ev.getX(); dragY = ev.getY();
        // botões do rodapé têm prioridade (área exclusiva deles)
        int btn = footerButtonAt(dragX, dragY);
        if (btn >= 0) {
            if (listener != null) listener.onFooterButton(btn);
            return;
        }
        for (int i = 0; i < 3; i++) {
            Piece pc = model.trayPiece(i);
            if (pc == null) continue;
            float cx = trayCenterX(i);
            float half = trayCell * Math.max(pc.w, 1) * 1.2f;
            if (Math.abs(dragX - cx) < half + trayCell && dragY > trayY - trayCell * 2 && dragY < trayY + trayCell * 2) {
                dragTray = i; dragPiece = pc;
                dragging = true;
                dragOffX = 0; dragOffY = 0;
                dragOffX = Math.max(0, Math.min(pc.w - 0.01f, (dragX - cx) / trayCell + pc.w / 2f));
                dragOffY = Math.max(0, Math.min(pc.h - 0.01f, (dragY - trayY) / trayCell + pc.h / 2f));
                updateGhost();
                invalidate();
                return;
            }
        }
    }

    private int ghostX = -99, ghostY = -99;
    private boolean ghostValid;

    private void updateGhost() {
        ghostValid = false;
        if (!dragging || dragPiece == null) return;
        int cx = Math.round((dragX - dragOffX * cell - boardLeft) / cell);
        int cy = Math.round((dragY - dragOffY * cell - boardTop) / cell);
        Piece pc = dragPiece;
        float pxc = dragX, pyc = dragY;
        int bestX = -99, bestY = -99; double bestD = Double.MAX_VALUE;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                if (model.canPlace(pc, x, y)) {
                    float ccx = boardLeft + (x + pc.w / 2f) * cell;
                    float ccy = boardTop + (y + pc.h / 2f) * cell;
                    double d = (ccx - pxc) * (ccx - pxc) + (ccy - pyc) * (ccy - pyc);
                    if (d < bestD) { bestD = d; bestX = x; bestY = y; }
                }
        if (bestX != -99 && bestD < cell * cell * 9) { ghostX = bestX; ghostY = bestY; ghostValid = true; }
    }

    private void endDrag() {
        if (ghostValid && dragPiece != null) {
            // captura as células da peça ANTES de place() consumir a bandeja
            int[] placedRel = dragPiece.cells.clone();
            int placedColor = dragPiece.color;
            GameModel.PlaceResult r = model.place(dragTray, ghostX, ghostY);
            if (r.ok) {
                onPlaced(r, placedRel, placedColor);
            } else {
                audio.play(4);
            }
        }
        dragging = false; dragPiece = null; dragTray = -1; ghostValid = false;
        invalidate();
        replayUiState();
        store.save(model);
    }

    private void onPlaced(GameModel.PlaceResult r, int[] placedRel, int placedColor) {
        audio.play(0);
        audio.buzz(12);
        hudPulse = 1f;
        // células recém-postas → flash pop-in
        placedCells.clear();
        for (int k = 0; k < placedRel.length; k += 2)
            placedCells.add(new int[]{ r.ox + placedRel[k], r.oy + placedRel[k + 1] });
        placedT = 1f;
        int n = r.lines + r.cols;
        if (n > 0) {
            popT = 0.05f;
            lastCleared = r.cleared;
            lastClearTime = System.currentTimeMillis();
            // faíscas por célula limpa
            for (int[] c : r.cleared)
                particles.burstSpark(boardLeft + (c[0] + 0.5f) * cell, boardTop + (c[1] + 0.5f) * cell,
                        skin.palette()[placedColor], 3);
            floaters.add(new Floater("+" + r.gained, boardLeft + 4 * cell, boardTop + 3.5f * cell, false));
            if (n >= 2) particles.ring(getWidth() / 2f, boardTop + 4 * cell, 0xFFFFFFFF);
            if (n >= 2 || r.comboNow >= 2) {
                String t = n >= 3 ? "INCRÍVEL!" : n == 2 ? "ÓTIMO!" : "COMBO x" + r.comboNow;
                floaters.add(new Floater(t, boardLeft + 4 * cell, boardTop + 2 * cell, true));
                particles.confettiRain(getWidth(), skin.palette(), 26);
                audio.play(2);
            } else {
                audio.play(1);
            }
            audio.buzz(30);
        }
        if (r.allClear) {
            // 🎉 LIMPEZA PERFEITA: celebração + troca de skin
            celebrateFrom = skinIndex;
            celebrateTo = (skinIndex + 1) % Skins.count();
            celebrateT = 1f;
            float bx = boardLeft + 4 * cell, by = boardTop + 4 * cell;
            particles.starRing(bx, by, cell * 1.5f, 18, 0xFFFFF176);
            particles.starRing(bx, by, cell * 2.5f, 14, skin.hudAccent());
            particles.confettiRain(getWidth(), Skins.byIndex(celebrateTo).palette(), 60);
            // (o banner dourado já comunica o bônus — sem floater duplicado)
            setSkin(celebrateTo);
        }
        if (model.isOver()) {
            audio.play(3);
            if (listener != null) listener.onGameOver(model.score(), model.best(), model.score() >= model.best());
        }
    }

    // ------------------------------------------------------------ ações públicas
    public void newGame() {
        model.resetNewGame();
        particles.clear();
        floaters.clear();
        popT = 0; lastCleared = null; celebrateT = 0;
        invalidate(); replayUiState(); store.save(model);
    }

    /** O "continue" honesto: troca a bandeja (máx. 3 por partida, sem anúncio). */
    public boolean swapTray() {
        boolean ok = model.swapTray();
        if (ok) {
            audio.play(2);
            toast = "Bandeja nova"; toastT = 1f;
            invalidate(); replayUiState(); store.save(model);
        }
        invalidate();
        return ok;
    }

    public GameModel model() { return model; }
    public void persist() { store.save(model); }

    /** Adota um modelo externo (cenas da DemoActivity) sem tocar o save real. */
    public void adoptModel(GameModel m) { this.model = m; invalidate(); }

    /** Dispara a celebração de LIMPEZA PERFEITA agora (fotografia da demo). */
    public void demoCelebrate() {
        // a limpeza perfeita ESVAZIA o tabuleiro (senão o still mente)
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++) model.setCellForDemo(x, y, 0);
        celebrateFrom = skinIndex;
        celebrateTo = (skinIndex + 1) % Skins.count();
        celebrateT = 0.62f;   // congela num momento fotogênico (faixa + texto visíveis)
        float bx = boardLeft + 4 * cell, by = boardTop + 4 * cell;
        particles.starRing(bx, by, cell * 1.5f, 18, 0xFFFFF176);
        particles.starRing(bx, by, cell * 2.5f, 14, skin.hudAccent());
        particles.confettiRainBoard(getWidth(), boardTop, boardTop + 8 * cell, skin.palette(), 60);
        particles.burstSpark(bx, by, 0xFFFFFFFF, 24);
        floaters.add(new Floater("LIMPEZA PERFEITA +300", bx, by - cell, true));
        // anel dourado de estrelas CERCANDO o tabuleiro — elipse que CABE na tela:
        // rx = boardSize/2 + folga; ry idem (board centro y = boardTop+4cell)
        float cxb = boardLeft + 4 * cell, cyb = boardTop + 4 * cell;
        float rx = 4 * cell * 0.97f;   // dentro: 360±338 → x 22..698
        float ry = 4 * cell * 0.99f;
        int gold = 0xFFFFF176;
        for (int i = 0; i < 24; i++) {
            float ang = (i / 24f) * (float) Math.PI * 2f;
            float px = cxb + (float) Math.cos(ang) * rx;
            float py = cyb + (float) Math.sin(ang) * ry;
            particles.emitStarAt(px, py, gold, 7f + (i % 3));
        }
        // congela o meio da explosão (as partículas ainda vivas no frame seguinte)
        for (int i = 0; i < 30; i++) particles.tick();
        invalidate();
    }

    // ------------------------------------------------------------ efeito
    private final java.util.List<Floater> floaters = new java.util.ArrayList<>();

    private static final class Floater {
        final String text; final float x, y; final boolean big; final long t0;
        Floater(String text, float x, float y, boolean big) {
            this.text = text; this.x = x; this.y = y; this.big = big;
            this.t0 = System.currentTimeMillis();
        }
    }
}
