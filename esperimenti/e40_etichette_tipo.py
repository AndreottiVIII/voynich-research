# -*- coding: utf-8 -*-
"""Esperimento 40: il tipo di oggetto etichettato cambia la forma dell'etichetta, a parita' di pagina?

Nella stessa pagina ci sono etichette di oggetti diversi: recipienti (Lc) e frammenti di
pianta (Lf) nella farmacia, ninfe (Ln) e vasche (Lt) nella sezione biologica, stelle (Ls)
e altre etichette nell'astronomia. Se la classe dell'oggetto entra nella forma del nome,
il primo o l'ultimo segno dipendono dal tipo anche a parita' di pagina; se le etichette
di una pagina sono uno stile di lotto, no. Rimescolamento dei tipi dentro la pagina.

Prima del Voynich, stima della potenza sugli stessi schemi di pagina.
Preregistrazione: preregistrazioni/e40.md. Scrive risultati/e40_etichette_tipo.json e .md.
"""
import json, os, random, sys
from collections import Counter

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
DIVIDI = misure.divisore(misure.GLIFI_EVA)
RIMESCOLAMENTI = 1000
SIMULAZIONI = 200
RIMESCOLAMENTI_POTENZA = 200   # per la sola stima della potenza, per stare nei tempi
FORZA = 0.3
CONFRONTI = [('farmacia: recipienti / frammenti', {'Lc': 'recipiente', 'Lf': 'frammento'}),
             ('biologica: ninfe / vasche', {'Ln': 'ninfa', 'Lt': 'vasca'}),
             ('astronomia: stelle / altre', {'Ls': 'stella', 'L0': 'altra', 'La': 'altra'})]
POSIZIONI = {'primo': 0, 'ultimo': -1}


def etichette(tipi):
    """[(pagina, tipo, segni)] delle etichette di quei tipi, sulle pagine con almeno due tipi."""
    out = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo in tipi:
            for w in r.parole:
                if trascrizione.pulita(w) and len(DIVIDI(w)) >= 2:
                    out.append((r.pagina, tipi[r.tipo], DIVIDI(w)))
    per_pagina = {}
    for pag, tipo, _ in out:
        per_pagina.setdefault(pag, set()).add(tipo)
    return [e for e in out if len(per_pagina[e[0]]) >= 2]


def _mi(a, b):
    ca, cb = Counter(a), Counter(b)
    cj = Counter(zip(a, b))
    n = len(a)
    return sum(c / n * np.log2(c * n / (ca[x] * cb[y])) for (x, y), c in cj.items())


def prova(dati, pos, rnd, rimescolamenti=RIMESCOLAMENTI):
    """Informazione tipo/segno in pos, contro i tipi rimescolati dentro ogni pagina."""
    tipi = [t for _, t, _ in dati]
    segni = [s[pos] for _, _, s in dati]
    indici = {}
    for i, (pag, _, _) in enumerate(dati):
        indici.setdefault(pag, []).append(i)
    oss = _mi(tipi, segni)
    nulle = []
    for _ in range(rimescolamenti):
        perm = list(tipi)
        for idx in indici.values():
            valori = [tipi[i] for i in idx]
            rnd.shuffle(valori)
            for i, v in zip(idx, valori):
                perm[i] = v
        nulle.append(_mi(perm, segni))
    nulle = np.array(nulle)
    return {'I': oss, 'nulla': float(nulle.mean()), 'eccesso': oss - float(nulle.mean()),
            'z': (oss - nulle.mean()) / nulle.std(ddof=1) if nulle.std() > 0 else 0.0,
            'p': float((1 + (nulle >= oss - 1e-12).sum()) / (1 + len(nulle)))}


def sintetiche(dati, pos, rnd):
    """Stessi schemi di pagina; con probabilita' FORZA il segno in pos dipende dal tipo,
    altrimenti l'etichetta e' presa a caso fra quelle vere della stessa pagina."""
    frequenti = [g for g, _ in Counter(s[pos] for _, _, s in dati).most_common()]
    tipi = sorted({t for _, t, _ in dati})
    marca = {t: frequenti[i % len(frequenti)] for i, t in enumerate(tipi)}
    per_pagina = {}
    for pag, _, s in dati:
        per_pagina.setdefault(pag, []).append(s)
    out = []
    for pag, t, _ in dati:
        s = list(rnd.choice(per_pagina[pag]))
        if rnd.random() < FORZA:
            s[pos] = marca[t]
        out.append((pag, t, s))
    return out


def main():
    ris = {}
    rnd = random.Random(40)
    for nome, tipi in CONFRONTI:
        dati = etichette(tipi)
        voce = {'etichette': len(dati), 'pagine': len({p for p, _, _ in dati}),
                'per_tipo': dict(Counter(t for _, t, _ in dati)),
                'lunghezza_media': {t: float(np.mean([len(s) for _, tt, s in dati if tt == t]))
                                    for t in sorted({t for _, t, _ in dati})}}
        for pnome, pos in POSIZIONI.items():
            # potenza: quante volte il test trova un effetto di forza FORZA, a p < 0,01
            riusciti = sum(prova(sintetiche(dati, pos, rnd), pos, rnd, RIMESCOLAMENTI_POTENZA)['p'] < 0.01
                           for _ in range(SIMULAZIONI))
            voce[pnome] = prova(dati, pos, rnd)
            voce[pnome]['potenza'] = riusciti / SIMULAZIONI
            voce[pnome]['iniziali_per_tipo'] = {
                t: Counter(s[pos] for _, tt, s in dati if tt == t).most_common(5)
                for t in sorted({t for _, t, _ in dati})}
            print('%-36s %-6s eccesso %.4f  z %.1f  p %.3f  potenza %.2f' % (
                nome, pnome, voce[pnome]['eccesso'], voce[pnome]['z'], voce[pnome]['p'], voce[pnome]['potenza']),
                flush=True)
        ris[nome] = voce
    with open(os.path.join(RISULTATI, 'e40_etichette_tipo.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ['# e40 — Tipo di oggetto e forma dell\'etichetta, a parità di pagina', '',
             'Informazione mutua fra tipo di etichetta e segno, contro %d rimescolamenti dei tipi dentro '
             'ogni pagina. Potenza: quota di %d simulazioni (stessi schemi di pagina, il tipo fissa il '
             'segno con probabilità %.1f) in cui il test trova p < 0,01.' % (RIMESCOLAMENTI, SIMULAZIONI, FORZA), '',
             '| confronto | etichette | pagine | posizione | eccesso (bit) | z | p | potenza | segni più frequenti per tipo |',
             '|---|---|---|---|---|---|---|---|---|']
    for nome, v in ris.items():
        for pnome in POSIZIONI:
            x = v[pnome]
            iniz = '; '.join('%s: %s' % (t, ' '.join('%s %d' % gc for gc in lst[:3]))
                             for t, lst in x['iniziali_per_tipo'].items())
            righe.append('| %s | %d | %d | %s | %.4f | %.1f | %.3f | %.2f | %s |' % (
                nome, v['etichette'], v['pagine'], pnome, x['eccesso'], x['z'], x['p'], x['potenza'], iniz))
    with open(os.path.join(RISULTATI, 'e40_etichette_tipo.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


def per_lunghezza():
    """Esplorativo (non preregistrato): le etichette dei recipienti sono piu' lunghe; l'effetto
    sull'ultimo segno resta se il rimescolamento avviene dentro pagina x classe di lunghezza?"""
    rnd = random.Random(41)
    ris = {}
    for nome, tipi in CONFRONTI[:1]:
        dati = etichette(tipi)
        for classi in ((2, 5, 7, 99), (2, 4, 5, 6, 7, 8, 99)):
            def classe(n):
                return next(i for i, c in enumerate(classi[1:]) if n < c)
            strati = [('%s|%d' % (pag, classe(len(s))), t, s) for pag, t, s in dati]
            for pnome, pos in POSIZIONI.items():
                r = prova(strati, pos, rnd)
                ris['%s, classi %s, %s' % (nome, classi[1:-1], pnome)] = r
                print('%-60s eccesso %.4f  z %.1f  p %.3f' % (
                    '%s, classi di lunghezza %s, %s' % (nome, classi[1:-1], pnome), r['eccesso'], r['z'], r['p']))
    with open(os.path.join(RISULTATI, 'e40_etichette_tipo_lunghezza.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ["# e40, esplorativo: l'effetto resta a parità di pagina e di lunghezza?", '',
             'Rimescolamento dei tipi dentro pagina × classe di lunghezza (in segni). Non preregistrato.', '',
             '| prova | eccesso (bit) | z | p |', '|---|---|---|---|']
    righe += ['| %s | %.4f | %.1f | %.3f |' % (k, v['eccesso'], v['z'], v['p']) for k, v in ris.items()]
    with open(os.path.join(RISULTATI, 'e40_etichette_tipo_lunghezza.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    if '--lunghezza' in sys.argv:
        per_lunghezza()
    else:
        main()
