# -*- coding: utf-8 -*-
"""Esperimento 60: formule a distanza. Sequenze di 2-3 parole che ritornano ad almeno 10 pagine di
distanza, rispetto alle stesse pagine con le parole rimescolate dentro la pagina (20 volte).

Preregistrazione: preregistrazioni/e60.md. Scrive risultati/e60_formule.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
from e07_codifiche import pagine_voynich
from e30_elenchi_medievali import OCR, pulisci_ocr
from e36_posizione_pagina import plinio
from e58_parola_sopra import da_file

RISULTATI = os.path.join(QUI, '..', 'risultati')
L_LONTANO, VICINO = 10, 2
RIMESCOLAMENTI = 20
D = misure.divisore(misure.GLIFI_EVA)


def quote(pagine, n):
    prima = {}
    lontane = vicine = tot = 0
    for ip, p in enumerate(pagine):
        for r in p:
            for i in range(len(r) - n + 1):
                s = tuple(r[i:i + n])
                tot += 1
                if s in prima:
                    dist = ip - prima[s][-1]
                    if ip - prima[s][0] >= L_LONTANO:
                        lontane += 1
                    if dist <= VICINO:
                        vicine += 1
                    prima[s].append(ip)
                else:
                    prima[s] = [ip]
    return lontane / tot, vicine / tot


def rimescola(pagine, rnd):
    out = []
    for p in pagine:
        parole = [w for r in p for w in r]
        rnd.shuffle(parole)
        it = iter(parole)
        out.append([[next(it) for _ in r] for r in p])
    return out


def misura(pagine, seme=60):
    rnd = random.Random(seme)
    ris = {}
    for n in (2, 3):
        lo, vi = quote(pagine, n)
        nulle = [quote(rimescola(pagine, rnd), n) for _ in range(RIMESCOLAMENTI)]
        nl = sum(x[0] for x in nulle) / len(nulle)
        nv = sum(x[1] for x in nulle) / len(nulle)
        ris[n] = {'lontane': lo, 'lontane_nulla': nl, 'eccesso_lontano': lo / nl if nl else None,
                  'vicine': vi, 'vicine_nulla': nv, 'eccesso_vicino': vi / nv if nv else None}
    return ris


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    modello = generatori.ModelloParole(voy, D)
    testi = OrderedDict()
    testi['Voynich'] = pagine_voynich(corrente)
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = da_file(os.path.join(e22.LAVORO, 'seme_%d' % s, 'generate', 'generated_text.txt'))
    testi['modello e51, seme 19'] = da_file(os.path.join(e22.LAVORO, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19',
                                                        'generate', 'generated_text.txt'))
    contenuto = OrderedDict()
    contenuto['Bibbia latina'] = lingue.parole('Latin')[:35000]
    contenuto['Plinio 20-27'] = [w for _, ps in plinio() for w in ps]
    for nome, (f, sha, a, b) in OCR.items():
        contenuto[nome] = pulisci_ocr(f, sha, a, b)[0][:35000]
    contenuto['Apicio (ricette)'] = lingue.genere('Apicio, ricette di cucina')[:35000]
    for nome, parole in contenuto.items():
        testi[nome] = misure.pagine_finte(parole)
        testi[nome + ', codificato'] = misure.pagine_finte(generatori.codice_per_rango(parole, voy, modello, random.Random(60)))
    ris = OrderedDict()
    for nome, pagine in testi.items():
        ris[nome] = misura(pagine)
        r = ris[nome]
        print('%-52s coppie: lontano x%.2f vicino x%.2f | terne: lontano x%s vicino x%s' % (
            nome, r[2]['eccesso_lontano'] or 0, r[2]['eccesso_vicino'] or 0,
            '%.2f' % r[3]['eccesso_lontano'] if r[3]['eccesso_lontano'] else '—',
            '%.2f' % r[3]['eccesso_vicino'] if r[3]['eccesso_vicino'] else '—'), flush=True)
    with open(os.path.join(RISULTATI, 'e60_formule.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e60 — Formule a distanza', '',
           'Quota delle sequenze di n parole (nella stessa riga) già comparse almeno %d pagine prima ("lontane") o '
           'entro %d pagine ("vicine"), divisa per la stessa quota con le parole rimescolate dentro ogni pagina '
           '(media di %d). Preregistrazione: `preregistrazioni/e60.md`.' % (L_LONTANO, VICINO, RIMESCOLAMENTI), '',
           '| testo | coppie lontane | coppie vicine | terne lontane | terne vicine |', '|---|---|---|---|---|']
    f2 = lambda x: '×%.2f' % x if x else '—'
    for nome, r in ris.items():
        out.append('| %s | %s | %s | %s | %s |' % (nome, f2(r[2]['eccesso_lontano']), f2(r[2]['eccesso_vicino']),
                                                   f2(r[3]['eccesso_lontano']), f2(r[3]['eccesso_vicino'])))
    with open(os.path.join(RISULTATI, 'e60_formule.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
