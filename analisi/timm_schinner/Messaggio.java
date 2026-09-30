/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * Un messaggio diluito (esperimento 44): a ogni posto di parola nuovo, con probabilita'
 * -Dmessaggio.quota=m, la parola scritta e' la successiva di un messaggio (un file con una
 * parola per riga, -Dmessaggio.file=...). Il sorteggio usa un generatore casuale separato
 * (-Dmessaggio.seme=...), cosi' con quota 0 il generatore e' identico all'originale.
 * Alla fine scrive in generate/messaggio_usato.txt quante parole del messaggio sono entrate.
 */
package de.voynich.text;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Messaggio {

    private static List<String> parole = null;
    private static double quota = 0.0;
    private static Random rnd = null;
    private static int posizione = 0;

    private static synchronized void carica() {
        if (parole != null) {
            return;
        }
        parole = new ArrayList<>();
        quota = Double.parseDouble(System.getProperty("messaggio.quota", "0"));
        String file = System.getProperty("messaggio.file");
        if (file == null || quota <= 0.0) {
            quota = 0.0;
            return;
        }
        rnd = new Random(Long.parseLong(System.getProperty("messaggio.seme", "44")));
        try {
            for (String riga : Files.readAllLines(Paths.get(file), StandardCharsets.UTF_8)) {
                if (!riga.trim().isEmpty()) {
                    parole.add(riga.trim());
                }
            }
        } catch (Exception e) {
            throw new IllegalStateException("messaggio illeggibile: " + file, e);
        }
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try (PrintWriter w = new PrintWriter("generate/messaggio_usato.txt", "UTF-8")) {
                w.println(posizione);
            } catch (Exception e) {
                // solo statistica: non deve far fallire la generazione
            }
        }));
    }

    public static boolean attivo() {
        carica();
        return quota > 0.0;
    }

    /** Questo posto di parola va al messaggio? */
    public static boolean scegli() {
        return rnd.nextDouble() < quota;
    }

    public static GlyphGroup prossima() {
        return new GlyphGroup(parole.get(posizione % parole.size()), GlyphGroup.GENERATE_TYPE.INITIAL);
    }

    public static void consumata() {
        posizione++;
    }
}
