# -*- coding: utf-8 -*-
"""IA32, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PYTHONIOENCODING=utf-8 USCITA=<cartella> python esperimenti/rifare_prove.py
Prove: (1) CMA-ES su una funzione nota con rumore; (2) la scelta a manopole neutre ha la stessa distribuzione di un softmax (frequenze su 40.000 estrazioni) e le manopole
cambiano la distribuzione nel verso atteso (temperatura bassa: piu' massa sul piu' probabile; top-p: niente fuori dal nucleo; correzione: spinta verso la tabella);
(3) la divisione dei fogli: parti disgiunte, quote giuste, ogni sezione rappresentata; (4) il cubo -> manopole: neutro e intervalli; (5) la guardia di copia: un libro
copiato dall'addestramento viola, un testo vero dei fogli tenuti fuori no; (6) il giudice b: vede una versione "rovinata" del testo (AUC alta) e non vede due copie dello
stesso processo (AUC vicino a 0,5).
"""
import math
import os
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def prova_cma():
    import rifare_cma as C
    f, d = C.prova()
    assert f < 0.05 and d < 0.15, (f, d)
    return 'CMA-ES: valore finale %.4f, distanza dall\'ottimo %.3f' % (f, d)


class _Finto:
    """Un Scrittore senza modello: solo `scegli` con le tabelle e i segni di un vocabolario di prova."""


def prova_scelta():
    import rifare_scrittura as RS
    import ia07_voynich_neurale as I7
    import ia16_imitatore as I16
    from types import SimpleNamespace
    voc = I7.vocabolario()
    s = RS.Scrittore.__new__(RS.Scrittore)
    s.ctx = SimpleNamespace(SP=voc['primo_contenuto'], EOL=voc['primo_contenuto'] + 1)
    V = len(voc['segni'])
    s.V = V
    rng = np.random.default_rng(5)
    T = rng.dirichlet(np.ones(V) * 0.3, size=V + 1)
    s.T = T
    s.logT = np.log(np.maximum(T, 1e-9))
    SP, EOL, u0 = s.ctx.SP, s.ctx.EOL, voc['primo_contenuto'] + 2
    lg = list(rng.normal(0, 2.0, V))
    amm = [SP, EOL] + list(range(u0, u0 + 8))
    G = np.zeros((V + 1, V))
    k = RS.da_cubo(RS.neutro_cubo())
    assert all(abs(k[n] - RS.NEUTRO[n]) < 1e-9 for n in RS.NOMI), k
    z = np.array([lg[a] for a in amm])
    p = np.exp(z - z.max())
    p /= p.sum()
    n = 40000
    cont = np.zeros(len(amm))
    for _ in range(n):
        cont[amm.index(s.scegli(lg, amm, V, 3, False, k, G, rng))] += 1
    err = np.abs(cont / n - p).max()
    assert err < 0.012, 'neutro: scarto massimo %.4f dal softmax' % err
    # temperatura bassa sui glifi interni: piu' massa sul piu' probabile fra i glifi
    k2 = dict(k)
    k2['T_int'] = 0.6
    cont2 = np.zeros(len(amm))
    for _ in range(n // 4):
        cont2[amm.index(s.scegli(lg, amm, V, 3, False, k2, G, rng))] += 1
    gl = [i for i, a in enumerate(amm) if a >= u0]
    top = max(gl, key=lambda i: p[i])
    assert cont2[top] / cont2[gl].sum() > cont[top] / cont[gl].sum() + 0.02, 'T_int bassa non concentra'
    # top-p: fuori dal nucleo mai
    k3 = dict(k)
    k3['top_p'] = 0.6
    q = np.exp(z[gl] - z[gl].max())
    q /= q.sum()
    o = np.argsort(-q)
    cum = np.cumsum(q[o])
    nucleo = {amm[gl[i]] for i in o[:int(np.searchsorted(cum, 0.6) + 1)]}
    visti = set()
    for _ in range(4000):
        t = s.scegli(lg, amm, V, 3, False, k3, G, rng)
        if t >= u0:
            visti.add(t)
    assert visti <= nucleo, 'top-p: segni fuori dal nucleo %s' % (visti - nucleo)
    # correzione a conteggi: con una tabella che vuole un segno solo, la scelta va li'
    s.T = np.full((V + 1, V), 1e-6)
    voluto = u0 + 2
    s.T[:, voluto] = 1.0
    s.T = s.T / s.T.sum(1, keepdims=True)
    s.logT = np.log(np.maximum(s.T, 1e-9))
    k4 = dict(k)
    k4['w_cont'] = 0.9
    G2 = np.zeros((V + 1, V))
    cont_a = 0
    for _ in range(3000):
        x = s.scegli(lg, amm, V, 3, False, k4, G2, rng)
        G2[V, x] += 1                      # come fa `pagina`: la scelta entra nei conti del libro in corso
        cont_a += (x == voluto)
    a = cont_a / 3000.0
    k5 = dict(k)
    b = sum(s.scegli(lg, amm, V, 3, False, k5, np.zeros((V + 1, V)), rng) == voluto for _ in range(3000)) / 3000.0
    assert a > b + 0.1, 'correzione a conteggi: %.3f contro %.3f' % (a, b)
    return 'scelta: neutro = softmax (scarto %.4f), T_int, top-p e correzione nel verso atteso (%.3f contro %.3f)' % (err, a, b)


def prova_fogli():
    import rifare_dati as RD
    import ia07_voynich_neurale as I7
    add, val, fuori = RD.divisione_fogli()
    tutti = {f for f, _ in RD.fogli_del_libro()}
    assert set(add) | set(val) | set(fuori) == tutti and not (set(add) & set(val)) and not (set(add) & set(fuori)) and not (set(val) & set(fuori))
    n = len(tutti)
    assert abs(len(fuori) / n - RD.FUORI32) < 0.04 and abs(len(val) / n - RD.VAL32) < 0.04, (len(add), len(val), len(fuori))
    sez = dict(RD.fogli_del_libro())
    for s in set(sez.values()):
        nfs = sum(1 for f in tutti if sez[f] == s)
        if nfs >= 8:
            assert any(sez[f] == s for f in fuori), 'sezione %s senza fogli fuori' % s
    assert RD.divisione_fogli() == (add, val, fuori)
    return 'fogli: %d / %d / %d, disgiunti, deterministici' % (len(add), len(val), len(fuori))


def prova_cubo():
    import rifare_scrittura as RS
    lo = RS.da_cubo(np.zeros(RS.DIM))
    hi = RS.da_cubo(np.ones(RS.DIM))
    for n in ('T_primo', 'T_int', 'T_fine', 'T_eol', 'T_riga'):
        assert abs(lo[n] - RS.T_LO) < 1e-9 and abs(hi[n] - RS.T_HI) < 1e-9
    assert lo['top_p'] == 0.6 and hi['top_p'] == 1.0 and lo['w_cont'] == 0.0 and abs(hi['w_cont'] - 2.4) < 1e-9 and abs(hi['w_tri'] - 2.4) < 1e-9 and lo['s'] == 0.0 and hi['s'] == 1.0
    return 'cubo: intervalli e neutro corretti'


def prova_copia():
    import rifare_scrittura as RS
    import rifare_dati as RD
    import righello_testi as RT
    import ia07_voynich_neurale as I7
    add, val, fuori = RD.divisione_fogli()
    righe = RS.righe_di_fogli(add)
    t = [('f0r', False, list(r)) for r in righe[:200] if len(r) >= 5]
    q = I7.quote(RS.copia_libro(t, add))
    assert q['5-grammi'] > 0.9 and q['righe vere'] > 0.9, q
    tf = [('f0r', False, list(r)) for r in RS.righe_di_fogli(fuori)[:200] if len(r) >= 5]
    q2 = I7.quote(RS.copia_libro(tf, add))
    assert q2['righe intere'] < 0.05, q2
    return 'guardia di copia: copiato %.2f / %.2f contro fogli fuori %.3f' % (q['5-grammi'], q['righe vere'], q2['righe intere'])


def prova_giudice_b():
    """Il giudice b su un testo di prova: due libri "gemelli" (la stessa catena di Markov con semi diversi) e un libro rovinato (parole con un glifo cambiato)."""
    import random
    import rifare_giudice as RGB
    import righello_giudici as RG
    import ia07_voynich_neurale as I7
    import ia01_giudice_neurale as G
    c = I7.contesto_A()
    pagine = [p for p in c['ids']][:60]
    voc = RG.vocabolario_N(c['vere'])
    D = I7.divisore()
    glifi = sorted({g for rows in c['vere'].values() for _, ws in rows for w in ws for g in w})

    def libro(seme, rovina):
        mk = G.markov(c['vere'], 2, seme)
        rnd = random.Random(seme)
        out = OrderedDict()
        for p in pagine:
            rows = []
            for ini, ws in mk[p]:
                ws2 = []
                for w in ws:
                    if rovina and rnd.random() < 0.5 and w:
                        j = rnd.randrange(len(w))
                        w = tuple(list(w[:j]) + [rnd.choice(glifi)] + list(w[j + 1:]))
                    ws2.append(tuple(w))
                rows.append((ini, ws2))
            out[p] = rows
        return out
    vere = OrderedDict((p, c['vere'][p]) for p in pagine)
    gem = [libro(100 + i, False) for i in range(6)]
    rov = [libro(200 + i, True) for i in range(6)]
    a_g = RGB.auc_b(vere, gem[:3], gem[3:], pagine, I7.foglio_di, voc)
    a_r = RGB.auc_b(vere, rov[:3], rov[3:], pagine, I7.foglio_di, voc)
    nul = [RGB.auc_b(vere, gem[:3], gem[3:], pagine, I7.foglio_di, voc, seme=k + 1, permuta=True) for k in range(4)]
    assert a_r > 0.75 and a_r > a_g + 0.15, (a_g, a_r)
    assert abs(np.mean(nul) - 0.5) < 0.12, nul
    return 'giudice b: gemelli %.3f, rovinati %.3f, nullo %.3f' % (a_g, a_r, float(np.mean(nul)))


def main():
    for f in (prova_cma, prova_cubo, prova_fogli, prova_scelta, prova_copia, prova_giudice_b):
        try:
            print('OK  ', f.__name__, '-', f(), flush=True)
        except AssertionError as e:
            print('FALLITA', f.__name__, e, flush=True)
            raise


if __name__ == '__main__':
    main()
