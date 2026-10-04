# -*- coding: utf-8 -*-
"""Esperimento e3b22: profilo della memoria delle scelte in lettere (e3b21) per mano e lingua; la mano 3 scrive in A e B.

Preregistrazione: preregistrazioni/e3b22.md. Scrive risultati/e3b22_memoria_mani.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b21_memoria_lettere_ab as e3b21

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRUPPI = (('mano 1 (A)', '1', 'A'), ('mano 2 (B)', '2', 'B'), ('mano 3 in A', '3', 'A'), ('mano 3 in B', '3', 'B'), ('mano 5 (B)', '5', 'B'))


def main():
    info = {}
    for r in trascrizione.leggi('ZL'):
        info.setdefault(r.pagina, (r.mano, r.lingua))
    per = defaultdict(list)
    for pg, pars in e341.pagine().items():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        per[info.get(pg)].append([r for r in righe if r])
    ris = OrderedDict()
    for nome, mano, lg in GRUPPI:
        pagine = per.get((mano, lg), [])
        pr = e3b21.profilo(pagine)
        j, n = e3b21.mezza(pr) if pr['0'][0] is not None else (None, None)
        ris[nome] = OrderedDict([('pagine', len(pagine)), ('profilo', OrderedDict((k, OrderedDict([('eccesso', v[0]), ('coppie', v[1])])) for k, v in pr.items())),
                                 ('mezza_vita_classe', n), ('indice', j)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    a, b = ris['mano 3 in A'], ris['mano 3 in B']
    if a['profilo']['0']['coppie'] < 300 or b['profilo']['0']['coppie'] < 300 or a['indice'] is None or b['indice'] is None:
        esito = 'dati insufficienti'
    elif a['indice'] <= 2 and b['indice'] >= 4:
        esito = 'dipende dalla lingua'
    elif abs(a['indice'] - b['indice']) <= 1:
        esito = 'dipende dallo scriba'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b22_memoria_mani.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda x: '%+.4f (%d)' % (x['eccesso'], x['coppie']) if x['eccesso'] is not None else '– (0)'
    md = ['# e3b22 — La memoria lunga di B è della lingua o degli scribi?', '', 'Preregistrazione: `preregistrazioni/e3b22.md`. Eccesso di accordo delle scelte per lettere scritte in mezzo.', '',
          '| lettere in mezzo | ' + ' | '.join('%s (%d pagine)' % (k, x['pagine']) for k, x in ris.items()) + ' |', '|---|' + '---|' * len(ris)]
    for _, _, cl in e3b21.CLASSI_L:
        md.append('| %s | %s |' % (cl, ' | '.join(f(x['profilo'][cl]) for x in ris.values())))
    md += ['', 'Mezza vita in lettere: ' + '; '.join('%s: %s' % (k, x['mezza_vita_classe']) for k, x in ris.items()) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b22_memoria_mani.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
