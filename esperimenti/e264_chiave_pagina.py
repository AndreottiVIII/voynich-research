# -*- coding: utf-8 -*-
"""Esperimento 264: applicando a ogni pagina la combinazione migliore di scambi fra segni simili (ch/sh, k/t, p/f, ckh/cth,
cph/cfh, l/r), quanto cresce la quota delle sue parole attestate nel resto del testo? Voynich contro generatore (negativo)
e generatore con una chiave di pagina a caso (positivo).

Preregistrazione: preregistrazioni/e264.md. Scrive risultati/e264_chiave_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from itertools import product

from scipy.stats import mannwhitneyu

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
FAMIGLIE = [('ch', 'sh'), ('k', 't'), ('p', 'f'), ('ckh', 'cth'), ('cph', 'cfh'), ('l', 'r')]
SEME, MIN_PAROLE = 264, 40
D = e237.D


def scambia(w, attivi):
    m = {}
    for a, b in attivi:
        m[a], m[b] = b, a
    return ''.join(m.get(x, x) for x in D(w))


def guadagni(pagine):
    tot = Counter(w for ws in pagine.values() for w in ws)
    out = []
    combinazioni = [tuple(f for f, s in zip(FAMIGLIE, bits) if s) for bits in product((0, 1), repeat=len(FAMIGLIE))]
    for p, ws in pagine.items():
        if len(ws) < MIN_PAROLE:
            continue
        propri = Counter(ws)
        resto = lambda x: tot[x] - propri[x] > 0
        cache = {}
        cop = []
        for comb in combinazioni:
            n = 0
            for w in ws:
                k = (w, comb)
                if k not in cache:
                    x = scambia(w, comb) if comb else w
                    cache[k] = resto(x)
                n += cache[k]
            cop.append(n / len(ws))
        out.append(max(cop) - cop[0])
    return out


def main():
    rnd = random.Random(SEME)
    c = e224.contesto()
    vp = e231.voynich()
    pv = OrderedDict((p, [w for r in rr for w in r]) for p, (_, rr) in vp.items())
    vpag = OrderedDict((p, rr) for p, (_, rr) in vp.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(vpag))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(vpag)))
    gp = e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102))
    neg = OrderedDict((p, [w for r in rr for w in r]) for p, rr in gp.items())
    pos = OrderedDict()
    for p, ws in neg.items():
        attivi = [f for f in FAMIGLIE if rnd.random() < 0.5]
        pos[p] = [scambia(w, attivi) for w in ws]
    ris = OrderedDict()
    g = OrderedDict([('Voynich', guadagni(pv)), ('generatore e241 (negativo)', guadagni(neg)), ('generatore con chiave di pagina (positivo)', guadagni(pos))])
    for nome, xs in g.items():
        ris[nome] = OrderedDict([('pagine', len(xs)), ('guadagno_medio', statistics.mean(xs)), ('guadagno_mediano', statistics.median(xs))])
        print(nome, dict(ris[nome]), flush=True)
    gv, gn, gpz = g['Voynich'], g['generatore e241 (negativo)'], g['generatore con chiave di pagina (positivo)']
    p_pos = float(mannwhitneyu(gpz, gn, alternative='greater').pvalue)
    p_voy = float(mannwhitneyu(gv, gn, alternative='greater').pvalue)
    mv, mn, mp = statistics.mean(gv), statistics.mean(gn), statistics.mean(gpz)
    valido = mp >= 2 * mn and p_pos < 0.01
    esito = ('non valido' if not valido else 'chiave di pagina' if mv >= 2 * mn and p_voy < 0.01
             else 'nessuna chiave di pagina' if p_voy > 0.05 else 'incerto')
    ris.update([('p_positivo_contro_negativo', p_pos), ('p_Voynich_contro_negativo', p_voy), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e264_chiave_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e264 — Una chiave che cambia a ogni pagina?', '',
          'Guadagno di copertura (parole della pagina attestate nel resto del testo) con la migliore delle 64 combinazioni di scambi %s. '
          'Preregistrazione: `preregistrazioni/e264.md`.' % ', '.join('%s↔%s' % f for f in FAMIGLIE), '',
          '| testo | pagine | guadagno medio | guadagno mediano |', '|---|---|---|---|']
    for nome in g:
        r = ris[nome]
        md.append('| %s | %d | %.4f | %.4f |' % (nome, r['pagine'], r['guadagno_medio'], r['guadagno_mediano']))
    md += ['', 'Mann-Whitney: positivo > negativo p = %.2g; Voynich > negativo p = %.2g. Esito: **%s**.' % (p_pos, p_voy, esito)]
    open(os.path.join(RISULTATI, 'e264_chiave_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
