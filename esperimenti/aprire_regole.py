# -*- coding: utf-8 -*-
"""Supporto di ia17 (modulo, non e' un esperimento): regole leggibili distillate dall'imitatore di ia16.

Che cosa c'e' qui, in parole semplici
- `costruisci_D`: mette in un'unica tabella i bit di ogni parola delle pagine tenute fuori, letti dall'imitatore (file in cache protetta,
  scritti dai lavori `leggi` di ia17), nel formato che `vedere_regole.py` (ia13) sa leggere.
- `regole_da_D`: come `regole_testo` di ia13: dalla "perdita" di ogni parola (y) tabelle di pezzi e alberi di decisione provati su pagine mai viste
  (R2 fuori campione, intervalli col bootstrap sulle pagine), il soffitto, e in piu' le "regole di eco": per ogni parola la distanza in righe
  dell'eco piu' vicina (parola uguale o a una modifica gia' scritta) e se c'e' entro k righe; tabelle e alberi solo con le regole di eco, solo
  con i pezzi di ia13, e con tutte e due.
- Le regole con glifi veri si scrivono solo nella cache protetta (`scrivi_regole`); i risultati hanno codici anonimi (rango di frequenza).
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import os
from collections import Counter, OrderedDict

import numpy as np

import ia13_cosa_vede_rete as I13
import vedere_regole as VR

FOGLIE = (4, 8, 16, 32)
K_ECO = (1, 2, 3, 5, 10)
RIF_IA13 = OrderedDict(albero4=0.095, albero8=0.137, albero16=0.193, albero32=0.246, migliore_tabella=0.268, contatto=0.263, soffitto=0.674)


def riferimenti_ia13(percorso):
    """I numeri di ia13 (testo `vere`) dal suo file di risultati, se c'e'; altrimenti quelli scritti nella preregistrazione di ia17."""
    import json
    out = OrderedDict(RIF_IA13)
    out['fonte'] = 'preregistrazione ia17 (numeri letti da risultati/ia13_cosa_vede_rete.json il 21/11/2026)'
    if os.path.exists(percorso):
        try:
            r = json.load(open(percorso, encoding='utf-8'))['testi']['vere']['regole']
            for L in (4, 8, 16, 32):
                out['albero%d' % L] = r['albero'][str(L)]['punto']
            fam = r['famiglie']
            out['migliore_tabella'] = max(v['R2']['punto'] for k, v in fam.items() if k != 'la parola intera')
            out['contatto'] = fam['contatto: ultimo(prec) -> primo']['R2']['punto']
            out['soffitto'] = r['soffitto']
            out['fonte'] = percorso
        except Exception:                                                     # noqa: BLE001
            pass
    return out


# ---------------------------------------------------------------- la tabella delle parole

def costruisci_D(liste, cartelle_target):
    """`liste`: lista (una per replica) di liste (una per piega) di dizionari caricati dai file `leggi` (stesse parole nello stesso ordine).
    Restituisce D con `delta_ord` (parole, repliche x rimescolamenti: solo i glifi), `delta_mem` (parole, repliche: bit in piu' senza la
    memoria della pagina) e le informazioni sull'eco."""
    rep = []
    for r_ in liste:
        d = OrderedDict()
        for k in ('J', 'nl', 'riga', 'dl_eq', 'dl_mod', 'mem_eq', 'mem_mod'):
            d[k] = np.concatenate([p['w_' + k] for p in r_])
        d['fold'] = np.concatenate([np.full(len(p['w_J']), p['piega'], dtype=np.int64) for p in r_])
        d['pagina'] = [n for p in r_ for n in p['nomi_pagine_parola']]
        d['parola'] = [w for p in r_ for w in p['parole']]
        d['rim'] = np.concatenate([p['rim_g'] for p in r_], axis=0)
        for nome in cartelle_target:
            d[nome] = np.concatenate([p['cost'][nome].sum(1) - p['cost']['pieno'].sum(1) for p in r_])
        rep.append(d)
    base = rep[0]
    for d in rep[1:]:
        if len(d['J']) != len(base['J']) or not np.array_equal(d['J'], base['J']) or d['pagina'] != base['pagina']:
            return None
    D = OrderedDict()
    for k in ('J', 'nl', 'riga', 'fold', 'dl_eq', 'dl_mod', 'pagina', 'parola'):
        D[k] = base[k]
    D['mem_eq'] = np.any([d['mem_eq'] for d in rep], axis=0)
    D['mem_mod'] = np.any([d['mem_mod'] for d in rep], axis=0)
    D['delta_ord'] = np.concatenate([d['rim'] for d in rep], axis=1)
    for nome in cartelle_target:
        D['delta_' + nome] = np.stack([d[nome] for d in rep], axis=1)
    D['pagine'] = sorted(set(D['pagina']))
    pos = {p: i for i, p in enumerate(D['pagine'])}
    D['pag'] = np.array([pos[p] for p in D['pagina']], dtype=np.int64)
    D['n_repliche'] = len(rep)
    return D


def D_semplice(L, nf, bersagli):
    """D per un solo modello letto (i controlli sintetici): le pagine si dividono in `nf` pieghe finte (numero d'ordine della pagina modulo nf).
    `L`: dizionario di `leggi_modello` (in memoria). Bersagli: i nomi di condizione (differenza di bit della parola con `pieno`)."""
    n = len(L['w_pag'])
    D = OrderedDict()
    for k in ('J', 'nl', 'riga', 'dl_eq', 'dl_mod', 'mem_eq', 'mem_mod'):
        D[k] = L['w_' + k]
    D['fold'] = (L['w_pag'] % nf).astype(np.int64)
    D['pagina'] = [L['pagine'][i] for i in L['w_pag']]
    D['parola'] = [tuple(int(x) for x in L['w_gl'][L['w_off'][i]:L['w_off'][i + 1]]) for i in range(n)]
    D['pagine'] = sorted(set(D['pagina']))
    pos = {p: i for i, p in enumerate(D['pagine'])}
    D['pag'] = np.array([pos[p] for p in D['pagina']], dtype=np.int64)
    for b in bersagli:
        D['delta_' + b] = (L['cost'][b].sum(1) - L['cost']['pieno'].sum(1)).astype(np.float64)[:, None]
    D['n_repliche'] = 1
    return D


def D_per_target(D, nome):
    """Copia di D nel formato di vedere_regole.tabella_regole: 'delta' (parole, colonne) = il bersaglio scelto."""
    d = dict(D)
    d['delta'] = np.asarray(D['delta_' + nome], dtype=np.float64)
    return d


# ---------------------------------------------------------------- regole di eco

def classe_eco(dl, in_mem):
    """0 nessun'eco, 1 stessa riga, 2 una riga sopra, 3 due, 4 tre, 5 quattro-cinque, 6 sei-nove, 7 dieci-diciannove, 8 venti o piu',
    9 solo nella coda della pagina precedente."""
    c = np.zeros(len(dl), dtype=np.int64)
    pos = dl >= 0
    c[pos] = 1 + np.digitize(dl[pos], [1, 2, 3, 4, 6, 10, 20])
    c[(~pos) & in_mem] = 9
    return c


def extra_eco(D, R):
    """Per le parole di R (con una parola prima nella riga): classi di eco uguale e a una modifica, e flag 'entro k righe'."""
    idx = R['idx']
    dle, dlm = D['dl_eq'][idx], D['dl_mod'][idx]
    me, mm = D['mem_eq'][idx], D['mem_mod'][idx]
    ce, cm = classe_eco(dle, me), classe_eco(dlm, mm)
    ent = OrderedDict()
    for k in K_ECO:
        ent[k] = ((dle >= 0) & (dle <= k), (dlm >= 0) & (dlm <= k))
    ent['pagina'] = ((dle >= 0) | me, (dlm >= 0) | mm)
    return OrderedDict(ce=ce, cm=cm, dle=dle, dlm=dlm, me=me, mm=mm, entro=ent)


def famiglie_eco(R, E):
    f = OrderedDict()
    f['eco: classe di distanza (uguale, a una modifica)'] = list(zip(E['ce'].tolist(), E['cm'].tolist()))
    for k in K_ECO + ('pagina',):
        a, b = E['entro'][k]
        f['eco: c\'e\' entro %s righe (uguale, a una modifica)' % (k if k != 'pagina' else 'la pagina')] = list(zip(a.tolist(), b.tolist()))
    mn = np.where(E['ce'] == 0, E['cm'], np.where(E['cm'] == 0, E['ce'], np.minimum(E['ce'], E['cm'])))
    f['eco: classe piu\' vicina e posto nella riga'] = [(int(c), min(int(j), 3)) for c, j in zip(mn, R['J'])]
    return f


def colonne_eco(R, E):
    """Colonne per l'albero con le sole regole di eco. Restituisce (X, nomi)."""
    col, nomi = [], []

    def agg(n, v):
        nomi.append((n, 0))
        col.append(np.asarray(v, dtype=np.float32))
    for k in K_ECO + ('pagina',):
        a, b = E['entro'][k]
        agg('eco uguale entro %s' % k, a)
        agg('eco a una modifica entro %s' % k, b)
    agg('righe dall\'eco uguale (99 = nessuna)', np.where(E['dle'] >= 0, E['dle'], 99))
    agg('righe dall\'eco a una modifica (99 = nessuna)', np.where(E['dlm'] >= 0, E['dlm'], 99))
    agg('eco uguale nella pagina precedente', E['me'])
    agg('eco a una modifica nella pagina precedente', E['mm'])
    agg('posto', R['J'])
    agg('posto dalla fine', R['e'])
    return np.stack(col, axis=1), nomi


def codici_anonimi(parole):
    c = Counter(g for w in parole for g in w)
    return {g: '#%d' % (i + 1) for i, (g, _) in enumerate(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))}


def cod_el(x, cod):
    if isinstance(x, (int, np.integer)):
        return cod.get(int(x), '?')
    if isinstance(x, tuple):
        if x == VR.NA:
            return 'NA'
        return ''.join(cod_el(y, cod) for y in x) if all(isinstance(y, (int, np.integer)) for y in x) else '(' + ','.join(cod_el(y, cod) for y in x) + ')'
    return str(x)


def regole_da_D(D, nome_target, con_eco, segni=None, percorso_cache=None, etichetta=''):
    """R2 fuori campione di tabelle e alberi per il bersaglio `nome_target` ('ord' o 'mem...'). Restituisce un dizionario di numeri e codici
    anonimi. Se `percorso_cache` e' dato scrive le regole con i glifi veri (solo cache protetta)."""
    Dt = D_per_target(D, nome_target)
    R = VR.tabella_regole(Dt)
    P = len(D['pagine'])
    y = R['y']
    cod = codici_anonimi(D['parola'])
    if len(set(D['fold'].tolist())) < 2:
        return None
    out = OrderedDict(righe=int(len(y)), colonne=int(Dt['delta'].shape[1]), delta_medio=float(y.mean()), deviazione=float(y.std()))
    out['soffitto'] = VR.soffitto(R['yr']) if R['yr'].shape[1] > 1 else float('nan')
    fam = VR.chiavi_famiglie(R)
    E = extra_eco(D, R) if con_eco else None
    fam_eco = famiglie_eco(R, E) if con_eco else OrderedDict()
    out['famiglie'] = OrderedDict()
    testo = []
    for gruppo, fams in (('pezzi', fam), ('eco', fam_eco)):
        for k, chiavi in fams.items():
            codici, dic = VR.codifica(chiavi)
            sse, sst = VR.valuta_tabella(codici, y, R['fold'], R['pag'], P)
            voce = OrderedDict(gruppo=gruppo, celle=len(dic), R2=I13.r2v(sse, sst, P))
            celle, mu = VR.celle_top(codici, dic, y, 8)
            if percorso_cache:
                testo.append('## %s (media generale %.3f)' % (k, mu))
                for c in celle:
                    ch = c[0]
                    testo.append('  %s: n=%d media=%.3f contributo=%.1f' % (_chiave_vera(ch, segni), c[1], c[2], c[3]))
            out['famiglie'][k] = voce
    glifi = sorted({g for w in D['parola'] for g in w})
    Xp, nomi_p = VR.matrice_albero(R, glifi)
    gruppi = OrderedDict([('pezzi', (Xp, nomi_p))])
    if con_eco:
        Xe, nomi_e = colonne_eco(R, E)
        gruppi['eco'] = (Xe, nomi_e)
        gruppi['pezzi+eco'] = (np.concatenate([Xp, Xe], axis=1), nomi_p + nomi_e)
    out['albero'] = OrderedDict()
    for g, (X, nomi) in gruppi.items():
        out['albero'][g] = OrderedDict()
        for L in FOGLIE:
            sse, sst = VR.valuta_albero(X, y, R['fold'], R['pag'], P, L)
            out['albero'][g][L] = I13.r2v(sse, sst, P)
    from sklearn.tree import export_text
    X, nomi = gruppi['pezzi+eco' if con_eco else 'pezzi']
    lab = [('%s=%s' % (n[0], cod_el(n[1], cod)) if n[1] != 0 else n[0]) for n in nomi]
    t8 = VR.albero_intero(X, y, 8)
    out['albero8_codici'] = export_text(t8, feature_names=lab, max_depth=4, decimals=2).splitlines()
    out['domande_principali'] = [lab[i] for i in VR.prime_domande(t8, nomi, 5)]
    if percorso_cache:
        os.makedirs(os.path.dirname(percorso_cache), exist_ok=True)
        t16 = VR.albero_intero(X, y, 16)
        reale = [('%s=%s' % (n[0], _chiave_vera(n[1], segni)) if n[1] != 0 else n[0]) for n in nomi]
        with open(percorso_cache, 'w', encoding='utf-8', newline='\n') as f:
            f.write('# regole leggibili distillate dall\'imitatore (%s), con glifi veri: SOLO in cache protetta\n' % etichetta)
            f.write('# codici: %s\n' % ', '.join('%s=%s' % (v, (segni[k] if segni else k)) for k, v in cod.items()))
            f.write('\n'.join(testo) + '\n\n## albero a 16 foglie\n')
            f.write(export_text(t16, feature_names=reale, decimals=2) + '\n')
    mig = max(((k, v['R2']) for k, v in out['famiglie'].items() if k != 'la parola intera' and v['gruppo'] == 'pezzi'), key=lambda kv: kv[1].p)
    out['migliore_pezzi'] = mig[0]
    if con_eco:
        mige = max(((k, v['R2']) for k, v in out['famiglie'].items() if v['gruppo'] == 'eco'), key=lambda kv: kv[1].p)
        out['migliore_eco'] = mige[0]
    return out


def _chiave_vera(x, segni):
    if isinstance(x, (int, np.integer)):
        return segni[int(x)] if segni else str(x)
    if isinstance(x, tuple):
        if x == VR.NA:
            return 'NA'
        if all(isinstance(y, (int, np.integer)) for y in x):
            return ''.join(segni[int(y)] for y in x) if segni else str(x)
        return '(' + ','.join(_chiave_vera(y, segni) for y in x) + ')'
    return str(x)
