# -*- coding: utf-8 -*-
"""Esperimento 368: indice di attacco I = A / (A + S) delle paroline p (s, d, y, o, l) a inizio riga e in mezzo, dove A
conta le forme p + X (X nota) e S la parolina p da sola seguita da una X nota.

Preregistrazione: preregistrazioni/e368.md. Scrive risultati/e368_attacco.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEGNI = ('s', 'd', 'y', 'o', 'l')


def main():
    rnd = random.Random(368)
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if len(ws) >= 3 and not r.inizio_par:
                righe.append(ws)
    freq = Counter(w for ws in righe for w in ws)
    U = {w: tuple(D(w)) for w in freq}
    nota = lambda x: freq.get(x, 0) >= 2

    def conta(ws):
        """Per riga: {(pos, p, 'A'/'S'): n}."""
        c = Counter()
        n = len(ws)
        for j, w in enumerate(ws):
            pos = 'inizio' if j == 0 else ('mezzo' if j < n - 1 else None)
            if pos is None:
                continue
            u = U[w]
            if w in SEGNI and j + 1 < n and nota(ws[j + 1]):
                c[(pos, w, 'S')] += 1
            elif len(u) >= 3 and u[0] in SEGNI and nota(''.join(u[1:])):
                c[(pos, u[0], 'A')] += 1
        return c
    per_riga = [conta(ws) for ws in righe]

    def indici(campione):
        tot = Counter()
        for c in campione:
            tot.update(c)
        out = {}
        for pos in ('inizio', 'mezzo'):
            for p in SEGNI + ('tutti',):
                ps = SEGNI if p == 'tutti' else (p,)
                a = sum(tot[(pos, q, 'A')] for q in ps)
                s = sum(tot[(pos, q, 'S')] for q in ps)
                out[(pos, p)] = (a / (a + s) if a + s else None, a, s)
        return out
    vero = indici(per_riga)
    diff = vero[('inizio', 'tutti')][0] - vero[('mezzo', 'tutti')][0]
    boot = []
    for _ in range(1000):
        b = indici([per_riga[rnd.randrange(len(per_riga))] for _ in per_riga])
        boot.append(b[('inizio', 'tutti')][0] - b[('mezzo', 'tutti')][0])
    sd = statistics.pstdev(boot)
    z = diff / sd if sd else 0.0
    boot.sort()
    esito = 'a inizio riga la parolina si attacca di più' if z > 3 else ('nessuna differenza' if abs(z) < 2 else 'incerto')
    tab = OrderedDict(('%s %s' % k, OrderedDict([('indice', v[0]), ('attaccate', v[1]), ('staccate', v[2])])) for k, v in vero.items())
    out = OrderedDict([('righe', len(righe)), ('indici', tab), ('differenza_inizio_meno_mezzo', diff), ('IC95', [boot[25], boot[974]]), ('z', z), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e368_attacco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e368 — Inizio riga contro centro: la parolina si attacca di più all\'inizio?', '', 'Preregistrazione: `preregistrazioni/e368.md`. %d righe (non prime di paragrafo).' % len(righe), '',
          '| segno | indice di attacco a inizio riga (attaccate/staccate) | in mezzo |', '|---|---|---|']
    for p in SEGNI + ('tutti',):
        a, m = vero[('inizio', p)], vero[('mezzo', p)]
        f = lambda v: ('%.3f (%d/%d)' % v) if v[0] is not None else '– (%d/%d)' % (v[1], v[2])
        md.append('| %s | %s | %s |' % (p, f(a), f(m)))
    md += ['', 'Differenza complessiva inizio − mezzo: %+.3f (IC 95%% %+.3f – %+.3f), z %.1f. Esito: **%s**.' % (diff, boot[25], boot[974], z, esito)]
    open(os.path.join(RISULTATI, 'e368_attacco.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
