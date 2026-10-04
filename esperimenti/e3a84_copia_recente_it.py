# -*- coding: utf-8 -*-
"""Esperimento e3a84: e3a83 (posizione delle fonti nella riga sopra) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3a84.md. Scrive risultati/e3a84_copia_recente_it.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a80_catena_takahashi as e3a80
import e3a83_copia_recente as e3a83

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3184)
    blocchi = []
    for pars in e3a80.pagine_it():
        for par in pars:
            pp = [r for r in par if r]
            if len(pp) >= 3:
                b = e3a83.paragrafo(pp, rnd)
                if b[6]:
                    blocchi.append(b)
    d, mo, mn = e3a83.sintesi(blocchi)
    boot = sorted(e3a83.sintesi([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi])[0] for _ in range(e3a83.BOOT))
    ic = [boot[int(0.025 * e3a83.BOOT)], boot[int(0.975 * e3a83.BOOT) - 1]]
    parole = sum(b[6] for b in blocchi)
    terzi = OrderedDict()
    for t, nome in enumerate(('primo terzo', 'secondo terzo', 'ultimo terzo')):
        o = sum(b[2][t] for b in blocchi) / parole
        n = sum(b[5][t] for b in blocchi) / parole
        terzi[nome] = OrderedDict([('osservate_per_parola', o), ('nullo_per_parola', n), ('eccesso', o - n)])
    esito = 'si ritrova' if ic[0] > 0 else 'non si ritrova'
    out = OrderedDict([('paragrafi', len(blocchi)), ('parole', parole), ('differenza', d), ('IC95', ic), ('terzi', terzi), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a84_copia_recente_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a84 — La preferenza per la fine della riga sopra si ritrova con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3a84.md`. Riferimento ZL (e3a83): +0,009 (IC +0,002 – +0,016).', '',
          'Paragrafi %d, parole %d. Differenza **%+.3f**, IC 95%% %+.3f – %+.3f.' % (len(blocchi), parole, d, ic[0], ic[1]), '',
          '| terzo della riga sopra | eccesso per parola |', '|---|---|']
    md += ['| %s | %+.4f |' % (k, x['eccesso']) for k, x in terzi.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a84_copia_recente_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
