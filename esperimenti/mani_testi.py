# -*- coding: utf-8 -*-
"""Testi, mani e controlli per ia12 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- `bundle_vere`: le pagine vere (o, con SOLO_CONTROLLI, un testo latino con una "disposizione finta" di lingue, sezioni e mani
  che imita la struttura pubblicata in e130/e244), con per ogni pagina la sezione, la lingua A/B e la mano.
- `bundle_controllo`: testi di controllo con la STESSA forma delle vere (stesse pagine, righe, lunghezze di riga, pieghe,
  etichette di lingua, sezione e mano) ma parole latine: negativi (nessuna differenza fra mani) e positivi (le pagine di una
  mano fatte con un processo noto diverso: copia, grammatica, catena di caratteri, ripresa della riga sopra).
- `registra_sotto`: mette un sotto-testo (le pagine scelte di una coppia di mani) e la sua versione "parole mescolate dentro la
  pagina" nelle tabelle dei testi di ia09 e ia10, cosi' si riusano per import i lavori di quegli esperimenti.
Nessuna parola della trascrizione e' scritta in uscita: questo modulo carica e costruisce e basta.
"""
import os
import random
import sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia01_giudice_neurale as G  # noqa: E402
import sintassi_testi as TT  # noqa: E402
import sintassi_modelli as SM  # noqa: E402

SOLO_CONTROLLI = G.SOLO_CONTROLLI
MANO_PIANTATA = '3'                       # nei controlli positivi le pagine di questa mano sono fatte con il processo noto
# parole latine: scostamenti (in parole) nel flusso di Plinio, uno per testo di controllo
SCOSTAMENTI = OrderedDict([('neg1', 100000), ('neg2', 160000), ('pos_eco', 220000), ('pos_gram', 280000),
                           ('pos_ctx', 340000), ('pos_riga', 400000), ('pos_loc', 460000)])
P_COPIA_PIANTATA = 0.04                   # come il livello "M" di ia09
SCALA_COPIA = 10.0
P_COPIA_LOC = 0.10                        # pos_loc: copia piu' forte e piu' vicina (a 15.000 parole la quota locale e' rumorosa)
SCALA_LOC = 3.0
FORZA_PIANTATA = 1.0                      # come il livello "F" di ia09 (la catena di classi e' un ciclo)
ORDINE_MARKOV = 3                         # come il controllo C1 di ia03

_B = {}
_FLUSSO = {}


# ---------------------------------------------------------------- disposizione finta (solo per le prove del codice)

# quote di pagine (da e244: mani 1, 2, 3, 5 con 101, 45, 30, 7 pagine) e sezioni (da e244: lo strato B|H ha 20 pagine della mano 2,
# 6 della mano 3, 6 della mano 5); sono numeri pubblicati nei risultati del repo, usati solo per dare una forma plausibile alla prova
QUOTE_FINTE = [('1', 'A', 0.552, [('H', 0.8), ('Z', 0.2)]),
               ('2', 'B', 0.246, [('H', 0.44), ('S', 0.56)]),
               ('3', 'B', 0.164, [('H', 0.20), ('C', 0.80)]),
               ('5', 'B', 0.038, [('H', 0.86), ('T', 0.14)])]


def layout_finto(nomi, seme=12):
    """Per ogni pagina (sezione, lingua, mano) di una disposizione finta con le proporzioni di e244."""
    nomi = sorted(nomi)
    n = len(nomi)
    rnd = random.Random(seme)
    out, k = {}, 0
    for i, (mano, lingua, q, sezioni) in enumerate(QUOTE_FINTE):
        m = n - k if i == len(QUOTE_FINTE) - 1 else int(round(q * n))
        blocco = nomi[k:k + m]
        k += m
        etich = []
        for s, qs in sezioni:
            etich += [s] * int(round(qs * len(blocco)))
        etich = (etich + [sezioni[-1][0]] * len(blocco))[:len(blocco)]
        rnd.shuffle(etich)
        for p, s in zip(blocco, etich):
            out[p] = (s, lingua, mano)
    return out


# ---------------------------------------------------------------- mani reali

def mani_reali(nomi):
    """Mano di ogni pagina (quella con piu' parole nella pagina) dalla trascrizione ZL (attributo $H, attribuzione di Davis);
    restituisce anche il numero di pagine con piu' di una mano."""
    import trascrizione
    cont = defaultdict(Counter)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            cont[r.pagina][str(r.mano or '?')] += len(ps)
    mano = {p: (cont[p].most_common(1)[0][0] if cont.get(p) else '?') for p in nomi}
    miste = sum(1 for p in nomi if len(cont.get(p, {})) > 1)
    return mano, miste


# ---------------------------------------------------------------- testi

def bundle_vere():
    """dict(nome, pagine, fold, sez, lingua, mano, miste)."""
    if 'vere' in _B:
        return _B['vere']
    c = G.contesto()
    nomi = list(c['vere'])
    if SOLO_CONTROLLI:
        lay = layout_finto(nomi)
        sez = {p: lay[p][0] for p in nomi}
        lingua = {p: lay[p][1] for p in nomi}
        mano = {p: lay[p][2] for p in nomi}
        miste = 0
    else:
        sez = {p: str(c['tipo'][p][0] or '?') for p in nomi}
        lingua = {p: str(c['tipo'][p][1] or '?') for p in nomi}
        mano, miste = mani_reali(nomi)
    b = dict(nome='vere', pagine=OrderedDict(c['vere']), fold=dict(c['fold']), sez=sez, lingua=lingua, mano=mano, miste=miste)
    _B['vere'] = b
    return b


def forma_di(b):
    """La 'forma' di un testo: per pagina, per riga (inizio paragrafo, numero di parole)."""
    return OrderedDict((p, [(ini, len(ws)) for ini, ws in rows]) for p, rows in b['pagine'].items())


def su_forma(forma, parole, ordine=None):
    """Riempie una forma con un flusso di parole (tuple di segni): le pagine si riempiono nell'ordine `ordine` (nomi di pagina; predefinito
    l'ordine della forma) e il risultato sta nell'ordine della forma. Con un ordine a caso, pagine vicine nel manoscritto non prendono
    tratti vicini del testo: nessuna mano ha un argomento suo."""
    righe_di = {}
    k = 0
    for p in (ordine or list(forma)):
        rows = []
        for ini, n in forma[p]:
            rows.append((ini, list(parole[k:k + n])))
            k += n
        righe_di[p] = rows
    return OrderedDict((p, righe_di[p]) for p in forma)


def flusso_latino():
    """Tutte le parole latine di Plinio (Gaskell e Bowern) in un'unica lista di tuple di segni."""
    if 'l' not in _FLUSSO:
        import e3c95_imparabilita as e95
        tt, _ = e95.lingue()
        righe = [r for r in tt[TT.CHIAVE_LATINO] if r]
        _FLUSSO['l'] = [tuple(w) for r in righe for w in r]
    return _FLUSSO['l']


def _mescola(base, altro, mano_piantata):
    """Le pagine della mano piantata prese da `altro`, le altre da `base`."""
    v = bundle_vere()
    return OrderedDict((p, (altro[p] if v['mano'][p] == mano_piantata else base[p])) for p in base)


def bundle_controllo(nome):
    """Testo di controllo con la forma e le etichette delle vere. neg1, neg2: latino puro. pos_eco: la mano piantata e' scritta da
    un generatore a sola copia; pos_loc: le mani 2 e 3 copiano a distanze diverse; pos_gram: a sola grammatica; pos_ctx: da una catena di Markov di caratteri di ordine 3; pos_riga:
    ogni riga della mano piantata comincia con gli ultimi 3 segni della riga sopra."""
    if nome in _B:
        return _B[nome]
    v = bundle_vere()
    forma = forma_di(v)
    n_par = sum(n for righe in forma.values() for _, n in righe)
    flusso = flusso_latino()
    off = SCOSTAMENTI[nome] % max(1, len(flusso) - n_par)
    ordine = sorted(forma)
    random.Random(G.seme_di('ia12:ordine:' + nome)).shuffle(ordine)           # pagine a caso: nessuna mano ha un argomento suo
    base = su_forma(forma, flusso[off:off + n_par], ordine)
    seme = G.seme_di('ia12:ctrl:' + nome)
    if nome in ('neg1', 'neg2'):
        pag = base
    elif nome == 'pos_eco':
        Cb = SM.Corpus(base)
        Cb.prepara()
        pag = _mescola(base, SM.genera_copia(Cb, seme, P_COPIA_PIANTATA, SCALA_COPIA), MANO_PIANTATA)
    elif nome == 'pos_gram':
        Cb = SM.Corpus(base)
        Cb.prepara()
        pag = _mescola(base, SM.genera_grammatica(Cb, seme, FORZA_PIANTATA)[0], MANO_PIANTATA)
    elif nome == 'pos_loc':
        # due mani con la stessa quantita' di copia ma diversa distanza: la mano 2 copia da ovunque nella pagina (scala 400 parole,
        # cioe' "di pagina"), la mano 3 copia da vicino (scala 3, "locale"): la quota locale deve differire
        Cb = SM.Corpus(base)
        Cb.prepara()
        loc = SM.genera_copia(Cb, seme, P_COPIA_LOC, SCALA_LOC)
        glo = SM.genera_copia(Cb, seme + 1, P_COPIA_LOC, 400.0)
        pag = OrderedDict((p, (loc[p] if v['mano'][p] == '3' else glo[p] if v['mano'][p] == '2' else base[p])) for p in base)
    elif nome == 'pos_ctx':
        pag = _mescola(base, G.markov(base, ORDINE_MARKOV, seme), MANO_PIANTATA)
    elif nome == 'pos_riga':
        import ia03_contesto as I3
        alt = OrderedDict()
        for p, rows in base.items():
            bl = [[tuple(w) for w in ws] for _, ws in rows]
            nuove = I3.ripresa_ultimi_segni([bl])[0]
            alt[p] = [(rows[j][0], list(r)) for j, r in enumerate(nuove)]
        pag = _mescola(base, alt, MANO_PIANTATA)
    else:
        raise ValueError(nome)
    b = dict(nome=nome, pagine=pag, fold=v['fold'], sez=v['sez'], lingua=v['lingua'], mano=v['mano'], miste=v['miste'])
    _B[nome] = b
    return b


def bundle(nome):
    return bundle_vere() if nome == 'vere' else bundle_controllo(nome)


def registra_sotto(nome, pid, m, pagine, fold):
    """Registra il sotto-testo (pagine scelte del testo `nome`) e la sua versione con le parole mescolate dentro la pagina (`~p`)
    nelle tabelle di ia09 e ia10 (prefisso 'm_'), per riusarne i lavori. Restituisce il nome del sotto-testo."""
    import ia09_dove_sta_sintassi as I9
    import ia10_famiglie_parole as I10
    b = bundle(nome)
    nm = 'm_%s__%s__%d' % (nome, pid, m)
    pag = OrderedDict((p, b['pagine'][p]) for p in sorted(pagine))
    rim = TT.rimescola_pagina(pag, G.seme_di('ia12:rim:' + nm))
    for suff, pg in (('', pag), ('~p', rim)):
        I9._T[nm + suff] = dict(pagine=pg, fold=fold, tipo=None, meta={})
        I10._T[nm + suff] = I10.FT.Testo(nm + suff, pg, tipo={}, piega=fold)
    return nm


# ---------------------------------------------------------------- gruppi di pagine

def gruppi(b):
    """Gruppi (mano, lingua) -> lista di pagine; con parole e pagine."""
    g = OrderedDict()
    for p in b['pagine']:
        g.setdefault((b['mano'][p], b['lingua'][p]), []).append(p)
    return g


def parole_pagina(b):
    return {p: sum(len(ws) for _, ws in rows) for p, rows in b['pagine'].items()}
