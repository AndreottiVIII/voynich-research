# -*- coding: utf-8 -*-
"""Esperimento 369: per gli "errori" (parole con 1-5 occorrenze a una modifica da una parola frequente) la madre frequente
sta nelle 2 righe sopra dello stesso paragrafo piu' del caso, e piu' che per le parole frequenti con una sorella?

Preregistrazione: preregistrazioni/e369.md. Scrive risultati/e369_errori_copia.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(369)
    pars = [p for pp in e341.pagine().values() for p in pp]
    freq = Counter(w for p in pars for r in p for w in r)
    sim = e350.simili_globali(set(freq))
    madri = {}
    for w, n in freq.items():
        vicine = {v for v in sim[w] if v != w and freq[v] >= 20}
        if vicine:
            if n <= 5:
                madri[w] = ('errore', vicine)
            elif n >= 20:
                madri[w] = ('confronto', vicine)
    voci = []    # (paragrafo, riga, parola, gruppo, madri)
    for k, p in enumerate(pars):
        for i in range(2, len(p)):
            for w in p[i]:
                if w in madri:
                    voci.append((k, i, w, madri[w][0], madri[w][1]))
    trova = lambda ms, righe: any(x in ms for r in righe for x in r)
    vero = {g: [] for g in ('errore', 'confronto')}
    for k, i, w, g, ms in voci:
        vero[g].append(trova(ms, [pars[k][i - 1], pars[k][i - 2]]))
    nul = {g: [] for g in vero}
    acc = [0.0] * len(voci)
    for _ in range(200):
        tmp = {g: [] for g in vero}
        for t, (k, i, w, g, ms) in enumerate(voci):
            altre = [j for j in range(len(pars[k])) if j != i]
            a, b = rnd.sample(altre, 2)
            x = trova(ms, [pars[k][a], pars[k][b]])
            tmp[g].append(x)
            acc[t] += x
        for g in vero:
            nul[g].append(statistics.mean(tmp[g]))
    out = OrderedDict()
    for g in ('errore', 'confronto'):
        v = statistics.mean(vero[g])
        m, sd = statistics.mean(nul[g]), statistics.pstdev(nul[g])
        out[g] = OrderedDict([('occorrenze', len(vero[g])), ('madre_nelle_2_righe_sopra', v), ('nullo', m), ('eccesso', v - m), ('z', (v - m) / sd if sd else 0.0)])
    # differenza degli eccessi con bootstrap sulle occorrenze (eccesso individuale = vero - media nulla della voce)
    ecc = {g: [] for g in vero}
    idx = {'errore': 0, 'confronto': 0}
    for t, (k, i, w, g, ms) in enumerate(voci):
        ecc[g].append(vero[g][idx[g]] - acc[t] / 200)
        idx[g] += 1
    boot = []
    for _ in range(1000):
        a = [ecc['errore'][rnd.randrange(len(ecc['errore']))] for _ in ecc['errore']]
        b = [ecc['confronto'][rnd.randrange(len(ecc['confronto']))] for _ in ecc['confronto']]
        boot.append(statistics.mean(a) - statistics.mean(b))
    d = statistics.mean(ecc['errore']) - statistics.mean(ecc['confronto'])
    zd = d / statistics.pstdev(boot) if statistics.pstdev(boot) else 0.0
    ze = out['errore']['z']
    esito = 'errori di copiatura' if (ze > 3 and zd > 2) else ('errori spontanei' if ze < 2 else 'incerto')
    res = OrderedDict([('gruppi', out), ('differenza_eccessi', d), ('z_differenza', zd), ('esito', esito)])
    print(json.dumps(res, ensure_ascii=False, default=float), flush=True)
    json.dump(res, open(os.path.join(RISULTATI, 'e369_errori_copia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e369 — Gli "errori" sono errori di copiatura dalla riga sopra?', '', 'Preregistrazione: `preregistrazioni/e369.md`.', '',
          '| gruppo | occorrenze | madre (o sorella) nelle 2 righe sopra | nullo (2 righe a caso del paragrafo) | eccesso | z |', '|---|---|---|---|---|---|']
    for g, v in out.items():
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %.1f |' % ('errori (1–5 occorrenze)' if g == 'errore' else 'parole frequenti con una sorella', v['occorrenze'],
                                                              v['madre_nelle_2_righe_sopra'], v['nullo'], v['eccesso'], v['z']))
    md += ['', 'Differenza degli eccessi (errori − confronto): %+.4f, z %.1f. Esito: **%s**.' % (d, zd, esito)]
    open(os.path.join(RISULTATI, 'e369_errori_copia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
