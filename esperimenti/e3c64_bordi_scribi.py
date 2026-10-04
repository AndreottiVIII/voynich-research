# -*- coding: utf-8 -*-
"""Esperimento e3c64: le forme di bordo riga negli scribi veri (batteria scribi, 5). Metodo dell'e389: a parità del
resto della parola, quanto un ultimo segno è più frequente a fine riga che in mezzo (e un primo segno a inizio riga),
contro il nullo con le etichette bordo/mezzo rimescolate nel gruppo. Voynich ZL rifatto nella stessa esecuzione (e389:
-m a fine riga Δ +0,151; s-/y- a inizio riga +0,098 / +0,092). Negli scribi si escludono a inizio riga le parole che
cominciano con una maiuscola (inizio di frase o di capitolo, non una forma di bordo).

Preregistrazione: preregistrazioni/e3c64.md. Scrive risultati/e3c64_bordi_scribi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e389_varianti_bordo as e389
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANOSCRITTI = ['AM-519a-4to', 'AM-677-4to', 'AM-60-4to', 'AM-242-fol', 'Holm-A-10', 'AM-302-fol']
PERM = 1000


def maiuscola(g):
    if g.startswith('&'):
        return g[1:2].isupper()
    return g.isupper()


def eventi_voynich():
    fine, inizio = [], []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(e389.D(w)) for w in r.parole if trascrizione.pulita(w)]
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
    return fine, inizio


def eventi_scriba(ms):
    fine, inizio = [], []
    for _, h, rr in e3c58.leggi(ms):
        for r in rr:
            ws = [tuple(w) for w in r if len(w) >= 2]
            n = len(r)
            if n < 2:
                continue
            for j, w in enumerate(r):
                w = tuple(w)
                if len(w) < 2:
                    continue
                mezzo = 0 < j < n - 1
                if mezzo or j == n - 1:
                    fine.append(((h, w[:-1]), j == n - 1, w[-1]))
                if (mezzo or j == 0) and not maiuscola(w[0]):
                    inizio.append(((h, w[1:]), j == 0, w[0]))
    return fine, inizio


def massimo(x):
    """Il segno che cresce di più al bordo con z > 3 (Δ, segno, z) o None."""
    su = [(v['delta'], s, v['z']) for s, v in x['segni'].items() if v['z'] > 3 and v['delta'] > 0]
    return max(su) if su else None


def main():
    e389.PERM = PERM
    rng = np.random.RandomState(3364)
    ris = OrderedDict()
    f, i = eventi_voynich()
    ris['Voynich ZL'] = OrderedDict([('fine riga', e389.analizza(f, rng)), ('inizio riga', e389.analizza(i, rng))])
    print('Voynich', json.dumps({k: list(v['segni'].items())[:3] for k, v in ris['Voynich ZL'].items()}, ensure_ascii=False, default=float), flush=True)
    for ms in MANOSCRITTI:
        f, i = eventi_scriba(ms)
        ris[ms] = OrderedDict([('fine riga', e389.analizza(f, rng)), ('inizio riga', e389.analizza(i, rng))])
        print(ms, json.dumps({k: list(v['segni'].items())[:3] for k, v in ris[ms].items()}, ensure_ascii=False, default=float), flush=True)
    soglie = OrderedDict((b, massimo(ris['Voynich ZL'][b])[0] / 2) for b in ('fine riga', 'inizio riga'))
    forti, deboli = [], []
    for ms in MANOSCRITTI:
        for b in ('fine riga', 'inizio riga'):
            m = massimo(ris[ms][b])
            if m is None:
                continue
            (forti if m[0] >= soglie[b] else deboli).append('%s, %s: %s (Δ %+.3f, z %.1f)' % (ms, b, m[1], m[0], m[2]))
    if forti:
        esito = 'almeno uno scriba ha forme di bordo forti come il Voynich'
    elif deboli:
        esito = 'gli scribi hanno forme di bordo, ma più deboli della metà del Voynich'
    else:
        esito = 'nessuna forma di bordo negli scribi'
    out = OrderedDict([('misure', ris), ('soglie', soglie), ('forti', forti), ('deboli', deboli), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c64_bordi_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c64 — Le forme di bordo riga negli scribi veri', '', 'Preregistrazione: `preregistrazioni/e3c64.md`. Δ = quanto il segno è più frequente al bordo che in mezzo, a parità del resto della parola (metodo dell\'e389).', '',
          '| testo | bordo | gruppi | parole al bordo | segni che crescono (Δ, z > 3) | segni che calano (z < −3) |', '|---|---|---|---|---|---|']
    for k, v in ris.items():
        for b, x in v.items():
            su = ', '.join('%s %+.3f (z %.1f)' % (s, x['segni'][s]['delta'], x['segni'][s]['z']) for s in x['crescono'][:5]) or 'nessuno'
            giu = ', '.join('%s %+.3f' % (s, x['segni'][s]['delta']) for s in x['calano'][:4]) or 'nessuno'
            md.append('| %s | %s | %d | %d | %s | %s |' % (k, b, x['gruppi'], x['parole_al_bordo'], su, giu))
    md += ['', 'Soglie (metà del segno che cresce di più nel Voynich): fine riga %.3f, inizio riga %.3f.' % (soglie['fine riga'], soglie['inizio riga']), '',
           'Esito: **%s**.' % esito, '', 'Forti: %s.' % ('; '.join(forti) or 'nessuno'), '', 'Deboli: %s.' % ('; '.join(deboli) or 'nessuno')]
    open(os.path.join(RISULTATI, 'e3c64_bordi_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
