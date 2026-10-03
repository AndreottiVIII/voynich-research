# -*- coding: utf-8 -*-
"""Esperimento e3a25: le righe consecutive (senza la prima riga del paragrafo) cominciano con gli stessi 2 segni (o lo
stesso primo segno) meno del caso? Confronto con i testi sensati; inizi piu' evitati nel Voynich.

Preregistrazione: preregistrazioni/e3a25.md. Scrive risultati/e3a25_inizi_evitati.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def inizi(par, k):
    """Inizi (primi k segni della prima parola) delle righe con almeno 3 parole; None per le altre."""
    return [r[0][:k] if len(r) >= 3 and len(r[0]) >= 2 else None for r in par]


def quota(paragrafi):
    si = tot = 0
    for ini in paragrafi:
        for a, b in zip(ini, ini[1:]):
            if a is None or b is None:
                continue
            tot += 1
            si += a == b
    return si, tot


def prova(paragrafi, rnd, perm=1000):
    s, t = quota(paragrafi)
    nul = [quota([rnd.sample(p, len(p)) for p in paragrafi])[0] / t for _ in range(perm)]
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('coppie', t), ('osservata', s / t), ('nullo', m), ('rapporto', (s / t) / m if m else None), ('z', (s / t - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3125)
    voy = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par][1:]
            if len(rr) >= 3:
                voy.append(rr)
    ris = OrderedDict()
    ris['Voynich, primi 2 segni'] = prova([inizi(p, 2) for p in voy], rnd)
    ris['Voynich, primo segno'] = prova([inizi(p, 1) for p in voy], rnd)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    # inizi piu' evitati
    oss, att = Counter(), Counter()
    pars2 = [inizi(p, 2) for p in voy]
    for ini in pars2:
        for a, b in zip(ini, ini[1:]):
            if a is not None and b is not None and a == b:
                oss[a] += 1
    for _ in range(200):
        for ini in pars2:
            s = rnd.sample(ini, len(ini))
            for a, b in zip(s, s[1:]):
                if a is not None and b is not None and a == b:
                    att[a] += 1 / 200
    evitati = sorted(((oss[k] - att[k], k) for k in att if att[k] >= 5), key=lambda t: t[0])[:10]
    ris['inizi_piu_evitati'] = [['.'.join(k), oss[k], round(att[k], 1)] for _, k in evitati]
    # testi sensati
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        blocchi = [inizi(righe[i:i + 25][1:], 2) for i in range(0, len(righe), 25)]
        x = prova(blocchi, rnd, 200)
        sens[k.replace('.txt', '')] = x
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: kv[1]['rapporto'] or 0))
    V = ris['Voynich, primi 2 segni']
    grandi = [x['rapporto'] for x in sens.values() if x['coppie'] >= 300 and x['rapporto'] is not None]
    if V['rapporto'] < 0.8 and V['z'] < -3 and V['rapporto'] < min(grandi):
        esito = 'le righe consecutive evitano di cominciare allo stesso modo'
    elif abs(V['z']) < 2:
        esito = 'era la prima riga del paragrafo'
    else:
        esito = 'incerto'
    ris['rapporto_testi_sensati_grandi'] = [min(grandi), statistics.median(grandi), max(grandi)]
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a25_inizi_evitati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a25 — Le righe consecutive evitano di cominciare allo stesso modo?', '', 'Preregistrazione: `preregistrazioni/e3a25.md`. Senza le prime righe dei paragrafi.', '',
          '| confronto | coppie | osservata | nullo | rapporto | z |', '|---|---|---|---|---|---|']
    for k in ('Voynich, primi 2 segni', 'Voynich, primo segno'):
        x = ris[k]
        md.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (k, x['coppie'], x['osservata'], x['nullo'], x['rapporto'], x['z']))
    g = ris['rapporto_testi_sensati_grandi']
    md += ['', 'Testi sensati con almeno 300 coppie, rapporto (primi 2 segni): minimo %.2f, mediana %.2f, massimo %.2f.' % tuple(g), '',
           'Inizi più evitati nel Voynich (osservate, attese): ' + '; '.join('%s %d contro %.1f' % tuple(x) for x in ris['inizi_piu_evitati']) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a25_inizi_evitati.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
