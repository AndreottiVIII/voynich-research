# -*- coding: utf-8 -*-
"""Esperimento e3a97: eccesso di parole vicine simili (uguali o a una modifica) nelle coppie continue e in quelle a
cavallo di un salto del disegno, rispetto al rimescolamento delle parole dentro la riga.

Preregistrazione: preregistrazioni/e3a97.md. Scrive risultati/e3a97_salto_ripetizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386
import e3a86_ripetizioni_riga as e3a86

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 500


def simili(a, b):
    return a == b or e3a86.una_modifica(a, b)


def conta(righe):
    """righe: [(parole, tipi delle giunture)]. {'continuo': [simili, coppie], 'salto': [...]}"""
    out = {'continuo': [0, 0], 'salto': [0, 0]}
    for ws, tipi in righe:
        for a, b, t in zip(ws, ws[1:], tipi):
            if a is None or b is None or len(a) < 2 or len(b) < 2:
                continue
            x = out[t]
            x[0] += simili(a, b)
            x[1] += 1
    return out


def main():
    rnd = random.Random(3197)
    righe = []
    for _, _, _, ws, seps in e386.righe():
        tipi = ['salto' if s == '|' else 'continuo' for s in seps]
        righe.append((ws, tipi))
    oss = conta(righe)
    nul = {'continuo': [], 'salto': []}
    for _ in range(PERM):
        rr = [(rnd.sample(ws, len(ws)), tipi) for ws, tipi in righe]
        c = conta(rr)
        for t in nul:
            nul[t].append(c[t][0] / c[t][1] if c[t][1] else 0.0)
    ris = OrderedDict()
    for t in ('continuo', 'salto'):
        q = oss[t][0] / oss[t][1] if oss[t][1] else None
        m, sd = statistics.mean(nul[t]), statistics.pstdev(nul[t])
        ris[t] = OrderedDict([('coppie', oss[t][1]), ('simili', oss[t][0]), ('quota', q), ('attesa', m), ('eccesso', q - m if q is not None else None), ('z', (q - m) / sd if sd else 0.0)])
    c, s = ris['continuo'], ris['salto']
    if s['coppie'] < 300:
        esito = 'dati insufficienti'
    elif c['z'] > 3 and s['eccesso'] < 0.5 * c['eccesso']:
        esito = 'il salto azzera la ripetizione immediata'
    else:
        esito = 'il salto non la azzera'
    out = OrderedDict([('coppie', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a97_salto_ripetizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a97 — Il salto di un disegno azzera anche la ripetizione immediata, come l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3a97.md`.', '',
          '| coppie | quante | simili | quota | attesa (rimescolamento nella riga) | eccesso | z |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %d | %.4f | %.4f | %+.4f | %.1f |' % (k, x['coppie'], x['simili'], x['quota'], x['attesa'], x['eccesso'], x['z']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a97_salto_ripetizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
