# -*- coding: utf-8 -*-
"""Esperimento e3a92: sintesi della catena (e3a78) e ripetizione di memoria corta (e3a89) con la trascrizione GC (v101).

Preregistrazione: preregistrazioni/e3a92.md. Scrive risultati/e3a92_glen_claston.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3a89_ripresa_lingue as e3a89

RISULTATI = os.path.join(QUI, '..', 'risultati')
SI = ('giuntura', 'chiusura della riga', 'catena dentro/fra le parole', 'frequenza-forma')
NO = ('ripresa dalla riga sopra', 'margine sinistro')


def pagine_gc():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('GC')):
        ws = [tuple(w) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    return [[par for par in pars if par] for pars in per.values() if any(pars)]


def main():
    rnd = random.Random(3192)
    pagine = pagine_gc()
    vero = e3a78.proprieta(pagine, rnd)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    risc = [e3a78.proprieta(e3a78.riscrivi(pagine, tab, rnd), rnd) for _ in range(e3a78.RISCRITTURE)]
    p1 = OrderedDict()
    for n in SI + NO:
        rv = statistics.mean(x[n] for x in risc)
        p1[n] = OrderedDict([('vero', vero[n]), ('riscritto_media', rv), ('R', rv / vero[n] if vero[n] else None)])
    regge1 = all(p1[n]['R'] is not None and p1[n]['R'] >= 0.75 for n in SI) and all(p1[n]['R'] is not None and p1[n]['R'] < 0.25 for n in NO)
    p2 = e3a89.misure(pagine, rnd)
    regge2 = p2['stessa_d1_4'] is not None and p2['stessa_d1_4'] > 0.003 and p2['calo'] is not None and p2['calo'] < 0.5
    out = OrderedDict([('parte1', p1), ('esito1', 'la sintesi regge' if regge1 else 'la sintesi non regge'), ('parte2', p2), ('esito2', 'regge' if regge2 else 'non regge')])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a92_glen_claston.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%+.4f' % v
    md = ['# e3a92 — Sintesi della catena e ripetizione di memoria corta con l\'alfabeto di Glen Claston', '', 'Preregistrazione: `preregistrazioni/e3a92.md`.', '',
          '## Parte 1', '', '| proprietà | GC vera | riscritta | R |', '|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %s |' % (n, x['vero'], x['riscritto_media'], '%.2f' % x['R'] if x['R'] is not None else 'n.d.') for n, x in p1.items()]
    md += ['', 'Esito parte 1: **%s**.' % out['esito1'], '', '## Parte 2', '',
           'Eccesso stessa riga d 1–4 %s, d 7–10 %s, calo %s (coppie d 7–10: %d).' % (f(p2['stessa_d1_4']), f(p2['stessa_d7_10']), f(p2['calo']), p2['coppie_stessa_d7_10']), '',
           'Esito parte 2: **%s**.' % out['esito2']]
    open(os.path.join(RISULTATI, 'e3a92_glen_claston.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
