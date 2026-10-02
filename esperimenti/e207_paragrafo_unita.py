# -*- coding: utf-8 -*-
"""Esperimento 207: somiglianza di vocabolario fra righe consecutive dello stesso paragrafo e a cavallo di un inizio
di paragrafo; Voynich e Macer floridus.

Preregistrazione: preregistrazioni/e207.md. Scrive risultati/e207_paragrafo_unita.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e99_macer as e99
import e148_bifogli as e148
import e154b_ordine_normalizzato as e154b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 207, 2000


def coppie(righe):
    """righe: (pagina, inizio paragrafo, Counter). -> [(pagina, a cavallo, somiglianza)]"""
    out = []
    for (p1, i1, c1), (p2, i2, c2) in zip(righe, righe[1:]):
        if p1 == p2 and c1 and c2:
            out.append((p1, i2, e148.coseno(c1, c2)))
    return out


def prova(cc, rnd):
    def stat(et):
        a = [s for (_, _, s), e in zip(cc, et) if not e]
        b = [s for (_, _, s), e in zip(cc, et) if e]
        return statistics.mean(a) - statistics.mean(b)
    et = [e for _, e, _ in cc]
    vero = stat(et)
    per = defaultdict(list)
    for i, (p, _, _) in enumerate(cc):
        per[p].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        x = et[:]
        for idx in per.values():
            v = [x[i] for i in idx]
            rnd.shuffle(v)
            for i, y in zip(idx, v):
                x[i] = y
        nulli.append(stat(x))
    p = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    return OrderedDict([('coppie', len(cc)), ('a_cavallo', sum(et)), ('differenza', vero), ('nullo', statistics.mean(nulli)), ('p', p)])


def main():
    rnd = random.Random(SEME)
    voy = [(r.pagina, bool(r.inizio_par), Counter(e154b.normalizza(w) for w in r.parole if trascrizione.pulita(w)))
           for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    versi = [(k, j == 0, Counter(ps)) for k, c in enumerate(e99.capitoli()) for j, ps in enumerate(c)]
    macer = [(i // 30, ini, c) for i, (_, ini, c) in enumerate(versi)]
    ris = OrderedDict()
    for nome, rr in (('Voynich', voy), ('Macer floridus', macer)):
        ris[nome] = prova(coppie(rr), rnd)
        r = ris[nome]
        print('%-16s coppie %d (a cavallo %d) | stesso − a cavallo %.4f (nullo %.4f) p %.4f' % (nome, r['coppie'], r['a_cavallo'], r['differenza'], r['nullo'], r['p']), flush=True)
    valido = ris['Macer floridus']['p'] < 0.01
    v = ris['Voynich']
    esito = 'test non valido' if not valido else ('il paragrafo è un\'unità di contenuto' if v['differenza'] > 0 and v['p'] < 0.01 else ('solo grafica' if v['p'] > 0.05 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    print(valido, esito)
    json.dump(ris, open(os.path.join(RISULTATI, 'e207_paragrafo_unita.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e207 — Il paragrafo è un\'unità di contenuto?', '', 'Somiglianza di vocabolario fra righe consecutive: stesso paragrafo meno a cavallo di un inizio di paragrafo. '
          'Preregistrazione: `preregistrazioni/e207.md`.', '', '| testo | coppie | a cavallo | differenza | nullo | p |', '|---|---|---|---|---|---|']
    for n in ('Voynich', 'Macer floridus'):
        r = ris[n]
        md.append('| %s | %d | %d | %.4f | %.4f | %.4f |' % (n, r['coppie'], r['a_cavallo'], r['differenza'], r['nullo'], r['p']))
    md += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e207_paragrafo_unita.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
