package com.blocolivre.core;

/** Peças do Bloco Livre: 33 formas clássicas (linhas, quadrados, L, T, S/Z). */
public final class Piece {
    public static final Piece[] SHAPES = build();

    public final int id;
    public final int[] cells;   // pares (dx,dy) achatados
    public final int w, h, n;
    public final int color;     // 1..7 (estético)

    private Piece(int id, int[] cells, int color) {
        this.id = id; this.cells = cells; this.color = color;
        int maxx = 0, maxy = 0;
        for (int k = 0; k < cells.length; k += 2) {
            if (cells[k] > maxx) maxx = cells[k];
            if (cells[k + 1] > maxy) maxy = cells[k + 1];
        }
        this.w = maxx + 1; this.h = maxy + 1; this.n = cells.length / 2;
    }

    public static Piece byId(int id) {
        if (id < 0 || id >= SHAPES.length) throw new IllegalArgumentException("piece id " + id);
        return SHAPES[id];
    }

    private static Piece[] build() {
        java.util.List<Piece> list = new java.util.ArrayList<>();
        java.util.List<int[]> raw = new java.util.ArrayList<>();
        // --- linhas e singleton
        raw.add(c(0,0));
        raw.add(c(0,0, 1,0)); raw.add(c(0,0, 1,0, 2,0)); raw.add(c(0,0, 1,0, 2,0, 3,0)); raw.add(c(0,0, 1,0, 2,0, 3,0, 4,0));
        raw.add(c(0,0, 0,1)); raw.add(c(0,0, 0,1, 0,2)); raw.add(c(0,0, 0,1, 0,2, 0,3)); raw.add(c(0,0, 0,1, 0,2, 0,3, 0,4));
        // --- quadrados / retângulos
        raw.add(c(0,0, 1,0, 0,1, 1,1));
        raw.add(grid3x3());
        raw.add(c(0,0, 1,0, 2,0, 0,1, 1,1, 2,1));          // 2x3
        raw.add(c(0,0, 1,0, 0,1, 1,1, 0,2, 1,2));          // 3x2
        // --- cantoneira pequena (3 células), 4 rotações
        raw.add(c(0,0, 1,0, 0,1)); raw.add(c(0,0, 1,0, 1,1));
        raw.add(c(0,0, 0,1, 1,1)); raw.add(c(1,0, 0,1, 1,1));
        // --- L grande (5 células), 4 rotações
        int[][] bigL = {
            {0,0, 0,1, 0,2, 1,2, 2,2}, {0,0, 1,0, 2,0, 2,1, 2,2},
            {0,0, 1,0, 2,0, 0,1, 0,2}, {2,0, 2,1, 2,2, 0,2, 1,2}
        };
        for (int[] s : bigL) raw.add(s);
        // --- T (4 células), 4 rotações
        int[][] t = {
            {0,0, 1,0, 2,0, 1,1}, {1,0, 0,1, 1,1, 1,2},
            {1,0, 0,1, 1,1, 2,1}, {0,0, 0,1, 0,2, 1,1}
        };
        for (int[] s : t) raw.add(s);
        // --- S/Z (4 células)
        raw.add(c(1,0, 2,0, 0,1, 1,1)); raw.add(c(0,0, 1,0, 1,1, 2,1));
        raw.add(c(0,0, 0,1, 1,1, 1,2)); raw.add(c(1,0, 1,1, 0,1, 0,2)); // S/Z verticais
        // --- L tetromino (4 células), 4 rotações
        int[][] l4 = {
            {0,0, 0,1, 0,2, 1,2}, {0,0, 1,0, 2,0, 0,1},
            {0,0, 1,0, 1,1, 1,2}, {2,0, 0,1, 1,1, 2,1}
        };
        for (int[] s : l4) raw.add(s);
        for (int i = 0; i < raw.size(); i++) list.add(new Piece(i, raw.get(i), 1 + (i % 7)));
        return list.toArray(new Piece[0]);
    }

    private static int[] c(int... xy) { return xy; }
    private static int[] grid3x3() {
        int[] a = new int[18];
        int k = 0;
        for (int y = 0; y < 3; y++) for (int x = 0; x < 3; x++) { a[k++] = x; a[k++] = y; }
        return a;
    }
}
