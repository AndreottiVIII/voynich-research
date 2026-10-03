# -*- coding: utf-8 -*-
"""Esperimenti 337, 338, 339. (e337) quanto ognuna delle 5 scelte di grafia dipende dalla posizione (nella riga, tipo di
riga, altezza nella pagina, paragrafo, faccia del foglio); (e338) le due previsioni dell'autocitazione di Timm e
Schinner (fonte nelle righe subito sopra; nella stessa colonna), con il loro generatore come controllo positivo; (e339)
le etichette dello zodiaco: la stessa posizione in mesi diversi porta la stessa etichetta?

Preregistrazione: preregistrazioni/e337.md. Scrive risultati/e337_posizione.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e310_inizi_etichette as e310
import e320_parole as e320

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
LUNGHI_KT = {'t', 'f', 'cth', 'cfh'}
SCELTE = ['ch/sh', 'k/t (gallows)', '-l/-r', 'o-/qo-', '-dy/-ey']
TS = os.path.join(QUI, '..', 'dati', 'cache', 'timm_schinner')


def posti(w):
    """[(scelta, forma lunga)] per una parola."""
    u = D(w)
    out = []
    for g in u:
        if g in ('ch', 'sh'):
            out.append((0, int(g == 'sh')))
        if g in GALL:
            out.append((1, int(g in LUNGHI_KT)))
    if len(u) >= 2 and u[-1] in ('l', 'r') and u[-2] in ('o', 'a'):
        out.append((2, int(u[-1] == 'r')))
    if (len(u) >= 3 and u[0] == 'q' and u[1] == 'o' and u[2] in GALL) or (len(u) >= 2 and u[0] == 'o' and u[1] in GALL):
        out.append((3, int(u[0] == 'q')))
    if len(u) >= 2 and u[-1] == 'y' and u[-2] in ('d', 'e'):
        out.append((4, int(u[-2] == 'e')))
    return out


# ---------- e337 ----------

def e337():
    from scipy.stats import chi2
    from sklearn.linear_model import LogisticRegression
    testa = e308.intestazioni()
    per_pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                per_pag.setdefault(r.pagina, []).append((bool(r.inizio_par), bool(r.fine_par), ws, '%s-%s' % (r.sezione or '?', r.lingua or '?'), r.quire or '?'))
    righe = defaultdict(list)    # scelta -> [(y, fattori)]
    for p, rs in per_pag.items():
        n = len(rs)
        lato = testa.get(p, {}).get('lato', '?')
        npar = 0
        for i, (ini, fine, ws, strato, q) in enumerate(rs):
            npar += ini
            tipo = 'prima' if ini else ('ultima' if fine else 'interna')
            alt = i / (n - 1) if n > 1 else 0.5
            m = len(ws)
            for j, w in enumerate(ws):
                pos = 'prima' if j == 0 else ('ultima' if j == m - 1 else ('seconda' if j == 1 else ('penultima' if j == m - 2 else 'mezzo')))
                for s, y in posti(w):
                    righe[s].append((y, {'posizione nella riga': pos, 'tipo di riga': tipo, 'altezza': alt, 'paragrafo': 'primo' if npar <= 1 else 'altri',
                                         'faccia': lato, 'strato': strato, 'fascicolo': q}))
    fattori = ['posizione nella riga', 'tipo di riga', 'altezza', 'paragrafo', 'faccia']
    out = OrderedDict()
    for s in range(5):
        dati = righe[s]
        y = np.array([d[0] for d in dati])

        def colonne(escludi):
            cols = []
            for f in fattori + ['strato', 'fascicolo']:
                if f == escludi:
                    continue
                if f == 'altezza':
                    a = np.array([d[1]['altezza'] for d in dati])
                    cols += [a - 0.5, (a - 0.5) ** 2]
                else:
                    livelli = sorted({d[1][f] for d in dati})
                    for lv in livelli[1:]:
                        cols.append(np.array([d[1][f] == lv for d in dati], dtype=float))
            return np.column_stack(cols)

        def ll(X):
            m = LogisticRegression(penalty=None, max_iter=5000).fit(X, y)
            p = np.clip(m.predict_proba(X)[:, 1], 1e-12, 1 - 1e-12)
            return float((y * np.log(p) + (1 - y) * np.log(1 - p)).sum()), X.shape[1]
        llf, kf = ll(colonne(None))
        tab = OrderedDict()
        for f in fattori:
            llr, kr = ll(colonne(f))
            lr = 2 * (llf - llr)
            df = kf - kr
            tab[f] = OrderedDict([('bit_per_posto', (llf - llr) / len(y) / math.log(2)), ('chi2', lr), ('gl', df), ('p', float(chi2.sf(lr, df)))])
        soglia = 0.001 / 25
        out[SCELTE[s]] = OrderedDict([('posti', len(y)), ('quota_lunga', float(y.mean())), ('fattori', tab),
                                      ('significativi', [f for f in sorted(tab, key=lambda f: -tab[f]['bit_per_posto']) if tab[f]['p'] < soglia])])
    return out


# ---------- e338 ----------

def pagine_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                per.setdefault(r.pagina, []).append(ws)
    return [v for v in per.values() if len(v) >= 10]


def pagine_ts(seme):
    testo = open(os.path.join(TS, 'seme_%d' % seme, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    linee = [l.split() for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    return [linee[i:i + 29] for i in range(0, min(len(linee), 29 * 140), 29) if len(linee[i:i + 29]) >= 10]


def e338_testo(pagine, rnd):
    prep = []
    for righe in pagine:
        tipi = sorted({w for r in righe for w in r})
        idx = {w: k for k, w in enumerate(tipi)}
        u = [tuple(D(w)) for w in tipi]
        M = np.zeros((len(tipi), len(tipi)), dtype=bool)
        for a in range(len(tipi)):
            M[a, a] = True
            for b in range(a + 1, len(tipi)):
                if abs(len(u[a]) - len(u[b])) <= 1 and e310.dist1(u[a], u[b]):
                    M[a, b] = M[b, a] = True
        prep.append(([[idx[w] for w in r] for r in righe], M))

    def E1(ordini):
        si = tot = 0
        for (righe, M), o in zip(prep, ordini):
            rr = [righe[k] for k in o]
            for i in range(2, len(rr)):
                sopra = rr[i - 1] + rr[i - 2]
                for w in rr[i]:
                    tot += 1
                    si += bool(M[w, sopra].any())
        return si / tot

    def E2(perm_sopra):
        si = tot = 0
        for righe, M in prep:
            for i in range(1, len(righe)):
                sopra = righe[i - 1]
                if perm_sopra:
                    sopra = rnd.sample(sopra, len(sopra))
                for j, w in enumerate(righe[i]):
                    hit = [k for k, x in enumerate(sopra) if M[w, x]]
                    if hit:
                        tot += 1
                        si += any(abs(k - j) <= 1 for k in hit)
        return si / tot if tot else 0.0
    base = [list(range(len(r))) for r, _ in prep]
    v1 = E1(base)
    n1 = []
    for _ in range(200):
        n1.append(E1([rnd.sample(b, len(b)) for b in base]))
    v2 = E2(False)
    n2 = [E2(True) for _ in range(200)]
    return OrderedDict([('pagine', len(prep)), ('fonte_2_righe', v1), ('nullo', statistics.mean(n1)), ('E1', v1 - statistics.mean(n1)), ('z_E1', (v1 - statistics.mean(n1)) / statistics.pstdev(n1)),
                        ('stessa_colonna', v2), ('nullo_colonna', statistics.mean(n2)), ('E2', v2 - statistics.mean(n2)), ('z_E2', (v2 - statistics.mean(n2)) / statistics.pstdev(n2))])


def e338(rnd):
    testi = OrderedDict([('Voynich', pagine_voynich())])
    for s in (1, 19):
        try:
            testi['Timm e Schinner, seme %d' % s] = pagine_ts(s)
        except FileNotFoundError:
            pass
    ris = OrderedDict((n, e338_testo(p, rnd)) for n, p in testi.items())
    gen = [v for n, v in ris.items() if n != 'Voynich']
    valido = bool(gen) and all(v['z_E1'] > 3 for v in gen)
    out = OrderedDict([('testi', ris), ('valido', valido)])
    for k in ('E1', 'E2'):
        v = ris['Voynich']
        g = statistics.mean(x[k] for x in gen) if gen else 0.0
        if not valido:
            es = 'non valido'
        elif v['z_' + k] > 3 and v[k] >= g / 2:
            es = 'autocitazione sostenuta'
        elif v['z_' + k] < 2 or v[k] < g / 4:
            es = 'non sostenuta'
        else:
            es = 'parziale'
        out['esito_' + k] = es
        out['rapporto_' + k] = v[k] / g if g else None
    return out


# ---------- e339 ----------

def e339(rnd):
    pag = OrderedDict()
    testo = Counter()
    for r in trascrizione.leggi('ZL'):
        if not r.parole:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if r.tipo == 'Lz' and ws:
            pag.setdefault(r.pagina, []).append(''.join(ws))
        elif r.tipo[0] == trascrizione.PARAGRAFO:
            testo.update(D(w)[0] for w in ws)
    pag = OrderedDict((p, v) for p, v in pag.items() if len(v) >= 10)
    nomi = list(pag)
    sim = lambda a, b: 1 - e320.lev(tuple(D(a)), tuple(D(b))) / max(len(D(a)), len(D(b)), 1)
    S = {}
    for i, a in enumerate(nomi):
        for b in nomi[i + 1:]:
            S[(a, b)] = np.array([[sim(x, y) for y in pag[b]] for x in pag[a]])
    W = {p: np.array([[sim(x, y) for y in pag[p]] for x in pag[p]]) for p in nomi}

    def stat(perm):
        same, diff = [], []
        for (a, b), M in S.items():
            pa, pb = perm[a], perm[b]
            k = min(len(pa), len(pb))
            Mp = M[np.ix_(pa, pb)]
            same.append(np.diag(Mp[:k, :k]).mean())
            mask = ~np.eye(Mp.shape[0], Mp.shape[1], dtype=bool)
            diff.append(Mp[mask].mean())
        lag = [np.mean([W[p][perm[p][i], perm[p][i + 1]] for i in range(len(perm[p]) - 1)]) for p in nomi]
        return float(np.mean(same) - np.mean(diff)), float(np.mean(lag))
    ident = {p: list(range(len(pag[p]))) for p in nomi}
    vero = stat(ident)
    nul = [stat({p: rnd.sample(ident[p], len(ident[p])) for p in nomi}) for _ in range(1000)]
    za = (vero[0] - statistics.mean(n[0] for n in nul)) / statistics.pstdev(n[0] for n in nul)
    zb = (vero[1] - statistics.mean(n[1] for n in nul)) / statistics.pstdev(n[1] for n in nul)
    iniz = Counter(D(x)[0] for v in pag.values() for x in v)
    tot_e, tot_t = sum(iniz.values()), sum(testo.values())
    esito = 'etichette come sequenza di giorni' if za > 3 else ('no' if abs(za) < 2 else 'incerto')
    return OrderedDict([('pagine', len(nomi)), ('etichette', sum(len(v) for v in pag.values())), ('per_pagina', {p: len(v) for p, v in pag.items()}),
                        ('stessa_posizione_meno_altre', vero[0]), ('z_a', za), ('consecutive', vero[1]), ('nullo_consecutive', statistics.mean(n[1] for n in nul)), ('z_b', zb),
                        ('esito', esito), ('iniziali_etichette', [(g, round(c / tot_e, 3), round(testo[g] / tot_t, 3)) for g, c in iniz.most_common(8)])])


def main():
    r339 = e339(random.Random(339))
    print('e339', r339['esito'], r339['pagine'], r339['etichette'], round(r339['stessa_posizione_meno_altre'], 4), round(r339['z_a'], 1), round(r339['z_b'], 1), flush=True)
    r338 = e338(random.Random(338))
    print('e338', r338['esito_E1'], r338['esito_E2'], {n: (round(v['E1'], 4), round(v['z_E1'], 1), round(v['E2'], 4), round(v['z_E2'], 1)) for n, v in r338['testi'].items()}, flush=True)
    r337 = e337()
    print('e337', {s: v['significativi'] for s, v in r337.items()}, flush=True)
    json.dump(OrderedDict([('e337', r337), ('e338', r338), ('e339', r339)]), open(os.path.join(RISULTATI, 'e337_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e337, e338, e339 — Grammatica della posizione; autocitazione; etichette dello zodiaco', '', 'Preregistrazione: `preregistrazioni/e337.md`.', '',
          '## e337 — perdita in bit per posto togliendo il fattore (p)', '', '| scelta | posti | quota lunga | ' + ' | '.join(['posizione nella riga', 'tipo di riga', 'altezza', 'paragrafo', 'faccia']) + ' |',
          '|---|---|---|---|---|---|---|---|']
    for s, v in r337.items():
        md.append('| %s | %d | %.3f | %s |' % (s, v['posti'], v['quota_lunga'], ' | '.join('%.4f (%.0e)' % (v['fattori'][f]['bit_per_posto'], v['fattori'][f]['p']) for f in v['fattori'])))
    md += [''] + ['- %s: significativi (Bonferroni, p < 0,001/25), in ordine di peso: %s.' % (s, ', '.join(v['significativi']) or 'nessuno') for s, v in r337.items()]
    md += ['', '## e338', '', '| testo | pagine | fonte nelle 2 righe sopra | nullo | E1 | z | stessa colonna | nullo | E2 | z |', '|---|---|---|---|---|---|---|---|---|---|']
    for n, v in r338['testi'].items():
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %.1f | %.3f | %.3f | %+.4f | %.1f |' % (n, v['pagine'], v['fonte_2_righe'], v['nullo'], v['E1'], v['z_E1'], v['stessa_colonna'], v['nullo_colonna'], v['E2'], v['z_E2']))
    md += ['', 'Valido: %s. E1 Voynich / generatore: %s → **%s**. E2: %s → **%s**.' % (
        'sì' if r338['valido'] else 'no', ('%.2f' % r338['rapporto_E1']) if r338['rapporto_E1'] is not None else '–', r338['esito_E1'],
        ('%.2f' % r338['rapporto_E2']) if r338['rapporto_E2'] is not None else '–', r338['esito_E2']), '',
           '## e339 — %d pagine dello zodiaco, %d etichette' % (r339['pagine'], r339['etichette']), '',
           '- (a) Somiglianza stessa posizione − posizioni diverse, fra pagine: %+.4f, z %.1f: **%s**.' % (r339['stessa_posizione_meno_altre'], r339['z_a'], r339['esito']),
           '- (b) Etichette consecutive nella pagina: %.3f contro %.3f del nullo, z %.1f.' % (r339['consecutive'], r339['nullo_consecutive'], r339['z_b']),
           '- (c) Segni iniziali (etichette, testo): %s.' % ', '.join('%s %.2f/%.2f' % x for x in r339['iniziali_etichette'])]
    open(os.path.join(RISULTATI, 'e337_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
