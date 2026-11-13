package com.blocolivre.game;

import android.content.Context;

import com.blocolivre.core.GameModel;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * Persistência 100% local (armazenamento interno do app): partida em curso,
 * recorde e estatísticas. Nenhuma rede, nenhuma permissão, nenhum rastreamento.
 */
public final class SaveStore {
    private final File file;
    private final File ctxFilesDir;
    private long lastBest;

    public SaveStore(Context ctx) {
        this.ctxFilesDir = ctx.getFilesDir();
        this.file = new File(ctxFilesDir, "save.dat");
        this.lastBest = 0;
    }

    public GameModel load() {
        GameModel g = null;
        if (file.exists()) {
            try (FileInputStream fis = new FileInputStream(file)) {
                byte[] buf = new byte[(int) file.length()];
                int read = fis.read(buf);
                if (read > 0) {
                    g = GameModel.deserialize(new String(buf, 0, read, StandardCharsets.UTF_8));
                }
            } catch (IOException ignored) { }
        }
        if (g == null) {
            g = new GameModel();
            g.setBest(lastBest);
        }
        lastBest = g.best();
        return g;
    }

    public void save(GameModel g) {
        if (g == null) return;
        lastBest = Math.max(lastBest, g.best());
        try (FileOutputStream fos = new FileOutputStream(file)) {
            fos.write(g.serialize().getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) { }
    }

    // ------------------------------------------------------------ skin ativa
    // Arquivo separado e trivial ("2" → skin índice 2). Legado ausente = 0.
    private File skinFile() { return new File(ctxFilesDir, "skin.cfg"); }

    public int loadSkin() {
        try (FileInputStream fis = new FileInputStream(skinFile())) {
            byte[] buf = new byte[8];
            int read = fis.read(buf);
            if (read > 0) {
                int v = Integer.parseInt(new String(buf, 0, read, StandardCharsets.UTF_8).trim());
                if (v >= 0 && v < Skins.count()) return v;
            }
        } catch (Exception ignored) { }
        return 0;
    }

    public void saveSkin(int i) {
        try (FileOutputStream fos = new FileOutputStream(skinFile())) {
            fos.write(String.valueOf(i).getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) { }
    }
}
