/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * Composizione (esperimento 48): a ogni posto di parola nuovo, con probabilita'
 * -Dcomposizione.quota=q, la parola e' composta segno per segno con un modello a trigrammi
 * di segni dentro la parola: P = lambda * P_pagina + (1 - lambda) * P_globale, con
 * -Dcomposizione.pagina=lambda. P_globale dalle parole di -Dcomposizione.file (una per riga);
 * P_pagina dalle parole gia' scritte nella pagina corrente. Generatore casuale separato
 * (-Dcomposizione.seme): con quota 0 il generatore e' identico all'originale.
 */
package de.voynich.text;

import de.voynich.text.util.Config;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class Composizione {

    private static final String[] FUSI = {"cth", "ckh", "cph", "cfh", "ch", "sh"};
    private static final String INIZIO = "^", FINE = "$";
    private static final int MASSIMO = 12;

    private static boolean caricato = false;
    private static double quota = 0.0, lambda = 0.0;
    private static Random rnd = null;
    private static final Map<String, Map<String, Integer>> globale = new HashMap<>();
    private static Map<String, Map<String, Integer>> pagina = new HashMap<>();
    private static int ultimaRigaDellaPagina = -1;

    static List<String> segni(String parola) {
        List<String> out = new ArrayList<>();
        int i = 0;
        while (i < parola.length()) {
            String trovato = null;
            for (String f : FUSI) {
                if (parola.startsWith(f, i)) {
                    trovato = f;
                    break;
                }
            }
            if (trovato == null) {
                trovato = parola.substring(i, i + 1);
            }
            out.add(trovato);
            i += trovato.length();
        }
        return out;
    }

    private static void conta(Map<String, Map<String, Integer>> tabella, String parola) {
        List<String> s = new ArrayList<>();
        s.add(INIZIO);
        s.add(INIZIO);
        s.addAll(segni(parola));
        s.add(FINE);
        for (int i = 2; i < s.size(); i++) {
            String ctx = s.get(i - 2) + "\t" + s.get(i - 1);
            tabella.computeIfAbsent(ctx, k -> new HashMap<>()).merge(s.get(i), 1, Integer::sum);
        }
    }

    private static synchronized void carica() {
        if (caricato) {
            return;
        }
        caricato = true;
        quota = Double.parseDouble(System.getProperty("composizione.quota", "0"));
        lambda = Double.parseDouble(System.getProperty("composizione.pagina", "0"));
        String file = System.getProperty("composizione.file");
        if (file == null || quota <= 0.0) {
            quota = 0.0;
            return;
        }
        rnd = new Random(Long.parseLong(System.getProperty("composizione.seme", "48")));
        try {
            for (String riga : Files.readAllLines(Paths.get(file), StandardCharsets.UTF_8)) {
                if (!riga.trim().isEmpty()) {
                    conta(globale, riga.trim());
                }
            }
        } catch (Exception e) {
            throw new IllegalStateException("parole illeggibili: " + file, e);
        }
    }

    public static boolean attiva() {
        carica();
        return quota > 0.0;
    }

    public static boolean scegli() {
        return rnd.nextDouble() < quota;
    }

    /** Da chiamare per ogni parola scritta; linesInPage si azzera a ogni pagina nuova. */
    public static void ricorda(String parola, int linesInPage) {
        if (!attiva()) {
            return;
        }
        if (linesInPage < ultimaRigaDellaPagina) {
            pagina = new HashMap<>();
        }
        ultimaRigaDellaPagina = linesInPage;
        conta(pagina, parola);
    }

    private static String pesca(String ctx) {
        Map<String, Integer> g = globale.get(ctx);
        Map<String, Integer> p = pagina.get(ctx);
        if (g == null && p == null) {
            return FINE;
        }
        double tg = g == null ? 0 : g.values().stream().mapToInt(Integer::intValue).sum();
        double tp = p == null ? 0 : p.values().stream().mapToInt(Integer::intValue).sum();
        double l = (p == null) ? 0.0 : (g == null ? 1.0 : lambda);
        // estrazione dalla miscela: le chiavi in ordine fisso, per la ripetibilita'
        java.util.TreeSet<String> chiavi = new java.util.TreeSet<>();
        if (g != null) chiavi.addAll(g.keySet());
        if (p != null) chiavi.addAll(p.keySet());
        double x = rnd.nextDouble(), cum = 0.0;
        String ultimo = FINE;
        for (String k : chiavi) {
            double pg = g == null ? 0 : g.getOrDefault(k, 0) / tg;
            double pp = p == null ? 0 : p.getOrDefault(k, 0) / tp;
            cum += l * pp + (1 - l) * pg;
            ultimo = k;
            if (x < cum) {
                return k;
            }
        }
        return ultimo;
    }

    public static GlyphGroup componi(Config config) {
        for (int tentativo = 0; tentativo < 20; tentativo++) {
            String a = INIZIO, b = INIZIO;
            StringBuilder w = new StringBuilder();
            for (int i = 0; i < MASSIMO; i++) {
                String c = pesca(a + "\t" + b);
                if (c.equals(FINE)) {
                    break;
                }
                w.append(c);
                a = b;
                b = c;
            }
            if (w.length() == 0) {
                continue;
            }
            GlyphGroup g = new GlyphGroup(w.toString(), GlyphGroup.GENERATE_TYPE.INITIAL);
            if (config.canFollow.isValid(g)) {
                return g;
            }
        }
        return null;
    }
}
