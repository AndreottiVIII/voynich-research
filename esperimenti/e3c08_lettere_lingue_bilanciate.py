# -*- coding: utf-8 -*-
"""Esperimento e3c08: il consumo con le lettere con la divisione bilanciata dell'e3c07 sulle lingue: i 16 testi
dell'e3b99 (classe generica dell'e3b98) e i 5 testi dell'e3b92 (classi -o/-a, -us/-a dell'e3b91).

Preregistrazione: preregistrazioni/e3c08.md. Scrive risultati/e3c08_lettere_lingue_bilanciate.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b91_accordo_lingue as e3b91
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b98_forma_lingue as e3b98
import e3c07_lettere_parole_bilanciate as e3c07

RISULTATI = os.path.join(QUI, '..', 'risultati')
MODO = 'lettere a parità di parole'


def misura(uu, nome, f, rng, seme):
    """Come e3c07.misura con una classe; None se la misura non è definita (per esempio una classe con un solo valore)."""
    c = e3c07.prepara(uu, [nome] * len(uu), f, MODO, seme)
    pr = e3b62.prova(OrderedDict([('x', c)]), rng)['insieme']
    if pr.get('nullo') is None:
        return None
    iv = e3b70.intervallo([e3b70.per_unita(c)], pr['nullo'], rng)
    return OrderedDict([('coppie_gruppo_0', pr['coppie_vicine']), ('M', pr['M']), ('nullo', pr['nullo']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3308)
    rif = json.load(open(os.path.join(RISULTATI, 'e3c07_lettere_parole_bilanciate.json'), encoding='utf-8'))['trascrizioni']
    voy = min(rif[q][MODO + ', con i bordi']['effetto'] for q in ('ZL', 'IT'))
    prima = json.load(open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), encoding='utf-8'))['lingue']
    tt = e381.testi()
    testi = OrderedDict()
    for nome in (k for k, x in prima.items() if x['conta'] and x['R'] is not None):
        righe = [r for r in tt[nome + '.txt'] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        f, _ = e3b98.classe_generica([b for u in uu for b in u])
        testi[nome + ' (classe generica)'] = (uu, f)
    for nome, (chiave, tipo) in e3b91.TESTI.items():
        righe = [r for r in tt[chiave] if r]
        testi[nome + ' (' + ('-o/-a' if tipo == 'romanzo' else '-us/-a') + ')'] = ([[b] for b in e3b51.blocchi(righe)], e3b91.oa if tipo == 'romanzo' else e3b91.usa)
    ris = OrderedDict()
    for n, (nome, (uu, f)) in enumerate(testi.items()):
        x = misura(uu, nome, f, rng, 3308 + 10 * n)
        print(nome, json.dumps(x, default=float), flush=True)
        if x is not None:
            ris[nome] = x
    sopra = sum(1 for x in ris.values() if x['IC95'][0] > 0)
    mediana = statistics.median(x['effetto'] for x in ris.values())
    if sopra < 3 and mediana < voy / 2:
        esito = 'il consumo con le lettere distingue'
    elif sopra >= 6 and mediana >= voy / 2:
        esito = 'non distingue'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('voynich_riferimento', voy), ('mediana', mediana), ('testi_sopra_zero', sopra), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c08_lettere_lingue_bilanciate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c08 — Consumo con le lettere nelle lingue, divisione bilanciata', '',
          'Preregistrazione: `preregistrazioni/e3c08.md`. Riferimento Voynich (e3c07, bilanciata, con i bordi, il più piccolo fra ZL e IT): %+.4f.' % voy, '',
          '| testo | coppie per gruppo | effetto (IC 95%) |', '|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.4f (%+.4f – %+.4f) |' % (k, x['coppie_gruppo_0'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Mediana %+.4f; testi con intervallo sopra 0: %d su %d. Esito: **%s**.' % (mediana, sopra, len(ris), esito)]
    open(os.path.join(RISULTATI, 'e3c08_lettere_lingue_bilanciate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
