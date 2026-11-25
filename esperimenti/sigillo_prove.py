# -*- coding: utf-8 -*-
"""IA41, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich; mondo di sviluppo `struttura3`).

    SOLO_CONTROLLI=1 MONDO41=3 PYTHONIOENCODING=utf-8 USCITA=<cartella nel repo> CACHE41=<cartella nel repo> python esperimenti/sigillo_prove.py [misure giudici divisione verdetto]
Prove: (1) `misure`: le quattordici misure sul testo latino, il rumore e l'effetto dei difetti piantati; (2) `giudici` (mondo `struttura3`): i giudici nuovi danno circa 0,5 sui gemelli del mondo (stessa regola, altri semi) e vedono
i difetti piantati; (3) `divisione`: una divisione nuova (seme dei fogli diverso) rifa' la rete sui suoi fogli e controlla che siano quelli della rete, senza leggere le cache delle altre; (4) `verdetto`: i criteri su numeri finti.
"""
import json
import os
import subprocess
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
BASE_PROVE = os.path.join(QUI, '..', 'dati', 'cache', 'ia41_prove')


def prova_misure():
    import ia07_voynich_neurale as I7
    import rifare_dati as RD
    import sigillo_misure as SM
    c = I7.contesto_A()
    f_add, f_val, f_fuori = RD.divisione_fogli()
    ho = [p for p in c['ids'] if I7.foglio_di(p) in set(f_fuori)]
    m = SM.misure(c['vere'], ho)
    assert set(m) == set(SM.TUTTE)
    mancanti = [n for n, v in m.items() if v is None]
    ru = SM.rumore(c['vere'], list(c['ids']), estrazioni=20)
    assert all(ru[n]['sd'] and ru[n]['sd'] > 0 for n in SM.TUTTE if ru[n]['n'] > 5), ru
    # i difetti piantati: pagine rimescolate muovono sezione, lingua, vicine; meta' righe cambia le misure di riga
    ph = SM.pagine_rimescolate(c['vere'])
    md = SM.misure(ph, ho)
    z = {n: (md[n] - m[n]) / ru[n]['sd'] for n in ('sezione', 'lingua', 'vicine') if md.get(n) is not None and m.get(n) is not None and ru[n]['sd']}
    assert z and all(abs(v) >= SM.SOGLIA_DIFETTO for v in z.values()), z
    import ia01_giudice_neurale as G
    mk = G.markov(c['vere'], 2, 5)
    mr = SM.meta_righe(c['vere'], mk)
    assert any(len(mr[p]) != len(c['vere'][p]) or mr[p] != c['vere'][p] for p in ho)
    return 'misure (latino di prova, %d pagine tenute fuori): 14 misure, mancanti %s; rumore su 20 estrazioni: %s; pagine rimescolate: z %s' % (
        len(ho), mancanti or 'nessuna', {n: round(ru[n]['sd'], 4) for n in SM.NUOVE if ru[n]['sd']}, {k: round(v, 1) for k, v in z.items()})


def _gemelli(n):
    """`n` gemelli del mondo `struttura3` (stessa regola, altri semi) nel formato pagina -> righe."""
    import ia07_voynich_neurale as I7
    import piano_mondo as PM
    import prudente_mondo as PMON
    base = I7._C['righe'] if 'righe' in I7._C else I7.libro_vero()
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    out = []
    import righello_testi as RT
    layout = RT._BASE.get('originale') or base
    for k in range(n):
        righe = PM.sintetico_struttura(layout, layout, PM.seme_str('ia41prova', k), D, unita, PMON.PAR_STRUTTURA3)
        out.append(OrderedDict((p, [(bool(x['ini']), [tuple(D(w)) for w in x['parole']]) for x in rr]) for p, rr in I7.per_pagina(righe).items()))
    return out


def prova_giudici():
    import righello_banco as B
    import righello_testi as RT
    import ia07_voynich_neurale as I7
    import rifare_dati as RD
    import sigillo_giudici as SG
    import sigillo_misure as SM
    import prudente_mondo  # noqa: F401  (registra struttura3)
    B.imposta_mondo('struttura3', [])
    c = I7.contesto_A()
    f_add, f_val, f_fuori = RD.divisione_fogli()
    G = SG.Giudici(c, f_add, f_val, f_fuori)
    gem = _gemelli(5)
    av = [G.auc_avanti(g) for g in gem]
    ind = G.auc_indietro(G.modello_finto(gem[0]), gem[1:])
    acc = [G.acc_indovina(g) for g in gem]
    acc_v = G.acc_indovina(c['vere'])
    # su 30 pagine tenute fuori il vero e' UNA estrazione: tutti i gemelli sbagliano nello stesso verso (rumore del campione, non del giudice): qui si controlla solo che non siano estremi
    assert all(0.25 <= x <= 0.85 for x in av), av
    assert all(0.25 <= x <= 0.85 for x in ind), ind
    assert abs(np.mean(acc) - acc_v) < 0.2, (acc, acc_v)
    # difetto piantato: meta' righe di un altro libro (markov di ordine 2): le sorprese si allontanano da 0,5
    import ia01_giudice_neurale as G01
    mk = G01.markov(c['vere'], 2, 9)
    dif = [SM.meta_righe(g, mk) for g in gem[1:]]
    av_d = [G.auc_avanti(g) for g in dif]
    ind_d = G.auc_indietro(G.modello_finto(gem[0]), dif)
    assert abs(np.mean(av_d) - 0.5) > abs(np.mean(av) - 0.5) + 0.05 or abs(np.mean(ind_d) - 0.5) > abs(np.mean(ind) - 0.5) + 0.05, (av, av_d, ind, ind_d)
    # difetto delle pagine rimescolate: indovina-sezione crolla
    acc_r = [G.acc_indovina(SM.pagine_rimescolate(g, seme=7 + i)) for i, g in enumerate(gem[:3])]
    assert np.mean(acc_r) < np.mean(acc) - 0.15, (acc, acc_r)
    # le pagine tenute fuori non sono ne' studiate ne' di validazione (controllato nel costruttore); ordine KN scelto sulla validazione
    return ('giudici nuovi (mondo struttura3, %d pagine tenute fuori, %d indovinabili in %d sezioni, KN ordine %d): sui gemelli avanti %s, indietro %s, indovina-sezione %.2f (vero %.2f); con meta\' righe di un altro libro avanti %s, '
            'indietro %s; pagine rimescolate: indovina-sezione %.2f') % (len(G.pag_ho), len(G.pagine_indovinabili()), len(G.classi), G.ordine, [round(x, 2) for x in av], [round(x, 2) for x in ind], np.mean(acc), acc_v,
                                                                       [round(x, 2) for x in av_d], [round(x, 2) for x in ind_d], np.mean(acc_r))


def prova_divisione():
    """Rilancia il programma come processo di divisione 1 (seme dei fogli 4101) in una cartella nuova con rete piccola: i fogli della rete devono essere quelli della divisione, diversi da quelli della divisione 0."""
    import tempfile
    import shutil
    os.makedirs(BASE_PROVE, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='divisione_', dir=BASE_PROVE)
    ref = os.path.join(BASE_PROVE, 'dev3', 'banco', 'struttura3')
    assert os.path.exists(os.path.join(ref, 'riferimento.json')), 'serve il riferimento di sviluppo in ' + ref
    ris = {}
    for k in (0, 1):
        d_banco = os.path.join(tmp, 'div%d' % k, 'banco', 'struttura3')
        os.makedirs(d_banco, exist_ok=True)
        shutil.copy(os.path.join(ref, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
        shutil.copytree(os.path.join(ref, 'modelli_misura'), os.path.join(d_banco, 'modelli_misura'), dirs_exist_ok=True)
        env = dict(os.environ, DIV41=str(k), FASE41='R', PROCESSI='1', CACHE41=tmp, MONDO41='3', PICCOLO32='1', EPOCHE32='3', USCITA=os.path.join(tmp, 'uscita'))
        r = subprocess.run([sys.executable, os.path.join(QUI, 'ia41_sigillato.py')], env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        ris[k] = json.load(open(os.path.join(tmp, 'div%d' % k, 'struttura3', 'controllo_divisione.json'), encoding='utf-8'))
        pj = json.load(open(os.path.join(tmp, 'div%d' % k, 'struttura3', 'rete_C', 'pieno.json'), encoding='utf-8'))
        assert pj['fogli'] == ris[k]['fogli'] and ris[k]['fogli_rete_uguali']
        assert not os.path.exists(os.path.join(tmp, 'div%d' % (1 - k), 'struttura3', 'rete_C')) or k == 1, 'la divisione 0 non deve toccare la 1'
    assert ris[0]['seme_fogli'] == 3232 and ris[1]['seme_fogli'] == 4101
    f0, f1 = set(ris[0]['tenuti_fuori']), set(ris[1]['tenuti_fuori'])
    assert f0 != f1 and len(f0 & f1) < len(f0), 'le due divisioni devono avere tenuti fuori diversi'
    # la rete della divisione 1 ha addestrato SOLO sui fogli della divisione 1: nessun foglio tenuto fuori della divisione 1 e' fra quelli della sua rete
    import torch
    d1 = torch.load(os.path.join(tmp, 'div1', 'struttura3', 'rete_C', 'pieno.pt'), weights_only=False)
    assert not (set(d1['f_add']) | set(d1['f_val'])) & f1
    return 'divisione nuova: seme fogli 4101 contro 3232; fogli %s e %s; tenuti fuori in comune %d su %d; la rete della divisione 1 non ha nessun foglio tenuto fuori della divisione 1 fra addestramento e validazione; cartelle separate (%s)' % (
        ris[0]['fogli'], ris[1]['fogli'], len(f0 & f1), len(f0), os.path.basename(tmp))


def prova_verdetto():
    sys.argv = sys.argv[:1]
    os.environ.setdefault('MONDO41', '3')
    import ia41_sigillato as X
    import sigillo_misure as SM

    def divisione(b_s, b_t, b_neu=0.9, z_sez=-1.0, difetti=True):
        z = {n: 0.5 for n in SM.TUTTE}
        z['sezione'] = z_sez
        riga = lambda b, zz=z: OrderedDict([('b', b), ('b_errore', 0.02), ('avanti', 0.5), ('indietro', 0.5), ('indovina', 0.7), ('z', zz)])
        r = OrderedDict([('s100k30', riga(b_s)), ('t100', riga(b_t)), ('neu', riga(b_neu)), ('dif', riga(0.8)), ('v21', riga(0.6))])
        r['dif']['avanti'] = 0.8
        r['dif']['indietro'] = 0.8
        zd = {n: 0.0 for n in SM.TUTTE}
        zd.update(sezione=-8.0, lingua=-6.0, vicine=-7.0)
        return OrderedDict([('divisione', 1), ('righe', r), ('vero', OrderedDict([('indovina', 0.7)])), ('difetti', OrderedDict([('pagine_rimescolate', OrderedDict([('z', zd), ('indovina', 0.3)]))]))])
    divs = [divisione(0.58, 0.64) for _ in range(4)]
    v = X.valuta(divs)
    assert v['c1']['ok'] and v['c2']['ok'] and v['c3']['ok'] and v['c4']['ok'] and v['c5']['ok'] and v['c6']['ok'] and v['esito'].startswith('confermato'), v
    v2 = X.valuta([divisione(0.64, 0.64) for _ in range(4)])
    assert not v2['c1']['ok'] and 'prima divisione' in v2['esito']
    v3 = X.valuta([divisione(0.58, 0.64, b_neu=0.6) for _ in range(4)])
    assert not v3['valido'] and v3['esito'].startswith('non valido')
    v4 = X.valuta([divisione(0.58, 0.64, z_sez=-3.0) for _ in range(4)])
    assert not v4['c3']['ok'] and 'prima divisione' in v4['esito']
    # uno strumento che non vede il suo difetto esce dal verdetto
    ds = [divisione(0.58, 0.64) for _ in range(4)]
    for d in ds:
        d['difetti']['pagine_rimescolate']['z']['lingua'] = 0.5
    v5 = X.valuta(ds)
    assert not v5['strumenti_validi']['lingua'] and 'lingua' in v5['c6']['usciti_dal_verdetto']
    return 'criteri e strumenti validi su numeri finti: confermato; criterio 1 o 3 caduto -> legata alla prima divisione; b non vede neu -> non valido; strumento che non vede il difetto -> fuori dal verdetto'


def main():
    prove = [prova_misure, prova_giudici, prova_divisione, prova_verdetto]
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
