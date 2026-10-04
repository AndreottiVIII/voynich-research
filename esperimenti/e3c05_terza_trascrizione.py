# -*- coding: utf-8 -*-
"""Esperimento e3c05: la regola automatica dell'e3c01 (alternanze interne dalle coppie minime) sulla terza trascrizione,
quella di Glen Claston (alfabeto v101, un carattere per segno): memoria (e3b62 + e3b70), forma (R, e3b98), consumo con le
lettere (e3b80), profilo (e3b95).

Preregistrazione: preregistrazioni/e3c05.md. Scrive risultati/e3c05_terza_trascrizione.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b98_forma_lingue as e3b98
import e3c01_alternanze_interne as e3c01
import e3c03_tre_tratti as e3c03

RISULTATI = os.path.join(QUI, '..', 'risultati')


def pagine_gc():
    """{pagina: [paragrafi]}, come e341.pagine ma sulla trascrizione GC."""
    per, ordine = {}, []
    for r in trascrizione.testo_corrente(trascrizione.leggi('GC')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if ws:
            if r.pagina not in per:
                per[r.pagina] = []
                ordine.append(r.pagina)
            pars = per[r.pagina]
            if r.inizio_par or not pars:
                pars.append([])
            pars[-1].append(ws)
    return OrderedDict((p, per[p]) for p in ordine)


def unita_gc(mano):
    """Pagine con una mano nota, righe come tuple di caratteri v101; strati = mani."""
    uu, ss = [], []
    for pg, pars in pagine_gc().items():
        h = mano.get(pg)
        if not h:
            continue
        rr = [[tuple(w) for w in r if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            uu.append(rr)
            ss.append(h)
    return uu, ss


def main():
    rng = np.random.default_rng(3305)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    uu, ss = unita_gc(mano)
    seq = [r for u in uu for r in u]
    scelte, punti = e3c01.alternanze(seq)
    classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
    x = e3c01.misura(uu, ss, classi, rng)
    forma = e3b98.analizza(uu, classi, rng)
    x.update([('alternanze', ['%s/%s' % c for c in scelte]), ('coppie_minime', punti), ('pagine', len(uu)), ('parole', sum(len(r) for r in seq)),
              ('accanto', forma['accanto']), ('accanto_IC95', forma['accanto_IC95']), ('R', forma['R']), ('R_IC95', forma['R_IC95']),
              ('lettere', e3c03.lettere(uu, ss, classi, rng)), ('profilo', e3c03.profilo(uu, classi))])
    print(json.dumps(x, ensure_ascii=False), flush=True)
    rif = json.load(open(os.path.join(RISULTATI, 'e3c03_tre_tratti.json'), encoding='utf-8'))['testi']['Voynich IT']
    memoria = bool(x['IC95'] and x['IC95'][0] > 0)
    forma_ok = bool(x['accanto_IC95'][0] > 0 and x['R_IC95'][0] is not None and x['R_IC95'][0] <= rif['R_IC95'][1] and rif['R_IC95'][0] <= x['R_IC95'][1])
    if memoria and forma_ok:
        esito = 'replica: memoria e forma come nelle altre due trascrizioni'
    elif memoria:
        esito = 'replica la memoria, non la forma'
    else:
        esito = 'non replica'
    out = OrderedDict([('GC', x), ('riferimento_IT_e3c03', OrderedDict([('R_IC95', rif['R_IC95']), ('accanto', rif['accanto'])])), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c05_terza_trascrizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    l = x['lettere']
    md = ['# e3c05 — La terza trascrizione (Glen Claston, v101) con la regola automatica', '', 'Preregistrazione: `preregistrazioni/e3c05.md`.', '',
          '| misura | GC (v101) |', '|---|---|',
          '| pagine, parole | %d, %d |' % (x['pagine'], x['parole']),
          '| alternanze scelte (coppie minime) | %s (%s) |' % (', '.join(x['alternanze']), ', '.join(str(p) for p in punti)),
          '| memoria (IC 95%%) | %+.4f (%+.4f – %+.4f) |' % (x['effetto'], x['IC95'][0], x['IC95'][1]),
          '| accordo fra parole accanto | %+.3f (%+.3f – %+.3f) |' % (x['accanto'], x['accanto_IC95'][0], x['accanto_IC95'][1]),
          '| R | %s |' % ('—' if x['R'] is None else '%.2f (%.2f – %.2f)' % (x['R'], x['R_IC95'][0], x['R_IC95'][1])),
          '| consumo con le lettere | %s |' % ('—' if l['effetto'] is None else '%+.4f (%+.4f – %+.4f)' % (l['effetto'], l['IC95'][0], l['IC95'][1])),
          '| profilo d=1…7 | %s |' % ' '.join('%+.3f' % v if v is not None else '—' for v in x['profilo'].values()),
          '', 'Riferimento Voynich IT (e3c03): R %s; accordo accanto %+.3f.' % (rif['R_IC95'], rif['accanto']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c05_terza_trascrizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
