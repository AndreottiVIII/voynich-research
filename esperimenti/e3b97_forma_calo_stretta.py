# -*- coding: utf-8 -*-
"""Esperimento e3b97: e3b96 togliendo le coppie con parole coperte a distanza di modifica <= 2.

Preregistrazione: preregistrazioni/e3b97.md. Scrive risultati/e3b97_forma_calo_stretta.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b96_forma_calo as e3b96

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def modifiche(a, b, tetto=3):
    """Distanza di modifica fra due tuple (si ferma a 'tetto')."""
    if abs(len(a) - len(b)) >= tetto:
        return tetto
    prec = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (x != y)))
        prec = cur
    return min(prec[-1], tetto)


def main():
    rnd = random.Random(3297)
    originale = e3a86.una_modifica
    e3a86.una_modifica = lambda a, b: modifiche(a, b) <= 2
    try:
        mano = {}
        for r in trascrizione.leggi('ZL'):
            mano.setdefault(r.pagina, r.mano)
        testi = OrderedDict()
        for q, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
            uu, _ = e3b62.voynich(pd, mano)
            testi[q] = (uu, e3b62.CV)
        righe = [r for r in e381.testi()['Modern - Italian - Literary - NT.txt'] if r]
        testi['italiano NT moderno'] = ([[b] for b in e3b51.blocchi(righe)], OrderedDict([('x', e3b91.oa)]))
        ris = OrderedDict()
        for nome, (u, cl) in testi.items():
            ss = [e3b96.somme_unita(x, cl) for x in u]
            r = e3b96.rapporto(ss)
            boot = sorted(x for x in (e3b96.rapporto([ss[rnd.randrange(len(ss))] for _ in ss]) for _ in range(BOOT)) if x is not None)
            ris[nome] = OrderedDict([('R', r), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]), ('unita', len(u))])
            print(nome, json.dumps(ris[nome]), flush=True)
    finally:
        e3a86.una_modifica = originale
    v, it = ris['Voynich IT'], ris['italiano NT moderno']
    if v['R'] > 0.5 and v['IC95'][0] > it['IC95'][1]:
        esito = 'la forma piatta regge'
    elif v['R'] < 0.4:
        esito = 'la forma piatta veniva dalle parole simili'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b97_forma_calo_stretta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b97 — La forma piatta della memoria del Voynich regge togliendo anche le parole a due modifiche?', '', 'Preregistrazione: `preregistrazioni/e3b97.md`. e3b96: Voynich IT 0,79; italiano NT moderno 0,17.', '',
          '| testo | unità | R (IC 95%) |', '|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.2f (%.2f – %.2f) |' % (k, x['unita'], x['R'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b97_forma_calo_stretta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
