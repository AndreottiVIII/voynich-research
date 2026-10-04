# -*- coding: utf-8 -*-
"""Esperimento e3b26: e3b20 solo a distanza 2, con la parola in mezzo di almeno 3 lettere (3-4 contro 6+).

Preregistrazione: preregistrazioni/e3b26.md. Scrive risultati/e3b26_memoria_segni_controllo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b20_memoria_segni as e3b20

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def gruppo(l):
    return 'corta' if 3 <= l <= 4 else ('lunga' if l >= 6 else None)


def diff(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, d, l, ok, att in cc:
        g = gruppo(l) if d == 2 else None
        if g:
            acc[g][0] += ok - att
            acc[g][1] += 1
    return acc['corta'][0] / acc['corta'][1] - acc['lunga'][0] / acc['lunga'][1], {g: (s / n, n) for g, (s, n) in acc.items()}


def main():
    rnd = random.Random(3226)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    cc = [x for x in e3b20.coppie(pagine) if x[1] == 2]
    d, dett = diff(cc)
    per = defaultdict(list)
    for x in cc:
        per[x[0]].append(x)
    chiavi = list(per)
    b = sorted(diff([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])[0] for _ in range(BOOT))
    ic = [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    esito = 'si consuma con le lettere anche così' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else "era l'effetto delle parole cortissime")
    out = OrderedDict([('dettaglio', dett), ('differenza', d), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b26_memoria_segni_controllo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b26 — La memoria si consuma con le lettere anche senza le parole cortissime in mezzo?', '', 'Preregistrazione: `preregistrazioni/e3b26.md`. Distanza 2; parola in mezzo di 3–4 lettere ("corta") o di 6 o più ("lunga").', '',
          '| parola in mezzo | coppie | eccesso di accordo |', '|---|---|---|']
    md += ['| %s | %d | %+.4f |' % (g, dett[g][1], dett[g][0]) for g in ('corta', 'lunga') if g in dett]
    md += ['', 'Differenza corta − lunga **%+.4f**, IC 95%% %+.4f – %+.4f.' % (d, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b26_memoria_segni_controllo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
