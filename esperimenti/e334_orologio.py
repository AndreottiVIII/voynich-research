# -*- coding: utf-8 -*-
"""Esperimenti 334, 335, 336. (e334) gli argomenti LDA dei paragrafi dell'erbario A sono piu' netti che su paragrafi
rimescolati? (e335) la quota di -ey come orologio: il verso ne ha piu' del recto? il foglio seguente piu' del verso?
(e336) la crescita di -ey sta dentro il paragrafo o fra i paragrafi?

Preregistrazione: preregistrazioni/e334.md. Scrive risultati/e334_orologio.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e308_libro_fisico as e308
import e328_livelli as e328

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
SCELTE = OrderedDict([('-dy/-ey', 4), ('-l/-r', 2), ('k/t', 1)])


def quota(ws, j=4):
    n, l = e328.scelte(ws)[j]
    return (l / n if n else None), n


def segno_flip(d, rnd):
    v = statistics.mean(d)
    nul = [statistics.mean(x * rnd.choice((-1, 1)) for x in d) for _ in range(PERM)]
    return v, (v - statistics.mean(nul)) / (statistics.pstdev(nul) or 1)


def e334(pag, rnd):
    from sklearn.decomposition import LatentDirichletAllocation
    meta = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        meta.setdefault(r.pagina, (r.sezione or '?', r.lingua or '?'))
    par = []
    for p, pars in pag.items():
        if meta.get(p) != ('H', 'A'):
            continue
        for x in pars:
            orig = [w for _, r_ in x for w in r_]
            if len(orig) >= 20:
                par.append(([e328.normalizza(w) for w in orig], orig))
    cnt = Counter(w for ws, _ in par for w in ws)
    frequenti = {w for w, _ in cnt.most_common(30)}
    voc = sorted(w for w, n in cnt.items() if n >= 5 and w not in frequenti)
    idx = {w: k for k, w in enumerate(voc)}

    def matrice(liste):
        M = np.zeros((len(liste), len(voc)))
        for i, ws in enumerate(liste):
            for w in ws:
                if w in idx:
                    M[i, idx[w]] += 1
        return M

    def conc(liste):
        M = matrice(liste)
        lda = LatentDirichletAllocation(n_components=6, random_state=332, learning_method='batch', max_iter=100).fit(M)
        th = lda.transform(M)
        return float(th.max(1).mean()), th
    vero, th = conc([ws for ws, _ in par])
    nul = []
    for _ in range(50):
        tutte = [w for ws, _ in par for w in ws]
        rnd.shuffle(tutte)
        liste, i = [], 0
        for ws, _ in par:
            liste.append(tutte[i:i + len(ws)])
            i += len(ws)
        nul.append(conc(liste)[0])
    z = (vero - statistics.mean(nul)) / statistics.pstdev(nul)
    esito = 'argomenti reali' if z > 3 else ('rumore' if z < 2 else 'incerto')
    ey = [quota(orig)[0] for _, orig in par]
    corr = []
    for t in range(6):
        xs = [(a, b) for a, b in zip(th[:, t], ey) if b is not None]
        corr.append(float(np.corrcoef([a for a, _ in xs], [b for _, b in xs])[0, 1]))
    return OrderedDict([('paragrafi', len(par)), ('concentrazione', vero), ('nullo', statistics.mean(nul)), ('z', z), ('esito', esito),
                        ('correlazione_argomenti_quota_ey', corr)])


def e335(pag, testa, rnd):
    parole = {p: [w for par in pars for _, ws in par for w in ws] for p, pars in pag.items()}
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seg = dict(zip(ordine, ordine[1:]))

    def q(p):
        v, n = quota(parole[p])
        return v if n >= 5 else None
    fogli, aperture = [], []
    for p in pag:
        h, s = testa.get(p), seg.get(p)
        if not h or not s or s not in pag:
            continue
        a, b = q(p), q(s)
        if a is None or b is None:
            continue
        if h['lato'] == 'r' and testa[s]['lato'] == 'v' and testa[s]['F'] == h['F']:
            fogli.append(b - a)
        elif h['lato'] == 'v' and testa[s]['lato'] == 'r':
            aperture.append(b - a)
    vf, zf = segno_flip(fogli, rnd)
    va, za = segno_flip(aperture, rnd)
    esito_f = 'il verso viene dopo il recto' if zf > 3 else ('la crescita è solo di posizione nella pagina' if abs(zf) < 2 else 'incerto')
    esito_a = 'l\'ordine dei fogli segue il tempo di scrittura' if za > 3 else ('no' if abs(za) < 2 else 'incerto')
    return OrderedDict([('fogli', OrderedDict([('coppie', len(fogli)), ('verso_meno_recto', vf), ('z', zf), ('esito', esito_f)])),
                        ('aperture', OrderedDict([('coppie', len(aperture)), ('recto_seguente_meno_verso', va), ('z', za), ('esito', esito_a)]))])


def e336(pag, rnd):
    out = OrderedDict()
    for nome, j in SCELTE.items():
        dentro, fra = [], []
        for p, pars in pag.items():
            prec = None
            for par in pars:
                righe = [ws for _, ws in par]
                if len(righe) >= 6:
                    h = len(righe) // 2
                    a, na = quota([w for ws in righe[:h] for w in ws], j)
                    b, nb = quota([w for ws in righe[h:] for w in ws], j)
                    if na >= 3 and nb >= 3:
                        dentro.append(b - a)
                v, n = quota([w for ws in righe for w in ws], j)
                cur = v if n >= 3 else None
                if prec is not None and cur is not None:
                    fra.append(cur - prec)
                prec = cur
        vd, zd = segno_flip(dentro, rnd)
        vf, zf = segno_flip(fra, rnd)
        out[nome] = OrderedDict([('dentro', OrderedDict([('paragrafi', len(dentro)), ('seconda_meno_prima', vd), ('z', zd)])),
                                 ('fra', OrderedDict([('coppie', len(fra)), ('seguente_meno_precedente', vf), ('z', zf)]))])
    e = out['-dy/-ey']
    esiti = [x for x, ok in (('deriva dentro il paragrafo', e['dentro']['z'] > 3), ('deriva fra paragrafi', e['fra']['z'] > 3)) if ok]
    esito = ', '.join(esiti) if esiti else ('nessuna' if abs(e['dentro']['z']) < 2 and abs(e['fra']['z']) < 2 else 'incerto')
    return OrderedDict([('scelte', out), ('esito', esito)])


def main():
    pag = e328.carica()
    testa = e308.intestazioni()
    r335 = e335(pag, testa, random.Random(335))
    print('e335', {k: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} for k, v in r335.items()}, flush=True)
    r336 = e336(pag, random.Random(336))
    print('e336', r336['esito'], {k: {a: (b['z'] and round(b['z'], 1)) for a, b in v.items()} for k, v in r336['scelte'].items()}, flush=True)
    r334 = e334(pag, random.Random(334))
    print('e334', r334['esito'], round(r334['concentrazione'], 3), round(r334['nullo'], 3), round(r334['z'], 1), [round(c, 2) for c in r334['correlazione_argomenti_quota_ey']], flush=True)
    json.dump(OrderedDict([('e334', r334), ('e335', r335), ('e336', r336)]), open(os.path.join(RISULTATI, 'e334_orologio.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e334, e335, e336 — Argomenti veri?; -ey come orologio; la deriva nel paragrafo', '', 'Preregistrazione: `preregistrazioni/e334.md`.', '',
          '## e334', '', '%d paragrafi dell\'erbario A. Concentrazione dell\'argomento dominante %.3f contro %.3f su paragrafi rimescolati, z %.1f. Esito: **%s**.' % (
              r334['paragrafi'], r334['concentrazione'], r334['nullo'], r334['z'], r334['esito']),
          'Correlazione fra il peso di ogni argomento e la quota di -ey del paragrafo: %s.' % ', '.join('%+.2f' % c for c in r334['correlazione_argomenti_quota_ey']), '',
          '## e335', '', '- Fogli (verso − recto, quota di -ey): %+.3f su %d fogli, z %.1f: **%s**.' % (r335['fogli']['verso_meno_recto'], r335['fogli']['coppie'], r335['fogli']['z'], r335['fogli']['esito']),
          '- Aperture (recto seguente − verso): %+.3f su %d, z %.1f: **%s**.' % (r335['aperture']['recto_seguente_meno_verso'], r335['aperture']['coppie'], r335['aperture']['z'], r335['aperture']['esito']),
          '', '## e336', '', '| scelta | dentro il paragrafo (seconda metà − prima) | z | fra paragrafi (seguente − precedente) | z |', '|---|---|---|---|---|']
    for k, v in r336['scelte'].items():
        md.append('| %s | %+.3f (%d) | %.1f | %+.3f (%d) | %.1f |' % (k, v['dentro']['seconda_meno_prima'], v['dentro']['paragrafi'], v['dentro']['z'], v['fra']['seguente_meno_precedente'], v['fra']['coppie'], v['fra']['z']))
    md += ['', 'Esito e336 (per -ey): **%s**.' % r336['esito']]
    open(os.path.join(RISULTATI, 'e334_orologio.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
