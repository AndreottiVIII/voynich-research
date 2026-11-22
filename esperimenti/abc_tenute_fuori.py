# -*- coding: utf-8 -*-
"""Misure TENUTE FUORI dalla stima per ia28 (modulo di supporto, non e' un esperimento).

Dopo la stima (ABC su statistiche classiche di quarti di libro) la verifica guarda grandezze che la stima NON ha usato, su libri
interi scritti con parametri pescati dalla distribuzione a posteriori di ogni famiglia:
  - statistiche classiche fuori dalla sintesi (`abc_statistiche.statistiche_extra`);
  - i giudici: e231 ed e266 (giudici del paper), A (rete sulla sorpresa dei segni, ia01/ia07) e K (n-grammi con memoria di pagina, ia11),
    tutti con le funzioni gia' esistenti, importate senza modificarle (`ia07_voynich_neurale`, `imitatore_misure`);
  - le misure di struttura di ia09, ia10 e ia20: copia netta, quota di copia rho, Λ (quota locale), contatto, D (ordine fra famiglie),
    G9 (vocabolario della pagina, giudice 2);
  - le misure di rete di ia02/ia03 (k90, GL, GR, R_rel, Q) con le funzioni di `ia14_quale_cifrario`.
Ogni misura e' un "lavoro" indipendente (`lavoro`), cosi' si dividono fra i processi. I libri stanno in `LIBRI_DIR` (pickle di pagine,
generati, mai testi del Voynich).

Punto d'aggancio del righello di IA26: se esiste `esperimenti/righello_*.py` (un solo file) con una funzione `misure(pagine)` che
restituisce un dizionario nome -> numero, `righello_misure(pagine)` la chiama e il risultato entra come misure "righello:*"; se il
modulo manca (o non ha quella funzione) restituisce None e la verifica va avanti senza (si dichiara nel rapporto).

Una pagina e' una lista di righe (inizio_paragrafo, [parola]); una parola e' una tupla di glifi (come ia01).
"""
import glob
import importlib
import os
import pickle
import sys
import time
import zlib
from collections import Counter, OrderedDict

import numpy as np

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

LIBRI_DIR = os.environ.get('LIBRI_DIR28', '')       # lo fissa il programma principale
MISURE_DIR = os.environ.get('MISURE_DIR28', '')
G9_NOME = 'G9 JSD pagina-manoscritto'
_C = {}


# ---------------------------------------------------------------- libri

def percorso_libro(nome):
    return os.path.join(LIBRI_DIR, nome.replace(':', '_') + '.pkl')


def _nome_valido(nome):
    return nome == 'vere' or nome == 'ctrl:parole' or nome.startswith('V21:') or os.path.exists(percorso_libro(nome))


def salva_libro(nome, pagine):
    os.makedirs(LIBRI_DIR, exist_ok=True)
    with open(percorso_libro(nome), 'wb') as f:
        pickle.dump(OrderedDict((p, [(bool(i), [tuple(w) for w in ws]) for i, ws in rows]) for p, rows in pagine.items()), f)


def carica_libro(nome):
    if nome == 'vere':
        import ia07_voynich_neurale as I7
        return I7.contesto_A()['vere']
    if nome == 'ctrl:parole':
        import ia07_voynich_neurale as I7
        return I7.libro_controllo_A('parole')
    if nome.startswith('V21:'):
        import ia07_voynich_neurale as I7
        return I7.libro_riferimento_A('a', int(nome.split(':')[1]))
    with open(percorso_libro(nome), 'rb') as f:
        return pickle.load(f)


def elenco_libri():
    return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(LIBRI_DIR, '*.pkl')))


def a_rr(pagine):
    """[(pagina, inizio, [parola come stringa])] per i giudici del paper e A."""
    return [(p, bool(ini), [''.join(w) for w in ws]) for p, rows in pagine.items() for ini, ws in rows]


def ranghi_glifi(pagine):
    """Glifi di un testo dal piu' al meno frequente (per il riallineamento dei nomi nei giudici)."""
    c = Counter(g for rows in pagine.values() for _, ws in rows for w in ws for g in w)
    return [g for g, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))]


# ---------------------------------------------------------------- righello di IA26 (punto d'aggancio)

def righello_misure(pagine):
    """Chiama `misure(pagine)` del modulo `righello_*` di IA26 se esiste; altrimenti None (si dichiara)."""
    if 'righello' not in _C:
        trovati = sorted(glob.glob(os.path.join(QUI, 'righello_*.py')))
        mod = None
        if len(trovati) == 1:
            m = importlib.import_module(os.path.splitext(os.path.basename(trovati[0]))[0])
            mod = m if hasattr(m, 'misure') else None
        _C['righello'] = mod
    if _C['righello'] is None:
        return None
    return OrderedDict(('righello:' + k, float(v)) for k, v in _C['righello'].misure(pagine).items())


# ---------------------------------------------------------------- lavori (uno per processo)

def lavoro_giudici(nome):
    """AUC dei giudici del paper e del giudice A per un libro (nelle pagine di `vere`)."""
    import ia07_voynich_neurale as I7
    pagine = carica_libro(nome)
    t = a_rr(pagine)
    out = OrderedDict()
    g = I7.giudica(t)
    out['AUC_e231'], out['AUC_e266'], out['pagine_giudicate'] = float(g['AUC_e231']), float(g['AUC_e266']), int(g['pagine_giudicate'])
    try:
        a = I7.giudice_A(I7.libro_A_da_righe(t))
        out['AUC_A'] = a.get('AUC_A')
        if a.get('A_errore'):
            out['A_errore'] = a['A_errore']
    except Exception as e:                                          # noqa: BLE001
        out['AUC_A'] = None
        out['A_errore'] = '%s: %s' % (type(e).__name__, str(e)[:200])
    return out


def lavoro_struttura(nome):
    """Copia netta, rho, Λ, contatto (ia09, ia08) e G9 (giudice 2) per un libro o per `vere`."""
    import e266_discriminatore_forte as e266
    import ia07_voynich_neurale as I7
    import imitatore_misure as MS
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows = c['vere']
        nf = k['vt266'][2]
        X = np.asarray(k['vt266'][1])
    else:
        rows = carica_libro(nome)
        tab = e266.tabella(I7.righe_ini(a_rr(rows)), k['rif266'])
        nf, X = tab[2], np.asarray(tab[1])
    j = next((i for i, n in enumerate(nf) if str(n).startswith(G9_NOME)), None)
    g9 = None if j is None else float(np.mean(X[:, j]))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    r = MS.lavoro_M('ia28:' + nome, pag, {p: c['fold'][p] for p in pag})
    s = MS.copia_netta_lambda(r)
    return OrderedDict([('G9', g9), ('copia_netta', float(s['copia_netta'])), ('lam', float(s['lam'])), ('rho', float(s['rho'])),
                        ('contatto', float(s['contatto']))])


def lavoro_K(f, nomi):
    """Giudice K sulla piega f: profili di sorpresa di `vere` e dei libri `nomi`; si salvano in MISURE_DIR."""
    import ia07_voynich_neurale as I7
    import imitatore_misure as MS
    c = I7.contesto_A()
    libri = OrderedDict((n, carica_libro(n)) for n in nomi)
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE_DIR, exist_ok=True)
    with open(os.path.join(MISURE_DIR, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('scelte_K', info), ('pagine_prova', len(prof['vere']))])


def auc_K(nomi, pieghe):
    """AUC del giudice K per ogni libro, dai profili salvati delle pieghe (a fine corsa)."""
    import ia07_voynich_neurale as I7
    import imitatore_misure as MS
    c = I7.contesto_A()
    lista = []
    for f in pieghe:
        with open(os.path.join(MISURE_DIR, 'K_f%d.pkl' % f), 'rb') as fh:
            lista.append(pickle.load(fh))
    prof = MS.unisci_profili(lista)
    return OrderedDict((n, MS.auc_da_profili(prof, n, len(c['ids']))) for n in nomi), MS.negativo_K(prof, 1)


def lavoro_D(f, nomi):
    """D di ia10 sulla piega f per `vere` e per i libri `nomi`: [somma ordine vero, coppie, somma rimescolata, pagine]."""
    import ia07_voynich_neurale as I7
    import imitatore_misure as MS
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi:
        testi[n] = carica_libro(n)
    out, info = MS.lavoro_D(f, c, testi)
    return OrderedDict([('D', OrderedDict((k, [float(x) for x in v]) for k, v in out.items())), ('famiglie', info)])


def lavoro_rete(nome, tipo, seme):
    """Misure di rete di ia02 (R: R_rel, Q) o di ia03 (K: k90, GL, GR) per un libro, con la procedura di ia14 (`lavoro_gru`)."""
    import ia14_quale_cifrario as I14
    pagine = carica_libro(nome)
    blocchi = I14.blocchi_di(pagine)
    t = OrderedDict([(nome, dict(blocchi=blocchi, ruolo='generatore', gruppo=nome, trasforma=None, speciali=None))])
    if tipo == 'R':
        I14.e95.SEMI = (seme,)
        lavori, scarti = I14.I2.prepara(t, t)
        mod = I14.I2
    else:
        I14.I3.SEMI = (seme,)
        lavori, scarti = I14.I3.prepara(t)
        mod = I14.I3
    if scarti or len(lavori) != 1:
        raise RuntimeError('lavoro di rete non preparato: %s' % (scarti,))
    corsa = mod.corsa(lavori[0])
    if tipo == 'R':
        x = I14.I2.misure_corsa(corsa)
        return OrderedDict([('R_rel', x['R_rel']), ('Q', x['Q_rete'])])
    x = I14.I3.misure_corsa(corsa, 'B')
    return OrderedDict([('k90', x['k90_interpolato']), ('GL', x['GL']), ('GR', x['GR_corte'])])


def lavoro_extra(nome):
    import abc_statistiche as S
    pagine = carica_libro(nome)
    out = OrderedDict(S.statistiche_extra(pagine))
    ro = righello_misure(pagine)
    if ro:
        out.update(ro)
    return out


def lavoro(args):
    """Esegue un lavoro; un errore non ferma gli altri (si registra). args: ('G', nome), ('S', nome), ('K', f, nomi), ('D', f, nomi),
    ('R', nome, 'R'|'K', seme), ('X', nome)."""
    inizio = time.time()
    ident = '|'.join(str(a) if not isinstance(a, (list, tuple)) else '#%08x' % (zlib.crc32('|'.join(a).encode('utf-8')) & 0xffffffff) for a in args)
    try:
        t = args[0]
        if t == 'G':
            r = lavoro_giudici(args[1])
        elif t == 'S':
            r = lavoro_struttura(args[1])
        elif t == 'K':
            r = lavoro_K(args[1], args[2])
        elif t == 'D':
            r = lavoro_D(args[1], args[2])
        elif t == 'R':
            r = lavoro_rete(args[1], args[2], args[3])
        elif t == 'X':
            r = lavoro_extra(args[1])
        else:
            raise ValueError(t)
        r = OrderedDict(r)
    except Exception as e:                                          # noqa: BLE001
        import traceback
        r = OrderedDict([('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1200:])])
    r['lavoro'] = ident
    r['tipo'] = args[0]
    r['nome'] = args[1] if isinstance(args[1], str) else None
    r['secondi'] = round(time.time() - inizio, 1)
    return r


def avvia_processo():
    import ia14_quale_cifrario as I14
    I14.avvia_processo()
