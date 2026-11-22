# -*- coding: utf-8 -*-
"""I testi del banco di IA26 e i "mondi" della taratura (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici
- Il **catalogo**: tutti i testi che il repo ha gia' e che il banco misura, ognuno con un nome stabile e un caricatore. Il formato comune e' quello di
  ia01: `pagine` = pagina -> lista di righe (inizio_paragrafo, [parola come tupla di glifi]); i testi sono tutti nella DISPOSIZIONE del libro vero
  (stesse pagine, stesso numero di parole per riga, stessi inizi di paragrafo).
    vero                      il libro vero (con SOLO_CONTROLLI=1: il latino nella disposizione del Voynich, come in ia07)
    V21:k                     libri v21 senza messaggio di ia01 (nelle prove: catene di Markov di ordine 2, come ia07)
    TS:s, NAIBBE:1            Timm e Schinner (semi 1-3) e Naibbe: le parole, nell'ordine, rimesse nella disposizione (le righe originali non si
                              conservano: dichiarato nella preregistrazione)
    ia07:i, ia16_*:i, ia20_M*:i, ia22_E*:i, ia23_P*:i, ia24_W*:i    libri degli imitatori, letti dai file della cache (se esistono)
    CIF:codice_valore_i1      i procedimenti di ia14 (cifrari_procedimenti.genera) nella disposizione; CIF:... con una sola istanza
    LG:lingua                 le 8 lingue di ia14 nella disposizione
    CTRL:*                    controlli: parole rimescolate nella riga, righe rimescolate nella pagina, parole rimescolate in tutto il libro
- I **mondi** (taratura): testi sintetici di processo noto con la stessa disposizione e lo stesso vocabolario del libro vero: markov2 (catena di
  Markov di ordine 2 sui glifi), ecocontatto (ia22), tec (ia23: tema + eco + contatto), calibrato (tema, eco e contatto portati ai valori del Voynich da
  `ia26_righello_taratura`), eco20 (ia20: solo eco; facoltativo). Un mondo diventa "il vero" di un processo: `attiva_mondo` sostituisce il libro vero di ia07 con il testo del mondo
  (da usare in un processo appena avviato, prima di ogni altra cosa).
Non importa mai il Voynich da se': il libro vero arriva da `ia07_voynich_neurale.libro_vero()` (che con SOLO_CONTROLLI=1 e' il latino).
Nessun risultato e' scritto qui.
"""
import json
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia01_giudice_neurale as G  # noqa: E402
import cifrari_procedimenti as CP  # noqa: E402

SOLO_CONTROLLI = I7.SOLO_CONTROLLI
CACHE_BASE = os.environ.get('CACHE_LIBRI26', os.path.join(QUI, '..', 'dati', 'cache'))
N_PER_SET = int(os.environ.get('N_PER_SET26', 5))            # libri per insieme di imitatori nel catalogo
N_V21 = int(os.environ.get('N_V21_26', 10))                  # libri v21 (senza messaggio)
SEMI_TS = (1, 2, 3)
ISTANZE_CIF = int(os.environ.get('ISTANZE_CIF26', 1))        # istanze per cella dei procedimenti di ia14

# le otto lingue di ia14 (copiate da ia14_quale_cifrario.LINGUE_CHIAVI per non importare il suo carico di moduli)
LINGUE_CHIAVI = OrderedDict([
    ('latino', "Historical - Latin - Technical - Pliny's Natural History.txt"),
    ('latino_nt', 'Historical - Latin - Literary - NT (Vulgate).txt'),
    ('italiano', 'Historical - Italian - Literary - NT - Diodati.txt'),
    ('inglese', 'Historical - English - Literary - NT (KJV).txt'),
    ('francese', 'Historical - French - Literary - NT - Martin.txt'),
    ('tedesco', 'Historical - German - Literary - NT - Luther.txt'),
    ('spagnolo', 'Historical - Spanish - Literary - NT - Sagradas Escrituras.txt'),
    ('maori', 'Modern - Maori - Literary - NT.txt'),
])
# insiemi di libri degli imitatori: etichetta -> (cartella in dati/cache, prefisso del file, nomi dei sottotipi, quanti libri esistono)
IMITATORI = OrderedDict([
    ('ia20', ('ia20', 'ia20_libro_%s_%d.txt', ['M1', 'M2', 'M3', 'M4', 'M5'], 10)),
    ('ia22', ('ia22', 'ia22_libro_%s_%d.txt', ['E0', 'E1', 'E2', 'E3'], 10)),
    ('ia23', ('ia23', 'ia23_libro_%s_%d.txt', ['P1', 'P2', 'P3'], 10)),
    ('ia24', ('ia24', 'ia24_libro_%s_%d.txt', ['W1', 'W2', 'W3'], 10)),
])

# ---- i mondi della taratura
# generatori: 'markov' (catena di ordine 2 sui glifi), 'eco' (ia22: eco e contatto piantati), 'tec' (ia23: tema, eco, contatto piantati), 'tec2' (come tec con i temi scelti fra i tipi non rari), 'gm' (ia20: eco piantata)
MONDI = OrderedDict([
    ('markov2', dict(gen='markov', ordine=2, par={})),
    ('ecocontatto', dict(gen='tec2', par=dict(eco=0.5, ritocco=0.6, inizio=0.5, tema=0.0, contatto=0.6, freq_min_tema=0))),                     # = ia22 SENS_TESTI['ecocontatto']
    ('tec', dict(gen='tec2', par=dict(eco=0.25, ritocco=0.6, inizio=0.0, tema=0.3, n_tema=25, contatto=0.7, freq_min_tema=0))),                  # = ia23 SENS_TESTI['tec']
    ('calibrato', dict(gen='tec2', par=dict(eco=0.06, ritocco=0.6, inizio=0.0, tema=0.12, n_tema=25, contatto=0.35, freq_min_tema=3))),           # partenza; la taratura la sostituisce
    ('eco20', dict(gen='gm', par=dict(eco=0.5, ritocco=0.6))),                                                                                    # = ia20 SENS_TESTI['eco'] (facoltativo)
])
CACHE26_CAL = os.environ.get('CAL26', '')                     # file json con i parametri calibrati (scritto da ia26_righello_taratura)


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- conversioni

def t_da_rows(rows):
    """pagine (pagina -> righe di tuple) -> lista (pagina, inizio, [parole come stringhe]), come `ia07.leggi_file`."""
    return [(p, bool(ini), [''.join(w) for w in ws]) for p, rr in rows.items() for ini, ws in rr]


def rows_da_t(t):
    return I7.libro_A_da_righe(t)


def layout_del_vero():
    """[(pagina, [(inizio_paragrafo, numero di parole), ...]), ...] del libro vero (solo lunghezze)."""
    out = OrderedDict()
    for x in I7.libro_vero():
        out.setdefault(x['pagina'], []).append((bool(x['ini']), len(x['parole'])))
    return list(out.items())


def _impagina_ciclico(layout, parole):
    """Come `cifrari_procedimenti.impagina`, ma se le parole non bastano si ricomincia dall'inizio (si conta quante volte)."""
    n = sum(k for _, rows in layout for _, k in rows)
    giri = 0
    while len(parole) < n:
        parole = parole + parole
        giri += 1
    return CP.impagina(layout, parole[:n]), giri


# ---------------------------------------------------------------- testi dal catalogo

def percorso_libro_imitatore(etichetta, tipo, i):
    cart, fmt, _, _ = IMITATORI[etichetta]
    return os.path.join(CACHE_BASE, cart, 'libri', fmt % (tipo, i))


def percorso_libro_ia07(i):
    return os.path.join(CACHE_BASE, 'ia07_libri', 'ia07_libro_senza_%d.txt' % i)


def percorso_libro_ia16(var, i):
    cart = os.path.join(CACHE_BASE, 'ia16')
    taglia = 'P'
    try:
        taglia = json.load(open(os.path.join(cart, 'taglia_scelta.json'), encoding='utf-8'))['taglia']
    except (OSError, ValueError, KeyError):
        pass
    return os.path.join(cart, 'libri', 'ia16_libro_%s_%s_%d.txt' % (var, taglia, i))


def _cifrario_args(nome):
    """'CIF:V_3_i1' o 'CIF:V_3_italiano_i1' -> (codice, valore, istanza, chiaro)."""
    corpo = nome.split(':', 1)[1]
    parti = corpo.split('_')
    cod, val = parti[0], parti[1].replace('p', '.')
    ist = int(parti[-1][1:])
    chiaro = parti[2] if len(parti) == 4 else None
    valore = float(val) if '.' in val else int(val)
    return cod, valore, ist, chiaro


def nomi_cifrari():
    nomi = []
    for cod, p in CP.PROCEDIMENTI.items():
        for v in p['valori']:
            for i in range(1, ISTANZE_CIF + 1):
                nomi.append('CIF:' + CP.nome_istanza(cod, v, i))
    for cod, v, ch in CP.VARIANTI_CHIARO:
        nomi.append('CIF:' + CP.nome_istanza(cod, v, 1, ch))
    nomi.append('CIF:T0_i1')                                # latino in chiaro nella disposizione
    return nomi


def catalogo():
    """Nomi (in ordine) di tutti i testi del banco che esistono. In prova (SOLO_CONTROLLI) i libri degli imitatori ci sono solo se qualcuno li ha messi
    in `CACHE_LIBRI26`."""
    nomi = ['vero']
    nomi += ['V21:%d' % k for k in I7.CHIAVI_V21[:N_V21]]
    nomi += ['TS:%d' % s for s in SEMI_TS] + ['NAIBBE:1']
    nomi += ['ia07:%d' % i for i in range(1, N_PER_SET + 1) if SOLO_CONTROLLI or os.path.exists(percorso_libro_ia07(i))]
    for var, n in (('P2', N_PER_SET), ('P1', N_PER_SET), ('R', N_PER_SET)):
        nomi += ['ia16_%s:%d' % (var, i) for i in range(1, n + 1) if os.path.exists(percorso_libro_ia16(var, i))]
    for et, (_, _, tipi, n) in IMITATORI.items():
        for tp in tipi:
            nomi += ['%s_%s:%d' % (et, tp, i) for i in range(1, min(N_PER_SET, n) + 1) if os.path.exists(percorso_libro_imitatore(et, tp, i))]
    nomi += nomi_cifrari()
    nomi += ['LG:' + l for l in LINGUE_CHIAVI]
    nomi += ['CTRL:parole', 'CTRL:righe', 'CTRL:tutto']
    filtro = [x for x in os.environ.get('TESTI26', '').split('|') if x]       # solo prove: tiene i testi il cui nome contiene una di queste sottostringhe
    if filtro:
        nomi = [n for n in nomi if n == 'vero' or any(x in n for x in filtro)]
    return nomi


def famiglia(nome):
    """Etichetta di gruppo di un nome (per le tabelle): 'ia20_M1:3' -> 'ia20_M1'; 'CIF:V_3_i1' -> 'CIF:V_3' (procedimento e valore del parametro)."""
    if nome == 'vero':
        return 'vero'
    pre, resto = nome.split(':', 1)
    if pre == 'CIF':
        return 'CIF:' + resto.rsplit('_', 1)[0]
    if pre in ('LG', 'CTRL'):
        return pre
    return pre


_RC = {}
_BASE = {}


def rows_di(nome):
    """Il testo `nome` come pagine (pagina -> righe (inizio, [parola come tupla di glifi])). None se non esiste. Le pagine sono quelle del libro vero
    (anche quelle sotto le 40 parole: i giudici e le misure scelgono)."""
    if nome in _RC:
        return _RC[nome]
    r = _rows_di(nome)
    if r is not None and len(_RC) < 6:                       # poche in memoria
        _RC[nome] = r
    return r


def _rows_di(nome):
    D = I7.divisore()
    pre = nome.split(':', 1)[0]
    if nome == 'vero':
        return OrderedDict((p, [(bool(x['ini']), [tuple(D(w)) for w in x['parole']]) for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items())
    if pre == 'V21':
        return I7.libro_riferimento_A('b', int(nome.split(':')[1]))
    if pre == 'TS':
        import e337_posizione as e337
        parole = [tuple(D(w)) for righe in e337.pagine_ts(int(nome.split(':')[1])) for r in righe for w in r]
        return _impagina_ciclico(layout_del_vero(), parole)[0]
    if pre == 'NAIBBE':
        import e134_generatori_esterni as e134
        parole = [tuple(D(w)) for _, ps in e134.naibbe_righe() for w in ps]
        return _impagina_ciclico(layout_del_vero(), parole)[0]
    if pre == 'ia07':
        p = percorso_libro_ia07(int(nome.split(':')[1]))
        if os.path.exists(p):
            return rows_da_t(I7.leggi_file(p))
        if SOLO_CONTROLLI:                                    # prova: un libro che rimescola le parole della riga (non e' ia07)
            return G.rimescola_parole(I7.contesto_A()['vere'], 1700000 + int(nome.split(':')[1]))
        return None
    if pre.startswith('ia16_'):
        p = percorso_libro_ia16(pre[5:], int(nome.split(':')[1]))
        return rows_da_t(I7.leggi_file(p)) if os.path.exists(p) else None
    if pre.split('_')[0] in IMITATORI:
        et, tp = pre.split('_')
        p = percorso_libro_imitatore(et, tp, int(nome.split(':')[1]))
        return rows_da_t(I7.leggi_file(p)) if os.path.exists(p) else None
    if pre == 'CIF':
        if nome == 'CIF:T0_i1':
            return CP.testo_lingua_in_layout(CP.CHIAVI_CHIARO['latino'], layout_del_vero(), 1)
        cod, val, ist, chiaro = _cifrario_args(nome)
        return CP.genera(cod, val, ist, layout_del_vero(), chiaro)[0]
    if pre == 'LG':
        return CP.testo_lingua_in_layout(LINGUE_CHIAVI[nome.split(':')[1]], layout_del_vero(), 0)
    if pre == 'CTRL':
        k = nome.split(':')[1]
        if k == 'tutto':
            return CP.rimescola_tutto(_tutte_le_pagine(), CP.seme_di('ia26', 'tutto'))
        return I7.libro_controllo_A(k)
    raise ValueError('testo sconosciuto: %s' % nome)


def _tutte_le_pagine():
    return _rows_di('vero')


# ---------------------------------------------------------------- mondi

def parametri_mondo(nome):
    """Parametri del mondo `nome`; per `calibrato` quelli del file di calibrazione se c'e'."""
    m = json.loads(json.dumps(MONDI[nome]))
    if nome == 'calibrato' and CACHE26_CAL and os.path.exists(CACHE26_CAL):
        cal = json.load(open(CACHE26_CAL, encoding='utf-8'))
        if cal.get('parametri'):
            m['par'].update(cal['parametri'])
            m['calibrato_da'] = os.path.basename(CACHE26_CAL)
    return m


def sintetico_tec2(righe, seme, divisore, unita, eco=0.25, ritocco=0.6, inizio=0.0, tema=0.3, n_tema=25, contatto=0.7, freq_min_tema=3, pref_seed=None):
    """Il generatore di tema di pagina, eco locale e contatto di ia23 (`pagina_modelli.sintetico_tema_eco_contatto`), con l'opzione `inizio` di ia22 (con questa probabilita'
    il ritocco di una parola d'eco e' "il primo glifo diventa quello preferito dal contatto") e DUE differenze, dichiarate nella preregistrazione:
    1. la tabella dei glifi iniziali preferiti (il "contatto") viene da `pref_seed` e non dal seme del testo: il mondo e il suo gemello (stesso processo, altro seme)
       hanno la STESSA tabella. In ia22 e ia23 la tabella cambia con il seme: due copie dello stesso generatore avevano glifi iniziali diversi, e i giudici del paper
       (che scelgono i riferimenti sul testo vero) le vedevano diverse (prova sul latino: gemello a 0,8). La tabella e' un parametro del processo, non del campione.
    2. le parole di tema di ogni pagina si scelgono fra i tipi che compaiono almeno `freq_min_tema` volte nel libro (0 = tutti, come ia23).
    Il resto e' identico (stesso ordine di scelta: eco, poi tema, poi parola fresca con il contatto)."""
    import bisect
    rng = random.Random(seme)
    conti = Counter(w for x in righe for w in x['parole'])
    voc = sorted(conti)
    voc_tema = [w for w in voc if conti[w] >= freq_min_tema] or voc
    cum, t = [], 0.0
    for w in voc:
        t += conti[w]
        cum.append(t)
    pref_rng = random.Random(seme if pref_seed is None else pref_seed)
    pref = {a: pref_rng.choice(unita) for a in unita}

    def fresca():
        return voc[min(bisect.bisect_right(cum, rng.random() * t), len(voc) - 1)]

    def con_primo(w, g):
        u = divisore(w)
        u2 = [g] + list(u[1:])
        w2 = ''.join(u2)
        return w2 if divisore(w2) == u2 else w

    def modifica(w):
        u = divisore(w)
        for _ in range(12):
            tp = rng.choice((1, 2, 3))
            if tp == 1:
                i = rng.randrange(len(u))
                nuovo = rng.choice(unita)
                if nuovo == u[i]:
                    continue
                u2 = list(u)
                u2[i] = nuovo
            elif tp == 2:
                i = rng.randrange(len(u) + 1)
                u2 = list(u[:i]) + [rng.choice(unita)] + list(u[i:])
            else:
                if len(u) < 2:
                    continue
                i = rng.randrange(len(u))
                u2 = list(u[:i]) + list(u[i + 1:])
            w2 = ''.join(u2)
            if w2 != w and divisore(w2) == u2:
                return w2
        return w

    out, pagina_corr, sopra, topici = [], None, None, []
    for x in righe:
        if x['pagina'] != pagina_corr:
            pagina_corr, sopra = x['pagina'], None
            topici = rng.sample(voc_tema, min(n_tema, len(voc_tema))) if tema else []
        n = len(x['parole'])
        ps = []
        for k in range(n):
            prima = ps[-1] if ps else None
            g_pref = pref[divisore(prima)[-1]] if prima is not None else None
            if eco and sopra and rng.random() < eco:
                w = rng.choice(sopra)
                if rng.random() < ritocco:
                    if inizio and g_pref is not None and rng.random() < inizio:
                        w = con_primo(w, g_pref)
                    else:
                        w = modifica(w)
            elif tema and topici and rng.random() < tema:
                w = rng.choice(topici)
            else:
                w = fresca()
                if contatto and g_pref is not None and rng.random() < contatto:
                    w = con_primo(w, g_pref)
            ps.append(w)
        sopra = ps
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out


def genera_sintetico(gen, base, seme, divisore, unita, par):
    """Il testo sintetico del generatore `gen` ('tec', 'tec2', 'eco', 'gm') sulla disposizione e sulle frequenze di `base`."""
    import echi_modelli as EM
    import pagina_modelli as PM
    if gen == 'eco':
        return EM.sintetico_eco_contatto(base, seme, divisore, unita, **par)
    if gen == 'tec':
        return PM.sintetico_tema_eco_contatto(base, seme, divisore, unita, **par)
    if gen == 'tec2':
        return sintetico_tec2(base, seme, divisore, unita, **par)
    if gen == 'gm':
        import gradini_modelli as GM
        return GM.sintetico(base, seme, divisore, unita, **par)
    raise ValueError(gen)


def righe_sintetiche(base, nome, gemello=False):
    """Le righe (dizionari come `ia07.libro_vero()`) del mondo `nome` costruite sul libro `base` (disposizione e frequenze). `gemello`: lo stesso
    processo con un altro seme (la replica che un imitatore perfetto sarebbe)."""
    m = parametri_mondo(nome)
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    seme = seme_str('ia26', 'mondo', nome, 'gemello' if gemello else 'vero')
    if m['gen'] == 'markov':
        vere = OrderedDict()
        for x in base:
            vere.setdefault(x['pagina'], []).append((bool(x['ini']), [tuple(D(w)) for w in x['parole']]))
        mk = G.markov(vere, m['ordine'], seme)
        cont = {p: 0 for p in mk}
        out = []
        for x in base:
            ini, ws = mk[x['pagina']][cont[x['pagina']]]
            cont[x['pagina']] += 1
            y = dict(x)
            y['parole'] = [''.join(w) for w in ws]
            out.append(y)
        return out
    par = dict(m['par'])
    if m['gen'] == 'tec2':
        par['pref_seed'] = seme_str('ia26', 'pref', nome)       # la stessa tabella di contatto per il mondo e per il suo gemello
    return genera_sintetico(m['gen'], base, seme, D, unita, par)


def attiva_mondo(nome):
    """Il libro vero di ia07 diventa il testo sintetico del mondo `nome` (e i riferimenti dei giudici del paper vengono dal mondo). Da chiamare in un
    processo appena avviato, prima di ogni uso di ia07. `vero` non cambia niente."""
    if nome == 'vero':
        return None
    base = I7.libro_vero()
    _BASE['originale'] = base                                  # il gemello si costruisce sul libro vero originale, non sul mondo
    righe = righe_sintetiche(base, nome)
    I7._C.clear()
    I7._C['righe'] = righe
    flag = I7.SOLO_CONTROLLI
    I7.SOLO_CONTROLLI = True                                  # riferimenti() costruisce i riferimenti dal libro_vero() (qui il mondo), non dalla trascrizione
    try:
        I7.riferimenti()
    finally:
        I7.SOLO_CONTROLLI = flag
    return righe


def rows_gemello(nome_mondo):
    """Il gemello del mondo: lo stesso processo con un altro seme (stessa disposizione e stesse frequenze del libro vero originale), in formato pagine.
    Va chiamato dopo `attiva_mondo` (che conserva il libro originale)."""
    D = I7.divisore()
    base = _BASE.get('originale') or I7.libro_vero()
    righe = righe_sintetiche(base, nome_mondo, gemello=True)
    return OrderedDict((p, [(bool(x['ini']), [tuple(D(w)) for w in x['parole']]) for x in rr]) for p, rr in I7.per_pagina(righe).items())
