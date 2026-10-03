# -*- coding: utf-8 -*-
"""Esperimento e3a06: la giuntura a capo nella sezione "solo testo" con p esatto e taratura su insiemi di pari dimensione
presi dalle altre sezioni.

Preregistrazione: preregistrazioni/e3a06.md. Scrive risultati/e3a06_solo_testo.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e377_giuntura_gibberish as e377
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')


def E_esatto(per_pag, rnd, perm):
    vero = e377.mi(Counter(x for xs in per_pag.values() for x in xs))
    nul = []
    for _ in range(perm):
        c = Counter()
        for xs in per_pag.values():
            dx = [b for _, b in xs]
            rnd.shuffle(dx)
            c.update((a, b) for (a, _), b in zip(xs, dx))
        nul.append(e377.mi(c))
    return vero - statistics.mean(nul), sum(x >= vero for x in nul) / perm


def main():
    rnd = random.Random(3106)
    rr = e386.righe()
    capo = defaultdict(lambda: defaultdict(list))
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        if k + 1 < len(rr) and rr[k + 1][1] == pag and rr[k + 1][2] == npar and ws[-1] and rr[k + 1][3][0]:
            capo[st.split('-')[0] == 'T'][pag].append((ws[-1][-1], rr[k + 1][3][0][0]))
    T = capo[True]
    nT = sum(len(x) for x in T.values())
    E_T, p_T = E_esatto(T, rnd, 10000)
    altre = list(capo[False].items())
    tar = []
    for _ in range(2000):
        rnd.shuffle(altre)
        camp, n = {}, 0
        for pg, xs in altre:
            if n >= nT:
                break
            camp[pg] = xs
            n += len(xs)
        tar.append(E_esatto(camp, rnd, 200)[0])
    q = sum(x >= E_T for x in tar) / len(tar)
    if p_T < 0.01 and q < 0.01:
        esito = 'nel solo testo la giuntura passa l\'a capo'
    elif p_T > 0.05 or q > 0.05:
        esito = 'era rumore'
    else:
        esito = 'incerto'
    out = OrderedDict([('coppie_a_capo_solo_testo', nT), ('E', E_T), ('p_esatto', p_T), ('taratura_quota_E_maggiore', q),
                       ('taratura_E', [min(tar), statistics.median(tar), max(tar)]), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a06_solo_testo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a06 — Nel "solo testo" la giuntura passa davvero l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3a06.md`.', '',
          'Coppie a capo nel solo testo: %d. E %.4f, p esatto %.4f. Taratura (2.000 insiemi di pari dimensione dalle altre sezioni): E da %.4f a %.4f (mediana %.4f); quota con E ≥ %.4f: %.4f.' % (
              nT, E_T, p_T, min(tar), max(tar), statistics.median(tar), E_T, q), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a06_solo_testo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
