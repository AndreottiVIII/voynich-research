# -*- coding: utf-8 -*-
"""Esperimento 382: la ripresa dalle 2 righe sopra (misura dell'e346) con unita' uguali per tutti: pagine del Voynich,
pagine di 25 righe per testi sensati (parole intere, prime 500 righe) e gibberish, pagine di Timm e Schinner.

Preregistrazione: preregistrazioni/e382.md. Scrive risultati/e382_ripresa_pagine.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e337_posizione as e337
import e346_gibberish as e346
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
ALT = 25


def a_pagine(righe, minimo=10):
    pp = [righe[i:i + ALT] for i in range(0, len(righe), ALT)]
    return [p for p in pp if len(p) >= minimo]


def gruppo(unita, segni, rnd):
    vals = []
    for r in unita:
        v = e346.misura_unita(r, segni, rnd)
        if v:
            vals.append(v)

    def stima(vs):
        si, tot, nu = sum(v[0] for v in vs), sum(v[1] for v in vs), sum(v[2] for v in vs)
        return (si - nu) / tot, si / nu if nu else 0.0
    E, R = stima(vals)
    boot = [stima([vals[rnd.randrange(len(vals))] for _ in vals]) for _ in range(1000)]
    be, br = sorted(b[0] for b in boot), sorted(b[1] for b in boot)
    return OrderedDict([('pagine', len(vals)), ('parole', sum(v[1] for v in vals)), ('E', E), ('IC95_E', [be[25], be[974]]), ('R', R), ('IC95_R', [br[25], br[974]])])


def esito(V, G, S, k):
    ic = 'IC95_' + k
    dentro = lambda x, i: i[0] <= x <= i[1]
    if V[k] > max(G[ic][1], S[ic][1]):
        return 'più di tutti'
    if dentro(V[k], G[ic]) and not dentro(V[k], S[ic]):
        return 'come il gibberish umano'
    if dentro(V[k], S[ic]) and not dentro(V[k], G[ic]):
        return 'come i testi sensati'
    if dentro(V[k], G[ic]) and dentro(V[k], S[ic]):
        return 'non distinguibile'
    return 'fuori da tutti e due'


def main():
    rnd = random.Random(382)
    tutto = lambda w: tuple(w)
    voy = list(e346.unita_voynich().values())
    sens = e381.testi()
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(n).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib += a_pagine(righe)
    ris = OrderedDict()
    ris['Voynich'] = gruppo(voy, lambda w: tuple(D(w)), rnd)
    ris['gibberish umano'] = gruppo(gib, tutto, rnd)
    pag_sens = {k: a_pagine(t[:500]) for k, t in sens.items()}
    ris['testi sensati'] = gruppo([p for pp in pag_sens.values() for p in pp], tutto, rnd)
    for cat in ('Historical', 'Modern', 'Conlangs'):
        ris['testi sensati: %s' % cat] = gruppo([p for k, pp in pag_sens.items() if k.startswith(cat) for p in pp], tutto, rnd)
    for s in (1, 19):
        ris['Timm e Schinner, seme %d' % s] = gruppo(e337.pagine_ts(s), lambda w: tuple(D(w)), rnd)
    for k, v in ris.items():
        print(k, json.dumps(v, default=float), flush=True)
    V, G, S = ris['Voynich'], ris['gibberish umano'], ris['testi sensati']
    out = OrderedDict([('gruppi', ris), ('esito_E', esito(V, G, S, 'E')), ('esito_R', esito(V, G, S, 'R'))])
    json.dump(out, open(os.path.join(RISULTATI, 'e382_ripresa_pagine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e382 — La ripresa dalle righe sopra a parità di unità', '', 'Preregistrazione: `preregistrazioni/e382.md`. Pagine di 25 righe per testi sensati e gibberish; pagine vere per il Voynich; parole intere.', '',
          '| testo | pagine | parole | E | IC 95% | R | IC 95% |', '|---|---|---|---|---|---|---|']
    for k, v in ris.items():
        md.append('| %s | %d | %d | %+.4f | %+.4f – %+.4f | %.3f | %.3f – %.3f |' % (k, v['pagine'], v['parole'], v['E'], v['IC95_E'][0], v['IC95_E'][1], v['R'], v['IC95_R'][0], v['IC95_R'][1]))
    md += ['', 'Esito su E: **%s**. Esito su R: **%s**.' % (out['esito_E'], out['esito_R'])]
    open(os.path.join(RISULTATI, 'e382_ripresa_pagine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
