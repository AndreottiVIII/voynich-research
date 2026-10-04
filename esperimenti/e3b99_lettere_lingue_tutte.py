# -*- coding: utf-8 -*-
"""Esperimento e3b99: misura dell'e3b80 (accordo con poche contro molte lettere in mezzo) sui 16 testi che contano
nell'e3b98, con la classe generica dell'e3b98.

Preregistrazione: preregistrazioni/e3b99.md. Scrive risultati/e3b99_lettere_lingue_tutte.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b80_memoria_lettere as e3b80
import e3b98_forma_lingue as e3b98

RISULTATI = os.path.join(QUI, '..', 'risultati')
VOYNICH = 0.066
VOLAPUK = 'Conlangs - Volapuk - Literary - NT'


def misura(uu, nome, f, rng):
    c = e3b80.prepara(uu, [nome] * len(uu), f)
    pr = e3b62.prova(OrderedDict([('x', c)]), rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
    return OrderedDict([('coppie_poche', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3299)
    prima = json.load(open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), encoding='utf-8'))['lingue']
    contano = [k for k, x in prima.items() if x['conta'] and x['R'] is not None]
    tt = e381.testi()
    ris = OrderedDict()
    for nome in contano:
        righe = [r for r in tt[nome + '.txt'] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        f, lettere = e3b98.classe_generica([b for u in uu for b in u])
        assert list(lettere) == prima[nome]['lettere']
        ris[nome] = misura(uu, nome, f, rng)
        ris[nome]['R_e3b98'] = prima[nome]['R']
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    sopra = sum(1 for x in ris.values() if x['IC95'][0] > 0)
    mediana = statistics.median(x['effetto'] for x in ris.values())
    if sopra < 3 and mediana < VOYNICH / 2:
        esito = 'il consumo con le lettere distingue'
    elif sopra >= 5 and mediana >= VOYNICH / 2:
        esito = 'non distingue'
    else:
        esito = 'incerto'
    v = ris.get(VOLAPUK)
    volapuk = None if v is None else bool(v['effetto'] >= VOYNICH / 2 and v['IC95'][0] > 0)
    out = OrderedDict([('testi', ris), ('mediana', mediana), ('testi_sopra_zero', sopra), ('esito', esito), ('volapuk_somiglia', volapuk)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b99_lettere_lingue_tutte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b99 — Le lingue del corpus si consumano con le lettere? (classe generica)', '', 'Preregistrazione: `preregistrazioni/e3b99.md`. Voynich (e3b80): +0,066 (ZL e IT).', '',
          '| testo | R (e3b98) | coppie con poche lettere | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %.2f | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (k, x['R_e3b98'], x['coppie_poche'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Effetto mediano %+.4f; testi con intervallo sopra 0: %d. Esito: **%s**. Il Volapük somiglia al Voynich anche qui: %s.' % (
        mediana, sopra, esito, {True: 'sì', False: 'no', None: '—'}[volapuk])]
    open(os.path.join(RISULTATI, 'e3b99_lettere_lingue_tutte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
