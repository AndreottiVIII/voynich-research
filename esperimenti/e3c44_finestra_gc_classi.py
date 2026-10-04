# -*- coding: utf-8 -*-
"""Esperimento e3c44: la finestra dell'e3c35 nella trascrizione di Glen Claston (v101) per le scelte corrispondenti a quelle
di EVA, ricavate allineando le righe ZL–GC: qo-/o- = 4o-/o-; sh/ch = 2/1; -ey/-dy = -c9, -C9 / -89, -79. Misura
dell'e3c34 (righe di almeno 6 parole senza bordi; atteso stessa parola + pagina + deriva).

Preregistrazione: preregistrazioni/e3c44.md. Scrive risultati/e3c44_finestra_gc_classi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3c05_terza_trascrizione as e3c05
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')


def v_qo(w):
    if len(w) >= 3 and w[0] == '4' and w[1] == 'o':
        return (1, ('*',) + w[1:])
    if len(w) >= 2 and w[0] == 'o':
        return (0, ('*',) + w)
    return None


def v_shch(w):
    pos = [i for i, c in enumerate(w) if c in ('1', '2')]
    if len(pos) != 1:
        return None
    i = pos[0]
    return (1 if w[i] == '2' else 0, w[:i] + ('*',) + w[i + 1:])


def v_eydy(w):
    if len(w) >= 3 and w[-1] == '9' and w[-2] in ('c', 'C', '8', '7'):
        return (1 if w[-2] in ('c', 'C') else 0, w[:-2] + ('*', '9'))
    return None


CLASSI = OrderedDict([('qo/o (4o/o)', v_qo), ('sh/ch (2/1)', v_shch), ('-ey/-dy (c9/89)', v_eydy)])


def main():
    rng = np.random.default_rng(3344)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, ss = e3c05.unita_gc(mano)
    pagine = list(zip(ss, uu))
    ris = OrderedDict()
    for k, f in CLASSI.items():
        ris[k] = e3c34.misura(pagine, OrderedDict([(k, f)]), rng)
        print(k, json.dumps(ris[k]), flush=True)
    esiti = OrderedDict()
    for k in ('sh/ch (2/1)', '-ey/-dy (c9/89)'):
        x = ris[k]
        esiti[k] = 'finestra replicata' if (x['K1_IC95'][0] > 0 and x['R0'] >= 0.5) else ('nessuna finestra' if x['R0'] < 0.3 else 'incerto')
    q = ris['qo/o (4o/o)']
    esiti['qo/o (4o/o)'] = 'replicato (niente accanto, accordo a 2–3 parole)' if (q['K1_IC95'][0] <= 0 <= q['K1_IC95'][1] and (q['K'][1] + q['K'][2]) / 2 > 0.03) else 'non replicato'
    n = sum(1 for k in ('sh/ch (2/1)', '-ey/-dy (c9/89)') if esiti[k] == 'finestra replicata')
    esito = 'finestra replicata in GC per %d scelte su 2 (sh/ch, -ey/-dy); qo/o: %s' % (n, esiti['qo/o (4o/o)'])
    out = OrderedDict([('classi', ris), ('esiti', esiti), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c44_finestra_gc_classi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c44 — La finestra nella trascrizione di Glen Claston con le scelte corrispondenti a EVA', '', 'Preregistrazione: `preregistrazioni/e3c44.md`. EVA (e3c35, ZL/IT): sh/ch R0 0,58/0,73; -ey/-dy 0,63/0,74; qo/o K(1) ≈ 0, K(3) +0,11.', '',
          '| classe (GC) | parole | K(1) (IC 95%) | K(2) | K(3) | R0 (IC 95%) | esito |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f (%.2f – %.2f) | %s |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['R0'], x['R0_IC95'][0], x['R0_IC95'][1], esiti[k]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c44_finestra_gc_classi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
