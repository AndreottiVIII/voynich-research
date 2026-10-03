# -*- coding: utf-8 -*-
"""Esperimento e3a02: e3a01 (-l/-r, la finale della prima parola si adatta alla seconda?) ed e396 (qo-/o-, cambia la
prima o la seconda?) con le fonti cercate nelle 2 righe sopra.

Preregistrazione: preregistrazioni/e3a02.md. Scrive risultati/e3a02_chi_si_adatta_2.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a', 'o', 'y'}
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 10000


def classe(s):
    return 'V' if s in V else ('C' if s in C else None)


def prova(ev, k, rnd):
    """ev: [(conflitto, misura1, misura2, ...)]; differenza conflitti - accordi della misura k e p."""
    et = [e[0] for e in ev]

    def diff(etich):
        a = [e[k] for c, e in zip(etich, ev) if c]
        b = [e[k] for c, e in zip(etich, ev) if not c]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else 0.0
    d = diff(et)
    e2 = list(et)
    nul = []
    for _ in range(PERM):
        rnd.shuffle(e2)
        nul.append(diff(e2))
    qc = [e[k] for e in ev if e[0]]
    qa = [e[k] for e in ev if not e[0]]
    return OrderedDict([('quota_conflitti', sum(qc) / len(qc) if qc else None), ('quota_accordi', sum(qa) / len(qa) if qa else None),
                        ('differenza', d), ('p', sum(x >= d for x in nul) / PERM)])


def main():
    rnd = random.Random(3102)
    par = OrderedDict()
    for st, pag, npar, ws, seps in e386.righe():
        par.setdefault((pag, npar), []).append((ws, seps))
    evA, evB = [], []
    for righe in par.values():
        for i in range(1, len(righe)):
            sopra = [x for q in righe[max(0, i - 2):i] for x in q[0] if x]
            insieme = set(sopra)
            tr_lr, nuclei, tr_vc = defaultdict(set), defaultdict(set), defaultdict(set)
            for x in sopra:
                f = e380.fin_lr(x)
                if f:
                    tr_lr[f[0]].add(f[1])
                q = e380.ini_qo(x)
                if q:
                    nuclei[q[0]].add(q[1])
                if len(x) >= 2 and classe(x[-1]):
                    tr_vc[x[:-1]].add(classe(x[-1]))
            ws, seps = righe[i]
            for j in range(len(ws) - 1):
                a, b = ws[j], ws[j + 1]
                if not a or not b or seps[j] != '.':
                    continue
                # parte A
                f = e380.fin_lr(a)
                if f and len(tr_lr.get(f[0], ())) == 1 and b in insieme and (b[0] in K or b[0] in A):
                    fa = next(iter(tr_lr[f[0]]))
                    cb = 'K' if b[0] in K else 'A'
                    evA.append(((fa == 'l' and cb == 'A') or (fa == 'r' and cb == 'K'), f[1] != fa))
                # parte B
                q = e380.ini_qo(b)
                ca = classe(a[-1]) if len(a) >= 2 else None
                if q and ca and len(nuclei.get(q[0], ())) == 1 and len(tr_vc.get(a[:-1], ())) == 1:
                    fb = next(iter(nuclei[q[0]]))
                    fa = next(iter(tr_vc[a[:-1]]))
                    evB.append(((fa == 'C' and fb == 'qo') or (fa == 'V' and fb == 'o'), ca != fa, q[1] != fb))
    nA, nB = sum(1 for e in evA if e[0]), sum(1 for e in evB if e[0])
    A_ = prova(evA, 1, rnd)
    if nA < 30:
        esA = 'non decidibile (meno di 30 conflitti)'
    elif A_['differenza'] > 0 and A_['p'] < 0.01:
        esA = 'lo scriba guarda avanti'
    elif A_['p'] > 0.1:
        esA = 'non guarda avanti'
    else:
        esA = 'incerto'
    Ba, Bb = prova(evB, 1, rnd), prova(evB, 2, rnd)
    if nB < 30:
        esB = 'non decidibile (meno di 30 conflitti)'
    elif Bb['p'] < 0.01 and Ba['p'] < 0.01:
        esB = 'tutte e due'
    elif Bb['p'] < 0.01:
        esB = 'si adatta la parola dopo'
    elif Ba['p'] < 0.01:
        esB = 'si adatta la parola prima'
    else:
        esB = 'non deciso'
    out = OrderedDict([('parte_A', OrderedDict([('coppie', len(evA)), ('conflitti', nA), ('cambia_a', A_), ('esito', esA)])),
                       ('parte_B', OrderedDict([('coppie', len(evB)), ('conflitti', nB), ('cambia_a', Ba), ('cambia_b', Bb), ('esito', esB)]))])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a02_chi_si_adatta_2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    f = lambda x: '%.2f' % x if x is not None else 'n.d.'
    md = ['# e3a02 — Chi si adatta a chi, con le fonti dalle 2 righe sopra', '', 'Preregistrazione: `preregistrazioni/e3a02.md`.', '',
          '| parte | coppie | conflitti | misura | nei conflitti | negli accordi | differenza | p |', '|---|---|---|---|---|---|---|---|',
          '| A (-l/-r) | %d | %d | cambia la finale di a | %s | %s | %+.3f | %.4f |' % (len(evA), nA, f(A_['quota_conflitti']), f(A_['quota_accordi']), A_['differenza'], A_['p']),
          '| B (qo-/o-) | %d | %d | cambia la finale di a | %s | %s | %+.3f | %.4f |' % (len(evB), nB, f(Ba['quota_conflitti']), f(Ba['quota_accordi']), Ba['differenza'], Ba['p']),
          '| B (qo-/o-) | | | cambia qo/o di b | %s | %s | %+.3f | %.4f |' % (f(Bb['quota_conflitti']), f(Bb['quota_accordi']), Bb['differenza'], Bb['p']),
          '', 'Esito A: **%s**. Esito B: **%s**.' % (esA, esB)]
    open(os.path.join(RISULTATI, 'e3a02_chi_si_adatta_2.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
