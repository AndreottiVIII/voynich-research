# -*- coding: utf-8 -*-
"""Esperimento 280: i quattro anelli a 12 settori (f67r1, f67r2 due volte, f67v1) nominano le stesse 12 cose? Somiglianza
dei settori allineati (migliore fra 24 disposizioni per coppia di anelli) contro il rimescolamento nell'anello, con un
positivo di mesi latini cifrati e negativi fatti di finestre di altre etichette.

Preregistrazione: preregistrazioni/e280.md. Scrive risultati/e280_anelli_dodici.json e .md.
"""
import itertools, json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e27_cartigli as e27

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SEME_NEG, RIMESCOLAMENTI, ERRORI = 280, 2801, 1000, 0.2
ANELLI = (('f67r1', 'Ri', 8, 19), ('f67r2', 'Ls', 52, 63), ('f67r2', 'L0', 1, 12), ('f67v1', 'L0', 1, 12))
MESI = ('ianuarius', 'februarius', 'martius', 'aprilis', 'maius', 'iunius', 'iulius', 'augustus', 'september', 'october', 'nouember', 'december')
G = misure.divisore(misure.GLIFI_EVA)
_SIM = {}


def sim(a, b):
    if (a, b) not in _SIM:
        prec = list(range(len(b) + 1))
        for i in range(1, len(a) + 1):
            cur = [i] + [0] * len(b)
            for j in range(1, len(b) + 1):
                cur[j] = min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (a[i - 1] != b[j - 1]))
            prec = cur
        _SIM[(a, b)] = 1 - prec[-1] / max(len(a), len(b), 1)
    return _SIM[(a, b)]


DISPOSIZIONI = [[(r + s * k) % 12 for k in range(12)] for r in range(12) for s in (1, -1)]


def S(anelli):
    tot = []
    for x, y in itertools.combinations(anelli, 2):
        tot.append(max(statistics.mean(sim(x[k], y[d[k]]) for k in range(12)) for d in DISPOSIZIONI))
    return statistics.mean(tot)


def prova(anelli, rnd):
    vero = S(anelli)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        nulli.append(S([rnd.sample(a, 12) for a in anelli]))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('S', vero), ('nullo', m), ('sd', sd), ('z', (vero - m) / sd if sd else None)])


def etichetta(r):
    return tuple(u for w in r.parole if trascrizione.pulita(w) for u in G(w))


def main():
    rnd = random.Random(SEME)
    righe = list(trascrizione.leggi('ZL'))
    anelli = []
    for pag, tipo, lo, hi in ANELLI:
        a = [etichetta(r) for r in righe if r.pagina == pag and r.tipo == tipo and lo <= r.numero <= hi]
        assert len(a) == 12, (pag, tipo, len(a))
        anelli.append(a)
    segni = [s for s, _ in Counter(u for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))) for u in G(w)).most_common(20)]
    chiave = e27.cifrario_verboso(segni, rnd)
    positivo = []
    for _ in range(4):
        d = rnd.choice(DISPOSIZIONI)
        nomi = [tuple(e27.cifra_nome(m, chiave, segni, rnd, ERRORI)) for m in MESI]
        positivo.append([nomi[d[k]] for k in range(12)])
    usate = {(p, t) for p, t, _, _ in ANELLI}
    altre = [etichetta(r) for r in righe if r.tipo and r.tipo.startswith('L') and (r.pagina, r.tipo) not in usate and etichetta(r)
             and (r.sezione in ('A', 'C', 'Z') or r.pagina.startswith(('f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73')))]
    finestre = [altre[i:i + 12] for i in range(0, len(altre) - 11, 12)]
    rn = random.Random(SEME_NEG)
    rn.shuffle(finestre)
    gruppi = [finestre[4 * g:4 * g + 4] for g in range(6) if len(finestre) >= 4 * g + 4]
    ris = OrderedDict([('anelli', prova(anelli, rnd)), ('positivo', prova(positivo, rnd))])
    for i, g in enumerate(gruppi):
        ris['negativo %d' % (i + 1)] = prova(g, rnd)
    for n, r in ris.items():
        print('%-12s S %.4f nullo %.4f z %.1f' % (n, r['S'], r['nullo'], r['z'] or 0), flush=True)
    zneg = max((ris[n]['z'] or 0) for n in ris if n.startswith('negativo')) if gruppi else float('nan')
    valido = (ris['positivo']['z'] or 0) > 4
    comune = (ris['anelli']['z'] or 0) > 3 and (ris['anelli']['z'] or 0) >= zneg + 2
    esito = 'non valido' if not valido else ('vocabolario comune (nessuna lettura)' if comune else 'nessun vocabolario comune')
    # descrittivo: settori allineati del migliore abbinamento fra i primi due anelli
    d0 = max(DISPOSIZIONI, key=lambda d: statistics.mean(sim(anelli[0][k], anelli[1][d[k]]) for k in range(12)))
    allineati = [(''.join(anelli[0][k]), ''.join(anelli[1][d0[k]])) for k in range(12)]
    json.dump(OrderedDict([('risultati', ris), ('negativi', len(gruppi)), ('finestre', len(finestre)), ('valido', valido), ('esito', esito), ('allineati_1_2', allineati)]),
              open(os.path.join(RISULTATI, 'e280_anelli_dodici.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e280 — I quattro anelli a 12 settori nominano le stesse cose?', '',
          'S = media sulle 6 coppie di anelli della migliore somiglianza media dei settori allineati (24 disposizioni); z contro %d rimescolamenti nell\'anello. '
          'Preregistrazione: `preregistrazioni/e280.md`.' % RIMESCOLAMENTI, '', '| insieme | S | nullo | z |', '|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %.4f | %.4f | %.1f |' % (n, r['S'], r['nullo'], r['z'] or 0))
    md += ['', 'Settori allineati, anelli 1 e 2: ' + '; '.join('%s / %s' % x for x in allineati) + '.', '',
           'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e280_anelli_dodici.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
