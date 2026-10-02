# -*- coding: utf-8 -*-
"""Esperimento 212: ricottura simulata (risolutore omofonico dell'e17) sul testo ripulito dall'involucro di riga,
in 14 lingue, con controlli positivi e negativi per ogni modo.

Preregistrazione: preregistrazioni/e212.md. Scrive risultati/e212_forza_bruta_ripulito.json e .md.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e17_ricottura as e17
import e160_testo_ripulito as e160

RISULTATI = os.path.join(QUI, '..', 'risultati')
MODI = ['grezzo, segni EVA', 'ripulito, segni EVA', 'ripulito, gruppi (20 fusioni)', 'ripulito, gruppi (50 fusioni)']


def modi():
    glifi = misure.divisore(misure.GLIFI_EVA)
    pagine = e160.pagine_voynich()
    pul = e160.ripulisci(pagine)
    grezzo = [[w if trascrizione.pulita(w) else None for w in ps] for p in pagine for _, ps in p]
    ripulito = [[w if trascrizione.pulita(w) else None for w in ps] for p in pul for _, ps in p]
    parole = [glifi(w) for r in ripulito for w in r if w]
    out = OrderedDict()
    out[MODI[0]] = e17.in_unita(grezzo, glifi)
    out[MODI[1]] = e17.in_unita(ripulito, glifi)
    for f, nome in ((20, MODI[2]), (50, MODI[3])):
        out[nome] = e17.in_unita(ripulito, e17.applica_gruppi(e17.impara_gruppi(parole, f), glifi))
    return out


def main():
    voynich = modi()
    for modo, righe in voynich.items():
        print('Voynich, %-30s simboli %3d lunghezza %6d righe %5d' % (modo, len({u for r in righe for u in r}), sum(map(len, righe)), len(righe)), flush=True)
    lavori = [(k, n, voynich) for k, n in e17.LINGUE.items()]
    ris = OrderedDict()
    percorso = os.path.join(RISULTATI, 'e212_forza_bruta_ripulito.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(e17.una_lingua, lavori):
            ris[nome] = r
            json.dump(ris, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    candidati = []
    righe_md = []
    for nome, r in ris.items():
        pos = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in MODI}
        for m in MODI[1:]:
            p, c = pos[m]
            if p >= 0.5 and c >= 0.5 and p - pos[MODI[0]][0] >= 0.2:
                candidati.append((nome, m, p, c))
        righe_md.append('| %s | %s |' % (nome, ' | '.join('%.2f / %.2f' % pos[m] for m in MODI)))
        print('%-12s %s' % (nome, ' | '.join('%s %.2f/%.2f' % (m.split(',')[0][:4] + m.split(',')[1][:8], *pos[m]) for m in MODI)), flush=True)
    esito = 'lettura plausibile, da esaminare' if candidati else 'nessuna lettura'
    out = {'lingue': ris, 'candidati': candidati, 'esito': esito}
    json.dump(out, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e212 — Forza bruta sul testo ripulito', '', 'Posizione del Voynich fra controllo negativo (0) e positivo (1): punteggio / copertura con parole di almeno 6 lettere. '
          'Preregistrazione: `preregistrazioni/e212.md`.', '', '| lingua | ' + ' | '.join(MODI) + ' |', '|---|' + '---|' * len(MODI)] + righe_md
    md += ['', 'Candidati: %s. Esito: **%s**.' % (candidati or 'nessuno', esito), '', 'Esempi decifrati (modo ripulito, segni EVA), solo descrittivi:', '']
    for nome, r in ris.items():
        v = r.get(MODI[1] + ', Voynich', {})
        md.append('- %s: %s' % (nome, ' / '.join(v.get('esempio', [])[:2])[:160]))
    open(os.path.join(RISULTATI, 'e212_forza_bruta_ripulito.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, candidati)


if __name__ == '__main__':
    main()
