# -*- coding: utf-8 -*-
"""IA35, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PICCOLO32=1 PYTHONIOENCODING=utf-8 USCITA=<cartella> python esperimenti/sezione_prove.py [parte ...]
Prove: (1) gli indici di condizionamento (una sola funzione per i dati e per la scrittura; "primo glifo" una volta per riga); (2) la rete: la condizionata ha i parametri in piu', l'ablazione no;
la scrittura segno per segno e' uguale al calcolo a tratti (condizionata e ablazione); l'addestramento scende; (3) addestramento intero e scrittura di un mezzo libro con lo scrittore di IA33 sopra
la rete (a taglia piccola); (4) il mondo `struttura2` (senza parole di tema, oracolo e gemello); (5) le due misure nuove; (6) il giudice b mediato; (7) le regole di lettura su numeri finti.
"""
import os
import sys
import tempfile
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def _pagine(n=4):
    import ia07_voynich_neurale as I7
    import gradini_modelli as GM
    import rifare_dati as RD
    import sezione_rete as SR
    f_add, _, _ = RD.divisione_fogli()
    voc, ctx = RD.contesto(f_add)
    info = SR.Info(voc)
    pp = RD.pagine_per_modello(f_add[:n], ctx)
    for P in pp:
        P['C'] = SR.cond_da_tok(P['tok'], info)
    return voc, ctx, info, pp


def prova_indici():
    import sezione_rete as SR
    voc, ctx, info, pp = _pagine(2)
    assert info.n[0] >= 2 and info.n[3] == 4, info.n
    P = pp[0]
    C = P['C']
    assert C.shape == (len(P['tok']), 7)
    # la sezione, la lingua e la mano restano costanti dopo la testa di pagina; una volta per riga il "primo glifo" (0)
    assert len(set(C[10:, 0])) == 1 and len(set(C[10:, 2])) == 1
    nlinee = int(sum(1 for t in P['tok'] if int(t) in ctx.Tset))
    assert int((C[:, 6] == 0).sum()) == nlinee, ((C[:, 6] == 0).sum(), nlinee)
    # lo stato incrementale e' la stessa funzione
    sc = SR.StatoCond(info)
    assert all(sc.passo(int(t)) == list(C[i]) for i, t in enumerate(P['tok']))
    return 'indici: %d famiglie (%s), un "primo glifo" per riga (%d righe), stato incrementale = dati' % (len(info.n), info.n, nlinee)


def prova_rete():
    import torch
    import gradini_modelli as GM
    import sezione_rete as SR
    voc, ctx, info, pp = _pagine(3)
    cfg = GM.cfg_completa(1, voc, ctx, True)
    ris = []
    for cond in (True, False):
        c = dict(cfg, cond=cond, sizes=list(info.n))
        torch.manual_seed(5)
        m = SR.costruisci_rete(c)
        m.info = info
        m.eval()
        n_par = sum(p.numel() for p in m.parameters())
        P = pp[0]
        T = len(P['tok']) - 1
        X = torch.as_tensor(np.asarray(P['tok'][:T], dtype=np.int64))[None]
        C = torch.as_tensor(P['C'][:T])[None]
        with torch.no_grad():
            batch = m(X, C)['logits'][0]
        pen = SR.PennaCond(m, ctx)
        pen.apri()
        passo = torch.tensor([pen.dai(int(t)) for t in P['tok'][:T]])
        err = float((passo - batch).abs().max())
        assert err < 1e-4, 'scrittura segno per segno diversa dal calcolo a tratti: %.2e (cond=%s)' % (err, cond)
        ris.append((cond, n_par, err))
    assert ris[0][1] > ris[1][1], 'la rete condizionata deve avere piu\' parametri'
    # le tre varianti della griglia: scrittura = calcolo a tratti, parametri, penalita' L2 solo nella terza
    var_info = []
    for nome, v in SR.VARIANTI.items():
        c = dict(cfg, cond=True, sizes=list(info.n), **v)
        torch.manual_seed(5)
        m = SR.costruisci_rete(c)
        m.info = info
        m.eval()
        P = pp[0]
        T = len(P['tok']) - 1
        X = torch.as_tensor(np.asarray(P['tok'][:T], dtype=np.int64))[None]
        C = torch.as_tensor(P['C'][:T])[None]
        with torch.no_grad():
            batch = m(X, C)['logits'][0]
        pen = SR.PennaCond(m, ctx)
        pen.apri()
        passo = torch.tensor([pen.dai(int(t)) for t in P['tok'][:T]])
        assert float((passo - batch).abs().max()) < 1e-4, nome
        for q in (m.b_sl.weight, m.b_tp.weight):
            torch.nn.init.normal_(q, std=0.5)
        pe = float(m.penalita()) if hasattr(m.penalita(), 'item') else m.penalita()
        assert (pe > 0) == (v['l2_bias'] > 0), (nome, pe)
        var_info.append('%s: %d parametri' % (nome, sum(p.numel() for p in m.parameters())))
    # la scelta sulla validazione: la perplessita' di validazione piu' bassa, sui fogli di validazione e mai su quelli tenuti fuori
    import json
    tmp = tempfile.mkdtemp(prefix='ia35scelta_')
    for nome, vv, ff in (('Ca', 2.9, 2.5), ('Cb', 2.8, 3.0), ('Cc', 2.85, 2.0), ('A', 2.95, 2.6)):
        os.makedirs(os.path.join(tmp, 'rete_' + nome))
        open(os.path.join(tmp, 'rete_' + nome, 'pieno.pt'), 'wb').write(b'x')
        json.dump(dict(bpc_val_A=vv, bpc_val_C=vv + 0.1, bpc_fuori_A=ff, bpc_fuori_C=ff + 0.1, variante=None), open(os.path.join(tmp, 'rete_' + nome, 'pieno.json'), 'w'))
    sc = SR.scegli_variante(tmp)
    assert sc['scelta'] == 'Cb' and sc['batte_ablazione_in_validazione'] and os.path.exists(os.path.join(tmp, 'rete_C', 'pieno.pt')), sc
    # l'addestramento scende (pochi passi su 3 pagine)
    c = dict(cfg, cond=True, sizes=list(info.n))
    torch.manual_seed(5)
    m = SR.costruisci_rete(c)
    m.info = info
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=GM.LR, weight_decay=GM.DECADIMENTO)
    rng = np.random.default_rng(1)
    prima = SR.bpc35(m, ctx, pp)
    for _ in range(4):
        SR._epoca35(m, ctx, pp, opt, rng)
    dopo = SR.bpc35(m, ctx, pp)
    assert dopo < prima, (prima, dopo)
    return 'rete (varianti: ' + '; '.join(var_info) + '; scelta sulla validazione provata): parametri %d (condizionata) contro %d (ablazione); scrittura = calcolo a tratti (errori %.1e / %.1e); bit per segno %.3f -> %.3f in 4 epoche' % (
        ris[0][1], ris[1][1], ris[0][2], ris[1][2], prima, dopo)


def prova_scrittore():
    import ia07_voynich_neurale as I7
    import oracolo_scrittura as OS
    import rifare_dati as RD
    import sezione_rete as SR
    import sezione_scrittura as SS
    out = []
    tmp = tempfile.mkdtemp(prefix='ia35prova_')
    for cond in (True, False):
        cart = os.path.join(tmp, 'rete_' + ('C' if cond else 'A'))
        ris = SR.addestra_pieno35(cart, cond)
        assert os.path.exists(os.path.join(cart, 'pieno.pt')) and ris['bpc_fuori_A'] is not None
        S = SS.ScrittoreCond(cart)
        fogli = sorted({I7.foglio_di(p) for p in S.pp})[:3]
        t, man = S.libro33(OS.neutro_cubo33(), 7, fogli)
        assert len(t) > 20 and all(isinstance(w, str) for _, _, ps in t for w in ps)
        k = list(OS.neutro_cubo33())
        k[6], k[7], k[10], k[13] = 0.5, 0.5, 0.5, 0.4           # correzioni a segni e a parole accese
        t2, _ = S.libro33(np.array(k), 8, fogli)
        assert len(t2) == len(t)
        out.append('%s: epoche %d, bit per segno validazione %.3f, fuori piega %.3f, %d righe' % ('C' if cond else 'A', ris['epoche_totali'], ris['bpc_val_A'], ris['bpc_fuori_A'], len(t)))
    return 'addestramento e scrittura a taglia piccola (' + '; '.join(out) + ')'


def prova_mondo():
    import ia07_voynich_neurale as I7
    import piano_mondo as PM
    import sezione_mondo as SMO
    base = I7.libro_vero()
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    assert SMO.PAR_STRUTTURA2['tema'] == 0.0 and PM.PAR_STRUTTURA['tema'] > 0
    r1 = PM.sintetico_struttura(base, base, 11, D, unita, SMO.PAR_STRUTTURA2)
    r2 = PM.sintetico_struttura(base, base, 11, D, unita, SMO.PAR_STRUTTURA2)
    assert [x['parole'] for x in r1] == [x['parole'] for x in r2]
    f_add = sorted({x['foglio'] for x in base})[::2]
    t = SMO.libro_oracolo(base, base, f_add, 1, 5)
    t2 = SMO.libro_oracolo(base, base, f_add, 2, 5)
    g = SMO.libro_gemello(base, 9)
    assert len(t) == len(base) == len(t2) == len(g)
    return 'mondo struttura2: deterministico, tema = 0, oracolo (1 e 2 volte) e gemello con la disposizione del libro'


def prova_misure():
    import righello_testi as RT
    import righello_banco as B
    import ia07_voynich_neurale as I7
    import sezione_misure as SM
    c = I7.contesto_A()
    ref = SM.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s), 30)
    for n in SM.NUOVE:
        assert ref['vero'][n] is not None and ref['sigma'][n], n
        assert 0 < ref['vero'][n] < 1
    m = SM.misure_testo(RT.rows_di('CTRL:tutto'), c['ids'])
    z = {n: (m[n] - ref['vero'][n]) / ref['sigma'][n] for n in SM.NUOVE}
    h1, h2 = B.dividi_meta(5)
    mh = SM.misure_testo(c['vere'], h1)
    zh = max(abs(mh[n] - ref['vero'][n]) / ref['scala'][n] for n in SM.NUOVE)
    assert zh < 4
    return 'misure nuove (ttr_pagina %.3f, hapax %.3f sul testo vero; sigma %.4f / %.4f); testo del tutto rimescolato: z %s; una meta\' entro %.1f scale' % (
        ref['vero']['ttr_pagina'], ref['vero']['hapax'], ref['sigma']['ttr_pagina'], ref['sigma']['hapax'], {k: round(v, 1) for k, v in z.items()}, zh)


def prova_giudice_b():
    import ia07_voynich_neurale as I7
    import ia01_giudice_neurale as G
    import righello_giudici as RG
    import rifare_dati as RD
    import sezione_giudice as SG
    c = I7.contesto_A()
    f = set(RD.divisione_fogli()[2])
    pagine = [p for p in c['ids'] if I7.foglio_di(p) in f]
    voc = RG.vocabolario_N(c['vere'])
    libri = [G.markov(c['vere'], 2, 100 + i) for i in range(6)]
    r = SG.esame_b_medio(c['vere'], libri, pagine, I7.foglio_di, voc, ripetizioni=3, permutazioni=3, seme=1)
    assert r['auc'] is not None and 3 <= len(r['per_libro']) <= 6 and r['nullo_sd'] is not None and 0.0 <= r['auc'] <= 1.0
    return 'giudice b mediato: auc %.3f su 3 ripetizioni, per libro %d valori (su 6), sd fra ripetizioni %.3f, nullo %.3f +- %.3f' % (r['auc'], len(r['per_libro']), r['sd_ripetizioni'], r['nullo_media'], r['nullo_sd'])


def prova_criteri():
    os.environ.setdefault('PICCOLO32', '1')
    import ia35_sezione as X

    def ins(media, err=0.01, n=8, ok=True, quota=1.0, mis=None, ali=None):
        j = OrderedDict((k, OrderedDict([('media', media[k]), ('sd_libri', 0.01), ('n', n), ('errore', err)])) for k in X.GIUDICI3)
        return OrderedDict([('n', n), ('ruolo', ''), ('giudici_mai_visti', j), ('giudici_ok', all(0.4 <= v <= 0.6 for v in media.values())), ('giudici_di_allenamento', {}),
                            ('misure_tenute_fuori', mis or {}), ('misure_di_allenamento', ali or {}), ('quota_entro_2sigma', quota), ('misure_fuori', []), ('copia_ok', ok),
                            ('copia_violazione_max', 0.0), ('copia_quote', {})])
    R = OrderedDict()
    R['orac'] = ins(dict(N=0.45, KN=0.62, b=0.66))
    R['orac2'] = ins(dict(N=0.48, KN=0.57, b=0.60))
    R['gem'] = ins(dict(N=0.50, KN=0.51, b=0.52), quota=0.8)
    R['neuC'] = ins(dict(N=0.98, KN=0.90, b=0.99), n=4)
    R['neuA'] = ins(dict(N=0.98, KN=0.90, b=0.99), n=4)
    O = X.lettura_O(R)
    assert O['verdetto'] == 'irraggiungibile' and O['giudici_oltre_0_60'] == ['KN', 'b'], O
    R['ia33A'] = ins(dict(N=0.33, KN=0.75, b=0.60), mis={'sezione': OrderedDict(z=-5.0), 'ini_par': OrderedDict(z=-3.0)})
    R['ia33C'] = ins(dict(N=0.33, KN=0.70, b=0.60), mis={'sezione': OrderedDict(z=-2.0), 'ini_par': OrderedDict(z=-1.0)})
    R['bestA'] = ins(dict(N=0.40, KN=0.70, b=0.60))
    R['best'] = ins(dict(N=0.45, KN=0.62, b=0.60), quota=0.8, mis={'sezione': OrderedDict(z=-1.0), 'ini_par': OrderedDict(z=0.5)})
    e = X.esito_L('struttura2', R, None, O)
    assert e['esito'] == "al livello dell'oracolo", e['esito']
    c = X.lettura_condizionamento('vero', R, {})
    assert c['best']['giudici']['KN']['condizionata'] == 0.62 and c['ia33']['misure_tenute_fuori']['sezione']['z_condizionata'] == -2.0
    assert c['misure_chiave']['sezione']['best'] == -1.0
    R['neuC'] = ins(dict(N=0.98, KN=0.90, b=0.60), n=4)
    assert X.esito_L('vero', R, None, O)['esito'] == 'non valido'
    return 'criteri e lettura del condizionamento: casi su numeri finti ok'


def main():
    prove = [prova_indici, prova_rete, prova_scrittore, prova_mondo, prova_misure, prova_giudice_b, prova_criteri]
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
