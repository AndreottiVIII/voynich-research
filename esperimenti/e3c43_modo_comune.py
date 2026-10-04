# -*- coding: utf-8 -*-
"""Esperimento e3c43: c'è un "modo marcato" comune a scelte diverse? Con la misura pulita (e3c39: atteso stessa parola +
pagina + deriva; parole interne), K fra parole della stessa riga a distanza 1–3 per coppie della stessa classe e per
coppie di classi diverse (accordo = tutte e due marcate o tutte e due semplici: 1 = qo, k, sh, -ey). ZL e IT.

Preregistrazione: preregistrazioni/e3c43.md. Scrive risultati/e3c43_modo_comune.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c39_finestra_a_capo as e3c39

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
GRUPPI = ('stessa classe', 'classi diverse')


def somme(tok, n_p):
    v, p = e3c39.attese(tok)
    per_riga = defaultdict(list)
    for j, t in enumerate(tok):
        if 0 < t['pos'] < t['L'] - 1:
            per_riga[(t['p'], t['par'], t['riga'])].append(j)
    out = np.zeros((n_p, len(GRUPPI), 3))
    for _, jj in per_riga.items():
        for a in jj:
            for b in jj:
                d = tok[b]['pos'] - tok[a]['pos']
                if not 1 <= d <= 3:
                    continue
                stessa = tok[a]['k'] == tok[b]['k']
                if stessa and (tok[a]['c'] == tok[b]['c'] or e3a86.una_modifica(tok[a]['c'], tok[b]['c'])):
                    continue
                g = 0 if stessa else 1
                att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
                out[tok[a]['p'], g, 0] += (v[a] == v[b]) - att
                out[tok[a]['p'], g, 1] += 1 - att
                out[tok[a]['p'], g, 2] += 1
    return out


def main():
    rng = np.random.default_rng(3343)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        tok = e3c39.raccogli(pd, mano, e3b62.CV)
        n_p = max(t['p'] for t in tok) + 1
        st = somme(tok, n_p)
        s = st.sum(0)
        k = s[:, 0] / s[:, 1]
        boot = []
        for _ in range(BOOT):
            b = st[rng.integers(0, n_p, n_p)].sum(0)
            boot.append(b[:, 0] / b[:, 1])
        boot = np.array(boot)
        ris[q] = OrderedDict((g, OrderedDict([('K', float(k[i])), ('IC95', [float(np.percentile(boot[:, i], 2.5)), float(np.percentile(boot[:, i], 97.5))]), ('coppie', int(s[i, 2]))]))
                             for i, g in enumerate(GRUPPI))
        print(q, json.dumps(ris[q]), flush=True)
    esiti = OrderedDict()
    for q, x in ris.items():
        st_, di = x['stessa classe'], x['classi diverse']
        if di['IC95'][0] > 0 and di['K'] >= st_['K'] / 3:
            esiti[q] = 'modo marcato comune a scelte diverse'
        elif di['IC95'][0] <= 0 or di['K'] < st_['K'] / 4:
            esiti[q] = 'accordo soprattutto dentro ogni scelta'
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c43_modo_comune.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c43 — C\'è un modo marcato comune a scelte diverse?', '', 'Preregistrazione: `preregistrazioni/e3c43.md`. Parole interne, distanza 1–3 nella riga, atteso stessa parola + pagina + deriva; 1 = qo, k, sh, -ey.', '',
          '| trascrizione | stessa classe | classi diverse |', '|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %s |' % (q, ' | '.join('%+.3f (%+.3f – %+.3f), %d coppie' % (x[g]['K'], x[g]['IC95'][0], x[g]['IC95'][1], x[g]['coppie']) for g in GRUPPI)))
    md += [''] + ['Esito %s: **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c43_modo_comune.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
