package com.blocolivre.game;

import android.content.Context;

/**
 * Áudio e vibração 100% via REFLEXÃO — nenhum link estático de bytecode para
 * android.media.* / android.os.Vibrator: em runtimes que ainda não implementam
 * essas APIs (ex.: headless de teste), Class.forName falha DENTRO do guest e
 * o jogo segue mudo e normal. Em aparelho real, sons e vibração funcionam.
 */
public final class AudioCompat {

    private final Object soundPool;        // android.media.SoundPool (ou null)
    private final java.lang.reflect.Method playMethod;
    private final int[] ids = new int[5];  // 0=place 1=clear 2=combo 3=over 4=bad
    private final Object vib;              // android.os.Vibrator (ou null)
    private final java.lang.reflect.Method vibVibrate; // vibrate(long) deprecated-form fallback

    private AudioCompat(Object sp, java.lang.reflect.Method play, Object vib,
                        java.lang.reflect.Method vibVibrate) {
        this.soundPool = sp; this.playMethod = play;
        this.vib = vib; this.vibVibrate = vibVibrate;
    }

    public static AudioCompat create(Context ctx, int[] rawResIds) {
        Object sp = null;
        java.lang.reflect.Method play = null;
        try {
            Class<?> spc = Class.forName("android.media.SoundPool");
            Class<?> abc = Class.forName("android.media.AudioAttributes$Builder");
            Class<?> aac = Class.forName("android.media.AudioAttributes");
            Object attrs = abc.getDeclaredConstructor().newInstance();
            abc.getMethod("setUsage", int.class).invoke(attrs, 11 /*USAGE_GAME*/);
            abc.getMethod("setContentType", int.class).invoke(attrs, 2 /*CONTENT_TYPE_MUSIC*/);
            attrs = aac.cast(abc.getMethod("build").invoke(attrs));
            Class<?> spb = Class.forName("android.media.SoundPool$Builder");
            Object b = spb.getDeclaredConstructor().newInstance();
            spb.getMethod("setMaxStreams", int.class).invoke(b, 4);
            spb.getMethod("setAudioAttributes", aac).invoke(b, attrs);
            sp = spb.getMethod("build").invoke(b);
            Class<?> ctxCls = Context.class;
            java.lang.reflect.Method load = spc.getMethod("load", ctxCls, int.class, int.class);
            for (int i = 0; i < rawResIds.length && i < 5; i++)
                idsOf(sp, load, ctx, rawResIds, i);
            play = spc.getMethod("play", int.class, float.class, float.class,
                    int.class, int.class, float.class);
        } catch (Throwable ignored) { }

        Object vib = null;
        java.lang.reflect.Method vibLong = null;
        try {
            vib = ctx.getSystemService(Context.VIBRATOR_SERVICE);
            if (vib != null)
                vibLong = vib.getClass().getMethod("vibrate", long.class);
        } catch (Throwable ignored) { }

        AudioCompat a = new AudioCompat(sp, play, vib, vibLong);
        if (sp != null && play != null) {
            try {
                java.lang.reflect.Method load = sp.getClass()
                        .getMethod("load", Context.class, int.class, int.class);
                for (int i = 0; i < rawResIds.length && i < 5; i++)
                    a.ids[i] = (Integer) load.invoke(sp, ctx, rawResIds[i], 1);
            } catch (Throwable ignored) { }
        }
        return a;
    }

    private static void idsOf(Object sp, java.lang.reflect.Method load, Context ctx,
                              int[] rawResIds, int i) { /* bookkeeping estático vazio */ }

    /** id 0=place 1=clear 2=combo 3=over 4=bad */
    public void play(int id) {
        if (soundPool == null || playMethod == null) return;
        try {
            playMethod.invoke(soundPool, ids[id], 1f, 1f, 1, 0, 1f);
        } catch (Throwable ignored) { }
    }

    /** vibração curta; silenciosa onde não houver suporte */
    public void buzz(long ms) {
        if (vib == null) return;
        try {
            if (vibVibrate != null) vibVibrate.invoke(vib, ms);
        } catch (Throwable ignored) { }
    }

    public boolean hasAudio() { return soundPool != null && playMethod != null; }
    public boolean hasBuzz() { return vib != null; }
}
