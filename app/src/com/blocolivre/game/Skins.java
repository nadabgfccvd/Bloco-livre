package com.blocolivre.game;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;

/**
 * Catálogo de skins do Bloco Livre. Cada skin é uma família visual completa:
 * paleta dos 7 blocos, fundos, cores de HUD e o desenho do próprio bloco.
 * A troca acontece na LIMPEZA PERFEITA (tabuleiro todo vazio) — o jogo
 * "floresce" para a próxima skin como recompensa estética.
 *
 * Tudo desenhado com primitivas de Canvas (roundRect/path/circle/line),
 * sem bitmaps — escala perfeita em qualquer densidade.
 */
public final class Skins {

    public static final String[] NAMES = {"Clássico", "Neon", "Gema", "Pixel"};

    // ================================================== CLÁSSICO
    static final class Classic implements Skin {
        static final int[] C = {
                0, // índice 0 nunca usado (vazio)
                0xFF4FC3F7, 0xFFFFB74D, 0xFFBA68C8, 0xFF81C784,
                0xFFE57373, 0xFFFFD54F, 0xFF4DB6AC
        };
        public int[] palette() { return C; }
        public int bg() { return 0xFF0E1420; }
        public int boardBg() { return 0xFF18202E; }
        public int boardBorder() { return 0xFF2A3648; }
        public int cellEmpty() { return 0xFF32405A; }
        public int hudTitle() { return 0xFFF2F6FC; }
        public int hudSub() { return 0xFF8FA3BF; }
        public int hudAccent() { return 0xFFFFD54F; }
        public int footerBtn() { return 0xFF23304A; }

        public void block(Canvas cv, float l, float t, float s, int color, Paint[] p) {
            // sombra dura inferior (3D de brinquedo)
            p[0].setColor(dim(color, 0.52f));
            RectF r = scratch();
            r.set(l, t + s * 0.08f, l + s, t + s);
            cv.drawRoundRect(r, s * 0.22f, s * 0.22f, p[0]);
            // corpo
            p[0].setColor(color);
            r.set(l, t, l + s, t + s * 0.92f);
            cv.drawRoundRect(r, s * 0.22f, s * 0.22f, p[0]);
            // GRADIENTE LATERAL: luz vem de cima-esq (2 faixas esquerda mais clara)
            p[0].setColor(withAlpha(dim(color, -0.16f), 255));
            r.set(l + s * 0.04f, t + s * 0.04f, l + s * 0.30f, t + s * 0.88f);
            cv.drawRoundRect(r, s * 0.10f, s * 0.10f, p[0]);
            // brilho de topo
            p[0].setColor(0x8CFFFFFF);
            r.set(l + s * 0.10f, t + s * 0.07f, l + s * 0.90f, t + s * 0.34f);
            cv.drawRoundRect(r, s * 0.14f, s * 0.14f, p[0]);
            // rim light inferior (rebatimento do board)
            p[0].setColor(withAlpha(dim(color, -0.30f), 255));
            r.set(l + s * 0.06f, t + s * 0.80f, l + s * 0.94f, t + s * 0.92f);
            cv.drawRoundRect(r, s * 0.10f, s * 0.10f, p[0]);
        }
    }

    // ================================================== NEON
    static final class Neon implements Skin {
        static final int[] C = {
                0,
                0xFF00E5FF, 0xFFFF6D00, 0xFFD500F9, 0xFF00E676,
                0xFFFF1744, 0xFFFFEA00, 0xFF2979FF
        };
        public int[] palette() { return C; }
        public int bg() { return 0xFF0A0812; }
        public int boardBg() { return 0xFF120E1C; }
        public int boardBorder() { return 0xFF3F2E66; }
        public int cellEmpty() { return 0xFF2C2450; }
        public int hudTitle() { return 0xFFE8F4FF; }
        public int hudSub() { return 0xFF6E7BA8; }
        public int hudAccent() { return 0xFF00E5FF; }
        public int footerBtn() { return 0xFF231A3E; }

        public void block(Canvas cv, float l, float t, float s, int color, Paint[] p) {
            // glow: cópia maior translúcida (simula shadowLayer onde não há)
            p[0].setColor(withAlpha(color, 70));
            RectF r = scratch();
            r.set(l - s * 0.06f, t - s * 0.06f, l + s * 1.06f, t + s * 1.06f);
            cv.drawRoundRect(r, s * 0.30f, s * 0.30f, p[0]);
            // moldura neon
            p[1].setColor(color);
            p[1].setStyle(Paint.Style.STROKE);
            p[1].setStrokeWidth(Math.max(2f, s * 0.10f));
            r.set(l + s * 0.07f, t + s * 0.07f, l + s * 0.93f, t + s * 0.93f);
            cv.drawRoundRect(r, s * 0.22f, s * 0.22f, p[1]);
            p[1].setStyle(Paint.Style.FILL);
            // interior escuro
            p[0].setColor(0xE6141020);
            r.set(l + s * 0.16f, t + s * 0.16f, l + s * 0.84f, t + s * 0.84f);
            cv.drawRoundRect(r, s * 0.16f, s * 0.16f, p[0]);
            // núcleo brilhante pequeno
            p[0].setColor(bright(color, 0.45f));
            r.set(l + s * 0.34f, t + s * 0.34f, l + s * 0.66f, t + s * 0.66f);
            cv.drawRoundRect(r, s * 0.10f, s * 0.10f, p[0]);
        }
    }

    // ================================================== GEMA
    static final class Gem implements Skin {
        static final int[] C = {
                0,
                0xFF64C7FF, 0xFFFFB84D, 0xFFC889E8, 0xFF7FE0A4,
                0xFFEF8A8A, 0xFFFFE28A, 0xFF6AD9CF
        };
        public int[] palette() { return C; }
        public int bg() { return 0xFF151226; }
        public int boardBg() { return 0xFF1E1A36; }
        public int boardBorder() { return 0xFF453B70; }
        public int cellEmpty() { return 0xFF3A3268; }
        public int hudTitle() { return 0xFFF6F1FF; }
        public int hudSub() { return 0xFF9C92C9; }
        public int hudAccent() { return 0xFFFFE28A; }
        public int footerBtn() { return 0xFF3A2F63; }

        public void block(Canvas cv, float l, float t, float s, int color, Paint[] p) {
            // gema facetada: octógono cortado + 2 facetas triangulares
            Path path = scratchPath();
            path.reset();
            float k = s * 0.24f;
            path.moveTo(l + k, t);
            path.lineTo(l + s - k, t);
            path.lineTo(l + s, t + k);
            path.lineTo(l + s, t + s - k);
            path.lineTo(l + s - k, t + s);
            path.lineTo(l + k, t + s);
            path.lineTo(l, t + s - k);
            path.lineTo(l, t + k);
            path.close();
            p[0].setColor(color);
            cv.drawPath(path, p[0]);
            // faceta superior (mais clara)
            path.reset();
            path.moveTo(l + k, t);
            path.lineTo(l + s - k, t);
            path.lineTo(l + s * 0.62f, t + s * 0.46f);
            path.lineTo(l + s * 0.38f, t + s * 0.46f);
            path.close();
            p[0].setColor(bright(color, 0.30f));
            cv.drawPath(path, p[0]);
            // faceta inferior (mais escura)
            path.reset();
            path.moveTo(l + k, t + s);
            path.lineTo(l + s - k, t + s);
            path.lineTo(l + s * 0.62f, t + s * 0.52f);
            path.lineTo(l + s * 0.38f, t + s * 0.52f);
            path.close();
            p[0].setColor(dim(color, 0.30f));
            cv.drawPath(path, p[0]);
            // brilho especular pequeno
            p[0].setColor(0x99FFFFFF);
            cv.drawCircle(l + s * 0.30f, t + s * 0.26f, s * 0.08f, p[0]);
        }
    }

    // ================================================== PIXEL
    static final class Pixel implements Skin {
        static final int[] C = {
                0,
                0xFF58A6FF, 0xFFF0883E, 0xFFBC8CFF, 0xFF7EE787,
                0xFFFF7B72, 0xFFE3B341, 0xFF56D4DD
        };
        // células vazias CINZAS neutras (nunca na família de matiz dos blocos)
        public int[] palette() { return C; }
        public int bg() { return 0xFF0D0D10; }
        public int boardBg() { return 0xFF17171B; }
        public int boardBorder() { return 0xFF2C2C34; }
        public int cellEmpty() { return 0xFF4A4E58; }        // cinza de leitura
        public int hudTitle() { return 0xFFF0F6FC; }
        public int hudSub() { return 0xFF8B949E; }
        public int hudAccent() { return 0xFFE3B341; }
        public int footerBtn() { return 0xFF26262E; }

        public void block(Canvas cv, float l, float t, float s, int color, Paint[] p) {
            // pixel-art DE VERDADE: paint sem AA, cantos retos, degraus nas diagonais
            Paint px = pixelPaint();
            // moldura escura de 1 "pixel"
            px.setColor(dim(color, 0.45f));
            cv.drawRect(l, t, l + s, t + s, px);
            float b = Math.max(2f, s * 0.10f);
            px.setColor(color);
            cv.drawRect(l + b, t + b, l + s - b, t + s - b, px);
            // rampa dura de 2 tons — metade mais clara, SEM gradiente
            float mid = l + b + (s - 2 * b) / 2f;
            px.setColor(bright(color, 0.14f));
            cv.drawRect(l + b, t + b, mid, t + s - b, px);
            // pixel de brilho 8-bit no canto sup-esq (retângulo duro)
            float pw = Math.max(2f, s * 0.16f);
            px.setColor(0xCCFFFFFF);
            cv.drawRect(l + b, t + b, l + b + pw, t + b + pw, px);
            // pixel de sombra no canto inf-dir
            px.setColor(0x55000000);
            cv.drawRect(l + s - b - pw, t + s - b - pw, l + s - b, t + s - b, px);
        }
    }

    // paint SEM anti-alias exclusivo da skin Pixel (bordas duras)
    private static final Paint PIXEL_PAINT = new Paint();
    static Paint pixelPaint() { PIXEL_PAINT.setAntiAlias(false); return PIXEL_PAINT; }

    // ================================================== infra
    public interface Skin {
        int[] palette();
        int bg();
        int boardBg();
        int boardBorder();
        int cellEmpty();
        int hudTitle();
        int hudSub();
        int hudAccent();
        int footerBtn();
        void block(Canvas cv, float l, float t, float s, int color, Paint[] p);
    }

    public static final Skin[] ALL = { new Classic(), new Neon(), new Gem(), new Pixel() };

    public static Skin byIndex(int i) { return ALL[((i % ALL.length) + ALL.length) % ALL.length]; }
    public static int count() { return ALL.length; }

    // ---- utilidades de cor (int ARGB puro, sem dependências)
    static int withAlpha(int color, int alpha) {
        return (color & 0x00FFFFFF) | (alpha << 24);
    }
    static int dim(int color, float f) {
        int r = (color >> 16) & 0xFF, g = (color >> 8) & 0xFF, b = color & 0xFF;
        return 0xFF000000 | ((int) (r * (1 - f)) << 16) | ((int) (g * (1 - f)) << 8) | (int) (b * (1 - f));
    }
    static int bright(int color, float f) {
        int r = (color >> 16) & 0xFF, g = (color >> 8) & 0xFF, b = color & 0xFF;
        return 0xFF000000 | ((int) (r + (255 - r) * f) << 16) | ((int) (g + (255 - g) * f) << 8) | (int) (b + (255 - b) * f);
    }

    // ---- scratch compartilhado (evita alocação no onDraw)
    private static final RectF SCRATCH = new RectF();
    private static final Path SCRATCH_PATH = new Path();
    static RectF scratch() { return SCRATCH; }
    static Path scratchPath() { return SCRATCH_PATH; }

    private Skins() { }
}
