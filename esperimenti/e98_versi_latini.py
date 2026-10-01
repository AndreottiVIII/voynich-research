# -*- coding: utf-8 -*-
"""Esperimento 98: il verso chiude la riga anche senza sandhi? Poeti latini, un verso per riga contro testo di seguito.

Preregistrazione: preregistrazioni/e98.md. Scrive risultati/e98_versi_latini.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e76_righe_piene as e76
import e83_evitamento_inizi as e83

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 98
TESTI = OrderedDict([
    ('Ovidio, Metamorfosi', ['ovid/ovid.met%d.txt' % i for i in range(1, 16)]),
    ('Lucrezio, De rerum natura', ['lucretius/lucretius%d.txt' % i for i in range(1, 7)]),
    ('Giovenale, Satire', ['juvenal/%d.txt' % i for i in range(1, 17)]),
    ('Orazio, Satire ed Epistole', ['horace/serm1.txt', 'horace/serm2.txt', 'horace/epist1.txt', 'horace/epist2.txt']),
    ('Marbodo, De ornamentis verborum', ['marbodus.txt']),
    ('Virgilio, Eneide (esplorativo prima)', ['vergil/aen%d.txt' % i for i in range(1, 13)]),
])
SERVIZIO = ('Latin Library', 'Classics Page', 'The Latin', 'Christian Latin', 'Medieval Latin')


def versi(file):
    out = []
    for rel in file:
        righe = open(os.path.join(lingue.LATIN_LIBRARY, rel), encoding='utf-8').read().splitlines()
        for k, l in enumerate(righe):
            s = re.sub(r'\d+', '', l).strip()
            if not s or k == 0 or any(x in s for x in SERVIZIO):
                continue
            lettere = [c for c in s if c.isalpha()]
            if lettere and all(c.isupper() for c in lettere):
                continue
            ps = lingue.normalizza(s).split()
            if ps:
                out.append(ps)
    return out


def R(righe, rnd):
    d, a = e74.coppie(righe, e71.lettere)
    x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
    return OrderedDict([('dentro', x), ('a_capo', y), ('R', y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None)])


def una(args):
    nome, file = args
    vv = versi(file)
    rnd = random.Random(SEME)
    per_versi = [(i // 20, i % 20 == 0, ps) for i, ps in enumerate(vv)]
    larghezza = statistics.median(sum(len(w) for w in ps) + len(ps) - 1 for ps in vv)
    flusso = [w for ps in vv for w in ps]
    seguito = [(i // 20, i % 20 == 0, ps) for i, (_, _, ps) in enumerate(e76.a_capo_per_voce([flusso], e71.lettere, larghezza))]
    larg = [sum(len(w) for w in ps) + len(ps) - 1 for ps in vv]
    per = OrderedDict()
    for i, ps in enumerate(vv):
        per.setdefault(i // 20, []).append((i // 20, i % 20 == 0, ps[0]))
    s1 = e83.misura(per, 1, lambda w: w[0], random.Random(SEME))
    return nome, OrderedDict([('versi', len(vv)), ('parole', len(flusso)), ('per_versi', R(per_versi, rnd)),
                              ('di_seguito', R(seguito, rnd)), ('cv', statistics.pstdev(larg) / statistics.mean(larg)),
                              ('S1', s1['S']), ('S1_z', s1['z'])])


def main():
    e83.PERMUTAZIONI = 300
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, list(TESTI.items())):
            ris[nome] = r
            p, s = r['per_versi'], r['di_seguito']
            print('%-38s versi %5d | per versi: dentro %.4f (z %.0f) R %.2f | di seguito: R %.2f | CV %.3f | S(1) %.2f (z %.1f)' % (
                nome, r['versi'], p['dentro']['eccesso'], p['dentro']['z'] or 0, p['R'], s['R'], r['cv'], r['S1'], r['S1_z']), flush=True)
    conto, esclusi = 0, []
    for nome, r in ris.items():
        if nome.startswith('Virgilio'):
            continue
        if nome.startswith('Marbodo') and (r['per_versi']['dentro']['z'] or 0) < 5:
            esclusi.append(nome)
            continue
        conto += r['per_versi']['R'] < 0.3 and r['di_seguito']['R'] > 0.6
    validi = 5 - len(esclusi)
    ris['conferma'] = OrderedDict([('testi_conformi', conto), ('testi_validi', validi), ('esclusi', esclusi),
                                   ('confermato', conto >= 4)])
    print('conformi %d su %d validi (esclusi %s): confermato %s' % (conto, validi, esclusi, conto >= 4))
    with open(os.path.join(RISULTATI, 'e98_versi_latini.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e98 — Il verso chiude la riga? Poeti latini', '',
           'R come nell\'e74, un verso per riga e testo di seguito mandato a capo. Preregistrazione: `preregistrazioni/e98.md`. '
           'Voynich per confronto: R 0,006 (ZL), CV 0,049 (sezione S), S(1) 0,52.', '',
           '| testo | versi | legame dentro la riga (z) | R per versi | R di seguito | CV | S(1) |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if nome == 'conferma':
            continue
        p = r['per_versi']
        out.append('| %s | %d | %.4f (%.0f) | %.2f | %.2f | %.3f | %.2f |' % (nome, r['versi'], p['dentro']['eccesso'], p['dentro']['z'] or 0,
                                                                         p['R'], r['di_seguito']['R'], r['cv'], r['S1']))
    out += ['', 'Testi conformi: %d su %d validi; confermato: **%s**.' % (conto, validi, 'sì' if conto >= 4 else 'no')]
    with open(os.path.join(RISULTATI, 'e98_versi_latini.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
