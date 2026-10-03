# -*- coding: utf-8 -*-
"""Esperimento 372: due parole vicine riprese dalla riga sopra vengono da due parole vicine sopra, nello stesso ordine,
piu' del caso (ordine della riga sopra rimescolato)? Riferimento: Timm e Schinner.

Preregistrazione: preregistrazioni/e372.md. Scrive risultati/e372_blocchi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e337_posizione as e337
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
simile = e341.simile


def misura(paragrafi, rnd):
    coppie = []    # (fonti di j, fonti di j+1, lunghezza riga sopra)
    for par in paragrafi:
        for i in range(1, len(par)):
            sopra, r = par[i - 1], par[i]
            fonti = [[k for k, x in enumerate(sopra) if simile(w, x)] for w in r]
            for j in range(len(r) - 1):
                if fonti[j] and fonti[j + 1]:
                    coppie.append((fonti[j], fonti[j + 1], len(sopra)))

    def quota(perm_fn):
        dir_ = inv = 0
        for a, b, n in coppie:
            pi = perm_fn(n)
            pa, pb = {pi[k] for k in a}, {pi[k] for k in b}
            dir_ += any(k + 1 in pb for k in pa)
            inv += any(k - 1 in pb for k in pa)
        return dir_ / len(coppie), inv / len(coppie)
    vero = quota(lambda n: list(range(n)))
    nul = [quota(lambda n: rnd.sample(range(n), n)) for _ in range(1000)]
    out = OrderedDict([('coppie', len(coppie))])
    for k, nome in enumerate(('stesso_ordine', 'ordine_invertito')):
        m, sd = statistics.mean(x[k] for x in nul), statistics.pstdev(x[k] for x in nul)
        out[nome] = OrderedDict([('quota', vero[k]), ('nullo', m), ('z', (vero[k] - m) / sd if sd else 0.0)])
    return out


def main():
    rnd = random.Random(372)
    pars = [p for pp in e341.pagine().values() for p in pp]
    ris = OrderedDict([('Voynich', misura(pars, rnd))])
    for s in (1, 19):
        ris['Timm e Schinner, seme %d' % s] = misura(e337.pagine_ts(s), rnd)
    for k, v in ris.items():
        print(k, json.dumps(v, ensure_ascii=False), flush=True)
    z = ris['Voynich']['stesso_ordine']['z']
    esito = 'copia a pezzi' if z > 3 else ('parole isolate' if z < 2 else 'incerto')
    json.dump(OrderedDict([('testi', ris), ('esito', esito)]), open(os.path.join(RISULTATI, 'e372_blocchi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e372 — La ripresa copia parole isolate o pezzi di riga?', '', 'Preregistrazione: `preregistrazioni/e372.md`.', '',
          '| testo | coppie vicine riprese | in blocco, stesso ordine | nullo | z | ordine invertito | nullo | z |', '|---|---|---|---|---|---|---|---|']
    for k, v in ris.items():
        a, b = v['stesso_ordine'], v['ordine_invertito']
        md.append('| %s | %d | %.3f | %.3f | %.1f | %.3f | %.3f | %.1f |' % (k, v['coppie'], a['quota'], a['nullo'], a['z'], b['quota'], b['nullo'], b['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e372_blocchi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
