# -*- coding: utf-8 -*-
"""Esperimento e3a09: la -m di fine riga (al posto di -r/-l) dipende dal riempimento della riga e dalla fine del paragrafo?

Preregistrazione: preregistrazioni/e3a09.md. Scrive risultati/e3a09_m_margine.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 10000


def diff_pesata(ev):
    """ev: [(strato, etichetta, m)] -> media pesata sugli strati di P(m | etichetta) - P(m | non etichetta)."""
    per = defaultdict(list)
    for s, e, m in ev:
        per[s].append((e, m))
    num = den = 0.0
    for xs in per.values():
        a = [m for e, m in xs if e]
        b = [m for e, m in xs if not e]
        if a and b:
            num += len(xs) * (sum(a) / len(a) - sum(b) / len(b))
            den += len(xs)
    return num / den if den else 0.0


def prova(ev, rnd):
    d = diff_pesata(ev)
    per = defaultdict(list)
    for i, (s, _, _) in enumerate(ev):
        per[s].append(i)
    nul = []
    for _ in range(PERM):
        e2 = list(ev)
        for idx in per.values():
            et = [ev[i][1] for i in idx]
            rnd.shuffle(et)
            for i, e in zip(idx, et):
                e2[i] = (ev[i][0], e, ev[i][2])
        nul.append(diff_pesata(e2))
    p = sum(abs(x) >= abs(d) for x in nul) / PERM
    a = [m for _, e, m in ev if e]
    b = [m for _, e, m in ev if not e]
    return OrderedDict([('eventi', [len(a), len(b)]), ('P_m', [sum(a) / len(a) if a else None, sum(b) / len(b) if b else None]), ('differenza', d), ('p', p)])


def main():
    rnd = random.Random(3109)
    righe = [r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if [w for w in r.parole if trascrizione.pulita(w)]]
    info = []
    for k, r in enumerate(righe):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if not ws:
            continue
        ultima = r.fine_par or (k + 1 < len(righe) and (righe[k + 1].inizio_par or righe[k + 1].pagina != r.pagina))
        info.append((r.pagina, '%s-%s' % (r.sezione or '?', r.lingua or '?'), sum(len(w) for w in ws), ultima, ws[-1]))
    mediana = {}
    per_pag = defaultdict(list)
    for pag, st, n, ultima, w in info:
        if not ultima:
            per_pag[pag].append(n)
    for pag, xs in per_pag.items():
        mediana[pag] = statistics.median(xs)
    evA, evB = [], []
    piene = defaultdict(list)
    for pag, st, n, ultima, w in info:
        if len(w) < 2 or w[-1] not in ('m', 'r', 'l'):
            continue
        evB.append((st, ultima, w[-1] == 'm'))
        if not ultima and pag in mediana:
            piene[st].append((n / mediana[pag], w[-1] == 'm'))
    for st, xs in piene.items():
        xs.sort(key=lambda t: t[0])
        t = len(xs) // 3
        if t < 5:
            continue
        evA += [(st, False, m) for _, m in xs[:t]] + [(st, True, m) for _, m in xs[-t:]]
    A = prova(evA, rnd)
    B = prova(evB, rnd)
    esA = '-m più frequente nelle righe piene' if A['differenza'] > 0 and A['p'] < 0.01 else ('non dipende dal riempimento' if A['p'] > 0.1 else 'incerto')
    esB = '-m più rara a fine paragrafo (legata al margine)' if B['differenza'] < 0 and B['p'] < 0.01 else ('-m anche a fine paragrafo (segna la fine della riga)' if B['p'] > 0.1 else 'incerto')
    out = OrderedDict([('A_righe_piene', A), ('B_fine_paragrafo', B), ('esito_A', esA), ('esito_B', esB)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a09_m_margine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    f = lambda x: '%.3f' % x if x is not None else 'n.d.'
    md = ['# e3a09 — La -m di fine riga dipende dal margine o segna solo la fine della riga?', '', 'Preregistrazione: `preregistrazioni/e3a09.md`. Ultime parole della riga in -m/-r/-l; P(-m).', '',
          '| prova | eventi (sì / no) | P(-m) sì | P(-m) no | differenza pesata | p |', '|---|---|---|---|---|---|',
          '| A: terzo più pieno contro terzo meno pieno | %d / %d | %s | %s | %+.3f | %.4f |' % (A['eventi'][0], A['eventi'][1], f(A['P_m'][0]), f(A['P_m'][1]), A['differenza'], A['p']),
          '| B: ultima riga del paragrafo contro le altre | %d / %d | %s | %s | %+.3f | %.4f |' % (B['eventi'][0], B['eventi'][1], f(B['P_m'][0]), f(B['P_m'][1]), B['differenza'], B['p']),
          '', 'Esito A: **%s**. Esito B: **%s**.' % (esA, esB)]
    open(os.path.join(RISULTATI, 'e3a09_m_margine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
