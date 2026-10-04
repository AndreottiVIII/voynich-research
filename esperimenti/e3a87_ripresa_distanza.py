# -*- coding: utf-8 -*-
"""Esperimento e3a87: ripetizione identica di una parola a distanza d (in parole) nello stesso paragrafo, separando le
coppie nella stessa riga e a cavallo dell'a capo; eccesso rispetto al Voynich riscritto dalla catena di ordine 2.

Preregistrazione: preregistrazioni/e3a87.md. Scrive risultati/e3a87_ripresa_distanza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
DMAX = 30
CONFRONTO = range(3, 9)
BOOT = 1000


def conta_par(par):
    """{(d, tipo): [colpi, coppie]} per un paragrafo."""
    seq = [(w, i) for i, r in enumerate(par) for w in r]
    c = defaultdict(lambda: [0, 0])
    for t, (w, ri) in enumerate(seq):
        if len(w) < 3:
            continue
        for d in range(1, DMAX + 1):
            if t - d < 0:
                break
            v, rj = seq[t - d]
            tipo = 'stessa riga' if rj == ri else 'a cavallo'
            x = c[d, tipo]
            x[0] += v == w
            x[1] += 1
    return c


def somma(cc):
    out = defaultdict(lambda: [0, 0])
    for c in cc:
        for k, (a, b) in c.items():
            out[k][0] += a
            out[k][1] += b
    return out


def quote(c):
    return {k: a / b for k, (a, b) in c.items() if b}


def confronto(c_vero, q_base):
    num = {'stessa riga': 0.0, 'a cavallo': 0.0}
    den = {'stessa riga': 0.0, 'a cavallo': 0.0}
    for d in CONFRONTO:
        for tipo in num:
            a, b = c_vero.get((d, tipo), (0, 0))
            if b and (d, tipo) in q_base:
                num[tipo] += a - b * q_base[d, tipo]
                den[tipo] += b
    e = {t: num[t] / den[t] if den[t] else None for t in num}
    return e['stessa riga'] - e['a cavallo'], e


def main():
    rnd = random.Random(3187)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append([par for par in pp if par])
    per_par = [conta_par(par) for pars in pagine for par in pars]
    vero = somma(per_par)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    base = somma([conta_par(par) for _ in range(e3a78.RISCRITTURE) for pars in e3a78.riscrivi(pagine, tab, rnd) for par in pars])
    qb = quote(base)
    qv = quote(vero)
    diff, e = confronto(vero, qb)
    boot = sorted(confronto(somma([per_par[rnd.randrange(len(per_par))] for _ in per_par]), qb)[0] for _ in range(BOOT))
    ic = [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]]
    esito = 'solo memoria' if ic[0] <= 0 <= ic[1] else ('la riga sopra conta di più' if ic[1] < 0 else 'la riga in corso conta di più')
    profilo = OrderedDict()
    for d in range(1, DMAX + 1):
        profilo[d] = OrderedDict((tipo, OrderedDict([('coppie', vero[d, tipo][1]), ('vero', qv.get((d, tipo))), ('base', qb.get((d, tipo))),
                                                     ('eccesso', (qv[d, tipo] - qb[d, tipo]) if (d, tipo) in qv and (d, tipo) in qb else None)]))
                                 for tipo in ('stessa riga', 'a cavallo') if vero[d, tipo][1])
    out = OrderedDict([('eccesso_medio_3_8', e), ('differenza', diff), ('IC95', ic), ('esito', esito), ('profilo', profilo)])
    print(json.dumps(OrderedDict((k, v) for k, v in out.items() if k != 'profilo'), ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a87_ripresa_distanza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: '–' if v is None else '%+.4f' % v
    md = ['# e3a87 — La ripresa dipende solo da quanto tempo fa si è scritta la parola, o la riga sopra conta di più?', '', 'Preregistrazione: `preregistrazioni/e3a87.md`. Eccesso = quota di parole identiche a distanza d nel vero meno nel riscritto dalla catena.', '',
          'Eccesso medio per d da 3 a 8: stessa riga %s, a cavallo dell\'a capo %s. Differenza **%+.4f**, IC 95%% %+.4f – %+.4f.' % (f(e['stessa riga']), f(e['a cavallo']), diff, ic[0], ic[1]), '',
          'Esito: **%s**.' % esito, '', '| d | coppie stessa riga | eccesso stessa riga | coppie a cavallo | eccesso a cavallo |', '|---|---|---|---|---|']
    for d, x in profilo.items():
        s, c = x.get('stessa riga', {}), x.get('a cavallo', {})
        md.append('| %d | %s | %s | %s | %s |' % (d, s.get('coppie', 0), f(s.get('eccesso')), c.get('coppie', 0), f(c.get('eccesso'))))
    open(os.path.join(RISULTATI, 'e3a87_ripresa_distanza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
