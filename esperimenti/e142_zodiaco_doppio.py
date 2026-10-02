# -*- coding: utf-8 -*-
"""Esperimento 142: le etichette delle due pagine dell'Ariete e delle due del Toro si somigliano piu' di quelle di altre
coppie di pagine zodiacali consecutive?

Preregistrazione: preregistrazioni/e142.md. Scrive risultati/e142_zodiaco_doppio.json e .md.
"""
import itertools, json, math, os, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
ORDINE = ['f70v2', 'f70v1', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3', 'f72v3', 'f72v2', 'f72v1', 'f73r', 'f73v']
STESSO = {('f70v1', 'f71r'), ('f71v', 'f72r1')}


def parole(zl, pag, tipi):
    return [w for r in zl if r.pagina == pag and r.tipo and r.tipo[0] in tipi for w in r.parole if trascrizione.pulita(w)]


def bigrammi(ws):
    c = Counter()
    for w in ws:
        u = ['^'] + D(w) + ['$']
        c.update(zip(u, u[1:]))
    return c


def coseno(a, b):
    num = sum(a[k] * b[k] for k in a if k in b)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def main():
    zl = trascrizione.leggi('ZL')
    et = {p: parole(zl, p, 'L') for p in ORDINE}
    tutto = {p: parole(zl, p, 'LC') for p in ORDINE}
    coppie = list(zip(ORDINE, ORDINE[1:]))
    misure_ = OrderedDict([
        ('(1) coseno dei bigrammi, etichette', lambda a, b: coseno(bigrammi(et[a]), bigrammi(et[b]))),
        ('(2) Jaccard dei tipi, etichette', lambda a, b: jaccard(et[a], et[b])),
        ('(3) coseno dei bigrammi, etichette + cerchi', lambda a, b: coseno(bigrammi(tutto[a]), bigrammi(tutto[b])))])
    ris = OrderedDict([('etichette_per_pagina', {p: len(et[p]) for p in ORDINE})])
    for nome, f in misure_.items():
        val = {c: f(*c) for c in coppie}
        stessi = [val[c] for c in coppie if c in STESSO]
        media = statistics.mean(stessi)
        scelte = list(itertools.combinations(coppie, 2))
        p = sum(statistics.mean([val[x], val[y]]) >= media - 1e-12 for x, y in scelte) / len(scelte)
        ris[nome] = OrderedDict([('coppie', OrderedDict(('%s-%s%s' % (a, b, ' (stesso segno)' if (a, b) in STESSO else ''), v) for (a, b), v in val.items())),
                                 ('media_stesso_segno', media), ('media_altre', statistics.mean(v for c, v in val.items() if c not in STESSO)), ('p', p)])
        r = ris[nome]
        print('%-46s stesso segno %.3f | altre %.3f | p %.3f | %s' % (nome, media, r['media_altre'], p,
                                                                   ' '.join('%s %.3f' % (k.replace(' (stesso segno)', '*'), v) for k, v in r['coppie'].items())), flush=True)
    p1 = ris['(1) coseno dei bigrammi, etichette']['p']
    p23 = min(ris['(2) Jaccard dei tipi, etichette']['p'], ris['(3) coseno dei bigrammi, etichette + cerchi']['p'])
    esito = p1 <= 1 / 55 + 1e-12 and p23 <= 0.1
    ris['etichette_dipendono_dal_segno'] = esito
    print('le etichette dipendono dal segno:', esito)
    with open(os.path.join(RISULTATI, 'e142_zodiaco_doppio.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e142 — Le etichette dei segni zodiacali doppi si somigliano?', '', 'Coppie di pagine zodiacali consecutive (11); le due dello stesso segno sono '
           'f70v1–f71r (Ariete) e f71v–f72r1 (Toro). Nullo esatto: 55 scelte di 2 coppie. Preregistrazione: `preregistrazioni/e142.md`.', '',
           '| misura | stesso segno (media) | altre coppie (media) | p |', '|---|---|---|---|']
    for nome in misure_:
        r = ris[nome]
        out.append('| %s | %.3f | %.3f | %.3f |' % (nome, r['media_stesso_segno'], r['media_altre'], r['p']))
    out += ['', '| coppia | ' + ' | '.join(misure_) + ' |', '|---|' + '---|' * len(misure_)]
    for k in ris['(1) coseno dei bigrammi, etichette']['coppie']:
        out.append('| %s | %s |' % (k, ' | '.join('%.3f' % ris[n]['coppie'][k] for n in misure_)))
    out += ['', 'Le etichette dipendono dal segno: **%s**.' % ('sì' if esito else 'no')]
    with open(os.path.join(RISULTATI, 'e142_zodiaco_doppio.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
