# -*- coding: utf-8 -*-
"""Esperimento e3c46: le scelte grafiche libere di scribi medievali veri con la misura pulita (e3c34: righe di almeno 6
parole senza bordi; atteso stessa parola + pagina + deriva), testi tagliati in righe finte con le lunghezze del Voynich
(e3c28): Codex Marianus и/ꙇ a inizio parola (e3b75; tutte le parole e solo quelle di almeno 2 segni, cioè senza la
congiunzione, e3b76); Hatton Gospels þ/ð a inizio parola e dentro la parola (e3b54).

Preregistrazione: preregistrazioni/e3c46.md. Scrive risultati/e3c46_scribi_veri.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b54_memoria_oltre_parole as e3b54
import e3b75_marianus as e3b75
import e3c28_forma_alla_pari as e3c28
import e3c34_finestra_tre_parole as e3c34

RISULTATI = os.path.join(QUI, '..', 'risultati')


def lunghe(f):
    return lambda w: f(w) if len(w) >= 2 else None


PROVE = OrderedDict([
    ('Codex Marianus, и/ꙇ a inizio parola', (e3b75.CHIAVE, e3b75.i_iniziale)),
    ('Codex Marianus, и/ꙇ, parole di almeno 2 segni', (e3b75.CHIAVE, lunghe(e3b75.i_iniziale))),
    ('Hatton Gospels, þ/ð a inizio parola', (e3b54.STORICI['Hatton Gospels'], e3b54.v_th_ini)),
    ('Hatton Gospels, þ/ð dentro la parola', (e3b54.STORICI['Hatton Gospels'], e3b54.v_th_int)),
])


def tipo(x):
    k1, k2, k3 = x['K']
    if x['K1_IC95'][0] <= 0:
        return 'nessun accordo fra parole accanto dimostrato'
    r = (k2 + k3) / 2 / k1
    if r >= 0.5:
        return 'come il Voynich (l\'accordo dura fino a 3 parole)'
    if r < 0.3:
        return 'come le lingue (l\'accordo crolla dopo la parola accanto)'
    return 'intermedio'


def main():
    rng = np.random.default_rng(3346)
    tt = e381.testi()
    lung = e3c28.lunghezze_voynich()
    ris = OrderedDict()
    for nome, (chiave, f) in PROVE.items():
        parole = [w for r in tt[chiave] if r for w in r]
        rr = e3c28.righe_finte(parole, lung)
        x = e3c34.misura([('x', rr[i:i + 25]) for i in range(0, len(rr), 25)], OrderedDict([(nome, f)]), rng)
        x['tipo'] = tipo(x)
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c46_scribi_veri.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c46 — Le scelte libere di scribi medievali veri con la misura pulita', '', 'Preregistrazione: `preregistrazioni/e3c46.md`. Voynich (e3c34–e3c35): K(1) +0,12 – +0,15, K(2) e K(3) +0,06 – +0,10.', '',
          '| scriba e scelta | parole | K(1) (IC 95%) | K(2) | K(3) | tipo |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %s |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2], x['tipo']))
    open(os.path.join(RISULTATI, 'e3c46_scribi_veri.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
