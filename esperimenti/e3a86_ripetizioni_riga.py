# -*- coding: utf-8 -*-
"""Esperimento e3a86: ripetizioni nella stessa riga (immediate, quasi immediate, a distanza 2-4) nel Voynich vero e
riscritto riga per riga dalla catena di ordine 2 (come e3a78).

Preregistrazione: preregistrazioni/e3a86.md. Scrive risultati/e3a86_ripetizioni_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NOMI = ('ripetizione immediata', 'quasi ripetizione immediata', 'ritorno nella riga (distanza 2-4)')


def una_modifica(a, b):
    if a == b:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if abs(len(a) - len(b)) != 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


def proprieta(pagine):
    rip = [0, 0]
    quasi = [0, 0]
    ritorno = [0, 0]
    for pars in pagine:
        for par in pars:
            for r in par:
                for a, b in zip(r, r[1:]):
                    if len(a) >= 2 and len(b) >= 2:
                        rip[0] += a == b
                        rip[1] += 1
                    if len(a) >= 3 and len(b) >= 3:
                        quasi[0] += una_modifica(a, b)
                        quasi[1] += 1
                for i in range(len(r)):
                    for k in (2, 3, 4):
                        if i + k < len(r) and len(r[i]) >= 3 and len(r[i + k]) >= 3:
                            ritorno[0] += r[i] == r[i + k]
                            ritorno[1] += 1
    return OrderedDict([(NOMI[0], rip[0] / rip[1]), (NOMI[1], quasi[0] / quasi[1]), (NOMI[2], ritorno[0] / ritorno[1])])


def main():
    rnd = random.Random(3186)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append([par for par in pp if par])
    vero = proprieta(pagine)
    print('vero', json.dumps(vero, ensure_ascii=False), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    risc = [proprieta(e3a78.riscrivi(pagine, tab, rnd)) for _ in range(e3a78.RISCRITTURE)]
    sintesi = OrderedDict()
    for n in NOMI:
        rv = statistics.mean(x[n] for x in risc)
        R = rv / vero[n] if vero[n] else None
        es = 'n.d.' if R is None else ('la catena la riproduce' if R >= 0.75 else ('in parte' if R >= 0.25 else 'serve un meccanismo in più'))
        sintesi[n] = OrderedDict([('vero', vero[n]), ('riscritto', [x[n] for x in risc]), ('riscritto_media', rv), ('R', R), ('esito', es)])
    print(json.dumps(sintesi, ensure_ascii=False, indent=1), flush=True)
    json.dump(OrderedDict([('sintesi', sintesi)]), open(os.path.join(RISULTATI, 'e3a86_ripetizioni_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a86 — Le parole ripetute nella stessa riga sono più di quelle che la catena di segni produce?', '', 'Preregistrazione: `preregistrazioni/e3a86.md`.', '',
          '| proprietà | Voynich vero | riscritto (media) | R | esito |', '|---|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %s | %s |' % (n, x['vero'], x['riscritto_media'], '%.2f' % x['R'] if x['R'] is not None else 'n.d.', x['esito']) for n, x in sintesi.items()]
    open(os.path.join(RISULTATI, 'e3a86_ripetizioni_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
