# -*- coding: utf-8 -*-
"""Esperimento e3b90: e3b73 (memoria alla fine del paragrafo) senza la prima parola del paragrafo nuovo.

Preregistrazione: preregistrazioni/e3b90.md. Scrive risultati/e3b90_paragrafo_prima_parola.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e395_takahashi as e395
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b73_memoria_paragrafo_pagina as e3b73
import e3b89_a_capo_prima_parola as e3b89

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
META_DENTRO = 0.044


def analisi(casi, quote, rnd):
    sm = {k: e3b89.somme(casi, quote, k, e3b89.coppie_senza_prima) for k in ('sotto', 'c1', 'c2')}
    unita = list(casi)

    def dd(pp):
        ks = {k: e3b64.kappa([sm[k][u] for u in pp])[0] for k in sm}
        if None in ks.values():
            return None
        return ks['sotto'] - (ks['c1'] + ks['c2']) / 2
    d = dd(unita)
    boot = sorted(x for x in (dd([rnd.choice(unita) for _ in unita]) for _ in range(BOOT)) if x is not None)
    return OrderedDict([('pagine', len(unita)), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]),
                        ('coppie_continuazione', int(sum(sm['sotto'][u][2] for u in unita)))])


def main():
    rnd = random.Random(3290)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(q)]
        quote = e3b64.quote_pagine(righe, e3b62.CV)
        ris[q] = analisi(e3b73.casi_paragrafo(e3b73.strutture(righe)), quote, rnd)
        print(q, json.dumps(ris[q]), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95'][0] > 0 and it['D'] > 0:
        esito = 'passa anche la fine del paragrafo'
    elif z['IC95'][0] <= 0 <= z['IC95'][1] and z['IC95'][1] < META_DENTRO:
        esito = 'riparte con il paragrafo'
    else:
        esito = 'non dimostrato'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b90_paragrafo_prima_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b90 — Alla fine del paragrafo la memoria riparte, o è la prima parola del paragrafo?', '', 'Preregistrazione: `preregistrazioni/e3b90.md`. e3b73 (tutte le coppie): ZL −0,015, IT −0,018.', '',
          '| trascrizione | pagine | D senza la prima parola (IC 95%) | coppie di continuazione |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %+.4f (%+.4f – %+.4f) | %d |' % (q, x['pagine'], x['D'], x['IC95'][0], x['IC95'][1], x['coppie_continuazione']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b90_paragrafo_prima_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
