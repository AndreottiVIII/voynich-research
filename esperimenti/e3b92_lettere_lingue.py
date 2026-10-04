# -*- coding: utf-8 -*-
"""Esperimento e3b92: misura dell'e3b80 (accordo con poche contro molte lettere in mezzo) sulle desinenze delle lingue
(classi dell'e3b91).

Preregistrazione: preregistrazioni/e3b92.md. Scrive risultati/e3b92_lettere_lingue.json e .md.
"""
import json, os, sys
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
import e3b91_accordo_lingue as e3b91

RISULTATI = os.path.join(QUI, '..', 'risultati')
VOYNICH = 0.066


def main():
    rng = np.random.default_rng(3292)
    tt = e381.testi()
    ris = OrderedDict()
    for nome, (chiave, tipo) in e3b91.TESTI.items():
        righe = [r for r in tt[chiave] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        f = e3b91.oa if tipo == 'romanzo' else e3b91.usa
        c = e3b80.prepara(uu, [nome] * len(uu), f)
        pr = e3b62.prova(OrderedDict([('x', c)]), rng)['insieme']
        iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
        ris[nome] = OrderedDict([('coppie_poche', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    sopra = sum(1 for x in ris.values() if x['IC95'][0] > 0)
    media = sum(x['effetto'] for x in ris.values()) / len(ris)
    if sopra == 0 or media < VOYNICH / 2:
        esito = 'il consumo con le lettere distingue'
    elif sopra >= 3 and media >= VOYNICH / 2:
        esito = 'non distingue'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('media', media), ('testi_sopra_zero', sopra), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b92_lettere_lingue.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b92 — L\'accordo grammaticale delle lingue si consuma con le lettere?', '', 'Preregistrazione: `preregistrazioni/e3b92.md`. Voynich (e3b80): +0,066 (ZL e IT).', '',
          '| testo | coppie con poche lettere | M | M nullo | effetto (IC 95%) |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) |' % (k, x['coppie_poche'], x['M'], x['nullo'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Media dei testi %+.4f; testi con intervallo sopra 0: %d. Esito: **%s**.' % (media, sopra, esito)]
    open(os.path.join(RISULTATI, 'e3b92_lettere_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
