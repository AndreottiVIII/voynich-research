# -*- coding: utf-8 -*-
"""Esperimento e3a43: sette proprieta' della notte, separatamente nella prima e nella seconda meta' del libro.

Preregistrazione: preregistrazioni/e3a43.md. Scrive risultati/e3a43_due_meta.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386
import e389_varianti_bordo as e389
import e390_scomposizione as e390
import e3a25_inizi_evitati as e3a25

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a'}


def proprieta(rr, rnd):
    """rr: righe nel formato di e386.righe()."""
    out = OrderedDict()
    riga, capo = defaultdict(list), defaultdict(list)
    qo, lr = [], []
    terne = []
    fine = []
    par = OrderedDict()
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        par.setdefault((pag, npar), []).append([w for w in ws if w])
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            riga[pag].append((a[-1], b[0]))
            q = e380.ini_qo(b)
            if q and (a[-1] in V or a[-1] in C):
                qo.append((a[-1] in V, q[1] == 'qo'))
            f = e380.fin_lr(a)
            if f and (b[0] in K or b[0] in A):
                lr.append((b[0] in K, f[1] == 'l'))
        if k + 1 < len(rr) and rr[k + 1][1] == pag and rr[k + 1][2] == npar and ws[-1] and rr[k + 1][3][0]:
            capo[pag].append((ws[-1][-1], rr[k + 1][3][0][0]))
        ww = [w for w in ws if w]
        for a, b, c in zip(ww, ww[1:], ww[2:]):
            terne.append(((pag, b), a[-1], c[0]))
        n = len(ww)
        for j, w in enumerate(ww):
            if len(w) >= 2 and (0 < j < n - 1 or j == n - 1) and n >= 2:
                fine.append(((st, w[:-1]), j == n - 1, w[-1]))
    g = e390.prova(riga, rnd)
    c = e390.prova(capo, rnd)
    out['1 giuntura nella riga'] = OrderedDict([('E', g['E']), ('z', g['z']), ('regge', g['z'] > 3)])
    out['2 giuntura a capo'] = OrderedDict([('E', c['E']), ('z', c['z']), ('regge', abs(c['z']) < 2)])
    for nome, ev in (('3 regola di qo-', qo), ('4 regola di -l/-r', lr)):
        d = sum(s for cl, s in ev if cl) / max(1, sum(1 for cl, _ in ev if cl)) - sum(s for cl, s in ev if not cl) / max(1, sum(1 for cl, _ in ev if not cl))
        cl = [c_ for c_, _ in ev]
        sc = [s for _, s in ev]
        nul = []
        for _ in range(2000):
            rnd.shuffle(cl)
            a_ = [s for c_, s in zip(cl, sc) if c_]
            b_ = [s for c_, s in zip(cl, sc) if not c_]
            nul.append(sum(a_) / len(a_) - sum(b_) / len(b_))
        p = sum(v >= d for v in nul) / len(nul)
        out[nome] = OrderedDict([('differenza', d), ('p', p), ('regge', d > 0 and p < 0.01)])
    blocchi = [e3a25.inizi(p[1:], 2) for p in par.values() if len(p) >= 4]
    m = e3a25.prova(blocchi, rnd, 1000)
    out['5 margine sinistro'] = OrderedDict([('rapporto', m['rapporto']), ('z', m['z']), ('regge', m['rapporto'] < 1 and m['z'] < -3)])
    t = e380.prova(terne, rnd, 1000)
    out['6 nessun legame a distanza 2'] = OrderedDict([('E', t['E']), ('z', t['z']), ('regge', abs(t['z']) < 2)])
    f6 = e389.analizza(fine, np.random.RandomState(rnd.randrange(10 ** 6)))
    zm, zr = f6['segni'].get('m', {}).get('z', 0.0), f6['segni'].get('r', {}).get('z', 0.0)
    out['7 -m al posto di -r'] = OrderedDict([('z_m', zm), ('z_r', zr), ('regge', zm > 3 and zr < -3)])
    return out


def main():
    rnd = random.Random(3143)
    rr = e386.righe()
    pagine = []
    for st, pag, npar, ws, seps in rr:
        if pag not in pagine:
            pagine.append(pag)
    meta = set(pagine[:len(pagine) // 2])
    ris = OrderedDict()
    for nome, sel in (('prima metà', lambda p: p in meta), ('seconda metà', lambda p: p not in meta)):
        ris[nome] = proprieta([x for x in rr if sel(x[1])], rnd)
        print(nome, json.dumps(ris[nome], ensure_ascii=False, default=float), flush=True)
    mancano = ['%s (%s)' % (k, m) for m, x in ris.items() for k, v in x.items() if not v['regge']]
    esito = 'tutte le proprietà reggono in tutte e due le metà' if not mancano else 'non reggono: ' + ', '.join(mancano)
    out = OrderedDict([('pagine_per_meta', [len(meta), len(pagine) - len(meta)]), ('prima_pagina_seconda_meta', pagine[len(pagine) // 2]), ('meta', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a43_due_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a43 — Le proprietà principali della notte reggono in tutte e due le metà del libro?', '', 'Preregistrazione: `preregistrazioni/e3a43.md`. Pagine per metà: %d e %d; la seconda metà comincia da %s.' % (len(meta), len(pagine) - len(meta), out['prima_pagina_seconda_meta']), '',
          '| proprietà | prima metà | seconda metà |', '|---|---|---|']
    for k in ris['prima metà']:
        cell = []
        for m in ('prima metà', 'seconda metà'):
            v = ris[m][k]
            vals = ', '.join('%s %.3f' % (kk, vv) for kk, vv in v.items() if kk != 'regge')
            cell.append('%s (%s)' % ('regge' if v['regge'] else 'NON regge', vals))
        md.append('| %s | %s | %s |' % (k, cell[0], cell[1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a43_due_meta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
