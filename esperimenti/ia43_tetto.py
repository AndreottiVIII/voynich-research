# -*- coding: utf-8 -*-
"""Esperimento IA43 (ia43): il tetto al messaggio. Quanto testo "ingenuo" in chiaro puo' esserci nel Voynich senza che le nostre misure se ne accorgano?

Strada 1 di `voynich-ia/PROPOSTE_DECIFRARE_FABLE.md`. Si prende il v21 (il generatore quasi indistinguibile dal Voynich) SENZA messaggio e si pianta un messaggio vero, non cifrato e non compresso (il Macer
floridus e l'inizio di Isidoro XVII, latino pubblico), a dosi crescenti (5, 10, 20, 40, 70, 100% dei posti di parola), in tre modi (a parola per parola, b lettera per lettera alla Naibbe, c solo "quali parole
stanno nella pagina") e con 1, 3 o 10 alternative per unita' (b: 1, 3 o 6 tavole). Una batteria fissa di misure e di giudici gia' esistenti dice da quale dose il messaggio si vede: quella dose e' il
tetto. Il Voynich entra solo come riferimento (giudici e riga "Voynich" delle misure), mai come testo da leggere. Non e' una decifrazione. Preregistrazione: preregistrazioni/ia43.md.

Fasi (un'unica esecuzione, riprende da dove si e' fermata con RIPRENDI=1; ogni lavoro scrive una riga di numeri in `risultati/ia43_corse.jsonl`):
  0  libri di partenza: 24 senza messaggio (chiavi 101-124), 6 di calibrazione (201-206), via `canale_sacco.codifica(None, ..., 'v21')` (circa 100 s l'uno);
  1  misure M (S, T, P: `tetto_batteria.misure_libro`) su tutti i libri (partenza, calibrazione piantata al 100%, piantati, controllo di sostituzione) e riga "Voynich" delle misure;
  2  giudici J (e231, e266, N) e b sui libri senza messaggio e di calibrazione; direzioni, soglie e k (`tetto_criteri`);
  3  giudici J e b sui piantati, solo dove le misure M da sole non vedono ancora il messaggio (regola scritta prima, vedi preregistrazione) e nella cella del controllo positivo;
  4  esito: controlli, tetti per cella e per famiglia, Voynich, `risultati/ia43_tetto.{md,json}`.

    nohup bash strumenti/coda.sh ia43 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia43" > /dev/null 2>&1 &
    PROVA43=1 PROCESSI=4 python esperimenti/ia43_tetto.py        (prova: "vero" = un libro v21 diverso da quelli piantati; niente Voynich; scrive in dati/cache/ia43_prove)

Variabili (valori senza virgole e senza due punti, con "-" fra i numeri): PROVA43, CACHE43, USCITA43, N_NEG43 (24), N_PIA43 (12), N_CAL43 (6), FORME43 (abc), DOSI43 (5-10-20-40-70-100), ALT43 (1-3-10; b usa ALT_B43 1-3-6),
DOSI_CTL43 (2-5-10-20-40-100), DOSI_BASSE43 (1-2: dosi in piu per le celle con 1 alternativa), MIN_VISTI43 (11), RIPRENDI, PROCESSI, PERM_P43 (100), FASE43 (fino a quale fase: 1, 2, 3).
"""
import json
import math
import os
import pickle
import sys
import time
import zlib
from collections import OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import tetto_piantare as P  # noqa: E402
import tetto_criteri as C  # noqa: E402

NOME = 'ia43_tetto'
PROVA = os.environ.get('PROVA43') == '1'
CACHE43 = os.environ.get('CACHE43', os.path.join(QUI, '..', 'dati', 'cache', 'ia43_prove', 'cache') if PROVA else os.path.join(QUI, '..', 'dati', 'cache', 'ia43'))
USCITA43 = os.environ.get('USCITA43', os.path.join(QUI, '..', 'dati', 'cache', 'ia43_prove', 'uscita') if PROVA else os.path.join(QUI, '..', 'risultati'))
BASI = os.path.join(CACHE43, 'basi')


def _lista(nome, default, tipo=int):
    return [tipo(x) for x in os.environ.get(nome, default).split('-') if x]


FORME = tuple(os.environ.get('FORME43', 'abc'))
DOSI = tuple(x / 100.0 for x in _lista('DOSI43', '5-10-20-40-70-100'))
DOSI_BASSE = tuple(x / 100.0 for x in _lista('DOSI_BASSE43', '1-2'))          # solo per le celle con 1 alternativa: dove il tetto potrebbe stare sotto il 5%
ALT = {'a': tuple(_lista('ALT43', '1-3-10')), 'c': tuple(_lista('ALT43', '1-3-10')), 'b': tuple(_lista('ALT_B43', '1-3-6'))}
DOSI_CTL = tuple(x / 100.0 for x in _lista('DOSI_CTL43', '2-5-10-20-40-100'))
N_NEG, N_PIA, N_CAL = int(os.environ.get('N_NEG43', 24)), int(os.environ.get('N_PIA43', 12)), int(os.environ.get('N_CAL43', 6))
MIN_VISTI = int(os.environ.get('MIN_VISTI43', C.MIN_VISTI))
FASE_FINE = int(os.environ.get('FASE43', 3))
RIPRENDI = os.environ.get('RIPRENDI') == '1'
PROCESSI = max(1, int(os.environ.get('PROCESSI', 1)))
# chiavi: nella corsa vera 101-124 (senza messaggio; le prime N_PIA sono anche le basi dei piantati) e 201-206 (calibrazione); nelle prove 302-... e 301 e' il "vero"
CH0 = 302 if PROVA else 101
CH_CAL0 = (302 + N_NEG) if PROVA else 201
CH_STANDIN = 301
CHIAVI_NEG = [str(CH0 + i) for i in range(N_NEG)]
CHIAVI_PIA = CHIAVI_NEG[:N_PIA]
CHIAVI_CAL = [str(CH_CAL0 + i) for i in range(N_CAL)]
PERCORSO = os.path.join(USCITA43, 'ia43_corse%s.jsonl' % ('_prova' if PROVA else ''))
FAMIGLIE = OrderedDict([('S', None), ('T', None), ('P', None), ('J', None), ('b', None)])


# ---------------------------------------------------------------- l'elenco dei libri

def dosi_cella(forma, alt):
    """Le dosi di una cella: la griglia principale e, per le celle con 1 alternativa, le dosi basse (1 e 2%)."""
    return (tuple(DOSI_BASSE) if alt == 1 else ()) + tuple(DOSI)


def pc(x):
    return int(round(100 * x))


def nome_libro(spec):
    return ':'.join(str(x) for x in spec)


def elenco():
    """Tutti i libri dell'esperimento: nome -> spec. Spec: ('neg', chiave), ('cal0', chiave), ('cal', forma, chiave), ('pia', forma, alt, dose%, chiave), ('ctl', 'z', dose%, chiave)."""
    out = OrderedDict()
    for k in CHIAVI_NEG:
        out[nome_libro(('neg', k))] = ('neg', k)
    for k in CHIAVI_CAL:
        out[nome_libro(('cal0', k))] = ('cal0', k)
        for f in FORME:
            out[nome_libro(('cal', f, k))] = ('cal', f, k)
    for f in FORME:
        for alt in ALT[f]:
            for d in dosi_cella(f, alt):
                for k in CHIAVI_PIA:
                    out[nome_libro(('pia', f, alt, pc(d), k))] = ('pia', f, alt, pc(d), k)
    if 'a' in FORME:
        for d in DOSI_CTL:
            for k in CHIAVI_PIA:
                out[nome_libro(('ctl', 'z', pc(d), k))] = ('ctl', 'z', pc(d), k)
    return out


def libro_di(spec):
    """(t, info) del libro: la base, o la base con il messaggio piantato."""
    t0 = P.leggi_base(spec[-1], BASI)
    if spec[0] in ('neg', 'cal0'):
        return t0, None
    if spec[0] == 'cal':
        return P.pianta(t0, spec[2], spec[1], 1.0, 1)
    if spec[0] == 'pia':
        return P.pianta(t0, spec[4], spec[1], spec[3] / 100.0, spec[2])
    if spec[0] == 'ctl':
        return P.pianta(t0, spec[3], 'z', spec[2] / 100.0, 1)
    raise ValueError(spec)


def cella(spec):
    """(forma, alt) di un libro piantato; per il controllo ('z', 1)."""
    if spec[0] == 'pia':
        return spec[1], spec[2]
    if spec[0] == 'ctl':
        return 'z', 1
    if spec[0] == 'cal':
        return spec[1], 1
    return None


def dose_di(spec):
    return spec[3] if spec[0] == 'pia' else (spec[2] if spec[0] == 'ctl' else (100 if spec[0] == 'cal' else 0))


# ---------------------------------------------------------------- lavori (dentro i processi)

_W = {}


def iniz():
    """Nei processi: il mondo. Nelle prove un libro v21 prende il posto del Voynich come "vero"."""
    if PROVA and 'mondo' not in _W:
        import tetto_batteria as T
        T.imposta_vero_standin(P.leggi_base(str(CH_STANDIN), BASI))
    _W['mondo'] = 'prova' if PROVA else 'vero'


def lavoro_base(chiave):
    inizio = time.time()
    P.genera_base(chiave, BASI)
    return OrderedDict([('lavoro', 'base|%s' % chiave), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome, spec):
    import tetto_batteria as T
    inizio = time.time()
    iniz()
    t, info = libro_di(spec)
    out = OrderedDict([('lavoro', 'M|%s' % nome), ('nome', nome), ('misure', T.misure_libro(t))])
    # integrita' del piantare: solo per a e c con 1 alternativa (il libro dei codici si inverte senza ambiguita'); b non si inverte qui
    if info is not None and info.get('parole_messaggio') is not None and spec[0] in ('cal', 'pia') and info['alt'] == 1 and info['dose'] >= 1.0:
        out['recuperato'] = P.recuperato(t, info)
        out['sbagliata'] = P.recuperato(t, info, posti_alt=_posti_sbagliati(t, info))
    if info is not None:
        out['posti_sostituiti'] = info['posti_sostituiti']
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def _posti_sbagliati(t, info):
    """Una chiave sbagliata: altrettanti posti scelti a caso fra quelli NON sostituiti."""
    import random
    tutti = set(P.posti(t)) - set(info['posti'])
    rnd = random.Random(P.seme_str('ia43-sbagliata', len(info['posti'])))
    return rnd.sample(sorted(tutti), min(len(info['posti']), len(tutti)))


def lavoro_V():
    import tetto_batteria as T
    inizio = time.time()
    iniz()
    return OrderedDict([('lavoro', 'V'), ('misure', T.valori_vero()), ('secondi', round(time.time() - inizio, 1))])


def lavoro_VT():
    """Solo nella corsa vera: le misure M sulla trascrizione di Takahashi. Non provata prima; se fallisce non ferma la corsa (misure None)."""
    import tetto_batteria as T
    inizio = time.time()
    iniz()
    try:
        m, nota = T.valori_takahashi(), None
    except Exception as e:                                                # noqa: BLE001
        m, nota = None, '%s: %s' % (type(e).__name__, str(e)[:200])
    return OrderedDict([('lavoro', 'VT'), ('misure', m), ('nota', nota), ('secondi', round(time.time() - inizio, 1))])


def lavoro_J(nome, spec):
    import tetto_batteria as T
    inizio = time.time()
    iniz()
    t, _ = libro_di(spec)
    return OrderedDict([('lavoro', 'J|%s' % nome), ('nome', nome), ('giudici', T.giudici_libro(t)), ('secondi', round(time.time() - inizio, 1))])


def lavoro_B(etichetta, nomi, seme):
    import tetto_batteria as T
    inizio = time.time()
    iniz()
    libri = [libro_di(elenco_cache()[n])[0] for n in nomi]
    r = T.giudice_b(libri, seme)
    out = OrderedDict([('lavoro', 'B|%s' % etichetta), ('nomi', nomi)])
    out.update(r)
    out['secondi'] = round(time.time() - inizio, 1)
    return out


_EL = {}


def elenco_cache():
    if 'e' not in _EL:
        _EL['e'] = elenco()
    return _EL['e']


def lavoro43(args):
    try:
        if args[0] == 'base':
            return lavoro_base(args[1])
        if args[0] == 'M':
            return lavoro_M(args[1], elenco_cache()[args[1]])
        if args[0] == 'V':
            return lavoro_V()
        if args[0] == 'VT':
            return lavoro_VT()
        if args[0] == 'J':
            return lavoro_J(args[1], elenco_cache()[args[1]])
        if args[0] == 'B':
            return lavoro_B(args[1], args[2], int(args[3]))
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:2])), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    raise ValueError(args)


def chiave_lavoro(a):
    if a[0] == 'base':
        return 'base|%s' % a[1]
    if a[0] in ('V', 'VT'):
        return a[0]
    return '%s|%s' % (a[0], a[1])


# ---------------------------------------------------------------- corse

def leggi_corse():
    out = OrderedDict()
    if os.path.exists(PERCORSO):
        for l in open(PERCORSO, encoding='utf-8'):
            l = l.strip()
            if l:
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                if not r.get('errore'):
                    out[r['lavoro']] = r
    return out


def esegui(lavori, corse, etichetta):
    """Fa girare i lavori non ancora fatti (in parallelo) e li aggiunge a `corse` e al file."""
    da_fare = [a for a in lavori if chiave_lavoro(a) not in corse]
    print('[%s] %d lavori da fare su %d' % (etichetta, len(da_fare), len(lavori)), flush=True)
    if not da_fare:
        return
    os.makedirs(os.path.dirname(PERCORSO), exist_ok=True)
    inizio = time.time()
    errori = 0
    with open(PERCORSO, 'a', encoding='utf-8', newline='\n') as f:
        def scrivi(r):
            nonlocal errori
            f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            f.flush()
            if r.get('errore'):
                errori += 1
                print('ERRORE %s: %s' % (r['lavoro'], r['errore']), flush=True)
            else:
                corse[r['lavoro']] = r
        if PROCESSI == 1:
            for i, a in enumerate(da_fare):
                scrivi(lavoro43(a))
                if (i + 1) % 10 == 0:
                    print('[%s] %d/%d, %.0f s' % (etichetta, i + 1, len(da_fare), time.time() - inizio), flush=True)
        else:
            with get_context('spawn').Pool(PROCESSI) as pool:
                for i, r in enumerate(pool.imap_unordered(lavoro43, da_fare)):
                    scrivi(r)
                    if (i + 1) % 25 == 0:
                        print('[%s] %d/%d, %.0f s' % (etichetta, i + 1, len(da_fare), time.time() - inizio), flush=True)
    if errori:
        raise SystemExit('%d lavori falliti in %s: si riprende con RIPRENDI=1 dopo aver visto il file %s' % (errori, etichetta, PERCORSO))
    print('[%s] fatto in %.0f s' % (etichetta, time.time() - inizio), flush=True)


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- analisi (numeri soli)

def valori(corse, nome):
    """Il dizionario nome-misura -> valore di un libro (misure M, giudici J e b)."""
    out = OrderedDict()
    r = corse.get('M|%s' % nome)
    if r:
        out.update(r['misure'])
    r = corse.get('J|%s' % nome)
    if r:
        out.update(r['giudici'])
    return out


def b_per_libro(corse, nomi_insieme_chiavi):
    """nome libro -> valore b, dai lavori B (un insieme per etichetta)."""
    out = {}
    for lav, r in corse.items():
        if lav.startswith('B|'):
            for n, v in zip(r['nomi'], r['per_libro']):
                out[n] = v
    return out


def con_b(corse, nome, bmap):
    v = valori(corse, nome)
    if nome in bmap:
        v['b'] = bmap[nome]
    return v


def insiemi_negativi():
    """Gli insiemi di libri senza messaggio su cui si calcola b: gruppi consecutivi di N_PIA chiavi (le basi dei piantati e gli altri)."""
    ins = OrderedDict()
    for g in range(0, N_NEG, N_PIA):
        ks = CHIAVI_NEG[g:g + N_PIA]
        if len(ks) >= 4:
            ins['neg%d' % (g // N_PIA + 1)] = [nome_libro(('neg', k)) for k in ks]
    return ins


def insiemi_calibrazione():
    return OrderedDict(('cal-%s' % f, [nome_libro(('cal', f, k)) for k in CHIAVI_CAL]) for f in FORME)


def lavori_fase2():
    """I giudici (e231, e266, N) su TUTTI i libri (costano circa 12 secondi l'uno) e b su ogni insieme: negativi, calibrazione, ogni cella e dose, controllo di sostituzione."""
    L = [('J', n) for n in elenco()]
    for et, nomi in list(insiemi_negativi().items()) + list(insiemi_calibrazione().items()):
        L.append(('B', et, nomi, seme_str('b43', et) % 1000))
    for f, alt in celle():
        for d in dosi_cella(f, alt):
            L.append(('B', 'pia-%s-%d-%d' % (f, alt, pc(d)), nomi_cella(f, alt, d), seme_str('b43', f, alt, pc(d)) % 1000))
    if 'a' in FORME:
        for d in DOSI_CTL:
            L.append(('B', 'ctl-%d' % pc(d), nomi_controllo(d), seme_str('b43', 'z', pc(d)) % 1000))
    return L


def analisi_base(corse):
    """Direzioni, validita', soglie e k dai libri senza messaggio e di calibrazione. Richiede M e J (e b) di negativi e calibrazione."""
    bmap = b_per_libro(corse, None)
    neg_nomi = [nome_libro(('neg', k)) for k in CHIAVI_NEG]
    neg_libri = [con_b(corse, n, bmap) for n in neg_nomi]
    nomi_m = list(neg_libri[0])
    neg = {n: [b.get(n) for b in neg_libri] for n in set().union(*[set(b) for b in neg_libri])}
    medie_b = C.media(neg.get('b', []))
    dirz, sog, k_B, k_M, fa_B, fa_M = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
    for f in FORME:
        cal = {}
        for k in CHIAVI_CAL:
            piant = con_b(corse, nome_libro(('cal', f, k)), bmap)
            base = con_b(corse, nome_libro(('cal0', k)), bmap)
            for n, v in piant.items():
                if n == 'b':
                    cal.setdefault(n, []).append(None if v is None or medie_b is None else v - medie_b)
                else:
                    cal.setdefault(n, []).append(None if v is None or base.get(n) is None else v - base[n])
        dirz[f] = C.direzioni(neg, cal)
        sog[f] = C.soglie(neg, dirz[f])
        k_B[f], fa_B[f] = C.scegli_k(neg_libri, dirz[f])
        k_M[f], fa_M[f] = C.scegli_k(neg_libri, dirz[f], solo=set(nomi_m) - set(['e231', 'e266', 'N', 'b']))
    if 'a' in dirz:
        dirz['z'], sog['z'], k_B['z'], k_M['z'], fa_B['z'], fa_M['z'] = dirz['a'], sog['a'], k_B['a'], k_M['a'], fa_B['a'], fa_M['a']
    return dict(dirz=dirz, sog=sog, k_B=k_B, k_M=k_M, fa_B=fa_B, fa_M=fa_M, neg=neg, neg_libri=neg_libri)


SOLO_M = ('e231', 'e266', 'N', 'b')


def conta_visti(corse, spec_nomi, forma, A, M_solo, bmap):
    """Quanti dei libri `spec_nomi` sono visti dalla batteria della forma (solo misure M se M_solo)."""
    k = A['k_M' if M_solo else 'k_B'][forma]
    escludi = set(SOLO_M) if M_solo else None
    vis = []
    for n in spec_nomi:
        v = con_b(corse, n, bmap)
        if M_solo:
            v = OrderedDict((a, x) for a, x in v.items() if a not in SOLO_M)
        vis.append(k is not None and len(C.visti_da(v, A['sog'][forma], A['dirz'][forma], solo=None)) >= k)
    return vis


def celle():
    out = []
    for f in FORME:
        for alt in ALT[f]:
            out.append((f, alt))
    return out


def nomi_cella(forma, alt, dose):
    return [nome_libro(('pia', forma, alt, pc(dose), k)) for k in CHIAVI_PIA]


def nomi_controllo(dose):
    return [nome_libro(('ctl', 'z', pc(dose), k)) for k in CHIAVI_PIA]


def esito(corse, A):
    """Tutte le tabelle dell'esito: controlli, per cella e per dose i libri visti, tetti, famiglie, Voynich."""
    bmap = b_per_libro(corse, None)
    ris = OrderedDict()
    ris['k_B'], ris['k_M'] = A['k_B'], A['k_M']
    ris['falsi_allarmi_B'] = A['fa_B']
    ris['falsi_allarmi_M'] = A['fa_M']
    ris['misure_valide'] = OrderedDict((f, [n for n, d in A['dirz'][f].items() if d['valida']]) for f in A['dirz'])
    ris['direzioni'] = A['dirz']
    ris['soglie'] = A['sog']
    celle_ris = OrderedDict()
    for f, alt in celle():
        c = OrderedDict()
        visti_B, visti_M, per_fam = OrderedDict(), OrderedDict(), OrderedDict()
        for d in dosi_cella(f, alt):
            nomi = nomi_cella(f, alt, d)
            eseguiti_J = all(('J|%s' % n) in corse for n in nomi)
            visti_M[pc(d)] = sum(conta_visti(corse, nomi, f, A, True, bmap))
            visti_B[pc(d)] = sum(conta_visti(corse, nomi, f, A, False, bmap)) if eseguiti_J else visti_M[pc(d)]
            c.setdefault('giudici_calcolati', OrderedDict())[pc(d)] = eseguiti_J
            lib = [con_b(corse, n, bmap) for n in nomi]
            for fam, nomi_m in (('S', ('heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par', 'ttr_pagina', 'hapax', 'lingua', 'dispersione', 'vicine', 'lunghezza', 'doppie', 'testa')),
                                ('T', tuple('T%d%s' % (i, v) for v in ('g', 'r') for i in (1, 2, 3, 4))), ('P', ('e375', 'e3a07', 'e211', 'e334')), ('J', ('e231', 'e266', 'N')), ('b', ('b',))):
                per_fam.setdefault(fam, OrderedDict())[pc(d)] = sum(len(C.visti_da(b, A['sog'][f], A['dirz'][f], solo=set(nomi_m))) >= 1 for b in lib)
        c['visti_batteria'], c['visti_solo_M'], c['visti_per_famiglia_almeno_una'] = visti_B, visti_M, per_fam
        c['tetto'] = C.tetto(OrderedDict((d / 100.0, v) for d, v in visti_B.items()), MIN_VISTI)
        c['tetto_solo_M'] = C.tetto(OrderedDict((d / 100.0, v) for d, v in visti_M.items()), MIN_VISTI)
        c['lettura'] = C.lettura_tetto(c['tetto'])
        # tetto per misura
        tm = OrderedDict()
        for n, t in A['sog'][f].items():
            vpd = OrderedDict((d, [con_b(corse, x, bmap).get(n) for x in nomi_cella(f, alt, d)]) for d in dosi_cella(f, alt))
            tm[n] = C.tetto_misura(vpd, t, A['dirz'][f][n]['segno'], MIN_VISTI)
        c['tetto_per_misura'] = tm
        celle_ris['%s%d' % (f, alt)] = c
    ris['celle'] = celle_ris
    # controllo di sostituzione
    if 'a' in FORME and 'z' in A['dirz']:
        z = OrderedDict()
        for d in DOSI_CTL:
            nomi = nomi_controllo(d)
            z[pc(d)] = OrderedDict([('visti_batteria', sum(conta_visti(corse, nomi, 'z', A, False, bmap)) if all(('J|%s' % n) in corse for n in nomi) else sum(conta_visti(corse, nomi, 'z', A, True, bmap))),
                                    ('visti_solo_M', sum(conta_visti(corse, nomi, 'z', A, True, bmap)))])
        ris['controllo_sostituzione'] = z
    # controllo positivo, recupero
    pos = ris['celle'].get('a1', {}).get('visti_batteria', {}).get(100)
    ris['controllo_positivo'] = OrderedDict([('visti_a1_100', pos), ('passa', pos == N_PIA if pos is not None else None)])
    rec = [corse['M|%s' % nome_libro(('pia', 'a', 1, 100, k))].get('recuperato') for k in CHIAVI_PIA if ('M|%s' % nome_libro(('pia', 'a', 1, 100, k))) in corse]
    sba = [corse['M|%s' % nome_libro(('pia', 'a', 1, 100, k))].get('sbagliata') for k in CHIAVI_PIA if ('M|%s' % nome_libro(('pia', 'a', 1, 100, k))) in corse]
    ris['recupero_con_chiave'] = OrderedDict([('giusta_media', C.media(rec)), ('sbagliata_media', C.media(sba))])
    # Voynich (o il "vero" delle prove): le sole misure M
    V = corse.get('V')
    voy = OrderedDict()
    if V:
        for f in A['dirz']:
            flag = C.visti_da(V['misure'], A['sog'][f], A['dirz'][f], solo=set(n for n in A['dirz'][f] if n not in SOLO_M))
            voy[f] = OrderedDict([('misure_oltre_la_soglia', flag), ('k_M', A['k_M'][f]), ('visto', bool(A['k_M'][f] is not None and len(flag) >= A['k_M'][f]))])
        ris['vero'] = voy
        ris['valori_vero'] = V['misure']
    VT = corse.get('VT')
    if VT and VT.get('misure'):
        vt = OrderedDict()
        for f in A['dirz']:
            flag = C.visti_da(VT['misure'], A['sog'][f], A['dirz'][f], solo=set(n for n in A['dirz'][f] if n not in SOLO_M))
            vt[f] = OrderedDict([('misure_oltre_la_soglia', flag), ('visto', bool(A['k_M'][f] is not None and len(flag) >= A['k_M'][f]))])
        ris['vero_takahashi'] = vt
        ris['valori_vero_takahashi'] = VT['misure']
    elif VT:
        ris['vero_takahashi'] = VT.get('nota')
    return ris


# ---------------------------------------------------------------- scrittura

def tutte_le_dosi():
    return sorted(set(DOSI) | set(DOSI_BASSE))


def nu(x, d=3):
    return '—' if x is None else ('%.*f' % (d, x)).replace('.', ',')


def scrivi_esito(ris):
    os.makedirs(USCITA43, exist_ok=True)
    suff = '_prova' if PROVA else ''
    json.dump(ris, open(os.path.join(USCITA43, NOME + suff + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ['# IA43 — Il tetto al messaggio%s' % (' (PROVA: il "vero" e\' un libro v21, non il Voynich)' if PROVA else ''), '',
          'Preregistrazione: `preregistrazioni/ia43.md`. Solo numeri. Messaggio in chiaro piantato nel v21; la batteria vede un libro se almeno k misure valide superano la soglia dei libri senza messaggio; '
          'il tetto di una cella e\' la dose piu\' bassa da cui in su almeno %d libri su %d sono visti.' % (MIN_VISTI, N_PIA), '',
          '## Controlli', '',
          '- Controllo positivo (forma a, 1 alternativa, 100%%): batteria vede **%s** libri su %d: **%s**.' % (ris['controllo_positivo']['visti_a1_100'], N_PIA, 'passato' if ris['controllo_positivo']['passa'] else 'NON passato'),
          '- Recupero con la chiave (forma a, 100%%): chiave giusta %s, chiave sbagliata %s.' % (nu(ris['recupero_con_chiave']['giusta_media']), nu(ris['recupero_con_chiave']['sbagliata_media'])),
          '- k (misure valide da superare): ' + '; '.join('forma %s: tutte %s, solo M %s' % (f, ris['k_B'][f], ris['k_M'][f]) for f in ris['k_B']) + '.',
          '- Falsi allarmi dei libri senza messaggio (uno fuori): ' + '; '.join('forma %s: %s' % (f, nu(ris['falsi_allarmi_B'][f].get(ris['k_B'][f]) if ris['k_B'][f] else None)) for f in ris['k_B']) + '.',
          '- Misure valide per forma: ' + '; '.join('%s: %d' % (f, len(v)) for f, v in ris['misure_valide'].items()) + '.', '',
          '## Per cella: libri visti su %d, per dose' % N_PIA, '',
          '| cella | ' + ' | '.join('%d%%' % pc(d) for d in tutte_le_dosi()) + ' | tetto | lettura | tetto con le sole misure M |', '|---|' + '---|' * (len(tutte_le_dosi()) + 3)]
    for nome, c in ris['celle'].items():
        md.append('| %s | %s | %s | %s | %s |' % (nome, ' | '.join((str(c['visti_batteria'][pc(d)]) if pc(d) in c['visti_batteria'] else '·') for d in tutte_le_dosi()),
                                                nu(c['tetto'], 2), c['lettura'], nu(c['tetto_solo_M'], 2)))
    md += ['', '`·` = dose non provata per quella cella (le dosi 1 e 2% si provano solo con 1 alternativa).', '']
    if 'controllo_sostituzione' in ris:
        md += ['## Controllo di sostituzione (come a, ma parole del messaggio rimescolate su tutto il libro)', '', '| dose | libri visti (batteria) | solo M |', '|---|---|---|']
        md += ['| %d%% | %s | %s |' % (d, x['visti_batteria'], x['visti_solo_M']) for d, x in ris['controllo_sostituzione'].items()]
        md.append('')
    md += ['## Voynich' if not PROVA else '## Il "vero" delle prove (un libro v21 senza messaggio: non deve essere visto)', '']
    for f, x in ris.get('vero', {}).items():
        md.append('- forma %s: %d misure M oltre la soglia (%s), k_M %s: **%s**.' % (f, len(x['misure_oltre_la_soglia']), ', '.join(x['misure_oltre_la_soglia']) or 'nessuna', x['k_M'], 'visto' if x['visto'] else 'non visto'))
    md.append('')
    vt = ris.get('vero_takahashi')
    if isinstance(vt, dict):
        md += ['Trascrizione di Takahashi (stesse misure M): ' + '; '.join('forma %s: %d oltre la soglia (%s)' % (f, len(x['misure_oltre_la_soglia']), 'visto' if x['visto'] else 'non visto') for f, x in vt.items()) + '.', '']
    elif vt:
        md += ['Trascrizione di Takahashi: non calcolata (%s).' % vt, '']
    open(os.path.join(USCITA43, NOME + suff + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- main

def main():
    print('IA43%s: cache %s, uscita %s, %d processi' % (' (PROVA)' if PROVA else '', CACHE43, USCITA43, PROCESSI), flush=True)
    corse = leggi_corse() if RIPRENDI else OrderedDict()
    if not RIPRENDI and os.path.exists(PERCORSO):
        os.replace(PERCORSO, PERCORSO + '.vecchio')
    el = elenco()
    # fase 0: libri di partenza
    chiavi = list(CHIAVI_NEG) + list(CHIAVI_CAL) + ([str(CH_STANDIN)] if PROVA else [])
    esegui([('base', k) for k in chiavi], corse, 'fase 0, libri di partenza')
    # fase 1: misure M
    lavori = [('V',)] + ([] if PROVA else [('VT',)]) + [('M', n) for n in el]
    esegui(lavori, corse, 'fase 1, misure M')
    if FASE_FINE < 2:
        return
    # fase 2: giudici e b
    esegui(lavori_fase2(), corse, 'fase 2, giudici e b')
    if FASE_FINE < 3:
        return
    # fase 3: soglie, k, esito
    A = analisi_base(corse)
    print('k_B %s, k_M %s' % (dict(A['k_B']), dict(A['k_M'])), flush=True)
    ris = esito(corse, A)
    scrivi_esito(ris)
    print('fatto: %s' % os.path.join(USCITA43, NOME + ('_prova' if PROVA else '') + '.md'), flush=True)


if __name__ == '__main__':
    main()
