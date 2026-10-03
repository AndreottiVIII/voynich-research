# -*- coding: utf-8 -*-
"""Esperimento 383: la giuntura (e377) in tre versioni: tutte le coppie, senza le coppie la cui unione e' una parola,
solo coppie di parole lunghe (3+ segni). Voynich, testi sensati (parole intere), gibberish umano.

Preregistrazione: preregistrazioni/e383.md. Scrive risultati/e383_giuntura_lunghe.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e375_coppie as e375
import e377_giuntura_gibberish as e377
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')


def tre(righe, rnd, perm):
    freq = Counter(w for r in righe for w in r)
    lessico = {w for w, n in freq.items() if n >= 2}
    filtri = [lambda a, b: True, lambda a, b: (a + b) not in lessico, lambda a, b: len(a) >= 3 and len(b) >= 3]

    def conta(rr):
        cs = [Counter() for _ in filtri]
        for r in rr:
            for a, b in zip(r, r[1:]):
                for c, f in zip(cs, filtri):
                    if f(a, b):
                        c[(a[-1], b[0])] += 1
        return cs
    righe = [r for r in righe if len(r) >= 2]
    vero = [e377.mi(c) for c in conta(righe)]
    nul = [[e377.mi(c) for c in conta([rnd.sample(r, len(r)) for r in righe])] for _ in range(perm)]
    out = []
    for k in range(3):
        xs = [x[k] for x in nul]
        m, sd = statistics.mean(xs), statistics.pstdev(xs)
        out.append(OrderedDict([('E', vero[k] - m), ('z', (vero[k] - m) / sd if sd else 0.0)]))
    return out


def main():
    rnd = random.Random(383)
    voy = [r for p in e375.voynich() for r in p]
    ris = OrderedDict()
    ris['Voynich'] = tre(voy, rnd, 1000)
    print('Voynich', json.dumps(ris['Voynich'], default=float), flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt'):
                gib += [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(n).decode('utf-8', errors='ignore').splitlines()) if ws]
    ris['gibberish umano'] = tre(gib, rnd, 100)
    print('gibberish', json.dumps(ris['gibberish umano'], default=float), flush=True)
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        ris[k.replace('.txt', '')] = tre(righe, rnd, 100)
        print(k, json.dumps(ris[k.replace('.txt', '')], default=float), flush=True)
    V = ris['Voynich']
    q2, q3 = V[1]['E'] / V[0]['E'], V[2]['E'] / V[0]['E']
    esito = 'la giuntura viene in buona parte dalle parole spezzate e dagli elementi corti' if q3 < 0.5 else ('la giuntura sta fra parole vere' if q3 > 0.8 else 'incerto')
    sens = [k for k in ris if k not in ('Voynich', 'gibberish umano')]
    qs2 = sorted(ris[k][1]['E'] / ris[k][0]['E'] for k in sens if ris[k][0]['E'] > 0)
    qs3 = sorted(ris[k][2]['E'] / ris[k][0]['E'] for k in sens if ris[k][0]['E'] > 0)
    sopra3 = sum(ris[k][2]['E'] > V[2]['E'] for k in sens)
    out = OrderedDict([('testi', ris), ('q2_voynich', q2), ('q3_voynich', q3), ('q2_sensati', [qs2[0], statistics.median(qs2), qs2[-1]]),
                       ('q3_sensati', [qs3[0], statistics.median(qs3), qs3[-1]]), ('sensati_con_E3_maggiore', sopra3), ('n_sensati', len(sens)), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e383_giuntura_lunghe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e383 — La giuntura viene dalle parole spezzate?', '', 'Preregistrazione: `preregistrazioni/e383.md`. E = eccesso (bit) della giuntura; 1 = tutte le coppie, 2 = senza unioni che sono parole, 3 = solo parole di 3+ segni.', '',
          '| testo | E1 | z | E2 | z | E3 | z | q2 | q3 |', '|---|---|---|---|---|---|---|---|---|']
    for k in ['Voynich', 'gibberish umano'] + sorted(sens, key=lambda k: -ris[k][2]['E']):
        x = ris[k]
        q = lambda i: x[i]['E'] / x[0]['E'] if x[0]['E'] > 0 else float('nan')
        md.append('| %s | %.4f | %.1f | %.4f | %.1f | %.4f | %.1f | %.2f | %.2f |' % (k, x[0]['E'], x[0]['z'], x[1]['E'], x[1]['z'], x[2]['E'], x[2]['z'], q(1), q(2)))
    md += ['', 'Voynich: q2 %.2f, q3 %.2f. Testi sensati (minimo, mediana, massimo): q2 %s; q3 %s. Testi sensati con E3 maggiore del Voynich: %d su %d.' % (
        q2, q3, ', '.join('%.2f' % x for x in out['q2_sensati']), ', '.join('%.2f' % x for x in out['q3_sensati']), sopra3, len(sens)), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e383_giuntura_lunghe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
