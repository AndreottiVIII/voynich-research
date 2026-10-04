# -*- coding: utf-8 -*-
"""Esperimento e3c41: le scelte si accordano anche fra parole una sopra l'altra (righe consecutive, stessa posizione nella
riga), vicine sulla pagina ma lontane nella scrittura? Misura pulita dell'e3c39 (atteso stessa parola + pagina + deriva):
K fra parole interne della stessa riga a distanza 1 (riferimento), fra la parola in posizione i di una riga e quella in
posizione i della riga sotto (verticale), e controllo con la riga di due sotto. Stesso paragrafo. Classi k/t, sh/ch,
-ey/-dy insieme. ZL e IT.

Preregistrazione: preregistrazioni/e3c41.md. Scrive risultati/e3c41_accordo_verticale.json e .md.
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
TRE = ('k/t', 'sh/ch', '-ey/-dy')
GRUPPI = ('stessa riga, d = 1', 'riga sotto, stessa posizione', 'controllo: due righe sotto')


def somme(tok, n_p):
    v, p = e3c39.attese(tok)
    idx = defaultdict(dict)
    for j, t in enumerate(tok):
        idx[(t['p'], t['par'], t['riga'], t['k'])][t['pos']] = j
    out = np.zeros((n_p, len(GRUPPI), 3))

    def aggiungi(a, b, g):
        if tok[a]['c'] == tok[b]['c'] or e3a86.una_modifica(tok[a]['c'], tok[b]['c']):
            return
        att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
        out[tok[a]['p'], g, 0] += (v[a] == v[b]) - att
        out[tok[a]['p'], g, 1] += 1 - att
        out[tok[a]['p'], g, 2] += 1
    for (pg, par, riga, k), pos in idx.items():
        for i, a in pos.items():
            if not 0 < i < tok[a]['L'] - 1:
                continue
            if (i + 1) in pos and i + 1 < tok[a]['L'] - 1:
                aggiungi(a, pos[i + 1], 0)
            for g, dr in ((1, 1), (2, 2)):
                b = idx.get((pg, par, riga + dr, k), {}).get(i)
                if b is not None and 0 < i < tok[b]['L'] - 1:
                    aggiungi(a, b, g)
    return out


def main():
    rng = np.random.default_rng(3341)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        tok = e3c39.raccogli(pd, mano, OrderedDict((k, e3b62.CV[k]) for k in TRE))
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
        rif, ver, ctrl = (x[g] for g in GRUPPI)
        if ver['IC95'][0] > ctrl['IC95'][1]:
            esiti[q] = 'accordo verticale: conta anche la vicinanza sulla pagina'
        elif ver['IC95'][0] <= ctrl['K'] <= ver['IC95'][1] and ver['K'] - ctrl['K'] < rif['K'] / 3:
            esiti[q] = 'nessun accordo verticale: conta la sequenza della scrittura'
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c41_accordo_verticale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c41 — Le scelte si accordano fra parole una sopra l\'altra?', '', 'Preregistrazione: `preregistrazioni/e3c41.md`. Classi k/t, sh/ch, -ey/-dy; atteso stessa parola + pagina + deriva; parole interne.', '',
          '| trascrizione | ' + ' | '.join(GRUPPI) + ' |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %s |' % (q, ' | '.join('%+.3f (%+.3f – %+.3f), %d coppie' % (x[g]['K'], x[g]['IC95'][0], x[g]['IC95'][1], x[g]['coppie']) for g in GRUPPI)))
    md += [''] + ['Esito %s: **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c41_accordo_verticale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
