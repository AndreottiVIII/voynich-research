# -*- coding: utf-8 -*-
"""Esperimento e3b98: rapporto R = K(3)/K(1) (rispetto a 8-12) con una classe generica (le due ultime lettere più
frequenti) su tutti i testi grandi del corpus, e sul Voynich come descrizione.

Preregistrazione: preregistrazioni/e3b98.md. Scrive risultati/e3b98_forma_lingue.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b96_forma_calo as e3b96

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
MIN_PAROLE = 50000
SOGLIA_R = 0.64
SOGLIA_ACCANTO = 0.02
GRUPPI = ('d1', 'd3', 'lontane')


def classe_generica(sequenze):
    """Funzione di classe sulle due ultime lettere più frequenti (parole di almeno 3 lettere)."""
    c = Counter(w[-1] for s in sequenze for w in s if len(w) >= 3)
    (l1, _), (l2, _) = c.most_common(2)

    def f(w):
        if len(w) >= 3 and w[-1] in (l1, l2):
            return (1 if w[-1] == l2 else 0, tuple(w[:-1]) + ('*',))
        return None
    return f, (l1, l2)


def matrice(ss):
    """(unità, 9): accordi, attesi, coppie per d1, d3, lontane."""
    return np.array([[s[g][k] for g in GRUPPI for k in range(3)] for s in ss], dtype=float)


def kappa(somme):
    """somme (..., 9) -> (K d1, K d3, K lontane)."""
    o, a, n = somme[..., 0::3], somme[..., 1::3], somme[..., 2::3]
    with np.errstate(divide='ignore', invalid='ignore'):
        return (o - a) / (n - a)


def misure(k):
    accanto = k[..., 0] - k[..., 2]
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(accanto > 0, (k[..., 1] - k[..., 2]) / accanto, np.nan)
    return accanto, r


def num(x):
    """Numero, o None se non definito (R non esiste se non c'è accordo accanto)."""
    return float(x) if np.isfinite(x) else None


def due(x):
    return '—' if x is None else '%.2f' % x


def analizza(unita, classi, rng):
    ss = [e3b96.somme_unita(u, classi) for u in unita]
    m = matrice(ss)
    acc, r = misure(kappa(m.sum(0)))
    bs_acc, bs_r = [], []
    n = len(m)
    for _ in range(BOOT // 500):
        idx = rng.integers(0, n, size=(500, n))
        cont = np.zeros((500, n))
        np.add.at(cont, (np.repeat(np.arange(500), n), idx.ravel()), 1)
        a, rr = misure(kappa(cont @ m))
        bs_acc.append(a)
        bs_r.append(rr)
    bs_acc, bs_r = np.concatenate(bs_acc), np.concatenate(bs_r)
    bs_r = bs_r[np.isfinite(bs_r)]
    ic_r = [num(np.percentile(bs_r, 2.5)), num(np.percentile(bs_r, 97.5))] if len(bs_r) >= BOOT // 2 else [None, None]
    return OrderedDict([('unita', n), ('coppie_d1', int(m[:, 2].sum())), ('accanto', float(acc)),
                        ('accanto_IC95', [float(np.percentile(bs_acc, 2.5)), float(np.percentile(bs_acc, 97.5))]),
                        ('R', num(r)), ('R_IC95', ic_r)])


def main():
    rng = np.random.default_rng(3298)
    tt = e381.testi()
    ris = OrderedDict()
    for chiave, righe in tt.items():
        righe = [r for r in righe if r]
        if 'Abbreviated' in chiave or sum(len(r) for r in righe) < MIN_PAROLE:
            continue
        uu = [[b] for b in e3b51.blocchi(righe)]
        f, lettere = classe_generica([b for u in uu for b in u])
        x = analizza(uu, OrderedDict([('x', f)]), rng)
        x['lettere'] = list(lettere)
        x['conta'] = x['accanto_IC95'][0] > SOGLIA_ACCANTO
        ris[chiave.replace('.txt', '')] = x
        print(chiave, json.dumps(x, ensure_ascii=False), flush=True)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    voy = OrderedDict()
    for nome, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        uu, _ = e3b62.voynich(pd, mano)
        f, lettere = classe_generica([r for u in uu for r in u])
        x = analizza(uu, OrderedDict([('x', f)]), rng)
        x['lettere'] = list(lettere)
        voy[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    contano = [k for k, x in ris.items() if x['conta'] and x['R'] is not None]
    sopra = [k for k in contano if ris[k]['R'] >= SOGLIA_R]
    if not sopra:
        esito = 'la forma resta propria del Voynich'
    elif len(sopra) >= 3:
        esito = 'la forma non è propria del Voynich'
    else:
        esito = 'incerto'
    rr = sorted(ris[k]['R'] for k in contano)
    out = OrderedDict([('lingue', ris), ('voynich_descrittivo', voy), ('contano', len(contano)), ('sopra_soglia', sopra),
                       ('R_lingue_mediana', float(np.median(rr)) if rr else None), ('R_lingue_massimo', rr[-1] if rr else None), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b98 — Qualche lingua del corpus ha la forma "piatta" della memoria del Voynich?', '',
          'Preregistrazione: `preregistrazioni/e3b98.md`. Classe generica: le due ultime lettere più frequenti. Voynich con le sue quattro scelte (e3b97): R 0,64–0,66.', '',
          '| testo | lettere | unità | accanto (IC 95%) | conta | R (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in list(ris.items()) + list(voy.items()):
        md.append('| %s | %s | %d | %+.3f (%+.3f – %+.3f) | %s | %s (%s – %s) |' % (
            k, '/'.join(x['lettere']), x['unita'], x['accanto'], x['accanto_IC95'][0], x['accanto_IC95'][1],
            {True: 'sì', False: 'no'}.get(x.get('conta'), 'descr.'), due(x['R']), due(x['R_IC95'][0]), due(x['R_IC95'][1])))
    md += ['', 'Testi che contano: %d. R mediano %.2f, massimo %.2f. Sopra 0,64: %s.' % (len(contano), out['R_lingue_mediana'] or float('nan'), out['R_lingue_massimo'] or float('nan'), ', '.join(sopra) or 'nessuno'),
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b98_forma_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
