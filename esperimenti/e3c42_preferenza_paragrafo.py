# -*- coding: utf-8 -*-
"""Esperimento e3c42: c'è una preferenza di paragrafo nelle scelte? K (misura pulita dell'e3c39: atteso stessa parola +
pagina + deriva) fra parole interne di righe diverse della stessa pagina, a 2–4 righe di distanza, separato per coppie
nello stesso paragrafo e in paragrafi diversi. Classi k/t, sh/ch, -ey/-dy e qo/o insieme. ZL e IT.

Preregistrazione: preregistrazioni/e3c42.md. Scrive risultati/e3c42_preferenza_paragrafo.json e .md.
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
GRUPPI = ('stesso paragrafo', 'paragrafi diversi')


def somme(tok, n_p):
    v, p = e3c39.attese(tok)
    # numero di riga nella pagina (contando i paragrafi in ordine)
    righe_pag = defaultdict(set)
    for t in tok:
        righe_pag[t['p']].add((t['par'], t['riga']))
    num = {}
    for pg, rr in righe_pag.items():
        for n, (par, riga) in enumerate(sorted(rr)):
            num[(pg, par, riga)] = n
    per_riga = defaultdict(list)
    for j, t in enumerate(tok):
        if 0 < t['pos'] < t['L'] - 1:
            per_riga[(t['p'], num[(t['p'], t['par'], t['riga'])], t['k'])].append(j)
    out = np.zeros((n_p, len(GRUPPI), 3))
    for (pg, n, k), aa in per_riga.items():
        for dr in (2, 3, 4):
            bb = per_riga.get((pg, n + dr, k), [])
            for a in aa:
                for b in bb:
                    if tok[a]['c'] == tok[b]['c'] or e3a86.una_modifica(tok[a]['c'], tok[b]['c']):
                        continue
                    g = 0 if tok[a]['par'] == tok[b]['par'] else 1
                    att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
                    out[pg, g, 0] += (v[a] == v[b]) - att
                    out[pg, g, 1] += 1 - att
                    out[pg, g, 2] += 1
    return out


def main():
    rng = np.random.default_rng(3342)
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
        dif = boot[:, 0] - boot[:, 1]
        ris[q] = OrderedDict([(g, OrderedDict([('K', float(k[i])), ('IC95', [float(np.nanpercentile(boot[:, i], 2.5)), float(np.nanpercentile(boot[:, i], 97.5))]), ('coppie', int(s[i, 2]))]))
                              for i, g in enumerate(GRUPPI)])
        ris[q]['differenza'] = OrderedDict([('valore', float(k[0] - k[1])), ('IC95', [float(np.nanpercentile(dif, 2.5)), float(np.nanpercentile(dif, 97.5))])])
        print(q, json.dumps(ris[q]), flush=True)
    esiti = OrderedDict()
    for q, x in ris.items():
        d = x['differenza']['IC95']
        esiti[q] = 'preferenza di paragrafo' if d[0] > 0 else ('nessuna preferenza di paragrafo dimostrata' if d[0] <= 0 <= d[1] else 'al contrario')
    out = OrderedDict([('trascrizioni', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c42_preferenza_paragrafo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c42 — C\'è una preferenza di paragrafo nelle scelte?', '', 'Preregistrazione: `preregistrazioni/e3c42.md`. Righe a 2–4 righe di distanza nella stessa pagina; quattro classi; atteso stessa parola + pagina + deriva.', '',
          '| trascrizione | stesso paragrafo | paragrafi diversi | differenza |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %+.3f (%+.3f – %+.3f), %d coppie | %+.3f (%+.3f – %+.3f), %d coppie | %+.3f (%+.3f – %+.3f) |' % (
            q, x[GRUPPI[0]]['K'], x[GRUPPI[0]]['IC95'][0], x[GRUPPI[0]]['IC95'][1], x[GRUPPI[0]]['coppie'], x[GRUPPI[1]]['K'], x[GRUPPI[1]]['IC95'][0], x[GRUPPI[1]]['IC95'][1], x[GRUPPI[1]]['coppie'],
            x['differenza']['valore'], x['differenza']['IC95'][0], x['differenza']['IC95'][1]))
    md += [''] + ['Esito %s: **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c42_preferenza_paragrafo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
