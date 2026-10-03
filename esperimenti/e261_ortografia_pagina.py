# -*- coding: utf-8 -*-
"""Esperimento 261: la mistura dell'e259b (base, cache, varianti pesate, lettere, lettere della pagina) applicata ai testi dei
generatori: hanno il peso delle "lettere della pagina" del Voynich?

Preregistrazione: preregistrazioni/e261.md. Scrive risultati/e261_ortografia_pagina.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241
import e259_bit_per_parola as e259
import e259b_varianti_pesate as e259b

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    vp, vu = e259.voynich()
    c = e224.contesto()
    pv = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    g241 = list(e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102)).values())
    g192 = list(e231.generatore_e192(1).values())
    ris = OrderedDict()
    for nome, pag in (('Voynich', vp), ('generatore e241 (seme 2)', g241), ('generatore e192 (seme 1)', g192)):
        ris[nome] = e259b.prova(nome, pag, vu)
    pv_ = ris['Voynich']['pesi_completo']['lettere della pagina']
    esiti = OrderedDict()
    for nome in list(ris)[1:]:
        pg = ris[nome]['pesi_completo']['lettere della pagina']
        esiti[nome] = 'ortografia di pagina mancante' if pg < 0.5 * pv_ else 'presente'
    ris['esiti'] = esiti
    json.dump(ris, open(os.path.join(RISULTATI, 'e261_ortografia_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e261 — I generatori hanno l\'"ortografia di pagina" del Voynich?', '',
          "Mistura dell'e259b. Preregistrazione: `preregistrazioni/e261.md`.", '',
          '| testo | bit/parola (completa) | pesi (base, cache, varianti, lettere, lettere della pagina) | esito |', '|---|---|---|---|']
    for nome in list(ris)[:3]:
        r = ris[nome]
        md.append('| %s | %.2f | %s | %s |' % (nome, r['bit']['+ cache + lettere della pagina'], ', '.join('%.2f' % x for x in r['pesi_completo'].values()),
                                            esiti.get(nome, 'riferimento')))
    open(os.path.join(RISULTATI, 'e261_ortografia_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esiti)


if __name__ == '__main__':
    main()
