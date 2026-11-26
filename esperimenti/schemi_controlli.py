# -*- coding: utf-8 -*-
"""IA44, ricerca (a): i controlli. Tutto su testi NON Voynich, sopra la layout (numero di parole per pagina, fascicolo, mano) dell'erbario.

Negativi (nessuno schema):
  v21      libro v21 senza messaggio (chiavi 1-24), una pagina per pagina di erbario che il libro ha;
  naibbe   libro Naibbe (16 libri di IA28);
  timm     testo di Timm e Schinner (semi 1, 2, 3, 4, 19) tagliato nelle lunghezze delle pagine;
  latino   Macer Floridus + Isidoro XVII, cifrati parola per parola SENZA schema, senza e con meta' riempitivo v21 (il negativo piu'
           vicino a un erbario vero: ha i temi delle piante);
  rimesc   libro v21 con le parole rimescolate fra le pagine dello stesso fascicolo e mano (un campione del nullo 'tok').
Positivi (schema piantato nel latino cifrato parola per parola, impaginato come l'erbario del Voynich):
  'Q4'  quattro qualita' (4 parole, una per pagina), tutte le pagine, senza riempitivo;
  'QG'  quattro qualita' e quattro gradi (8 parole, due per pagina), meta' dei segni sostituita da parole del v21 (riempitivo);
  'QGd' come QG ma le parole piantate non sono riservate (compaiono anche per caso altrove) e solo l'80% delle pagine ha lo schema;
  'QGq100', 'QGq60', 'QGq40', 'QGq25' come QGd con il 100%, 60%, 40%, 25% delle pagine con lo schema (la curva di potenza);
  'CS'  caldo/freddo e secco/umido (2 + 2 parole), dentro il primo terzo della pagina, meta' riempitivo.
"""
import os
import random
import sys
import time

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import schemi_dati as D          # noqa: E402
import schemi_libri as L         # noqa: E402
import schemi_erbario as E       # noqa: E402

PROB = {'qualita': (0.35, 0.25, 0.25, 0.15), 'gradi': (0.10, 0.25, 0.40, 0.25), 'caldo_freddo': (0.5, 0.5), 'secco_umido': (0.5, 0.5)}
SCHEMI = {
    'Q4': dict(gruppi=('qualita',), riempitivo=0.0, riservate=True, quota=1.0, regione='qualsiasi'),
    'QG': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=True, quota=1.0, regione='qualsiasi'),
    'QGd': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=False, quota=0.8, regione='qualsiasi'),
    'QGq100': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=False, quota=1.0, regione='qualsiasi'),
    'QGq60': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=False, quota=0.6, regione='qualsiasi'),
    'QGq40': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=False, quota=0.4, regione='qualsiasi'),
    'QGq25': dict(gruppi=('qualita', 'gradi'), riempitivo=0.5, riservate=False, quota=0.25, regione='qualsiasi'),
    'CS': dict(gruppi=('caldo_freddo', 'secco_umido'), riempitivo=0.5, riservate=True, quota=1.0, regione='inizio'),
}
RANGO_PIANTATE = (80, 700)       # le parole piantate: tipi del vocabolario v21 di rango 80-700 (frequenza media)

_CACHE = {}


def libro_v21_cache(k):
    if ('v21', k) not in _CACHE:
        _CACHE[('v21', k)] = L.libro_v21(k)
    return _CACHE[('v21', k)]


def una_lettera(a, b):
    """Vera se le due parole sono uguali o differiscono per una lettera (sostituzione, inserzione, cancellazione)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


# ---------------------------------------------------------------- dalla layout alle pagine

def pagine_di_libro(libro, pagine_layout):
    """Per le pagine della layout che il libro ha: (liste di parole, pagine tenute)."""
    tenute = [p for p in pagine_layout if p['pagina'] in libro]
    return [[w for _, ws in libro[p['pagina']] for w in ws] for p in tenute], tenute


def pagine_da_flusso(flusso, pagine_layout, inizio=0):
    out, i, n = [], inizio, len(flusso)
    for p in pagine_layout:
        out.append([flusso[(i + j) % n] for j in range(p['n'])])
        i += p['n']
    return out


# ---------------------------------------------------------------- negativi

def negativo(famiglia, indice, unita, layout):
    """(pagine, strati) di un libro negativo per l'unita' 'A' o 'B' della layout. `indice` e' la chiave/seme della famiglia."""
    lay = layout[unita]
    if famiglia == 'v21':
        pag, ten = pagine_di_libro(libro_v21_cache(indice), lay)
    elif famiglia == 'naibbe':
        pag, ten = pagine_di_libro(L.libro_naibbe(indice), lay)
    elif famiglia == 'timm':
        flusso = L.flusso_timm(indice)
        pag, ten = pagine_da_flusso(flusso, lay), lay
    elif famiglia in ('latino', 'latino_rif'):
        pag, ten = latino_cifrato(lay, indice, riempitivo=0.5 if famiglia == 'latino_rif' else 0.0), lay
    elif famiglia == 'rimesc':
        base, ten = pagine_di_libro(libro_v21_cache(indice), lay)
        _, token = E.vocabolario(base)
        voc = E.vocabolario(base)[0]
        rnd = np.random.RandomState(L.seme_str('rimesc', indice, unita))
        tok = E.rimescola_token(token, D.strati(ten), rnd)
        pag = [[voc[i] for i in a] for a in tok]
    else:
        raise ValueError(famiglia)
    return pag, D.strati(ten)


# ---------------------------------------------------------------- latino cifrato, con o senza schema piantato

def _scegli_piantate(vocabolario, quante, rnd, escluse=()):
    a, b = RANGO_PIANTATE
    pool = [w for w in vocabolario[a:b] if len(w) >= 3]
    rnd.shuffle(pool)
    scelte = []
    for w in pool:
        if all(not una_lettera(w, x) for x in list(scelte) + list(escluse)):
            scelte.append(w)
        if len(scelte) == quante:
            break
    return scelte


def latino_cifrato(pagine_layout, seme, riempitivo=0.0, schema=None, controllo=None):
    """Pagine di latino cifrato parola per parola (Macer + Isidoro XVII) con la lunghezza delle pagine della layout. Se `schema` e'
    uno dei SCHEMI, vi pianta lo schema; ritorna le pagine (e, con `controllo` = dict, riempie controllo['piantate'] con i gruppi)."""
    cfg = SCHEMI[schema] if schema else None
    rnd = random.Random(L.seme_str('lat', seme, schema))
    chiavi = sorted(set(L.CHIAVI_V21))
    k_cifra, k_fill = rnd.sample(chiavi, 2)
    voc = L.vocabolario_ordinato(libro_v21_cache(k_cifra))
    gruppi = {}
    if cfg:
        escluse = []
        for g in cfg['gruppi']:
            n = len(PROB[g])
            gruppi[g] = _scegli_piantate(voc, n, rnd, escluse)
            escluse += gruppi[g]
    riservate = [w for ws in gruppi.values() for w in ws] if (cfg and cfg['riservate']) else []
    flusso, _ = L.cifra_latino(L.flusso_latino(seme), voc, seme, riservate=riservate)
    fill = [w for righe in libro_v21_cache(k_fill).values() for _, ws in righe for w in ws if w not in set(riservate)]
    riemp = cfg['riempitivo'] if cfg else riempitivo
    pagine = pagine_da_flusso(flusso, pagine_layout, inizio=rnd.randrange(len(flusso)))
    jf = rnd.randrange(len(fill))
    if riemp > 0:
        for ps in pagine:
            for j in range(len(ps)):
                if rnd.random() < riemp:
                    ps[j] = fill[jf % len(fill)]
                    jf += 1
    if cfg:
        for ps in pagine:
            if rnd.random() >= cfg['quota']:
                continue
            usate = set()
            for g, parole in gruppi.items():
                classe = rnd.choices(range(len(parole)), weights=PROB[g])[0]
                n = len(ps)
                limite = n // 3 if cfg['regione'] == 'inizio' else n
                libere = [j for j in range(max(limite, 1)) if j not in usate]
                j = rnd.choice(libere)
                usate.add(j)
                ps[j] = parole[classe]
    if controllo is not None:
        controllo['piantate'] = gruppi
    return pagine


# ---------------------------------------------------------------- una prova completa su un'unita'

def prova_unita(pagine, strati, k_nulli, seme_nulli, piantate=None):
    """Esegue la ricerca (a) su un'unita': osservato, k_nulli campioni per ciascuno dei due nulli. Ritorna un dict di soli numeri
    (con, se `piantate`, il recupero dello schema)."""
    U = E.Unita(pagine, strati)
    oss, gruppi = U.osservato()
    nulli = {}
    for t in E.NULLI:
        nulli[t] = np.array([U.nullo(t, seme_nulli * 100003 + 7 * i + (0 if t == 'tok' else 1)) for i in range(k_nulli)])
    ev = E.valuta(oss, nulli)
    pf = E.p_finale([ev])
    out = dict(p=pf['p'], per_tipo={t: dict(p=v['p'], stat=v['stat'], variante=list(v['variante']), indice=v['indice'], nullo_p95=v['nullo_p95'])
                                    for t, v in pf['per_tipo'].items()},
               oss=[round(float(x), 4) for x in oss], N=U.N, V=U.V)
    if piantate:
        piant = {w for ws in piantate.values() for w in ws}
        j = pf['per_tipo']['tok']['indice'] // 2
        gruppo = [U.voc[i] for i in gruppi[j]]
        m = len(gruppo)
        out['recuperate'] = sum(w in piant for w in gruppo)
        out['taglia_gruppo'] = m
        out['recupero'] = bool(m and sum(w in piant for w in gruppo) >= int(np.ceil(0.75 * m)))
    return out


def lavoro(args):
    """Per i processi: args = dict(tipo='neg'|'pos', famiglia/schema, indice, unita, K). Ritorna dict di soli numeri."""
    t0 = time.time()
    layout = D.layout_erbario('ZL')
    unita = args['unita']
    if args['tipo'] == 'neg':
        pag, strati = negativo(args['famiglia'], args['indice'], unita, layout)
        r = prova_unita(pag, strati, args['K'], args['indice'] + 1)
    else:
        ctrl = {}
        pag = latino_cifrato(layout[unita], args['indice'], schema=args['schema'], controllo=ctrl)
        r = prova_unita(pag, D.strati(layout[unita]), args['K'], args['indice'] + 1, piantate=ctrl['piantate'])
    r.update({k: v for k, v in args.items() if k != 'K'})
    r['K'] = args['K']
    r['secondi'] = round(time.time() - t0, 1)
    return r
