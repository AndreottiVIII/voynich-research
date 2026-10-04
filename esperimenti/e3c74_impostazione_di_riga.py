# -*- coding: utf-8 -*-
"""Esperimento e3c74: ogni riga ha una sua "impostazione" delle scelte? K corretto (e3c48) per coppie della stessa scelta
(qo/o, k/t, sh/ch, -ey/-dy): (a) nella stessa riga a distanza 5 o più; (b) in due righe consecutive della stessa pagina
(tutte le coppie); (c) in righe a due di distanza nella stessa pagina. Con un'impostazione per riga, (a) è positivo e
(b), (c) circa zero; con uno stato che scorre lungo il testo, (b) è positivo. L'atteso contiene già la pagina. Voynich ZL
e IT.

Preregistrazione: preregistrazioni/e3c74.md. Scrive risultati/e3c74_impostazione_di_riga.json e .md.
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
GRUPPI = ('stessa riga, distanza ≥ 5', 'righe consecutive', 'righe a due di distanza')
PERM = 50
BOOT = 2000


def somme(tok, n_p):
    v, p = e3c68.attese(tok)
    per = defaultdict(list)
    for j, t in enumerate(tok):
        per[(t[0], t[2], t[5])].append(j)
    righe_pag = defaultdict(set)
    for (pg, rid, k) in per:
        righe_pag[pg].add(rid)
    out = np.zeros((n_p, len(GRUPPI), 2))

    def aggiungi(a, b, g):
        if tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
            return
        att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
        out[tok[a][0], g, 0] += (v[a] == v[b]) - att
        out[tok[a][0], g, 1] += 1 - att
    for (pg, rid, k), jj in per.items():
        for a in jj:
            for b in jj:
                if tok[b][3] - tok[a][3] >= 5:
                    aggiungi(a, b, 0)
        for salto, g in ((1, 1), (2, 2)):
            altre = per.get((pg, rid + salto, k))
            if altre:
                for a in jj:
                    for b in altre:
                        aggiungi(a, b, g)
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
    boot = np.array([kappa(oss[i].sum(0)) - kappa(nul[i].sum(0)) for i in (rng.integers(0, n_p, n_p) for _ in range(BOOT))])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ris = OrderedDict([('parole', len(tok))])
    for g, nome in enumerate(GRUPPI):
        ris[nome] = OrderedDict([('K_osservato', float(kappa(oss.sum(0))[g])), ('K_nullo', float(kappa(nul.sum(0))[g])), ('K_corretto', float(kc[g])), ('IC95', ic(boot[:, g]))])
    ris['stessa riga − righe consecutive'] = OrderedDict([('valore', float(kc[0] - kc[1])), ('IC95', ic(boot[:, 0] - boot[:, 1]))])
    return ris


def voce(x):
    a, b = x[GRUPPI[0]], x[GRUPPI[1]]
    dif = x['stessa riga − righe consecutive']
    if b['IC95'][0] > 0:
        return 'lo stato attraversa le righe'
    if a['IC95'][0] > 0.02 and b['IC95'][0] <= 0 <= b['IC95'][1] and dif['IC95'][0] > 0.02:
        return 'ogni riga ha una sua impostazione delle scelte'
    if a['IC95'][0] <= 0 <= a['IC95'][1]:
        return 'nessuna preferenza di riga lontano nella riga'
    return 'incerto'


def main():
    rng = np.random.default_rng(3374)
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
    json.dump(out, open(os.path.join(RISULTATI, 'e3c74_impostazione_di_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c74 — Ogni riga ha una sua impostazione delle scelte?', '', 'Preregistrazione: `preregistrazioni/e3c74.md`.', '',
          '| trascrizione | ' + ' | '.join(GRUPPI) + ' | stessa riga − righe consecutive | voce |', '|---|' + '---|' * (len(GRUPPI) + 2)]
    for q, x in ris.items():
        md.append('| %s | %s | %+.3f (%+.3f – %+.3f) | %s |' % (q, ' | '.join('%+.3f (%+.3f – %+.3f)' % (x[g]['K_corretto'], x[g]['IC95'][0], x[g]['IC95'][1]) for g in GRUPPI),
                                                              x['stessa riga − righe consecutive']['valore'], *x['stessa riga − righe consecutive']['IC95'], x['voce']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c74_impostazione_di_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
