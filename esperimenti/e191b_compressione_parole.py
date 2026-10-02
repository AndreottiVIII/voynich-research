# -*- coding: utf-8 -*-
"""Esperimento 191b: come l'e191, ma il nullo permuta le parole dentro la riga (ogni parola con le sue scelte).

Preregistrazione: preregistrazioni/e191b.md. Scrive risultati/e191b_compressione_parole.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e135_stato_riga as e135
import e191_compressione_scelte as e191

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 1912, 50
SCELTE = (0, 1, 2, 4, 6)
_CACHE = {}


def scelte_parola(w):
    if w not in _CACHE:
        _CACHE[w] = [(f, v) for f, _, _, v in e135.occorrenze([('x', [w])]) if f in SCELTE] if trascrizione.pulita(w) else []
    return _CACHE[w]


def main():
    rnd = random.Random(SEME)
    righe = [list(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    seq = [x for ps in righe for w in ps for x in scelte_parola(w)]
    vero = e191.migliore([f for f, _ in seq], [v for _, v in seq])
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        s = []
        for ps in righe:
            ps = ps[:]
            rnd.shuffle(ps)
            s += [x for w in ps for x in scelte_parola(w)]
        nulli.append(e191.migliore([f for f, _ in s], [v for _, v in s]))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    z = (m - vero) / sd if sd else None
    esito = 'ridondanza fra parole' if (z or 0) > 4 else ('il guadagno dell\'e191 è interno alle parole' if (z or 0) < 2 else 'incerto')
    ris = OrderedDict([('occorrenze', len(seq)), ('bit_per_occorrenza', vero), ('nullo', m), ('guadagno', m - vero), ('z', z), ('esito', esito)])
    print('occorrenze %d | %.4f bit/occ (nullo parole %.4f) guadagno %.4f z %.1f | %s' % (len(seq), vero, m, m - vero, z or 0, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e191b_compressione_parole.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e191b — Il guadagno di compressione viene dall\'interno delle parole?', '', 'Nullo: permutazione delle parole dentro la riga. Preregistrazione: `preregistrazioni/e191b.md`.', '',
           '| occorrenze | bit/occ | nullo | guadagno | z |', '|---|---|---|---|---|', '| %d | %.4f | %.4f | %.4f | %.1f |' % (len(seq), vero, m, m - vero, z or 0), '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e191b_compressione_parole.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
