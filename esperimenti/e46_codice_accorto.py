# -*- coding: utf-8 -*-
"""Esperimento 46: il codice accorto. Messaggio intero; ogni parola ha piu' forme equivalenti
e chi scrive sceglie quella piu' simile a cio' che ha appena scritto (stile di pagina),
eventualmente rispettando le giunture.

Forme ammesse S(w): la forma base (codice_per_rango) piu' fino a 11 varianti con una o due
modifiche del Voynich, fisse per tipo latino (seme dal tipo, con crc32: niente hash di Python).
Scelta con probabilita' proporzionale a exp(beta * somiglianza) * R^gamma.

Preregistrazione: preregistrazioni/e46.md. Scrive risultati/e46_codice_accorto.json e .md.
"""
import json, math, os, random, sys, zlib
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
from e07_codifiche import impronta, pagine_voynich
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
BETA = (0, 3, 8, 20)
TAU = (1.5, 6.0)
GAMMA = (0, 3)
VARIANTI = 11
PESO_MINIMO = 0.05          # righe con peso exp(-d/tau) sotto questa soglia non entrano nel contesto
R_IGNOTA = 0.05             # rapporto per giunture mai viste nel Voynich


def tabella_giunture(righe, dividi):
    coppie, fine, inizio = Counter(), Counter(), Counter()
    for r in righe:
        for a, b in zip(r, r[1:]):
            u, v = dividi(a)[-1], dividi(b)[0]
            coppie[u, v] += 1
            fine[u] += 1
            inizio[v] += 1
    tot = sum(coppie.values())
    return {(a, b): (c / fine[a]) / (inizio[b] / tot) for (a, b), c in coppie.items()}


def forme_ammesse(tipi, base, modifiche):
    """{tipo latino: [forme]} con la forma base per prima; fisse per tipo."""
    out = {}
    for t in tipi:
        rnd = random.Random(zlib.crc32(t.encode('utf-8')))
        u0 = tuple(modifiche.dividi(base[t]))
        forme = [u0]
        for _ in range(60):
            if len(forme) > VARIANTI:
                break
            u = u0
            for _ in range(rnd.choice((1, 2))):
                prova = modifiche.modifica(u, rnd)
                if modifiche.valida(prova):
                    u = prova
            if u not in forme:
                forme.append(u)
        out[t] = forme
    return out


def scrivi(struttura, messaggio, forme, giunture, beta, tau, gamma, rnd):
    dist = misure._dist_norm
    pos = 0
    pagine_out = []
    profondita = int(-tau * math.log(PESO_MINIMO))
    for righe_pagina in struttura:
        pagina = []
        for n in righe_pagina:
            riga = []
            for _ in range(n):
                w = messaggio[pos % len(messaggio)]
                pos += 1
                candidate = forme[w]
                if len(candidate) == 1 or (beta == 0 and gamma == 0):
                    scelta = rnd.choice(candidate)
                else:
                    contesto = Counter()
                    for u in riga:
                        contesto[u] += 1.0
                    for d in range(1, min(profondita, len(pagina)) + 1):
                        peso = math.exp(-d / tau)
                        for u in pagina[-d]:
                            contesto[u] += peso
                    tot = sum(contesto.values())
                    pesi = []
                    for c in candidate:
                        sim = (sum(p * (1 - dist(c, u)) for u, p in contesto.items()) / tot) if tot else 0.0
                        g = 1.0
                        if gamma and riga:
                            g = giunture.get((riga[-1][-1], c[0]), R_IGNOTA) ** gamma
                        pesi.append(math.exp(beta * sim) * g)
                    scelta = rnd.choices(candidate, weights=pesi)[0]
                riga.append(scelta)
            pagina.append(riga)
        pagine_out.append([[''.join(u) for u in r] for r in pagina])
    return pagine_out


def lista(pagine, dividi):
    """La lista di controllo dell'e22 senza ordine dei segni e anagrammi (preregistrazione)."""
    righe = [r for p in pagine for r in p]
    r = impronta(pagine, dividi)
    r['spazio_spiegato'] = misure.spazi(righe, dividi)['spiegata']
    r['confine'] = misure.confine(righe, dividi, solo_interne=True)['im_confine_eccesso']
    voc = Counter(p for rr in righe for p in rr)
    coppie = [(a, b) for rr in righe for a, b in zip(rr, rr[1:])]
    prime = [a for a, _ in coppie]
    rnd = random.Random(12)
    r['unione_attestata'] = sum(1 for a, b in coppie if voc[a + b]) / len(coppie)
    r['unione_caso'] = sum(1 for a, b in coppie if voc[rnd.choice(prime) + b]) / len(coppie)
    return r


def compatibile(r):
    return (r['identiche_vs_riga'] >= 0.7 and r['somiglianza_riga'] >= 0.03
            and r['somiglianza_6_righe'] < r['somiglianza_riga'] and r['h2'] <= 2.40
            and r['confine'] >= 0.15 and r['hapax'] >= 0.55)


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    pagine_v = pagine_voynich(corrente)
    struttura = [[len(r) for r in p] for p in pagine_v]
    modifiche = generatori.Modifiche(parole_v, glifi)
    giunture = tabella_giunture([r for p in pagine_v for r in p], glifi)
    latino = [w for _, ps in plinio() for w in ps]
    codice = generatori.codice_per_rango(latino, parole_v, generatori.ModelloParole(parole_v, glifi), random.Random(46))
    base = {}
    for w, c in zip(latino, codice):
        base.setdefault(w, c)
    forme = forme_ammesse(sorted(base), base, modifiche)
    chi = defaultdict(set)
    for t, fs in forme.items():
        for f in fs:
            chi[f].add(t)
    ris = OrderedDict()
    ris['Voynich'] = lista(pagine_v, glifi)
    ris['cifrario'] = {'tipi_latini': len(forme), 'forme_medie': sum(map(len, forme.values())) / len(forme),
                       'forme_ambigue': sum(1 for f in chi if len(chi[f]) > 1) / len(chi)}
    print('cifrario', ris['cifrario'], flush=True)
    for gamma in GAMMA:
        for tau in TAU:
            for beta in BETA:
                if beta == 0 and tau != TAU[0]:
                    continue                     # con beta 0 tau non conta
                nome = 'beta %g, tau %g, gamma %g' % (beta, tau, gamma)
                pagine = scrivi(struttura, latino, forme, giunture, beta, tau, gamma, random.Random(46))
                r = lista(pagine, glifi)
                scritte = [tuple(glifi(p)) for pg in pagine for rr in pg for p in rr]
                r['posti_ambigui'] = sum(1 for u in scritte if len(chi[u]) > 1) / len(scritte)
                r['compatibile'] = compatibile(r)
                r.update({'beta': beta, 'tau': tau, 'gamma': gamma})
                ris[nome] = r
                print('%-28s rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f hapax %.2f tipi %.3f ambigui %.2f %s' % (
                    nome, r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_6_righe'], r['h2'],
                    r['confine'], r['hapax'], r['tipi_su_parole'], r['posti_ambigui'],
                    'COMPATIBILE' if r['compatibile'] else ''), flush=True)
    with open(os.path.join(RISULTATI, 'e46_codice_accorto.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    c = ris['cifrario']
    out = ['# e46 — Il codice accorto: messaggio intero, forme equivalenti scelte per stile', '',
           'Plinio (libri 20–27) scritto parola per parola; ogni tipo latino ha fino a %d forme equivalenti '
           '(in media %.1f; %.1f%% delle forme ammesse da più tipi). Scelta ∝ exp(β·somiglianza al contesto '
           'della pagina, peso exp(−d/τ) per riga) · R_giunture^γ. Compatibile = ripetizione ≥ 0,7, somiglianza '
           'nella riga ≥ 3%% e calante, h2 ≤ 2,40, legame ≥ 0,15, parole uniche ≥ 0,55. Preregistrazione: '
           '`preregistrazioni/e46.md`.' % (VARIANTI + 1, c['forme_medie'], 100 * c['forme_ambigue']), '',
           '| testo | h2 | spazio | parole uniche | tipi/parole | ripetizione | somigl. riga | 6 righe | legame | posti ambigui | compatibile |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if nome == 'cifrario':
            continue
        out.append('| %s | %.2f | %.0f%% | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | %s | %s |' % (
            nome, r['h2'], 100 * r['spazio_spiegato'], r['hapax'], r['tipi_su_parole'], r['identiche_vs_riga'],
            100 * r['somiglianza_riga'], 100 * r['somiglianza_6_righe'], r['confine'],
            '%.0f%%' % (100 * r['posti_ambigui']) if 'posti_ambigui' in r else '—',
            'sì' if r.get('compatibile') else ''))
    with open(os.path.join(RISULTATI, 'e46_codice_accorto.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
