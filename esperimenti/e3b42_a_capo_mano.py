# -*- coding: utf-8 -*-
"""Esperimento e3b42: la memoria che passa l'a capo nelle pagine "solo testo" togliendo una pagina per volta, e a parità
di mano (mano 2: pagine T contro altre pagine).

Preregistrazione: preregistrazioni/e3b42.md. Scrive risultati/e3b42_a_capo_mano.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b10_scelte_a_capo as e3b10
import e3b38_solo_testo_a_capo as e3b38

RISULTATI = os.path.join(QUI, '..', 'risultati')


def a_cavallo(pagine):
    cc = []
    for pid, pars in enumerate(pagine):
        cc += e3b10.coppie_pagina(pars, pid)
    e = e3b10.eccessi(cc)
    return e['a cavallo'] if 'a cavallo' in e else (None, 0)


def main():
    rnd = random.Random(3242)
    sezione, mano = {}, {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
        mano.setdefault(r.pagina, r.mano)
    pagine = OrderedDict()
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp:
            pagine[pg] = pp
    t = [pg for pg in pagine if sezione.get(pg) == 'T']
    pieno = a_cavallo([pagine[p] for p in t])
    fuori = OrderedDict()
    for p in t:
        v, n = a_cavallo([pagine[q] for q in t if q != p])
        fuori[p] = OrderedDict([('eccesso', v), ('coppie', n)])
    sola = OrderedDict()
    for p in t:
        v, n = a_cavallo([pagine[p]])
        sola[p] = OrderedDict([('eccesso', v), ('coppie', n), ('mano', mano.get(p))])
    vals = [x['eccesso'] for x in fuori.values()]
    if all(v is not None and v > 0.03 for v in vals):
        esito1 = 'non dipende da una pagina'
    elif any(v is None or v < 0.01 for v in vals):
        esito1 = 'dipende da una pagina'
    else:
        esito1 = 'in parte'
    m2t = [pagine[p] for p in pagine if mano.get(p) == '2' and sezione.get(p) == 'T']
    m2a = [pagine[p] for p in pagine if mano.get(p) == '2' and sezione.get(p) != 'T']
    ris_t, ris_a = e3b38.analizza(m2t, rnd), e3b38.analizza(m2a, rnd)
    if ris_t['IC95_a_cavallo'][0] > 0 and ris_a['IC95_a_cavallo'][0] <= 0:
        esito2 = 'stessa mano, comportamento diverso'
    elif ris_t['IC95_a_cavallo'][0] <= 0 <= ris_t['IC95_a_cavallo'][1]:
        esito2 = 'non distinguibile'
    else:
        esito2 = 'incerto'
    out = OrderedDict([('pieno', pieno), ('una_fuori', fuori), ('da_sola', sola), ('esito_1', esito1),
                       ('mano2_T', ris_t), ('mano2_altre', ris_a), ('esito_2', esito2)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b42_a_capo_mano.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b42 — La memoria che passa l\'a capo: una sola pagina? a parità di scriba?', '', 'Preregistrazione: `preregistrazioni/e3b42.md`.', '',
          'Valore pieno (6 pagine T): %+.4f (%d coppie).' % pieno, '', '## Una pagina per volta fuori', '', '| pagina tolta | eccesso a cavallo (coppie) | pagina da sola (coppie, mano) |', '|---|---|---|']
    md += ['| %s | %+.4f (%d) | %+.4f (%d, mano %s) |' % (p, fuori[p]['eccesso'], fuori[p]['coppie'], sola[p]['eccesso'] if sola[p]['eccesso'] is not None else float('nan'), sola[p]['coppie'], sola[p]['mano']) for p in t]
    md += ['', 'Esito 1: **%s**.' % esito1, '', '## Mano 2', '', '| pagine | quante | stessa riga (coppie) | a cavallo (coppie) | IC 95% a cavallo |', '|---|---|---|---|---|']
    for k, x in (('mano 2, solo testo', ris_t), ('mano 2, altre pagine', ris_a)):
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f – %+.4f |' % (k, x['pagine'], x['stessa_riga'], x['coppie_stessa'], x['a_cavallo'], x['coppie_a_cavallo'], x['IC95_a_cavallo'][0], x['IC95_a_cavallo'][1]))
    md += ['', 'Esito 2: **%s**.' % esito2]
    open(os.path.join(RISULTATI, 'e3b42_a_capo_mano.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
