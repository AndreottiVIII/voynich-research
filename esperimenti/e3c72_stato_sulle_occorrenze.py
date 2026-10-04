# -*- coding: utf-8 -*-
"""Esperimento e3c72: lo stato delle scelte si trasmette di parola in parola o di occorrenza in occorrenza della scelta?
Coppie della stessa scelta a distanza 2 e 3 nella riga, divise secondo quante parole in mezzo fanno la stessa scelta
(0, 1, 2). K corretto (e3c48) per gruppo, con lo stesso nullo; differenze con intervalli per pagine. Nasce
dall'osservazione non preregistrata dell'e3c68 (con la parola in mezzo fuori dalla scelta l'accordo a distanza 2 è più
basso). Voynich ZL e IT, qo/o, k/t, sh/ch, -ey/-dy.

Preregistrazione: preregistrazioni/e3c72.md. Scrive risultati/e3c72_stato_sulle_occorrenze.json e .md.
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
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48
import e3c68_segno_che_azzera as e3c68

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
GRUPPI = ('d2, in mezzo 0', 'd2, in mezzo 1', 'd3, in mezzo 0', 'd3, in mezzo 1', 'd3, in mezzo 2')
PERM = 50
BOOT = 2000


def somme(tok, n_p):
    v, p = e3c68.attese(tok)
    idx = defaultdict(dict)
    for j, t in enumerate(tok):
        idx[(t[2], t[5])][t[3]] = j
    out = np.zeros((n_p, len(GRUPPI), 2))
    for (_, k), pos in idx.items():
        for i, a in pos.items():
            for d in (2, 3):
                b = pos.get(i + d)
                if b is None or tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                    continue
                n_in = sum(1 for x in range(i + 1, i + d) if x in pos)
                g = GRUPPI.index('d%d, in mezzo %d' % (d, n_in))
                att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
                out[tok[a][0], g, 0] += (v[a] == v[b]) - att
                out[tok[a][0], g, 1] += 1 - att
    return out


def kappa(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        return s[..., 0] / s[..., 1]


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    oss = somme(tok, n_p)
    nul = np.mean([somme(e3c48.rimescola(tok, rng), n_p) for _ in range(PERM)], axis=0)
    kc = kappa(oss.sum(0)) - kappa(nul.sum(0))
    boot = []
    for _ in range(BOOT):
        i = rng.integers(0, n_p, n_p)
        boot.append(kappa(oss[i].sum(0)) - kappa(nul[i].sum(0)))
    boot = np.array(boot)
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ris = OrderedDict([('parole', len(tok))])
    for g, nome in enumerate(GRUPPI):
        ris[nome] = OrderedDict([('coppie_pesate', float(oss.sum(0)[g, 1])), ('K_corretto', float(kc[g])), ('IC95', ic(boot[:, g]))])
    ris['d2: 1 − 0'] = OrderedDict([('valore', float(kc[1] - kc[0])), ('IC95', ic(boot[:, 1] - boot[:, 0]))])
    ris['d3: 2 − 0'] = OrderedDict([('valore', float(kc[4] - kc[2])), ('IC95', ic(boot[:, 4] - boot[:, 2]))])
    return ris


def voce(x):
    a, b = x['d2: 1 − 0']['IC95'], x['d3: 2 − 0']['IC95']
    if a[0] > 0 and b[0] > 0:
        return 'lo stato passa per le occorrenze della scelta'
    if a[1] < 0 and b[1] < 0:
        return 'segno opposto: le occorrenze in mezzo indeboliscono lo stato'
    if a[0] <= 0 <= a[1] and b[0] <= 0 <= b[1]:
        return 'lo stato non dipende dalle occorrenze in mezzo'
    return 'incerto'


def main():
    rng = np.random.default_rng(3372)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        x = misura(pagine, cl, rng)
        x['voce'] = voce(x)
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    a, b = ris['ZL']['voce'], ris['IT']['voce']
    esito = a if a == b else 'ZL: %s; IT: %s' % (a, b)
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c72_stato_sulle_occorrenze.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c72 — Lo stato passa di parola in parola o di occorrenza in occorrenza?', '', 'Preregistrazione: `preregistrazioni/e3c72.md`. "in mezzo n" = quante parole fra le due fanno la stessa scelta.', '',
          '| trascrizione | ' + ' | '.join(GRUPPI) + ' | d2: 1 − 0 | d3: 2 − 0 | voce |', '|---|' + '---|' * (len(GRUPPI) + 3)]
    for q, x in ris.items():
        md.append('| %s | %s | %s | %s | %s |' % (q, ' | '.join('%+.3f (%+.3f – %+.3f)' % (x[g]['K_corretto'], x[g]['IC95'][0], x[g]['IC95'][1]) for g in GRUPPI),
                                               '%+.3f (%+.3f – %+.3f)' % (x['d2: 1 − 0']['valore'], *x['d2: 1 − 0']['IC95']),
                                               '%+.3f (%+.3f – %+.3f)' % (x['d3: 2 − 0']['valore'], *x['d3: 2 − 0']['IC95']), x['voce']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c72_stato_sulle_occorrenze.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
