# -*- coding: utf-8 -*-
"""Esperimento 107: il risolutore dell'e17 sulla trascrizione ripulita dalle convenzioni grafiche (segno aggiunto a
inizio riga, gallow d'inizio paragrafo, varianti di posizione).

Preregistrazione: preregistrazioni/e107.md. Scrive risultati/e107_ripulita_risolutore.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e17_ricottura as e17

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
LEGGERA = {'sh': 'ch', 'p': 't', 'f': 'k'}
FORTE = dict(LEGGERA, **{'k': 't', 'f': 't', 'cph': 'cth', 'cfh': 'ckh', 'r': 'd', 's': 'd'})
LINGUE = OrderedDict([('Latin', 'latino'), ('Italian', 'italiano'), ('Hebrew', 'ebraico')])


def ripulita(fusione):
    righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    mezzo = Counter(w for r in righe for w in r.parole[1:-1] if trascrizione.pulita(w))
    out, tolti = [], Counter()
    for r in righe:
        ps = [p if trascrizione.pulita(p) else None for p in r.parole]
        if ps and ps[0]:
            u = D(ps[0])
            if r.inizio_par and len(u) >= 3 and u[0] in ('p', 't', 'k', 'f'):
                ps[0] = ''.join(u[1:])
                tolti['gallow di paragrafo'] += 1
            elif not r.inizio_par and len(u) >= 3 and u[0] in ('y', 'd', 's', 'o') and mezzo[''.join(u[1:])] >= 2:
                ps[0] = ''.join(u[1:])
                tolti['segno aggiunto'] += 1
        ps = [''.join(fusione.get(g, g) for g in D(p)) if p else None for p in ps]
        out.append(ps)
    return out, tolti


def modi():
    leggera, tolti = ripulita(LEGGERA)
    forte, _ = ripulita(FORTE)
    m = OrderedDict()
    m['segni EVA, pulizia + fusione leggera'] = e17.in_unita(leggera, D)
    m['segni EVA, pulizia + fusione forte'] = e17.in_unita(forte, D)
    parole = [D(p) for r in leggera for p in r if p]
    m['gruppi (50 fusioni), pulizia + fusione leggera'] = e17.in_unita(leggera, e17.applica_gruppi(e17.impara_gruppi(parole, 50), D))
    return m, tolti


def main():
    voynich, tolti = modi()
    print('tolti:', dict(tolti))
    for modo, righe in voynich.items():
        print('Voynich, %-48s simboli %3d  lunghezza %6d  righe %5d' % (modo, len({u for r in righe for u in r}), sum(map(len, righe)), len(righe)), flush=True)
    ris = OrderedDict([('tolti', dict(tolti))])
    percorso = os.path.join(RISULTATI, 'e107_ripulita_risolutore.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(e17.una_lingua, [(k, n, voynich) for k, n in LINGUE.items()]):
            ris[nome] = r
            with open(percorso, 'w', encoding='utf-8') as f:
                json.dump(ris, f, ensure_ascii=False, indent=1)
    # confronto con l'e17 (trascrizione non ripulita)
    vecchio = json.load(open(os.path.join(RISULTATI, 'e17_ricottura.json'), encoding='utf-8'))
    out = ['# e107 — La trascrizione ripulita nel risolutore', '',
           'Posizione del Voynich fra controllo negativo (0) e positivo (1); copertura a 6+ lettere. Tolti: %s. '
           'Preregistrazione: `preregistrazioni/e107.md`.' % dict(tolti), '',
           '| lingua | modo | posizione (punteggio) | posizione (copertura) | copertura 6+ del Voynich |', '|---|---|---|---|---|']
    rilevante = False
    for nome in LINGUE.values():
        r = ris[nome]
        for modo in voynich:
            pp = e17.posizione(r, modo, 'punteggio')
            pc = e17.posizione(r, modo, 'copertura')
            c6 = r[modo + ', Voynich']['copertura_6']
            out.append('| %s | %s | %.2f | %.2f | %.1f%% |' % (nome, modo, pp, pc, 100 * c6))
        if nome in vecchio:
            for modo in ('segni EVA', 'gruppi (50 fusioni)'):
                if modo + ', Voynich' in vecchio[nome]:
                    out.append('| %s | %s (e17, non ripulita) | %.2f | %.2f | %.1f%% |' % (
                        nome, modo, e17.posizione(vecchio[nome], modo, 'punteggio'), e17.posizione(vecchio[nome], modo, 'copertura'),
                        100 * vecchio[nome][modo + ', Voynich']['copertura_6']))
        base = max((e17.posizione(vecchio[nome], m, 'punteggio') for m in ('segni EVA', 'gruppi (50 fusioni)')
                    if nome in vecchio and m + ', Voynich' in vecchio[nome]), default=0)
        for modo in voynich:
            pp = e17.posizione(r, modo, 'punteggio')
            if pp >= 0.5 and pp - base >= 0.15 and r[modo + ', Voynich']['copertura_6'] >= 0.10:
                rilevante = True
    ris['miglioramento_rilevante'] = rilevante
    out += ['', 'Miglioramento rilevante: **%s**.' % ('sì' if rilevante else 'no')]
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RISULTATI, 'e107_ripulita_risolutore.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
