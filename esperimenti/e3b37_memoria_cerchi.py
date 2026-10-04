# -*- coding: utf-8 -*-
"""Esperimento e3b37: memoria corta delle scelte di grafia (vicino d 2-3 contro lontano d 6-10) nei testi in cerchio e nei
raggi della ZL; atteso dalle altre righe di cerchio e di raggio.

Preregistrazione: preregistrazioni/e3b37.md. Scrive risultati/e3b37_memoria_cerchi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b20_memoria_segni as e3b20

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
VICINO, LONTANO = (2, 3), tuple(range(6, 11))


def main():
    rnd = random.Random(3237)
    righe = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] in (trascrizione.CERCHIO, trascrizione.RAGGIO):
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append(ws)
    ev = []
    for c, f in e3b20.CLASSI.items():
        val = [[f(w) for w in r] for r in righe]
        tot = [sum(1 for v in vv if v is not None) for vv in val]
        uno = [sum(1 for v in vv if v == 1) for vv in val]
        T, U = sum(tot), sum(uno)
        for i, vv in enumerate(val):
            t, u = T - tot[i], U - uno[i]
            if t < 5:
                continue
            p = u / t
            att = p * p + (1 - p) * (1 - p)
            for a in range(len(vv)):
                if vv[a] is None:
                    continue
                for d in VICINO + LONTANO:
                    b = a + d
                    if b < len(vv) and vv[b] is not None:
                        ev.append((i, 'vicino' if d in VICINO else 'lontano', int(vv[a] == vv[b]) - att))

    def diff(e):
        acc = defaultdict(lambda: [0.0, 0])
        for _, g, x in e:
            acc[g][0] += x
            acc[g][1] += 1
        return acc['vicino'][0] / acc['vicino'][1] - acc['lontano'][0] / acc['lontano'][1], {g: (s / n, n) for g, (s, n) in acc.items()}
    d, dett = diff(ev)
    per = defaultdict(list)
    for x in ev:
        per[x[0]].append(x)
    chiavi = list(per)
    b = sorted(diff([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])[0] for _ in range(BOOT))
    ic = [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    esito = 'memoria corta anche nei cerchi' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'non si vede nei cerchi')
    out = OrderedDict([('righe', len(righe)), ('parole', sum(len(r) for r in righe)), ('dettaglio', dett), ('differenza', d), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b37_memoria_cerchi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b37 — Anche nei testi in cerchio c\'è la memoria corta delle scelte di grafia?', '', 'Preregistrazione: `preregistrazioni/e3b37.md`. Righe di cerchio e di raggio: %d, parole %d.' % (len(righe), out['parole']), '',
          '| coppie | quante | eccesso di accordo |', '|---|---|---|']
    md += ['| %s | %d | %+.4f |' % (g, dett[g][1], dett[g][0]) for g in ('vicino', 'lontano') if g in dett]
    md += ['', 'Differenza vicino − lontano **%+.4f**, IC 95%% %+.4f – %+.4f. (Paragrafi, e3b06: +0,031.)' % (d, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b37_memoria_cerchi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
