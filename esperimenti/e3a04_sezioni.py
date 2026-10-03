# -*- coding: utf-8 -*-
"""Esperimento e3a04: giuntura nella riga, giuntura a capo, regole di qo- e di -l/-r, sezione per sezione.

Preregistrazione: preregistrazioni/e3a04.md. Scrive risultati/e3a04_sezioni.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386
import e390_scomposizione as e390
import e395_takahashi as e395

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a'}
NOMI = {'H': 'erbario', 'B': 'biologia', 'S': 'ricette', 'P': 'farmacia', 'T': 'solo testo', 'C': 'cosmologia', 'A': 'astronomia', 'Z': 'zodiaco'}


def main():
    rnd = random.Random(3104)
    rr = e386.righe()
    riga = defaultdict(lambda: defaultdict(list))
    capo = defaultdict(lambda: defaultdict(list))
    qo, lr = defaultdict(list), defaultdict(list)
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        sez = st.split('-')[0]
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            riga[sez][pag].append((a[-1], b[0]))
            q = e380.ini_qo(b)
            if q and (a[-1] in V or a[-1] in C):
                qo[sez].append((a[-1] in V, q[1] == 'qo'))
            f = e380.fin_lr(a)
            if f and (b[0] in K or b[0] in A):
                lr[sez].append((b[0] in K, f[1] == 'l'))
        if k + 1 < len(rr) and rr[k + 1][1] == pag and rr[k + 1][2] == npar and ws[-1] and rr[k + 1][3][0]:
            capo[sez][pag].append((ws[-1][-1], rr[k + 1][3][0][0]))
    ris = OrderedDict()
    tutte = True
    for sez in sorted(riga, key=lambda s: -sum(len(x) for x in riga[s].values())):
        n = sum(len(x) for x in riga[sez].values())
        if n < 1000:
            continue
        x = OrderedDict([('coppie', n)])
        g = e390.prova(riga[sez], rnd)
        c = e390.prova(capo[sez], rnd)
        x['1 giuntura nella riga'] = OrderedDict([('E', g['E']), ('z', g['z']), ('regge', g['z'] > 3)])
        x['2 giuntura a capo'] = OrderedDict([('coppie', c['coppie']), ('E', c['E']), ('z', c['z']), ('regge', c['z'] < 2)])
        for nome, ev in (('3 regola di qo-', qo[sez]), ('4 regola di -l/-r', lr[sez])):
            na = sum(1 for cl, _ in ev if cl)
            nb = len(ev) - na
            if na < 30 or nb < 30:
                x[nome] = OrderedDict([('eventi', [na, nb]), ('regge', None)])
                continue
            r = e395.regola(ev, rnd)
            x[nome] = OrderedDict([('eventi', [na, nb]), ('differenza', r['differenza']), ('p', r['p']), ('regge', r['differenza'] > 0 and r['p'] < 0.01)])
        for k_, v in x.items():
            if isinstance(v, dict) and v.get('regge') is False:
                tutte = False
        ris[sez] = x
        print(sez, json.dumps(x, default=float), flush=True)
    esito = 'le proprietà reggono in tutte le sezioni' if tutte else 'non reggono ovunque'
    out = OrderedDict([('sezioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a04_sezioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a04 — Giuntura e raccordo reggono in ogni sezione del libro?', '', 'Preregistrazione: `preregistrazioni/e3a04.md`.', '',
          '| sezione | coppie | giuntura nella riga E (z) | a capo E (z) | regola qo- Δ (p) | regola -l/-r Δ (p) |', '|---|---|---|---|---|---|']
    for sez, x in ris.items():
        def r(nome):
            v = x[nome]
            if v['regge'] is None:
                return 'pochi dati (%d / %d)' % tuple(v['eventi'])
            return '%+.2f (%.4f)%s' % (v['differenza'], v['p'], '' if v['regge'] else ' NO')
        g, c = x['1 giuntura nella riga'], x['2 giuntura a capo']
        md.append('| %s | %d | %.3f (%.1f)%s | %.3f (%.1f)%s | %s | %s |' % (NOMI.get(sez, sez), x['coppie'], g['E'], g['z'], '' if g['regge'] else ' NO', c['E'], c['z'], '' if c['regge'] else ' NO', r('3 regola di qo-'), r('4 regola di -l/-r')))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a04_sezioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
