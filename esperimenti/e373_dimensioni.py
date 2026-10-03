# -*- coding: utf-8 -*-
"""Esperimento 373: correlazioni fra otto misure dei bifogli (scarti dallo strato): asse, forme nuove, errori, ripresa,
-ey, qo-, lunghezza, coppie identiche; componenti principali.

Preregistrazione: preregistrazioni/e373.md. Scrive risultati/e373_dimensioni.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e341_fonti as e341
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
NOMI = ['asse', 'forme nuove', 'errori', 'ripresa', '-ey', 'qo-', 'lunghezza', 'coppie identiche']


def main():
    rnd = random.Random(373)
    from scipy.stats import spearmanr
    testa = e308.intestazioni()
    pag = e341.pagine()
    strato = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        strato.setdefault(r.pagina, '%s-%s' % (r.sezione or '?', r.lingua or '?'))
    freq = Counter(w for pars in pag.values() for p in pars for r in p for w in r)
    sim = e350.simili_globali(set(freq))
    cat = {}
    for w, n in freq.items():
        if n == 1:
            cat[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
    bif = defaultdict(list)
    for p, pars in pag.items():
        if testa.get(p, {}).get('Q'):
            bif[(testa[p]['Q'], testa[p]['B'])].append(p)
    righe_di = lambda b: [r for p in bif[b] for par in pag[p] for r in par]
    grandi = [b for b in bif if sum(len(r) for r in righe_di(b)) >= 150]
    st_b = {b: Counter(strato[p] for p in bif[b]).most_common(1)[0][0] for b in grandi}
    raw = {}
    for b in grandi:
        ws = [w for r in righe_di(b) for w in r]
        u = [D(w) for w in ws]
        segni = Counter(g for x in u for g in x)
        tot = sum(segni.values())
        n = len(ws)
        asse = (segni['e'] / tot) + sum(x[-1] == 'y' for x in u) / n - segni['a'] / tot - segni['n'] / tot - sum(x[-1] == 'n' for x in u) / n
        dyey = [x[-2] == 'e' for x in u if len(x) >= 2 and x[-1] == 'y' and x[-2] in ('d', 'e')]
        qo = [x[0] == 'q' for x in u if (len(x) >= 3 and x[0] == 'q' and x[1] == 'o' and x[2] in GALL) or (len(x) >= 2 and x[0] == 'o' and x[1] in GALL)]
        cp = [(a, c) for r in righe_di(b) for a, c in zip(r, r[1:])]
        si = tt = nulsum = 0.0
        for p in bif[b]:
            for par in pag[p]:
                if len(par) < 4:
                    continue

                def q(x):
                    s_ = t_ = 0
                    for i in range(2, len(x)):
                        sopra = x[i - 1] + x[i - 2]
                        for w in x[i]:
                            t_ += 1
                            s_ += e341.ha_fonte(w, sopra)
                    return s_, t_
                s1, t1 = q(par)
                si += s1
                tt += t1
                nulsum += statistics.mean(q(rnd.sample(par, len(par)))[0] for _ in range(50))
        raw[b] = [asse, sum(cat.get(w) == 'nuova' for w in ws) / n, sum(cat.get(w) == 'errore' for w in ws) / n,
                  (si - nulsum) / tt if tt else 0.0, statistics.mean(dyey) if dyey else 0.0, statistics.mean(qo) if qo else 0.0,
                  statistics.mean(len(x) for x in u), sum(a == c for a, c in cp) / len(cp) if cp else 0.0]
    X = np.array([raw[b] for b in grandi])
    per_st = defaultdict(list)
    for i, b in enumerate(grandi):
        per_st[st_b[b]].append(i)
    R = X.copy()
    for idx in per_st.values():
        R[idx] = X[idx] - X[idx].mean(0)
    k = len(NOMI)
    corr = OrderedDict()
    soglia = 0.05 / 28
    for a in range(k):
        for c in range(a + 1, k):
            rho = spearmanr(R[:, a], R[:, c]).correlation
            nul = [spearmanr(R[:, a], rnd.sample(list(R[:, c]), len(grandi))).correlation for _ in range(1000)]
            z = (rho - statistics.mean(nul)) / statistics.pstdev(nul)
            p = sum(abs(x) >= abs(rho) for x in nul) / 1000
            corr['%s ~ %s' % (NOMI[a], NOMI[c])] = OrderedDict([('rho', rho), ('z', z), ('p', p), ('legata', p < soglia and abs(z) > 3)])
    Z = (R - R.mean(0)) / np.maximum(R.std(0), 1e-12)
    w, v = np.linalg.eigh(np.cov(Z.T))
    ordine = np.argsort(-w)
    quote = (w[ordine] / w.sum()).tolist()
    pc1 = [(NOMI[i], round(float(v[i, ordine[0]]), 2)) for i in np.argsort(-np.abs(v[:, ordine[0]]))]
    pc2 = [(NOMI[i], round(float(v[i, ordine[1]]), 2)) for i in np.argsort(-np.abs(v[:, ordine[1]]))]
    legate = [k_ for k_, x in corr.items() if x['legata']]
    esito = ('un solo carattere di sessione' if quote[0] > 0.40 else 'più dimensioni') + ('; coppie legate: ' + ', '.join(legate) if legate else '; dimensioni indipendenti (nessuna coppia legata)')
    out = OrderedDict([('bifogli', len(grandi)), ('correlazioni', corr), ('quote_componenti', quote[:4]), ('prima_componente', pc1), ('seconda_componente', pc2), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:2000], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e373_dimensioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e373 — Le dimensioni delle sessioni', '', 'Preregistrazione: `preregistrazioni/e373.md`. %d bifogli, misure come scarti dallo strato.' % len(grandi), '',
          '| coppia | Spearman | z | legata (Bonferroni) |', '|---|---|---|---|']
    for k_, x in corr.items():
        md.append('| %s | %+.2f | %.1f | %s |' % (k_, x['rho'], x['z'], 'sì' if x['legata'] else '') )
    md += ['', 'Varianza spiegata dalle prime componenti: %s.' % ', '.join('%.0f%%' % (100 * q) for q in quote[:4]),
           'Prima componente: %s.' % ', '.join('%s %+.2f' % t for t in pc1), 'Seconda componente: %s.' % ', '.join('%s %+.2f' % t for t in pc2), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e373_dimensioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
