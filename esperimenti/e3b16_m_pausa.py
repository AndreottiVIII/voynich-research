# -*- coding: utf-8 -*-
"""Esperimento e3b16: distribuzione del primo segno dopo una parola in -m in mezzo alla riga, confrontata con quella a
inizio riga e con quelle dopo le altre finali (divergenza di Jensen-Shannon).

Preregistrazione: preregistrazioni/e3b16.md. Scrive risultati/e3b16_m_pausa.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
FINALI = ('d', 'l', 'n', 'o', 'r', 's', 'y')
BOOT = 1000


def jsd(a, b):
    na, nb = sum(a.values()), sum(b.values())
    k = set(a) | set(b)
    pa = {x: a.get(x, 0) / na for x in k}
    pb = {x: b.get(x, 0) / nb for x in k}
    m = {x: (pa[x] + pb[x]) / 2 for x in k}
    kl = lambda p: sum(p[x] * math.log2(p[x] / m[x]) for x in k if p[x] > 0)
    return (kl(pa) + kl(pb)) / 2


def main():
    rnd = random.Random(3216)
    dopo = {f: Counter() for f in FINALI}
    dopo_m = []
    inizio = Counter()
    for pars in e341.pagine().values():
        for par in pars:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            rr = [r for r in rr if r]
            for j, r in enumerate(rr):
                if j >= 1:
                    inizio[r[0][0]] += 1
                for a in range(1, len(r) - 2):
                    w, v = r[a], r[a + 1]
                    if w[-1] == 'm':
                        dopo_m.append(v[0])
                    elif w[-1] in dopo:
                        dopo[w[-1]][v[0]] += 1
    n_m = len(dopo_m)
    if n_m < 100:
        esito = 'dati insufficienti'
        out = OrderedDict([('parole_dopo_m', n_m), ('esito', esito)])
    else:
        cm = Counter(dopo_m)
        dist = OrderedDict([('inizio riga', jsd(cm, inizio))] + [('dopo -' + f, jsd(cm, dopo[f])) for f in FINALI])
        piu_vicina = min(dist, key=dist.get)
        min_fin = min(v for k, v in dist.items() if k != 'inizio riga')
        diff = dist['inizio riga'] - min_fin
        boot = []
        for _ in range(BOOT):
            cb = Counter(rnd.choices(dopo_m, k=n_m))
            dd = [jsd(cb, dopo[f]) for f in FINALI]
            boot.append(jsd(cb, inizio) - min(dd))
        boot.sort()
        ic = [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]]
        if piu_vicina == 'inizio riga' and ic[1] < 0:
            esito = 'dopo -m si riparte come a inizio riga'
        elif piu_vicina != 'inizio riga' and ic[0] > 0:
            esito = 'dopo -m è come dopo un\'altra finale'
        else:
            esito = 'incerto'
        prime = lambda c: ', '.join('%s %.0f%%' % (k, 100 * v / sum(c.values())) for k, v in c.most_common(6))
        out = OrderedDict([('parole_dopo_m', n_m), ('divergenze', dist), ('piu_vicina', piu_vicina), ('differenza', diff), ('IC95', ic),
                           ('primi_segni', OrderedDict([('dopo -m', prime(cm)), ('inizio riga', prime(inizio))] + [('dopo -' + f, prime(dopo[f])) for f in FINALI])),
                           ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b16_m_pausa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b16 — Dopo una -m in mezzo alla riga si riparte come a inizio riga?', '', 'Preregistrazione: `preregistrazioni/e3b16.md`.', '', 'Parole dopo -m in mezzo alla riga: %d.' % n_m, '']
    if 'divergenze' in out:
        md += ['| confronto | divergenza JS da "dopo -m" | primi segni più frequenti |', '|---|---|---|']
        md += ['| %s | %.4f | %s |' % (k, v, out['primi_segni'][k]) for k, v in out['divergenze'].items()]
        md += ['', 'Dopo -m: %s.' % out['primi_segni']['dopo -m'], '', 'Più vicina: **%s**. Differenza (inizio riga − finale più vicina) %+.4f, IC 95%% %+.4f – %+.4f.' % (out['piu_vicina'], out['differenza'], out['IC95'][0], out['IC95'][1])]
    md += ['', 'Esito: **%s**.' % out['esito']]
    open(os.path.join(RISULTATI, 'e3b16_m_pausa.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
