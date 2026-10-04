# -*- coding: utf-8 -*-
"""Esperimento e3b09: differenza vicino - lontano dell'accordo delle scelte di grafia (e3b06/e3b08) nei generatori.

Preregistrazione: preregistrazioni/e3b09.md. Scrive risultati/e3b09_scelte_generatori.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3a58_spazi_prevedibili as e3a58
import e3b06_scelte_riga_distanza as e3b06
import e3b07_scelte_memoria_controlli as e3b07
import e3b08_scelte_differenza as e3b08

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3209)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            righe = [r for r in e3a58.righe_prime([[x for x in ps if x] for _, ps in v]) if r]
            testi[k] = [righe[i:i + 25] for i in range(0, len(righe), 25)]
    testi['Timm e Schinner, seme 1'] = [[list(r) for r in p] for p in e337.pagine_ts(1)]
    ris = OrderedDict()
    for k, pg in testi.items():
        a = e3b08.con_ic(e3b06.coppie(pg), rnd)
        b = e3b08.con_ic(e3b07.coppie_senza_simili(pg), rnd)
        ris[k] = OrderedDict([('tutte', a), ('senza_simili', b), ('esito', 'ha la memoria delle scelte' if b['IC95'][0] > 0 else 'no')])
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b09_scelte_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b09 — I generatori hanno la memoria corta delle scelte di grafia?', '', 'Preregistrazione: `preregistrazioni/e3b09.md`. Voynich (e3b08): +0,031 con tutte le coppie, +0,027 senza parole simili.', '',
          '| generatore | differenza, tutte le coppie | IC 95% | differenza, senza parole simili | IC 95% | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %+.4f | %+.4f – %+.4f | %+.4f | %+.4f – %+.4f | %s |' % (k, x['tutte']['differenza'], x['tutte']['IC95'][0], x['tutte']['IC95'][1], x['senza_simili']['differenza'], x['senza_simili']['IC95'][0], x['senza_simili']['IC95'][1], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3b09_scelte_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
