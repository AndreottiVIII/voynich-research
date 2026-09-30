# -*- coding: utf-8 -*-
"""Esperimento 58: la parola "di sopra". Una parola somiglia alla parola nella stessa posizione
della riga precedente piu' che alle altre parole di quella riga? (Prova del meccanismo di copia
verticale del generatore di Timm e Schinner.)

Rapporto dei totali S_sopra / S_altre (somiglianza = 1 - distanza di edit normalizzata, segni
composti fusi), per posizione assoluta e relativa; nulla: 1.000 rimescolamenti dell'ordine delle
parole della riga precedente.
Preregistrazione: preregistrazioni/e58.md. Scrive risultati/e58_parola_sopra.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
from e07_codifiche import pagine_voynich
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
RIMESCOLAMENTI = 1000


def prepara(pagine, dividi):
    """Coppie (riga, riga precedente) come liste di tuple di segni."""
    out = []
    for p in pagine:
        p = [[tuple(dividi(w)) if dividi else tuple(w) for w in r] for r in p]
        for a, b in zip(p, p[1:]):
            if len(a) >= 2 and len(b) >= 2:
                out.append((b, a))       # (riga corrente, riga sopra)
    return out


def sim(a, b):
    return 1 - misure._dist_norm(a, b)


def statistica(coppie, relativa=False, ordini=None):
    num = den = 0.0
    ident = n = 0
    for k, (riga, sopra) in enumerate(coppie):
        if ordini is not None:
            sopra = [sopra[j] for j in ordini[k]]
        L = len(sopra)
        for i, w in enumerate(riga):
            j = round(i / (len(riga) - 1) * (L - 1)) if relativa and len(riga) > 1 else i
            if j >= L:
                continue
            s = [sim(w, x) for x in sopra]
            altre = (sum(s) - s[j]) / (L - 1)
            num += s[j]
            den += altre
            ident += w == sopra[j]
            n += 1
    return num / den, ident / n


def prova(coppie, relativa, seme=58):
    oss, ident = statistica(coppie, relativa)
    rnd = random.Random(seme)
    nulle = []
    for _ in range(RIMESCOLAMENTI):
        ordini = [rnd.sample(range(len(s)), len(s)) for _, s in coppie]
        nulle.append(statistica(coppie, relativa, ordini)[0])
    nulle = np.array(nulle)
    return {'rapporto': oss, 'nulla': float(nulle.mean()), 'z': float((oss - nulle.mean()) / nulle.std(ddof=1)),
            'p': float((1 + (nulle >= oss).sum()) / (1 + RIMESCOLAMENTI)), 'identiche_sopra': ident}


def da_file(percorso):
    linee = [l.split() for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    return [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]


def main():
    testi = OrderedDict()
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    testi['Voynich'] = (pagine_voynich(corrente), D)
    for L in ('A', 'B'):
        testi['Voynich, Currier %s' % L] = (pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=L)), D)
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d (controllo positivo)' % s] = (
            da_file(os.path.join(e22.LAVORO, 'seme_%d' % s, 'generate', 'generated_text.txt')), D)
    testi['modello e51 (seme 19)'] = (da_file(os.path.join(e22.LAVORO, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19',
                                                           'generate', 'generated_text.txt')), D)
    testi['Bibbia latina (controllo negativo)'] = (misure.pagine_finte(lingue.parole('Latin')[:35000]), None)
    latino = [w for _, ps in plinio() for w in ps]
    testi['Plinio (controllo negativo)'] = (misure.pagine_finte(latino), None)
    voy = trascrizione.parole(corrente)
    codice = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(58))
    testi['codice parola per parola (controllo negativo)'] = (misure.pagine_finte(codice), D)
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    testi['Naibbe (controllo negativo)'] = (misure.pagine_finte(naibbe), D)
    ris = OrderedDict()
    for nome, (pagine, dividi) in testi.items():
        coppie = prepara(pagine, dividi)
        ris[nome] = {'coppie_di_righe': len(coppie), 'assoluta': prova(coppie, False), 'relativa': prova(coppie, True)}
        a, r = ris[nome]['assoluta'], ris[nome]['relativa']
        print('%-48s assoluta %.3f (z %.1f, p %.3f, ident %.3f)  relativa %.3f (z %.1f, p %.3f)' % (
            nome, a['rapporto'], a['z'], a['p'], a['identiche_sopra'], r['rapporto'], r['z'], r['p']), flush=True)
    with open(os.path.join(RISULTATI, 'e58_parola_sopra.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e58 — La parola "di sopra": prova del meccanismo di copia verticale', '',
           'Rapporto fra la somiglianza di una parola con quella nella stessa posizione della riga precedente e la '
           'somiglianza media con le altre parole di quella riga (rapporto dei totali). Nulla: %d rimescolamenti '
           'dell\'ordine della riga precedente. Posizione assoluta (i) e relativa (i / lunghezza). Preregistrazione: '
           '`preregistrazioni/e58.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | assoluta | z | p | identiche sopra | relativa | z | p |',
           '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        a, b = r['assoluta'], r['relativa']
        out.append('| %s | %d | %.3f | %.1f | %.3f | %.3f | %.3f | %.1f | %.3f |' % (
            nome, r['coppie_di_righe'], a['rapporto'], a['z'], a['p'], a['identiche_sopra'], b['rapporto'], b['z'], b['p']))
    with open(os.path.join(RISULTATI, 'e58_parola_sopra.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
