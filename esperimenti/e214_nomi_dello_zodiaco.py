# -*- coding: utf-8 -*-
"""Esperimento 214: una chiave che fa leggere il nome del segno o del mese sulle pagine dello zodiaco, contro
assegnazioni permutate dei nomi alle pagine; chiavi omofoniche e biunivoche; controllo con nomi cifrati inseriti.

Preregistrazione: preregistrazioni/e214.md. Scrive risultati/e214_nomi_dello_zodiaco.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
RIPARTENZE, PERMUTAZIONI = 150, 200
PAGINE = OrderedDict([
    ('f70v2', ('pisces', 'martius', 'mars', 'marzo', 'merz')),
    ('f70v1', ('aries', 'aprilis', 'abril', 'aprile', 'april')),
    ('f71r', ('aries', 'aprilis', 'abril', 'aprile', 'april')),
    ('f71v', ('taurus', 'maius', 'may', 'maggio', 'mai')),
    ('f72r1', ('taurus', 'maius', 'may', 'maggio', 'mai')),
    ('f72r2', ('gemini', 'iunius', 'yony', 'giugno', 'iuni')),
    ('f72r3', ('cancer', 'iulius', 'iollet', 'luglio', 'iuli')),
    ('f72v3', ('leo', 'augustus', 'augst', 'agosto', 'august')),
    ('f72v2', ('uirgo', 'september', 'setembre', 'settembre', 'september')),
    ('f72v1', ('libra', 'october', 'octembre', 'ottobre', 'oktober')),
    ('f73r', ('scorpio', 'nouember', 'nouembre', 'nouembre', 'nouember')),
    ('f73v', ('sagittarius', 'december', 'decembre', 'dicembre', 'december')),
])


def parole_pagine():
    out = OrderedDict((p, set()) for p in PAGINE)
    for r in trascrizione.leggi('ZL'):
        if r.pagina in out:
            out[r.pagina].update(tuple(D(w)) for w in r.parole if trascrizione.pulita(w))
    return out


def coppie(parole, nomi):
    out = []
    for u in parole:
        for n in set(nomi):
            if len(u) == len(n):
                out.append((u, n))
    return out


def punteggio(per_pagina, biunivoca, rnd):
    """per_pagina: liste di coppie (unita', nome). Massimo numero di pagine soddisfatte (golosa, ripartenze)."""
    migliore = 0
    ordine = list(range(len(per_pagina)))
    for _ in range(RIPARTENZE):
        rnd.shuffle(ordine)
        mappa, inv, n = {}, {}, 0
        for i in ordine:
            cc = per_pagina[i][:]
            rnd.shuffle(cc)
            for u, nome in cc:
                ok = True
                nuovi = {}
                for a, b in zip(u, nome):
                    if mappa.get(a, nuovi.get(a, b)) != b:
                        ok = False
                        break
                    if biunivoca:
                        inv_a = inv.get(b)
                        if inv_a is not None and inv_a != a:
                            ok = False
                            break
                        if any(x != a and y == b for x, y in nuovi.items()):
                            ok = False
                            break
                    nuovi[a] = b
                if ok:
                    for a, b in nuovi.items():
                        mappa[a] = b
                        inv[b] = a
                    n += 1
                    break
        migliore = max(migliore, n)
    return migliore


def prova(parole, nomi_per_pagina, biunivoca, rnd):
    pp = list(parole)
    vere = [coppie(parole[p], nomi_per_pagina[p]) for p in pp]
    vero = punteggio(vere, biunivoca, rnd)
    gruppi = [nomi_per_pagina[p] for p in pp]
    nulli = []
    for _ in range(PERMUTAZIONI):
        g = gruppi[:]
        rnd.shuffle(g)
        nulli.append(punteggio([coppie(parole[p], gg) for p, gg in zip(pp, g)], biunivoca, rnd))
    p = (1 + sum(n >= vero for n in nulli)) / (1 + PERMUTAZIONI)
    return OrderedDict([('vero', vero), ('nullo_media', statistics.mean(nulli)), ('nullo_max', max(nulli)), ('p', p)])


def main():
    rnd = random.Random(214)
    parole = parole_pagine()
    nomi = OrderedDict((p, v) for p, v in PAGINE.items())
    # controllo: il mese scritto sul foglio cifrato con una chiave biunivoca casuale lettera -> unita'
    rc = random.Random(2142)
    unita = sorted({u for s in parole.values() for w in s for u in w})
    lettere = sorted({c for v in PAGINE.values() for n in v for c in n})
    rc.shuffle(unita)
    chiave = dict(zip(lettere, unita))
    controllo = OrderedDict((p, set(s) | {tuple(chiave[c] for c in PAGINE[p][2])}) for p, s in parole.items())
    ris = OrderedDict([('parole_per_pagina', {p: len(s) for p, s in parole.items()})])
    for nome_t, par in (('Voynich', parole), ('controllo: nomi cifrati inseriti', controllo)):
        for tipo, biu in (('omofonica', False), ('biunivoca', True)):
            r = prova(par, nomi, biu, random.Random(2141))
            ris['%s, chiave %s' % (nome_t, tipo)] = r
            print('%-34s chiave %-10s vero %d | nullo media %.1f max %d | p %.4f' % (nome_t, tipo, r['vero'], r['nullo_media'], r['nullo_max'], r['p']), flush=True)
    c = ris['controllo: nomi cifrati inseriti, chiave biunivoca']
    valido = c['vero'] == 12 and c['p'] < 0.01
    v = ris['Voynich, chiave biunivoca']
    esito = 'test non valido' if not valido else ('nomi trovati' if v['vero'] >= 6 and v['p'] < 0.01 else ('nessun nome' if v['p'] > 0.05 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    print('valido %s | %s' % (valido, esito))
    json.dump(ris, open(os.path.join(RISULTATI, 'e214_nomi_dello_zodiaco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e214 — I nomi dei mesi e dei segni nello zodiaco', '', 'Pagine (su 12) con almeno una parola che, decifrata con una sola chiave, è il nome del segno o del mese; '
          'contro assegnazioni permutate. Preregistrazione: `preregistrazioni/e214.md`.', '', '| testo, chiave | vero | nullo (media / max) | p |', '|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict) and 'vero' in r:
            md.append('| %s | %d | %.1f / %d | %.4f |' % (k, r['vero'], r['nullo_media'], r['nullo_max'], r['p']))
    md += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e214_nomi_dello_zodiaco.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
