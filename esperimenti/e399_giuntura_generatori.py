# -*- coding: utf-8 -*-
"""Esperimento 399: giuntura nella riga e a capo (misura dell'e384) nei generatori pubblicati (Naibbe, U2, U3, Timm e
Schinner) contro il Voynich.

Preregistrazione: preregistrazioni/e399.md. Scrive risultati/e399_giuntura_generatori.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e341_fonti as e341
import e384_giuntura_a_capo as e384

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def blocchi_voynich():
    out = []
    for pag, pars in e341.pagine().items():
        corti = []
        for par in pars:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            if len(rr) >= 4:
                out.append([rr])
            else:
                corti.append(rr)
        if corti:
            out.append(corti)
    return out


def blocchi_righe(righe, alt=29):
    rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in righe]
    rr = [r for r in rr if r]
    return [[rr[i:i + alt]] for i in range(0, len(rr), alt)]


def main():
    rnd = random.Random(399)
    e134.controlla()
    t = e134.testi()
    corpi = OrderedDict([('Voynich', blocchi_voynich())])
    for k, v in t.items():
        if k != 'Voynich':
            corpi[k] = blocchi_righe([ps for _, ps in v])
    for s in (1, 19):
        corpi['Timm e Schinner, seme %d' % s] = [[[[tuple(D(w)) for w in r] for r in p]] for p in e337.pagine_ts(s)]
    ris = OrderedDict()
    for k, b in corpi.items():
        x, _ = e384.misura(b, rnd)
        ris[k] = x
        print(k, json.dumps(x, default=float), flush=True)
    Ev = ris['Voynich']['riga']['E']
    riprod = [k for k, x in ris.items() if k != 'Voynich' and x['riga']['E'] >= 0.5 * Ev and x['Q'] is not None and x['Q'] < 0.3]
    esito = ('un generatore riproduce la giuntura del Voynich: ' + ', '.join(riprod)) if riprod else 'nessun generatore la riproduce'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e399_giuntura_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e399 — I generatori pubblicati hanno una giuntura che si ferma all\'a capo?', '', 'Preregistrazione: `preregistrazioni/e399.md`.', '',
          '| testo | E nella riga | z | E a capo | z | Q |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %.4f | %.1f | %.4f | %.1f | %s |' % (k, x['riga']['E'], x['riga']['z'], x['capo']['E'], x['capo']['z'], '%.2f' % x['Q'] if x['Q'] is not None else ''))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e399_giuntura_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
