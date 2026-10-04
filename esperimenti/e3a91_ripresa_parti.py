# -*- coding: utf-8 -*-
"""Esperimento e3a91: misure dell'e3a89 (ripetizione di memoria corta nella riga) per lingua A, B e mani 1, 2, 3.

Preregistrazione: preregistrazioni/e3a91.md. Scrive risultati/e3a91_ripresa_parti.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure as mis
import trascrizione
import e341_fonti as e341
import e3a89_ripresa_lingue as e3a89

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = mis.divisore(mis.GLIFI_EVA)


def main():
    rnd = random.Random(3191)
    info = {}
    for r in trascrizione.leggi('ZL'):
        info.setdefault(r.pagina, (r.lingua, r.mano))
    tutte = OrderedDict()
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        tutte[pg] = [par for par in pp if par]
    parti = OrderedDict([('lingua A', lambda i: i[0] == 'A'), ('lingua B', lambda i: i[0] == 'B'),
                         ('mano 1', lambda i: i[1] == '1'), ('mano 2', lambda i: i[1] == '2'), ('mano 3', lambda i: i[1] == '3')])
    ris = OrderedDict()
    for nome, f in parti.items():
        pagine = [pp for pg, pp in tutte.items() if pg in info and f(info[pg]) and pp]
        x = e3a89.misure(pagine, rnd)
        e14, c = x['stessa_d1_4'], x['calo']
        if x['coppie_stessa_d7_10'] < 500 or c is None:
            es = 'n.d.'
        elif e14 > 0.003 and c < 0.5:
            es = 'regge'
        elif e14 < 0.001 or c > 1.10:
            es = 'non regge'
        else:
            es = 'incerto'
        x['pagine'] = len(pagine)
        x['esito'] = es
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a91_ripresa_parti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%+.4f' % v
    md = ['# e3a91 — La ripetizione di memoria corta nella riga vale in lingua A e B e per ogni scriba?', '', 'Preregistrazione: `preregistrazioni/e3a91.md`. Voynich intero (e3a87): eccesso d 1–4 +0,0066, calo 0,12.', '',
          '| parte | pagine | eccesso stessa riga d 1–4 | d 7–10 | calo | coppie d 7–10 | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %s | %s | %s | %d | %s |' % (k, x['pagine'], f(x['stessa_d1_4']), f(x['stessa_d7_10']), f(x['calo']), x['coppie_stessa_d7_10'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a91_ripresa_parti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
