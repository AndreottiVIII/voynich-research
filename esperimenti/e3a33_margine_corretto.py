# -*- coding: utf-8 -*-
"""Esperimento e3a33: legame verticale sul margine sinistro con il nullo corretto (ordine delle righe rimescolato dentro
il paragrafo, dalla seconda riga in poi). (1) per ogni inizio di riga, ZL; (2) qo-/o- come l'e3a26 in ZL, A, B, IT.

Preregistrazione: preregistrazioni/e3a33.md. Scrive risultati/e3a33_margine_corretto.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e3a27_margine_robustezza as e3a27

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 10000


def inizio(w):
    return 'qo' if w[:2] == ('q', 'o') else w[0]


def righe_utili(pars):
    """Per ogni paragrafo, le righe dalla seconda in poi come (inizio, esito qo/o-gallows o None)."""
    out = []
    for rr in pars:
        xs = []
        for r in rr[1:]:
            if not r:
                continue
            q = e380.ini_qo(r[0])
            xs.append((inizio(r[0]), (q[1] == 'qo') if q else None))
        if len(xs) >= 2:
            out.append(xs)
    return out


def statistiche(pars, segni):
    N = 0
    nc, hc, th = Counter(), Counter(), Counter()
    qa = [0, 0]   # (eventi, qo) con sopra qo
    qb = [0, 0]   # senza
    for xs in pars:
        for (a, _), (b, qb_) in zip(xs, xs[1:]):
            N += 1
            nc[a] += 1
            th[b] += 1
            if a == b:
                hc[a] += 1
            if qb_ is not None:
                t = qa if a == 'qo' else qb
                t[0] += 1
                t[1] += qb_
    d = {}
    for s in segni:
        if nc[s] and N - nc[s]:
            d[s] = hc[s] / nc[s] - (th[s] - hc[s]) / (N - nc[s])
    dq = (qa[1] / qa[0] - qb[1] / qb[0]) if qa[0] and qb[0] else None
    return d, dq, (qa[0], qb[0])


def prova(pars, segni, rnd):
    d, dq, ev = statistiche(pars, segni)
    nul_d, nul_q = {s: [] for s in segni}, []
    for _ in range(PERM):
        dn, dqn, _ = statistiche([rnd.sample(xs, len(xs)) for xs in pars], segni)
        for s in segni:
            nul_d[s].append(dn.get(s, 0.0))
        if dqn is not None:
            nul_q.append(dqn)
    z = lambda v, xs: (v - statistics.mean(xs)) / statistics.pstdev(xs) if statistics.pstdev(xs) else 0.0
    per_s = OrderedDict((s, OrderedDict([('delta', d[s]), ('nullo', statistics.mean(nul_d[s])), ('z', z(d[s], nul_d[s]))])) for s in segni if s in d)
    q = OrderedDict([('eventi', list(ev)), ('delta', dq), ('nullo', statistics.mean(nul_q)), ('z', z(dq, nul_q))]) if dq is not None else None
    return per_s, q


def main():
    rnd = random.Random(3133)
    zl = righe_utili(e3a27.paragrafi('ZL'))
    conta = Counter(a for xs in zl for (a, _) in xs[:-1])
    segni = [s for s, n in conta.most_common() if n >= 30]
    per_s, q_zl = prova(zl, segni, rnd)
    for s, x in per_s.items():
        x['righe_sopra'] = conta[s]
        x['esito'] = 'evitato' if x['delta'] < 0 and x['z'] < -3.3 else ('ripetuto' if x['delta'] > 0 and x['z'] > 3.3 else '—')
        print(s, json.dumps(x), flush=True)
    evitati = [s for s, x in per_s.items() if x['esito'] == 'evitato']
    ripetuti = [s for s, x in per_s.items() if x['esito'] == 'ripetuto']
    if evitati == ['qo']:
        es1 = 'solo qo- evitato'
    elif len(evitati) >= 3:
        es1 = 'il margine evita in generale gli inizi ripetuti'
    else:
        es1 = 'evitati: %s; ripetuti: %s' % (', '.join(evitati) or 'nessuno', ', '.join(ripetuti) or 'nessuno')
    qo = OrderedDict([('ZL', q_zl)])
    for nome, pars in (('ZL, lingua A', e3a27.paragrafi('ZL', 'A')), ('ZL, lingua B', e3a27.paragrafi('ZL', 'B')), ('IT (Takahashi)', e3a27.paragrafi('IT'))):
        qo[nome] = prova(righe_utili(pars), [], rnd)[1]
    for k, x in qo.items():
        x['esito'] = 'regge' if x['delta'] < 0 and x['z'] < -3 else ('non regge' if x['z'] > -2 else 'incerto')
        print(k, json.dumps(x), flush=True)
    out = OrderedDict([('per_inizio', per_s), ('esito_1', es1), ('qo', qo)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a33_margine_corretto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a33 — Il margine sinistro con il nullo corretto', '', 'Preregistrazione: `preregistrazioni/e3a33.md`. Nullo: ordine delle righe (dalla seconda) rimescolato nel paragrafo.', '',
          '## 1. Per ogni inizio (ZL)', '', '| inizio | righe sopra | Δ | nullo | z | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %+.3f | %+.3f | %.1f | %s |' % (s, x['righe_sopra'], x['delta'], x['nullo'], x['z'], x['esito']) for s, x in per_s.items()]
    md += ['', 'Esito 1: **%s**.' % es1, '', '## 2. qo-/o- a inizio riga dopo una riga che comincia con qo-', '',
           '| prova | eventi (sopra qo / no) | Δ P(qo) | nullo | z | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %d / %d | %+.3f | %+.3f | %.1f | %s |' % (k, x['eventi'][0], x['eventi'][1], x['delta'], x['nullo'], x['z'], x['esito']) for k, x in qo.items()]
    open(os.path.join(RISULTATI, 'e3a33_margine_corretto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
