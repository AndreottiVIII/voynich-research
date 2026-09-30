# -*- coding: utf-8 -*-
"""Esperimento 42: le etichette della farmacia sono marcate per classe o scritte per lotti?

e40: a parita' di pagina, recipienti e frammenti finiscono in modo diverso. Se lo scriba
ha scritto ogni tipo in un lotto copiando e ritoccando (autocitazione), le etichette dello
stesso tipo si somigliano anche nel corpo (l'etichetta senza l'ultimo segno); se il tipo e'
marcato dalla terminazione, no. Test: distanza di edit fra i corpi, stesso tipo contro
tipo diverso, dentro la pagina; controlli sintetici sugli stessi schemi di pagina.

Preregistrazione: preregistrazioni/e42.md. Scrive risultati/e42_lotti.json e .md.
"""
import json, os, random, sys
from collections import Counter

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
from e40_etichette_tipo import etichette, CONFRONTI

RISULTATI = os.path.join(QUI, '..', 'risultati')
RIMESCOLAMENTI = 2000
SIMULAZIONI = 200


def per_pagina(dati):
    out = {}
    for pag, tipo, s in dati:
        out.setdefault(pag, []).append((tipo, tuple(s)))
    return out


def prepara(pagine, parte):
    """Per ogni pagina: tipi (0/1) e matrice delle distanze fra le parti scelte."""
    out = []
    for voci in pagine.values():
        tipi = np.array([t == 'recipiente' for t, _ in voci], dtype=int)
        pezzi = [parte(s) for _, s in voci]
        n = len(pezzi)
        d = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                d[i, j] = d[j, i] = parte.distanza(pezzi[i], pezzi[j])
        out.append((tipi, d))
    return out


def statistica(pagine, tipi_per_pagina):
    num = den = 0.0
    for (_, d), t in zip(pagine, tipi_per_pagina):
        n = len(t)
        if n < 3:
            continue
        iu = np.triu_indices(n, 1)
        stesso = (t[:, None] == t[None, :])[iu]
        valori = d[iu]
        if stesso.all() or not stesso.any():
            continue
        coppie = len(valori)
        num += (valori[~stesso].mean() - valori[stesso].mean()) * coppie
        den += coppie
    return num / den if den else 0.0


def prova(pagine, rnd):
    oss = statistica(pagine, [t for t, _ in pagine])
    nulle = np.array([statistica(pagine, [rnd.permutation(t) for t, _ in pagine]) for _ in range(RIMESCOLAMENTI)])
    return {'D': float(oss), 'nulla': float(nulle.mean()), 'z': float((oss - nulle.mean()) / nulle.std(ddof=1)),
            'p': float((1 + (nulle >= oss).sum()) / (1 + RIMESCOLAMENTI))}


class Corpo:
    """L'etichetta senza l'ultimo segno; distanza di edit normalizzata."""
    def __call__(self, s):
        return s[:-1]

    @staticmethod
    def distanza(a, b):
        return misure._dist_norm(a, b)


class Fine:
    """L'ultimo segno; distanza 0 se uguale, 1 se diverso."""
    def __call__(self, s):
        return s[-1]

    @staticmethod
    def distanza(a, b):
        return float(a != b)


def sintetico_lotti(pagine_vere, pool, inventario, rnd):
    out = {}
    for pag, voci in pagine_vere.items():
        ultima = {}
        nuove = []
        for tipo, _ in voci:
            if tipo not in ultima:
                s = list(rnd.choice(pool))
            else:
                s = list(ultima[tipo])
                for _ in range(rnd.choice((1, 2))):
                    azione = rnd.choice(('sost', 'ins', 'canc')) if len(s) > 3 else rnd.choice(('sost', 'ins'))
                    i = rnd.randrange(len(s))
                    if azione == 'sost':
                        s[i] = rnd.choice(inventario)
                    elif azione == 'ins':
                        s.insert(i, rnd.choice(inventario))
                    else:
                        del s[i]
            ultima[tipo] = s
            nuove.append((tipo, tuple(s)))
        out[pag] = nuove
    return out


def sintetico_classe(pagine_vere, pool, fini, rnd):
    out = {}
    for pag, voci in pagine_vere.items():
        out[pag] = []
        for tipo, _ in voci:
            corpo = rnd.choice(pool)[:-1]
            out[pag].append((tipo, tuple(corpo) + (rnd.choice(fini[tipo]),)))
    return out


def main():
    rnd_np = np.random.default_rng(42)
    rnd = random.Random(42)
    dati = [d for d in etichette(CONFRONTI[0][1]) if len(d[2]) >= 3]
    pagine = per_pagina(dati)
    pool = [tuple(s) for _, _, s in dati]
    inventario = sorted({g for s in pool for g in s})
    fini = {t: [s[-1] for _, tt, s in dati if tt == t] for t in ('recipiente', 'frammento')}
    ris = {'etichette': len(dati), 'pagine': len(pagine), 'per_tipo': dict(Counter(t for _, t, _ in dati))}
    ris['voynich_corpo'] = prova(prepara(pagine, Corpo()), rnd_np)
    ris['voynich_fine'] = prova(prepara(pagine, Fine()), rnd_np)
    print('Voynich corpo: D %.4f z %.1f p %.4f | fine: D %.4f z %.1f p %.4f' % (
        ris['voynich_corpo']['D'], ris['voynich_corpo']['z'], ris['voynich_corpo']['p'],
        ris['voynich_fine']['D'], ris['voynich_fine']['z'], ris['voynich_fine']['p']), flush=True)
    for nome, gen, soglia in (('controllo lotti', lambda: sintetico_lotti(pagine, pool, inventario, rnd), 0.01),
                              ('controllo classe', lambda: sintetico_classe(pagine, pool, fini, rnd), 0.05)):
        ps = []
        for _ in range(SIMULAZIONI):
            ps.append(prova(prepara(gen(), Corpo()), rnd_np)['p'])
        ris[nome] = {'quota_p_sotto_soglia': float(np.mean(np.array(ps) < soglia)), 'soglia': soglia,
                     'p_mediana': float(np.median(ps))}
        print('%s: quota p < %.2f = %.2f (p mediana %.3f)' % (nome, soglia, ris[nome]['quota_p_sotto_soglia'],
                                                            ris[nome]['p_mediana']), flush=True)
    validi = ris['controllo lotti']['quota_p_sotto_soglia'] >= 0.8 and ris['controllo classe']['quota_p_sotto_soglia'] <= 0.1
    ris['controlli_validi'] = bool(validi)
    with open(os.path.join(RISULTATI, 'e42_lotti.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    v, f_ = ris['voynich_corpo'], ris['voynich_fine']
    righe = ['# e42 — Etichette della farmacia: classe marcata o lotti di scrittura?', '',
             '%d etichette (recipienti %d, frammenti %d) su %d pagine, almeno 3 segni. D = distanza media fra '
             'coppie di tipo diverso − fra coppie dello stesso tipo, dentro la pagina (positivo = lo stesso tipo '
             'si somiglia di più); %d rimescolamenti dei tipi dentro la pagina. Preregistrazione: '
             '`preregistrazioni/e42.md`.' % (len(dati), ris['per_tipo'].get('recipiente', 0),
                                              ris['per_tipo'].get('frammento', 0), len(pagine), RIMESCOLAMENTI), '',
             '| prova | D | z | p (una coda) |', '|---|---|---|---|',
             '| Voynich, corpo (senza l\'ultimo segno) | %.4f | %.1f | %.4f |' % (v['D'], v['z'], v['p']),
             '| Voynich, ultimo segno | %.4f | %.1f | %.4f |' % (f_['D'], f_['z'], f_['p']), '',
             '| controllo (%d simulazioni) | criterio | esito | p mediana |' % SIMULAZIONI, '|---|---|---|---|',
             '| lotti: copia e ritocco per tipo | p < 0,01 in almeno 80%% | %.0f%% | %.3f |' % (
                 100 * ris['controllo lotti']['quota_p_sotto_soglia'], ris['controllo lotti']['p_mediana']),
             '| classe: corpo a caso + terminazione del tipo | p < 0,05 in non più del 10%% | %.0f%% | %.3f |' % (
                 100 * ris['controllo classe']['quota_p_sotto_soglia'], ris['controllo classe']['p_mediana']), '',
             'Controlli validi: %s.' % ('sì' if validi else 'no — l\'esito sul Voynich non conta')]
    with open(os.path.join(RISULTATI, 'e42_lotti.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
