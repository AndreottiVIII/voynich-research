# -*- coding: utf-8 -*-
"""Esperimento e3c89: le misure di riga del Voynich a parità di lunghezza con i testi di confronto (10.000 parole).

Nota A8 del revisore: le misure dipendono dalla grandezza del campione. Quasi tutti i confronti con le lingue usano già
il Voynich ridotto a 10.000 parole (e3a49, e3a55, e3a58, e3a61, e3a67, e3a03, e3b25, e3c84). Restano due misure fatte su
tutto il Voynich contro 10.000 parole delle lingue: la chiusura della riga (Q dell'e384) e il margine sinistro (rapporto
dell'e3a35). Qui si rifanno su 5 sottoinsiemi di pagine a caso da 10.000 parole.

Preregistrazione: preregistrazioni/e3c89.md. Scrive risultati/e3c89_riga_a_lunghezza_pari.json e .md.
SOLO_CONTROLLI=1: prova del codice sul latino (stessi valori dell'e384 e dell'e3a35), niente Voynich.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381
import e384_giuntura_a_capo as e384
import e3a25_inizi_evitati as e3a25

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
D = misure.divisore(misure.GLIFI_EVA)
SOTTOINSIEMI = 5


def blocchi_pagina(pars):
    """Come l'e384: paragrafi di almeno 4 righe da soli; i paragrafi corti della pagina insieme."""
    out, corti = [], []
    for rr in pars:
        if len(rr) >= 4:
            out.append([rr])
        else:
            corti.append(rr)
    if corti:
        out.append(corti)
    return out


def q_capo(pagine, rnd):
    return e384.misura([b for pars in pagine for b in blocchi_pagina(pars)], rnd)[0]['Q']


def margine(pagine, rnd):
    pars = [p[1:] for pars in pagine for p in pars if len(p[1:]) >= 3]
    return e3a25.prova([e3a25.inizi(p, 2) for p in pars], rnd, 1000)['rapporto']


def main():
    rnd = random.Random(3389)
    if SOLO_CONTROLLI:
        t = e381.testi()['Historical - Latin - Literary - NT (Vulgate).txt']
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        pagine = [[righe[i:i + 25]] for i in range(0, len(righe), 25)]
        print('latino: Q', q_capo(pagine, rnd), '(e384 sul testo intero: %.3f)' % json.load(open(os.path.join(RISULTATI, 'e384_giuntura_a_capo.json'), encoding='utf-8'))['testi']['Historical - Latin - Literary - NT (Vulgate)']['Q'])
        print('latino: margine', margine(pagine, rnd), '(e3a35: %.3f)' % json.load(open(os.path.join(RISULTATI, 'e3a35_margine_confronti.json'), encoding='utf-8'))['testi_sensati']['Historical - Latin - Literary - NT (Vulgate)']['primi 2 segni']['rapporto'])
        return
    pagine = [[[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars] for pars in e341.pagine().values()]
    tutto = OrderedDict([('Q', q_capo(pagine, rnd)), ('margine', margine(pagine, rnd))])
    sub = []
    for _ in range(SOTTOINSIEMI):
        ordine = rnd.sample(pagine, len(pagine))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese.append(p)
            n += sum(len(r) for par in p for r in par)
        sub.append(OrderedDict([('Q', q_capo(prese, rnd)), ('margine', margine(prese, rnd))]))
        print(json.dumps(sub[-1]), flush=True)
    med = OrderedDict((k, statistics.median(s[k] for s in sub)) for k in ('Q', 'margine'))
    lingue = json.load(open(os.path.join(RISULTATI, 'e3c84_confronti_per_lingua.json'), encoding='utf-8'))['statistiche']
    marg_l = sorted(lingue['margine']['lingua']['valori'].values())
    p10 = statistics.quantiles(marg_l, n=10)[0]
    esito = OrderedDict([
        ('riga chiusa', 'regge a 10.000 parole' if med['Q'] <= 0.10 else 'non regge a 10.000 parole'),
        ('margine', ('regge a 10.000 parole' if med['margine'] <= p10 else 'non regge a 10.000 parole') + ' (10° percentile delle lingue %.2f)' % p10)])
    out = OrderedDict([('tutto', tutto), ('sottoinsiemi', sub), ('mediane', med), ('margine_lingue_p10', p10), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c89_riga_a_lunghezza_pari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c89 — Riga chiusa e margine del Voynich a 10.000 parole', '', 'Preregistrazione: `preregistrazioni/e3c89.md`.', '',
          '| misura | tutto il Voynich | 5 sottoinsiemi da 10.000 parole | mediana | riferimento delle lingue |', '|---|---|---|---|---|',
          '| Q (a capo / nella riga) | %.3f | %s | %.3f | lingue: mediana %.2f; Q ≤ 0,10 solo in ebraico |' % (tutto['Q'], ', '.join('%.3f' % s['Q'] for s in sub), med['Q'], lingue['a_capo_Q']['lingua']['mediana']),
          '| margine (rapporto) | %.3f | %s | %.3f | 10° percentile %.2f |' % (tutto['margine'], ', '.join('%.3f' % s['margine'] for s in sub), med['margine'], p10),
          '', 'Esito: riga chiusa **%s**; margine **%s**.' % (esito['riga chiusa'], esito['margine'])]
    open(os.path.join(RISULTATI, 'e3c89_riga_a_lunghezza_pari.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
