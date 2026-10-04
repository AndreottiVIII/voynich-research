# -*- coding: utf-8 -*-
"""Esperimento e3b33: e3b21 (memoria delle scelte in lettere, lingua A e B) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3b33.md. Scrive risultati/e3b33_memoria_ab_it.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b21_memoria_lettere_ab as e3b21

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    per = defaultdict(lambda: defaultdict(list))
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if ws:
            per[lingua.get(r.pagina)][r.pagina].append(ws)
    ris = OrderedDict()
    for lg in ('A', 'B'):
        pr = e3b21.profilo(list(per[lg].values()))
        j, n = e3b21.mezza(pr)
        ris['lingua ' + lg] = OrderedDict([('profilo', OrderedDict((k, OrderedDict([('eccesso', v[0]), ('coppie', v[1])])) for k, v in pr.items())), ('mezza_vita_classe', n), ('indice', j)])
        print(lg, json.dumps(ris['lingua ' + lg], ensure_ascii=False), flush=True)
    ja, jb = ris['lingua A']['indice'], ris['lingua B']['indice']
    if ja is None or jb is None:
        esito = 'n.d.'
    elif jb >= ja + 2:
        esito = 'si ritrova'
    elif ja >= jb + 2:
        esito = 'al contrario'
    else:
        esito = 'non si ritrova'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b33_memoria_ab_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda x: '%+.4f (%d)' % (x['eccesso'], x['coppie']) if x['eccesso'] is not None else '– (0)'
    md = ['# e3b33 — La memoria più lunga in lingua B (e3b21) si ritrova con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b33.md`. ZL (e3b21): mezza vita A 5–9 lettere, B 20–29.', '',
          '| lettere in mezzo | lingua A | lingua B |', '|---|---|---|']
    for _, _, cl in e3b21.CLASSI_L:
        md.append('| %s | %s | %s |' % (cl, f(ris['lingua A']['profilo'][cl]), f(ris['lingua B']['profilo'][cl])))
    md += ['', 'Mezza vita in lettere: A %s, B %s.' % (ris['lingua A']['mezza_vita_classe'], ris['lingua B']['mezza_vita_classe']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b33_memoria_ab_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
