# -*- coding: utf-8 -*-
"""Esperimenti 341, 344, 345 sulle "fonti" (parole uguali o a una modifica). (e341) fra la fine del recto e l'inizio del
verso c'e' piu' ripresa che fra l'inizio del recto e la fine del verso? (e344) le parole d'inizio paragrafo hanno una
fonte nelle righe sopra? (e345) la prima e l'ultima parola della riga riprendono la prima e l'ultima della riga sopra?

Preregistrazione: preregistrazioni/e341.md. Scrive risultati/e341_fonti.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e310_inizi_etichette as e310

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
_CACHE, _U = {}, {}


def u(w):
    if w not in _U:
        _U[w] = tuple(D(w))
    return _U[w]


def simile(a, b):
    if a == b:
        return True
    k = (a, b) if a < b else (b, a)
    if k not in _CACHE:
        x, y = u(a), u(b)
        _CACHE[k] = abs(len(x) - len(y)) <= 1 and e310.dist1(x, y)
    return _CACHE[k]


def ha_fonte(w, parole):
    return any(simile(w, x) for x in parole)


def pagine():
    """{pagina: [paragrafi]}, paragrafo = lista di righe (parole), nell'ordine del libro."""
    per = {}
    ordine = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
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


def segno_flip(d, rnd, n=1000):
    v = statistics.mean(d)
    nul = [statistics.mean(x * rnd.choice((-1, 1)) for x in d) for _ in range(n)]
    return v, (v - statistics.mean(nul)) / (statistics.pstdev(nul) or 1)


def ripresa(b1, b2):
    w1 = [w for r in b1 for w in r]
    w2 = [w for r in b2 for w in r]
    a = statistics.mean(ha_fonte(w, w1) for w in w2)
    b = statistics.mean(ha_fonte(w, w2) for w in w1)
    return (a + b) / 2


def e341(pag, testa, rnd):
    righe = {p: [r for par in pars for r in par] for p, pars in pag.items()}
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seg = dict(zip(ordine, ordine[1:]))
    fogli, aperture = [], []
    for p in pag:
        h, q = testa.get(p), seg.get(p)
        if not h or not q or q not in pag or len(righe[p]) < 6 or len(righe[q]) < 6:
            continue
        a, b = righe[p], righe[q]
        diff = ripresa(a[-3:], b[:3]) - ripresa(a[:3], b[-3:])
        if h['lato'] == 'r' and testa[q]['lato'] == 'v' and testa[q]['F'] == h['F']:
            fogli.append(diff)
        elif h['lato'] == 'v' and testa[q]['lato'] == 'r':
            aperture.append(diff)
    vf, zf = segno_flip(fogli, rnd)
    va, za = segno_flip(aperture, rnd)
    esito = 'scritto di seguito girando il foglio' if zf > 3 else ('no' if zf < 2 else 'incerto')
    return OrderedDict([('fogli', OrderedDict([('coppie', len(fogli)), ('vicina_meno_lontana', vf), ('z', zf)])),
                        ('aperture', OrderedDict([('coppie', len(aperture)), ('vicina_meno_lontana', va), ('z', za)])), ('esito', esito)])


def nucleo(w):
    x = u(w)
    return ''.join(x[1:]) if (x[0] in GALL and len(x) >= 3) else w


def e344(pag, rnd):
    gruppi = {'a': [], 'b': []}     # (pagina, indice riga, parola)
    righe = {p: [(k == 0, r) for par in pars for k, r in enumerate(par)] for p, pars in pag.items()}
    for p, rr in righe.items():
        for i in range(2, len(rr)):
            ini, r = rr[i]
            gruppi['a' if ini else 'b'].append((p, i, r[0]))

    def quota(voci, f, casuale):
        si = 0
        for p, i, w in voci:
            rr = righe[p]
            if casuale:
                altre = [k for k in range(len(rr)) if k != i]
                ks = rnd.sample(altre, 2)
            else:
                ks = [i - 1, i - 2]
            si += ha_fonte(f(w), [x for k in ks for x in rr[k][1]])
        return si / len(voci)
    out = OrderedDict()
    for g in ('a', 'b'):
        for nome, f in (('parola intera', lambda w: w), ('nucleo', nucleo)):
            v = quota(gruppi[g], f, False)
            nul = [quota(gruppi[g], f, True) for _ in range(200)]
            out['%s, %s' % ({'a': '(a) prime parole dei paragrafi', 'b': '(b) prime parole delle altre righe'}[g], nome)] = OrderedDict([
                ('parole', len(gruppi[g])), ('righe_sopra', v), ('nullo', statistics.mean(nul)), ('eccesso', v - statistics.mean(nul)),
                ('z', (v - statistics.mean(nul)) / (statistics.pstdev(nul) or 1))])
    z = out['(a) prime parole dei paragrafi, parola intera']['z']
    esito = 'la prima parola del paragrafo riprende le righe sopra' if z > 3 else ('parole nuove anche rispetto alle righe sopra' if z < 2 else 'incerto')
    return OrderedDict([('gruppi', out), ('esito', esito)])


def e345(pag, rnd):
    coppie = []     # (paragrafo, i)
    pars = [par for pars_ in pag.values() for par in pars_ if len(par) >= 4]
    for k, par in enumerate(pars):
        for i in range(1, len(par)):
            if len(par[i]) >= 3 and len(par[i - 1]) >= 3:
                coppie.append((k, i))

    def misure_(sopra_di):
        pr = ul = 0
        mz = []
        for (k, i) in coppie:
            r, s = pars[k][i], pars[k][sopra_di(k, i)]
            pr += simile(r[0], s[0])
            ul += simile(r[-1], s[-1])
            n = min(len(r), len(s))
            if n >= 3:
                mz.append(statistics.mean(simile(r[j], s[j]) for j in range(1, n - 1)))
        return pr / len(coppie), ul / len(coppie), statistics.mean(mz)

    def caso(k, i):
        altre = [j for j in range(len(pars[k])) if j not in (i, i - 1) and len(pars[k][j]) >= 3]
        return rnd.choice(altre) if altre else i - 1
    vero = misure_(lambda k, i: i - 1)
    nul = [misure_(caso) for _ in range(200)]
    out = OrderedDict()
    for j, nome in enumerate(('prima parola', 'ultima parola', 'parole in mezzo, stessa posizione')):
        m, sd = statistics.mean(n[j] for n in nul), statistics.pstdev(n[j] for n in nul)
        out[nome] = OrderedDict([('quota', vero[j]), ('nullo', m), ('rapporto', vero[j] / m if m else None), ('z', (vero[j] - m) / (sd or 1))])
    bordi = [n for n in ('prima parola', 'ultima parola') if out[n]['z'] > 3]
    return OrderedDict([('coppie_di_righe', len(coppie)), ('misure', out), ('esito', 'colonna dei bordi: ' + ', '.join(bordi) if bordi else 'nessuna colonna dei bordi')])


def main():
    pag = pagine()
    testa = e308.intestazioni()
    r341 = e341(pag, testa, random.Random(341))
    print('e341', r341, flush=True)
    r345 = e345(pag, random.Random(345))
    print('e345', r345['esito'], {k: (round(v['quota'], 3), round(v['nullo'], 3), round(v['z'], 1)) for k, v in r345['misure'].items()}, flush=True)
    r344 = e344(pag, random.Random(344))
    print('e344', r344['esito'], {k: (round(v['righe_sopra'], 3), round(v['nullo'], 3), round(v['z'], 1)) for k, v in r344['gruppi'].items()}, flush=True)
    json.dump(OrderedDict([('e341', r341), ('e344', r344), ('e345', r345)]), open(os.path.join(RISULTATI, 'e341_fonti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e341, e344, e345 — Girando il foglio con le fonti; le parole d\'inizio paragrafo; colonne e bordi', '', 'Preregistrazione: `preregistrazioni/e341.md`.', '', '## e341', '',
          '- Fogli (fine recto + inizio verso, contro inizio recto + fine verso): %+.4f su %d fogli, z %.1f.' % (r341['fogli']['vicina_meno_lontana'], r341['fogli']['coppie'], r341['fogli']['z']),
          '- Aperture (fine verso + inizio recto seguente, contro gli estremi opposti): %+.4f su %d, z %.1f.' % (r341['aperture']['vicina_meno_lontana'], r341['aperture']['coppie'], r341['aperture']['z']),
          '', 'Esito e341: **%s**.' % r341['esito'], '', '## e344', '', '| gruppo | parole | fonte nelle 2 righe sopra | nullo (2 righe a caso della pagina) | eccesso | z |', '|---|---|---|---|---|---|']
    for k, v in r344['gruppi'].items():
        md.append('| %s | %d | %.3f | %.3f | %+.3f | %.1f |' % (k, v['parole'], v['righe_sopra'], v['nullo'], v['eccesso'], v['z']))
    md += ['', 'Esito e344: **%s**.' % r344['esito'], '', '## e345 — %d coppie di righe consecutive' % r345['coppie_di_righe'], '',
           '| parola | con fonte nella stessa posizione della riga sopra | nullo (un\'altra riga del paragrafo) | rapporto | z |', '|---|---|---|---|---|']
    for k, v in r345['misure'].items():
        md.append('| %s | %.3f | %.3f | %.2f | %.1f |' % (k, v['quota'], v['nullo'], v['rapporto'], v['z']))
    md += ['', 'Esito e345: **%s**.' % r345['esito']]
    open(os.path.join(RISULTATI, 'e341_fonti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
