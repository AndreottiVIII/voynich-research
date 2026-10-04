# -*- coding: utf-8 -*-
"""Esperimento e3b40: forme di bordo della riga (-m a fine riga, y/s/d a inizio riga) e margine sinistro nelle pagine
"solo testo" contro le altre.

Preregistrazione: preregistrazioni/e3b40.md. Scrive risultati/e3b40_solo_testo_bordi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a25_inizi_evitati as e3a25

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def bordi(righe):
    """righe: (parole, prima del paragrafo). Le prime righe dei paragrafi non contano per l'inizio riga."""
    fin = [r[-1] for r, _ in righe]
    alt = [w for r, _ in righe for w in r[:-1]]
    ini = [r[0] for r, prima in righe if not prima]
    alt2 = [w for r, _ in righe for w in r[1:]]
    m = sum(w[-1] == 'm' for w in fin) / len(fin) - sum(w[-1] == 'm' for w in alt) / len(alt)
    y = sum(w[0] in ('y', 's', 'd') for w in ini) / len(ini) - sum(w[0] in ('y', 's', 'd') for w in alt2) / len(alt2)
    return m, y


def main():
    rnd = random.Random(3240)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    gruppi = {'solo testo (T)': [], 'altre pagine': []}
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r if trascrizione.pulita(x)) if w] for r in par] for par in pars]
        pp = [[r for r in par if len(r) >= 2] for par in pp]
        gruppi['solo testo (T)' if sezione.get(pg) == 'T' else 'altre pagine'] += [par for par in pp if par]
    ris = OrderedDict()
    for k, pars in gruppi.items():
        righe = [(r, i == 0) for par in pars for i, r in enumerate(par)]
        m, y = bordi(righe)
        bm, by = [], []
        for _ in range(BOOT):
            rb = [righe[rnd.randrange(len(righe))] for _ in righe]
            a, b = bordi(rb)
            bm.append(a)
            by.append(b)
        bm.sort()
        by.sort()
        blocchi = [e3a25.inizi(par[1:], 2) for par in pars if len(par[1:]) >= 3]
        marg = e3a25.prova(blocchi, rnd, 1000)
        ris[k] = OrderedDict([('righe', len(righe)), ('righe_non_prime', sum(not p for _, p in righe)), ('m_fine', m), ('IC_m', [bm[50], bm[1949]]), ('ysd_inizio', y), ('IC_ysd', [by[50], by[1949]]),
                              ('margine_rapporto', marg['rapporto']), ('margine_z', marg['z']), ('margine_coppie', marg['coppie'])])
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    t, a = ris['solo testo (T)'], ris['altre pagine']
    manca = all(t[k] < 0.5 * a[k] and t[ic][0] <= 0 <= t[ic][1] for k, ic in (('m_fine', 'IC_m'), ('ysd_inizio', 'IC_ysd')))
    ci_sono = all(t[ic][0] > 0 for ic in ('IC_m', 'IC_ysd'))
    esito = 'nelle pagine solo testo mancano le forme di bordo' if manca else ('le forme di bordo ci sono anche lì' if ci_sono else 'in parte')
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b40_solo_testo_bordi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b40 — Nelle pagine "solo testo" mancano anche le forme di bordo della riga?', '', 'Preregistrazione: `preregistrazioni/e3b40.md`.', '',
          '| pagine | righe | -m a fine riga (IC 95%) | y/s/d a inizio riga (IC 95%) | margine: rapporto (z, coppie) |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) | %.2f (%.1f, %d) |' % (k, x['righe'], x['m_fine'], x['IC_m'][0], x['IC_m'][1], x['ysd_inizio'], x['IC_ysd'][0], x['IC_ysd'][1],
                                                                                    x['margine_rapporto'] or float('nan'), x['margine_z'], x['margine_coppie']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b40_solo_testo_bordi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
