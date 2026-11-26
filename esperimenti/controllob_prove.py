# -*- coding: utf-8 -*-
"""IA42, prove di unita' (modulo di supporto, non e' un esperimento). Mai sul Voynich e mai sul libro v21 scelto come vero: per le prove si usa V21_VERO42=14.

    SOLO_CONTROLLI=1 V21_VERO42=14 PYTHONIOENCODING=utf-8 USCITA=<cartella nel repo> CACHE42=<cartella nel repo> python esperimenti/controllob_prove.py [verdetto mondo]
Prove: (1) `verdetto`: i criteri su numeri finti (validita', esiti, strumenti che escono dal verdetto, niente "sorprese"); (2) `mondo`: il mondo `v21w` (le righe del libro v21 con foglio, sezione, lingua e mano
di ogni pagina dal libro di base; inizi di paragrafo e fine pagina coerenti).
"""
import os
import sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def _div(b_gem, b_s, b_t, z_s, z_dif, ind_vero=0.8, ind_dif=0.2):
    mis = ('heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par', 'ttr_pagina', 'hapax', 'dispersione', 'vicine', 'lunghezza', 'doppie', 'testa')
    zs = OrderedDict((n, z_s.get(n, 0.5)) for n in mis)
    zd = OrderedDict((n, z_dif.get(n, 0.2)) for n in mis)
    riga = lambda b, z: OrderedDict([('n', 8), ('b', b), ('b_errore', 0.03), ('b_sd_libri', 0.05), ('indovina', 0.8), ('z', z)])
    return OrderedDict([('divisione', 1), ('righe', OrderedDict([('s100k30', riga(b_s, zs)), ('t100', riga(b_t, zs)), ('neu', riga(0.9, zs)), ('gem', riga(b_gem, OrderedDict((n, 0.1) for n in mis)))])),
                        ('difetti', OrderedDict([('pagine_rimescolate', OrderedDict([('z', zd), ('indovina', ind_dif)]))])), ('vero', OrderedDict([('indovina', ind_vero)]))])


def prova_verdetto():
    import ia42_controllob as C
    visto = {'sezione': -9.0, 'vicine': -5.0}
    out = []

    def v(b, gem=0.5, z=None, zd=None, ind_dif=0.2):
        d = _div(gem, b, b, z or {}, zd if zd is not None else visto, ind_dif=ind_dif)
        return C.valuta([d, d])
    r = v(0.66, z={'dispersione': -2.5, 'vicine': -1.0, 'sezione': -1.0})
    assert r['valido'] and r['esito'].startswith('STESSO VOTO') and r['b']['previsione_ok'], r['esito']
    assert r['misure_riferimento']['dispersione']['lettura'].startswith('fuori da 2') and r['misure_riferimento']['vicine']['lettura'].startswith('dentro qui e fuori sul Voynich'), r['misure_riferimento']
    assert r['previsione_misure']['dispersione_fuori_anche_qui'] and r['previsione_misure']['vicine_dentro']
    out.append('b 0,66 -> stesso voto, previsione di Fable confermata')
    r = v(0.55)
    assert r['esito'].startswith("VOYNICH PIU' DIFFICILE"), r['esito']
    r = v(0.59)
    assert r['esito'].startswith('NON DECISO'), r['esito']
    r = v(0.75)
    assert r['esito'].startswith('NON DECISO'), r['esito']
    assert v(0.71)['esito'].startswith('STESSO VOTO') and v(0.58)['esito'].startswith("VOYNICH PIU'") and v(0.61)['esito'].startswith('STESSO VOTO')
    out.append("b 0,55 -> Voynich piu' difficile; 0,59 e 0,75 -> non deciso; estremi 0,58 / 0,61 / 0,71 nel verso scritto")
    r = v(0.66, gem=0.72)
    assert not r['valido'] and r['esito'].startswith('non valido'), r['esito']
    r = v(0.66, gem=0.35)
    assert not r['valido']
    r = v(0.66, zd={'sezione': 1.0, 'vicine': -5.0})
    assert not r['valido'] and not r['strumenti_visti']['sezione']
    r = v(0.66, ind_dif=0.7)
    assert not r['valido'] and not r['strumenti_visti']['indovina']
    out.append('non valido: gemelli fuori fascia (sopra e sotto), `sezione` o indovina-sezione che non vedono le pagine rimescolate')
    # `vicine` che non vede il suo difetto esce DA SOLA dal verdetto: il controllo resta valido, la sua riga dice "fuori dal verdetto"
    r = v(0.66, z={'vicine': -4.0}, zd={'sezione': -9.0, 'vicine': -0.5})
    assert r['valido'] and r['misure_riferimento']['vicine']['lettura'].startswith('fuori dal verdetto') and not r['misure_riferimento']['vicine']['valida'], r['misure_riferimento']['vicine']
    assert r['previsione_misure']['vicine_dentro'] is None, r['previsione_misure']
    assert 'vicine' not in r['altre_misure_fuori_qui']
    out.append('`vicine` senza difetto visto: esce dal verdetto (ne\' passata ne\' bocciata), il controllo resta valido')
    assert 'sorpresa' not in str(sorted(r.keys())) and 'sorprese' not in str(r['strumenti_visti'])
    out.append('nessuna "sorpresa" fra gli strumenti')
    return '; '.join(out)


def prova_mondo():
    import ia07_voynich_neurale as I7
    import ia42_controllob as C
    assert C.V21_VERO != 13, 'le prove non usano il libro scelto come vero (13)'
    base = I7.libro_vero()
    rows = C.righe_v21w(base)
    pag_base = list(OrderedDict.fromkeys(x['pagina'] for x in base))
    pag = list(OrderedDict.fromkeys(x['pagina'] for x in rows))
    assert pag and all(p in pag_base for p in pag), 'pagine fuori dal libro di base'
    attr = {x['pagina']: (x['foglio'], x['sezione'], x['lingua'], x['mano']) for x in base}
    for x in rows:
        assert (x['foglio'], x['sezione'], x['lingua'], x['mano']) == attr[x['pagina']]
        assert x['parole'] and all(isinstance(w, str) and w for w in x['parole'])
        assert isinstance(x['ini'], bool) and isinstance(x['fin'], bool)
    for i, x in enumerate(rows):          # `fin` = ultima riga di un paragrafo: ultima della pagina o la riga dopo e' un inizio
        dopo = rows[i + 1] if i + 1 < len(rows) else None
        assert x['fin'] == (dopo is None or dopo['pagina'] != x['pagina'] or dopo['ini'])
    k = C.V21_VERO
    rif = I7.libro_riferimento_A('b', k)
    n_rif = sum(1 for p in pag_base for _, ws in rif.get(p, []) if ws)
    assert len(rows) == n_rif, (len(rows), n_rif)
    # la parola scritta in unita' tutte e' la stessa che si ottiene dividendola di nuovo
    D = I7.divisore()
    for (p, righe) in list(rif.items())[:5]:
        for _, ws in righe:
            for w in ws:
                assert tuple(D(''.join(w))) == tuple(w), (w, D(''.join(w)))
    # il mondo e' registrato e le righe vengono dal mondo
    import righello_testi as RT
    assert C.MONDO in RT.MONDI
    r2 = RT.righe_sintetiche(base, C.MONDO)
    assert len(r2) == len(rows)
    return 'mondo `v21w` con il libro v21 n. %d: %d righe su %d pagine (base: %d pagine), attributi per pagina uguali alla base, inizi e fine paragrafo coerenti, parole che si risuddividono come prima' % (k, len(rows), len(pag), len(pag_base))


PROVE = OrderedDict([('verdetto', prova_verdetto), ('mondo', prova_mondo)])

if __name__ == '__main__':
    scelte = sys.argv[1:] or list(PROVE)
    for n in scelte:
        print('[%s] %s' % (n, PROVE[n]()), flush=True)
    print('prove riuscite: %s' % ', '.join(scelte))
