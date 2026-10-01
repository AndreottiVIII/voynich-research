/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * Filtro di forma (esperimento 68): una parola candidata si accetta con probabilita'
 * min(1, (r_inizio * r_fine)^eta / M). Le r vengono da un file (-Dforma.file=..., righe
 * "i<TAB>segno<TAB>r" e "f<TAB>segno<TAB>r"); eta da -Dforma.eta; M e' calcolato sul file.
 * Generatore casuale separato (-Dforma.seme): con eta 0 (o senza file) il generatore e'
 * identico all'originale.
 */
package de.voynich.text;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Forma {

    private static boolean caricato = false;
    private static double eta = 0.0, massimo = 1.0;
    private static final Map<String, Double> inizio = new HashMap<>(), fine = new HashMap<>();
    private static Random rnd = null;

    private static synchronized void carica() {
        if (caricato) {
            return;
        }
        caricato = true;
        eta = Double.parseDouble(System.getProperty("forma.eta", "0"));
        String file = System.getProperty("forma.file");
        if (file == null || eta <= 0.0) {
            eta = 0.0;
            return;
        }
        rnd = new Random(Long.parseLong(System.getProperty("forma.seme", "68")));
        try {
            for (String riga : Files.readAllLines(Paths.get(file), StandardCharsets.UTF_8)) {
                String[] c = riga.split("\t");
                if (c.length == 3) {
                    (c[0].equals("i") ? inizio : fine).put(c[1], Double.parseDouble(c[2]));
                }
            }
        } catch (Exception e) {
            throw new IllegalStateException("tabella della forma illeggibile: " + file, e);
        }
        double mi = inizio.values().stream().mapToDouble(Double::doubleValue).max().orElse(1.0);
        double mf = fine.values().stream().mapToDouble(Double::doubleValue).max().orElse(1.0);
        massimo = Math.pow(mi * mf, eta);
    }

    public static boolean attiva() {
        carica();
        return eta > 0.0;
    }

    /** Vero se la parola passa il filtro. */
    public static boolean accetta(String parola) {
        if (!attiva() || parola.isEmpty()) {
            return true;
        }
        double ri = inizio.getOrDefault(Giunture.primo(parola), 0.2);
        double rf = fine.getOrDefault(Giunture.ultimo(parola), 0.2);
        return rnd.nextDouble() < Math.min(1.0, Math.pow(ri * rf, eta) / massimo);
    }
}
