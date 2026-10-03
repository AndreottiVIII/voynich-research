# -*- coding: utf-8 -*-
"""Esperimento 393: (1) qo-/o- a inizio riga dipende dall'ultimo segno della riga sopra? (2) giuntura e giuntura
neutralizzata in lingua A e in lingua B a parita' di coppie.

Preregistrazione: preregistrazioni/e393.md. Scrive risultati/e393_inizio_riga_ab.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386
import e390_scomposizione as e390

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 10000


def main():
    rnd = random.Random(393)
    rr = e386.righe()
    # parte 1
    ev = []    # (strato, classe V, qo)
    prima = defaultdict(Counter)
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        if not ws or not ws[0]:
            continue
        q = e380.ini_qo(ws[0])
        if not q:
            continue
        stesso = k > 0 and rr[k - 1][1] == pag and rr[k - 1][2] == npar
        prima[st][('altre righe' if stesso else 'prima riga del paragrafo', q[1] == 'qo')] += 1
        if stesso:
            ult = rr[k - 1][3][-1]
            if ult and (ult[-1] in V or ult[-1] in C):
                ev.append((st, ult[-1] in V, q[1] == 'qo'))

    def delta(e):
        per = defaultdict(list)
        for s, c, q in e:
            per[s].append((c, q))
        num = den = 0.0
        for xs in per.values():
            a = [q for c, q in xs if c]
            b = [q for c, q in xs if not c]
            if a and b:
                num += len(xs) * (sum(a) / len(a) - sum(b) / len(b))
                den += len(xs)
        return num / den if den else 0.0
    d = delta(ev)
    per = defaultdict(list)
    for i, e in enumerate(ev):
        per[e[0]].append(i)
    nul = []
    for _ in range(PERM):
        e2 = [list(e) for e in ev]
        for idx in per.values():
            vals = [ev[i][1] for i in idx]
            rnd.shuffle(vals)
            for i, v in zip(idx, vals):
                e2[i][1] = v
        nul.append(delta(e2))
    p = sum(x >= d for x in nul) / PERM
    esito1 = 'qo- a inizio riga segue la fine della riga sopra' if d > 0 and p < 0.01 else ('non la segue' if p > 0.1 else 'incerto')
    tab_prima = OrderedDict()
    for st, c in sorted(prima.items()):
        for tipo in ('prima riga del paragrafo', 'altre righe'):
            n = c[(tipo, True)] + c[(tipo, False)]
            if n >= 10:
                tab_prima['%s, %s' % (st, tipo)] = OrderedDict([('eventi', n), ('P_qo', c[(tipo, True)] / n)])
    # parte 2
    vero, neutra = {'A': defaultdict(list), 'B': defaultdict(list)}, {'A': defaultdict(list), 'B': defaultdict(list)}
    for st, pag, npar, ws, seps in rr:
        lg = st.split('-')[1]
        if lg not in ('A', 'B'):
            continue
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            vero[lg][pag].append((a[-1], b[0]))
            q = e380.ini_qo(b)
            neutra[lg][pag].append(('l|r' if a[-1] in ('l', 'r') else a[-1], 'o' if q and q[1] == 'qo' else b[0]))
    n_min = min(sum(len(x) for x in vero[lg].values()) for lg in 'AB')

    def campioni(dati):
        pagine = list(dati)
        out = []
        for _ in range(20):
            ordine = rnd.sample(pagine, len(pagine))
            sub, n = {}, 0
            for pg in ordine:
                if n >= n_min:
                    break
                sub[pg] = dati[pg]
                n += len(dati[pg])
            out.append(e390.prova(sub, rnd)['E'])
        return out
    p2 = OrderedDict()
    for nome, dd in (('giuntura', vero), ('neutralizzata', neutra)):
        p2[nome] = OrderedDict((lg, campioni(dd[lg])) for lg in 'AB')
    A, B = p2['giuntura']['A'], p2['giuntura']['B']
    if statistics.median(B) > max(A):
        esito2 = 'giuntura più forte in B'
    elif statistics.median(A) > max(B):
        esito2 = 'giuntura più forte in A'
    else:
        esito2 = 'uguale'
    out = OrderedDict([('parte1', OrderedDict([('eventi', len(ev)), ('delta', d), ('p', p), ('qo_per_tipo_di_riga', tab_prima), ('esito', esito1)])),
                       ('parte2', OrderedDict([('coppie_per_campione', n_min), ('E', p2), ('esito', esito2)]))])
    print(json.dumps(out, ensure_ascii=False, default=float)[:3000], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e393_inizio_riga_ab.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    med = lambda xs: statistics.median(xs)
    md = ['# e393 — qo- a inizio riga e giuntura in lingua A e B', '', 'Preregistrazione: `preregistrazioni/e393.md`.', '',
          '## Parte 1', '', 'Prime parole *qo*/*o* + gallows (righe non d\'inizio paragrafo) con la riga sopra che finisce in V o C: %d. Δ = %+.3f, p %.4f. Esito: **%s**.' % (len(ev), d, p, esito1), '',
          '| strato e tipo di riga | eventi | P(qo) a inizio riga |', '|---|---|---|']
    md += ['| %s | %d | %.2f |' % (k, x['eventi'], x['P_qo']) for k, x in tab_prima.items()]
    md += ['', '## Parte 2', '', 'Campioni di %d coppie (mediana e intervallo di 20).' % n_min, '', '| misura | A | B |', '|---|---|---|']
    for nome, x in p2.items():
        md.append('| %s | %.4f (%.4f – %.4f) | %.4f (%.4f – %.4f) |' % (nome, med(x['A']), min(x['A']), max(x['A']), med(x['B']), min(x['B']), max(x['B'])))
    md += ['', 'Esito: **%s**.' % esito2]
    open(os.path.join(RISULTATI, 'e393_inizio_riga_ab.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
