/*
 * Aggiunta al generatore ad autocitazione di Timm e Schinner
 * (github.com/TorstenTimm/SelfCitationTextgenerator, Copyright (c) 2019 Torsten Timm,
 * licenza MIT: il testo della licenza e' nel file LICENSE di quel repository).
 *
 * Due regole per un vocabolario piu' vario, entrambe eseguibili a mano:
 * - doppio ritocco: con probabilita' varieta.doppio (0-100) la copia ritoccata si
 *   ritocca una seconda volta;
 * - copia da lontano: con probabilita' varieta.lontano (0-100) la parola da copiare si
 *   prende da una riga qualsiasi delle pagine gia' finite, invece che dalla pagina
 *   in corso.
 * Le probabilita' si passano con -Dvarieta.doppio=... e -Dvarieta.lontano=...; a zero
 * (o assenti) le regole non ci sono e non consumano numeri casuali: il generatore
 * resta quello originale.
 */
package de.voynich.text.sourcechooser;

import de.voynich.text.GlyphGroup;
import de.voynich.text.util.random.I_RandomNumberGenerator;

import java.util.ArrayList;
import java.util.List;

public class Varieta {

    private static final int DOPPIO = Integer.parseInt(System.getProperty("varieta.doppio", "0"));
    private static final int LONTANO = Integer.parseInt(System.getProperty("varieta.lontano", "0"));

    /** Vero se la copia va ritoccata una seconda volta. */
    public static boolean doppio(I_RandomNumberGenerator caso) {
        return DOPPIO > 0 && caso.rand(100) < DOPPIO;
    }

    /** Una parola (con la seguente, come fa il generatore) presa dalle pagine gia'
     *  finite, oppure null se la regola non scatta. */
    public static List<GlyphGroup> daLontano(List<List<GlyphGroup>> righe, int righeNellaPagina,
                                             I_RandomNumberGenerator caso) {
        if (LONTANO <= 0 || caso.rand(100) >= LONTANO) {
            return null;
        }
        int finite = righe.size() - righeNellaPagina;
        if (finite <= 0) {
            return null;
        }
        List<GlyphGroup> riga = righe.get(caso.rand(finite));
        if (riga.isEmpty()) {
            return null;
        }
        int i = caso.rand(riga.size());
        List<GlyphGroup> ret = new ArrayList<>();
        ret.add(riga.get(i));
        ret.add(i + 1 < riga.size() ? riga.get(i + 1) : riga.get(i));
        ChooserHelper.removeInitialGallow(ret);
        return ret;
    }
}
