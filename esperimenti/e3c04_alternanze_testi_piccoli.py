# -*- coding: utf-8 -*-
"""Esperimento e3c04: la regola dell'e3c01 (tre alternanze interne dalle coppie minime, memoria e3b62 + e3b70) sui
testi in lingue naturali del corpus fra 10.000 e 50.000 parole (erbari e testi tecnici medievali compresi).

Preregistrazione: preregistrazioni/e3c04.md. Scrive risultati/e3c04_alternanze_testi_piccoli.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3c01_alternanze_interne as e3c01

RISULTATI = os.path.join(QUI, '..', 'risultati')
MINIMO, MASSIMO = 10000, 50000


def scelti(tt):
    out = OrderedDict()
    for chiave, righe in tt.items():
        righe = [r for r in righe if r]
        n = sum(len(r) for r in righe)
        if chiave.startswith('Conlangs') or 'Abbreviated' in chiave or not MINIMO <= n < MASSIMO:
            continue
        out[chiave.replace('.txt', '')] = righe
    return out


def main():
    rng = np.random.default_rng(3304)
    rif = json.load(open(os.path.join(RISULTATI, 'e3c01_alternanze_interne.json'), encoding='utf-8'))['riferimento_voynich']
    ris = OrderedDict()
    for nome, righe in scelti(e381.testi()).items():
        uu = [[b] for b in e3b51.blocchi(righe)]
        scelte, punti = e3c01.alternanze([b for u in uu for b in u])
        classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
        x = e3c01.misura(uu, [nome] * len(uu), classi, rng)
        x['parole'] = sum(len(r) for r in righe)
        x['alternanze'] = ['%s/%s' % c for c in scelte]
        x['coppie_minime'] = punti
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    simili = [k for k, x in ris.items() if x['IC95'] and x['IC95'][0] > 0 and x['effetto'] >= rif / 2]
    if len(simili) <= 1:
        esito = 'le alternanze interne hanno memoria solo nel Voynich anche fra i testi piccoli'
    elif len(simili) >= 3:
        esito = 'anche i testi piccoli'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('riferimento_voynich', rif), ('testi_simili', simili), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c04_alternanze_testi_piccoli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c04 — Le alternanze interne hanno memoria nei testi piccoli (erbari e testi tecnici)?', '', 'Preregistrazione: `preregistrazioni/e3c04.md`. Riferimento Voynich (e3c01): %+.4f.' % rif, '',
          '| testo | parole | alternanze | occorrenze | coppie vicine | memoria (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        ef = '—' if x['effetto'] is None or not x['IC95'] else '%+.4f (%+.4f – %+.4f)' % (x['effetto'], x['IC95'][0], x['IC95'][1])
        md.append('| %s | %d | %s | %d | %d | %s |' % (k, x['parole'], ' '.join(x['alternanze']), x['occorrenze'], x['coppie_vicine'], ef))
    md += ['', 'Testi con intervallo sopra 0 ed effetto almeno metà del Voynich: %s.' % (', '.join(simili) or 'nessuno'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c04_alternanze_testi_piccoli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
