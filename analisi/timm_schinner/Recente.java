/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * Recenza delle fonti (esperimento 50): con -Drecente.paragrafi=K la riga iniziale di
 * paragrafo da copiare si sceglie fra le ultime K invece che fra tutte. Cambia solo
 * l'intervallo del numero casuale, non il numero delle estrazioni: con K = 0 (o senza la
 * proprieta') il generatore e' identico all'originale.
 */
package de.voynich.text;

public class Recente {

    private static Integer limite = null;

    /** Quante delle n righe candidate si possono usare (le ultime). */
    public static int quante(int n) {
        if (limite == null) {
            limite = Integer.parseInt(System.getProperty("recente.paragrafi", "0"));
        }
        if (limite <= 0 || limite >= n) {
            return n;
        }
        return limite;
    }
}
