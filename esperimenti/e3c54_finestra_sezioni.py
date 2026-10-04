# -*- coding: utf-8 -*-
"""Esperimento e3c54: la finestra (misura corretta dell'e3c48; k/t, sh/ch, -ey/-dy insieme) per gruppi di pagine: erbario
A, erbario B, biologia, farmacia, stelle/ricette, il resto; e per lingua di Currier A e B. ZL e IT.

Preregistrazione: preregistrazioni/e3c54.md. Scrive risultati/e3c54_finestra_sezioni.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48
import e3c52_eva_per_scelta as e3c52

RISULTATI = os.path.join(QUI, '..', 'risultati')
TRE = ('k/t', 'sh/ch', '-ey/-dy')
MINIMO = 1500
GRUPPI = OrderedDict([
    ('erbario A', lambda s, l: s == 'H' and l == 'A'),
    ('erbario B', lambda s, l: s == 'H' and l == 'B'),
    ('biologia', lambda s, l: s == 'B'),
    ('farmacia', lambda s, l: s == 'P'),
    ('stelle / ricette', lambda s, l: s == 'S'),
    ('il resto (astronomia, cosmologia, zodiaco, solo testo)', lambda s, l: s not in ('H', 'B', 'P', 'S')),
    ('lingua A', lambda s, l: l == 'A'),
    ('lingua B', lambda s, l: l == 'B'),
])
SEZIONI = list(GRUPPI)[:6]


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3354)
    mano, sez, lin = {}, {}, {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
        if r.sezione:
            sez.setdefault(r.pagina, r.sezione)
        if r.lingua:
            lin.setdefault(r.pagina, r.lingua)
    cl = OrderedDict((k, e3b62.CV[k]) for k in TRE)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        tutte = [(pg, mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        for g, f in GRUPPI.items():
            pagine = [(h, rr) for pg, h, rr in tutte if f(sez.get(pg), lin.get(pg))]
            e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
            n = len(e3c33.raccogli(pagine, cl))
            k = '%s, %s' % (q, g)
            if n < MINIMO:
                ris[k] = OrderedDict([('pagine', len(pagine)), ('parole', n), ('misurabile', False), ('voce', 'non misurabile')])
                print(k, 'non misurabile', n, flush=True)
                continue
            x = e3c48.misura(pagine, cl, rng)
            x['pagine'], x['misurabile'], x['voce'] = len(pagine), True, e3c52.voce(x)
            ris[k] = x
            print(k, json.dumps(x, ensure_ascii=False), flush=True)
    mis = [g for g in SEZIONI if ris['ZL, ' + g]['misurabile'] or ris['IT, ' + g]['misurabile']]
    manca = [g for g in mis if all(ris['%s, %s' % (q, g)]['voce'] == 'nessun accordo chiaro' for q in ('ZL', 'IT') if ris['%s, %s' % (q, g)]['misurabile'])]
    tutte_f = all(any(ris['%s, %s' % (q, g)]['voce'] == 'finestra' for q in ('ZL', 'IT')) for g in mis)
    if manca:
        esito = 'la finestra manca in qualche sezione: ' + ', '.join(manca)
    elif tutte_f:
        esito = 'la finestra è di tutto il manoscritto'
    else:
        esito = 'incerto'
    lingue = OrderedDict((g, '; '.join('%s: %s' % (q, ris['%s, %s' % (q, g)]['voce']) for q in ('ZL', 'IT'))) for g in ('lingua A', 'lingua B'))
    out = OrderedDict([('gruppi', ris), ('sezioni_misurabili', mis), ('esito', esito), ('lingue', lingue)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c54_finestra_sezioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c54 — La finestra sezione per sezione e in lingua A e B, con la misura corretta', '',
          'Preregistrazione: `preregistrazioni/e3c54.md`. Tutto il manoscritto (e3c48, ZL): K corretto +0,131 / +0,093 / +0,086, r 0,68.', '',
          '| trascrizione, gruppo | pagine | parole | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) | voce |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if not x['misurabile']:
            md.append('| %s | %d | %d | | | | non misurabile |' % (k, x['pagine'], x['parole']))
            continue
        md.append('| %s | %d | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s |' % (
            k, x['pagine'], x['parole'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2],
            x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['r_IC95'][0], x['r_IC95'][1], x['voce']))
    md += ['', 'Esito sezioni: **%s**.' % esito, ''] + ['- %s: %s' % kv for kv in lingue.items()]
    open(os.path.join(RISULTATI, 'e3c54_finestra_sezioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
