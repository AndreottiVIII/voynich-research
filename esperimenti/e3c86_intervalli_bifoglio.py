# -*- coding: utf-8 -*-
"""Esperimento e3c86: gli intervalli delle misure principali ricampionando bifogli e fascicoli invece delle pagine.

Nota A5 del revisore: il paper mostra che il bifoglio è un'unità (identità condivisa da recto, verso e foglio coniugato),
quindi le pagine dello stesso bifoglio non sono indipendenti e il bootstrap per pagina può dare intervalli troppo stretti.
Per ogni misura si calcolano i contributi per pagina, si sommano per gruppo (pagina, bifoglio, fascicolo) e si
ricampionano i gruppi (2.000 volte).

Misure (Voynich ZL, testo corrente):
- stato breve delle scelte: K corretto a distanza 1 e media 2–3 (misura dell'e3c48; k/t, sh/ch, -ey/-dy; nullo 50);
- deriva lungo la riga: pendenza ogni 10 segni per qo/o, k/t, sh/ch, -ey/-dy (misura dell'e3c13);
- giuntura E fra ultimo e primo segno di parole vicine (misura dell'e377; nullo 50 rimescolamenti nella riga);
- margine sinistro: rapporto osservato/atteso degli inizi uguali (primi 2 segni) fra righe consecutive, righe dalla
  seconda del paragrafo, atteso = media di 200 rimescolamenti dell'ordine delle righe nel paragrafo (e3a35);
- ripetizione immediata esatta e quasi esatta (e3b25).

Preregistrazione: preregistrazioni/e3c86.md. Scrive risultati/e3c86_intervalli_bifoglio.json e .md.
SOLO_CONTROLLI=1: prova del codice del bootstrap su dati finti (niente Voynich).
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e308_libro_fisico as e308
import e341_fonti as e341
import e3a25_inizi_evitati as e3a25
import e3a86_ripetizioni_riga as e3a86
import e3b62_memoria_nullo_largo as e3b62
import e3c10_strati_lettere_parole as e3c10
import e3c13_sh_lungo_la_riga as e3c13
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
BOOT = 2000
PERM = 50
PERM_MARGINE = 200
D = misure.divisore(misure.GLIFI_EVA)
LIVELLI = ('pagina', 'bifoglio', 'fascicolo')


# --------------------------------------------------------------------------- bootstrap per gruppi
def gruppi_di(nomi, testa):
    """Indici di gruppo per pagina, bifoglio (fascicolo + bifoglio) e fascicolo."""
    out = OrderedDict()
    for liv in LIVELLI:
        chiavi = []
        for p in nomi:
            v = testa.get(p) or {}
            if liv == 'pagina' or not v.get('Q'):
                chiavi.append(('p', p))
            elif liv == 'bifoglio':
                chiavi.append((v['Q'], v['B']))
            else:
                chiavi.append((v['Q'],))
        _, idx = np.unique(np.array([repr(k) for k in chiavi]), return_inverse=True)
        out[liv] = idx
    return out


def somma_per_gruppo(st, g):
    S = np.zeros((int(g.max()) + 1,) + st.shape[1:])
    np.add.at(S, g, st)
    return S


def intervallo(st, g, funzione, rng, metodo='percentile'):
    """st: contributi per pagina (prima dimensione = pagine); funzione(somma totale) -> valore (o vettore).
    metodo 'basic' (intervallo rovesciato, 2θ − q): per l'informazione mutua, che il ricampionamento gonfia."""
    S = somma_per_gruppo(st, g)
    n = len(S)
    boot = np.array([funzione(S[rng.integers(0, n, n)].sum(0)) for _ in range(BOOT)])
    lo, hi = np.nanpercentile(boot, 2.5, axis=0), np.nanpercentile(boot, 97.5, axis=0)
    if metodo == 'basic':
        t = np.asarray(funzione(st.sum(0)))
        lo, hi = 2 * t - hi, 2 * t - lo
    return n, lo, hi


# --------------------------------------------------------------------------- dati
def pagine_zl():
    """[(pagina, mano, paragrafi -> righe -> parole come tuple di segni)] in ordine."""
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    out = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        out.append((pg, mano.get(pg), pp))
    return out


# --------------------------------------------------------------------------- misure con contributi per pagina
def stato(pagine, rng):
    usate = [(pg, h, [r for par in pp for r in par]) for pg, h, pp in pagine if h]
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    cl = OrderedDict((k, e3b62.CV[k]) for k in e3c48.TRE)
    tok = e3c33.raccogli([(h, rr) for _, h, rr in usate], cl)
    n_p = len(usate)
    st = e3c33.somme(tok, n_p)
    nul = []
    for _ in range(PERM):
        s = e3c33.somme(e3c48.rimescola(tok, rng), n_p).sum(0)
        nul.append(s[:, 0] / s[:, 1])
    k_nul = np.mean(nul, axis=0)

    def f(s):
        k = s[:, 0] / s[:, 1] - k_nul
        return np.array([k[0], (k[1] + k[2]) / 2])
    return [pg for pg, _, _ in usate], st, f, f(st.sum(0))


def deriva(pagine, scelta):
    usate = [(pg, h, [r for par in pp for r in par if r]) for pg, h, pp in pagine if h]
    uu = [rr for _, _, rr in usate]
    obs = [(u, (scelta, cop), x, v) for (u, cop, x, v) in e3c13.osservazioni(uu, e3b62.CV[scelta])]
    un = np.array([o[0] for o in obs])
    _, strato = np.unique(np.array([hash(o[1]) for o in obs]), return_inverse=True)
    x = np.array([o[2] for o in obs], dtype=float)
    y = np.array([o[3] for o in obs], dtype=float)
    st = e3c10.statistiche(strato, x, y, un, len(uu), int(strato.max()) + 1)

    def f(s):
        return 10 * e3c10.pendenza(s)
    return [pg for pg, _, _ in usate], st, f, f(st.sum(0))


NULLI_GIUNTURA = 20


def giuntura(pagine, rng):
    """Per ogni pagina: conteggi delle coppie (ultimo segno, primo segno) e, accanto, quelli di 20 versioni della pagina
    con le parole rimescolate in ogni riga. A ogni ricampionamento E = MI(osservato) − media MI(rimescolati) sulle stesse
    pagine: il nullo ha la stessa distorsione da campione piccolo dell'osservato."""
    righe_per_pagina = [[r for par in pp for r in par if len(r) >= 2] for _, _, pp in pagine]
    segni = sorted({x for rr in righe_per_pagina for r in rr for w in r for x in (w[0], w[-1])})
    ix = {s: i for i, s in enumerate(segni)}
    G = len(segni)

    def conta(rr):
        m = np.zeros((G, G))
        for r in rr:
            for a, b in zip(r, r[1:]):
                m[ix[a[-1]], ix[b[0]]] += 1
        return m

    def mi(m):
        n = m.sum()
        pa, pb = m.sum(1, keepdims=True), m.sum(0, keepdims=True)
        with np.errstate(divide='ignore', invalid='ignore'):
            t = np.where(m > 0, m / n * np.log2(m * n / (pa * pb)), 0.0)
        return float(t.sum())
    st = np.array([[conta(rr)] + [conta([[r[i] for i in rng.permutation(len(r))] for r in rr]) for _ in range(NULLI_GIUNTURA)]
                   for rr in righe_per_pagina])

    def f(s):
        return mi(s[0]) - float(np.mean([mi(s[k]) for k in range(1, len(s))]))
    return [pg for pg, _, _ in pagine], st, f, f(st.sum(0))


def margine(pagine, rnd):
    nomi, st = [], []
    for pg, _, pp in pagine:
        oss = att = 0.0
        for par in pp:
            rr = par[1:]
            if len(rr) < 3:
                continue
            ini = e3a25.inizi(rr, 2)   # come l'e3a35: righe di almeno 3 parole, prima parola di almeno 2 segni
            oss += e3a25.quota([ini])[0]
            att += sum(e3a25.quota([rnd.sample(ini, len(ini))])[0] for _ in range(PERM_MARGINE)) / PERM_MARGINE
        nomi.append(pg)
        st.append([oss, att])
    st = np.array(st)

    def f(s):
        return s[0] / s[1]
    return nomi, st, f, f(st.sum(0))


def ripetizioni(pagine):
    nomi, st = [], []
    for pg, _, pp in pagine:
        e = [0, 0, 0, 0]
        for par in pp:
            for r in par:
                for a, b in zip(r, r[1:]):
                    if len(a) >= 2 and len(b) >= 2:
                        e[0] += a == b
                        e[1] += 1
                    if len(a) >= 3 and len(b) >= 3:
                        e[2] += e3a86.una_modifica(a, b)
                        e[3] += 1
        nomi.append(pg)
        st.append(e)
    st = np.array(st, dtype=float)

    def f(s):
        return np.array([s[0] / s[1], s[2] / s[3]])
    return nomi, st, f, f(st.sum(0))


# --------------------------------------------------------------------------- prova del codice
def controlli():
    rng = np.random.default_rng(1)
    # (a) con gruppi = pagine il bootstrap per gruppo coincide con quello per pagina
    st = rng.normal(1.0, 0.3, size=(200, 2)).clip(0.01)
    f = lambda s: s[0] / s[1]
    g = np.arange(200)
    a = intervallo(st, g, f, np.random.default_rng(5))
    b = intervallo(st, g, f, np.random.default_rng(5))
    print('(a) stesso seme, gruppi = pagine:', a[1:], b[1:])
    # (b) effetto di gruppo forte: 40 gruppi di 5 pagine che condividono un livello -> intervallo per gruppo più largo
    livello = np.repeat(rng.normal(0, 0.5, 40), 5)
    st2 = np.stack([np.exp(livello + rng.normal(0, 0.1, 200)), np.ones(200)], 1)
    _, lo_p, hi_p = intervallo(st2, np.arange(200), f, rng)
    _, lo_g, hi_g = intervallo(st2, np.repeat(np.arange(40), 5), f, rng)
    print('(b) larghezza per pagina %.3f, per gruppo %.3f, rapporto %.2f' % (hi_p - lo_p, hi_g - lo_g, (hi_g - lo_g) / (hi_p - lo_p)))
    # (c) senza effetto di gruppo -> larghezze simili
    st3 = np.stack([np.exp(rng.normal(0, 0.5, 200)), np.ones(200)], 1)
    _, lo_p, hi_p = intervallo(st3, np.arange(200), f, rng)
    _, lo_g, hi_g = intervallo(st3, np.repeat(np.arange(40), 5), f, rng)
    print('(c) larghezza per pagina %.3f, per gruppo %.3f, rapporto %.2f' % (hi_p - lo_p, hi_g - lo_g, (hi_g - lo_g) / (hi_p - lo_p)))


# --------------------------------------------------------------------------- principale
RIFERIMENTO = OrderedDict([  # (nome, indice nel vettore o None, valore da escludere, lato: 'sopra' = l'intervallo deve stare sopra)
    ('stato breve K1', ('stato', 0, 0.0, 'sopra')), ('stato breve K2-3', ('stato', 1, 0.0, 'sopra')),
    ('deriva qo/o', ('deriva qo/o', None, 0.0, 'sotto')), ('deriva k/t', ('deriva k/t', None, 0.0, 'sotto')),
    ('deriva sh/ch', ('deriva sh/ch', None, 0.0, 'sotto')), ('deriva -ey/-dy', ('deriva -ey/-dy', None, 0.0, 'sotto')),
    ('giuntura E', ('giuntura', None, 0.0, 'sopra')), ('margine (rapporto)', ('margine', None, 1.0, 'sotto')),
    ('ripetizione esatta', ('ripetizioni', 0, 0.0040, 'sopra')), ('ripetizione quasi esatta', ('ripetizioni', 1, 0.0186, 'sopra'))])


def main():
    if SOLO_CONTROLLI:
        controlli()
        return
    rng = np.random.default_rng(3386)
    rnd = random.Random(3386)
    testa = e308.intestazioni()
    pagine = pagine_zl()
    misure_ = OrderedDict()
    misure_['stato'] = stato(pagine, rng)
    for k in ('qo/o', 'k/t', 'sh/ch', '-ey/-dy'):
        misure_['deriva %s' % k] = deriva(pagine, k)
    misure_['giuntura'] = giuntura(pagine, rng)
    misure_['margine'] = margine(pagine, rnd)
    misure_['ripetizioni'] = ripetizioni(pagine)
    ris = OrderedDict()
    for nome, (mis, i, rif, lato) in RIFERIMENTO.items():
        nomi, st, f, valore = misure_[mis]
        g = gruppi_di(nomi, testa)
        v = float(valore[i]) if i is not None else float(valore)
        r = OrderedDict([('valore', v), ('riferimento', rif), ('lato', lato)])
        for liv in LIVELLI:
            n, lo, hi = intervallo(st, g[liv], f, rng)
            lo, hi = (float(lo[i]), float(hi[i])) if i is not None else (float(lo), float(hi))
            regge = (lo > rif) if lato == 'sopra' else (hi < rif)
            r[liv] = OrderedDict([('gruppi', n), ('IC95', [lo, hi]), ('larghezza', hi - lo), ('regge', bool(regge))])
        r['rapporto_larghezza_bifoglio'] = r['bifoglio']['larghezza'] / r['pagina']['larghezza']
        r['rapporto_larghezza_fascicolo'] = r['fascicolo']['larghezza'] / r['pagina']['larghezza']
        r['esito'] = 'regge per bifoglio e per fascicolo' if r['bifoglio']['regge'] and r['fascicolo']['regge'] else (
            'regge per bifoglio, non per fascicolo' if r['bifoglio']['regge'] else 'non regge per bifoglio')
        ris[nome] = r
        print(nome, json.dumps(r, default=float), flush=True)
    json.dump(OrderedDict([('misure', ris)]), open(os.path.join(RISULTATI, 'e3c86_intervalli_bifoglio.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c86 — Intervalli ricampionando pagine, bifogli e fascicoli', '', 'Preregistrazione: `preregistrazioni/e3c86.md`. Voynich ZL; bootstrap 2.000 per livello.', '',
          '| misura | valore | IC 95% per pagina | per bifoglio | per fascicolo | larghezza bifoglio/pagina | fascicolo/pagina | esito |', '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        md.append('| %s | %+.4f | %+.4f – %+.4f | %+.4f – %+.4f | %+.4f – %+.4f | %.2f | %.2f | %s |' % (
            nome, r['valore'], *r['pagina']['IC95'], *r['bifoglio']['IC95'], *r['fascicolo']['IC95'],
            r['rapporto_larghezza_bifoglio'], r['rapporto_larghezza_fascicolo'], r['esito']))
    md += ['', 'Gruppi: %d pagine, %d bifogli, %d fascicoli (stato breve).' % tuple(ris['stato breve K1'][l]['gruppi'] for l in LIVELLI)]
    open(os.path.join(RISULTATI, 'e3c86_intervalli_bifoglio.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
