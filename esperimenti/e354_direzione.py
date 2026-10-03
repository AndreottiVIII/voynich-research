# -*- coding: utf-8 -*-
"""Esperimento 354: nelle coppie a una modifica fra righe interne consecutive dello stesso paragrafo, la parola sopra e'
piu' spesso la piu' frequente? Nullo: righe interne rimescolate nel paragrafo. Riferimento: Timm e Schinner.

Preregistrazione: preregistrazioni/e354.md. Scrive risultati/e354_direzione.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e337_posizione as e337
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
simile = e341.simile
NULLI = 200


def interne_di(paragrafi):
    return [p[1:-1] for p in paragrafi if len(p) >= 4]


def Q(blocchi, freq):
    sopra_piu = tot = 0
    for b in blocchi:
        for i in range(1, len(b)):
            for w in b[i]:
                for x in b[i - 1]:
                    if x != w and freq[x] != freq[w] and simile(w, x):
                        tot += 1
                        sopra_piu += freq[x] > freq[w]
    return sopra_piu / tot if tot else None, tot


def prova(paragrafi, rnd):
    freq = Counter(w for p in paragrafi for r in p for w in r)
    blocchi = interne_di(paragrafi)
    q, n = Q(blocchi, freq)
    nul = [Q([rnd.sample(b, len(b)) for b in blocchi], freq)[0] for _ in range(NULLI)]
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('coppie', n), ('Q', q), ('nullo', m), ('z', (q - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(354)
    pag = e341.pagine()
    ris = OrderedDict([('Voynich', prova([p for pp in pag.values() for p in pp], rnd))])
    for s in (1, 19):
        ris['Timm e Schinner, seme %d' % s] = prova(e337.pagine_ts(s), rnd)
    for k, v in ris.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()}, flush=True)
    z = ris['Voynich']['z']
    esito = 'la ripresa va dall\'alto in basso' if z > 3 else ('senza direzione' if abs(z) < 2 else ('al contrario' if z < -3 else 'incerto'))
    json.dump(OrderedDict([('testi', ris), ('esito', esito)]), open(os.path.join(RISULTATI, 'e354_direzione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e354 — La direzione della ripresa', '', 'Preregistrazione: `preregistrazioni/e354.md`.', '',
          '| testo | coppie | quota con la forma più frequente sopra | nullo | z |', '|---|---|---|---|---|']
    for k, v in ris.items():
        md.append('| %s | %d | %.4f | %.4f | %.1f |' % (k, v['coppie'], v['Q'], v['nullo'], v['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e354_direzione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
