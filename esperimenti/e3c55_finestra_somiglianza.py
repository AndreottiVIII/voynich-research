# -*- coding: utf-8 -*-
"""Esperimento e3c55: la finestra (misura corretta dell'e3c48) divisa secondo quanto si somigliano le due parole della
coppia (distanza di Levenshtein fra le parole coperte: 2, 3, 4 o più; 0 e 1 sono già escluse dalla misura). Se l'accordo
viene dal copiare parole vicine modificandole (idea di Timm e Schinner), sta soprattutto fra parole simili; se viene da
uno "stato" di chi scrive che dura qualche parola, è uguale fra parole simili e diverse. Voynich ZL e IT (k/t, sh/ch,
-ey/-dy insieme); riferimento: il generatore di Timm e Schinner (copia con modifiche).

Preregistrazione: preregistrazioni/e3c55.md. Scrive risultati/e3c55_finestra_somiglianza.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c02_alternanze_generatori as e3c02
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
CLASSI_D = ('2', '3', '4+')
PERM = 50
BOOT = 2000
_DIST = {}


def classe_d(a, b):
    k = (a, b) if a <= b else (b, a)
    d = _DIST.get(k)
    if d is None:
        d = _DIST[k] = misure.distanza(a, b)
    return None if d <= 1 else min(d, 4) - 2


def somme(tok, n_p):
    """Come e3c33.somme, con in più la classe di distanza fra le parole coperte: (pagine, 3 classi, DMAX, 2)."""
    v, x, tipo, mano, sp, npg, sx, beta = e3c33.preparazione(tok)
    per_riga = defaultdict(dict)
    for j, t in enumerate(tok):
        per_riga[(t[2], t[5])][t[3]] = j
    out = np.zeros((n_p, 3, e3c33.DMAX, 2))
    for (_, k), pos in per_riga.items():
        for i, a in pos.items():
            for d in range(1, e3c33.DMAX + 1):
                b = pos.get(i + d)
                if b is None:
                    continue
                c = classe_d(tok[a][7], tok[b][7])
                if c is None:
                    continue
                ch = (tok[a][0], k)
                if npg[ch] > 2:
                    off = (sp[ch] - v[a] - v[b]) / (npg[ch] - 2)
                    xm = (sx[ch] - x[a] - x[b]) / (npg[ch] - 2)
                    pa = tipo[a] + off - mano[a] + beta[k] * (x[a] - xm)
                    pb = tipo[b] + off - mano[b] + beta[k] * (x[b] - xm)
                else:
                    pa, pb = tipo[a], tipo[b]
                pa, pb = min(max(pa, 0.01), 0.99), min(max(pb, 0.01), 0.99)
                att = pa * pb + (1 - pa) * (1 - pb)
                out[tok[a][0], c, d - 1, 0] += (v[a] == v[b]) - att
                out[tok[a][0], c, d - 1, 1] += 1 - att
    return out


def kappe(s):
    """s (..., 3, DMAX, 2) -> K per classe e distanza (..., 3, DMAX) e K con le distanze 1-3 insieme (..., 3)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return s[..., 0] / s[..., 1], s[..., 0].sum(-1) / s[..., 1].sum(-1)


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    st = somme(tok, n_p)
    k_oss, t_oss = kappe(st.sum(0))
    nk, nt = [], []
    for _ in range(PERM):
        a, b = kappe(somme(e3c48.rimescola(tok, rng), n_p).sum(0))
        nk.append(a)
        nt.append(b)
    k_nul, t_nul = np.mean(nk, 0), np.mean(nt, 0)
    bt = []
    for _ in range(BOOT):
        _, b = kappe(st[rng.integers(0, n_p, n_p)].sum(0))
        bt.append(b - t_nul)
    bt = np.array(bt)
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ris = OrderedDict([('parole', len(tok))])
    coppie = defaultdict(int)
    per_riga = defaultdict(dict)
    for j, t in enumerate(tok):
        per_riga[(t[2], t[5])][t[3]] = j
    for (_, k), pos in per_riga.items():
        for i, a in pos.items():
            for d in range(1, 4):
                b = pos.get(i + d)
                if b is not None:
                    c = classe_d(tok[a][7], tok[b][7])
                    if c is not None:
                        coppie[CLASSI_D[c]] += 1
    ris['coppie'] = dict(coppie)
    for c, nome in enumerate(CLASSI_D):
        ris['distanza ' + nome] = OrderedDict([('K_corretto_per_d', [float(z) for z in k_oss[c] - k_nul[c]]), ('K_corretto', float(t_oss[c] - t_nul[c])),
                                               ('K_osservato', float(t_oss[c])), ('K_nullo', float(t_nul[c])), ('IC95', ic(bt[:, c]))])
    ris['differenza 2 meno 4+'] = OrderedDict([('valore', float((t_oss[0] - t_nul[0]) - (t_oss[2] - t_nul[2]))), ('IC95', ic(bt[:, 0] - bt[:, 2]))])
    return ris


def main():
    rng = np.random.default_rng(3355)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        ris['Voynich ' + q] = x = misura(pagine, cl, rng)
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    righe = e3c02.generatori()['Timm e Schinner, seme 1']
    ris['Timm e Schinner (riferimento)'] = x = misura([('g', righe[i:i + 25]) for i in range(0, len(righe), 25)], cl, rng)
    print('TS', json.dumps(x, ensure_ascii=False), flush=True)

    def voce(x):
        dif = x['differenza 2 meno 4+']['IC95']
        if dif[0] > 0:
            return 'legato alla somiglianza'
        if dif[0] <= 0 <= dif[1] and x['distanza 4+']['IC95'][0] > 0.02:
            return 'uguale per parole simili e diverse'
        return 'incerto'
    voci = OrderedDict((k, voce(x)) for k, x in ris.items())
    a, b = voci['Voynich ZL'], voci['Voynich IT']
    esito = ('accordo legato alla somiglianza (copia)' if a == b == 'legato alla somiglianza' else
             'accordo uguale per parole simili e diverse (stato)' if a == b == 'uguale per parole simili e diverse' else 'incerto')
    out = OrderedDict([('misure', ris), ('voci', voci), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c55_finestra_somiglianza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c55 — La finestra secondo quanto si somigliano le due parole', '', 'Preregistrazione: `preregistrazioni/e3c55.md`. K corretto con le distanze 1–3 nella riga insieme; distanza = Levenshtein fra le parole coperte.', '',
          '| testo | distanza fra le parole | coppie | K osservato | K nullo | K corretto (IC 95%) | K corretto a 1 / 2 / 3 parole |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        for c in CLASSI_D:
            y = x['distanza ' + c]
            md.append('| %s | %s | %d | %+.3f | %+.3f | %+.3f (%+.3f – %+.3f) | %s |' % (k, c, x['coppie'].get(c, 0), y['K_osservato'], y['K_nullo'], y['K_corretto'], y['IC95'][0], y['IC95'][1],
                                                                                     ' / '.join('%+.3f' % z for z in y['K_corretto_per_d'])))
        dd = x['differenza 2 meno 4+']
        md.append('| %s | **differenza 2 meno 4+** | | | | %+.3f (%+.3f – %+.3f) | %s |' % (k, dd['valore'], dd['IC95'][0], dd['IC95'][1], voci[k]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c55_finestra_somiglianza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
