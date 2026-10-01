# -*- coding: utf-8 -*-
"""Esperimento 113: il Voynich come lingua monosillabica? Confronto con vietnamita e cinese (pinyin con e senza toni,
caratteri) sulle misure "a sillabe" dell'e111.

Preregistrazione: preregistrazioni/e113.md. Scrive risultati/e113_monosillabiche.json e .md.
"""
import json, os, re, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e111_parole_sillabe as e111

RISULTATI = os.path.join(QUI, '..', 'risultati')
MISURE = ('classi', 'quota_classi_uniche', 'h1', 'h2', 'zipf', 'ripetizione')


def a_righe(unita, n=9):
    return [unita[i:i + n] for i in range(0, len(unita), n)]


def identiche_vs_riga(righe):
    """Ripetizione immediata rispetto all'attesa dentro la riga (come l'e09): quota di coppie vicine uguali /
    quota di coppie qualsiasi uguali nella stessa riga."""
    vic = sum(a == b for r in righe for a, b in zip(r, r[1:])) / max(1, sum(len(r) - 1 for r in righe if r))
    tot = uguali = 0
    for r in righe:
        c = Counter(r)
        n = len(r)
        tot += n * (n - 1) / 2
        uguali += sum(k * (k - 1) / 2 for k in c.values())
    return vic / (uguali / tot) if uguali else None


def compatibile(v, x):
    out = {}
    for m in ('classi', 'quota_classi_uniche', 'h1', 'h2'):
        out[m] = abs(x[m] - v[m]) <= 0.2 * abs(v[m])
    out['zipf'] = abs(x['zipf'] - v['zipf']) <= 0.15
    out['ripetizione'] = 0.5 <= x['ripetizione'] / v['ripetizione'] <= 2 if v['ripetizione'] else False
    return out


def main():
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))]
    voy = [r for r in voy if r]
    ris = OrderedDict()
    for k, L in enumerate(('N0', 'N1', 'N2')):
        rr = e111.tronca([[e111.normalizza(w, k) for w in r] for r in voy])
        s = e111.statistiche(rr)
        s['identiche_vs_riga'] = identiche_vs_riga(rr)
        ris['Voynich ' + L] = s
    flussi = OrderedDict()
    flussi['vietnamita'] = lingue.parole('Vietnamese')
    py = lingue.parole('Chinese-pinyin')
    flussi['cinese pinyin con toni'] = py
    flussi['cinese pinyin senza toni'] = [re.sub(r'\d', '', s) for s in py]
    testo = open(os.path.join(lingue.CACHE, 'Chinese.txt'), encoding='utf-8').read()
    flussi['cinese caratteri'] = [c for c in testo if not c.isspace()]
    for chiave, nome in (('Latin', 'sillabe latine'), ('Italian', 'sillabe italiane')):
        ps = lingue.parole(chiave)[:40000]
        flussi[nome] = [s for w in ps for s in generatori.sillabe(w)]
    for nome, u in flussi.items():
        rr = e111.tronca(a_righe(u))
        s = e111.statistiche(rr)
        s['identiche_vs_riga'] = identiche_vs_riga(rr)
        comp = {}
        for L in ('N0', 'N1', 'N2'):
            c = compatibile(ris['Voynich ' + L], s)
            comp[L] = (sum(c.values()), [m for m, ok in c.items() if ok])
        migliore = max(comp, key=lambda L: comp[L][0])
        s['compatibilita'] = comp
        s['migliore'] = (migliore, comp[migliore][0])
        ris[nome] = s
    for nome, r in ris.items():
        print('%-26s classi %5d uniche %.2f h1 %.2f h2 %.2f zipf %.2f rip %.4f id/riga %.2f %s' % (
            nome, r['classi'], r['quota_classi_uniche'], r['h1'], r['h2'], r['zipf'], r['ripetizione'], r['identiche_vs_riga'] or 0,
            '| migliore %s %d/6 %s' % (r['migliore'][0], r['migliore'][1], r['compatibilita'][r['migliore'][0]][1]) if 'migliore' in r else ''), flush=True)
    vicine = [n for n, r in ris.items() if 'migliore' in r and r['migliore'][1] >= 5]
    ris['vicine'] = vicine
    print('vicine (>=5/6):', vicine)
    with open(os.path.join(RISULTATI, 'e113_monosillabiche.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e113 — Una lingua monosillabica?', '', 'Prime 30.000 unità, righe di 9 (Voynich: righe vere). Preregistrazione: '
           '`preregistrazioni/e113.md`.', '', '| flusso | classi | uniche | h1 | h2 | Zipf | ripetizione | identiche/riga | compatibilità migliore |',
           '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        comp = '%s: %d/6 (%s)' % (r['migliore'][0], r['migliore'][1], ', '.join(r['compatibilita'][r['migliore'][0]][1])) if 'migliore' in r else '–'
        out.append('| %s | %d | %.2f | %.2f | %.2f | %.2f | %.4f | %.2f | %s |' % (nome, r['classi'], r['quota_classi_uniche'], r['h1'], r['h2'],
                                                                           r['zipf'], r['ripetizione'], r['identiche_vs_riga'] or 0, comp))
    out += ['', 'Vicine (≥ 5/6): **%s**.' % (', '.join(vicine) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e113_monosillabiche.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
