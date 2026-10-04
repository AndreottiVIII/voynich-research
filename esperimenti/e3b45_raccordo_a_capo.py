# -*- coding: utf-8 -*-
"""Esperimento e3b45: regola di raccordo (qo- dopo -y/-o/-d, o- dopo -n/-r/-s/-m/-l) fra l'ultima parola di una riga e
la prima della riga sotto, nelle pagine "solo testo" e nelle altre (ZL e IT).

Preregistrazione: preregistrazioni/e3b45.md. Scrive risultati/e3b45_raccordo_a_capo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm', 'l'}
PERM = 10000
BOOT = 2000
MIN_T = 30


def evento(w, v):
    """(classe della fine di w, 1 se v comincia con qo) oppure None."""
    x = e380.ini_qo(v)
    if not x or not w:
        return None
    if w[-1] in V:
        return ('V', int(x[1] == 'qo'))
    if w[-1] in C:
        return ('C', int(x[1] == 'qo'))
    return None


def eventi(pagine):
    """(a cavallo, stessa riga): liste di (classe, qo) da pagine di paragrafi di righe di stringhe EVA."""
    cav, stessa = [], []
    for pars in pagine:
        for par in pars:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            rr = [r for r in rr if r]
            for i, r in enumerate(rr):
                for a, b in zip(r, r[1:]):
                    e = evento(a, b)
                    if e:
                        stessa.append(e)
                if i:
                    e = evento(rr[i - 1][-1], r[0])
                    if e:
                        cav.append(e)
    return cav, stessa


def diff(ev):
    v = [q for c, q in ev if c == 'V']
    c = [q for k, q in ev if k == 'C']
    if not v or not c:
        return None
    return sum(v) / len(v) - sum(c) / len(c)


def prova(ev, rnd):
    d = diff(ev)
    if d is None:
        return OrderedDict([('coppie', len(ev)), ('differenza', None)])
    et = [c for c, _ in ev]
    qs = [q for _, q in ev]
    ge = 0
    for _ in range(PERM):
        rnd.shuffle(et)
        ge += diff(list(zip(et, qs))) >= d
    boot = sorted(x for x in (diff([ev[rnd.randrange(len(ev))] for _ in ev]) for _ in range(BOOT)) if x is not None)
    nv = sum(1 for c, _ in ev if c == 'V')
    return OrderedDict([('coppie', len(ev)), ('V', nv), ('C', len(ev) - nv), ('differenza', d), ('p', ge / PERM),
                        ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])


def pagine_it():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    return OrderedDict((pg, [par for par in pars if par]) for pg, pars in per.items())


def main():
    rnd = random.Random(3245)
    sezione, mano = {}, {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
        mano.setdefault(r.pagina, r.mano)
    zl = OrderedDict((pg, [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]) for pg, pars in e341.pagine().items())
    it = pagine_it()
    gruppi = OrderedDict([
        ('ZL, solo testo (T)', [p for pg, p in zl.items() if sezione.get(pg) == 'T']),
        ('ZL, mano 2 non T', [p for pg, p in zl.items() if sezione.get(pg) != 'T' and mano.get(pg) == '2']),
        ('ZL, tutte le non T', [p for pg, p in zl.items() if sezione.get(pg) != 'T']),
        ('IT, solo testo (T)', [p for pg, p in it.items() if sezione.get(pg) == 'T']),
        ('IT, tutte le non T', [p for pg, p in it.items() if sezione.get(pg) != 'T']),
    ])
    ris = OrderedDict()
    for k, pp in gruppi.items():
        cav, stessa = eventi(pp)
        ris[k] = OrderedDict([('pagine', len(pp)), ('a_cavallo', prova(cav, rnd)), ('stessa_riga_differenza', diff(stessa)), ('stessa_riga_coppie', len(stessa))])
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    t, n, ti = ris['ZL, solo testo (T)']['a_cavallo'], ris['ZL, tutte le non T']['a_cavallo'], ris['IT, solo testo (T)']['a_cavallo']
    if t['coppie'] < MIN_T or t['differenza'] is None:
        esito = 'dati insufficienti'
    elif t['p'] < 0.05 and (ti.get('differenza') or 0) > 0 and n['differenza'] < 0.5 * t['differenza']:
        esito = "il raccordo passa l'a capo nelle pagine solo testo"
    elif t['p'] > 0.20:
        esito = 'non passa'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b45_raccordo_a_capo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b45 — Nelle pagine "solo testo" la regola di raccordo passa l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3b45.md`. Differenza = P(qo | riga sopra finita in -y/-o/-d) − P(qo | finita in -n/-r/-s/-m/-l).', '',
          '| gruppo | pagine | a cavallo: coppie (V, C) | differenza a cavallo (IC 95%) | p | stessa riga: differenza (coppie) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        a = x['a_cavallo']
        if a.get('differenza') is None:
            md.append('| %s | %d | %d | — | — | %s (%d) |' % (k, x['pagine'], a['coppie'], x['stessa_riga_differenza'], x['stessa_riga_coppie']))
        else:
            md.append('| %s | %d | %d (%d, %d) | %+.3f (%+.3f – %+.3f) | %.4f | %+.3f (%d) |' % (k, x['pagine'], a['coppie'], a['V'], a['C'], a['differenza'], a['IC95'][0], a['IC95'][1], a['p'], x['stessa_riga_differenza'], x['stessa_riga_coppie']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b45_raccordo_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
