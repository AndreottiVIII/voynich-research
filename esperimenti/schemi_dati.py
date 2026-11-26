# -*- coding: utf-8 -*-
"""IA44: i dati di struttura del manoscritto (pagine, fascicoli, mani, etichette dello zodiaco) e il testo SOLO a richiesta.

Due livelli, tenuti separati di proposito:
  * la LAYOUT (`layout_erbario`, `layout_zodiaco`): solo numeri (quante parole per pagina, fascicolo, mano, quante etichette per
    segno). E' quella che usano i controlli, che mettono sopra testi non Voynich. Nessuna parola.
  * il TESTO (`testo_erbario`, `testo_zodiaco`): le parole della trascrizione. Si chiama solo nella fase V (Voynich), che parte solo
    dopo che i controlli sono passati e che e' stata commessa la preregistrazione.
Le parole illeggibili (con ? o *) si scartano, come in tutto il repo. Trascrizioni: 'ZL' (Zandbergen-Landini) e 'IT' (Takahashi).
"""
import os
import sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import trascrizione as T  # noqa: E402

MIN_PAROLE_PAGINA = 20          # pagine con meno parole pulite non entrano (frammenti)

# I 12 fogli dello zodiaco in 10 segni (come e103 ed e214): Pesci f70v2, Ariete f70v1+f71r, Toro f71v+f72r1, Gemelli f72r2,
# Cancro f72r3, Leone f72v3, Vergine f72v2, Bilancia f72v1, Scorpione f73r, Sagittario f73v. Capricorno e Acquario mancano.
SEGNI = OrderedDict([
    ('Pesci', ('f70v2',)), ('Ariete', ('f70v1', 'f71r')), ('Toro', ('f71v', 'f72r1')), ('Gemelli', ('f72r2',)),
    ('Cancro', ('f72r3',)), ('Leone', ('f72v3',)), ('Vergine', ('f72v2',)), ('Bilancia', ('f72v1',)),
    ('Scorpione', ('f73r',)), ('Sagittario', ('f73v',))])
# posizione di ogni segno sulla ruota dello zodiaco tropicale (0 = Ariete ... 11 = Pesci)
RUOTA = OrderedDict([('Ariete', 0), ('Toro', 1), ('Gemelli', 2), ('Cancro', 3), ('Leone', 4), ('Vergine', 5), ('Bilancia', 6),
                     ('Scorpione', 7), ('Sagittario', 8), ('Capricorno', 9), ('Acquario', 10), ('Pesci', 11)])
ORDINE_SEGNI = tuple(SEGNI)


def _pagine(trascr):
    """OrderedDict pagina -> dict(sezione, lingua, mano, quire, par=[parole pulite dei paragrafi], et=[[parole] per riga di
    etichetta], altro=[parole di cerchi e raggi]). Le parole ci sono sempre qui: le funzioni sotto le tolgono per la layout."""
    out = OrderedDict()
    for r in T.leggi(trascr):
        d = out.setdefault(r.pagina, dict(sezione=r.sezione, lingua=r.lingua, mano=r.mano, quire=r.quire, par=[], et=[], altro=[]))
        ps = [w for w in r.parole if T.pulita(w)]
        t = r.tipo[0]
        if t == T.PARAGRAFO:
            d['par'].extend(ps)
        elif t == T.ETICHETTA:
            d['et'].append(ps)
        else:
            d['altro'].extend(ps)
    return out


def _erbario(trascr, con_testo):
    unita = OrderedDict((u, []) for u in ('A', 'B'))
    for nome, d in _pagine(trascr).items():
        if d['sezione'] != 'H' or d['lingua'] not in ('A', 'B') or len(d['par']) < MIN_PAROLE_PAGINA:
            continue
        unita[d['lingua']].append(dict(pagina=nome, n=len(d['par']), quire=d['quire'] or '?', mano=d['mano'] or '?',
                                       parole=list(d['par']) if con_testo else None))
    return unita


def layout_erbario(trascr='ZL'):
    """Per le unita' 'A' e 'B' dell'erbario: lista di dict(pagina, n, quire, mano). Nessuna parola."""
    return _erbario(trascr, False)


def testo_erbario(trascr='ZL'):
    """Come `layout_erbario` ma con `parole`: SOLO per la fase V."""
    return _erbario(trascr, True)


def strati(pagine):
    """Indice di gruppo (fascicolo e mano) per ogni pagina: i rimescolamenti avvengono solo dentro lo stesso gruppo."""
    chiavi = OrderedDict()
    out = []
    for p in pagine:
        out.append(chiavi.setdefault((p['quire'], p['mano']), len(chiavi)))
    return out


def _zodiaco(trascr, con_testo):
    pag = _pagine(trascr)
    out = OrderedDict()
    for segno, fogli in SEGNI.items():
        et, altro = [], []
        for f in fogli:
            d = pag.get(f)
            if d is None:
                continue
            et.extend([ps for ps in d['et'] if ps])
            altro.extend(d['altro'])
        out[segno] = dict(n_etichette=len(et), n_parole_et=[len(ps) for ps in et], n_altro=len(altro),
                          etichette=et if con_testo else None, altro=altro if con_testo else None)
    return out


def layout_zodiaco(trascr='ZL'):
    """Per ogni segno: numero di righe di etichetta, parole per riga e parole di cerchi e raggi. Nessuna parola."""
    return _zodiaco(trascr, False)


def testo_zodiaco(trascr='ZL'):
    """Come `layout_zodiaco` ma con `etichette` (liste di parole per riga) e `altro`: SOLO per la fase V."""
    return _zodiaco(trascr, True)
