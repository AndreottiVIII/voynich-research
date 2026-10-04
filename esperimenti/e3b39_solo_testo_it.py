# -*- coding: utf-8 -*-
"""Esperimento e3b39: e3b38 (memoria delle scelte a cavallo dell'a capo, pagine solo testo contro le altre) con la IT.

Preregistrazione: preregistrazioni/e3b39.md. Scrive risultati/e3b39_solo_testo_it.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b38_solo_testo_a_capo as e3b38

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3239)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    gruppi = {'solo testo (T)': [], 'altre pagine': []}
    for pg, pars in per.items():
        pp = [par for par in pars if par]
        if pp:
            gruppi['solo testo (T)' if sezione.get(pg) == 'T' else 'altre pagine'].append(pp)
    ris = OrderedDict((k, e3b38.analizza(v, rnd)) for k, v in gruppi.items())
    t, a = ris['solo testo (T)'], ris['altre pagine']
    esito = 'si ritrova' if t['IC95_a_cavallo'][0] > 0 and a['IC95_a_cavallo'][0] <= 0 <= a['IC95_a_cavallo'][1] else 'non si ritrova'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b39_solo_testo_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b39 — La memoria che passa l\'a capo nelle pagine "solo testo" si ritrova con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b39.md`. ZL (e3b38): T a cavallo +0,075 (IC +0,025 – +0,133); altre −0,002.', '',
          '| pagine | quante | stessa riga: eccesso (coppie) | a cavallo dell\'a capo: eccesso (coppie) | IC 95% a cavallo |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f – %+.4f |' % (k, x['pagine'], x['stessa_riga'], x['coppie_stessa'], x['a_cavallo'], x['coppie_a_cavallo'], x['IC95_a_cavallo'][0], x['IC95_a_cavallo'][1]) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b39_solo_testo_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
