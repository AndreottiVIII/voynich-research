# -*- coding: utf-8 -*-
"""Esperimento e3b24: e3b23 (memoria delle scelte per sezione x lingua) con le coppie dentro lo stesso tratto scritto di
seguito (righe divise ai salti del disegno e alle parole illeggibili).

Preregistrazione: preregistrazioni/e3b24.md. Scrive risultati/e3b24_memoria_tratti.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e386_salto_disegno as e386
import e3b21_memoria_lettere_ab as e3b21

RISULTATI = os.path.join(QUI, '..', 'risultati')


def tratti(ws, seps):
    out, cur = [], []
    for i, w in enumerate(ws):
        if w is None or (i and seps[i - 1] == '|'):
            if cur:
                out.append(cur)
            cur = [] if w is None else [''.join(w)]
            continue
        cur.append(''.join(w))
    if cur:
        out.append(cur)
    return out


def main():
    per = defaultdict(lambda: defaultdict(list))
    for strato, pg, _, ws, seps in e386.righe():
        sez, lg = strato.split('-')
        per[(sez, lg)][pg] += tratti(ws, seps)
        per[('tutte', lg)][pg] += tratti(ws, seps)
    ris = OrderedDict()
    for (sez, lg), pagine in sorted(per.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if lg not in ('A', 'B'):
            continue
        pr = e3b21.profilo(list(pagine.values()))
        if pr['0'][1] < 300:
            continue
        j, n = e3b21.mezza(pr)
        nome = '%s %s' % ('tutte le sezioni' if sez == 'tutte' else trascrizione.SEZIONI.get(sez, sez), lg)
        ris[nome] = OrderedDict([('pagine', len(pagine)), ('coppie_0', pr['0'][1]), ('profilo', OrderedDict((k, OrderedDict([('eccesso', v[0]), ('coppie', v[1])])) for k, v in pr.items())),
                                 ('mezza_vita_classe', n), ('indice', j)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    hb = ris.get('erbario B')
    if hb is None or hb['indice'] is None:
        esito = 'n.d.'
    elif hb['indice'] >= 4:
        esito = "era l'effetto dei disegni"
    elif hb['indice'] <= 2:
        esito = 'la differenza fra sezioni resta'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b24_memoria_tratti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda x: '%+.3f' % x['eccesso'] if x['eccesso'] is not None else '–'
    md = ['# e3b24 — Senza contare le coppie a cavallo dei disegni, la memoria è corta anche nell\'erbario?', '', 'Preregistrazione: `preregistrazioni/e3b24.md`. Coppie dentro lo stesso tratto scritto di seguito.', '',
          '| gruppo | pagine | coppie a 0 lettere | eccesso a 0 | a 5–9 | a 15–19 | mezza vita in lettere |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %d | %s | %s | %s | %s |' % (k, x['pagine'], x['coppie_0'], f(x['profilo']['0']), f(x['profilo']['5–9']), f(x['profilo']['15–19']), x['mezza_vita_classe']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b24_memoria_tratti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
