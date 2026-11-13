package com.blocolivre.game;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Sistema de partículas do Bloco Livre — faíscas de limpeza, confete de
 * combo e a explosão de estrelas da LIMPEZA PERFEITA. Física simples e
 * determinística o suficiente para animar a 60fps sem alocação por frame.
 */
final class ParticleSystem {

    private static final int CAP = 220;
    private final float[] x = new float[CAP];
    private final float[] y = new float[CAP];
    private final float[] vx = new float[CAP];
    private final float[] vy = new float[CAP];
    private final float[] life = new float[CAP];      // 1 → 0
    private final float[] decay = new float[CAP];
    private final float[] size = new float[CAP];
    private final int[] color = new int[CAP];
    private final int[] kind = new int[CAP];          // 0 faísca · 1 confete · 2 estrela · 3 anel
    private final float[] rot = new float[CAP];
    private final float[] vrot = new float[CAP];
    private int n = 0;

    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF scratch = new RectF();
    private final Random rng = new Random();

    boolean busy() { return n > 0; }

    void clear() { n = 0; }

    /** Faíscas radiais no ponto (limpeza de linha/coluna). */
    void burstSpark(float cx, float cy, int color, int count) {
        for (int i = 0; i < count && n < CAP; i++) {
            float ang = rng.nextFloat() * (float) Math.PI * 2f;
            float spd = (0.45f + rng.nextFloat() * 0.75f) * 34f;
            emit(cx, cy, (float) Math.cos(ang) * spd, (float) Math.sin(ang) * spd,
                    0.7f + rng.nextFloat() * 0.5f, 2.5f + rng.nextFloat() * 3.5f, color, 0);
        }
    }

    /** Chuva de confete (combos grandes / celebração). */
    void confettiRain(float width, int[] palette, int count) {
        for (int i = 0; i < count && n < CAP; i++) {
            emit(rng.nextFloat() * width, -12f - rng.nextFloat() * 60f,
                    (rng.nextFloat() - 0.5f) * 24f, 60f + rng.nextFloat() * 90f,
                    1.6f + rng.nextFloat() * 1.2f, 4f + rng.nextFloat() * 4f,
                    palette[1 + rng.nextInt(palette.length - 1)], 1);
        }
    }

    /** Confete restrito à ZONA DO TABULEIRO (nunca sobre o HUD/wordmark). */
    void confettiRainBoard(float width, float yTop, float yBottom, int[] palette, int count) {
        for (int i = 0; i < count && n < CAP; i++) {
            emit(rng.nextFloat() * width, yTop + rng.nextFloat() * (yBottom - yTop),
                    (rng.nextFloat() - 0.5f) * 26f, 34f + rng.nextFloat() * 70f,   // vy SEMPRE > 0: nunca invade o HUD
                    1.7f + rng.nextFloat() * 1.1f, 5f + rng.nextFloat() * 5f,
                    palette[1 + rng.nextInt(palette.length - 1)], 1);
        }
    }

    /** Anel de estrelas expandindo do centro (LIMPEZA PERFEITA). */
    void starRing(float cx, float cy, float r, int count, int color) {
        for (int i = 0; i < count && n < CAP; i++) {
            float ang = (i / (float) count) * (float) Math.PI * 2f;
            float px = cx + (float) Math.cos(ang) * r;
            float py = cy + (float) Math.sin(ang) * r;
            float spd = 46f + rng.nextFloat() * 26f;
            emit(px, py, (float) Math.cos(ang) * spd, (float) Math.sin(ang) * spd,
                    1.1f + rng.nextFloat() * 0.6f, 5f + rng.nextFloat() * 4f, color, 2);
        }
    }

    /** Anel fino em expansão (realce da limpeza dupla). */
    void ring(float cx, float cy, int color) {
        if (n < CAP) emit(cx, cy, 0, 0, 0.5f, 10f, color, 3);
    }

    /** Estrela quase-estática na posição (anel de coroação do tabuleiro). */
    void emitStarAt(float px, float py, int color, float size) {
        if (n < CAP) emit(px, py, 0, 0, 2.6f, size, color, 2);   // vida longa, sem vel.
    }

    private void emit(float px, float py, float pvx, float pvy,
                      float plife, float psize, int pcolor, int pkind) {
        x[n] = px; y[n] = py; vx[n] = pvx; vy[n] = pvy;
        life[n] = 1f; decay[n] = 1f / (plife * 60f);
        size[n] = psize; color[n] = pcolor; kind[n] = pkind;
        rot[n] = rng.nextFloat() * (float) Math.PI;
        vrot[n] = (rng.nextFloat() - 0.5f) * 6f;
        n++;
    }

    /** Avança 1 frame (dt em frações de segundo ~1/60). */
    void tick() {
        for (int i = 0; i < n; i++) {
            x[i] += vx[i] / 60f;
            y[i] += vy[i] / 60f;
            vy[i] += 120f / 60f;                      // gravidade
            if (kind[i] == 1) vx[i] *= 0.985f;        // arrasto do confete
            rot[i] += vrot[i] / 60f;
            life[i] -= decay[i];
            if (life[i] <= 0) {                       // remove trocando com o último
                n--;
                x[i] = x[n]; y[i] = y[n]; vx[i] = vx[n]; vy[i] = vy[n];
                life[i] = life[n]; decay[i] = decay[n]; size[i] = size[n];
                color[i] = color[n]; kind[i] = kind[n]; rot[i] = rot[n]; vrot[i] = vrot[n];
                i--;
            }
        }
    }

    void draw(Canvas cv) {
        for (int i = 0; i < n; i++) {
            float lf = life[i];
            int a = (int) (255 * Math.min(1f, lf * 1.6f));
            paint.setColor((color[i] & 0x00FFFFFF) | (a << 24));
            float s = size[i] * (0.5f + 0.5f * lf);
            switch (kind[i]) {
                case 0: {                              // faísca: traço na direção do movimento
                    float len = s * 2.2f;
                    float dx = vx[i], dy = vy[i];
                    float m = (float) Math.sqrt(dx * dx + dy * dy) + 0.001f;
                    dx /= m; dy /= m;
                    paint.setStrokeWidth(Math.max(1.5f, s * 0.5f));
                    paint.setStyle(Paint.Style.STROKE);
                    cv.drawLine(x[i], y[i], x[i] + dx * len, y[i] + dy * len, paint);
                    paint.setStyle(Paint.Style.FILL);
                    break;
                }
                case 1: {                              // confete: retângulo girando
                    cv.save();
                    cv.translate(x[i], y[i]);
                    cv.rotate(rot[i] * 57.2958f);
                    scratch.set(-s, -s * 0.55f, s, s * 0.55f);
                    cv.drawRect(scratch, paint);
                    cv.restore();
                    break;
                }
                case 2: {                              // estrela de 4 pontas
                    cv.save();
                    cv.translate(x[i], y[i]);
                    cv.rotate(rot[i] * 57.2958f);
                    float r1 = s, r2 = s * 0.38f;
                    android.graphics.Path path = Skins.scratchPath();
                    path.reset();
                    for (int k = 0; k < 8; k++) {
                        float ang = k * (float) Math.PI / 4f;
                        float rr = (k % 2 == 0) ? r1 : r2;
                        float px = (float) Math.cos(ang) * rr;
                        float py = (float) Math.sin(ang) * rr;
                        if (k == 0) path.moveTo(px, py); else path.lineTo(px, py);
                    }
                    path.close();
                    cv.drawPath(path, paint);
                    cv.restore();
                    break;
                }
                case 3: {                              // anel em expansão
                    float pr = (1f - lf) * 90f + s;
                    paint.setStyle(Paint.Style.STROKE);
                    paint.setStrokeWidth(3f + 5f * lf);
                    cv.drawCircle(x[i], y[i], pr, paint);
                    paint.setStyle(Paint.Style.FILL);
                    break;
                }
            }
        }
    }

    /** Fábrica estática dispensável (mantida por clareza de chamadas antigas). */
    static ParticleSystem create() { return new ParticleSystem(); }

    @SuppressWarnings("unused")
    private static void unused() { List<int[]> l = new ArrayList<>(); }
}
