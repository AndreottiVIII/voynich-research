# -*- coding: utf-8 -*-
"""Esperimento e3a42: somiglianza lessicale fra paragrafi consecutivi contro paragrafi lontani della stessa pagina, con
l'ordine dei paragrafi rimescolato come nullo.

Preregistrazione: preregistrazioni/e3a42.md. Scrive risultati/e3a42_paragrafi_vicini.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rnd = random.Random(3142)
    pagine = []
    for pp in e341.pagine().values():
        pars = [[w for r in par for w in (tuple(D(x)) for x in r) if w] for par in pp]
        pars = [p for p in pars if len(p) >= 15]
        if len(pars) >= 3:
            pagine.append(pars)
    # matrici di somiglianza per pagina (calcolate una volta)
    matrici = []
    for pars in pagine:
        sim = e385.simili_unita(pars)
        insiemi = [set(p) for p in pars]
        n = len(pars)
        M = [[0.0] * n for _ in range(n)]
        for i in range(n):
            bers = [w for w in pars[i] if len(w) >= 3]
            for j in range(n):
                if i != j and bers:
                    M[i][j] = sum(1 for w in bers if sim[w] & insiemi[j]) / len(bers)
        S = [[(M[i][j] + M[j][i]) / 2 for j in range(n)] for i in range(n)]
        matrici.append(S)

    def stat(ordini):
        vic, lon = [], []
        for S, o in zip(matrici, ordini):
            n = len(o)
            for a in range(n):
                for b in range(a + 1, n):
                    (vic if b - a == 1 else lon).append(S[o[a]][o[b]])
        return statistics.mean(vic) - statistics.mean(lon), statistics.mean(vic), statistics.mean(lon)
    vero = stat([list(range(len(S))) for S in matrici])
    nul = [stat([rnd.sample(range(len(S)), len(S)) for S in matrici])[0] for _ in range(2000)]
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero[0] - m) / sd if sd else 0.0
    esito = 'continuità fra paragrafi vicini' if vero[0] > 0 and z > 3 else ('paragrafi indipendenti dentro la pagina' if abs(z) < 2 else 'incerto')
    out = OrderedDict([('pagine', len(pagine)), ('paragrafi', sum(len(p) for p in pagine)), ('somiglianza_vicini', vero[1]), ('somiglianza_lontani', vero[2]),
                       ('differenza', vero[0]), ('nullo', m), ('z', z), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a42_paragrafi_vicini.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a42 — I paragrafi vicini nella pagina si somigliano più di quelli lontani?', '', 'Preregistrazione: `preregistrazioni/e3a42.md`.', '',
          '%d pagine, %d paragrafi. Somiglianza fra paragrafi consecutivi %.3f, fra paragrafi lontani %.3f; differenza %+.4f (nullo %+.4f), z %.1f.' % (
              out['pagine'], out['paragrafi'], vero[1], vero[2], vero[0], m, z), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a42_paragrafi_vicini.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
