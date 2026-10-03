# -*- coding: utf-8 -*-
"""Esperimento e3a30: classi "vocali/consonanti" di Sukhotin ricavate dentro le parole; quota di coppie di parole vicine
in cui l'ultimo e il primo segno sono di classe diversa, contro le parole rimescolate nella riga. Voynich, testi sensati,
gibberish.

Preregistrazione: preregistrazioni/e3a30.md. Scrive risultati/e3a30_sukhotin.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')


def sukhotin(righe):
    adj = defaultdict(lambda: defaultdict(int))
    segni = set()
    for r in righe:
        for w in r:
            segni.update(w)
            for a, b in zip(w, w[1:]):
                if a != b:
                    adj[a][b] += 1
                    adj[b][a] += 1
    somme = {s: sum(adj[s].values()) for s in segni}
    vocali = set()
    while True:
        cand = [s for s in segni if s not in vocali]
        if not cand:
            break
        v = max(cand, key=lambda s: somme[s])
        if somme[v] <= 0:
            break
        vocali.add(v)
        for s in cand:
            if s != v:
                somme[s] -= 2 * adj[s][v]
    return vocali


def alternanza(righe, vocali, rnd, perm):
    righe = [r for r in righe if len(r) >= 2]

    def q(rr):
        alt = tot = 0
        for r in rr:
            for a, b in zip(r, r[1:]):
                tot += 1
                alt += (a[-1] in vocali) != (b[0] in vocali)
        return alt / tot
    vero = q(righe)
    nul = [q([rnd.sample(r, len(r)) for r in righe]) for _ in range(perm)]
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('osservata', vero), ('nullo', m), ('A', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3130)
    voy = [r for p in e375.voynich() for r in p]
    vv = sukhotin(voy)
    ris = OrderedDict([('Voynich', alternanza(voy, vv, rnd, 1000))])
    ris['Voynich']['vocali'] = sorted(vv)
    print('Voynich', json.dumps(ris['Voynich'], ensure_ascii=False), flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
    gv = sukhotin(gib)
    ris['gibberish umano'] = alternanza(gib, gv, rnd, 200)
    ris['gibberish umano']['vocali'] = sorted(gv)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        v = sukhotin(righe)
        x = alternanza(righe, v, rnd, 200)
        x['vocali'] = sorted(v)
        sens[k.replace('.txt', '')] = x
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -(kv[1]['A'] or 0)))
    As = [x['A'] for x in sens.values() if x['A'] is not None]
    V = ris['Voynich']
    if V['z'] < 2:
        esito = 'non alterna'
    elif V['A'] > 1 and V['z'] > 3 and V['A'] > max(As):
        esito = 'alterna più delle lingue'
    elif V['A'] > 1 and V['z'] > 3 and min(As) <= V['A'] <= max(As):
        esito = 'il confine alterna come le lingue (%d testi su %d con A maggiore)' % (sum(1 for a in As if a > V['A']), len(As))
    else:
        esito = 'incerto'
    ris['A_lingue'] = [min(As), statistics.median(As), max(As)]
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a30_sukhotin.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a30 — Al confine fra parole si alternano "vocali" e "consonanti"?', '', 'Preregistrazione: `preregistrazioni/e3a30.md`. A = quota di coppie con ultimo e primo segno di classe diversa / nullo.', '',
          'Voynich: A %.3f (z %.1f); "vocali" di Sukhotin: %s. Gibberish umano: A %.3f (z %.1f). Testi sensati: A da %.3f a %.3f (mediana %.3f).' % (
              V['A'], V['z'], ', '.join(V['vocali']), ris['gibberish umano']['A'], ris['gibberish umano']['z'], *ris['A_lingue'][::2], ris['A_lingue'][1]), '',
          '| testo sensato | A | z | "vocali" |', '|---|---|---|---|']
    md += ['| %s | %.3f | %.1f | %s |' % (k, x['A'], x['z'], ' '.join(x['vocali'])) for k, x in ris['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a30_sukhotin.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
