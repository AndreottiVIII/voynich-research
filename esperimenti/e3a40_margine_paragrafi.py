# -*- coding: utf-8 -*-
"""Esperimento e3a40: inizi uguali (1) fra la prima riga di un paragrafo e la riga subito sopra, (2) fra le prime righe
di paragrafi consecutivi, nella stessa pagina.

Preregistrazione: preregistrazioni/e3a40.md. Scrive risultati/e3a40_margine_paragrafi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def inizio(r):
    if not r:
        return None
    w = r[0]
    return 'qo' if w[:2] == ('q', 'o') else w[0]


def main():
    rnd = random.Random(3140)
    pagine = []
    for pp in e341.pagine().values():
        pars = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pp]
        pars = [p for p in pars if p and p[0]]
        if len(pars) >= 2:
            pagine.append(pars)

    def q1(pagine_):
        s = t = 0
        for pars in pagine_:
            for a, b in zip(pars, pars[1:]):
                x, y = inizio(a[-1]), inizio(b[0])
                if x and y:
                    t += 1
                    s += x == y
        return s / t, t

    def q2(pagine_):
        s = t = 0
        for pars in pagine_:
            for a, b in zip(pars, pars[1:]):
                x, y = inizio(a[0]), inizio(b[0])
                if x and y:
                    t += 1
                    s += x == y
        return s / t, t

    ris = OrderedDict()
    # 1: prime righe rimescolate fra i paragrafi della pagina
    def mescola_prime(pagine_):
        out = []
        for pars in pagine_:
            prime = [p[0] for p in pars]
            rnd.shuffle(prime)
            out.append([[pr] + p[1:] for pr, p in zip(prime, pars)])
        return out
    for nome, f, mescola in (('1 prima riga contro la riga sopra', q1, mescola_prime), ('2 prime righe di paragrafi consecutivi', q2, lambda pg: [rnd.sample(p, len(p)) for p in pg])):
        vero, t = f(pagine)
        nul = [f(mescola(pagine))[0] for _ in range(1000)]
        m, sd = statistics.mean(nul), statistics.pstdev(nul)
        r = vero / m if m else None
        z = (vero - m) / sd if sd else 0.0
        es = 'evitato' if r is not None and r < 0.8 and z < -3 else ('ripetuto' if r is not None and r > 1.2 and z > 3 else 'indifferente')
        ris[nome] = OrderedDict([('coppie', t), ('osservata', vero), ('nullo', m), ('rapporto', r), ('z', z), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    inizi = Counter(inizio(p[0]) for pars in pagine for p in pars)
    out = OrderedDict([('pagine', len(pagine)), ('inizi_dei_paragrafi', inizi.most_common(8)), ('misure', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a40_margine_paragrafi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a40 — La regola del margine sinistro vale anche fra paragrafi?', '', 'Preregistrazione: `preregistrazioni/e3a40.md`. %d pagine con almeno 2 paragrafi; inizi dei paragrafi: %s.' % (
        len(pagine), ', '.join('%s %d' % kv for kv in inizi.most_common(8))), '',
          '| misura | coppie | osservata | nullo | rapporto | z | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.3f | %.2f | %.1f | %s |' % (k, x['coppie'], x['osservata'], x['nullo'], x['rapporto'], x['z'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a40_margine_paragrafi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
