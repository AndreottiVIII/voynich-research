# -*- coding: utf-8 -*-
"""Esperimento 181: canale "baconiano" nelle cinque scelte di grafia. Indice di coincidenza dei gruppi di L scelte
consecutive (ordine di lettura) contro il rimescolamento dentro riga e scelta; controllo con latino in alfabeto di Bacon.

Preregistrazione: preregistrazioni/e181.md. Scrive risultati/e181_bacone.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e135_stato_riga as e135

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 181, 200
SCELTE = (0, 1, 2, 4, 6)
ALFABETO = 'abcdefghiklmnopqrstuwxyz'   # 24 lettere: i=j, u=v


def occorrenze():
    righe = [(r.pagina, list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    return [(f, k, v) for f, k, _, v in e135.occorrenze(righe) if f in SCELTE]


def bacone(n_bit):
    bit = []
    for w in lingue.parole('Latin')[:20000]:
        for c in w.lower().replace('j', 'i').replace('v', 'u'):
            if c in ALFABETO:
                i = ALFABETO.index(c)
                bit += [(i >> s) & 1 for s in (4, 3, 2, 1, 0)]
        if len(bit) >= n_bit:
            break
    return bit[:n_bit]


def ioc(valori, L):
    migliore = 0.0
    for o in range(L):
        simboli = Counter(tuple(valori[i:i + L]) for i in range(o, len(valori) - L + 1, L))
        N = sum(simboli.values())
        x = sum(n * (n - 1) for n in simboli.values()) / (N * (N - 1)) if N > 1 else 0.0
        migliore = max(migliore, x)
    return migliore


def prova(occ, valori, L, rnd):
    vero = ioc(valori, L)
    gruppi = defaultdict(list)
    for i, (f, k, _) in enumerate(occ):
        gruppi[(f, k)].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        vv = list(valori)
        for idx in gruppi.values():
            if len(idx) > 1:
                x = [vv[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vv[i] = y
        nulli.append(ioc(vv, L))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('ioc', vero), ('nullo', m), ('z', (vero - m) / s if s else None)])


def main():
    rnd = random.Random(SEME)
    occ = occorrenze()
    voy = [v for _, _, v in occ]
    msg = bacone(len(voy))
    testi = OrderedDict()
    testi['Voynich'] = voy
    testi['controllo: Bacone puro (π 1)'] = msg
    mescolato = [m if rnd.random() < 0.7 else v for m, v in zip(msg, voy)]
    testi['controllo: Bacone mescolato (π 0,7)'] = mescolato
    ris = OrderedDict([('occorrenze', len(occ)), ('per_scelta', dict(Counter(f for f, _, _ in occ)))])
    for nome, vv in testi.items():
        ris[nome] = OrderedDict()
        for L in (5, 4, 6, 7):
            ris[nome]['L%d' % L] = prova(occ, vv, L, rnd)
        print('%-36s ' % nome + ' | '.join('L%d z %.1f' % (L, ris[nome]['L%d' % L]['z'] or 0) for L in (5, 4, 6, 7)), flush=True)
    z = lambda n: ris[n]['L5']['z'] or 0
    valido = z('controllo: Bacone puro (π 1)') > 4
    esito = 'test non valido' if not valido else ('canale baconiano presente' if z('Voynich') > 4 else ('assente' if z('Voynich') < 2 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    print('valido %s | esito: %s' % (valido, esito))
    with open(os.path.join(RISULTATI, 'e181_bacone.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e181 — Un messaggio "baconiano" nelle scelte di grafia?', '',
           'Indice di coincidenza dei gruppi di L scelte consecutive (massimo sugli sfasamenti), z contro %d rimescolamenti dentro riga e scelta. '
           '%d occorrenze. Preregistrazione: `preregistrazioni/e181.md`.' % (RIMESCOLAMENTI, len(occ)), '',
           '| testo | L 5 (principale) | L 4 | L 6 | L 7 |', '|---|---|---|---|---|']
    for nome in testi:
        out.append('| %s | %s |' % (nome, ' | '.join('%.4f (z %.1f)' % (ris[nome]['L%d' % L]['ioc'], ris[nome]['L%d' % L]['z'] or 0) for L in (5, 4, 6, 7))))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e181_bacone.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
