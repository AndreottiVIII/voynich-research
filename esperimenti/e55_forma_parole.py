# -*- coding: utf-8 -*-
"""Esperimento 55: la forma delle parole. Distanza Jensen-Shannon fra le distribuzioni del segno in
ciascuna posizione (primo, secondo, penultimo, ultimo) di un testo e del Voynich; riferimenti:
Voynich pagine pari contro dispari (rumore), Currier A contro B (dialetto). V8: distanza <= A-B
in tutte e quattro le posizioni.

Usa i testi dei generatori gia' in cache (e22, e23, e51, e53). Preregistrazione: preregistrazioni/e55.md.
Scrive risultati/e55_forma_parole.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
from e36_posizione_pagina import plinio
from e53_scissione import scindi, giunture_morbide

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
POS = OrderedDict([('primo', 0), ('secondo', 1), ('penultimo', -2), ('ultimo', -1)])
CACHE = e22.LAVORO
SEMI = (19, 1, 2)


def distr(parole, pos):
    c = Counter(D(w)[pos] for w in parole if len(D(w)) >= 2)
    n = sum(c.values())
    return {k: v / n for k, v in c.items()}


def jsd(p, q):
    ks = set(p) | set(q)
    m = {k: (p.get(k, 0) + q.get(k, 0)) / 2 for k in ks}
    kl = lambda a: sum(a[k] * math.log2(a[k] / m[k]) for k in ks if a.get(k, 0) > 0)
    return (kl(p) + kl(q)) / 2


def distanze(a, b):
    return {n: jsd(distr(a, p), distr(b, p)) for n, p in POS.items()}


def da_file(percorso):
    return [l.split() for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]


def main():
    righe_zl = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(righe_zl)
    pagine = list(dict.fromkeys(r.pagina for r in righe_zl))
    pari = {p for i, p in enumerate(pagine) if i % 2 == 0}
    v_pari = [w for r in righe_zl if r.pagina in pari for w in r.parole if trascrizione.pulita(w)]
    v_disp = [w for r in righe_zl if r.pagina not in pari for w in r.parole if trascrizione.pulita(w)]
    va = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A'))
    vb = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B'))
    ris = OrderedDict()
    ris['rumore: Voynich pagine pari / dispari'] = distanze(v_pari, v_disp)
    ris['dialetto: Currier A / B'] = distanze(va, vb)
    soglia = ris['dialetto: Currier A / B']
    testi = OrderedDict()
    morbide = giunture_morbide()
    for s in SEMI:
        testi['Timm e Schinner, seme %d' % s] = da_file(os.path.join(CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt'))
        testi['+ giunture (e23), seme %d' % s] = da_file(os.path.join(CACHE, 'giunture', 'forza_3_seme_%d' % s, 'generate', 'generated_text.txt'))
        testi['modello e51, seme %d' % s] = da_file(os.path.join(CACHE, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_%d' % s, 'generate', 'generated_text.txt'))
        base = da_file(os.path.join(CACHE, 'recenza_novita', 'e53_finali_0_seme_%d' % s, 'generate', 'generated_text.txt'))
        testi['modello e53 (d 0,06), seme %d' % s] = scindi([base], 0.06, morbide, random.Random(53 + s))[0]
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    testi['Naibbe (Plinio XVI, Greshko)'] = [naibbe]
    latino = [w for _, ps in plinio() for w in ps]
    testi['codice parola per parola (Plinio)'] = [generatori.codice_per_rango(
        latino, voy, generatori.ModelloParole(voy, D), random.Random(55))]
    for nome, righe in testi.items():
        parole = [w for r in righe for w in r]
        d = distanze(parole, voy)
        d['V8'] = all(d[n] <= soglia[n] for n in POS)
        ris[nome] = d
        print('%-40s %s %s' % (nome, '  '.join('%s %.3f' % (n[:3], d[n]) for n in POS), 'V8' if d['V8'] else ''), flush=True)
    with open(os.path.join(RISULTATI, 'e55_forma_parole.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e55 — La forma delle parole: distanza dal Voynich della distribuzione dei segni per posizione', '',
           'Distanza Jensen–Shannon (bit) fra la distribuzione del segno in ciascuna posizione del testo e quella del '
           'Voynich. V8 = distanza non superiore a quella fra Currier A e B in tutte le posizioni. '
           'Preregistrazione: `preregistrazioni/e55.md`.', '',
           '| testo | primo | secondo | penultimo | ultimo | V8 |', '|---|---|---|---|---|---|']
    for nome, d in ris.items():
        out.append('| %s | %s | %s |' % (nome, ' | '.join('%.3f' % d[n] for n in POS), 'sì' if d.get('V8') else ''))
    with open(os.path.join(RISULTATI, 'e55_forma_parole.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
