# -*- coding: utf-8 -*-
"""Esperimento e3c91: la finestra dello scriba svedese di Holm A 10 (ꝛ/r; trovata come "presente" nell'e3c90) è uno
"stato" come quello del Voynich (accordo anche fra parole molto diverse) o una copia di parole vicine (accordo solo fra
parole simili)? Stessa prova dell'e3c79 (AM 302 fol), senza cambi. Misura
dell'e3c55 (K corretto con le coppie a 1 – 3 parole insieme, divise per la distanza di Levenshtein fra le parole coperte:
2, 3, 4 o più). Riferimento: i valori del Voynich dell'e3c55.

Preregistrazione: preregistrazioni/e3c91.md. Scrive risultati/e3c91_holm_stato_o_copia.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c55_finestra_somiglianza as e3c55
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')


def voce(x):
    dif = x['differenza 2 meno 4+']['IC95']
    if dif[0] > 0:
        return 'legato alla somiglianza (copia)'
    if dif[0] <= 0 <= dif[1] and x['distanza 4+']['IC95'][0] > 0.02:
        return 'uguale per parole simili e diverse (stato)'
    return 'incerto'


def main():
    rng = np.random.default_rng(3391)
    pagine = [(h, rr) for _, h, rr in e3c58.leggi('Holm-A-10')]
    x = e3c55.misura(pagine, OrderedDict([('ꝛ/r', e3c58.scelta(['ꝛ', '&rrot;'], ['r']))]), rng)
    x['voce'] = voce(x)
    print(json.dumps(x, ensure_ascii=False), flush=True)
    voy = json.load(open(os.path.join(RISULTATI, 'e3c55_finestra_somiglianza.json'), encoding='utf-8'))['misure']['Voynich ZL']
    out = OrderedDict([('Holm A 10, ꝛ/r', x), ('Voynich ZL (e3c55)', voy), ('esito', x['voce'])])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c91_holm_stato_o_copia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c91 — La finestra dello scriba di Holm A 10 (ꝛ/r): stato o copia?', '', 'Preregistrazione: `preregistrazioni/e3c91.md`.', '',
          '| testo | distanza fra le parole | coppie | K corretto (IC 95%) |', '|---|---|---|---|']
    for nome, y in (('Holm A 10, ꝛ/r', x), ('Voynich ZL (e3c55)', voy)):
        for c in e3c55.CLASSI_D:
            z = y['distanza ' + c]
            md.append('| %s | %s | %d | %+.3f (%+.3f – %+.3f) |' % (nome, c, y['coppie'].get(c, 0), z['K_corretto'], z['IC95'][0], z['IC95'][1]))
        d = y['differenza 2 meno 4+']
        md.append('| %s | **differenza 2 − 4+** | | %+.3f (%+.3f – %+.3f) |' % (nome, d['valore'], d['IC95'][0], d['IC95'][1]))
    md += ['', 'Esito: **%s**.' % x['voce']]
    open(os.path.join(RISULTATI, 'e3c91_holm_stato_o_copia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
