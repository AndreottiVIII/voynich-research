# -*- coding: utf-8 -*-
"""Esperimento 247c: la correlazione fra scarti consecutivi (e247, e247b) resta togliendo lo slittamento della riga (mediana
dei Delta delle altre coppie della stessa riga)?

Preregistrazione: preregistrazioni/e247c.md. Scrive risultati/e247c_slittamento_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e247b_copia_in_sequenza as e247b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 2472, 200


def residui_corr(pr, solo_resto):
    a, b = [], []
    for key, v in pr.items():
        if len(v) < 4:
            continue
        for i in range(len(v) - 1):
            x, y = v[i], v[i + 1]
            if y[0] != x[0] + 1:
                continue
            if solo_resto and (y[1] - x[1]) in (0, 1):
                continue
            altri = [d for t, (_, _, d) in enumerate(v) if t not in (i, i + 1)]
            if len(altri) < 2:
                continue
            m = statistics.median(altri)
            a.append(x[2] - m)
            b.append(y[2] - m)
    return (float(np.corrcoef(a, b)[0, 1]) if len(a) > 10 else None), len(a)


def main():
    rnd = random.Random(SEME)
    pr = e247b.coppie_con_indice()
    ris = OrderedDict()
    for nome, solo in (('tutte le coppie consecutive', False), ('coppie non a passo 0 o +1', True)):
        vera, n = residui_corr(pr, solo)
        nulli = []
        for _ in range(REPLICHE):
            m = OrderedDict()
            for key, v in pr.items():
                ds = [d for _, _, d in v]
                rnd.shuffle(ds)
                m[key] = [(j, t, d) for (j, t, _), d in zip(v, ds)]
            nulli.append(residui_corr(m, solo)[0])
        mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        ris[nome] = OrderedDict([('coppie', n), ('residuo', vera), ('nullo', mu), ('z', (vera - mu) / sd if sd else None)])
        print(nome, dict(ris[nome]), flush=True)
    z = ris['coppie non a passo 0 o +1']['z'] or 0
    ris['esito'] = 'slittamento di riga' if abs(z) <= 2 else ('struttura non spiegata, da esaminare' if abs(z) > 3 else 'incerto')
    json.dump(ris, open(os.path.join(RISULTATI, 'e247c_slittamento_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e247c — La correlazione degli scarti è uno slittamento di riga?', '',
          'Residui = Δ meno la mediana dei Δ delle altre coppie della stessa riga; nullo: %d rimescolamenti dei Δ nella riga. '
          'Preregistrazione: `preregistrazioni/e247c.md`.' % REPLICHE, '', '| coppie | n | correlazione dei residui | nulla | z |', '|---|---|---|---|---|']
    for nome in ('tutte le coppie consecutive', 'coppie non a passo 0 o +1'):
        r = ris[nome]
        md.append('| %s | %d | %.3f | %.3f | %.1f |' % (nome, r['coppie'], r['residuo'], r['nullo'], r['z'] or 0))
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e247c_slittamento_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
