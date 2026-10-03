# -*- coding: utf-8 -*-
"""Esperimento 269: ricottura (harness dell'e17) sul testo fatto solo delle parole che non sono copie (classi N e A
dell'e237), lette di seguito, con lo stesso testo rimescolato come controllo nel criterio.

Preregistrazione: preregistrazioni/e269.md. Scrive risultati/e269_parole_non_copiate.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import forza_bruta, trascrizione
import e17_ricottura as e17
import e160_testo_ripulito as e160
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 269
LINGUE = OrderedDict((k, v) for k, v in e17.LINGUE.items() if v in ('latino', 'italiano', 'tedesco', 'ebraico', 'arabo'))
G = forza_bruta.G
D = e237.D
MODI = ['ripulito, segni EVA', 'solo non copiate', 'solo non copiate, rimescolato']


def classi_per_parola(pagine):
    """pagine: liste di righe di parole pulite. -> stesse strutture con la classe di ogni parola (None per la prima)."""
    tutte = Counter(w for p in pagine for r in p for w in r)
    top = {w for w, _ in tutte.most_common(200)}
    inventario = sorted({x for w in tutte for x in D(w)})
    visti_prima, out = set(), []
    for p in pagine:
        sulla, primo, cp = set(), True, []
        for r in p:
            cr = []
            for w in r:
                u = tuple(D(w))
                if primo:
                    c = None
                elif u in sulla:
                    c = 'R'
                elif e237.vicini(u, inventario) & sulla:
                    c = 'V'
                elif w in top:
                    c = 'F'
                elif w in visti_prima:
                    c = 'A'
                else:
                    c = 'N'
                primo = False
                sulla.add(u)
                cr.append((w, c))
            cp.append(cr)
        visti_prima |= {w for r in p for w in r}
        out.append(cp)
    return out


def main():
    pul = e160.ripulisci(e160.pagine_voynich())
    pagine = [[[w for w in ps if trascrizione.pulita(w)] for _, ps in p] for p in pul]
    classi = classi_per_parola(pagine)
    conta = Counter(c for p in classi for r in p for _, c in r)
    righe_nc = [[w for w, c in r if c in ('N', 'A')] for p in classi for r in p]
    righe_nc = [r for r in righe_nc if r]
    parole = [w for r in righe_nc for w in r]
    rnd = random.Random(SEME)
    mesc = parole[:]
    rnd.shuffle(mesc)
    it = iter(mesc)
    righe_m = [[next(it) for _ in r] for r in righe_nc]
    print('classi sul testo ripulito: %s; parole tenute: %d' % (dict(conta), len(parole)), flush=True)
    modi = OrderedDict([(MODI[0], e17.in_unita(forza_bruta.righe_ripulite(), G)), (MODI[1], e17.in_unita(righe_nc, G)), (MODI[2], e17.in_unita(righe_m, G))])
    ris = forza_bruta.esegui(modi, LINGUE, 'e269_parole_non_copiate', 'e269 — Solo le parole non copiate (classi N e A), con il rimescolato nel criterio',
                             'preregistrazioni/e269.md')
    candidati, righe_md = [], []
    for nome, r in ris.items():
        pos = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in MODI}
        p, c = pos[MODI[1]]
        pm, cm = pos[MODI[2]]
        if p >= 0.5 and c >= 0.5 and p - pm >= 0.3 and c - cm >= 0.3:
            candidati.append(nome)
        righe_md.append('| %s | %s |' % (nome, ' | '.join('%.2f / %.2f' % pos[m] for m in MODI)))
    esito = 'candidato, da esaminare' if candidati else 'nessuna lettura'
    md = open(os.path.join(RISULTATI, 'e269_parole_non_copiate.md'), encoding='utf-8').read()
    md += ('\n## Criterio preregistrato (con il rimescolato)\n\nParole tenute (N + A): %d; classi sul testo ripulito: %s.\n\n| lingua | ' % (len(parole), dict(conta))
           + ' | '.join(MODI) + ' |\n|---|---|---|---|\n' + '\n'.join(righe_md) + '\n\nCandidati: %s. Esito: **%s**.\n' % (candidati or 'nessuno', esito))
    open(os.path.join(RISULTATI, 'e269_parole_non_copiate.md'), 'w', encoding='utf-8').write(md)
    d = json.load(open(os.path.join(RISULTATI, 'e269_parole_non_copiate.json'), encoding='utf-8'))
    d['criterio_con_rimescolato'] = {'candidati': candidati, 'esito': esito, 'classi': dict(conta), 'parole_tenute': len(parole)}
    json.dump(d, open(os.path.join(RISULTATI, 'e269_parole_non_copiate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(esito, candidati)


if __name__ == '__main__':
    main()
