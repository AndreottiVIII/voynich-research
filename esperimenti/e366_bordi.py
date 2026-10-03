# -*- coding: utf-8 -*-
"""Esperimento 366: le forme nuove prime della riga diventano parole note togliendo il primo segno, e le ultime togliendo
l'ultimo, piu' delle forme nuove in mezzo alla riga?

Preregistrazione: preregistrazioni/e366.md. Scrive risultati/e366_bordi.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def zbin(p1, n1, p2, n2):
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    return (p1 - p2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 0.0


def main():
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append((bool(r.inizio_par), ws))
    freq = Counter(w for _, ws in righe for w in ws)
    sim = e350.simili_globali(set(freq))
    U = {w: tuple(D(w)) for w in freq}
    nuova = {w for w, n in freq.items() if n == 1 and len(U[w]) >= 3 and not any(freq[v] >= 20 for v in sim[w] if v != w)}
    gruppi = {'prima': [], 'ultima': [], 'mezzo': []}
    for ini, ws in righe:
        n = len(ws)
        for j, w in enumerate(ws):
            if w not in nuova:
                continue
            if j == 0 and not ini and n >= 2:
                gruppi['prima'].append(w)
            elif j == n - 1 and n >= 2:
                gruppi['ultima'].append(w)
            elif 0 < j < n - 1:
                gruppi['mezzo'].append(w)
    nota = lambda s: freq.get(s, 0) >= 2
    togli_i = lambda w: ''.join(U[w][1:])
    togli_f = lambda w: ''.join(U[w][:-1])
    out = OrderedDict()
    for g, ws in gruppi.items():
        qi = sum(nota(togli_i(w)) for w in ws) / len(ws)
        qf = sum(nota(togli_f(w)) for w in ws) / len(ws)
        out[g] = OrderedDict([('forme_nuove', len(ws)), ('togliendo_il_primo', qi), ('togliendo_l_ultimo', qf),
                              ('primi_segni_tolti', Counter(U[w][0] for w in ws if nota(togli_i(w))).most_common(6)),
                              ('ultimi_segni_tolti', Counter(U[w][-1] for w in ws if nota(togli_f(w))).most_common(6))])
    zi = zbin(out['prima']['togliendo_il_primo'], out['prima']['forme_nuove'], out['mezzo']['togliendo_il_primo'], out['mezzo']['forme_nuove'])
    zf = zbin(out['ultima']['togliendo_l_ultimo'], out['ultima']['forme_nuove'], out['mezzo']['togliendo_l_ultimo'], out['mezzo']['forme_nuove'])
    es = lambda z, nome: nome if z > 3 else ('no' if z < 2 else 'incerto')
    res = OrderedDict([('gruppi', out), ('z_inizio', zi), ('esito_inizio', es(zi, 'segno di inizio riga')), ('z_fine', zf), ('esito_fine', es(zf, 'segno di fine riga'))])
    print(json.dumps(res, ensure_ascii=False), flush=True)
    json.dump(res, open(os.path.join(RISULTATI, 'e366_bordi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e366 — Le forme nuove ai bordi della riga sono parole normali con un segno di bordo?', '', 'Preregistrazione: `preregistrazioni/e366.md`.', '',
          '| forme nuove | numero | diventano parola nota togliendo il primo segno | togliendo l\'ultimo |', '|---|---|---|---|']
    for g, v in out.items():
        md.append('| %s | %d | %.3f | %.3f |' % (g, v['forme_nuove'], v['togliendo_il_primo'], v['togliendo_l_ultimo']))
    md += ['', 'Inizio riga contro in mezzo: z %.1f → **%s**. Fine riga contro in mezzo: z %.1f → **%s**.' % (zi, res['esito_inizio'], zf, res['esito_fine']),
           'Segni tolti all\'inizio (prime della riga): %s. Segni tolti alla fine (ultime della riga): %s.' % (out['prima']['primi_segni_tolti'], out['ultima']['ultimi_segni_tolti'])]
    open(os.path.join(RISULTATI, 'e366_bordi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
