# -*- coding: utf-8 -*-
"""Statistiche di sintesi per ia28 (modulo di supporto, non e' un esperimento).

Servono all'inferenza per simulazione (ABC): devono costare pochi secondi per un quarto di libro (circa 7-10.000 parole), perche' se ne
calcolano migliaia. Sono tutte CLASSICHE (conteggi, entropie, nessuna rete) e sono versioni a basso costo delle misure di ia14, ia19 e
ia20: dove una misura esiste gia' (contatto di ia08, bande d'eco di ia09 e ia15, firma dei bordi di ia17) si richiama la funzione del
repo senza modificarla; le altre sono definite qui. Le misure pesanti (k90 e le altre della rete, copia netta e Λ di ia09, D di ia10, i
giudici) NON entrano nella stima: restano fuori per la verifica (`abc_tenute_fuori.py`).

Una pagina e' una lista di righe (inizio_paragrafo, [parola, ...]); una parola e' una tupla di glifi (come ia01).

Le 29 statistiche di sintesi (`NOMI`), in sei gruppi:
  forma delle parole (8)   lunghezza media e sd; entropia dei glifi H0 (nessun contesto), H1, H2, H3 (contesto di 1, 2, 3 glifi dentro la
                           parola, con inizio e fine parola); entropia del primo e dell'ultimo glifo
  vocabolario (6)          tipi/parole; hapax/parole; quota di parole il cui tipo sta in una sola pagina; quota delle 10 parole piu'
                           frequenti; quota di parole con un tipo "vicino" (a una modifica); parole uguali alla precedente
  contatto (1)             informazione mutua ultimo glifo -> primo glifo successivo, al netto delle parole rimescolate nella riga (ia08)
  eco (8)                  per quattro fasce (riga in corso; riga sopra; 2-7 righe sopra; 8 o piu' sopra): eccesso di parole UGUALI e di
                           parole a UNA modifica nella fascia, rispetto alla stessa fascia di un'altra pagina dello stesso gruppo
                           (stessa lingua e sezione dove nota: correzione del riferimento "pagina a caso", revisione A4)
  bordi (6)                distanza di Jensen e Shannon fra prima/ultima parola di riga e parole interne (primo glifo, ultimo glifo,
                           lunghezza)
Fuori dalla stima (`NOMI_EXTRA`, per la verifica): entropie H4 e H5; righe uguali alla riga sopra e a 2 righe; parole nella riga a
distanza 1-3; esponente di Heaps; somiglianza fra pagine consecutive meno quella fra pagine a caso; ripetizioni interne.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NOMI = ['lung_media', 'lung_sd', 'H0', 'H1', 'H2', 'H3', 'H_primo', 'H_ultimo',
        'tipi_su_parole', 'hapax_su_parole', 'quota_una_pagina', 'top10', 'quota_vicini', 'ripetute_subito',
        'contatto',
        'eco_uguali_riga', 'eco_uguali_R1', 'eco_uguali_R247', 'eco_uguali_R8',
        'eco_mod_riga', 'eco_mod_R1', 'eco_mod_R247', 'eco_mod_R8',
        'bordo_inizio_primo', 'bordo_inizio_ultimo', 'bordo_inizio_lung', 'bordo_fine_primo', 'bordo_fine_ultimo', 'bordo_fine_lung']
NOMI_EXTRA = ['H4', 'H5', 'righe_sopra_uguali', 'righe_2sopra_uguali', 'in_riga_d1', 'in_riga_d2', 'in_riga_d3', 'heaps',
              'consecutive_meno_caso', 'righe4_ripetute', 'ripetute_riga_sopra']
FASCE_ECO = OrderedDict([('riga', [0, 1, 2]), ('R1', [3]), ('R247', [4, 5]), ('R8', [6])])
ORDINE_MAX_H = 5


# ---------------------------------------------------------------- entropie dei glifi dentro la parola

def _flusso(parole, k_pad):
    """Sequenza piatta: per ogni parola k_pad zeri (inizio), gli id dei glifi (>= 2) e un 1 (fine parola)."""
    idx = {}
    flat = []
    pad = [0] * k_pad
    for w in parole:
        flat.extend(pad)
        for g in w:
            i = idx.get(g)
            if i is None:
                i = idx[g] = len(idx) + 2
            flat.append(i)
        flat.append(1)
    return np.array(flat, dtype=np.int64), len(idx) + 2


def _H(codici):
    if len(codici) == 0:
        return 0.0
    _, c = np.unique(codici, return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def entropie_glifi(parole, ordini=(1, 2, 3)):
    """H0 e le entropie condizionali di ordine `ordini` (bit per glifo, con la fine parola come simbolo), plug-in. Restituisce un dizionario."""
    k_pad = max(ordini)
    arr, B = _flusso(parole, k_pad)
    out = OrderedDict()
    bersaglio = arr != 0
    out['H0'] = _H(arr[arr >= 2])
    for k in ordini:
        n = len(arr)
        ctx = np.zeros(n, dtype=np.int64)
        for m in range(1, k + 1):
            ctx[m:] += arr[:n - m] * (B ** (m - 1))
        mask = bersaglio.copy()
        mask[:k] = False
        joint = ctx[mask] * B + arr[mask]
        out['H%d' % k] = _H(joint) - _H(ctx[mask])
    primo = np.zeros(len(arr), dtype=bool)
    primo[k_pad:] = (arr[k_pad - 1:-1] == 0) & (arr[k_pad:] >= 2)
    out['H_primo'] = _H(arr[primo])
    ult = np.zeros(len(arr), dtype=bool)
    ult[:-1] = (arr[1:] == 1) & (arr[:-1] >= 2)
    out['H_ultimo'] = _H(arr[ult])
    return out


# ---------------------------------------------------------------- eco con riferimento nello stesso gruppo

def deranga_nei_gruppi(nomi, gruppi, seme):
    """Permutazione delle pagine senza punti fissi, dentro ogni gruppo (stessa lingua e sezione); le pagine che restano sole in un
    gruppo si permutano fra loro. `gruppi`: pagina -> etichetta (o None: un solo gruppo)."""
    nomi = list(nomi)
    if gruppi is None:
        return R.derangement(nomi, seme)
    per = OrderedDict()
    for p in nomi:
        per.setdefault(gruppi.get(p, '?'), []).append(p)
    perm, avanzi = {}, []
    for i, (g, ps) in enumerate(per.items()):
        if len(ps) >= 2:
            perm.update(R.derangement(ps, seme * 31 + i))
        else:
            avanzi.extend(ps)
    if len(avanzi) >= 2:
        perm.update(R.derangement(avanzi, seme * 31 + 977))
    elif len(avanzi) == 1:
        altri = [p for p in nomi if p != avanzi[0]]
        perm[avanzi[0]] = altri[0] if altri else avanzi[0]
    return perm


def conti_eco(pagine, gruppi=None, seme=1):
    """Matrice S (9 x 7) di `rifarlo_ritocchi.conti_eco`, sommata sulle pagine, con la pagina di riferimento dello stesso gruppo."""
    nomi = list(pagine)
    perm = deranga_nei_gruppi(nomi, gruppi, seme)
    ws = {p: [w for _, r in pagine[p] for w in r] for p in nomi}
    nb = R.vicini_tipi(w for x in ws.values() for w in x)
    S = np.zeros((9, R.NB))
    for p in nomi:
        L, J, ls = R.struttura(pagine[p])
        a, b = R.intervalli_bande(L, J, ls)
        S += R.conti_eco(ws[p], ws[perm[p]], a, b, nb, None)
    return S


def eco_fasce(S):
    """Otto numeri: eccesso di parole uguali e a una modifica, per le quattro fasce, sul totale delle parole con la fascia non vuota."""
    out = OrderedDict()
    for nome, B in FASCE_ECO.items():
        den = max(float(S[6][B].sum()), 1.0)
        out['eco_uguali_' + nome] = float((S[0][B].sum() - S[1][B].sum()) / den)
    for nome, B in FASCE_ECO.items():
        den = max(float(S[6][B].sum()), 1.0)
        out['eco_mod_' + nome] = float((S[4][B].sum() - S[5][B].sum()) / den)
    return out


# ---------------------------------------------------------------- statistiche di sintesi

def statistiche(pagine, gruppi=None, seme=1):
    """Le 29 statistiche di sintesi (dizionario nome -> numero, nell'ordine di NOMI). Un valore non definito (ad esempio i bordi su un
    testo senza righe di 5 parole) vale 0."""
    righe = [ws for rows in pagine.values() for _, ws in rows]
    parole = [w for ws in righe for w in ws]
    N = len(parole)
    out = OrderedDict()
    lung = np.array([len(w) for w in parole], dtype=float)
    out['lung_media'] = float(lung.mean())
    out['lung_sd'] = float(lung.std())
    out.update(entropie_glifi(parole))
    cont = Counter(parole)
    out['tipi_su_parole'] = len(cont) / N
    out['hapax_su_parole'] = sum(1 for c in cont.values() if c == 1) / N
    pag_di = {}
    for p, rows in pagine.items():
        for _, ws in rows:
            for w in ws:
                pag_di.setdefault(w, set()).add(p)
    out['quota_una_pagina'] = sum(cont[w] for w, ps in pag_di.items() if len(ps) == 1) / N
    out['top10'] = sum(c for _, c in cont.most_common(10)) / N
    vic = R.vicini_tipi(list(cont))
    out['quota_vicini'] = sum(cont[w] for w in vic) / N
    coppie = [(a, b) for ws in righe for a, b in zip(ws, ws[1:])]
    out['ripetute_subito'] = (sum(1 for a, b in coppie if a == b) / len(coppie)) if coppie else 0.0
    out['contatto'] = float(R.mi_contatto(pagine, nrim=3, seme=seme))
    out.update(eco_fasce(conti_eco(pagine, gruppi, seme)))
    fb = AP.firma_bordi(pagine)
    for k in ('inizio_primo', 'inizio_ultimo', 'inizio_lung', 'fine_primo', 'fine_ultimo', 'fine_lung'):
        v = fb.get(k)
        out['bordo_' + k] = float(v) if v is not None else 0.0
    return OrderedDict((k, float(out[k])) for k in NOMI)


def statistiche_extra(pagine, seme=1):
    """Statistiche NON usate nella stima (per la verifica predittiva): entropie di ordine 4 e 5, ripetizioni di righe e di parole a
    distanza, esponente di Heaps, somiglianza fra pagine consecutive (meglio su libri interi: nei quarti le pagine consecutive non lo sono)."""
    righe_pp = OrderedDict((p, [list(ws) for _, ws in rows]) for p, rows in pagine.items())
    righe = [ws for rr in righe_pp.values() for ws in rr]
    parole = [w for ws in righe for w in ws]
    out = OrderedDict()
    e = entropie_glifi(parole, ordini=(1, 2, 3, 4, 5))
    out['H4'], out['H5'] = e['H4'], e['H5']
    ru = AP.righe_uguali_a_distanza(righe_pp, dmax=2, min_parole=3)
    out['righe_sopra_uguali'] = ru[1] if ru[1] is not None else 0.0
    out['righe_2sopra_uguali'] = ru[2] if ru[2] is not None else 0.0
    pr = AP.parole_in_riga_a_distanza(righe_pp, dmax=3)
    for d in (1, 2, 3):
        out['in_riga_d%d' % d] = pr[d] if pr[d] is not None else 0.0
    vistos, V = set(), []
    for i, w in enumerate(parole):
        vistos.add(w)
        V.append(len(vistos))
    n = len(parole)
    out['heaps'] = float(math.log(V[-1] / max(V[n // 2 - 1], 1)) / math.log(n / (n // 2))) if n >= 100 else 0.0
    insiemi = [set(w for _, ws in rows for w in ws) for rows in pagine.values()]
    rnd = random.Random(seme)

    def jac(a, b):
        return len(a & b) / max(len(a | b), 1)
    cons = [jac(a, b) for a, b in zip(insiemi, insiemi[1:])]
    caso = []
    for _ in range(len(cons)):
        i, j = rnd.sample(range(len(insiemi)), 2)
        caso.append(jac(insiemi[i], insiemi[j]))
    out['consecutive_meno_caso'] = float(np.mean(cons) - np.mean(caso)) if cons else 0.0
    rr = None
    try:
        import imitatore_misure as MS
        rr = MS.ripetizioni_interne(righe_pp)
    except Exception:
        rr = None
    if rr:
        k4, k5 = 'righe uguali a una precedente nella pagina (>= 4 parole)', 'righe uguali alla riga sopra (>= 2 parole)'
        out['righe4_ripetute'] = rr[k4][0] / max(rr[k4][1], 1)
        out['ripetute_riga_sopra'] = rr[k5][0] / max(rr[k5][1], 1)
    else:
        out['righe4_ripetute'] = out['ripetute_riga_sopra'] = 0.0
    return OrderedDict((k, float(out[k])) for k in NOMI_EXTRA)


def vettore(d, nomi=None):
    nomi = nomi or NOMI
    return np.array([d[k] for k in nomi], dtype=float)


def prova_statistiche():
    """Prove interne su testi inventati: entropie note, invarianza per rinomina dei glifi, valori finiti, gruppi, extra."""
    ris = OrderedDict()
    rnd = random.Random(5)
    # testo di 3 glifi equiprobabili e indipendenti dentro parole di lunghezza fissa 4: H0 = log2(3), H1 = H2 = H3 vicino a log2(3) (la fine parola e' certa)
    pagine = OrderedDict()
    for i in range(40):
        rows = []
        for j in range(10):
            rows.append((j == 0, [tuple(rnd.choice('abc') for _ in range(4)) for _ in range(8)]))
        pagine['P%d' % i] = rows
    e = entropie_glifi([w for r in pagine.values() for _, ws in r for w in ws])
    ris['H0 di 3 glifi equiprobabili vicino a log2(3)'] = abs(e['H0'] - math.log2(3)) < 0.02
    h25 = -(0.25 * math.log2(0.25) + 0.75 * math.log2(0.75))
    atteso_h1 = (math.log2(3) + 4 * (h25 + 0.75 * math.log2(3))) / 5      # dopo un glifo: fine parola (1/4) o uno dei 3 glifi (3/4)
    ris['H1 uguale al valore calcolato a mano (log2 3 + 4 volte (h(1/4) + 3/4 log2 3)) / 5'] = abs(e['H1'] - atteso_h1) < 0.03
    # parole tutte uguali: entropie zero
    uguali = OrderedDict((p, [(ini, [('a', 'b', 'c')] * len(ws)) for ini, ws in rows]) for p, rows in pagine.items())
    e2 = entropie_glifi([w for r in uguali.values() for _, ws in r for w in ws])
    ris['parole tutte uguali: H1, H2, H3 zero'] = max(e2['H1'], e2['H2'], e2['H3']) < 1e-9
    s = statistiche(pagine)
    ris['29 statistiche, tutte finite'] = len(s) == 29 and all(math.isfinite(v) for v in s.values())
    # rinomina dei glifi: stesse statistiche
    mappa = {'a': 'x', 'b': 'yy', 'c': 'zzz'}
    ren = OrderedDict((p, [(ini, [tuple(mappa[g] for g in w) for w in ws]) for ini, ws in rows]) for p, rows in pagine.items())
    s2 = statistiche(ren)
    ris['invarianza per rinomina dei glifi'] = all(abs(s[k] - s2[k]) < 1e-9 for k in s)
    # eco piantata: testo in cui la meta' delle parole e' la parola subito prima -> eco_uguali_riga alta
    eco = OrderedDict()
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            ws = list(ws)
            for i in range(1, len(ws)):
                if rnd.random() < 0.5:
                    ws[i] = ws[i - 1]
            nr.append((ini, ws))
        eco[p] = nr
    se = statistiche(eco)
    ris['eco piantata: eco_uguali_riga sale di oltre 0,2'] = se['eco_uguali_riga'] - s['eco_uguali_riga'] > 0.2
    ris['eco piantata: ripetute_subito vicino a 0,5'] = abs(se['ripetute_subito'] - 0.5) < 0.1
    # gruppi: la permutazione resta dentro il gruppo
    nomi = ['P%d' % i for i in range(12)]
    gr = {p: ('A' if i < 6 else 'B') for i, p in enumerate(nomi)}
    perm = deranga_nei_gruppi(nomi, gr, 3)
    ris['riferimento dentro il gruppo, senza punti fissi'] = all(gr[p] == gr[q] and p != q for p, q in perm.items())
    ex = statistiche_extra(pagine)
    ris['statistiche extra finite'] = len(ex) == len(NOMI_EXTRA) and all(math.isfinite(v) for v in ex.values())
    ris['nessun nome in comune fra sintesi ed extra'] = not set(NOMI) & set(NOMI_EXTRA)
    return ris


if __name__ == '__main__':
    r = prova_statistiche()
    for k, v in r.items():
        print('%-60s %s' % (k, 'ok' if v else 'FALLITA'))
    sys.exit(0 if all(r.values()) else 1)
