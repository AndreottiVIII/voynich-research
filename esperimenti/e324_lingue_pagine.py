# -*- coding: utf-8 -*-
"""Esperimenti 324, 325, 326. (e324) nelle pagine miste dell'erbario A e B si mescolano nella riga o si alternano per
righe? (e325) le etichette A/B di Currier contro un classificatore sul lessico; (e326) lo stato cambia fra la meta' alta e
la meta' bassa della pagina?

Preregistrazione: preregistrazioni/e324.md. Scrive risultati/e324_lingue_pagine.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e320_parole as e320

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def pagine_e_righe():
    """{pagina: {'sezione', 'lingua', 'mano', 'righe': [[parole]], 'parole': [...]}} nell'ordine del libro."""
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                x = out.setdefault(r.pagina, {'sezione': r.sezione or '?', 'lingua': r.lingua or '?', 'mano': r.mano or '?', 'righe': [], 'parole': []})
                x['righe'].append(ws)
                x['parole'] += ws
    return out


def parole_caratteristiche(pag, testa):
    """Per ogni pagina dell'erbario A/B: (insieme A, insieme B) scelti sull'altra meta' dei bifogli; per le altre pagine
    gli insiemi scelti su tutto l'erbario."""
    herb = [p for p, x in pag.items() if x['sezione'] == 'H' and x['lingua'] in ('A', 'B') and len(x['parole']) >= 60]
    bif = lambda p: (testa.get(p, {}).get('Q'), testa.get(p, {}).get('B'))
    bifs = sorted({bif(p) for p in herb}, key=str)
    meta = {b: k % 2 for k, b in enumerate(bifs)}
    conv = lambda ps: [{'parole': pag[p]['parole']} for p in ps]
    scelte = {}
    for f in (0, 1):
        a, b, _ = e320.caratteristiche_AB(conv([p for p in herb if meta[bif(p)] == f and pag[p]['lingua'] == 'A']),
                                          conv([p for p in herb if meta[bif(p)] == f and pag[p]['lingua'] == 'B']))
        scelte[f] = (set(a), set(b))
    a, b, _ = e320.caratteristiche_AB(conv([p for p in herb if pag[p]['lingua'] == 'A']), conv([p for p in herb if pag[p]['lingua'] == 'B']))
    tutte = (set(a), set(b))
    return {p: (scelte[1 - meta[bif(p)]] if p in herb else tutte) for p in pag}, set(herb)


def varianza_righe(righe_lab):
    """righe_lab: lista di liste di etichette 1 (A) / 0 (B). Varianza fra righe dell'indice-A, pesata sulle occorrenze."""
    tutte = [x for r in righe_lab for x in r]
    m = statistics.mean(tutte)
    return sum(len(r) * (statistics.mean(r) - m) ** 2 for r in righe_lab) / len(tutte)


def gruppo_V(pagine_lab, rnd):
    vero = statistics.mean(varianza_righe(r) for r in pagine_lab)
    nul = []
    for _ in range(PERM):
        vs = []
        for righe in pagine_lab:
            tutte = [x for r in righe for x in r]
            rnd.shuffle(tutte)
            out, i = [], 0
            for r in righe:
                out.append(tutte[i:i + len(r)])
                i += len(r)
            vs.append(varianza_righe(out))
        nul.append(statistics.mean(vs))
    return OrderedDict([('pagine', len(pagine_lab)), ('V', vero), ('nullo', statistics.mean(nul)), ('z', (vero - statistics.mean(nul)) / statistics.pstdev(nul))])


def e324(pag, insiemi, herb, rnd):
    def etichette(p):
        sA, sB = insiemi[p]
        righe = []
        for ws in pag[p]['righe']:
            r = [1 if w in sA else 0 for w in ws if w in sA or w in sB]
            if len(r) >= 2:
                righe.append(r)
        return righe

    def indice(p):
        sA, sB = insiemi[p]
        na = sum(w in sA for w in pag[p]['parole'])
        nb = sum(w in sB for w in pag[p]['parole'])
        return na / (na + nb) if na + nb >= 10 else None
    idx = {p: indice(p) for p in herb}
    miste = [p for p in herb if idx[p] is not None and 0.30 <= idx[p] <= 0.65]
    pureA = [p for p in herb if idx[p] is not None and idx[p] > 0.75]
    pureB = [p for p in herb if idx[p] is not None and idx[p] < 0.15]
    lab = {p: etichette(p) for p in miste + pureA + pureB}
    ok = lambda ps: [lab[p] for p in ps if len(lab[p]) >= 4]
    finte = []
    for _ in range(20):
        a, b = rnd.choice(pureA), rnd.choice(pureB)
        la, lb = lab[a], lab[b]
        alt = [x for pair in zip(la, lb) for x in pair]
        if len(alt) >= 4:
            finte.append(alt)
    out = OrderedDict([('miste', gruppo_V(ok(miste), rnd)), ('pure', gruppo_V(ok(pureA + pureB), rnd)), ('controllo positivo: righe alternate', gruppo_V(finte, rnd))])
    z = out['miste']['z']
    esito = 'righe alternate' if z > 3 else ('mescolate nella riga' if z < 2 else 'incerto')
    elenco = [(p, pag[p]['lingua'], round(idx[p], 2)) for p in miste]
    return OrderedDict([('gruppi', out), ('esito', esito), ('pagine_miste', elenco)])


def e325(pag, testa, rnd):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    pp = [p for p, x in pag.items() if len(x['parole']) >= 60]
    herb = [p for p in pp if pag[p]['sezione'] == 'H' and pag[p]['lingua'] in ('A', 'B')]
    top = [w for w, _ in Counter(w for p in herb for w in pag[p]['parole']).most_common(100)]
    feat = lambda p: [Counter(pag[p]['parole'])[w] / len(pag[p]['parole']) for w in top]
    Xh = np.array([feat(p) for p in herb])
    yh = np.array([1 if pag[p]['lingua'] == 'B' else 0 for p in herb])
    gr = np.array([hash((testa.get(p, {}).get('Q'), testa.get(p, {}).get('B'))) for p in herb])
    mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
    prob = dict(zip(herb, cross_val_predict(mdl, Xh, yh, cv=GroupKFold(n_splits=5), groups=gr, method='predict_proba')[:, 1]))
    mdl.fit(Xh, yh)
    altre = [p for p in pp if p not in prob]
    if altre:
        prob.update(zip(altre, mdl.predict_proba(np.array([feat(p) for p in altre]))[:, 1]))
    disacc, senza, per_sez = [], [], defaultdict(lambda: [0, 0])
    for p in pp:
        pb, lg, sz = float(prob[p]), pag[p]['lingua'], pag[p]['sezione']
        if lg in ('A', 'B') and (pb < 0.2 or pb > 0.8):
            accordo = (pb > 0.8) == (lg == 'B')
            per_sez[sz][0] += accordo
            per_sez[sz][1] += 1
            if not accordo:
                disacc.append((p, sz, lg, round(pb, 2)))
        if lg not in ('A', 'B'):
            senza.append((p, sz, round(pb, 2)))
    acc_h = per_sez['H'][0] / per_sez['H'][1] if per_sez['H'][1] else None
    esito = 'etichette confermate' if (acc_h is not None and acc_h >= 0.95) else 'etichette non tutte confermate'
    return OrderedDict([('pagine', len(pp)), ('accordo_per_sezione', OrderedDict((s, OrderedDict([('accordo', a / n if n else None), ('pagine_sicure', n)])) for s, (a, n) in sorted(per_sez.items(), key=str))),
                        ('accordo_erbario', acc_h), ('esito', esito), ('disaccordi', disacc), ('senza_etichetta', senza)])


def e326(pag, rnd):
    def riga_stat(ws):
        u = [D(w) for w in ws]
        return (Counter(g for x in u for g in x), len(u), sum(x[-1] == 'y' for x in u), sum(x[-1] == 'n' for x in u))

    def somma(rs):
        segni, n, fy, fn = Counter(), 0, 0, 0
        for c, a, b, d in rs:
            segni.update(c)
            n += a
            fy += b
            fn += d
        tot = sum(segni.values())
        return {'e': segni['e'] / tot, 'a': segni['a'] / tot, 'n': segni['n'] / tot, 'fy': fy / n, 'fn': fn / n}, segni
    pp = [p for p, x in pag.items() if len(x['parole']) >= 60]
    st = {p: [riga_stat(ws) for ws in pag[p]['righe']] for p in pp}
    vals = [somma(st[p])[0] for p in pp]
    mu = {k: statistics.mean(v[k] for v in vals) for k in vals[0]}
    sd = {k: statistics.pstdev(v[k] for v in vals) for k in vals[0]}
    punteggio = lambda v: (v['e'] - mu['e']) / sd['e'] + (v['fy'] - mu['fy']) / sd['fy'] - (v['a'] - mu['a']) / sd['a'] - (v['n'] - mu['n']) / sd['n'] - (v['fn'] - mu['fn']) / sd['fn']

    def jsd(c1, c2):
        t1, t2 = sum(c1.values()), sum(c2.values())
        out = 0.0
        for k in set(c1) | set(c2):
            a, b = c1[k] / t1, c2[k] / t2
            m = (a + b) / 2
            out += (a * math.log2(a / m) if a else 0) + (b * math.log2(b / m) if b else 0)
        return out / 2
    lunghe = [p for p in pp if len(pag[p]['righe']) >= 16]

    def misura(div):
        d1, d2 = [], []
        for alta, bassa in div:
            sa, ca = somma(alta)
            sb, cb = somma(bassa)
            d1.append(abs(punteggio(sa) - punteggio(sb)))
            d2.append(jsd(ca, cb))
        return statistics.mean(d1), statistics.mean(d2), d1
    vere = []
    for p in lunghe:
        r = st[p]
        h = len(r) // 2
        vere.append((r[:h], r[h:]))
    v1, v2, per_pag = misura(vere)
    n1, n2 = [], []
    for _ in range(PERM):
        div = []
        for p in lunghe:
            r = list(st[p])
            rnd.shuffle(r)
            h = len(r) // 2
            div.append((r[:h], r[h:]))
        a, b, _ = misura(div)
        n1.append(a)
        n2.append(b)
    z1 = (v1 - statistics.mean(n1)) / statistics.pstdev(n1)
    z2 = (v2 - statistics.mean(n2)) / statistics.pstdev(n2)
    esito = 'lo stato cambia dentro la pagina' if (z1 > 3 or z2 > 3) else ('costante' if (z1 < 2 and z2 < 2) else 'incerto')
    peggiori = sorted(zip(lunghe, per_pag), key=lambda t: -t[1])[:10]
    return OrderedDict([('pagine', len(lunghe)), ('D1', v1), ('nullo_D1', statistics.mean(n1)), ('z_D1', z1), ('D2', v2), ('nullo_D2', statistics.mean(n2)), ('z_D2', z2),
                        ('esito', esito), ('pagine_con_differenza_maggiore', [(p, pag[p]['sezione'], pag[p]['lingua'], round(d, 2)) for p, d in peggiori])])


def main():
    pag = pagine_e_righe()
    testa = e308.intestazioni()
    insiemi, herb = parole_caratteristiche(pag, testa)
    r324 = e324(pag, insiemi, herb, random.Random(324))
    print('e324', r324['esito'], {k: (v['pagine'], round(v['V'], 4), round(v['nullo'], 4), round(v['z'], 1)) for k, v in r324['gruppi'].items()}, flush=True)
    r325 = e325(pag, testa, random.Random(325))
    print('e325', r325['esito'], r325['accordo_erbario'], len(r325['disaccordi']), r325['disaccordi'][:12], flush=True)
    r326 = e326(pag, random.Random(326))
    print('e326', r326['esito'], round(r326['z_D1'], 1), round(r326['z_D2'], 1), flush=True)
    json.dump(OrderedDict([('e324', r324), ('e325', r325), ('e326', r326)]), open(os.path.join(RISULTATI, 'e324_lingue_pagine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e324, e325, e326 — Zona di passaggio A/B; riclassificare le pagine; lo stato dentro la pagina', '', 'Preregistrazione: `preregistrazioni/e324.md`.', '',
          '## e324', '', '| pagine | numero | V (varianza fra righe dell\'indice-A) | nullo | z |', '|---|---|---|---|---|']
    for k, v in r324['gruppi'].items():
        md.append('| %s | %d | %.4f | %.4f | %.1f |' % (k, v['pagine'], v['V'], v['nullo'], v['z']))
    md += ['', 'Esito e324: **%s**. Pagine miste: %s.' % (r324['esito'], ', '.join('%s (%s, %.2f)' % x for x in r324['pagine_miste'])), '', '## e325', '',
           'Accordo con Currier fra le previsioni sicure: %s.' % '; '.join('%s %s su %d' % (s, ('%.0f%%' % (100 * v['accordo'])) if v['accordo'] is not None else '-', v['pagine_sicure'])
                                                                         for s, v in r325['accordo_per_sezione'].items()),
           'Esito e325: **%s**.' % r325['esito'], '', 'Disaccordi (pagina, sezione, etichetta, P(B)): %s.' % (', '.join('%s %s-%s %.2f' % d for d in r325['disaccordi']) or 'nessuno'),
           '', 'Pagine senza etichetta: %s.' % (', '.join('%s %s P(B) %.2f' % x for x in r325['senza_etichetta']) or 'nessuna'), '', '## e326', '',
           '%d pagine con almeno 16 righe. Metà alta contro metà bassa: differenza del punteggio dell\'asse %.2f (nullo %.2f, z %.1f); distanza fra i segni %.4f (nullo %.4f, z %.1f). Esito: **%s**.' % (
               r326['pagine'], r326['D1'], r326['nullo_D1'], r326['z_D1'], r326['D2'], r326['nullo_D2'], r326['z_D2'], r326['esito']), '',
           'Pagine con la differenza maggiore: %s.' % ', '.join('%s (%s-%s, %.2f)' % x for x in r326['pagine_con_differenza_maggiore'])]
    open(os.path.join(RISULTATI, 'e324_lingue_pagine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
