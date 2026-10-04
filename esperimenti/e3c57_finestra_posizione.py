# -*- coding: utf-8 -*-
"""Esperimento e3c57: la finestra corretta (e3c48) con un nullo che conserva la posizione nella riga. Il nullo dell'e3c48
rimescola le scelte fra le occorrenze della stessa parola coperta in qualunque punto della riga; se le scelte dipendono
dalla posizione in modo non lineare (la deriva è più ripida all'inizio della riga, e3c13 – e3c20), parole vicine hanno
posizioni simili e la parte non lineare della deriva passa per "finestra". Qui tre nulli, con le somme per pagina:

- A: dentro (mano, classe, parola coperta) = e3c48;
- P: dentro (mano, classe, parola coperta, fascia di posizione) — fasce sui segni prima della parola: ≤10, 11–20, 21–30,
  31–40, 41+ (come e3c14, più una fascia);
- R (placebo): come P ma con le fasce rimescolate a caso dentro ogni gruppo (stesse dimensioni dei gruppi, nessun legame
  con la posizione), per separare l'effetto della posizione da quello di gruppi più piccoli.

Preregistrazione: preregistrazioni/e3c57.md. Scrive risultati/e3c57_finestra_posizione.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
PERM = 50
BOOT = 2000


def fascia(segni):
    return min(max(segni - 1, 0) // 10, 4)


def rimescola(tok, rng, chiave):
    gruppi = defaultdict(list)
    for j, t in enumerate(tok):
        gruppi[chiave(j, t)].append(j)
    nuovo = [t[6] for t in tok]
    for jj in gruppi.values():
        vals = [tok[j][6] for j in jj]
        rng.shuffle(vals)
        for j, x in zip(jj, vals):
            nuovo[j] = x
    return [t[:6] + (x,) + t[7:] for t, x in zip(tok, nuovo)]


def chiavi(tok, rng):
    fa = [fascia(t[4]) for t in tok]
    # placebo: le fasce rimescolate dentro ogni (mano, classe, parola coperta)
    gruppi = defaultdict(list)
    for j, t in enumerate(tok):
        gruppi[(t[1], t[5], t[7])].append(j)
    fr = list(fa)
    for jj in gruppi.values():
        ff = [fa[j] for j in jj]
        rng.shuffle(ff)
        for j, f in zip(jj, ff):
            fr[j] = f
    return OrderedDict([('A', lambda j, t: (t[1], t[5], t[7])),
                        ('P', lambda j, t: (t[1], t[5], t[7], fa[j])),
                        ('R', lambda j, t: (t[1], t[5], t[7], fr[j]))])


def kappa(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        return s[..., 0] / s[..., 1]


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    oss = e3c33.somme(tok, n_p)
    nulli = OrderedDict()
    for nome in ('A', 'P', 'R'):
        acc = np.zeros_like(oss)
        for _ in range(PERM):
            ch = chiavi(tok, rng)[nome]
            acc += e3c33.somme(rimescola(tok, rng, ch), n_p)
        nulli[nome] = acc / PERM
    ris = OrderedDict([('parole', len(tok)), ('K_osservato', [float(z) for z in kappa(oss.sum(0))])])
    boot = defaultdict(list)
    for _ in range(BOOT):
        idx = rng.integers(0, n_p, n_p)
        ko = kappa(oss[idx].sum(0))
        for nome, nu in nulli.items():
            kc = ko - kappa(nu[idx].sum(0))
            boot[nome].append(np.array([kc[0], (kc[1] + kc[2]) / 2]))
        boot['R−P'].append(boot['R'][-1] - boot['P'][-1])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ko = kappa(oss.sum(0))
    for nome, nu in nulli.items():
        kc = ko - kappa(nu.sum(0))
        b = np.array(boot[nome])
        ris['nullo ' + nome] = OrderedDict([('K_nullo', [float(z) for z in kappa(nu.sum(0))]), ('K_corretto', [float(z) for z in kc]),
                                            ('K1_IC95', ic(b[:, 0])), ('K23', float((kc[1] + kc[2]) / 2)), ('K23_IC95', ic(b[:, 1]))])
    b = np.array(boot['R−P'])
    ris['R meno P'] = OrderedDict([('K1', float(ris['nullo R']['K_corretto'][0] - ris['nullo P']['K_corretto'][0])), ('K1_IC95', ic(b[:, 0])),
                                   ('K23', float(ris['nullo R']['K23'] - ris['nullo P']['K23'])), ('K23_IC95', ic(b[:, 1]))])
    return ris


def voce(x):
    p, r = x['nullo P'], x['nullo R']
    if p['K1_IC95'][0] > 0.02 and p['K23_IC95'][0] > 0.02:
        return 'la finestra non viene dalla posizione nella riga'
    if p['K23_IC95'][0] <= 0 <= p['K23_IC95'][1] and r['K23_IC95'][0] > 0.02:
        return 'la finestra viene in buona parte dalla posizione'
    return 'incerto'


def main():
    rng = np.random.default_rng(3357)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        x = misura(pagine, cl, rng)
        x['voce'] = voce(x)
        ris['Voynich ' + q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    a, b = ris['Voynich ZL']['voce'], ris['Voynich IT']['voce']
    esito = a if a == b else 'ZL: %s; IT: %s' % (a, b)
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c57_finestra_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c57 — La finestra con un nullo che conserva la posizione nella riga', '', 'Preregistrazione: `preregistrazioni/e3c57.md`. A = nullo dell\'e3c48; P = con la fascia di posizione; R = placebo (fasce a caso, stessi gruppi).', '',
          '| testo | nullo | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2–3 (IC 95%) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        for n in ('A', 'P', 'R'):
            y = x['nullo ' + n]
            md.append('| %s | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) |' % (k, n, ' '.join('%+.3f' % z for z in y['K_nullo']), y['K_corretto'][0], y['K1_IC95'][0], y['K1_IC95'][1], y['K23'], y['K23_IC95'][0], y['K23_IC95'][1]))
        y = x['R meno P']
        md.append('| %s | **R − P (parte dovuta alla posizione)** | | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) |' % (k, y['K1'], y['K1_IC95'][0], y['K1_IC95'][1], y['K23'], y['K23_IC95'][0], y['K23_IC95'][1]))
        md.append('| %s | voce | | %s | |' % (k, x['voce']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c57_finestra_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
