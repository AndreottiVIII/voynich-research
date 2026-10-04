# -*- coding: utf-8 -*-
"""Esperimento e3c48: la misura dell'e3c34 corretta per la sua distorsione: K_corretto(d) = K osservato − media di K con le
scelte rimescolate fra le occorrenze della stessa parola coperta (nella mano / nel testo), che non hanno accordo vero ma
hanno lo stesso rumore dell'atteso. Unità = pagine intere o blocchi di 5 righe (Voynich ZL e IT, k/t + sh/ch + -ey/-dy);
unità di 25 o 5 righe finte (Hatton, þ/ð a inizio parola).

Preregistrazione: preregistrazioni/e3c48.md. Scrive risultati/e3c48_finestra_corretta.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3c28_forma_alla_pari as e3c28
import e3c33_riga_o_memoria as e3c33

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 50
BOOT = 2000
TRE = ('k/t', 'sh/ch', '-ey/-dy')


def rimescola(tok, rng):
    gruppi = defaultdict(list)
    for j, t in enumerate(tok):
        gruppi[(t[1], t[5], t[7])].append(j)
    v = [t[6] for t in tok]
    nuovo = list(v)
    for jj in gruppi.values():
        vals = [v[j] for j in jj]
        rng.shuffle(vals)
        for j, x in zip(jj, vals):
            nuovo[j] = x
    return [t[:6] + (x,) + t[7:] for t, x in zip(tok, nuovo)]


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    st = e3c33.somme(tok, n_p)
    k_oss = st.sum(0)[:, 0] / st.sum(0)[:, 1]
    nul = []
    for _ in range(PERM):
        s = e3c33.somme(rimescola(tok, rng), n_p).sum(0)
        nul.append(s[:, 0] / s[:, 1])
    k_nul = np.mean(nul, axis=0)
    boot = []
    for _ in range(BOOT):
        s = st[rng.integers(0, n_p, n_p)].sum(0)
        boot.append(s[:, 0] / s[:, 1] - k_nul)
    boot = np.array(boot)
    kc = k_oss - k_nul
    r = (kc[1] + kc[2]) / 2 / kc[0] if kc[0] > 0 else float('nan')
    br = (boot[:, 1] + boot[:, 2]) / 2 / boot[:, 0]
    return OrderedDict([('parole', len(tok)), ('K_osservato', [float(z) for z in k_oss]), ('K_nullo', [float(z) for z in k_nul]),
                        ('K_corretto', [float(z) for z in kc]), ('K1_IC95', [float(np.percentile(boot[:, 0], 2.5)), float(np.percentile(boot[:, 0], 97.5))]),
                        ('K23_IC95', [float(np.percentile((boot[:, 1] + boot[:, 2]) / 2, 2.5)), float(np.percentile((boot[:, 1] + boot[:, 2]) / 2, 97.5))]),
                        ('r', float(r)), ('r_IC95', [float(np.nanpercentile(br, 2.5)), float(np.nanpercentile(br, 97.5))])])


def main():
    rng = np.random.default_rng(3348)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine, blocchi = [], []
        for pg, pars in pd.items():
            if not mano.get(pg):
                continue
            righe = [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]
            pagine.append((mano[pg], righe))
            for i in range(0, len(righe), 5):
                blocchi.append((mano[pg], righe[i:i + 5]))
        for nome, pp in (('pagine intere', pagine), ('blocchi di 5 righe', blocchi)):
            ris['Voynich %s, %s' % (q, nome)] = x = misura(pp, cl, rng)
            print(q, nome, json.dumps(x), flush=True)
    parole = [w for r in e381.testi()[e3b54.STORICI['Hatton Gospels']] if r for w in r]
    rr = e3c28.righe_finte(parole, e3c28.lunghezze_voynich())
    for n in (25, 5):
        ris['Hatton þ/ð, unità di %d righe' % n] = x = misura([('x', rr[i:i + n]) for i in range(0, len(rr), n)], OrderedDict([('th', e3b54.v_th_ini)]), rng)
        print('Hatton', n, json.dumps(x), flush=True)
    esiti = OrderedDict()
    for q in ('ZL', 'IT'):
        x = ris['Voynich %s, blocchi di 5 righe' % q]
        if x['K1_IC95'][0] > 0 and x['r'] >= 0.5 and x['K23_IC95'][0] > 0:
            esiti[q] = 'la finestra regge anche togliendo le preferenze di tratti di 5 righe'
        elif x['r'] < 0.3 or x['K23_IC95'][0] <= 0:
            esiti[q] = 'la finestra del Voynich viene in gran parte da preferenze di tratti brevi'
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('varianti', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c48_finestra_corretta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c48 — La finestra corretta per la distorsione della misura', '', 'Preregistrazione: `preregistrazioni/e3c48.md`. K corretto = K osservato − K con le scelte rimescolate (50 volte). r = media di K(2) e K(3) corretti divisa per K(1) corretto.', '',
          '| variante | parole | K osservato 1/2/3 | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) |' % (
            k, x['parole'], ' '.join('%+.3f' % z for z in x['K_osservato']), ' '.join('%+.3f' % z for z in x['K_nullo']),
            x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['r_IC95'][0], x['r_IC95'][1]))
    md += [''] + ['Esito %s (blocchi di 5 righe): **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c48_finestra_corretta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
