# -*- coding: utf-8 -*-
"""IA38, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PYTHONIOENCODING=utf-8 USCITA=<cartella nel repo> python esperimenti/sezobi_prove.py [riferimento] [peso0 | rumore]
Prove: (1) `riferimento`: il riferimento della differenza fra sezioni usa SOLO pagine di fogli d'addestramento (mai validazione ne' tenuti fuori) e il confronto candidato/vero usa le stesse pagine,
le stesse sezioni e gli stessi vocabolari; un testo senza struttura di sezione (le pagine rimescolate fra sezioni) ha z fortemente negativo; (2) `peso0` (richiede un mondo preparato: `CACHE38`, `MONDO38`, e
`PESO_SEZ38=0`): la valutazione di IA38 con peso zero e' ESATTAMENTE quella di IA37 (stesso argomento, stesso risultato); (3) `rumore` (richiede `CACHE38`, `MONDO38`): il rumore della differenza fra sezioni
di un mezzo libro (seme e divisione dei fogli) rispetto alla differenza fra punti di manopole.
"""
import json
import os
import random
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def prova_riferimento():
    import righello_banco as B
    import ia07_voynich_neurale as I7
    import rifare_dati as RD
    import piano_misure as PMS
    import sezobi_misure as SO
    c = I7.contesto_A()
    f_add, f_val, f_fuori = RD.divisione_fogli()
    sp = {p: k[0] for p, k in PMS.chiavi_pagina().items()}
    ref = SO.riferimento(c['vere'], c['ids'], lambda s: B.dividi_meta(s), f_add, divisioni=30)
    tutte = SO.pagine_addestramento(c['ids'], f_add)
    assert ref['pagine_addestramento'] == len(tutte) and tutte
    assert all(I7.foglio_di(p) in set(f_add) for p in tutte) and not any(I7.foglio_di(p) in set(f_val) | set(f_fuori) for p in tutte), 'solo fogli d\'addestramento'
    for n in SO.NOMI_OBI:
        assert ref['vero'][n] is not None and ref['scala'][n] and ref['scala'][n] > 0, n
    # candidato = vero stesso: z = 0 per costruzione (stesse pagine, stesse sezioni, stessi vocabolari)
    spec = SO.Spec(c['vere'], tutte, sp)
    b, p = SO.div_con(c['vere'], tutte, spec, sp)
    assert abs(b - ref['vero']['div_bigr']) < 1e-12 and abs(p - ref['vero']['div_par']) < 1e-12
    # un testo in cui ogni pagina porta le righe di un'altra pagina a caso (sezioni rimescolate): la differenza fra sezioni cade
    rnd = random.Random(7)
    perm = list(tutte)
    rnd.shuffle(perm)
    rim = OrderedDict((pg, c['vere'][q]) for pg, q in zip(tutte, perm))
    bz, pz = SO.div_con(rim, tutte, spec, sp)
    z = ((bz - ref['vero']['div_bigr']) / ref['scala']['div_bigr'], (pz - ref['vero']['div_par']) / ref['scala']['div_par'])
    assert z[0] < -1 and z[1] < -1, z
    # una meta' vera confrontata con il vero delle stesse pagine non e' lontana (la meta' ha un Spec proprio: confronto sulla stessa meta')
    h1, _ = B.dividi_meta(3)
    pg1 = SO.pagine_addestramento(h1, f_add)
    sp1 = SO.Spec(c['vere'], pg1, sp)
    v1 = SO.div_con(c['vere'], pg1, sp1, sp)
    assert v1[0] is not None and v1[1] is not None
    return 'riferimento della differenza fra sezioni (latino di prova): %d pagine d\'addestramento di %d, nessuna di validazione ne\' tenuta fuori; vero bigrammi %.4f (scala %.4f), parole %.4f (scala %.4f), sezioni %s / %s; testo con le pagine rimescolate fra sezioni: z %.1f e %.1f' % (
        len(tutte), len(c['ids']), ref['vero']['div_bigr'], ref['scala']['div_bigr'], ref['vero']['div_par'], ref['scala']['div_par'], ','.join(ref['sezioni_bigr']), ','.join(ref['sezioni_parole']), z[0], z[1])


def _prepara():
    import ia38_sezioni as X
    mondo = os.environ.get('MONDO38', 'struttura3')
    X.attiva_main(mondo, [])
    X.avvia(mondo, [])
    return X, mondo


def prova_peso0():
    X, mondo = _prepara()
    import sezobi_lavori as SOL
    import prudente_lavori as PLV
    import oracolo_scrittura as OS
    import freqsez_scrittura as FW
    assert SOL.PESO_SEZ == 0.0, 'va lanciata con PESO_SEZ38=0'
    ff = sorted({x['foglio'] for x in X.I7.libro_vero()})
    fogli = ff[::2]
    u = np.concatenate([OS.cubo_da_valori(dict(w_cont=3.0, w_tri=2.0, w_quad=3.0, w_uni=0.8, w_bi=0.8, b_nuove=-0.5, w_pag=0.3)), [0.6]])
    args = (5, 3, list(map(float, u)), 1234, fogli, False, 'C')
    a = SOL.valuta38(args)
    b = PLV.valuta36(args)
    assert not a.get('errore') and not b.get('errore'), (a.get('errore'), b.get('errore'))
    for k in ('somma', 'n', 'obiettivo', 'obiettivo_puro', 'penalita', 'z', 'zg', 'valori', 'copia', 'parole'):
        assert a[k] == b[k], (k, a[k], b[k])
    assert 'div_bigr' not in a['z'] and a['zdiv'] and set(a['zdiv']) == {'div_bigr', 'div_par'}
    return 'con PESO_SEZ38=0 la valutazione di IA38 e\' ESATTAMENTE quella di IA37 (stesso argomento: somma %.4f su %d grandezze, obiettivo %.4f, z e valori identici); le due grandezze nuove si registrano lo stesso (zdiv: %s)' % (
        a['somma'], a['n'], a['obiettivo'], {k: round(v, 2) for k, v in a['zdiv'].items()})


def prova_rumore():
    """Il rumore della differenza fra sezioni di un mezzo libro (z in scale, contro il vero delle stesse pagine d'addestramento): per tre punti di manopole (rete sola, correzioni forti globali, correzioni
    forti di sezione), `N_DIV38` divisioni dei fogli x `N_SEME38` semi. Riporta, per ogni punto, media e deviazione standard (fra seme e divisione) di z, e la differenza fra punti in unita' di rumore."""
    X, mondo = _prepara()
    import sezobi_lavori as SOL
    import oracolo_scrittura as OS
    import freqsez_scrittura as FW
    import ia07_voynich_neurale as I7
    import prudente_lavori as PLV
    S = FW.ScrittoreFreq(X.cart38(mondo, 'rete_C'))
    forte = OS.cubo_da_valori(dict(w_cont=4.0, w_tri=3.0, w_quad=6.0, w_uni=1.0, w_bi=1.0))
    punti = OrderedDict([('rete_sola', np.concatenate([OS.neutro_cubo33(), [0.2]])), ('globali', np.concatenate([forte, [0.2]])), ('di_sezione', np.concatenate([forte, [1.0]]))])
    nd, ns = int(os.environ.get('N_DIV38', 3)), int(os.environ.get('N_SEME38', 2))
    out = OrderedDict()
    rif = SOL._W['div38']
    for nome, u in punti.items():
        zs = {n: [] for n in ('div_bigr', 'div_par')}
        for d in range(nd):
            mA, _ = X.meta_fogli(mondo, d)
            for k in range(ns):
                t, _ = S.libro33(u, 900 + 10 * d + k, mA)
                z, _ = SOL.z_div(I7.libro_A_da_righe(t), mA)
                for n in zs:
                    zs[n].append(z[n])
        out[nome] = OrderedDict((n, OrderedDict([('media', float(np.mean(v))), ('sd', float(np.std(v, ddof=1))), ('n', len(v)), ('valori', [round(x, 3) for x in v])])) for n, v in zs.items())
        print('punto', nome, json.dumps(out[nome]), flush=True)
    for n in ('div_bigr', 'div_par'):
        sd = float(np.mean([out[p][n]['sd'] for p in punti]))
        out['rumore_' + n] = sd
        out['rete_vs_globali_' + n] = (out['rete_sola'][n]['media'] - out['globali'][n]['media']) / sd
        out['rete_vs_sezione_' + n] = (out['rete_sola'][n]['media'] - out['di_sezione'][n]['media']) / sd
    out['scala'] = rif['scala']
    print('rumore', json.dumps(out, indent=1), flush=True)
    return 'rumore della differenza fra sezioni di un mezzo libro (mondo %s, %d divisioni x %d semi): %s' % (mondo, nd, ns, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items() if k.startswith(('rumore', 'rete_vs'))}))


def main():
    prove = OrderedDict([('riferimento', prova_riferimento), ('peso0', prova_peso0), ('rumore', prova_rumore)])
    filtro = sys.argv[1:] or ['riferimento']
    for nome, f in prove.items():
        if nome in filtro:
            print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
