# -*- coding: utf-8 -*-
"""Esperimento 246: la sequenza delle operazioni di variante (classe V) ha struttura sequenziale da messaggio, dentro la
riga (S1) o a cavallo delle righe (S2), oltre i rimescolamenti? Voynich, generatore (negativo), operazioni sostituite da
un testo latino (positivo).

Preregistrazione: preregistrazioni/e246.md. Scrive risultati/e246_messaggio_varianti.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e239_operatore_variante as e239
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, TOP = 246, 200, 25
D = e237.D


def operazioni(pagine):
    """{(pagina, riga): [(posizione, operazione)]} per le parole V."""
    tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
    inventario = sorted({x for w in tutte for x in D(w)})
    out = OrderedDict()
    for p, rr in pagine.items():
        sulla = OrderedDict()
        for k, r in enumerate(rr):
            for j, w in enumerate(r):
                u = tuple(D(w))
                if sulla and u not in sulla:
                    vic = e237.vicini(u, inventario)
                    fonti = [x for x in sulla if x in vic]
                    if fonti:
                        m = max(sulla[x] for x in fonti)
                        s = next(x for x in fonti if sulla[x] == m)
                        out.setdefault((p, k), []).append((j, e239.operazione(s, u)[1]))
                sulla[u] = k
                sulla.move_to_end(u)
    return out


def riduci(ops, top):
    return {k: [(j, o if o in top else 'altro') for j, o in v] for k, v in ops.items()}


def s1(ops):
    return misure.informazione_mutua([(a[1], b[1]) for v in ops.values() for a, b in zip(v, v[1:])])


def s2(ops):
    per_pag = defaultdict(list)
    for (p, k), v in ops.items():
        per_pag[p].append((k, v))
    coppie = []
    for p, ll in per_pag.items():
        ll.sort()
        for (k1, v1), (k2, v2) in zip(ll, ll[1:]):
            coppie.append((v1[-1][1], v2[0][1]))
    return misure.informazione_mutua(coppie)


def prova(ops, rnd):
    v1, v2 = s1(ops), s2(ops)
    n1, n2 = [], []
    for _ in range(RIMESCOLAMENTI):
        m1 = {}
        for k, v in ops.items():
            o = [x for _, x in v]
            rnd.shuffle(o)
            m1[k] = [(j, x) for (j, _), x in zip(v, o)]
        n1.append(s1(m1))
        per_pag = defaultdict(list)
        for (p, k), v in ops.items():
            per_pag[p].append(k)
        m2 = {}
        for p, ks in per_pag.items():
            ks2 = ks[:]
            rnd.shuffle(ks2)
            for a, b in zip(sorted(ks), ks2):
                m2[(p, a)] = ops[(p, b)]
        n2.append(s2(m2))
    z = lambda x, xs: (x - statistics.mean(xs)) / statistics.pstdev(xs) if statistics.pstdev(xs) else None
    conta = Counter(o for v in ops.values() for _, o in v)
    n = sum(conta.values())
    h = -sum(c / n * math.log2(c / n) for c in conta.values())
    return OrderedDict([('varianti', n), ('S1', v1), ('S1_nullo', statistics.mean(n1)), ('z_S1', z(v1, n1)),
                        ('S2', v2), ('S2_nullo', statistics.mean(n2)), ('z_S2', z(v2, n2)), ('entropia_bit', h), ('bit_totali', h * n)])


def main():
    rnd = random.Random(SEME)
    c = e224.contesto()
    vpag = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    ops_v = operazioni(vpag)
    top = [o for o, _ in Counter(o for v in ops_v.values() for _, o in v).most_common(TOP)]
    ops_v = riduci(ops_v, set(top))
    # negativo: generatore e241, seme 2
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(vpag))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(vpag)))
    gp = e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102))
    ops_g = riduci(operazioni(gp), set(top))
    # positivo: le stesse posizioni con le operazioni dettate da un testo latino (lettera di rango i -> operazione di rango i)
    lettere = [ch for _, ps in plinio() for w in ps for ch in w]
    rango_l = [l for l, _ in Counter(lettere).most_common()]
    simboli = top + ['altro']
    mappa = {l: simboli[min(i, len(simboli) - 1)] for i, l in enumerate(rango_l)}
    it = iter(lettere)
    ops_p = {k: [(j, mappa[next(it)]) for j, _ in v] for k, v in ops_v.items()}
    ris = OrderedDict()
    for nome, ops in (('Voynich', ops_v), ('generatore e241 (negativo)', ops_g), ('testo latino nelle varianti (positivo)', ops_p)):
        ris[nome] = prova(ops, rnd)
        r = ris[nome]
        print('%s: varianti %d, S1 %.4f (z %.1f), S2 %.4f (z %.1f), %.2f bit/variante, %.0f bit' % (
            nome, r['varianti'], r['S1'], r['z_S1'] or 0, r['S2'], r['z_S2'] or 0, r['entropia_bit'], r['bit_totali']), flush=True)
    v, g, p = (ris[k] for k in ris)
    valido = (p['z_S1'] or 0) > 3 or (p['z_S2'] or 0) > 3
    struttura = (v['z_S2'] or 0) > 3 or ((v['z_S1'] or 0) > 3 and (v['z_S1'] or 0) - (g['z_S1'] or 0) >= 3)
    esito = 'non valido' if not valido else ('struttura nelle varianti, da esaminare' if struttura else 'nessuna struttura')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e246_messaggio_varianti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e246 — Un messaggio nella sequenza delle varianti?', '',
          'Operazioni delle varianti (25 più frequenti + altro). S1: informazione mutua fra operazioni consecutive nella riga (nullo: rimescolamento '
          'nella riga); S2: fra l\'ultima di una riga e la prima della successiva (nullo: rimescolamento delle righe nella pagina). %d rimescolamenti. '
          'Preregistrazione: `preregistrazioni/e246.md`.' % RIMESCOLAMENTI, '',
          '| testo | varianti | S1 | z S1 | S2 | z S2 | bit per variante | bit totali |', '|---|---|---|---|---|---|---|---|']
    for nome in list(ris)[:3]:
        r = ris[nome]
        md.append('| %s | %d | %.4f | %.1f | %.4f | %.1f | %.2f | %.0f |' % (nome, r['varianti'], r['S1'], r['z_S1'] or 0, r['S2'], r['z_S2'] or 0, r['entropia_bit'], r['bit_totali']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e246_messaggio_varianti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
