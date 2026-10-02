# -*- coding: utf-8 -*-
"""Esperimento 231: un discriminatore (regressione logistica su caratteristiche di pagina, validazione incrociata per
gruppi) fra pagine vere del Voynich e pagine gemelle del generatore e192; controlli A contro B ed etichette a caso.

Preregistrazione: preregistrazioni/e231.md. Scrive risultati/e231_discriminatore.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_PAROLE, PIEGHE, SEMI, SEMI_NEGATIVO = 40, 10, (231, 232, 233, 234, 235), (1, 2, 3, 4, 5)
GRUPPI = ('G1', 'G2', 'G3', 'G4', 'G5')


def voynich():
    """OrderedDict pagina -> (lingua, righe di parole pulite)."""
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            out.setdefault(r.pagina, [r.lingua, []])[1].append(ps)
    return out


def generatore_e192(seme=1):
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    out = OrderedDict()
    for pag, _, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), seme, None):
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            out.setdefault(pag, []).append(ps)
    return out


def sim(a, b):
    return 1 - misure._dist_norm(a, b)


def riferimenti(vpag):
    """Unita', coppie, primi e ultimi segni piu' frequenti nel Voynich."""
    U = [tuple(D(w)) for _, rr in vpag.values() for r in rr for w in r]
    cu = Counter(x for u in U for x in u)
    cb = Counter(p for u in U for p in zip(u, u[1:]))
    ini = Counter(tuple(D(r[0]))[0] for _, rr in vpag.values() for r in rr)
    fin = Counter(tuple(D(r[-1]))[-1] for _, rr in vpag.values() for r in rr)
    return ([x for x, _ in cu.most_common(30)], [p for p, _ in cb.most_common(150)],
            [x for x, _ in ini.most_common(10)], [x for x, _ in fin.most_common(10)])


def caratteristiche(pagine, rif):
    """pagine: OrderedDict nome -> righe. -> (nomi delle pagine, matrice, nomi delle caratteristiche)."""
    unita_top, coppie_top, ini_top, fin_top = rif
    tutte = [w for rr in pagine.values() for r in rr for w in r]
    freq = Counter(tutte)
    top100 = {w for w, _ in freq.most_common(100)}
    nomi_p, X, nomi_f = [], [], None
    for pag, rr in pagine.items():
        ws = [w for r in rr for w in r]
        if len(ws) < MIN_PAROLE:
            continue
        T = [[tuple(D(w)) for w in r] for r in rr]
        U = [u for r in T for u in r]
        f = OrderedDict()
        cu = Counter(x for u in U for x in u)
        n = sum(cu.values())
        for x in unita_top:
            f['G1 %s' % x] = cu[x] / n
        cb = Counter(p for u in U for p in zip(u, u[1:]))
        nb = sum(cb.values()) or 1
        for p in coppie_top:
            f['G2 %s+%s' % p] = cb[p] / nb
        lung = [len(u) for u in U]
        cw = Counter(ws)
        f['G3 lunghezza media'] = statistics.mean(lung)
        f['G3 lunghezza deviazione'] = statistics.pstdev(lung)
        f['G3 tipi su parole'] = len(cw) / len(ws)
        f['G3 uniche nella pagina'] = sum(cw[w] == 1 for w in ws) / len(ws)
        f['G3 uniche nel testo'] = sum(freq[w] == 1 for w in ws) / len(ws)
        f['G3 fra le 100 piu frequenti'] = sum(w in top100 for w in ws) / len(ws)
        ini = Counter(r[0][0] for r in T if r)
        fin = Counter(r[-1][-1] for r in T if r)
        for x in ini_top:
            f['G4 inizio %s' % x] = ini[x] / (sum(ini.values()) or 1)
        for x in fin_top:
            f['G4 fine %s' % x] = fin[x] / (sum(fin.values()) or 1)
        vic = [sim(a, b) for r in T for a, b in zip(r, r[1:])]
        f['G4 somiglianza fra vicine'] = statistics.mean(vic) if vic else 0.0
        cp = [(a, b) for r in rr for a, b in zip(r, r[1:])]
        f['G4 unioni attestate'] = sum(freq[a + b] > 0 for a, b in cp) / len(cp) if cp else 0.0
        vert = []
        for s, r in zip(T, T[1:]):
            si, ri = s[1:-1], r[1:-1]
            if len(si) >= 2:
                for j, w in enumerate(ri):
                    if j < len(si):
                        altre = [sim(w, x) for t, x in enumerate(si) if t != j]
                        vert.append(sim(w, si[j]) - statistics.mean(altre))
        f['G5 verticale'] = statistics.mean(vert) if vert else 0.0
        nomi_p.append(pag)
        X.append(list(f.values()))
        nomi_f = list(f)
    return nomi_p, np.array(X), nomi_f


def modello():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))


def auc_cv(X, y, gruppi=None, semi=SEMI):
    aucs = []
    for s in semi:
        if gruppi is not None:
            pieghe = StratifiedGroupKFold(n_splits=PIEGHE, shuffle=True, random_state=s).split(X, y, gruppi)
        else:
            pieghe = StratifiedKFold(n_splits=PIEGHE, shuffle=True, random_state=s).split(X, y)
        p = np.zeros(len(y))
        for tr, te in pieghe:
            m = modello().fit(X[tr], y[tr])
            p[te] = m.predict_proba(X[te])[:, 1]
        aucs.append(roc_auc_score(y, p))
    return float(np.mean(aucs))


def per_gruppi(X, y, nomi_f, gruppi=None):
    out = OrderedDict()
    for g in GRUPPI:
        col = [i for i, n in enumerate(nomi_f) if n.startswith(g + ' ')]
        out[g] = auc_cv(X[:, col], y, gruppi) if col else None
    return out


def confronto(vpag, gpag, rif):
    """AUC fra pagine vere e pagine gemelle generate, con gruppi, caratteristiche piu' pesanti."""
    nv, Xv, nomi_f = caratteristiche(OrderedDict((p, rr) for p, (_, rr) in vpag.items()), rif)
    ng, Xg, _ = caratteristiche(gpag, rif)
    comuni = [p for p in nv if p in set(ng)]
    iv, ig = {p: i for i, p in enumerate(nv)}, {p: i for i, p in enumerate(ng)}
    X = np.vstack([Xv[[iv[p] for p in comuni]], Xg[[ig[p] for p in comuni]]])
    y = np.array([0] * len(comuni) + [1] * len(comuni))
    gruppi = np.array(comuni + comuni)
    auc = auc_cv(X, y, gruppi)
    m = modello().fit(X, y)
    coef = m[-1].coef_[0]
    pesanti = [(nomi_f[i], float(coef[i]), float(X[y == 0, i].mean()), float(X[y == 1, i].mean())) for i in np.argsort(-np.abs(coef))[:10]]
    return OrderedDict([('pagine', len(comuni)), ('AUC', auc), ('AUC_per_gruppo', per_gruppi(X, y, nomi_f, gruppi)), ('piu_pesanti', pesanti)])


def main():
    vpag = voynich()
    rif = riferimenti(vpag)
    ris = OrderedDict()
    # controllo positivo: A contro B
    nv, Xv, nomi_f = caratteristiche(OrderedDict((p, rr) for p, (_, rr) in vpag.items()), rif)
    lingua = {p: l for p, (l, _) in vpag.items()}
    ab = [i for i, p in enumerate(nv) if lingua[p] in ('A', 'B')]
    yab = np.array([lingua[nv[i]] == 'B' for i in ab], int)
    ris['controllo positivo (A contro B)'] = OrderedDict([('pagine', len(ab)), ('AUC', auc_cv(Xv[ab], yab)), ('AUC_per_gruppo', per_gruppi(Xv[ab], yab, nomi_f))])
    # controllo negativo: etichette a caso
    neg = []
    for s in SEMI_NEGATIVO:
        y = np.array([1] * (len(nv) // 2) + [0] * (len(nv) - len(nv) // 2))
        random.Random(s).shuffle(y)
        neg.append(auc_cv(Xv, y, semi=(s,)))
    ris['controllo negativo (etichette a caso)'] = OrderedDict([('pagine', len(nv)), ('AUC', float(np.mean(neg))), ('AUC_singoli', neg)])
    print('controlli: A/B %.3f, a caso %.3f' % (ris['controllo positivo (A contro B)']['AUC'], ris['controllo negativo (etichette a caso)']['AUC']), flush=True)
    ris['generatore e192 contro Voynich'] = confronto(vpag, generatore_e192(1), rif)
    g = ris['generatore e192 contro Voynich']
    print('generatore e192: AUC %.3f, per gruppo %s' % (g['AUC'], {k: round(v, 3) for k, v in g['AUC_per_gruppo'].items()}), flush=True)
    valido = ris['controllo positivo (A contro B)']['AUC'] >= 0.8 and 0.4 <= ris['controllo negativo (etichette a caso)']['AUC'] <= 0.6
    esito = ('non valido' if not valido else 'indistinguibile' if g['AUC'] <= 0.6 else 'distinguibile' if g['AUC'] >= 0.7 else 'parzialmente distinguibile')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e231_discriminatore.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e231 — Discriminatore: pagine vere contro pagine del generatore', '',
          'Regressione logistica su caratteristiche di pagina, validazione incrociata a %d pieghe ripetuta %d volte; per il generatore '
          'la pagina vera e la gemella generata stanno nella stessa piega. Preregistrazione: `preregistrazioni/e231.md`.' % (PIEGHE, len(SEMI)), '',
          '| confronto | pagine | AUC | G1 segni | G2 coppie | G3 parole | G4 riga | G5 verticale |', '|---|---|---|---|---|---|---|---|']
    for nome in ('controllo positivo (A contro B)', 'generatore e192 contro Voynich'):
        r = ris[nome]
        md.append('| %s | %d | %.3f | %s |' % (nome, r['pagine'], r['AUC'], ' | '.join('%.3f' % r['AUC_per_gruppo'][k] for k in GRUPPI)))
    r = ris['controllo negativo (etichette a caso)']
    md.append('| controllo negativo (etichette a caso) | %d | %.3f | | | | | |' % (r['pagine'], r['AUC']))
    md += ['', 'Caratteristiche più pesanti (coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, c, a, b in g['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, c, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e231_discriminatore.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
