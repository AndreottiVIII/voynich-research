# -*- coding: utf-8 -*-
"""Esperimento 367: le prime parole di riga della forma p + X (p segno singolo s/d/y/o/l/r, X parola nota) corrispondono a
coppie "p X" scritte staccate in mezzo alla riga piu' del caso?

Preregistrazione: preregistrazioni/e367.md. Scrive risultati/e367_staccati.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEGNI = ('s', 'd', 'y', 'o', 'l', 'r')


def main():
    rnd = random.Random(367)
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append((bool(r.inizio_par), ws))
    freq = Counter(w for _, ws in righe for w in ws)
    U = {w: tuple(D(w)) for w in freq}
    staccate = Counter()
    for _, ws in righe:
        for j in range(1, len(ws) - 1):
            if ws[j] in SEGNI:
                staccate[(ws[j], ws[j + 1])] += 1
    casi = []
    for ini, ws in righe:
        if ini or len(ws) < 2:
            continue
        u = U[ws[0]]
        if len(u) >= 3 and u[0] in SEGNI:
            x = ''.join(u[1:])
            if freq.get(x, 0) >= 2:
                casi.append((u[0], x))
    vero = statistics.mean(staccate[(p, x)] > 0 for p, x in casi) if casi else 0.0
    decile = {}
    xs_noti = sorted({w for w, n in freq.items() if n >= 2}, key=lambda w: freq[w])
    for k, w in enumerate(xs_noti):
        decile[w] = 10 * k // len(xs_noti)
    per_dec = defaultdict(list)
    for w in xs_noti:
        per_dec[decile[w]].append(w)
    nul = []
    for _ in range(1000):
        nul.append(statistics.mean(staccate[(p, rnd.choice(per_dec[decile[x]]))] > 0 for p, x in casi))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero - m) / sd if sd else 0.0
    sola_inizio = Counter(ws[0] for ini, ws in righe if not ini and ws[0] in SEGNI)
    sola_mezzo = Counter(w for _, ws in righe for w in ws[1:-1] if w in SEGNI)
    n_ini = sum(1 for ini, ws in righe if not ini)
    n_mezzo = sum(max(0, len(ws) - 2) for _, ws in righe)
    desc = OrderedDict((p, OrderedDict([('da_sola_a_inizio_riga', sola_inizio[p] / n_ini), ('da_sola_in_mezzo', sola_mezzo[p] / n_mezzo),
                                         ('attaccata_a_inizio_riga', sum(1 for q, _ in casi if q == p) / n_ini)])) for p in SEGNI)
    esito = 'la parolina staccata si attacca a inizio riga' if z > 3 else ('no' if z < 2 else 'incerto')
    out = OrderedDict([('casi', len(casi)), ('quota_con_coppia_staccata', vero), ('nullo', m), ('z', z), ('esito', esito), ('descrittiva', desc),
                       ('esempi', [('%s%s' % (p, x), staccate[(p, x)]) for p, x in casi if staccate[(p, x)] > 0][:15])])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e367_staccati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e367 — Il segno attaccato a inizio riga è la parolina staccata di metà riga?', '', 'Preregistrazione: `preregistrazioni/e367.md`.', '',
          '- Prime parole di riga della forma p + X (X nota): %d. Con la coppia "p X" staccata altrove in mezzo alla riga: %.3f; nullo %.3f; z %.1f.' % (len(casi), vero, m, z),
          '', '| segno | da solo a inizio riga | da solo in mezzo | attaccato a inizio riga |', '|---|---|---|---|']
    for p, v in desc.items():
        md.append('| %s | %.4f | %.4f | %.4f |' % (p, v['da_sola_a_inizio_riga'], v['da_sola_in_mezzo'], v['attaccata_a_inizio_riga']))
    md += ['', 'Esito: **%s**. Esempi: %s.' % (esito, ', '.join('%s (%d)' % e for e in out['esempi']))]
    open(os.path.join(RISULTATI, 'e367_staccati.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
