# -*- coding: utf-8 -*-
"""Esperimento 191: compressione adattiva (Markov KT, contesto tipo + ultimi k bit) della sequenza delle scelte di
grafia, contro rimescolamento dentro riga e scelta; controlli con latino in codice di Huffman.

Preregistrazione: preregistrazioni/e191.md. Scrive risultati/e191_compressione_scelte.json e .md.
"""
import heapq, json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e181_bacone as e181

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, KMAX = 191, 50, 12


def lunghezza(tipi, bit, k):
    cont = defaultdict(lambda: [0.5, 0.5])
    tot = 0.0
    storia = ()
    for t, b in zip(tipi, bit):
        c = cont[(t, storia)]
        tot -= math.log2(c[b] / (c[0] + c[1]))
        c[b] += 1
        storia = (storia + (b,))[-k:] if k else ()
    return tot / len(bit)


def migliore(tipi, bit):
    return min(lunghezza(tipi, bit, k) for k in range(KMAX + 1))


def huffman(n_bit):
    lettere = [c for w in lingue.parole('Latin')[:30000] for c in w if c.isalpha()]
    freq = Counter(lettere)
    heap = [[n, i, {c: ''}] for i, (c, n) in enumerate(freq.items())]
    heapq.heapify(heap)
    i = len(heap)
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        codici = {c: '0' + x for c, x in a[2].items()}
        codici.update({c: '1' + x for c, x in b[2].items()})
        heapq.heappush(heap, [a[0] + b[0], i, codici])
        i += 1
    codici = heap[0][2]
    out = []
    for c in lettere:
        out += [int(x) for x in codici[c]]
        if len(out) >= n_bit:
            break
    return out[:n_bit]


def prova(occ, bit, rnd):
    tipi = [f for f, _, _ in occ]
    vero = migliore(tipi, bit)
    gruppi = defaultdict(list)
    for i, (f, k, _) in enumerate(occ):
        gruppi[(f, k)].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        vv = list(bit)
        for idx in gruppi.values():
            if len(idx) > 1:
                x = [vv[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vv[i] = y
        nulli.append(migliore(tipi, vv))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('bit_per_occorrenza', vero), ('nullo', m), ('guadagno', m - vero), ('z', (m - vero) / s if s else None)])


def main():
    rnd = random.Random(SEME)
    occ = e181.occorrenze()
    voy = [v for _, _, v in occ]
    msg = huffman(len(voy))
    testi = OrderedDict([('Voynich', voy), ('controllo: Huffman puro (π 1)', msg),
                         ('controllo: Huffman mescolato (π 0,7)', [m if rnd.random() < 0.7 else v for m, v in zip(msg, voy)])])
    ris = OrderedDict([('occorrenze', len(occ))])
    for n, b in testi.items():
        ris[n] = prova(occ, b, rnd)
        print('%-38s %.4f bit/occ (nullo %.4f) guadagno %.4f z %.1f' % (n, ris[n]['bit_per_occorrenza'], ris[n]['nullo'], ris[n]['guadagno'], ris[n]['z'] or 0), flush=True)
    z = lambda n: ris[n]['z'] or 0
    valido = z('controllo: Huffman puro (π 1)') > 4
    esito = 'test non valido' if not valido else ('ridondanza da messaggio' if z('Voynich') > 4 else ('assente' if z('Voynich') < 2 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    print('valido %s | %s' % (valido, esito))
    with open(os.path.join(RISULTATI, 'e191_compressione_scelte.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e191 — Un messaggio a codice variabile nelle scelte di grafia? Test di compressione', '',
           'Lunghezza di codice (bit per occorrenza) con un modello di Markov adattivo (miglior ordine 0–%d), contro %d rimescolamenti dentro riga e scelta. '
           'Preregistrazione: `preregistrazioni/e191.md`.' % (KMAX, RIMESCOLAMENTI), '', '| testo | bit/occ | nullo | guadagno | z |', '|---|---|---|---|---|']
    for n in testi:
        r = ris[n]
        out.append('| %s | %.4f | %.4f | %.4f | %.1f |' % (n, r['bit_per_occorrenza'], r['nullo'], r['guadagno'], r['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e191_compressione_scelte.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
