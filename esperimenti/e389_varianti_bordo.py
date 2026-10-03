# -*- coding: utf-8 -*-
"""Esperimento 389: a parita' del resto della parola (tronco o corpo) e dello strato, quali ultimi segni crescono e
quali calano a fine riga, e quali primi segni a inizio riga (righe non d'inizio paragrafo), rispetto al mezzo della
riga; nullo con le etichette bordo/mezzo rimescolate dentro il gruppo.

Preregistrazione: preregistrazioni/e389.md. Scrive risultati/e389_varianti_bordo.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def analizza(eventi, rng):
    """eventi: [(gruppo, al_bordo, segno)]."""
    per = defaultdict(list)
    for g, b, s in eventi:
        per[g].append((b, s))
    gruppi = []
    for g, xs in per.items():
        nb = sum(b for b, _ in xs)
        nm = len(xs) - nb
        if nm >= 5 and nb >= 1:
            gruppi.append(xs)
    segni = sorted({s for xs in gruppi for _, s in xs})
    idx = {s: i for i, s in enumerate(segni)}
    arr = [(np.array([b for b, _ in xs], bool), np.array([idx[s] for _, s in xs])) for xs in gruppi]
    k = len(segni)

    def delta(etich):
        num = np.zeros(k)
        den = 0
        for (b, s), e in zip(arr, etich):
            nb = e.sum()
            nm = len(e) - nb
            pb = np.bincount(s[e], minlength=k) / nb
            pm = np.bincount(s[~e], minlength=k) / nm
            num += nb * (pb - pm)
            den += nb
        return num / den
    vero = delta([b for b, _ in arr])
    nul = np.array([delta([rng.permutation(b) for b, _ in arr]) for _ in range(PERM)])
    m, sd = nul.mean(0), nul.std(0)
    z = np.where(sd > 0, (vero - m) / np.where(sd > 0, sd, 1), 0.0)
    nb_tot = sum(int(b.sum()) for b, _ in arr)
    righe = OrderedDict()
    for i in np.argsort(-z):
        righe[segni[i]] = OrderedDict([('delta', float(vero[i])), ('z', float(z[i]))])
    su = [s for s, x in righe.items() if x['z'] > 3]
    giu = [s for s, x in sorted(righe.items(), key=lambda kv: kv[1]['z']) if x['z'] < -3]
    if su and giu:
        esito = '%s è la variante di bordo di %s' % ('/'.join(su), giu[0])
    elif su:
        esito = 'si aggiungono senza sostituire un segno preciso'
    else:
        esito = 'nessun segno cresce al bordo'
    return OrderedDict([('gruppi', len(arr)), ('parole_al_bordo', nb_tot), ('segni', righe), ('crescono', su), ('calano', giu), ('esito', esito)])


def main():
    rng = np.random.RandomState(389)
    fine, inizio = [], []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        n = len(ws)
        if n < 2:
            continue
        st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
        for j, w in enumerate(ws):
            if len(w) < 2:
                continue
            mezzo = 0 < j < n - 1
            if mezzo or j == n - 1:
                fine.append(((st, w[:-1]), j == n - 1, w[-1]))
            if mezzo or (j == 0 and not r.inizio_par):
                inizio.append(((st, w[1:]), j == 0, w[0]))
    ris = OrderedDict([('fine riga', analizza(fine, rng)), ('inizio riga', analizza(inizio, rng))])
    for k, x in ris.items():
        print(k, x['esito'], json.dumps(OrderedDict(list(x['segni'].items())[:6]), default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e389_varianti_bordo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e389 — Le forme di bordo riga stanno al posto di quali forme normali?', '', 'Preregistrazione: `preregistrazioni/e389.md`. Δ = quanto il segno è più frequente al bordo che in mezzo, a parità del resto della parola e dello strato.', '']
    for k, x in ris.items():
        md += ['## %s (%d gruppi, %d parole al bordo)' % (k, x['gruppi'], x['parole_al_bordo']), '', '| segno | Δ | z |', '|---|---|---|']
        for s, v in x['segni'].items():
            if abs(v['z']) >= 2:
                md.append('| %s | %+.4f | %.1f |' % (s, v['delta'], v['z']))
        md += ['', 'Crescono (z > 3): %s. Calano (z < −3): %s. Esito: **%s**.' % (', '.join(x['crescono']) or 'nessuno', ', '.join(x['calano']) or 'nessuno', x['esito']), '']
    open(os.path.join(RISULTATI, 'e389_varianti_bordo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
