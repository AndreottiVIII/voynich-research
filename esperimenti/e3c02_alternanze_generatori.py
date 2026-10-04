# -*- coding: utf-8 -*-
"""Esperimento e3c02: la regola automatica dell'e3c01 (tre alternanze interne dalle coppie minime) sui generatori
(Naibbe, U2, U3, Timm e Schinner): deve dare memoria nulla, come le classi scelte a mano (e3b70).

Preregistrazione: preregistrazioni/e3c02.md. Scrive risultati/e3c02_alternanze_generatori.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3b62_memoria_nullo_largo as e3b62
import e3c01_alternanze_interne as e3c01

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e3b62.D


def generatori():
    gen = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            gen[k] = [r for r in ([w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v) if r]
    gen['Timm e Schinner, seme 1'] = [r for r in ([tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r]
    return gen


def main():
    rng = np.random.default_rng(3302)
    prima = json.load(open(os.path.join(RISULTATI, 'e3c01_alternanze_interne.json'), encoding='utf-8'))
    rif = prima['riferimento_voynich']
    ris = OrderedDict()
    for nome, righe in generatori().items():
        uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
        scelte, punti = e3c01.alternanze(righe)
        classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
        x = e3c01.misura(uu, [nome] * len(uu), classi, rng)
        x['alternanze'] = ['%s/%s' % c for c in scelte]
        x['coppie_minime'] = punti
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    simili = [k for k, x in ris.items() if x['IC95'] and x['IC95'][0] > 0 and x['effetto'] >= rif / 2]
    if not simili:
        esito = 'la regola automatica non trova memoria nei generatori'
    elif len(simili) >= 2:
        esito = 'la regola automatica trova memoria anche nei generatori'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('riferimento_voynich', rif), ('generatori_simili', simili), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c02_alternanze_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c02 — La regola automatica delle alternanze interne sui generatori', '', 'Preregistrazione: `preregistrazioni/e3c02.md`. Riferimento Voynich (e3c01): %+.4f.' % rif, '',
          '| generatore | alternanze | occorrenze | coppie vicine | effetto (IC 95%) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        ef = '—' if x['effetto'] is None or not x['IC95'] else '%+.4f (%+.4f – %+.4f)' % (x['effetto'], x['IC95'][0], x['IC95'][1])
        md.append('| %s | %s | %d | %d | %s |' % (k, ' '.join(x['alternanze']), x['occorrenze'], x['coppie_vicine'], ef))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c02_alternanze_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
