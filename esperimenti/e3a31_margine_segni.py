# -*- coding: utf-8 -*-
"""Esperimento e3a31: per ogni inizio di riga (primo segno; qo per q), la riga lo evita o lo ripete se la riga sopra
comincia allo stesso modo? Righe dalla seconda del paragrafo in poi.

Preregistrazione: preregistrazioni/e3a31.md. Scrive risultati/e3a31_margine_segni.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 10000


def inizio(w):
    return 'qo' if w[:2] == ('q', 'o') else w[0]


def main():
    rnd = random.Random(3131)
    coppie = []    # (paragrafo, inizio sopra, inizio sotto)
    k = 0
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            k += 1
            for i in range(2, len(rr)):
                if rr[i] and rr[i - 1]:
                    coppie.append((k, inizio(rr[i - 1][0]), inizio(rr[i][0])))
    conta = Counter(a for _, a, _ in coppie)
    segni = [s for s, n in conta.items() if n >= 30]
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(coppie):
        per[p].append(i)
    ris = OrderedDict()
    for s in sorted(segni, key=lambda s: -conta[s]):
        def delta(cond):
            a = [b == s for c, (_, _, b) in zip(cond, coppie) if c]
            n = [b == s for c, (_, _, b) in zip(cond, coppie) if not c]
            return sum(a) / len(a) - sum(n) / len(n)
        cond = [a == s for _, a, _ in coppie]
        d = delta(cond)
        nul = []
        for _ in range(PERM):
            c2 = list(cond)
            for idx in per.values():
                vals = [cond[i] for i in idx]
                rnd.shuffle(vals)
                for i, v in zip(idx, vals):
                    c2[i] = v
            nul.append(delta(c2))
        m, sd = statistics.mean(nul), statistics.pstdev(nul)
        z = (d - m) / sd if sd else 0.0
        ris[s] = OrderedDict([('righe_sopra_con_s', conta[s]), ('delta', d), ('z', z),
                              ('esito', 'evitato' if d < 0 and z < -3.3 else ('ripetuto' if d > 0 and z > 3.3 else '—'))])
        print(s, json.dumps(ris[s]), flush=True)
    evitati = [s for s, x in ris.items() if x['esito'] == 'evitato']
    ripetuti = [s for s, x in ris.items() if x['esito'] == 'ripetuto']
    if evitati == ['qo']:
        esito = 'solo qo- è evitato'
    elif len(evitati) >= 3:
        esito = 'il margine evita in generale gli inizi ripetuti'
    else:
        esito = 'evitati: %s; ripetuti: %s' % (', '.join(evitati) or 'nessuno', ', '.join(ripetuti) or 'nessuno')
    out = OrderedDict([('coppie', len(coppie)), ('inizi', ris), ('evitati', evitati), ('ripetuti', ripetuti), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a31_margine_segni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a31 — Il margine sinistro evita solo qo- o ogni inizio ripetuto?', '', 'Preregistrazione: `preregistrazioni/e3a31.md`. %d coppie di righe consecutive (dalla seconda del paragrafo).' % len(coppie), '',
          '| inizio | righe sopra con l\'inizio | Δ | z | esito |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.3f | %.1f | %s |' % (s, x['righe_sopra_con_s'], x['delta'], x['z'], x['esito']) for s, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a31_margine_segni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
