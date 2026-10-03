# -*- coding: utf-8 -*-
"""Esperimento 249: ricottura (harness dell'e17) con i pezzi delle parole come simboli (segmentazione di Viterbi su un
lessico di n-grammi di unita'), con il testo a parole rimescolate come controllo dentro il criterio.

Preregistrazione: preregistrazioni/e249.md. Scrive risultati/e249_pezzi_simboli.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import forza_bruta
import e17_ricottura as e17

RISULTATI = os.path.join(QUI, '..', 'risultati')
LESSICO, N_MAX, PENALITA, SEME = 150, 4, 2.0, 249
LINGUE = OrderedDict((k, v) for k, v in e17.LINGUE.items() if v in ('latino', 'italiano', 'tedesco', 'ebraico', 'arabo'))
G = forza_bruta.G
MODI = ['ripulito, segni EVA', 'pezzi', 'pezzi, rimescolato']


def segmentatore(parole):
    conta = Counter()
    for w in parole:
        u = G(w)
        for n in range(1, N_MAX + 1):
            for i in range(len(u) - n + 1):
                conta[tuple(u[i:i + n])] += 1
    lessico = {x for x, _ in conta.most_common(LESSICO)} | {x for x in conta if len(x) == 1}
    tot = sum(conta[x] for x in lessico)
    lp = {x: math.log(conta[x] / tot) - PENALITA for x in lessico}

    def taglia(w):
        u = tuple(G(w))
        best = [(0.0, [])] + [(-1e18, None)] * len(u)
        for i in range(1, len(u) + 1):
            for n in range(1, min(N_MAX, i) + 1):
                x = u[i - n:i]
                if x in lp and best[i - n][1] is not None and best[i - n][0] + lp[x] > best[i][0]:
                    best[i] = (best[i - n][0] + lp[x], best[i - n][1] + [''.join(x)])
        return best[len(u)][1]
    return taglia


def main():
    righe = forza_bruta.righe_ripulite()
    parole = [w for r in righe for w in r if w]
    taglia = segmentatore(parole)
    rnd = random.Random(SEME)
    mesc = parole[:]
    rnd.shuffle(mesc)
    it = iter(mesc)
    righe_m = [[next(it) if w else None for w in r] for r in righe]
    modi = OrderedDict([(MODI[0], e17.in_unita(righe, G)), (MODI[1], e17.in_unita(righe, taglia)), (MODI[2], e17.in_unita(righe_m, taglia))])
    esempi = [' '.join('|'.join(taglia(w)) for w in parole[i:i + 6]) for i in (0, 500, 5000)]
    print('esempi di segmentazione:', esempi, flush=True)
    ris = forza_bruta.esegui(modi, LINGUE, 'e249_pezzi_simboli', 'e249 — Pezzi delle parole come simboli, con il rimescolato nel criterio',
                             'preregistrazioni/e249.md')
    candidati = []
    righe_md = []
    for nome, r in ris.items():
        pos = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in MODI}
        p, c = pos['pezzi']
        pm, cm = pos['pezzi, rimescolato']
        if p >= 0.5 and c >= 0.5 and p - pm >= 0.3 and c - cm >= 0.3:
            candidati.append(nome)
        righe_md.append('| %s | %s |' % (nome, ' | '.join('%.2f / %.2f' % pos[m] for m in MODI)))
    esito = 'candidato, da esaminare' if candidati else 'nessuna lettura'
    md = open(os.path.join(RISULTATI, 'e249_pezzi_simboli.md'), encoding='utf-8').read()
    md += '\n## Criterio preregistrato (con il rimescolato)\n\n| lingua | ' + ' | '.join(MODI) + ' |\n|---|---|---|---|\n' + '\n'.join(righe_md)
    md += '\n\nEsempi di segmentazione: %s.\n\nCandidati secondo il criterio con il rimescolato: %s. Esito: **%s**.\n' % (' ; '.join(esempi), candidati or 'nessuno', esito)
    open(os.path.join(RISULTATI, 'e249_pezzi_simboli.md'), 'w', encoding='utf-8').write(md)
    d = json.load(open(os.path.join(RISULTATI, 'e249_pezzi_simboli.json'), encoding='utf-8'))
    d['criterio_con_rimescolato'] = {'candidati': candidati, 'esito': esito, 'esempi_segmentazione': esempi}
    json.dump(d, open(os.path.join(RISULTATI, 'e249_pezzi_simboli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(esito, candidati)


if __name__ == '__main__':
    main()
