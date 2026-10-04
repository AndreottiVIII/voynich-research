# -*- coding: utf-8 -*-
"""Esperimento e3b23: mezza vita in lettere della memoria delle scelte (e3b21) per sezione x lingua.

Preregistrazione: preregistrazioni/e3b23.md. Scrive risultati/e3b23_memoria_sezioni.json e .md.
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


def main():
    info = {}
    for r in trascrizione.leggi('ZL'):
        info.setdefault(r.pagina, (r.sezione, r.lingua))
    per = defaultdict(list)
    for pg, pars in e341.pagine().items():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        per[info.get(pg)].append([r for r in righe if r])
    ris = OrderedDict()
    for (sez, lg), pagine in sorted(per.items(), key=lambda kv: (str(kv[0][1]), str(kv[0][0]))):
        if lg not in ('A', 'B'):
            continue
        pr = e3b21.profilo(pagine)
        if pr['0'][1] < 300:
            continue
        j, n = e3b21.mezza(pr)
        nome = '%s %s' % (trascrizione.SEZIONI.get(sez, sez), lg)
        ris[nome] = OrderedDict([('pagine', len(pagine)), ('coppie_0', pr['0'][1]), ('profilo', OrderedDict((k, OrderedDict([('eccesso', v[0]), ('coppie', v[1])])) for k, v in pr.items())),
                                 ('mezza_vita_classe', n), ('indice', j)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    b = {k: x for k, x in ris.items() if k.endswith(' B')}
    ha = next((x for k, x in ris.items() if k.endswith(' A') and 'erbario' in k), None)
    ib = [x['indice'] for x in b.values() if x['indice'] is not None]
    if ib and ha is not None and ha['indice'] is not None and all(i >= 4 for i in ib) and ha['indice'] <= 2:
        esito = 'proprietà di B'
    elif ib and max(ib) - min(ib) >= 2:
        esito = 'dipende dalla sezione'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b23_memoria_sezioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b23 — Dentro la lingua B, la memoria lunga c\'è in tutte le sezioni?', '', 'Preregistrazione: `preregistrazioni/e3b23.md`.', '',
          '| gruppo | pagine | coppie a 0 lettere | eccesso a 0 | a 5–9 | a 15–19 | mezza vita in lettere |', '|---|---|---|---|---|---|---|']
    f = lambda x: '%+.3f' % x['eccesso'] if x['eccesso'] is not None else '–'
    md += ['| %s | %d | %d | %s | %s | %s | %s |' % (k, x['pagine'], x['coppie_0'], f(x['profilo']['0']), f(x['profilo']['5–9']), f(x['profilo']['15–19']), x['mezza_vita_classe']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b23_memoria_sezioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
