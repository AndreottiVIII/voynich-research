# -*- coding: utf-8 -*-
"""Esperimento 67: il modello senza messaggio consolidato (parametri fissati in anticipo):
Timm e Schinner + giunture (3) + composizione di forme nuove (q 0,10, lambda 0,75, con giunture)
+ recenza K 5 + scissione d 0,03; pagella intera (e61) su tre semi.

Preregistrazione: preregistrazioni/e67.md. Serve Java. Scrive risultati/e67_modello_consolidato.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e23_giunture as e23
import e50_recenza_novita as e50
import e53_scissione as e53
import e55_forma_parole as e55
import e61_pagella as e61
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
Q, LAM, K, DSC = 0.10, 0.75, 5, 0.03
SEMI = (19, 1, 2)
D = misure.divisore(misure.GLIFI_EVA)


def main():
    os.makedirs(e50.LAVORO, exist_ok=True)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    parole_file = os.path.join(e50.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(voy) + '\n')
    tabella = os.path.join(e50.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = e50.compila()
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    morbide = e53.giunture_morbide()
    ris = OrderedDict()
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    ris['Voynich'] = v
    esiti_per_seme = OrderedDict()
    for s in SEMI:
        pagine, _ = e50.genera(classi, tabella, parole_file, Q, LAM, K, s)
        pagine = e53.scindi(pagine, DSC, morbide, random.Random(67 + s))
        r = e61.scheda(pagine, D, voy, soglia_ab)
        ris['seme %d' % s] = r
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(r, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti_per_seme[s] = esiti
        print('seme %d: %d/%d %s' % (s, sum(esiti.values()), len(esiti), ' '.join(p for p, x in esiti.items() if not x)),
              flush=True)
    ris['esiti'] = esiti_per_seme
    props = list(e61.BANDE)
    out = ['# e67 — Il modello senza messaggio consolidato', '',
           'Timm e Schinner + giunture (forza 3) + forme nuove nello stile della pagina (q %.2f, λ %.2f, con giunture) + '
           'recenza K %d + scissione d %.2f. Parametri fissati prima. Bande della pagella (e61). Preregistrazione: '
           '`preregistrazioni/e67.md`.' % (Q, LAM, K, DSC), '',
           '| proprietà | Voynich | ' + ' | '.join('seme %d' % s for s in SEMI) + ' |', '|---|---|' + '---|' * len(SEMI)]
    for prop in props:
        chiave = e61.VALORI.get(prop, '')
        xv = v.get(chiave)
        celle = []
        for s in SEMI:
            x = ris['seme %d' % s].get(chiave)
            celle.append(('✓ ' if esiti_per_seme[s][prop] else '· ') + ('%.3g' % x if isinstance(x, (int, float)) else ''))
        out.append('| %s | %s | %s |' % (prop, '%.3g' % xv if isinstance(xv, (int, float)) else '', ' | '.join(celle)))
    out.append('| **totale** | | %s |' % ' | '.join('%d/%d' % (sum(esiti_per_seme[s].values()), len(props)) for s in SEMI))
    with open(os.path.join(RISULTATI, 'e67_modello_consolidato.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(RISULTATI, 'e67_modello_consolidato.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
