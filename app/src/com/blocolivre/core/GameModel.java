package com.blocolivre.core;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Núcleo puro do Bloco Livre — zero dependência de Android (roda em JVM).
 *
 * Antídoto ao "GCT" acusado no vídeo: o sorteio é UNIFORME e INDEPENDENTE.
 * Nenhuma linha daqui olha recorde, sequência de derrotas, país, dispositivo
 * ou "valor do jogador". O fim do jogo é consequência do tabuleiro e da sorte
 * — nunca de uma regra que arma mãos insolúveis quando você supera o recorde.
 * A honestidade é verificável: os testes rodam exatamente este arquivo.
 */
public final class GameModel {
    public static final int W = 8, H = 8;
    public static final int TRAY = 3;

    private final int[] grid = new int[W * H];     // 0 = vazio, 1..7 = cor
    private final int[] tray = new int[TRAY];      // id da peça ou -1
    private final Piece[] trayPieces = new Piece[TRAY];

    private long score, best, combo, comboBest;
    private long piecesPlaced, linesCleared, gamesPlayed, perfectClears;
    private boolean over;
    private final long seed;
    private final Random rng;

    // auditoria de honestidade do sorteio
    private long draws;
    private final long[] pieceCount = new long[Piece.SHAPES.length];

    public GameModel() { this(System.nanoTime() ^ System.identityHashCode(new Object())); }
    public GameModel(long seed) {
        this.seed = seed;
        this.rng = new Random(seed);
        java.util.Arrays.fill(tray, -1);
        refillTray();
    }

    // ------------------------------------------------------------ geometria
    public boolean canPlace(Piece p, int ox, int oy) {
        for (int k = 0; k < p.cells.length; k += 2) {
            int x = ox + p.cells[k], y = oy + p.cells[k + 1];
            if (x < 0 || x >= W || y < 0 || y >= H) return false;
            if (grid[y * W + x] != 0) return false;
        }
        return true;
    }

    /** Existe posição válida para alguma peça da bandeja? (fim honesto) */
    public boolean anyMoveLeft() {
        for (int t = 0; t < TRAY; t++) {
            Piece p = trayPiece(t);
            if (p == null) continue;
            for (int y = 0; y < H; y++)
                for (int x = 0; x < W; x++)
                    if (canPlace(p, x, y)) return true;
        }
        return false;
    }

    // ------------------------------------------------------------ bandeja
    private Piece drawPiece() {
        int idx = rng.nextInt(Piece.SHAPES.length);   // uniforme, sem ajuste de pesos
        draws++;
        pieceCount[idx]++;
        return Piece.byId(idx);
    }

    private void refillTray() {
        for (int i = 0; i < TRAY; i++)
            if (tray[i] == -1) { trayPieces[i] = drawPiece(); tray[i] = trayPieces[i].id; }
            else trayPieces[i] = Piece.byId(tray[i]);
    }

    public Piece trayPiece(int i) {
        if (i < 0 || i >= TRAY) return null;
        if (trayPieces[i] == null && tray[i] >= 0) trayPieces[i] = Piece.byId(tray[i]);
        return trayPieces[i];
    }

    public boolean trayFull() {
        for (int i = 0; i < TRAY; i++) if (tray[i] == -1) return false;
        return true;
    }

    // ------------------------------------------------------------ colocação
    public static final class PlaceResult {
        public int placedColor, ox, oy;
        public boolean ok;
        public final List<int[]> cleared = new ArrayList<>();  // (x,y) limpos
        public int lines, cols;                                  // linhas/colunas completas
        public long gained;
        public long comboNow;
        public boolean trayEmpty;
        public boolean allClear;                                 // tabuleiro 100% vazio após limpar
    }

    /**
     * Pontuação estilo Block Blast, sem números mágicos ocultos:
     *  +1 por célula da peça · +10 por célula limpa · +15 por limpeza dupla
     *  numa só colocação (2 linhas = +30) · combo soma +2 por nível.
     */
    public PlaceResult place(int t, int ox, int oy) {
        PlaceResult r = new PlaceResult();
        if (over) return r;
        Piece p = trayPiece(t);
        if (p == null || !canPlace(p, ox, oy)) return r;
        r.ok = true; r.ox = ox; r.oy = oy; r.placedColor = p.color;
        for (int k = 0; k < p.cells.length; k += 2)
            grid[(oy + p.cells[k + 1]) * W + (ox + p.cells[k])] = p.color;
        piecesPlaced++;
        tray[t] = -1; trayPieces[t] = null;
        r.trayEmpty = trayFull() && tray[0] == -1 && tray[1] == -1 && tray[2] == -1;
        r.trayEmpty = (tray[0] == -1 && tray[1] == -1 && tray[2] == -1);

        long gained = p.n;                       // 1 por célula colocada
        List<int[]> cleared = clearFullLines();
        int cellsCleared = cleared.size();
        r.lines = lastLines; r.cols = lastCols;
        r.cleared.addAll(cleared);
        if (cellsCleared > 0) {
            linesCleared += r.lines + r.cols;
            combo++;
            comboBest = Math.max(comboBest, combo);
            gained += 10L * cellsCleared;
            int lc = r.lines + r.cols;
            if (lc >= 2) gained += 15L * lc * (lc - 1);   // bônus multi-linha
            if (combo > 1) gained += 2L * (combo - 1) * cellsCleared / 4;
        } else {
            combo = 0;
        }
        // LIMPEZA PERFEITA: tabuleiro todo vazio depois da limpeza —
        // bônus generoso e o gatilho da celebração/troca de skin na UI.
        if (cellsCleared > 0) {
            boolean empty = true;
            for (int v : grid) if (v != 0) { empty = false; break; }
            if (empty) { r.allClear = true; perfectClears++; gained += 300L; }
        }
        r.gained = gained; r.comboNow = combo;
        score += gained;
        if (score > best) best = score;
        if (r.trayEmpty) refillTray();
        if (!over && !anyMoveLeft()) { over = true; gamesPlayed++; }
        return r;
    }

    private List<int[]> clearFullLines() {
        List<int[]> cells = new ArrayList<>();
        lastLines = 0; lastCols = 0;
        for (int y = 0; y < H; y++) {
            boolean full = true;
            for (int x = 0; x < W; x++) if (grid[y * W + x] == 0) { full = false; break; }
            if (full) { for (int x = 0; x < W; x++) cells.add(new int[]{x, y}); lastLines++; }
        }
        for (int x = 0; x < W; x++) {
            boolean full = true;
            for (int y = 0; y < H; y++) if (grid[y * W + x] == 0) { full = false; break; }
            if (full) { for (int y = 0; y < H; y++) cells.add(new int[]{x, y}); lastCols++; }
        }
        for (int[] c : cells) grid[c[1] * W + c[0]] = 0;
        return cells;
    }

    private int lastLines, lastCols;

    // ------------------------------------------------------------ revive honesto
    /**
     * O "continue" SEM anúncio: troca a bandeja inteira por 3 peças novas,
     * desde que ao menos uma caiba no tabuleiro. Máx. 3 por partida
     * (contador mantido pela UI, salvo junto). Nunca resgata quem não
     * tem mais jogada nenhuma — o fim continua consequência do jogo.
     */
    public boolean swapTray() {
        if (over) return false;
        for (int attempt = 0; attempt < 200; attempt++) {
            Piece[] cand = { drawPiece(), drawPiece(), drawPiece() };
            for (Piece pc : cand) {
                outer:
                for (int y = 0; y < H; y++)
                    for (int x = 0; x < W; x++)
                        if (canPlace(pc, x, y)) {
                            for (int i = 0; i < TRAY; i++) { tray[i] = cand[i].id; trayPieces[i] = cand[i]; }
                            return true;
                        }
            }
        }
        return false;
    }

    public int reviveBudget = 3;
    public boolean revive() {
        if (!over || reviveBudget <= 0) return false;
        // sobre o tabuleiro congelado: troca a bandeja até achar peças que
        // caibam — se NENHUMA tripla sorteável couber, o jogo segue encerrado
        // (orçamento não gasto, pontuação intacta).
        boolean ok = swapTray();
        if (ok) { reviveBudget--; over = false; gamesPlayed--; }
        return ok;
    }

    // ------------------------------------------------------------ novo jogo
    public void resetNewGame() {
        java.util.Arrays.fill(grid, 0);
        score = 0; combo = 0; over = false; reviveBudget = 3;
        for (int i = 0; i < TRAY; i++) { tray[i] = -1; trayPieces[i] = null; }
        refillTray();
    }

    /** O tabuleiro está completamente vazio? (para UI: preview de limpeza perfeita) */
    public boolean boardEmpty() {
        for (int v : grid) if (v != 0) return false;
        return true;
    }

    /** Escrita direta de célula — SÓ para montagem de cenas de demo/fotografia. */
    public void setCellForDemo(int x, int y, int color) {
        if (x < 0 || x >= W || y < 0 || y >= H) return;
        grid[y * W + x] = Math.max(0, Math.min(7, color));
    }

    /** Força a bandeja da demo (SÓ fotografia de cenas). */
    public void forceTrayForDemo(int slot, int pieceId, int unused) {
        if (slot < 0 || slot >= TRAY) return;
        tray[slot] = pieceId;
        trayPieces[slot] = Piece.byId(pieceId);
    }

    // ------------------------------------------------------------ serialização
    // v1 = 12 campos + grade + bandeja (legado, ainda aceito)
    // v2 = idem + perfectClears (salvo por games jogados)
    public String serialize() {
        StringBuilder sb = new StringBuilder(240);
        sb.append("v2;").append(seed).append(';').append(score).append(';').append(best)
          .append(';').append(combo).append(';').append(comboBest)
          .append(';').append(piecesPlaced).append(';').append(linesCleared)
          .append(';').append(gamesPlayed).append(';').append(over ? 1 : 0)
          .append(';').append(draws).append(';').append(reviveBudget)
          .append(';').append(perfectClears);
        for (int v : grid) sb.append(';').append(v);
        for (int v : tray) sb.append(';').append(v);
        return sb.toString();
    }

    public static GameModel deserialize(String s) {
        try {
            String[] p = s.split(";", -1);
            boolean v2 = "v2".equals(p[0]);
            if (!v2 && !"v1".equals(p[0])) return null;
            if (p.length != (v2 ? 13 : 12) + 64 + 3) return null;
            GameModel g = new GameModel(Long.parseLong(p[1]));
            g.score = Long.parseLong(p[2]); g.best = Long.parseLong(p[3]);
            g.combo = Long.parseLong(p[4]); g.comboBest = Long.parseLong(p[5]);
            g.piecesPlaced = Long.parseLong(p[6]); g.linesCleared = Long.parseLong(p[7]);
            g.gamesPlayed = Long.parseLong(p[8]); g.over = "1".equals(p[9]);
            g.draws = Long.parseLong(p[10]); g.reviveBudget = Integer.parseInt(p[11]);
            if (v2) g.perfectClears = Long.parseLong(p[12]);
            for (int i = 0; i < W * H; i++) g.grid[i] = Integer.parseInt(p[(v2 ? 13 : 12) + i]);
            for (int i = 0; i < TRAY; i++) {
                g.tray[i] = Integer.parseInt(p[(v2 ? 13 : 12) + 64 + i]);
                g.trayPieces[i] = g.tray[i] >= 0 ? Piece.byId(g.tray[i]) : null;
            }
            return g;
        } catch (Exception e) {
            return null;
        }
    }

    // ------------------------------------------------------------ acesso
    public int cell(int x, int y) { return grid[y * W + x]; }
    public int[] trayIds() { return tray.clone(); }
    public long score() { return score; }
    public long best() { return best; }
    public long combo() { return combo; }
    public long comboBest() { return comboBest; }
    public long piecesPlaced() { return piecesPlaced; }
    public long linesCleared() { return linesCleared; }
    public long gamesPlayed() { return gamesPlayed; }
    public long perfectClears() { return perfectClears; }
    public boolean isOver() { return over; }
    public void setBest(long b) { best = b; }
    public long seed() { return seed; }
    public long draws() { return draws; }
    public long[] pieceStats() { return pieceCount.clone(); }

    /**
     * Demo de VM pura (executável via `rd vm exec` sem UI): joga uma partida
     * de bot gulosa com a seed dada e devolve "score;pecas;limpas" — prova de
     * que o motor roda idêntico em qualquer runtime Dalvik compatível.
     */
    public static String vmDemo(long seed) {
        GameModel g = new GameModel(seed);
        int guard = 0;
        while (!g.isOver() && guard++ < 2000) {
            boolean placed = false;
            for (int t = 0; t < TRAY && !placed; t++) {
                Piece p = g.trayPiece(t);
                if (p == null) continue;
                for (int y = H - 1; y >= 0 && !placed; y--)
                    for (int x = 0; x < W && !placed; x++)
                        if (g.canPlace(p, x, y)) { g.place(t, x, y); placed = true; }
            }
            if (!placed) { if (!g.swapTray()) break; }
        }
        return g.score() + ";" + g.piecesPlaced() + ";" + g.linesCleared();
    }
}
