# -*- coding: utf-8 -*-
"""Esperimento 66: parole chiave e argomenti (misura nello spirito di Montemurro e Zanette 2013).

I(s) = somma sulle parole (n_w/N) * (H_rimescolato - H_reale) della distribuzione delle occorrenze
fra parti consecutive di s parole. Preregistrazione: preregistrazioni/e66.md.
Scrive risultati/e66_parole_chiave.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCALE = (250, 500, 1000, 2000, 4000)
N, MIN_OCC, RIMESCOLAMENTI = 34000, 10, 10
D = misure.divisore(misure.GLIFI_EVA)


def entropie(parole, s):
    per = defaultdict(Counter)
    for i, w in enumerate(parole):
        per[w][i // s] += 1
    out = {}
    for w, c in per.items():
        n = sum(c.values())
        if n >= MIN_OCC:
            out[w] = (n, -sum(k / n * math.log2(k / n) for k in c.values()))
    return out


def informazione(parole, s, rnd):
    reale = entropie(parole, s)
    acc = defaultdict(float)
    for _ in range(RIMESCOLAMENTI):
        m = parole[:]
        rnd.shuffle(m)
        for w, (n, h) in entropie(m, s).items():
            acc[w] += h / RIMESCOLAMENTI
    return sum(n / len(parole) * (acc[w] - h) for w, (n, h) in reale.items())


def da_file(percorso):
    return [w for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')
            for w in l.split()]


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    latino = [w for _, ps in plinio() for w in ps]
    testi = OrderedDict()
    testi['Voynich'] = voy
    testi['Bibbia latina'] = lingue.parole('Latin')
    testi['Plinio 20-27'] = latino
    testi['Plinio codificato'] = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(66))
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = da_file(os.path.join(e22.LAVORO, 'seme_%d' % s, 'generate', 'generated_text.txt'))
    testi['modello e51 (seme 19)'] = da_file(os.path.join(e22.LAVORO, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19',
                                                          'generate', 'generated_text.txt'))
    testi['modello e50 con recenza K 5 (seme 19)'] = da_file(os.path.join(e22.LAVORO, 'recenza_novita',
                                                                           'q_0.2_l_0.9_k_5_n_1_seme_19', 'generate',
                                                                           'generated_text.txt'))
    testi['Naibbe'] = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                           encoding='utf-8').read().split()
    ris = OrderedDict()
    for nome, parole in testi.items():
        parole = parole[:N]
        rnd = random.Random(66)
        curva = OrderedDict((s, informazione(parole, s, rnd)) for s in SCALE)
        migliore = max(curva, key=curva.get)
        ris[nome] = {'parole': len(parole), 'curva': curva, 'I_max': curva[migliore], 'scala_max': migliore}
        print('%-40s %s | I* %.3f a s=%d' % (nome, '  '.join('%d:%.3f' % kv for kv in curva.items()),
                                              curva[migliore], migliore), flush=True)
    with open(os.path.join(RISULTATI, 'e66_parole_chiave.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e66 — Parole chiave e argomenti', '',
           'I(s) in bit per parola: informazione nella distribuzione delle parole (almeno %d occorrenze) fra parti '
           'consecutive di s parole, rispetto a %d rimescolamenti. Testi troncati a %d parole. Preregistrazione: '
           '`preregistrazioni/e66.md`.' % (MIN_OCC, RIMESCOLAMENTI, N), '',
           '| testo | ' + ' | '.join('s = %d' % s for s in SCALE) + ' | I* | scala |', '|---|' + '---|' * (len(SCALE) + 2)]
    for nome, r in ris.items():
        out.append('| %s | %s | %.3f | %d |' % (nome, ' | '.join('%.3f' % r['curva'][s] for s in SCALE), r['I_max'], r['scala_max']))
    with open(os.path.join(RISULTATI, 'e66_parole_chiave.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
