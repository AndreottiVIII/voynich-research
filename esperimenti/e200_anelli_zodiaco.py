# -*- coding: utf-8 -*-
"""Esperimento 200: informazione fra prefisso delle etichette zodiacali e anello (esterno/medio/interno), con
rimescolamento dentro la pagina.

Preregistrazione: preregistrazioni/e200.md. Scrive risultati/e200_anelli_zodiaco.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e183_etichette_oggetti as e183

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 200, 2000
D = misure.divisore(misure.GLIFI_EVA)


def etichette():
    per = defaultdict(list)
    anello = defaultdict(int)
    for r in trascrizione.leggi('ZL'):
        if r.sezione != 'Z' or not r.tipo:
            continue
        if r.tipo.startswith('C'):
            anello[r.pagina] += 1
        elif r.tipo == 'Lz':
            ps = [w for w in r.parole if trascrizione.pulita(w)]
            if ps and anello[r.pagina] >= 1:
                per[r.pagina].append((anello[r.pagina], ps[0]))
    out = []
    for pag, v in per.items():
        mx = max(a for a, _ in v)
        if mx < 2:
            continue
        for a, w in v:
            cat = 'esterno' if a == 1 else ('interno' if a == mx else 'medio')
            out.append((pag, cat, w))
    return out


def stat(dati):
    return e183.im([(''.join(D(w)[:2]), c) for _, c, w in dati])


def main():
    rnd = random.Random(SEME)
    dati = etichette()
    vero = stat(dati)
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(dati):
        per[p].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        cat = [c for _, c, _ in dati]
        for idx in per.values():
            x = [cat[i] for i in idx]
            rnd.shuffle(x)
            for i, y in zip(idx, x):
                cat[i] = y
        nulli.append(stat([(p, c, w) for (p, _, w), c in zip(dati, cat)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    z = (vero - m) / s if s else None
    p = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    esito = 'preferenze d\'anello presenti' if (z or 0) > 3 and p < 0.01 else ('assenti' if p > 0.05 else 'incerto')
    desc = OrderedDict()
    for rad in ('okal', 'otal'):
        c = Counter(cat for _, cat, w in dati if w.startswith(rad))
        desc[rad] = dict(c)
    ris = OrderedDict([('etichette', len(dati)), ('per_anello', dict(Counter(c for _, c, _ in dati))), ('im', vero), ('nullo', m), ('z', z), ('p', p),
                       ('okal_otal', desc), ('esito', esito)])
    print('etichette %d %s | IM %.4f (nullo %.4f) z %.1f p %.4f | %s | %s' % (len(dati), ris['per_anello'], vero, m, z or 0, p, dict(desc), esito), flush=True)
    with open(os.path.join(RISULTATI, 'e200_anelli_zodiaco.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e200 — Le etichette dello zodiaco preferiscono un anello?', '', 'Preregistrazione: `preregistrazioni/e200.md`.', '',
           '| etichette | IM prefisso–anello | nullo | z | p |', '|---|---|---|---|---|', '| %d | %.4f | %.4f | %.1f | %.4f |' % (len(dati), vero, m, z or 0, p), '',
           'Per anello: %s. okal…: %s; otal…: %s.' % (ris['per_anello'], desc['okal'], desc['otal']), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e200_anelli_zodiaco.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
