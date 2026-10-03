# -*- coding: utf-8 -*-
"""Esperimento 340: controllo dell'e338. (E1p) fonte nelle 2 righe sopra, con il nullo che rimescola le righe dentro il
paragrafo; (E2m) stessa colonna, solo parole in mezzo alla riga. Controllo positivo: il generatore di Timm e Schinner.

Preregistrazione: preregistrazioni/e340.md. Scrive risultati/e340_autocitazione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e310_inizi_etichette as e310
import e337_posizione as e337

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NULLI = 200


def pagine_voynich():
    """Pagine con almeno 10 righe: lista di paragrafi, ognuno lista di righe (parole)."""
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                pars = per.setdefault(r.pagina, [])
                if r.inizio_par or not pars:
                    pars.append([])
                pars[-1].append(ws)
    return [v for v in per.values() if sum(len(p) for p in v) >= 10]


def prepara(pagina):
    tipi = sorted({w for par in pagina for r in par for w in r})
    idx = {w: k for k, w in enumerate(tipi)}
    u = [tuple(D(w)) for w in tipi]
    M = np.zeros((len(tipi), len(tipi)), dtype=bool)
    for a in range(len(tipi)):
        M[a, a] = True
        for b in range(a + 1, len(tipi)):
            if abs(len(u[a]) - len(u[b])) <= 1 and e310.dist1(u[a], u[b]):
                M[a, b] = M[b, a] = True
    return [[[idx[w] for w in r] for r in par] for par in pagina], M


def misura(prep, rnd):
    def E1(ordini):
        si = tot = 0
        for (pars, M), op in zip(prep, ordini):
            for par, o in zip(pars, op):
                if len(par) < 4:
                    continue
                rr = [par[k] for k in o]
                for i in range(2, len(rr)):
                    sopra = rr[i - 1] + rr[i - 2]
                    for w in rr[i]:
                        tot += 1
                        si += bool(M[w, sopra].any())
        return si / tot

    def E2(rimescola):
        si = tot = 0
        for pars, M in prep:
            for par in pars:
                for i in range(1, len(par)):
                    sopra = par[i - 1][1:-1]
                    pos = list(range(1, len(par[i - 1]) - 1))
                    if rimescola:
                        pos = rnd.sample(pos, len(pos))
                    for j in range(1, len(par[i]) - 1):
                        w = par[i][j]
                        hit = [p for p, x in zip(pos, sopra) if M[w, x]]
                        if hit:
                            tot += 1
                            si += any(abs(p - j) <= 1 for p in hit)
        return si / tot if tot else 0.0
    base = [[list(range(len(par))) for par in pars] for pars, _ in prep]
    v1 = E1(base)
    n1 = [E1([[rnd.sample(b, len(b)) for b in bp] for bp in base]) for _ in range(NULLI)]
    v2 = E2(False)
    n2 = [E2(True) for _ in range(NULLI)]
    return OrderedDict([('pagine', len(prep)), ('fonte_2_righe', v1), ('nullo_dentro_paragrafo', statistics.mean(n1)), ('E1p', v1 - statistics.mean(n1)),
                        ('z_E1p', (v1 - statistics.mean(n1)) / statistics.pstdev(n1)), ('stessa_colonna_mezzo', v2), ('nullo_colonna', statistics.mean(n2)),
                        ('E2m', v2 - statistics.mean(n2)), ('z_E2m', (v2 - statistics.mean(n2)) / statistics.pstdev(n2))])


def main():
    rnd = random.Random(340)
    testi = OrderedDict([('Voynich', [prepara(p) for p in pagine_voynich()])])
    for s in (1, 19):
        testi['Timm e Schinner, seme %d' % s] = [prepara([pag]) for pag in e337.pagine_ts(s)]
    ris = OrderedDict()
    for n, prep in testi.items():
        ris[n] = misura(prep, rnd)
        print(n, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in ris[n].items()}, flush=True)
    gen = [v for n, v in ris.items() if n != 'Voynich']
    valido = all(v['z_E1p'] > 3 and v['z_E2m'] > 3 for v in gen)
    v = ris['Voynich']
    if not valido:
        esito = 'non valido'
    elif v['z_E1p'] > 3 and v['z_E2m'] > 3:
        esito = 'copia dalle righe sopra'
    elif v['z_E1p'] < 2 and v['z_E2m'] < 2:
        esito = 'solo lessico di paragrafo e posizione'
    else:
        esito = 'parziale (regge %s)' % ' e '.join(k for k in ('E1p', 'E2m') if v['z_' + k] > 3) if (v['z_E1p'] > 3 or v['z_E2m'] > 3) else 'parziale'
    json.dump(OrderedDict([('testi', ris), ('valido', valido), ('esito', esito)]), open(os.path.join(RISULTATI, 'e340_autocitazione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e340 — Autocitazione: copia vera o effetti di paragrafo e di posizione?', '', 'Preregistrazione: `preregistrazioni/e340.md`.', '',
          '| testo | pagine | fonte nelle 2 righe sopra | nullo (dentro il paragrafo) | E1p | z | stessa colonna (parole in mezzo) | nullo | E2m | z |', '|---|---|---|---|---|---|---|---|---|---|']
    for n, x in ris.items():
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %.1f | %.3f | %.3f | %+.4f | %.1f |' % (n, x['pagine'], x['fonte_2_righe'], x['nullo_dentro_paragrafo'], x['E1p'], x['z_E1p'],
                                                                                         x['stessa_colonna_mezzo'], x['nullo_colonna'], x['E2m'], x['z_E2m']))
    md += ['', 'Valido: %s. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e340_autocitazione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
