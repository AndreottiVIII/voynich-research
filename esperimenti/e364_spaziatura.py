# -*- coding: utf-8 -*-
"""Esperimento 364: la dispersione fra i bifogli delle forme nuove sta in quelle con una giuntura di parola (spaziatura)
o in quelle senza (inventiva)? Legame con la lunghezza media delle parole del bifoglio.

Preregistrazione: preregistrazioni/e364.md. Scrive risultati/e364_spaziatura.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def main():
    rnd = random.Random(364)
    testa = e308.intestazioni()
    righe, tok = [], []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append(ws)
                if testa.get(r.pagina, {}).get('Q'):
                    b = (testa[r.pagina]['Q'], testa[r.pagina]['B'])
                    st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
                    tok += [(b, st, w) for w in ws]
    freq = Counter(w for r in righe for w in r)
    U = {w: tuple(D(w)) for w in freq}
    sim = e350.simili_globali(set(freq))
    fra, dentro = Counter(), Counter()
    for r in righe:
        for a, b in zip(r, r[1:]):
            fra[(U[a][-1], U[b][0])] += 1
    for r in righe:
        for w in r:
            if freq[w] >= 2:
                u = U[w]
                for i in range(len(u) - 1):
                    dentro[(u[i], u[i + 1])] += 1
    nf, nd = sum(fra.values()), sum(dentro.values())
    confine = {k for k, c in fra.items() if c >= 20 and (c / nf) >= 5 * ((dentro[k] + 0.5) / nd)}
    giunt = lambda w: any((U[w][i], U[w][i + 1]) in confine for i in range(1, len(U[w]) - 2))
    cat = {}
    for w, n in freq.items():
        if n == 1 and len(U[w]) >= 3 and not any(freq[v] >= 20 for v in sim[w] if v != w):
            cat[w] = 'con giuntura' if giunt(w) else 'senza giuntura'
    bif = defaultdict(list)
    for b, st, w in tok:
        bif[b].append((st, w))
    grandi = [b for b, xs in bif.items() if len(xs) >= 150]
    st_b = {b: Counter(x[0] for x in bif[b]).most_common(1)[0][0] for b in grandi}
    per_st = defaultdict(list)
    for b in grandi:
        per_st[st_b[b]].append(b)
    etich = {b: [cat.get(w, '-') for _, w in bif[b]] for b in grandi}

    def var(e, c):
        tot = []
        for st, bs in per_st.items():
            if len(bs) < 2:
                continue
            q = {b: sum(x == c for x in e[b]) / len(e[b]) for b in bs}
            m = statistics.mean(q.values())
            tot += [q[b] - m for b in bs]
        return statistics.mean(x * x for x in tot)
    cats = ['con giuntura', 'senza giuntura']
    vero = {c: var(etich, c) for c in cats}
    nul = {c: [] for c in cats}
    for _ in range(PERM):
        e2 = {}
        for st, bs in per_st.items():
            tutte = [x for b in bs for x in etich[b]]
            rnd.shuffle(tutte)
            i = 0
            for b in bs:
                n = len(etich[b])
                e2[b] = tutte[i:i + n]
                i += n
        for c in cats:
            nul[c].append(var(e2, c))
    res = OrderedDict()
    for c in cats:
        m, sd = statistics.mean(nul[c]), statistics.pstdev(nul[c])
        res[c] = OrderedDict([('varianza_scarti', vero[c]), ('nullo', m), ('rapporto', vero[c] / m if m else None), ('z', (vero[c] - m) / sd if sd else 0.0)])
    from scipy.stats import spearmanr
    lun = [statistics.mean(len(U[w]) for _, w in bif[b] if w not in cat) for b in grandi]
    qg = [sum(x == 'con giuntura' for x in etich[b]) / len(etich[b]) for b in grandi]
    rho = spearmanr(lun, qg).correlation
    nr = [spearmanr(lun, rnd.sample(qg, len(qg))).correlation for _ in range(PERM)]
    zr = (rho - statistics.mean(nr)) / statistics.pstdev(nr)
    zg, zs = res['con giuntura']['z'], res['senza giuntura']['z']
    if zg > 3 and zs > 3:
        esito = 'tutte e due'
    elif zg > 3 and zs < 2:
        esito = 'l\'inventiva è soprattutto spaziatura'
    elif zs > 3 and zg < 2:
        esito = 'inventiva vera'
    else:
        esito = 'incerto'
    out = OrderedDict([('bifogli', len(grandi)), ('coppie_di_confine', len(confine)), ('dispersione', res), ('spearman_lunghezza_giunture', rho), ('z_spearman', zr), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e364_spaziatura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e364 — L\'"inventiva" delle sessioni è un\'abitudine di spaziatura?', '', 'Preregistrazione: `preregistrazioni/e364.md`. %d bifogli.' % len(grandi), '',
          '| forme nuove | dispersione fra bifogli, rapporto sul nullo | z |', '|---|---|---|']
    for c, v in res.items():
        md.append('| %s | %.2f | %.1f |' % (c, v['rapporto'], v['z']))
    md += ['', 'Spearman fra lunghezza media delle parole del bifoglio e quota di forme nuove con giuntura: %.3f, z %.1f.' % (rho, zr), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e364_spaziatura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
