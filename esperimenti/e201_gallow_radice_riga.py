# -*- coding: utf-8 -*-
"""Esperimento 201: la scelta k/t si prevede meglio dalla radice della parola o dalle altre scelte k/t della riga?

Preregistrazione: preregistrazioni/e201.md. Scrive risultati/e201_gallow_radice_riga.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PSEUDO = 2.0


def occorrenze():
    out = []
    pagine = []
    for k, r in enumerate(x for x in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if x.parole):
        if r.pagina not in pagine:
            pagine.append(r.pagina)
        for w in r.parole:
            if not trascrizione.pulita(w):
                continue
            u = D(w)
            idx = [i for i, g in enumerate(u) if g in ('k', 't')]
            if len(idx) == 1:
                rad = tuple('G' if i == idx[0] else g for i, g in enumerate(u))
                out.append((r.pagina, k, rad, 1 if u[idx[0]] == 't' else 0))
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    return out, meta


def bit(p, v):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log2(p if v else 1 - p)


def main():
    occ, meta = occorrenze()
    per_riga = defaultdict(list)
    for i, (pag, k, rad, v) in enumerate(occ):
        per_riga[k].append(i)
    tot = OrderedDict((m, 0.0) for m in ('M0', 'MR', 'ML', 'MRL'))
    n = 0
    for verifica in (0, 1):
        stima = [o for o in occ if meta[o[0]] != verifica]
        g = sum(v for *_, v in stima) / len(stima)
        cr = defaultdict(lambda: [0, 0])
        for _, _, rad, v in stima:
            cr[rad][0] += v
            cr[rad][1] += 1
        for i, (pag, k, rad, v) in enumerate(occ):
            if meta[pag] != verifica:
                continue
            n += 1
            a, b = cr.get(rad, [0, 0])
            pr = (a + PSEUDO * g) / (b + PSEUDO)
            altri = [occ[j][3] for j in per_riga[k] if j != i]
            pl = (sum(altri) + PSEUDO * g) / (len(altri) + PSEUDO)
            odds = (pr / (1 - pr)) * (pl / (1 - pl)) / (g / (1 - g))
            prl = odds / (1 + odds)
            for m, p in (('M0', g), ('MR', pr), ('ML', pl), ('MRL', prl)):
                tot[m] += bit(p, v)
    b = OrderedDict((m, x / n) for m, x in tot.items())
    rr, rl = b['M0'] - b['MR'], b['M0'] - b['ML']
    esito = 'classificatore di radice' if rr >= 2 * rl else ('abitudine di riga' if rl >= rr else 'entrambi')
    ris = OrderedDict([('occorrenze', n), ('bit_per_occorrenza', b), ('risparmio_radice', rr), ('risparmio_riga', rl), ('risparmio_entrambi', b['M0'] - b['MRL']),
                       ('quota_t', sum(v for *_, v in occ) / len(occ)), ('esito', esito)])
    print('occorrenze %d | M0 %.4f MR %.4f ML %.4f MRL %.4f | risparmio radice %.4f, riga %.4f, entrambi %.4f | %s' % (
        n, b['M0'], b['MR'], b['ML'], b['MRL'], rr, rl, b['M0'] - b['MRL'], esito), flush=True)
    with open(os.path.join(RISULTATI, 'e201_gallow_radice_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e201 — k o t: la decide la radice della parola o la riga?', '', 'Bit per occorrenza in validazione incrociata (pagine pari/dispari). Preregistrazione: `preregistrazioni/e201.md`.', '',
           '| M0 | MR (radice) | ML (riga) | MRL (entrambi) |', '|---|---|---|---|', '| %.4f | %.4f | %.4f | %.4f |' % (b['M0'], b['MR'], b['ML'], b['MRL']), '',
           'Risparmio: radice %.4f, riga %.4f, entrambi %.4f bit per occorrenza (%d occorrenze). Esito: **%s**.' % (rr, rl, b['M0'] - b['MRL'], n, esito)]
    with open(os.path.join(RISULTATI, 'e201_gallow_radice_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
