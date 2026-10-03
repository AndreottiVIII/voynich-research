# -*- coding: utf-8 -*-
"""Esperimento 300 (con l'e301): (e300) le pagine consecutive nella rilegatura si somigliano piu' di pagine qualsiasi della
stessa sezione? (e301) le mani 2 e 3 di Davis (lingua B) si distinguono per le abitudini fini di riga?

Preregistrazione: preregistrazioni/e300.md. Scrive risultati/e300_ordine_scribi.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_PAROLE, PERM = 40, 1000
GALLOWS = {'k', 't', 'p', 'f'}


def coseno(a, b):
    num = sum(a[w] * b[w] for w in a if w in b)
    den = math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    return num / den if den else 0.0


def ordine(pagine, rnd):
    """pagine: [(nome, sezione, parole)] in ordine. A, z, Spearman distanza-somiglianza, coppie meno simili."""
    freq = Counter(w for _, _, ws in pagine for w in ws)
    vett = [Counter(w for w in ws if 3 <= freq[w] <= 50) for _, _, ws in pagine]
    per_sez = defaultdict(list)
    for i, (_, s, _) in enumerate(pagine):
        per_sez[s].append(i)

    def A(ordini):
        cc = [coseno(vett[a], vett[b]) for idx in ordini.values() for a, b in zip(idx, idx[1:])]
        return statistics.mean(cc)
    vero = A(per_sez)
    nulli = []
    for _ in range(PERM):
        mes = {}
        for s, idx in per_sez.items():
            x = list(idx)
            rnd.shuffle(x)
            mes[s] = x
        nulli.append(A(mes))
    sd = statistics.pstdev(nulli)
    dist, sim = [], []
    for idx in per_sez.values():
        for i in range(len(idx)):
            for j in range(i + 1, min(len(idx), i + 21)):
                dist.append(j - i)
                sim.append(coseno(vett[idx[i]], vett[idx[j]]))

    def ranghi(x):
        o = sorted(range(len(x)), key=lambda i: x[i])
        r = [0] * len(x)
        for k, i in enumerate(o):
            r[i] = k
        return r
    sp = statistics.correlation(ranghi(dist), ranghi(sim)) if len(dist) > 2 else None
    coppie = sorted(((coseno(vett[a], vett[b]), pagine[a][0], pagine[b][0]) for idx in per_sez.values() for a, b in zip(idx, idx[1:])))[:8]
    return OrderedDict([('pagine', len(pagine)), ('A', vero), ('nullo', statistics.mean(nulli)), ('z', (vero - statistics.mean(nulli)) / sd if sd else None),
                        ('spearman_distanza_somiglianza', sp), ('coppie_consecutive_meno_simili', coppie)])


def caratteristiche(righe):
    """righe: [(parole)] di una pagina."""
    ini = [D(r[0])[0] for r in righe if r]
    t, k = sum(x == 't' for x in ini), sum(x == 'k' for x in ini)
    conc = []
    for r in righe:
        fin = [D(w)[-2] for w in r if len(D(w)) >= 2 and D(w)[-1] == 'y' and D(w)[-2] in ('d', 'e')]
        if len(fin) >= 2:
            conc.append(len(set(fin)) == 1)
    rima = [tuple(D(a)[-2:]) == tuple(D(b)[-2:]) for r in righe for a, b in zip(r, r[1:])]
    qo = [(D(w)[0] == 'q') for r in righe for w in r if len(D(w)) >= 3 and ((D(w)[0] == 'q' and D(w)[1] == 'o' and D(w)[2] in GALLOWS) or (D(w)[0] == 'o' and D(w)[1] in GALLOWS))]
    fine = [D(r[-1])[-1] in ('m', 'g') for r in righe if r]
    lung = [len(D(w)) for r in righe for w in r]
    m = lambda x: statistics.mean(x) if x else 0.0
    return [t / (t + k) if t + k else 0.5, m(conc), m(rima), m(qo), m(fine), m(lung)]


def classifica(X, y, rnd):
    n, d = len(X), len(X[0])
    mu = [statistics.mean(r[j] for r in X) for j in range(d)]
    sd = [statistics.pstdev(r[j] for r in X) or 1.0 for j in range(d)]
    Z = [[(r[j] - mu[j]) / sd[j] for j in range(d)] for r in X]

    def acc(etich):
        giusti = 0
        for i in range(n):
            cent = {}
            for c in set(etich):
                pts = [Z[k] for k in range(n) if k != i and etich[k] == c]
                if pts:
                    cent[c] = [statistics.mean(p[j] for p in pts) for j in range(d)]
            pred = min(cent, key=lambda c: sum((Z[i][j] - cent[c][j]) ** 2 for j in range(d)))
            giusti += pred == etich[i]
        return giusti / n
    vero = acc(y)
    nulli = []
    for _ in range(PERM):
        e = list(y)
        rnd.shuffle(e)
        nulli.append(acc(e))
    sd_ = statistics.pstdev(nulli)
    return OrderedDict([('pagine', n), ('accuratezza', vero), ('nullo', statistics.mean(nulli)), ('z', (vero - statistics.mean(nulli)) / sd_ if sd_ else None)])


def main():
    R = [r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    per = OrderedDict()
    for r in R:
        x = per.setdefault(r.pagina, {'sezione': r.sezione, 'mano': r.mano, 'lingua': r.lingua, 'righe': []})
        x['righe'].append([w for w in r.parole if trascrizione.pulita(w)])
    pagine = [(p, x['sezione'], [w for rr in x['righe'] for w in rr]) for p, x in per.items() if sum(len(rr) for rr in x['righe']) >= MIN_PAROLE]
    lat = [w.lower() for w in lingue.parole('Latin', max_caratteri=400000) if w.isalpha()]
    positivo = [('p%d' % i, 'Bibbia', lat[i * 170:(i + 1) * 170]) for i in range(200)]
    e300 = OrderedDict([('Voynich', ordine(pagine, random.Random(300))), ('controllo positivo: Bibbia latina in pagine', ordine(positivo, random.Random(300)))])
    for n, r in e300.items():
        print('e300 %-44s A %.4f nullo %.4f z %.1f | Spearman %.3f' % (n, r['A'], r['nullo'], r['z'] or 0, r['spearman_distanza_somiglianza'] or 0), flush=True)
    zv, zp = e300['Voynich']['z'] or 0, e300['controllo positivo: Bibbia latina in pagine']['z'] or 0
    esito300 = 'non valido' if zp <= 3 else ('ordine di rilegatura vicino a quello di scrittura' if zv > 3 else ('nessuna traccia d\'ordine' if zv < 1 else 'incerto'))
    sel = [(p, x) for p, x in per.items() if x['lingua'] == 'B' and x['mano'] in ('2', '3') and sum(len(rr) for rr in x['righe']) >= MIN_PAROLE]
    X = [caratteristiche(x['righe']) for _, x in sel]
    y = [x['mano'] for _, x in sel]
    rnd = random.Random(301)
    tutto = classifica(X, y, rnd)
    sez = Counter((x['sezione'], x['mano']) for _, x in sel)
    strati = OrderedDict()
    for s in sorted({x['sezione'] for _, x in sel}):
        if sez[(s, '2')] >= 5 and sez[(s, '3')] >= 5:
            idx = [i for i, (_, x) in enumerate(sel) if x['sezione'] == s]
            strati[s] = classifica([X[i] for i in idx], [y[i] for i in idx], rnd)
    zz = tutto['z'] or 0
    esito301 = ('mani distinguibili' if zz > 3 else ('no' if zz < 2 else 'incerto')) + ('' if strati else ' (mano e sezione non si separano: nessuna sezione con 5 pagine di ciascuna mano)')
    print('e301 mani 2 e 3: %s | strati %s | sezioni per mano %s' % (dict(tutto), {s: round(v['z'] or 0, 1) for s, v in strati.items()}, dict(sez)), flush=True)
    json.dump(OrderedDict([('e300', e300), ('e300_esito', esito300), ('e301', OrderedDict([('tutte', tutto), ('per_sezione', strati), ('sezioni_per_mano', {'%s %s' % k: v for k, v in sez.items()}),
               ('esito', esito301)]))]), open(os.path.join(RISULTATI, 'e300_ordine_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e300 ed e301 — Ordine delle pagine; scribi di Davis', '', 'Preregistrazione: `preregistrazioni/e300.md`.', '', '## e300', '',
          '| testo | pagine | A (consecutive) | nullo | z | Spearman distanza-somiglianza |', '|---|---|---|---|---|---|']
    for n, r in e300.items():
        md.append('| %s | %d | %.4f | %.4f | %.1f | %.3f |' % (n, r['pagine'], r['A'], r['nullo'], r['z'] or 0, r['spearman_distanza_somiglianza'] or 0))
    md += ['', 'Coppie consecutive meno simili nel Voynich: ' + '; '.join('%s–%s (%.3f)' % (a, b, c) for c, a, b in e300['Voynich']['coppie_consecutive_meno_simili']) + '.',
           '', 'Esito e300: **%s**.' % esito300, '', '## e301', '',
           'Mani 2 e 3 (lingua B), %d pagine: accuratezza %.3f contro %.3f del nullo, z %.1f. Per sezione: %s. Sezioni per mano: %s.' % (
               tutto['pagine'], tutto['accuratezza'], tutto['nullo'], zz, ', '.join('%s z %.1f' % (s, v['z'] or 0) for s, v in strati.items()) or 'nessuna sezione con entrambe',
               ', '.join('%s %s: %d' % (k[0], k[1], v) for k, v in sorted(sez.items()))), '', 'Esito e301: **%s**.' % esito301]
    open(os.path.join(RISULTATI, 'e300_ordine_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito300, '|', esito301)


if __name__ == '__main__':
    main()
