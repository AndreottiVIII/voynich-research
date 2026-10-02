# -*- coding: utf-8 -*-
"""Esperimento 179: distanza fisica (spaziatura, passo di riga, scuro) delle adiacenze presenti solo nell'ordine
ricostruito contro quelle presenti solo nella rilegatura.

Preregistrazione: preregistrazioni/e179.md. Scrive risultati/e179_adiacenze_in_disaccordo.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154
import e154b_ordine_normalizzato as e154b
import e161_inchiostro as e161
import e170_scuro_ordine as e170
import e178_spaziatura_ordine as e178

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 179, 5000
NOMI = ('spaziatura', 'passo di riga', 'scuro')


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    sp, pa, sc = e178.per_foglio(), e161.passo_per_foglio(), e170.per_foglio()
    C = {}
    for n in U:
        ff = [int(x[1:]) for x in n.split('-')]
        a = [sp[f] for f in ff if f in sp]
        b = [pa[f][0] for f in ff if f in pa]
        c = [sc[f][0] for f in ff if f in sc]
        if a and b and c:
            C[n] = [statistics.mean(a), statistics.mean(b), statistics.mean(c)]
    gruppi = defaultdict(list)
    for n, u in U.items():
        if n in C:
            gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = OrderedDict((k, v) for k, v in sorted(gruppi.items(), key=lambda kv: -len(kv[1])) if len(v) >= 6)
    archi = []  # (gruppo, etichetta 'R'/'B', distanza, distanze per misura)
    for k, nomi in gruppi.items():
        X = e154.standardizza({n: C[n] for n in nomi})
        vett = {n: Counter(e154b.normalizza(w) for ps in U[n]['righe'] for w in ps) for n in nomi}
        S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
        ric = [nomi[i] for i in e150.ricostruisci(S)]
        ril = sorted(nomi, key=lambda n: U[n]['primo'])
        er = {frozenset(p) for p in zip(ric, ric[1:])}
        eb = {frozenset(p) for p in zip(ril, ril[1:])}
        for et, insieme in (('R', er - eb), ('B', eb - er)):
            for e in sorted(insieme, key=sorted):
                a, b = sorted(e)
                archi.append((k, et, math.dist(X[a], X[b]), [abs(X[a][j] - X[b][j]) for j in range(3)]))

    def stat(etichette, j=None):
        r = [(a[2] if j is None else a[3][j]) for a, e in zip(archi, etichette) if e == 'R']
        b = [(a[2] if j is None else a[3][j]) for a, e in zip(archi, etichette) if e == 'B']
        return statistics.mean(b) - statistics.mean(r)
    vere = [a[1] for a in archi]
    vero = stat(vere)
    per_g = defaultdict(list)
    for i, a in enumerate(archi):
        per_g[a[0]].append(i)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        et = vere[:]
        for idx in per_g.values():
            v = [et[i] for i in idx]
            rnd.shuffle(v)
            for i, x in zip(idx, v):
                et[i] = x
        nulli.append(stat(et))
    p_ric = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    p_ril = (1 + sum(n <= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    esito = 'ricostruito favorito' if vero > 0 and p_ric < 0.05 else ('rilegatura favorita' if vero < 0 and p_ril < 0.05 else 'nessuna preferenza')
    per_misura = OrderedDict((NOMI[j], stat(vere, j)) for j in range(3))
    ris = OrderedDict([('unita', len(C)), ('gruppi', {('%s/%s' % k): len(v) for k, v in gruppi.items()}), ('archi_R', vere.count('R')), ('archi_B', vere.count('B')),
                       ('statistica', vero), ('p_ricostruito', p_ric), ('p_rilegatura', p_ril), ('per_misura', per_misura), ('esito', esito)])
    print('unità %d gruppi %s | archi R %d B %d | B−R %.3f | p ricostruito %.4f, p rilegatura %.4f | %s | per misura %s' % (
        len(C), ris['gruppi'], ris['archi_R'], ris['archi_B'], vero, p_ric, p_ril, esito, {k: round(v, 3) for k, v in per_misura.items()}), flush=True)
    with open(os.path.join(RISULTATI, 'e179_adiacenze_in_disaccordo.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=float)
    out = ['# e179 — Ordine ricostruito contro rilegatura, solo sulle adiacenze in disaccordo', '',
           'Distanza fisica (spaziatura, passo di riga, scuro; standardizzati nel gruppo) delle coppie consecutive solo nell\'ordine ricostruito (R) '
           'o solo nella rilegatura (B). Preregistrazione: `preregistrazioni/e179.md`.', '',
           '| | valore |', '|---|---|', '| coppie R / B | %d / %d |' % (ris['archi_R'], ris['archi_B']),
           '| media B − media R | %.3f |' % vero, '| p (ricostruito favorito) | %.4f |' % p_ric, '| p (rilegatura favorita) | %.4f |' % p_ril, '',
           'Per misura (B − R): ' + ', '.join('%s %.3f' % kv for kv in per_misura.items()) + '.', '', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e179_adiacenze_in_disaccordo.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
