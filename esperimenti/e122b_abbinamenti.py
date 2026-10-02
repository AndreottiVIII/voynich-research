# -*- coding: utf-8 -*-
"""Esperimento 122b: le pagine della farmacia condividono vocabolario con le pagine d'erbario della stessa pianta?
Abbinamenti pubblicati (commenti ZL) e visivi (Claude, alla cieca rispetto al testo).

Preregistrazione: preregistrazioni/e122b.md (misura dell'e122). Scrive risultati/e122b_abbinamenti.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
PUBBLICATI = os.path.join(QUI, '..', 'dati', 'corrispondenze_farmacia.json')
VISIVI = os.path.join(QUI, '..', 'dati', 'abbinamenti_visivi.json')
SEME, PERM = 122, 10000


def pagina_base(p):
    return p.split('[')[0]


def coppie_pubblicate():
    d = json.load(open(PUBBLICATI, encoding='utf-8'))
    out = []
    for c in d['coppie']:
        out.append((pagina_base(c['farmacia']), c['erbario'], 'media' if c['incerta'] else 'alta'))
    for c in d['scartate']:
        out.append((pagina_base(c['farmacia']), c['erbario'], 'alta'))
    return out


def coppie_visive():
    if not os.path.exists(VISIVI):
        return []
    return [(c['farmacia'], c['erbario'], c['certezza']) for c in json.load(open(VISIVI, encoding='utf-8'))['coppie']]


def vocabolari():
    voc = defaultdict(set)
    for r in trascrizione.leggi('ZL'):
        for w in r.parole:
            if trascrizione.pulita(w):
                voc[r.pagina].add(w)
    return voc


def erbario_pagine():
    return sorted({r.pagina for r in trascrizione.leggi('ZL') if r.sezione == 'H'})


def sim(a, b, voc, varianti):
    A, B = voc[a], voc[b]
    if not A:
        return 0.0
    if not varianti:
        return len(A & B) / len(A)
    return sum(1 for w in A if w in B or any(misure._dist_norm(w, x) <= 0.2 for x in B)) / len(A)


def analisi(coppie, voc, erb, varianti, rnd, normalizza):
    coppie = sorted({(f, e) for f, e, _ in coppie if voc[f] and voc[e]})
    if not coppie:
        return None
    media_tutte = {}
    if normalizza:
        for f in {f for f, _ in coppie}:
            media_tutte[f] = statistics.mean(sim(f, e, voc, varianti) for e in erb) or 1.0
    val = lambda f, e: sim(f, e, voc, varianti) / (media_tutte[f] if normalizza else 1.0)
    reale = statistics.mean(val(f, e) for f, e in coppie)
    per_f = defaultdict(int)
    for f, _ in coppie:
        per_f[f] += 1
    cache = {}
    nulli = []
    for _ in range(PERM):
        xs = []
        for f, n in per_f.items():
            for e in rnd.sample(erb, n):
                if (f, e) not in cache:
                    cache[(f, e)] = val(f, e)
                xs.append(cache[(f, e)])
        nulli.append(statistics.mean(xs))
    p = sum(x >= reale for x in nulli) / PERM
    return OrderedDict([('coppie', len(coppie)), ('pagine_farmacia', len(per_f)), ('media', reale), ('nullo', statistics.mean(nulli)), ('p', p)])


def main():
    rnd = random.Random(SEME)
    voc, erb = vocabolari(), erbario_pagine()
    A = coppie_pubblicate()
    B = [c for c in coppie_visive() if (c[0], c[1]) not in {(f, e) for f, e, _ in A}]
    insiemi = OrderedDict([('(A) pubblicati', A), ('(A) + (B) alta e media', A + [c for c in B if c[2] in ('alta', 'media')]),
                           ('(B) bassa (descrittiva)', [c for c in B if c[2] == 'bassa'])])
    ris = OrderedDict()
    for nome, cc in insiemi.items():
        if not cc:
            continue
        ris[nome] = OrderedDict()
        for etich, var, norm in (('principale', False, False), ('secondaria (varianti)', True, False), ('principale, normalizzata', False, True)):
            r = analisi(cc, voc, erb, var, rnd, norm)
            ris[nome][etich] = r
            if r:
                print('%-26s %-26s coppie %2d (pagine farmacia %d) | media %.4f nullo %.4f p %.4f' % (nome, etich, r['coppie'], r['pagine_farmacia'], r['media'], r['nullo'], r['p']), flush=True)
        pr, se = ris[nome]['principale'], ris[nome]['secondaria (varianti)']
        ris[nome]['valido'] = bool(pr) and pr['coppie'] >= 15
        ris[nome]['segnale'] = bool(pr) and (pr['p'] < 0.01 or (pr['p'] < 0.05 and se and se['p'] < 0.05))
    with open(os.path.join(RISULTATI, 'e122b_abbinamenti.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e122b — Pagine abbinate farmacia–erbario', '', 'Quota dei tipi della pagina della farmacia presenti nella pagina d\'erbario abbinata, contro %d permutazioni. '
           'Preregistrazioni: `preregistrazioni/e122.md`, `preregistrazioni/e122b.md`.' % PERM, '',
           '| insieme | misura | coppie | media | nullo | p |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        for k in ('principale', 'secondaria (varianti)', 'principale, normalizzata'):
            x = r.get(k)
            if x:
                out.append('| %s | %s | %d | %.4f | %.4f | %.4f |' % (nome, k, x['coppie'], x['media'], x['nullo'], x['p']))
    out += ['']
    for nome, r in ris.items():
        out.append('- %s: valido (≥ 15 coppie) **%s**, segnale di nominazione **%s**.' % (nome, 'sì' if r['valido'] else 'no', 'sì' if r['segnale'] else 'no'))
    with open(os.path.join(RISULTATI, 'e122b_abbinamenti.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
