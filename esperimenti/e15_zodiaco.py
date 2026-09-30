# -*- coding: utf-8 -*-
"""Esperimento 15: le etichette dello zodiaco sono numeri scritti con stili diversi?

Ogni segno dello zodiaco ha circa 30 ninfe, come i gradi di un segno o i
giorni di un mese, e ogni ninfa ha un'etichetta. Le etichette sono quasi tutte
diverse, quindi non sono gli stessi 30 nomi ripetuti tale e quale. Ma lo stile
di scrittura del Voynich cambia da pagina a pagina: potrebbero essere le
stesse 30 voci scritte ogni volta con abitudini diverse.

Se fosse cosi', l'etichetta in posizione i di un segno somiglierebbe
all'etichetta in posizione i degli altri segni, almeno dopo aver trovato il
punto di partenza giusto del cerchio. Per ogni coppia di segni cerchiamo lo
spostamento circolare che rende le etichette piu' simili, e lo confrontiamo con
lo stesso calcolo fatto su etichette rimescolate a caso dentro ogni segno.

Scrive risultati/e15_zodiaco.json e risultati/e15_zodiaco.md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
# i segni divisi su due pagine si ricompongono: Ariete e Toro
SEGNI = OrderedDict([
    ('Pesci', ['f70v2']), ('Ariete', ['f70v1', 'f71r']), ('Toro', ['f71v', 'f72r1']),
    ('Gemelli', ['f72r2']), ('Cancro', ['f72r3']), ('Leone', ['f72v3']), ('Vergine', ['f72v2']),
    ('Bilancia', ['f72v1']), ('Scorpione', ['f73r']), ('Sagittario', ['f73v']),
])
RIMESCOLAMENTI = 200


def etichette(zl):
    out = OrderedDict()
    for segno, pagine in SEGNI.items():
        lab = []
        for pag in pagine:
            lab += ['.'.join(r.parole) for r in zl if r.pagina == pag and r.tipo == 'Lz'
                    and r.parole and all(trascrizione.pulita(p) for p in r.parole)]
        out[segno] = lab
    return out


def somiglianza(a, b, dividi):
    ua, ub = tuple(dividi(a)), tuple(dividi(b))
    return 1 - misure._dist_norm(ua, ub)


def miglior_allineamento(x, y, dividi):
    """Lo spostamento circolare di y che massimizza la somiglianza media con x
    (sulle posizioni comuni), e quella somiglianza."""
    n = min(len(x), len(y))
    migliore = (-1, 0)
    for s in range(len(y)):
        m = sum(somiglianza(x[i], y[(i + s) % len(y)], dividi) for i in range(n)) / n
        if m > migliore[0]:
            migliore = (m, s)
    return migliore


def media_allineamenti(lab, dividi):
    segni = list(lab)
    valori = []
    for i in range(len(segni)):
        for j in range(i + 1, len(segni)):
            valori.append(miglior_allineamento(lab[segni[i]], lab[segni[j]], dividi)[0])
    return sum(valori) / len(valori)


def main():
    zl = trascrizione.leggi('ZL')
    glifi = misure.divisore(misure.GLIFI_EVA)
    lab = etichette(zl)
    for s, l in lab.items():
        print('%-11s %2d etichette: %s' % (s, len(l), ' '.join(l[:8])))
    vera = media_allineamenti(lab, glifi)
    rnd = random.Random(15)
    nulle = []
    for _ in range(RIMESCOLAMENTI):
        m = OrderedDict((s, rnd.sample(l, len(l))) for s, l in lab.items())
        nulle.append(media_allineamenti(m, glifi))
    nulle.sort()
    p = sum(1 for x in nulle if x >= vera) / len(nulle)
    # stessa posizione senza spostamenti (se la trascrizione parte dallo stesso punto)
    segni = list(lab)
    stessa, diversa = [], []
    for i in range(len(segni)):
        for j in range(i + 1, len(segni)):
            x, y = lab[segni[i]], lab[segni[j]]
            for a in range(min(len(x), len(y))):
                stessa.append(somiglianza(x[a], y[a], glifi))
                diversa.append(somiglianza(x[a], y[(a + len(y) // 2) % len(y)], glifi))
    ris = {'etichette': {s: l for s, l in lab.items()},
           'allineamento_migliore_medio': vera,
           'rimescolate': {'media': sum(nulle) / len(nulle), 'p95': nulle[int(0.95 * len(nulle))],
                           'massimo': nulle[-1]},
           'p': p,
           'stessa_posizione': sum(stessa) / len(stessa),
           'posizione_opposta': sum(diversa) / len(diversa)}
    print('allineamento migliore medio %.3f; rimescolate: media %.3f, 95%% %.3f, massimo %.3f; p = %.3f' % (
        vera, ris['rimescolate']['media'], ris['rimescolate']['p95'], ris['rimescolate']['massimo'], p))
    print('senza spostamenti: stessa posizione %.3f, posizione opposta %.3f' % (
        ris['stessa_posizione'], ris['posizione_opposta']))
    with open(os.path.join(RISULTATI, 'e15_zodiaco.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RISULTATI, 'e15_zodiaco.md'), 'w', encoding='utf-8') as f:
        f.write('# Esperimento 15: le etichette dello zodiaco sono numeri?\n\n'
                '%d etichette su %d segni. Per ogni coppia di segni: lo spostamento circolare che rende più '
                'simili le etichette nella stessa posizione; poi la media su tutte le coppie.\n\n'
                '| | somiglianza media |\n|---|---|\n'
                '| etichette vere, allineamento migliore | %.3f |\n'
                '| etichette rimescolate (%d volte): media | %.3f |\n'
                '| etichette rimescolate: 95° percentile | %.3f |\n\n'
                'Probabilità di un allineamento così buono per caso: p = %.3f.\n\n'
                'Senza spostamenti, stessa posizione: %.3f; posizione opposta: %.3f.\n' % (
                    sum(len(l) for l in lab.values()), len(lab), vera, RIMESCOLAMENTI,
                    ris['rimescolate']['media'], ris['rimescolate']['p95'], p,
                    ris['stessa_posizione'], ris['posizione_opposta']))


if __name__ == '__main__':
    main()
