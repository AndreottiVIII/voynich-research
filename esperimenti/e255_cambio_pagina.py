# -*- coding: utf-8 -*-
"""Esperimento 255: le prime righe di una pagina riprendono le ultime della pagina precedente (piu' delle sue prime)?
Precedente nella rilegatura, pagina a fronte (per i versi), successiva; nullo: pagine a caso della stessa sezione e mano.

Preregistrazione: preregistrazioni/e255.md. Scrive risultati/e255_cambio_pagina.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE, N_RIGHE = 255, 500, 3
D = e237.D


def main():
    rnd = random.Random(SEME)
    ordine = []
    for r in trascrizione.leggi('ZL'):
        if r.pagina not in ordine:
            ordine.append(r.pagina)
    P = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        if ps:
            P.setdefault(r.pagina, {'sezione': r.sezione, 'mano': r.mano, 'righe': []})['righe'].append(ps)
    P = OrderedDict((p, d) for p, d in P.items() if len(d['righe']) >= 2 * N_RIGHE)
    tutte = {u for d in P.values() for r in d['righe'] for u in r}
    inventario = sorted({x for u in tutte for x in u})
    vic = {}

    def V(u):
        if u not in vic:
            vic[u] = e237.vicini(u, inventario) | {u}
        return vic[u]

    F = {p: [u for r in d['righe'][:N_RIGHE] for u in r] for p, d in P.items()}
    L = {p: {u for r in d['righe'][-N_RIGHE:] for u in r} for p, d in P.items()}
    Fs = {p: set(F[p]) for p in P}

    def S(A, B):
        return sum(1 for u in A if V(u) & B) / len(A) if A else 0.0

    def Dc(p, q):
        return S(F[p], L[q]) - S(F[p], Fs[q])

    idx = {p: i for i, p in enumerate(ordine)}
    prec = {p: ordine[idx[p] - 1] for p in P if idx[p] > 0 and ordine[idx[p] - 1] in P}
    succ = {p: ordine[idx[p] + 1] for p in P if idx[p] + 1 < len(ordine) and ordine[idx[p] + 1] in P}
    fronte = {}
    for p in P:
        m = re.fullmatch(r'f(\d+)v', p)
        if m and 'f%dr' % (int(m.group(1)) + 1) in P:
            fronte[p] = 'f%dr' % (int(m.group(1)) + 1)
    stesso_foglio = {p: p[:-1] + 'r' for p in fronte if p[:-1] + 'r' in P}
    gruppi = defaultdict(list)
    for p, d in P.items():
        gruppi[(d['sezione'], d['mano'])].append(p)
    ris = OrderedDict()
    for nome, rel in (('precedente nella rilegatura', prec), ('successiva nella rilegatura', succ),
                      ('a fronte (versi)', fronte), ('recto dello stesso foglio (versi)', stesso_foglio)):
        pp = list(rel)
        vera = statistics.mean(Dc(p, rel[p]) for p in pp)
        nulli = []
        for _ in range(REPLICHE):
            vs = []
            for p in pp:
                esclusi = {p, prec.get(p), succ.get(p), fronte.get(p)}
                cand = [q for q in gruppi[(P[p]['sezione'], P[p]['mano'])] if q not in esclusi]
                if cand:
                    vs.append(Dc(p, rnd.choice(cand)))
            nulli.append(statistics.mean(vs))
        mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        ris[nome] = OrderedDict([('pagine', len(pp)), ('D_medio', vera), ('nullo', mu), ('z', (vera - mu) / sd if sd else None),
                                 ('S_fine', statistics.mean(S(F[p], L[rel[p]]) for p in pp)), ('S_inizio', statistics.mean(S(F[p], Fs[rel[p]]) for p in pp))])
        print(nome, dict(ris[nome]), flush=True)
    zp, zs = ris['precedente nella rilegatura']['z'] or 0, ris['successiva nella rilegatura']['z'] or 0
    zf, zr = ris['a fronte (versi)']['z'] or 0, ris['recto dello stesso foglio (versi)']['z'] or 0
    esiti = []
    if zp > 3 and ris['precedente nella rilegatura']['D_medio'] > ris['successiva nella rilegatura']['D_medio']:
        esiti.append('copia attraverso la pagina (dalla precedente nella rilegatura)')
    if zf > 3 and ris['a fronte (versi)']['D_medio'] > ris['recto dello stesso foglio (versi)']['D_medio']:
        esiti.append('copia dalla pagina a fronte')
    if not esiti:
        esiti.append('nessuna copia attraverso la pagina' if max(zp, zs, zf, zr) <= 2 else 'incerto')
    ris['esito'] = '; '.join(esiti)
    json.dump(ris, open(os.path.join(RISULTATI, 'e255_cambio_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e255 — Si copia anche attraverso il cambio di pagina?', '',
          'D = S(prime 3 righe di p, ultime 3 righe di q) − S(prime 3 righe di p, prime 3 righe di q), S = quota di ripetizioni o varianti a distanza 1; '
          'nullo: pagine a caso della stessa sezione e mano, %d repliche. Preregistrazione: `preregistrazioni/e255.md`.' % REPLICHE, '',
          '| q | pagine | S con la fine | S con l\'inizio | D medio | nullo | z |', '|---|---|---|---|---|---|---|']
    for nome in list(ris)[:4]:
        r = ris[nome]
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %+.4f | %.1f |' % (nome, r['pagine'], r['S_fine'], r['S_inizio'], r['D_medio'], r['nullo'], r['z'] or 0))
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e255_cambio_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
