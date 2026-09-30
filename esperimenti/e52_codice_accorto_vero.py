# -*- coding: utf-8 -*-
"""Esperimento 52: il codice accorto con varianti vere del Voynich.

Come l'e46, ma le forme ammesse di ogni parola latina sono la forma base piu' fino a 8 parole
vere del Voynich (attestate almeno 2 volte) a distanza di edit 1 dalla base.
Preregistrazione: preregistrazioni/e52.md. Scrive risultati/e52_codice_accorto_vero.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e46_codice_accorto as e46
from e07_codifiche import pagine_voynich
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
BETA = (5, 20, 50)
TAU = (1.5, 6.0)
GAMMA = (0, 1.5)
VARIANTI = 8


def vicine(u, v):
    """Distanza di edit 1 fra due tuple di segni (sostituzione, inserimento o cancellazione)."""
    if abs(len(u) - len(v)) > 1 or u == v:
        return False
    if len(u) == len(v):
        return sum(a != b for a, b in zip(u, v)) == 1
    corta, lunga = (u, v) if len(u) < len(v) else (v, u)
    return any(lunga[:i] + lunga[i + 1:] == corta for i in range(len(lunga)))


def forme_vere(base, parole_v, dividi):
    freq = Counter(tuple(dividi(w)) for w in parole_v)
    attestate = [u for u, c in freq.most_common() if c >= 2]
    per_lunghezza = defaultdict(list)
    for u in attestate:
        per_lunghezza[len(u)].append(u)
    cache = {}
    out = {}
    for t, b in base.items():
        u0 = tuple(dividi(b))
        if u0 not in cache:
            cand = [u for L in (len(u0) - 1, len(u0), len(u0) + 1) for u in per_lunghezza.get(L, []) if vicine(u0, u)]
            cand.sort(key=lambda u: -freq[u])
            cache[u0] = [u0] + cand[:VARIANTI]
        out[t] = cache[u0]
    return out


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    pagine_v = pagine_voynich(corrente)
    struttura = [[len(r) for r in p] for p in pagine_v]
    giunture = e46.tabella_giunture([r for p in pagine_v for r in p], glifi)
    latino = [w for _, ps in plinio() for w in ps]
    codice = generatori.codice_per_rango(latino, parole_v, generatori.ModelloParole(parole_v, glifi), random.Random(52))
    base = {}
    for w, c in zip(latino, codice):
        base.setdefault(w, c)
    forme = forme_vere(base, parole_v, glifi)
    chi = defaultdict(set)
    for t, fs in forme.items():
        for f in fs:
            chi[f].add(t)
    ris = OrderedDict()
    ris['Voynich'] = e46.lista(pagine_v, glifi)
    ris['cifrario'] = {'tipi_latini': len(forme), 'forme_medie': sum(map(len, forme.values())) / len(forme),
                       'forme_ambigue': sum(1 for f in chi if len(chi[f]) > 1) / len(chi)}
    print('cifrario', ris['cifrario'], flush=True)
    for gamma in GAMMA:
        for tau in TAU:
            for beta in BETA:
                nome = 'beta %g, tau %g, gamma %g' % (beta, tau, gamma)
                pagine = e46.scrivi(struttura, latino, forme, giunture, beta, tau, gamma, random.Random(52))
                r = e46.lista(pagine, glifi)
                scritte = [tuple(glifi(p)) for pg in pagine for rr in pg for p in rr]
                r['posti_ambigui'] = sum(1 for u in scritte if len(chi[u]) > 1) / len(scritte)
                r['compatibile'] = e46.compatibile(r)
                ris[nome] = r
                print('%-28s rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f hapax %.2f tipi %.3f ambigui %.2f %s' % (
                    nome, r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_6_righe'], r['h2'],
                    r['confine'], r['hapax'], r['tipi_su_parole'], r['posti_ambigui'],
                    'COMPATIBILE' if r['compatibile'] else ''), flush=True)
    with open(os.path.join(RISULTATI, 'e52_codice_accorto_vero.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    c = ris['cifrario']
    out = ['# e52 — Il codice accorto con varianti vere del Voynich', '',
           'Come l\'e46, ma le forme ammesse sono la base più fino a %d parole vere del Voynich (attestate ≥ 2 volte) '
           'a distanza di edit 1 (in media %.1f forme per parola latina; %.1f%% delle forme ammesse da più parole). '
           'Preregistrazione: `preregistrazioni/e52.md`.' % (VARIANTI, c['forme_medie'], 100 * c['forme_ambigue']), '',
           '| testo | h2 | spazio | parole uniche | tipi/parole | ripetizione | somigl. riga | 6 righe | legame | posti ambigui | compatibile |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if nome == 'cifrario':
            continue
        out.append('| %s | %.2f | %.0f%% | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | %s | %s |' % (
            nome, r['h2'], 100 * r['spazio_spiegato'], r['hapax'], r['tipi_su_parole'], r['identiche_vs_riga'],
            100 * r['somiglianza_riga'], 100 * r['somiglianza_6_righe'], r['confine'],
            '%.0f%%' % (100 * r['posti_ambigui']) if 'posti_ambigui' in r else '—', 'sì' if r.get('compatibile') else ''))
    with open(os.path.join(RISULTATI, 'e52_codice_accorto_vero.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
