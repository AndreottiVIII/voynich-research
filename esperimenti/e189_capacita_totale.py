# -*- coding: utf-8 -*-
"""Esperimento 189: capacita' massima di tre canali (scelte di grafia, segno d'inizio riga, ordine delle parole nella
riga sotto il modello delle giunture).

Preregistrazione: preregistrazioni/e189.md. Scrive risultati/e189_capacita_totale.json e .md.
"""
import itertools, json, math, os, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e152_righe_in_ordine as e152

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
E182 = os.path.join(RISULTATI, 'e182_capacita.json')


def classe(w):
    g = D(w)[0]
    return g if g in ('y', 'd', 's') else 'altro'


def inizio(righe):
    pagine = []
    for pag, _, _ in righe:
        if pag not in pagine:
            pagine.append(pag)
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    casi = []
    for k in range(1, len(righe)):
        pag, ini, ps = righe[k]
        pag0, _, ps0 = righe[k - 1]
        if pag == pag0 and not ini and ps and ps0 and trascrizione.pulita(ps[0]) and trascrizione.pulita(ps0[0]):
            casi.append((meta[pag], classe(ps0[0]), classe(ps[0])))
    tot = 0.0
    for verifica in (0, 1):
        c = defaultdict(Counter)
        for m, a, b in casi:
            if m != verifica:
                c[a][b] += 1
        for m, a, b in casi:
            if m == verifica:
                n = sum(c[a].values())
                tot += -math.log2((c[a][b] + 1) / (n + 4))
    return OrderedDict([('righe', len(casi)), ('bit_per_riga', tot / len(casi)), ('bit_totali', tot)])


def ordine(righe, L):
    def peso(seq):
        p = 1.0
        for a, b in zip(seq, seq[1:]):
            p *= L.get((D(a)[-1], D(b)[0]), 0.05)
        return p
    per_n = defaultdict(list)
    lunghe = 0
    for _, _, ps in righe:
        ps = [w for w in ps if trascrizione.pulita(w)]
        n = len(ps)
        if n < 3:
            continue
        if n > 7:
            lunghe += n - 1
            continue
        resto = ps[1:]
        perms = set(itertools.permutations(resto))
        z = sum(peso([ps[0]] + list(p)) for p in perms)
        per_n[n].append(-math.log2(peso(ps) / z))
    bit = sum(sum(v) for v in per_n.values())
    per_parola = statistics.mean([x / (n - 1) for n in (6, 7) for x in per_n[n]])
    estrapolati = per_parola * lunghe
    return OrderedDict([('righe_esatte', sum(len(v) for v in per_n.values())), ('bit_esatti', bit), ('bit_per_parola_6_7', per_parola),
                        ('parole_righe_lunghe', lunghe), ('bit_estrapolati', estrapolati), ('bit_totali', bit + estrapolati),
                        ('bit_per_riga_per_n', {n: statistics.mean(v) for n, v in sorted(per_n.items())})])


def main():
    righe = [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    a = json.load(open(E182, encoding='utf-8'))['Voynich']['bit_totali']
    b = inizio(righe)
    c = ordine(righe, e152.lift())
    tot = a + b['bit_totali'] + c['bit_totali']
    ris = OrderedDict([('a_scelte_di_grafia', a), ('b_segno_d_inizio', b), ('c_ordine_nella_riga', c), ('totale_bit', tot),
                       ('lettere_latino_compresso', tot / 2), ('lettere_latino_grezzo', tot / 4.1), ('parole_latine_compresso', tot / 2 / 6), ('parole_latine_grezzo', tot / 4.1 / 6)])
    print('(a) scelte %.0f bit | (b) inizio %.0f bit (%.2f/riga) | (c) ordine %.0f bit (esatti %.0f su %d righe, %.2f bit/parola) | totale %.0f bit = %.0f–%.0f lettere, %.0f–%.0f parole latine' % (
        a, b['bit_totali'], b['bit_per_riga'], c['bit_totali'], c['bit_esatti'], c['righe_esatte'], c['bit_per_parola_6_7'], tot, tot / 4.1, tot / 2, tot / 4.1 / 6, tot / 2 / 6), flush=True)
    with open(os.path.join(RISULTATI, 'e189_capacita_totale.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e189 — Capacità massima di tre canali "liberi"', '', 'Preregistrazione: `preregistrazioni/e189.md`.', '',
           '| canale | bit |', '|---|---|', '| (a) scelte di grafia (e182) | %.0f |' % a,
           '| (b) segno d\'inizio riga | %.0f (%.2f per riga, %d righe) |' % (b['bit_totali'], b['bit_per_riga'], b['righe']),
           '| (c) ordine delle parole nella riga | %.0f (esatti %.0f su %d righe; %.2f bit per parola nelle righe di 6–7) |' % (c['bit_totali'], c['bit_esatti'], c['righe_esatte'], c['bit_per_parola_6_7']),
           '| **totale** | **%.0f** |' % tot, '', 'Equivalente: %.0f–%.0f lettere di latino, cioè %.0f–%.0f parole (grezzo–compresso).' % (tot / 4.1, tot / 2, tot / 4.1 / 6, tot / 2 / 6)]
    with open(os.path.join(RISULTATI, 'e189_capacita_totale.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
