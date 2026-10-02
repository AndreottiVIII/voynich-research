# -*- coding: utf-8 -*-
"""Esperimento 210: limite piu' stretto per il canale delle cinque scelte di grafia: modelli con la parola
(lessicalizzazione), la riga e la riga precedente, in validazione incrociata.

Preregistrazione: preregistrazioni/e210.md. Scrive risultati/e210_capacita_stretta.json e .md.
Espone anche bit_per_occorrenza() per l'e209.
"""
import json, math, os, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e135_stato_riga as e135
import e154b_ordine_normalizzato as e154b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCELTE = (0, 1, 2, 4, 6)
PSEUDO = 2.0
_CACHE = {}


def occorrenze():
    """[(pagina, riga, scelta, chiave lessicale, valore)] nell'ordine di lettura."""
    righe = [(r.pagina, list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    out = []
    for k, (pag, ps) in enumerate(righe):
        for w in ps:
            if not trascrizione.pulita(w):
                continue
            if w not in _CACHE:
                _CACHE[w] = [(f, v) for f, _, _, v in e135.occorrenze([('x', [w])]) if f in SCELTE]
            n = e154b.normalizza(w)
            for f, v in _CACHE[w]:
                out.append((pag, k, f, n, v))
    return righe, out


def bit(p, v):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log2(p if v else 1 - p)


def odds(p):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return p / (1 - p)


def bit_per_occorrenza(righe, occ, valori=None):
    """Bit di ogni occorrenza sotto MX, MXL, MXLP (validazione incrociata pagine pari/dispari)."""
    valori = valori if valori is not None else [o[4] for o in occ]
    pagine = []
    for pag, _ in righe:
        if pag not in pagine:
            pagine.append(pag)
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    per_riga = defaultdict(list)
    for i, (pag, k, f, n, _) in enumerate(occ):
        per_riga[(k, f)].append(i)
    out = {m: [0.0] * len(occ) for m in ('M0', 'MX', 'MXL', 'MXLP')}
    for verifica in (0, 1):
        g = defaultdict(lambda: [0, 0])
        lx = defaultdict(lambda: [0, 0])
        for (pag, k, f, n, _), v in zip(occ, valori):
            if meta[pag] != verifica:
                g[f][0] += v
                g[f][1] += 1
                lx[(f, n)][0] += v
                lx[(f, n)][1] += 1
        for i, ((pag, k, f, n, _), v) in enumerate(zip(occ, valori)):
            if meta[pag] != verifica:
                continue
            q = (g[f][0] + 1) / (g[f][1] + 2)
            a, b = lx.get((f, n), [0, 0])
            px = (a + PSEUDO * q) / (b + PSEUDO)
            altri = [valori[j] for j in per_riga[(k, f)] if j != i]
            pl = (sum(altri) + PSEUDO * q) / (len(altri) + PSEUDO)
            prec = [valori[j] for j in per_riga.get((k - 1, f), [])] if k > 0 and righe[k - 1][0] == pag else []
            pp = (sum(prec) + PSEUDO * q) / (len(prec) + PSEUDO)
            o_xl = odds(px) * odds(pl) / odds(q)
            o_xlp = o_xl * odds(pp) / odds(q)
            out['M0'][i] = bit(q, v)
            out['MX'][i] = bit(px, v)
            out['MXL'][i] = bit(o_xl / (1 + o_xl), v)
            out['MXLP'][i] = bit(o_xlp / (1 + o_xlp), v)
    return out


def main():
    righe, occ = occorrenze()
    b = bit_per_occorrenza(righe, occ)
    medie = OrderedDict((m, sum(x) / len(x)) for m, x in b.items())
    migliore = min(medie, key=medie.get)
    tot = sum(b[migliore])
    per_scelta = OrderedDict()
    for f in SCELTE:
        idx = [i for i, o in enumerate(occ) if o[2] == f]
        per_scelta[e135.SCELTE[f]] = OrderedDict((m, sum(b[m][i] for i in idx) / len(idx)) for m in b)
    e182 = json.load(open(os.path.join(RISULTATI, 'e182_capacita.json'), encoding='utf-8'))['Voynich']
    e189 = json.load(open(os.path.join(RISULTATI, 'e189_capacita_totale.json'), encoding='utf-8'))
    nuovo_189 = tot + e189['b_segno_d_inizio']['bit_totali'] + e189['c_ordine_nella_riga']['bit_totali']
    ris = OrderedDict([('occorrenze', len(occ)), ('bit_per_occorrenza', medie), ('migliore', migliore), ('bit_totali', tot),
                       ('e182_bit_totali', e182['bit_totali']), ('riduzione', 1 - tot / e182['bit_totali']), ('per_scelta', per_scelta),
                       ('tre_canali_nuovo_totale', nuovo_189), ('lettere_latino', [nuovo_189 / 4.1, nuovo_189 / 2]), ('parole_latine', [nuovo_189 / 4.1 / 6, nuovo_189 / 2 / 6])])
    print('bit/occ %s | migliore %s: %.0f bit (e182 %.0f, -%.0f%%) | tre canali %.0f bit = %.0f–%.0f parole latine' % (
        {m: round(x, 4) for m, x in medie.items()}, migliore, tot, e182['bit_totali'], 100 * ris['riduzione'], nuovo_189, nuovo_189 / 4.1 / 6, nuovo_189 / 2 / 6), flush=True)
    for s, x in per_scelta.items():
        print('  %-14s %s' % (s, {m: round(y, 3) for m, y in x.items()}))
    with open(os.path.join(RISULTATI, 'e210_capacita_stretta.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e210 — Un limite più stretto per il canale delle scelte di grafia', '', 'Preregistrazione: `preregistrazioni/e210.md`.', '',
           '| scelta | M0 | MX (parola) | MXL (+ riga) | MXLP (+ riga precedente) |', '|---|---|---|---|---|']
    for s, x in per_scelta.items():
        out.append('| %s | %.3f | %.3f | %.3f | %.3f |' % (s, x['M0'], x['MX'], x['MXL'], x['MXLP']))
    out.append('| **tutte** | %.3f | %.3f | %.3f | %.3f |' % tuple(medie[m] for m in ('M0', 'MX', 'MXL', 'MXLP')))
    out += ['', 'Modello migliore %s: %.0f bit (e182: %.0f; riduzione %.0f%%). Tre canali (e189 con il canale delle scelte aggiornato): %.0f bit, cioè %.0f–%.0f parole latine.' % (
        migliore, tot, e182['bit_totali'], 100 * ris['riduzione'], nuovo_189, nuovo_189 / 4.1 / 6, nuovo_189 / 2 / 6)]
    with open(os.path.join(RISULTATI, 'e210_capacita_stretta.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
