# -*- coding: utf-8 -*-
"""Esperimento 39: riconciliare h2 con Rozanova e Temerev (2026, arXiv 2608.17096).

Loro: h2 = 2,7 bit per il Voynich contro circa 3,5 per latino, italiano, inglese.
Noi (e01): 2,2 contro 2,6-3,3. Si calcola h2 con cinque ricette sullo stesso testo
(ZL, paragrafi, parole pulite) e sugli stessi controlli, tutti troncati allo stesso
numero di simboli del Voynich in quella ricetta. Preregistrazione: preregistrazioni/e39.md.

Scrive risultati/e39_h2_arxiv.json e .md.
"""
import json, os, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')

FUSI_NOSTRI = misure.GLIFI_EVA                                 # cth ckh cph cfh ch sh
FUSI_LORO = misure.GLIFI_EVA + ['iin', 'in', 'ee']            # la loro "composite-collapsed"

RICETTE = [
    # nome, segni fusi (solo Voynich), spazio come simbolo
    ('nostra: fusi 6, con spazi', FUSI_NOSTRI, True),
    ('fusi 6, senza spazi', FUSI_NOSTRI, False),
    ('loro: fusi 9, senza spazi', FUSI_LORO, False),
    ('fusi 9, con spazi', FUSI_LORO, True),
    ('EVA scomposto, senza spazi', None, False),
]

CONTROLLI = [('latino (Bibbia)', lambda: lingue.parole('Latin')),
             ('italiano (Bibbia)', lambda: lingue.parole('Italian')),
             ('inglese (Bibbia)', lambda: lingue.parole('English')),
             ('Isidoro XVII, piante', lambda: lingue.genere('Isidoro XVII, piante')),
             ('Columella XII, ricette', lambda: lingue.genere('Columella XII, conserve e ricette'))]


def flusso(parole, dividi, spazio):
    return misure.sequenza(parole, dividi, spazio=spazio)


def main():
    parole_v = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    testi = {nome: f() for nome, f in CONTROLLI}
    ris = {'parole_voynich': len(parole_v), 'ricette': {}}
    for nome, fusi, spazio in RICETTE:
        dividi = misure.divisore(fusi) if fusi else None
        seq_v = flusso(parole_v, dividi, spazio)
        n = len(seq_v)
        riga = {'simboli_voynich': n, 'voynich': misure.condizionate(seq_v, k_max=2)}
        for c, parole in testi.items():
            seq = flusso(parole, None, spazio)
            if len(seq) < n:
                riga[c] = {'nota': 'testo troppo corto: %d simboli' % len(seq)}
                continue
            riga[c] = misure.condizionate(seq[:n], k_max=2)
        ris['ricette'][nome] = riga
        print('%-30s n=%d  Voynich h2 %.3f  | %s' % (
            nome, n, riga['voynich']['h2'],
            '  '.join('%s %.3f' % (c.split(' ')[0], riga[c]['h2']) for c in testi if 'h2' in riga[c])))
    os.makedirs(RISULTATI, exist_ok=True)
    with open(os.path.join(RISULTATI, 'e39_h2_arxiv.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ['# e39 — h2 con cinque ricette', '',
             'Testo in paragrafi ZL, %d parole pulite. Ogni controllo è troncato allo stesso numero '
             'di simboli del Voynich in quella ricetta. h2 in bit, stima diretta.' % len(parole_v), '',
             '| ricetta | simboli | Voynich | ' + ' | '.join(testi) + ' | distacco minimo |',
             '|---|---|---|' + '---|' * len(testi) + '---|']
    for nome, riga in ris['ricette'].items():
        h = [riga[c]['h2'] for c in testi if 'h2' in riga[c]]
        righe.append('| %s | %d | %.2f | %s | %.2f |' % (
            nome, riga['simboli_voynich'], riga['voynich']['h2'],
            ' | '.join('%.2f' % riga[c]['h2'] if 'h2' in riga[c] else '—' for c in testi),
            min(h) - riga['voynich']['h2']))
    with open(os.path.join(RISULTATI, 'e39_h2_arxiv.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
