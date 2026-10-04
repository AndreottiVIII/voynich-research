# -*- coding: utf-8 -*-
"""Esperimento e3b11: statistica dell'e3b05 (spazio facoltativo e unita' intera, a parita' di 4 segni e lunghezze) sui
testi in pinyin (scrittura a sillabe separate) e sul maori.

Preregistrazione: preregistrazioni/e3b11.md. Scrive risultati/e3b11_lessicale_sillabe.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3b05_lessicale_generatori as e3b05

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTI = ('Modern - Chinese (Pinyin) - Literary - NT - Matthew', 'Modern - Chinese (Pinyin) - Technical - Voynich Wiki', 'Modern - Maori - Literary - NT')


def main():
    rnd = random.Random(3211)
    t = e381.testi()
    ris = OrderedDict()
    for k in TESTI:
        ris[k] = e3b05.misura(t[k + '.txt'], rnd)
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    py = [ris[k] for k in TESTI[:2]]
    if any('scarto' not in x for x in py):
        esito = 'n.d.'
    elif all(x['scarto'] > 1.0 and x['z'] > 3 for x in py):
        esito = 'anche a sillabe lo spazio è lessicale'
    elif all(x['scarto'] < 0.3 for x in py):
        esito = 'a sillabe lo spazio somiglia al Voynich'
    else:
        esito = 'in mezzo'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b11_lessicale_sillabe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b11 — In una scrittura a sillabe separate lo spazio segue l\'unità intera?', '', 'Preregistrazione: `preregistrazioni/e3b11.md`. Voynich (stesso nullo, e3b03): scarto +0,195; latino +4.', '',
          '| testo | punti facoltativi | differenza vera | nullo | scarto | z |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        if 'scarto' in x:
            md.append('| %s | %d | %+.3f | %+.3f | %+.3f | %+.1f |' % (k, x['punti'], x['differenza_vera'], x['nullo_media'], x['scarto'], x['z']))
        else:
            md.append('| %s | %d | – | – | – | n.d. |' % (k, x['punti']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b11_lessicale_sillabe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
