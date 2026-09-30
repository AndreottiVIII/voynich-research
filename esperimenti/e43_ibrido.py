# -*- coding: utf-8 -*-
"""Esperimento 43: l'ibrido di D'Imperio, parole in codice piu' riempitivi copiati.

Ogni posto di parola, con probabilita' f, e' un riempitivo (copia ritoccata di una parola
vicina, come in generatori.autocitazione); altrimenti e' la parola successiva di un
messaggio vero (Plinio, libri 20-27) codificato parola per parola con parole del Voynich
(generatori.codice_per_rango). Struttura di pagine e righe del Voynich. Griglia f x lambda.

Preregistrazione: preregistrazioni/e43.md. Scrive risultati/e43_ibrido.json e .md.
"""
import itertools, json, math, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
from e10_naibbe import completa, pagine_voynich
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
F = (0.2, 0.4, 0.6, 0.8)
LAMBDA = (0.7, 1.0, 1.5)
TAU, LONTANO = 1.5, 0.05


def ibrido(struttura, messaggio, modifiche, rnd, f, lam):
    dividi = modifiche.dividi
    msg = itertools.cycle([tuple(dividi(w)) for w in messaggio])   # ciclo solo se il messaggio finisse
    scritte = []
    pagine_out = []
    for righe_pagina in struttura:
        pagina = []
        for n_parole in righe_pagina:
            riga = []
            for _ in range(n_parole):
                if (pagina or riga) and rnd.random() < f:
                    if rnd.random() < LONTANO:
                        fonte = rnd.choice(scritte)
                    else:
                        candidate = [(0, riga)] if riga else []
                        candidate += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                        _, sorgente = rnd.choices(candidate, weights=[math.exp(-d / TAU) for d, _ in candidate])[0]
                        fonte = rnd.choice(sorgente)
                    nuova = fonte
                    for _ in range(generatori.poisson(rnd, lam)):
                        prova = modifiche.modifica(nuova, rnd)
                        if modifiche.valida(prova):
                            nuova = prova
                else:
                    nuova = next(msg)
                riga.append(nuova)
                scritte.append(nuova)
            pagina.append(riga)
        pagine_out.append([[''.join(u) for u in riga] for riga in pagina])
    return pagine_out


def praticabile(r):
    return (r['identiche_vs_riga'] >= 0.8 and r['somiglianza_riga'] >= 0.03
            and r['somiglianza_6_righe'] < r['somiglianza_riga'] and r['hapax'] >= 0.60 and 2.0 <= r['h2'] <= 2.5)


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    pagine_v = pagine_voynich(corrente)
    struttura = [[len(r) for r in pag] for pag in pagine_v]
    modello = generatori.ModelloParole(parole_v, glifi)
    modifiche = generatori.Modifiche(parole_v, glifi)
    latino = [w for _, ps in plinio() for w in ps]
    messaggio = generatori.codice_per_rango(latino, parole_v, modello, random.Random(43))
    ris = OrderedDict()
    ris['Voynich (pagine e righe vere)'] = completa(pagine_v, glifi)
    ris['solo codice (f = 0)'] = completa(ibrido(struttura, messaggio, modifiche, random.Random(43), 0.0, 1.0), glifi)
    for f in F:
        for lam in LAMBDA:
            chiave = 'f %.1f, lambda %.1f' % (f, lam)
            r = completa(ibrido(struttura, messaggio, modifiche, random.Random(43), f, lam), glifi)
            r['praticabile'] = praticabile(r)
            ris[chiave] = r
            print('%-20s ident x%.2f somigl %.1f%%/%.1f%%/%.1f%% hapax %.2f h2 %.2f confine %.3f %s' % (
                chiave, r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'],
                100 * r['somiglianza_6_righe'], r['hapax'], r['h2'], r['im_confine_eccesso'],
                'PRATICABILE' if r['praticabile'] else ''), flush=True)
    with open(os.path.join(RISULTATI, 'e43_ibrido.json'), 'w', encoding='utf-8') as fh:
        json.dump(ris, fh, ensure_ascii=False, indent=1)
    out = ["# e43 — L'ibrido di D'Imperio: codice più riempitivi copiati", '',
           'f = quota di riempitivi (copie ritoccate di parole vicine); λ = modifiche medie per copia. '
           'Messaggio: Plinio, libri 20–27, codice parola per parola sul vocabolario del Voynich. '
           'Praticabile = ripetizione ≥ 0,8, somiglianza nella riga ≥ 3% e calante, parole uniche ≥ 0,60, '
           'h2 fra 2,0 e 2,5. Preregistrazione: `preregistrazioni/e43.md`.', '',
           '| testo | h2 | hapax | identiche subito | somiglianza: riga | riga sotto | 6 righe | confine | praticabile |',
           '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %.2f | %.2f | ×%.2f | %.1f%% | %.1f%% | %.1f%% | %.3f | %s |' % (
            nome, r['h2'], r['hapax'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'],
            100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe'], r['im_confine_eccesso'],
            'sì' if r.get('praticabile') else ''))
    with open(os.path.join(RISULTATI, 'e43_ibrido.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
