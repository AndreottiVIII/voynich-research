# -*- coding: utf-8 -*-
"""Esperimento 182: capacita' massima del canale delle scelte di grafia: perdita logaritmica (validazione incrociata
per pagine) sotto modelli di abitudine M0, M1, M2.

Preregistrazione: preregistrazioni/e182.md. Scrive risultati/e182_capacita.json e .md.
"""
import json, math, os, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e135_stato_riga as e135
import e181_bacone as e181

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCELTE = (0, 1, 2, 4, 6)


def occorrenze():
    righe = [(r.pagina, list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    occ = [(f, k, st[1:], v) for f, k, st, v in e135.occorrenze(righe) if f in SCELTE]
    return righe, occ


def contesti(righe, occ, valori):
    """Per ogni occorrenza: (chiave M0, chiave M1, chiave M2)."""
    quota = defaultdict(lambda: [0, 0])
    for (f, k, st, _), v in zip(occ, valori):
        quota[(f, st)][0] += v
        quota[(f, st)][1] += 1
    res = defaultdict(list)
    for (f, k, st, _), v in zip(occ, valori):
        a, n = quota[(f, st)]
        res[(f, k)].append(v - a / n)
    media = {kk: statistics.mean(x) for kk, x in res.items()}
    out = []
    for f, k, st, _ in occ:
        prec = media.get((f, k - 1)) if k > 0 and righe[k - 1][0] == righe[k][0] else None
        segno = 'assente' if prec is None else ('+' if prec > 0 else '-')
        out.append(((f,), (f, st), (f, st, segno)))
    return out


def perdita(righe, occ, valori):
    ctx = contesti(righe, occ, valori)
    pagine = sorted({righe[k][0] for _, k, _, _ in occ}, key=lambda p: [r[0] for r in righe].index(p))
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    tot = OrderedDict((m, 0.0) for m in ('M0', 'M1', 'M2'))
    n = 0
    for verifica in (0, 1):
        cont = [defaultdict(lambda: [0, 0]) for _ in range(3)]
        for (f, k, st, _), c, v in zip(occ, ctx, valori):
            if meta[righe[k][0]] != verifica:
                for j in range(3):
                    cont[j][c[j]][0] += v
                    cont[j][c[j]][1] += 1
        for (f, k, st, _), c, v in zip(occ, ctx, valori):
            if meta[righe[k][0]] == verifica:
                n += 1
                for j, m in enumerate(tot):
                    a, b = cont[j].get(c[j], [0, 0])
                    p1 = (a + 1) / (b + 2)
                    tot[m] += -math.log2(p1 if v else 1 - p1)
    return OrderedDict((m, x / n) for m, x in tot.items()), n


def main():
    righe, occ = occorrenze()
    voy = [v for _, _, _, v in occ]
    n_righe = len({k for _, k, _, _ in occ})
    ris = OrderedDict([('occorrenze', len(occ)), ('righe_con_scelte', n_righe)])
    for nome, valori in (('Voynich', voy), ('canale pieno (Bacone, e181)', e181.bacone(len(voy)))):
        bit, n = perdita(righe, occ, valori)
        migliore = min(bit.values())
        totale = migliore * len(occ)
        ris[nome] = OrderedDict([('bit_per_occorrenza', bit), ('migliore', migliore), ('bit_per_riga', totale / n_righe), ('bit_totali', totale),
                                 ('lettere_latino_compresso', totale / 2), ('lettere_latino_grezzo', totale / 4.1)])
        print('%-30s M0 %.3f M1 %.3f M2 %.3f bit/occ | %.2f bit/riga | totale %.0f bit = %.0f lettere (compresso) / %.0f (grezzo)' % (
            nome, bit['M0'], bit['M1'], bit['M2'], totale / n_righe, totale, totale / 2, totale / 4.1), flush=True)
    with open(os.path.join(RISULTATI, 'e182_capacita.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e182 — Quanta informazione potrebbero portare le scelte di grafia?', '',
           'Perdita logaritmica in validazione incrociata (pagine pari/dispari) sotto tre modelli di abitudine. %d occorrenze in %d righe. '
           'Preregistrazione: `preregistrazioni/e182.md`.' % (len(occ), n_righe), '',
           '| testo | M0 | M1 | M2 (bit/occorrenza) | bit/riga | bit totali | lettere di latino (compresso / grezzo) |', '|---|---|---|---|---|---|---|']
    for nome in ('Voynich', 'canale pieno (Bacone, e181)'):
        r = ris[nome]
        out.append('| %s | %.3f | %.3f | %.3f | %.2f | %.0f | %.0f / %.0f |' % (nome, r['bit_per_occorrenza']['M0'], r['bit_per_occorrenza']['M1'], r['bit_per_occorrenza']['M2'],
                   r['bit_per_riga'], r['bit_totali'], r['lettere_latino_compresso'], r['lettere_latino_grezzo']))
    with open(os.path.join(RISULTATI, 'e182_capacita.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
