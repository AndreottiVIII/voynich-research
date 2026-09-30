/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * La regola delle giunture: quando nella riga c'e' gia' una parola, la parola nuova
 * si accetta con probabilita' min(1, R^forza), dove R dice quanto nel Voynich il
 * primo segno della parola nuova segue piu' (R > 1) o meno (R < 1) del normale
 * l'ultimo segno della parola precedente. R viene da un file (una riga per coppia:
 * ultimo segno, primo segno, R), indicato con -Dgiunture.file=...; la forza con
 * -Dgiunture.forza=... Con forza 0 (o senza file) la regola non c'e' e il
 * generatore e' identico all'originale.
 */
package de.voynich.text;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class Giunture {

    private static final String[] FUSI = {"cth", "ckh", "cph", "cfh", "ch", "sh"};
    private static Map<String, Double> tabella = null;
    private static double forza = 0.0;

    private static synchronized void carica() {
        if (tabella != null) {
            return;
        }
        tabella = new HashMap<>();
        String file = System.getProperty("giunture.file");
        forza = Double.parseDouble(System.getProperty("giunture.forza", "0"));
        if (file == null || forza == 0.0) {
            forza = 0.0;
            return;
        }
        try (BufferedReader r = new BufferedReader(new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            String riga;
            while ((riga = r.readLine()) != null) {
                String[] c = riga.split("\t");
                if (c.length == 3) {
                    tabella.put(c[0] + "\t" + c[1], Double.parseDouble(c[2]));
                }
            }
        } catch (Exception e) {
            throw new IllegalStateException("tabella delle giunture illeggibile: " + file, e);
        }
    }

    public static boolean attiva() {
        carica();
        return forza > 0.0;
    }

    static String primo(String parola) {
        for (String f : FUSI) {
            if (parola.startsWith(f)) {
                return f;
            }
        }
        return parola.substring(0, 1);
    }

    static String ultimo(String parola) {
        for (String f : FUSI) {
            if (parola.endsWith(f)) {
                return f;
            }
        }
        return parola.substring(parola.length() - 1);
    }

    /** Probabilita' di accettare la parola dopo la precedente. */
    public static double probabilita(String precedente, String nuova) {
        carica();
        if (precedente.isEmpty() || nuova.isEmpty()) {
            return 1.0;
        }
        Double r = tabella.get(ultimo(precedente) + "\t" + primo(nuova));
        if (r == null) {
            r = 0.1;   // coppia mai vista nel Voynich
        }
        return Math.min(1.0, Math.pow(r, forza));
    }
}
