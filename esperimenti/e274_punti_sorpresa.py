# -*- coding: utf-8 -*-
"""Esperimento 274: sorpresa di ogni parola secondo la mistura dell'e259b (validazione incrociata pagine pari/dispari),
residuo per lunghezza e posizione nella riga; i punti caldi (10% dei residui piu' alti) sono raggruppati fra parole vicine?
Voynich, generatore e241 (negativo), Voynich con frammenti di Plinio inseriti (positivo).

Preregistrazione: preregistrazioni/e274.md. Scrive risultati/e274_punti_sorpresa.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241
import e259_bit_per_parola as e259
import e259b_varianti_pesate as e259b
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, QUOTA_CALDI = 274, 500, 0.10


def sorprese(pagine, unita):
    """Sorpresa (bit) di ogni parola, in validazione incrociata pari/dispari; stesso ordine di pagine, righe, parole."""
    out = {}
    for verifica in (0, 1):
        train = [p for i, p in enumerate(pagine) if i % 2 != verifica]
        test_idx = [i for i in range(len(pagine)) if i % 2 == verifica]
        k = int(len(train) * 0.8)
        lam = e259b.em(e259b.componenti(e259b.Modello2(train[:k], unita), train[k:]), set(range(e259b.NC)))
        m = e259b.Modello2(train, unita)
        for i in test_idx:
            comp = e259b.componenti(m, [pagine[i]])
            out[i] = [-math.log2(max(1e-300, sum(lam[c] * x[c] for c in range(e259b.NC)))) for x in comp]
    return [out[i] for i in range(len(pagine))]


def prova(nome, pagine, unita, rnd):
    s = sorprese(pagine, unita)
    voci = []                                   # (pagina, riga, posizione, residuo)
    gruppi = defaultdict(list)
    for i, p in enumerate(pagine):
        t = 0
        for k, r in enumerate(p):
            for j, w in enumerate(r):
                pos = 0 if j == 0 else (2 if j == len(r) - 1 else 1)
                chiave = (min(len(unita(w)), 8), pos)
                gruppi[chiave].append(s[i][t])
                voci.append((i, k, j, chiave, s[i][t]))
                t += 1
    medie = {k: statistics.mean(v) for k, v in gruppi.items()}
    res = [(i, k, j, x - medie[ch]) for i, k, j, ch, x in voci]
    soglia = sorted(r for *_, r in res)[int(len(res) * (1 - QUOTA_CALDI))]
    per_riga = defaultdict(list)
    for i, k, j, r in res:
        per_riga[(i, k)].append(r)

    def G(righe):
        n = c = 0
        for v in righe:
            for a, b in zip(v, v[1:]):
                n += 1
                c += a >= soglia and b >= soglia
        return c / n if n else 0.0

    righe = list(per_riga.values())
    vera = G(righe)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        nulli.append(G([rnd.sample(v, len(v)) for v in righe]))
    mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    r = OrderedDict([('parole', len(res)), ('G', vera), ('nullo', mu), ('z', (vera - mu) / sd if sd else None),
                     ('sorpresa_media', statistics.mean(x for *_, x in voci))])
    print(nome, dict(r), flush=True)
    return r


def main():
    rnd = random.Random(SEME)
    vp, vu = e259.voynich()
    c = e224.contesto()
    pv = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    g241 = list(e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102)).values())
    latino = [w for _, ps in plinio() for w in ps]
    pos = []
    t = 0
    for p in vp:
        np_ = []
        for r in p:
            r = list(r)
            if len(r) >= 4 and rnd.random() < 1 / 3:
                a = rnd.randrange(0, len(r) - 2)
                r[a:a + 3] = latino[t:t + 3]
                t += 3
            np_.append(r)
        pos.append(np_)
    ris = OrderedDict()
    for nome, pag in (('Voynich', vp), ('generatore e241 (negativo)', g241), ('Voynich con frammenti di Plinio (positivo)', pos)):
        ris[nome] = prova(nome, pag, vu, rnd)
    v, g, p = (ris[k] for k in ris)
    valido = (p['z'] or 0) > 3
    esito = ('non valido' if not valido else 'punti caldi raggruppati, da esaminare' if (v['z'] or 0) > 3 and (v['z'] or 0) - (g['z'] or 0) >= 3
             else 'nessun raggruppamento')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e274_punti_sorpresa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e274 — Dove il testo sorprende: i punti imprevedibili sono raggruppati?', '',
          "Sorpresa secondo la mistura dell'e259b (validazione incrociata pari/dispari), residuo per lunghezza e posizione; G = quota di coppie vicine "
          'entrambe nel %d%% più sorprendente; nullo: %d rimescolamenti nella riga. Preregistrazione: `preregistrazioni/e274.md`.' % (int(100 * QUOTA_CALDI), RIMESCOLAMENTI), '',
          '| testo | parole | sorpresa media (bit) | G | nullo | z |', '|---|---|---|---|---|---|']
    for nome in list(ris)[:3]:
        r = ris[nome]
        md.append('| %s | %d | %.2f | %.4f | %.4f | %.1f |' % (nome, r['parole'], r['sorpresa_media'], r['G'], r['nullo'], r['z'] or 0))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e274_punti_sorpresa.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
