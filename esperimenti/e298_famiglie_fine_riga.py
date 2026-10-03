# -*- coding: utf-8 -*-
"""Esperimento 298 (con l'e299): famiglie di parole nella pagina (componenti dei tipi legati da una modifica) e lunghezza
relativa delle righe che finiscono in m o g, nel Voynich e nel generatore dell'e288 (semi 7-9).

Preregistrazione: preregistrazioni/e298.md. Scrive risultati/e298_famiglie_fine_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure, trascrizione
import e296_rare_errori as e296

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEMI, MIN_PAROLE, SEME = (7, 8, 9), 40, 299


def famiglie(righe):
    per = OrderedDict()
    for pag, _, ps in righe:
        per.setdefault(pag, []).extend(ps)
    mis = defaultdict(list)
    for pag, ws in per.items():
        if len(ws) < MIN_PAROLE:
            continue
        cnt = Counter(ws)
        tipi = list(cnt)
        u = {w: tuple(D(w)) for w in tipi}
        padre = {w: w for w in tipi}

        def trova(x):
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x
        per_l = defaultdict(list)
        for w in tipi:
            per_l[len(u[w])].append(w)
        for w in tipi:
            for L in (len(u[w]), len(u[w]) + 1):
                for v in per_l.get(L, ()):
                    if v != w and e296.dist1(u[w], u[v]):
                        padre[trova(w)] = trova(v)
        comp = defaultdict(list)
        for w in tipi:
            comp[trova(w)].append(w)
        occ = {r: sum(cnt[w] for w in ws_) for r, ws_ in comp.items()}
        mis['tipi'].append(len(tipi))
        mis['famiglie'].append(len(comp))
        mis['tipi per famiglia'].append(len(tipi) / len(comp))
        mis['occorrenze in famiglie di 2+ tipi'].append(sum(o for r, o in occ.items() if len(comp[r]) >= 2) / len(ws))
        mis['quota della famiglia più grande'].append(max(occ.values()) / len(ws))
    return OrderedDict((k, statistics.mean(v)) for k, v in mis.items())


def fine_riga(righe, rnd):
    per = defaultdict(list)
    for i, (pag, ini, ps) in enumerate(righe):
        fine_par = i + 1 >= len(righe) or righe[i + 1][1] or righe[i + 1][0] != pag
        if ps and not fine_par:
            per[pag].append((sum(len(D(w)) for w in ps), D(ps[-1])[-1] in ('m', 'g')))
    dati = []
    for pag, xs in per.items():
        if len(xs) >= 4:
            media = statistics.mean(L for L, _ in xs)
            dati.append([(L / media, f) for L, f in xs])

    def diff(gruppi):
        a = [x for g in gruppi for x, f in g if f]
        b = [x for g in gruppi for x, f in g if not f]
        return statistics.mean(a) - statistics.mean(b) if a and b else 0.0
    vero = diff(dati)
    nulli = []
    for _ in range(1000):
        mes = []
        for g in dati:
            fl = [f for _, f in g]
            rnd.shuffle(fl)
            mes.append([(x, f) for (x, _), f in zip(g, fl)])
        nulli.append(diff(mes))
    sd = statistics.pstdev(nulli)
    return OrderedDict([('righe', sum(len(g) for g in dati)), ('quota_m_g', sum(f for g in dati for _, f in g) / sum(len(g) for g in dati)),
                        ('differenza_lunghezza_relativa', vero), ('z', (vero - statistics.mean(nulli)) / sd if sd else None)])


def main():
    rnd = random.Random(SEME)
    voy = [(r.pagina, bool(r.inizio_par), [w for w in r.parole if trascrizione.pulita(w)]) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    testi = OrderedDict([('Voynich', voy)])
    import corpo2
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    c, c2, freq, _, _, _ = e251.contesto()
    for s in SEMI:
        e233.SIGMA_POST = 0.04
        rr = e236.dopo(corpo2.genera_v2(c2, dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), s), freq, 100 + s)
        testi['generatore e288, seme %d' % s] = [(p, ini, [w for w in ps if trascrizione.pulita(w)]) for p, ini, ps in rr]
    ris = OrderedDict((n, OrderedDict([('famiglie', famiglie(t)), ('fine_riga', fine_riga(t, rnd))])) for n, t in testi.items())
    for n, r in ris.items():
        print('%-26s famiglie %s | fine riga %s' % (n, {k: round(v, 3) for k, v in r['famiglie'].items()}, {k: round(v, 3) if isinstance(v, float) else v for k, v in r['fine_riga'].items()}), flush=True)
    gen = [n for n in ris if n != 'Voynich']
    diverse = OrderedDict()
    for k, v in ris['Voynich']['famiglie'].items():
        g = [ris[n]['famiglie'][k] for n in gen]
        diverse[k] = abs(v - statistics.mean(g)) / statistics.mean(g) > 0.10 and not (min(g) <= v <= max(g))
    zv = ris['Voynich']['fine_riga']['z'] or 0
    zg = [ris[n]['fine_riga']['z'] or 0 for n in gen]
    e299 = 'giustificazione' if abs(zv) > 3 and all(abs(z) < 2 for z in zg) else ('nessuna' if abs(zv) < 2 else 'incerto')
    json.dump(OrderedDict([('risultati', ris), ('e298_misure_diverse', diverse), ('e299_esito', e299)]), open(os.path.join(RISULTATI, 'e298_famiglie_fine_riga.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)
    md = ['# e298 ed e299 — Famiglie di parole nella pagina; fine riga e lunghezza della riga', '', 'Preregistrazione: `preregistrazioni/e298.md`.', '', '## e298', '',
          '| testo | ' + ' | '.join(ris['Voynich']['famiglie']) + ' |', '|---|' + '---|' * len(ris['Voynich']['famiglie'])]
    for n, r in ris.items():
        md.append('| %s | %s |' % (n, ' | '.join('%.3f' % v for v in r['famiglie'].values())))
    md += ['', 'Misure diverse dal generatore (oltre il 10%% e fuori dai tre semi): %s.' % (', '.join(k for k, v in diverse.items() if v) or 'nessuna'), '', '## e299', '',
           '| testo | righe | quota in m/g | differenza di lunghezza relativa (m/g − altre) | z |', '|---|---|---|---|---|']
    for n, r in ris.items():
        f = r['fine_riga']
        md.append('| %s | %d | %.3f | %+.4f | %.1f |' % (n, f['righe'], f['quota_m_g'], f['differenza_lunghezza_relativa'], f['z'] or 0))
    md += ['', 'Esito e299: **%s**.' % e299]
    open(os.path.join(RISULTATI, 'e298_famiglie_fine_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(diverse, e299)


if __name__ == '__main__':
    main()
