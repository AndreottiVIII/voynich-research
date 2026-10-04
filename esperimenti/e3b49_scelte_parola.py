# -*- coding: utf-8 -*-
"""Esperimento e3b49: risparmio in bit, fuori campione, nel prevedere una scelta di grafia (qo/o, k/t, sh/ch, -ey/-dy)
conoscendo la parola intera oltre ai segni vicini (due prima e due dopo); Voynich contro il Voynich riscritto dalla
propria catena di ordine 2; generatori come descrittivo.

Preregistrazione: preregistrazioni/e3b49.md. Scrive risultati/e3b49_scelte_parola.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e341_fonti as e341
import e380_sandhi as e380
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
BETA = 2.0
S, I, F = ' ', '^', '$'
CLASSI = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')


def eventi_riga(r):
    """[(classe, contesto, parola, scelta)] per una riga (lista di parole, tuple di segni)."""
    seq, inizio = [I, I], []
    for j, w in enumerate(r):
        if j:
            seq.append(S)
        inizio.append(len(seq))
        seq += list(w)
    seq += [F, F]
    out = []
    for j, w in enumerate(r):
        a = inizio[j]
        x = e380.ini_qo(w)
        if x:
            resto, v = x
            prima = r[j - 1][-1] if j else I
            out.append(('qo/o', (prima, resto[0], resto[1] if len(resto) > 1 else S), resto, v))
        for classe, coppia in (('k/t', ('k', 't')), ('sh/ch', ('sh', 'ch'))):
            pos = [i for i, s in enumerate(w) if s in coppia]
            if len(pos) != 1:
                continue
            if classe == 'k/t' and any(s in GALLOWS for i, s in enumerate(w) if i != pos[0]):
                continue
            i = a + pos[0]
            ctx = (seq[i - 2], seq[i - 1], seq[i + 1], seq[i + 2])
            out.append((classe, ctx, w[:pos[0]] + ('*',) + w[pos[0] + 1:], w[pos[0]]))
        y = e380.fin_dyey(w)
        if y:
            tronco, v = y
            i = a + len(w) - 2
            out.append(('-ey/-dy', (seq[i - 2], seq[i - 1]), tronco, v))
    return out


def risparmio(treno, prova):
    """Bit per occorrenza di A − B sulla prova, stimando sul treno."""
    n0, nc, ncr = Counter(), defaultdict(Counter), defaultdict(Counter)
    for ctx, par, v in treno:
        n0[v] += 1
        nc[ctx][v] += 1
        ncr[(ctx, par)][v] += 1
    N = sum(n0.values())
    valori = set(n0) | {v for _, _, v in prova}
    K = len(valori)
    ba = bb = 0.0
    for ctx, par, v in prova:
        p0 = (n0[v] + 0.5) / (N + 0.5 * K)
        c = nc.get(ctx, Counter())
        pa = (c[v] + p0) / (sum(c.values()) + 1)
        cr = ncr.get((ctx, par), Counter())
        pb = (cr[v] + BETA * pa) / (sum(cr.values()) + BETA)
        ba -= math.log2(pa)
        bb -= math.log2(pb)
    return (ba - bb), len(prova)


def misura(pagine):
    """{classe: (risparmio in bit per occorrenza, occorrenze)} con pagine pari/dispari."""
    per = {c: ([], []) for c in CLASSI}
    for k, pars in enumerate(pagine):
        for par in pars:
            for r in par:
                for c, ctx, par_, v in eventi_riga(r):
                    per[c][k % 2].append((ctx, par_, v))
    out = OrderedDict()
    for c in CLASSI:
        a, b = per[c]
        if not a or not b:
            out[c] = (None, 0)
            continue
        s1, n1 = risparmio(a, b)
        s2, n2 = risparmio(b, a)
        out[c] = ((s1 + s2) / (n1 + n2), n1 + n2)
    return out


def a_pagine(righe, n=25):
    return [[righe[i:i + n]] for i in range(0, len(righe), n)]


def main():
    rnd = random.Random(3249)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp:
            pagine.append(pp)
    voy = misura(pagine)
    print('Voynich', json.dumps(voy), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    catene = []
    for k in range(5):
        catene.append(misura(e3a78.riscrivi(pagine, tab, rnd)))
        print('catena', k, json.dumps(catene[-1]), flush=True)
    gen = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            gen[k] = misura(a_pagine([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]))
            print(k, json.dumps(gen[k]), flush=True)
    gen['Timm e Schinner, seme 1'] = misura(a_pagine([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]))
    print('T&S', json.dumps(gen['Timm e Schinner, seme 1']), flush=True)
    sopra = sotto = 0
    conf = OrderedDict()
    for c in CLASSI:
        vc = voy[c][0]
        cs = [x[c][0] for x in catene if x[c][0] is not None]
        mx, mm = max(cs), sum(cs) / len(cs)
        conf[c] = OrderedDict([('voynich', vc), ('catena_media', mm), ('catena_max', mx), ('occorrenze', voy[c][1])])
        if vc > mx and vc - mm >= 0.01:
            sopra += 1
        if vc <= mx or vc - mx < 0.005:
            sotto += 1
    esito = 'le scelte sono legate alla parola' if sopra >= 3 else ('solo segni vicini' if sotto >= 3 else 'incerto')
    out = OrderedDict([('confronto', conf), ('catene', catene), ('generatori', gen), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b49_scelte_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b49 — Le scelte di grafia sono legate alla parola intera o solo ai segni vicini?', '', 'Preregistrazione: `preregistrazioni/e3b49.md`. Risparmio in bit per occorrenza, fuori campione, conoscendo la parola oltre ai segni vicini.', '',
          '| classe | occorrenze (Voynich) | Voynich | catena: media (massimo di 5) | ' + ' | '.join(gen) + ' |', '|---|---|---|---|' + '---|' * len(gen)]
    f = lambda x: '%.4f' % x if x is not None else 'n.d.'
    for c in CLASSI:
        x = conf[c]
        md.append('| %s | %d | %s | %s (%s) | ' % (c, x['occorrenze'], f(x['voynich']), f(x['catena_media']), f(x['catena_max'])) + ' | '.join('%s (%d)' % (f(g[c][0]), g[c][1]) for g in gen.values()) + ' |')
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b49_scelte_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
