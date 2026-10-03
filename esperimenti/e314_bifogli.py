# -*- coding: utf-8 -*-
"""Esperimenti 314, 315, 318. (e314) lo stato di ogni bifoglio: quanto pesa, che cosa porta, un ordine dei bifogli;
(e315) che cosa separa le lingue A e B nell'erbario oltre all'asse -edy/-aiin; (e318) le pagine candidate fuori posto
contro le irregolarita' fisiche, e i fogli con recto e verso diversi.

Preregistrazione: preregistrazioni/e314.md (con la correzione dell'e315). Scrive risultati/e314_bifogli.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e307_identita_pagine as e307
import e308_libro_fisico as e308

RISULTATI = os.path.join(QUI, '..', 'risultati')
ASSE = ['segno e', 'segno a', 'segno n', 'segno i', 'segno y', 'segno d', 'segno ch', 'iniziale o', 'iniziale ch', 'finale y', 'finale n']
CANDIDATE = ['f1v', 'f2r', 'f2v', 'f4r', 'f7r', 'f52v', 'f53r', 'f90r1', 'f88r']


def punteggio(X, nomi):
    col = {n: k for k, n in enumerate(nomi)}
    Z = (X - X.mean(0)) / np.maximum(X.std(0), 1e-12)
    return Z[:, col['segno e']] + Z[:, col['finale y']] - Z[:, col['segno a']] - Z[:, col['segno n']] - Z[:, col['finale n']]


def eta2(valori, etichette, strati):
    """Quota della varianza (scarti dalla media dello strato) spiegata dai gruppi (strato, etichetta); valori 1D o 2D."""
    v = np.asarray(valori, dtype=float)
    R = v.copy()
    for idx in strati.values():
        R[idx] = v[idx] - v[idx].mean(0)
    gruppi = defaultdict(list)
    for i, e in enumerate(etichette):
        if e is not None:
            gruppi[e].append(i)
    tra = sum(len(g) * R[g].mean(0) ** 2 for g in gruppi.values())
    tot = (R ** 2).sum(0)
    return tra / np.maximum(tot, 1e-15)


def permuta(v, strati, rnd):
    out = v.copy()
    for idx in strati.values():
        x = list(idx)
        rnd.shuffle(x)
        out[idx] = v[x]
    return out


def e314(voy, P, nomi, s, testa, rnd):
    n = len(voy.pagine)
    nomi_p = [p['nome'] for p in voy.pagine]
    strato = [p['strato'] for p in voy.pagine]
    bif = [((testa[x]['Q'], testa[x]['B']) if x in testa and testa[x]['Q'] else None) for x in nomi_p]
    etich = {'bifoglio': [(st, b) if b else None for st, b in zip(strato, bif)],
             'mano': [(st, p['mano']) for st, p in zip(strato, voy.pagine)],
             'fascicolo': [(st, p['fascicolo']) for st, p in zip(strato, voy.pagine)]}
    a = OrderedDict()
    for k, et in etich.items():
        vero = float(eta2(s, et, voy.strati))
        nulli = [float(eta2(permuta(s, voy.strati, rnd), et, voy.strati)) for _ in range(1000)]
        a[k] = OrderedDict([('eta2', vero), ('nullo', statistics.mean(nulli)), ('z', (vero - statistics.mean(nulli)) / statistics.pstdev(nulli))])
    vero_f = eta2(P, etich['bifoglio'], voy.strati)
    nulli_f = np.array([eta2(permuta(P, voy.strati, rnd), etich['bifoglio'], voy.strati) for _ in range(200)])
    zf = (vero_f - nulli_f.mean(0)) / np.maximum(nulli_f.std(0), 1e-12)
    b = [OrderedDict([('caratteristica', nomi[j]), ('eta2', float(vero_f[j])), ('nullo', float(nulli_f[:, j].mean())), ('z', float(zf[j]))]) for j in np.argsort(-zf)[:15]]
    # (c) ordine dei bifogli dentro la sezione
    per_bif = defaultdict(list)
    for i, bb in enumerate(bif):
        if bb:
            per_bif[bb].append(i)
    sez_bif = {bb: Counter(voy.pagine[i]['strato'][0] for i in idx).most_common(1)[0][0] for bb, idx in per_bif.items()}
    mano_bif = {bb: Counter(voy.pagine[i]['mano'] for i in idx).most_common(1)[0][0] for bb, idx in per_bif.items()}
    pos_bif = {bb: statistics.mean(voy.pagine[i]['posizione'] for i in idx) for bb, idx in per_bif.items()}
    from scipy.stats import spearmanr
    c = OrderedDict()
    for sz in sorted(set(sez_bif.values()), key=str):
        bb = [x for x in per_bif if sez_bif[x] == sz]
        if len(bb) < 8:
            continue
        St = np.array([P[per_bif[x]].mean(0) for x in bb])
        C = np.corrcoef(St)
        Sm = np.maximum(np.nan_to_num(C), 0)
        np.fill_diagonal(Sm, 0)
        L = np.diag(Sm.sum(1)) - Sm
        f = np.linalg.eigh(L)[1][:, 1]
        ordine = [bb[i] for i in np.argsort(f)]
        rho = abs(spearmanr(f, [pos_bif[x] for x in bb]).correlation)
        cambi = sum(mano_bif[x] != mano_bif[y] for x, y in zip(ordine, ordine[1:]))
        nr, nc = [], []
        for _ in range(1000):
            o = list(bb)
            rnd.shuffle(o)
            nc.append(sum(mano_bif[x] != mano_bif[y] for x, y in zip(o, o[1:])))
            nr.append(abs(spearmanr(range(len(o)), [pos_bif[x] for x in o]).correlation))
        zc = (cambi - statistics.mean(nc)) / (statistics.pstdev(nc) or 1)
        zr = (rho - statistics.mean(nr)) / (statistics.pstdev(nr) or 1)
        c[sz] = OrderedDict([('bifogli', len(bb)), ('rho_con_il_libro', rho), ('z_rho', zr), ('cambi_di_mano', cambi), ('cambi_attesi', statistics.mean(nc)), ('z_cambi', zc),
                             ('ordine', ['%s-%s (mano %s)' % (x[0], x[1], mano_bif[x]) for x in ordine])])
    esito = 'stato di bifoglio' if a['bifoglio']['z'] > 3 else 'nessuno stato di bifoglio'
    extra = [k for k in ('mano', 'fascicolo') if a[k]['z'] > 3]
    mano_segue = [sz for sz, v in c.items() if v['z_cambi'] < -3]
    return OrderedDict([('a', a), ('esito_a', esito), ('spiegano_anche', extra), ('b', b), ('c', c), ('la_mano_segue_lo_stato_in', mano_segue)])


def e315(voy, X, nomi, s, testa, rnd):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import GroupKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    idx = [i for i, p in enumerate(voy.pagine) if p['strato'][0] == 'H' and p['strato'][1] in ('A', 'B')]
    pag = [voy.pagine[i] for i in idx]
    erb = Counter(w for p in pag for w in p['parole'])
    top = [w for w, _ in erb.most_common(100)]
    Wd = np.array([[Counter(p['parole'])[w] / len(p['parole']) for w in top] for p in pag])
    F = np.hstack([X[idx], Wd])
    nomiF = list(nomi) + ['erbario %s' % w for w in top]
    y = np.array([1 if p['strato'][1] == 'B' else 0 for p in pag])
    gruppi = np.array([hash((testa.get(p['nome'], {}).get('Q'), testa.get(p['nome'], {}).get('B'))) for p in pag])

    def d_cohen(F, y):
        a, b = F[y == 0], F[y == 1]
        sd = np.sqrt((a.var(0) * (len(a) - 1) + b.var(0) * (len(b) - 1)) / (len(a) + len(b) - 2))
        return (b.mean(0) - a.mean(0)) / np.maximum(sd, 1e-12)
    d = d_cohen(F, y)
    nul = np.array([d_cohen(F, np.array(rnd.sample(list(y), len(y)))) for _ in range(1000)])
    zd = (d - nul.mean(0)) / np.maximum(nul.std(0), 1e-12)
    top20 = [OrderedDict([('caratteristica', nomiF[j]), ('d', float(d[j])), ('z', float(zd[j]))]) for j in np.argsort(-np.abs(d))[:20]]
    parola = lambda nm: nm.startswith('parola ') or nm.startswith('erbario ')
    fine_yn = lambda nm: parola(nm) and nm.split(' ', 1)[1][-1] in ('y', 'n')
    sel = OrderedDict([('(i) solo l\'asse', None), ('(ii) tutte', [j for j in range(len(nomiF))]),
                       ('(iii) tutte tranne l\'asse e le parole in -y/-n', [j for j, nm in enumerate(nomiF) if nm not in ASSE and not fine_yn(nm)]),
                       ('(iv) solo parole non in -y/-n', [j for j, nm in enumerate(nomiF) if parola(nm) and not fine_yn(nm)])])

    def auc(cols, yy):
        M = s[idx].reshape(-1, 1) if cols is None else F[:, cols]
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
        pr = cross_val_predict(mdl, M, yy, cv=GroupKFold(n_splits=5), groups=gruppi, method='predict_proba')[:, 1]
        return float(roc_auc_score(yy, pr))
    cl = OrderedDict((k, OrderedDict([('caratteristiche', 1 if c is None else len(c)), ('AUC', auc(c, y))])) for k, c in sel.items())
    k3 = '(iii) tutte tranne l\'asse e le parole in -y/-n'
    nulli = [auc(sel[k3], np.array(rnd.sample(list(y), len(y)))) for _ in range(200)]
    z3 = (cl[k3]['AUC'] - statistics.mean(nulli)) / statistics.pstdev(nulli)
    cl[k3]['nullo'] = statistics.mean(nulli)
    cl[k3]['z'] = z3
    a3 = cl[k3]['AUC']
    esito = 'A e B differiscono oltre l\'asse' if (a3 >= 0.85 and z3 > 3) else ('solo l\'asse' if a3 < 0.70 else 'incerto')
    return OrderedDict([('pagine_A', int((y == 0).sum())), ('pagine_B', int((y == 1).sum())), ('prime_20', top20), ('classificazione', cl), ('esito', esito)])


def e318(voy, P, testa, rnd):
    from scipy.stats import fisher_exact
    per_q = defaultdict(list)
    for p, v in testa.items():
        m = re.match(r'^f(\d+)', p)
        if m and v['Q']:
            per_q[v['Q']].append(int(m.group(1)))
    mancanti = {q for q, nn in per_q.items() if set(range(min(nn), max(nn) + 1)) - set(nn)}
    fogli_bif = defaultdict(set)
    for p, v in testa.items():
        if v['Q']:
            fogli_bif[(v['Q'], v['B'])].add(v['F'])

    def flag(p):
        v = testa.get(p)
        if not v or not v['Q']:
            return OrderedDict()
        return OrderedDict([('senza coniugato', len(fogli_bif[(v['Q'], v['B'])]) == 1), ('fascicolo con fogli mancanti', v['Q'] in mancanti),
                            ('pieghevole', bool(re.match(r'^f\d+[rv]\d+$', p))), ('bifoglio esterno', v['B'] == '1')])
    nomi_p = [p['nome'] for p in voy.pagine]
    fl = {p: flag(p) for p in nomi_p}
    irr = {p: any(fl[p].values()) for p in nomi_p}
    cand = [p for p in CANDIDATE if p in irr]
    altre = [p for p in nomi_p if p not in cand]
    tab = [[sum(irr[p] for p in cand), sum(not irr[p] for p in cand)], [sum(irr[p] for p in altre), sum(not irr[p] for p in altre)]]
    pval = fisher_exact(tab, alternative='greater')[1]
    esito_a = 'concentrate sui fogli irregolari' if pval < 0.01 else ('no' if pval > 0.1 else 'incerto')
    # (b) recto e verso dello stesso foglio
    idx_di = {p: i for i, p in enumerate(nomi_p)}
    fogli = defaultdict(lambda: {'r': [], 'v': []})
    for p in nomi_p:
        v = testa.get(p)
        if v and v['Q'] and v['lato'] in ('r', 'v'):
            fogli[(v['Q'], v['F'])][v['lato']].append(p)
    C = np.corrcoef(P)
    righe = []
    for f, d in fogli.items():
        if len(d['r']) == 1 and len(d['v']) == 1:
            a, b = voy.pagine[idx_di[d['r'][0]]], voy.pagine[idx_di[d['v'][0]]]
            cambia = a['mano'] != b['mano'] or a['strato'] != b['strato']
            righe.append((d['r'][0], d['v'][0], float(C[idx_di[d['r'][0]], idx_di[d['v'][0]]]), cambia, a['mano'], b['mano'], a['strato'], b['strato']))
    cor = np.array([r[2] for r in righe])
    ca = np.array([r[3] for r in righe])
    diff = cor[ca].mean() - cor[~ca].mean() if ca.any() and (~ca).any() else 0.0
    nulli = []
    for _ in range(1000):
        x = np.array(rnd.sample(list(ca), len(ca)))
        nulli.append(cor[x].mean() - cor[~x].mean())
    zb = (diff - statistics.mean(nulli)) / (statistics.pstdev(nulli) or 1)
    peggiori = sorted(righe, key=lambda r: r[2])[:10]
    return OrderedDict([('a', OrderedDict([('candidate', OrderedDict((p, fl[p]) for p in cand)), ('quota_irregolari_candidate', tab[0][0] / max(1, len(cand))),
                                           ('quota_irregolari_altre', tab[1][0] / max(1, len(altre))), ('p', pval), ('esito', esito_a)])),
                        ('b', OrderedDict([('fogli', len(righe)), ('con_cambio', int(ca.sum())), ('correlazione_media', float(cor.mean())), ('differenza_cambio_meno_altri', float(diff)), ('z', zb),
                                           ('esito', 'le facce diverse coincidono con un cambio' if zb < -3 else 'no'),
                                           ('dieci_fogli_con_facce_piu_diverse', [OrderedDict([('recto', r[0]), ('verso', r[1]), ('correlazione', round(r[2], 3)),
                                                                                                ('mani', '%s/%s' % (r[4], r[5])), ('strati', '%s/%s' % ('-'.join(r[6]), '-'.join(r[7])))]) for r in peggiori])]))])


def main():
    testa = e308.intestazioni()
    voy, X, nomi, P = e308.profili()
    s = punteggio(X, nomi)
    r314 = e314(voy, P, nomi, s, testa, random.Random(314))
    print('e314', r314['esito_a'], {k: (round(v['eta2'], 3), round(v['z'], 1)) for k, v in r314['a'].items()}, flush=True)
    r315 = e315(voy, X, nomi, s, testa, random.Random(315))
    print('e315', r315['esito'], {k: round(v['AUC'], 3) for k, v in r315['classificazione'].items()}, flush=True)
    r318 = e318(voy, P, testa, random.Random(318))
    print('e318', r318['a']['esito'], round(r318['a']['p'], 4), r318['b']['esito'], round(r318['b']['z'], 1), flush=True)
    json.dump(OrderedDict([('e314', r314), ('e315', r315), ('e318', r318)]), open(os.path.join(RISULTATI, 'e314_bifogli.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=str)
    md = ['# e314, e315, e318 — Lo stato dei bifogli; le lingue A e B; i fogli irregolari', '', 'Preregistrazione: `preregistrazioni/e314.md` (con la correzione dell\'e315).', '',
          '## e314 — Lo stato di ogni bifoglio', '', '| raggruppamento (dentro lo strato) | η² del punteggio dell\'asse | nullo | z |', '|---|---|---|---|']
    for k, v in r314['a'].items():
        md.append('| %s | %.3f | %.3f | %.1f |' % (k, v['eta2'], v['nullo'], v['z']))
    md += ['', 'Esito (a): **%s**; spiegano qualcosa anche: %s.' % (r314['esito_a'], ', '.join(r314['spiegano_anche']) or 'nessun altro'), '',
           'Caratteristiche più legate al bifoglio: %s.' % ', '.join('%s (η² %.2f, z %.1f)' % (x['caratteristica'], x['eta2'], x['z']) for x in r314['b']), '']
    for sz, v in r314['c'].items():
        md.append('- Sezione %s, %d bifogli: ordine spettrale contro il libro |ρ| %.2f (z %.1f); cambi di mano %d contro %.1f attesi (z %.1f). Ordine: %s.' % (
            sz, v['bifogli'], v['rho_con_il_libro'], v['z_rho'], v['cambi_di_mano'], v['cambi_attesi'], v['z_cambi'], ', '.join(v['ordine'])))
    md += ['', 'La mano segue lo stato in: %s.' % (', '.join(r314['la_mano_segue_lo_stato_in']) or 'nessuna sezione'), '',
           '## e315 — Lingue A e B nell\'erbario (%d pagine A, %d B)' % (r315['pagine_A'], r315['pagine_B']), '', '| caratteristica | d (B − A) | z |', '|---|---|---|']
    for x in r315['prime_20']:
        md.append('| %s | %+.2f | %.1f |' % (x['caratteristica'], x['d'], x['z']))
    md += ['', '| classificazione (validazione per bifoglio) | caratteristiche | AUC |', '|---|---|---|']
    for k, v in r315['classificazione'].items():
        md.append('| %s | %d | %.3f%s |' % (k, v['caratteristiche'], v['AUC'], (' (nullo %.3f, z %.1f)' % (v['nullo'], v['z'])) if 'z' in v else ''))
    md += ['', 'Esito e315: **%s**.' % r315['esito'], '', '## e318 — Fogli irregolari e fogli con le due facce diverse', '',
           '(a) Candidate con almeno un\'irregolarità fisica: %.0f%%; altre pagine: %.0f%%; p = %.3f. Esito: **%s**. Dettaglio: %s.' % (
               100 * r318['a']['quota_irregolari_candidate'], 100 * r318['a']['quota_irregolari_altre'], r318['a']['p'], r318['a']['esito'],
               '; '.join('%s: %s' % (p, ', '.join(k for k, v in f.items() if v) or 'nessuna') for p, f in r318['a']['candidate'].items())), '',
           '(b) %d fogli con recto e verso profilati (%d con un cambio di mano, lingua o sezione); correlazione media %.3f; differenza (con cambio − senza) %+.3f, z %.1f. Esito: **%s**.' % (
               r318['b']['fogli'], r318['b']['con_cambio'], r318['b']['correlazione_media'], r318['b']['differenza_cambio_meno_altri'], r318['b']['z'], r318['b']['esito']), '',
           'Fogli con le facce più diverse: %s.' % '; '.join('%s/%s %.2f (mani %s, strati %s)' % (x['recto'], x['verso'], x['correlazione'], x['mani'], x['strati'])
                                                             for x in r318['b']['dieci_fogli_con_facce_piu_diverse'])]
    open(os.path.join(RISULTATI, 'e314_bifogli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
