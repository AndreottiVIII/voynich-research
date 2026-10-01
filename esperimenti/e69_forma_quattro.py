# -*- coding: utf-8 -*-
"""Esperimento 69: filtro di forma su 2 o 4 posizioni (primo, secondo, penultimo, ultimo segno),
eta 0,5 o 1, lambda 0,6 o 0,75, sopra il modello e51. Pagella (e61).

Preregistrazione: preregistrazioni/e69.md. Serve Java. Scrive risultati/e69_forma_quattro.json e .md.
"""
import json, os, subprocess, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e55_forma_parole as e55
import e61_pagella as e61
import e68_filtro_forma as e68
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
POSIZIONI = {2: (('i', 0), ('f', -1)), 4: (('i', 0), ('s', 1), ('p', -2), ('f', -1))}
ETA = (0.5, 1.0)
LAMBDA = (0.6, 0.75)
SEMI = (19, 1, 2)
D = misure.divisore(misure.GLIFI_EVA)
BERSAGLI = ('forma parole', 'spazio', 'omogeneità')
FUORI = ('profilo pagina', 'lunghezze vicine', 'verticale', 'formule', 'deriva', 'Zipf', 'unioni')


def tabella(voy, base, posizioni, percorso):
    righe = []
    for etichetta, pos in posizioni:
        cv = Counter(D(w)[pos] for w in voy if len(D(w)) >= 2)
        cb = Counter(D(w)[pos] for w in base if len(D(w)) >= 2)
        nv, nb = sum(cv.values()), sum(cb.values())
        for g in sorted(set(cv) | set(cb)):
            righe.append('%s\t%s\t%.5f' % (etichetta, g, (cv[g] / nv + 1e-4) / (cb[g] / nb + 1e-4)))
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(righe) + '\n')


def main():
    e68.LAVORO = os.path.join(e22.LAVORO, 'forma_quattro')
    os.makedirs(e68.LAVORO, exist_ok=True)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    parole_file = os.path.join(e68.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(voy) + '\n')
    giunture = os.path.join(e68.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(giunture)
    base = [w for l in open(e68.BASE_E51 % 19, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')
            for w in l.split()]
    classi = e68.compila()
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    ris = OrderedDict()
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    ris['Voynich'] = v
    medie = OrderedDict()
    for npos, posizioni in POSIZIONI.items():
        forma_file = os.path.join(e68.LAVORO, 'forma_%d.tsv' % npos)
        tabella(voy, base, posizioni, forma_file)
        for eta in ETA:
            for lam in LAMBDA:
                e68.LAM = lam
                nome = '%d posizioni, eta %.1f, lambda %.2f' % (npos, eta, lam)
                gruppo, bloccata = [], False
                for s in SEMI:
                    try:
                        pagine, _ = e68.genera(classi, giunture, parole_file, forma_file, eta, s)
                    except subprocess.CalledProcessError:
                        bloccata = True
                        break
                    r = e61.scheda(pagine, D, voy, soglia_ab)
                    ris['%s, seme %d' % (nome, s)] = r
                    gruppo.append(r)
                if bloccata:
                    medie[nome] = {'bloccata': True}
                    print('%-36s BLOCCATA' % nome, flush=True)
                    continue
                chiavi = [c for c, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(c), (int, float)) for g in gruppo)]
                m = {c: sum(g[c] for g in gruppo) / len(gruppo) for c in chiavi}
                esiti = OrderedDict()
                for prop, f in e61.BANDE.items():
                    try:
                        esiti[prop] = bool(f(m, v))
                    except (KeyError, TypeError, ZeroDivisionError):
                        esiti[prop] = False
                m['esiti'] = esiti
                medie[nome] = m
                print('%-36s %d/17 | bersagli %s | fuori %d/%d | forma %.2f spazio %.2f omog %.3f h2 %.2f rip %.2f R %.2f lungh %.3f' % (
                    nome, sum(esiti.values()), ''.join('✓' if esiti[p] else '·' for p in BERSAGLI),
                    sum(esiti[p] for p in FUORI), len(FUORI), m.get('V8_forma', 0), m['spazio_spiegato'],
                    m['somiglianza_riga'], m['h2'], m['identiche_vs_riga'], m['V3_R'] or 0,
                    m['V6_autocorrelazione_lunghezze']), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e69_forma_quattro.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE)
    out = ['# e69 — Filtro di forma su quattro posizioni', '',
           'Modello e51 con filtro di forma (D-011). Medie su tre semi. Bersagli: %s; fuori campione: %s. '
           'Preregistrazione: `preregistrazioni/e69.md`.' % (', '.join(BERSAGLI), ', '.join(FUORI)), '',
           '| combinazione | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        if m.get('bloccata'):
            out.append('| %s | bloccata | %s |' % (nome, ' | '.join('' for _ in props)))
            continue
        out.append('| %s | %d/17 | %s |' % (nome, sum(m['esiti'].values()), ' | '.join(
            ('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e69_forma_quattro.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
