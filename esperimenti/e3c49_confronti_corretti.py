# -*- coding: utf-8 -*-
"""Esperimento e3c49: i confronti con lingue e generatori rifatti con la misura corretta per la distorsione (e3c48:
K osservato − K con le scelte rimescolate fra le occorrenze della stessa parola). Lingue: le 21 misure dell'e3c34 (righe
finte con le lunghezze del Voynich, unità di 25 righe); generatori: Naibbe, U2, U3, Timm e Schinner (k/t, sh/ch, -ey/-dy).

Preregistrazione: preregistrazioni/e3c49.md. Scrive risultati/e3c49_confronti_corretti.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b98_forma_lingue as e3b98
import e3c02_alternanze_generatori as e3c02
import e3c28_forma_alla_pari as e3c28
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')


def main():
    e3c48.PERM = 20
    rng = np.random.default_rng(3349)
    prima = json.load(open(os.path.join(RISULTATI, 'e3c48_finestra_corretta.json'), encoding='utf-8'))['varianti']
    soglia = min(prima['Voynich %s, pagine intere' % q]['r_IC95'][0] for q in ('ZL', 'IT'))
    k1v = min(prima['Voynich %s, pagine intere' % q]['K_corretto'][0] for q in ('ZL', 'IT'))
    lung = e3c28.lunghezze_voynich()
    tt = e381.testi()
    testi = OrderedDict()
    lingue98 = json.load(open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), encoding='utf-8'))['lingue']
    for nome in (k for k, x in lingue98.items() if x['conta'] and x['R'] is not None):
        parole = [w for r in tt[nome + '.txt'] if r for w in r]
        f, _ = e3b98.classe_generica([parole])
        testi[nome + ' (classe generica)'] = (parole, f)
    for nome, (chiave, t) in e3b91.TESTI.items():
        parole = [w for r in tt[chiave] if r for w in r]
        testi[nome + ' (' + ('-o/-a' if t == 'romanzo' else '-us/-a') + ')'] = (parole, e3b91.oa if t == 'romanzo' else e3b91.usa)
    ris = OrderedDict()
    for nome, (parole, f) in testi.items():
        rr = e3c28.righe_finte(parole, lung)
        x = e3c48.misura([('x', rr[i:i + 25]) for i in range(0, len(rr), 25)], OrderedDict([('x', f)]), rng)
        x['conta'] = x['K1_IC95'][0] > 0.02
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    gen = OrderedDict()
    for nome, righe in e3c02.generatori().items():
        x = e3c48.misura([('g', righe[i:i + 25]) for i in range(0, len(righe), 25)], OrderedDict((k, e3b62.CV[k]) for k in TRE), rng)
        x['finestra'] = x['K1_IC95'][0] > 0.02 and x['K23_IC95'][0] > 0.02
        gen[nome] = x
        print(nome, json.dumps(x), flush=True)
    lingue = [k for k, x in ris.items() if x['conta'] and np.isfinite(x['r'])]
    sopra = [k for k in lingue if ris[k]['r'] >= soglia]
    if not sopra:
        esito_l = 'la finestra resta propria del Voynich'
    elif len(sopra) >= 3:
        esito_l = 'la finestra non è propria del Voynich'
    else:
        esito_l = 'incerto'
    gfin = [k for k, x in gen.items() if x['finestra']]
    esito_g = 'nessun generatore ha la finestra' if not gfin else 'finestra in: ' + ', '.join(gfin)
    out = OrderedDict([('lingue', ris), ('generatori', gen), ('soglia_r', soglia), ('lingue_sopra', sopra), ('esito_lingue', esito_l), ('esito_generatori', esito_g)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c49_confronti_corretti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c49 — Confronti con lingue e generatori, con la misura corretta per la distorsione', '',
          'Preregistrazione: `preregistrazioni/e3c49.md`. Voynich (e3c48, pagine intere): K corretto +0,131 / +0,093 / +0,086 (ZL), r 0,68 (0,53 – 0,84); IT r 0,66 (0,53 – 0,82).', '',
          '| testo | K osservato 1/2/3 | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2/3 | r (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in list(ris.items()) + list(gen.items()):
        md.append('| %s | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f | %.2f (%.2f – %.2f) |' % (
            k, ' '.join('%+.3f' % z for z in x['K_osservato']), ' '.join('%+.3f' % z for z in x['K_nullo']), x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1],
            x['K_corretto'][1], x['K_corretto'][2], x['r'], x['r_IC95'][0], x['r_IC95'][1]))
    md += ['', 'Soglia r: %.2f. Lingue che contano sopra la soglia: %s.' % (soglia, ', '.join(sopra) or 'nessuna'), '',
           'Esito lingue: **%s**. Esito generatori: **%s**.' % (esito_l, esito_g)]
    open(os.path.join(RISULTATI, 'e3c49_confronti_corretti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
