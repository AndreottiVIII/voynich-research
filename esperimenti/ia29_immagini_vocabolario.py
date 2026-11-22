# -*- coding: utf-8 -*-
"""Esperimento IA29 (ia29): immagini e vocabolario della pagina.

Domanda (proposta C6 di REVIEW_FABLE.md e punto 6 di PROPOSTA_METODI_OPUS.md): le pagine con disegni simili hanno anche vocabolario simile, oltre a
quanto spiegano sezione, lingua A/B, mano, fascicolo, bifoglio e distanza nel manoscritto? E, prima ancora, il metodo e' capace di vedere un legame
vero (controllo positivo su un erbario a stampa del 1542, con curva di diluizione) e di non inventarlo (controlli negativi), e quanto piccolo e' il
legame piu' piccolo che vede con il numero di pagine del Voynich (legami piantati)? E' descrittivo: un legame immagine-parole sarebbe un indizio sul
contenuto delle pagine, mai una decifrazione.

Preregistrazione: preregistrazioni/ia29.md. Moduli: immagini_dati.py (inventario, metadati, riquadri, copertura del testo), immagini_vettori.py (modelli
di immagini sul processore), immagini_legame.py (distanze, correlazione parziale, permutazioni, legami piantati), immagini_controllo.py (erbario di
controllo). Scrive risultati/ia29_immagini_vocabolario.json e .md: SOLO numeri e aggregati (nessuna parola, nessuna riga, nessuna immagine). Vettori,
immagini di controllo e modelli stanno in dati/cache/ia29 (protetti: non si committano).

Fasi (variabile FASI, lettere; predefinito EKNPVS):
  E vettori visivi (controllo e, se non SOLO_CONTROLLI, Voynich); K controllo positivo (Fuchs) con curva di diluizione; N controlli negativi;
  P potenza con legami piantati sul disegno del Voynich; V prova sul Voynich (e varianti); S sintesi e letture preregistrate.

    nohup bash strumenti/coda.sh ia29 "PY=dati/cache/.venv_immagini/Scripts/python,PROCESSI=8:ia29" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 USCITA=<cartella fuori dal repo> PICCOLO29=1 python esperimenti/ia29_immagini_vocabolario.py     (prova, mai sul Voynich)

SOLO_CONTROLLI=1: del Voynich si tengono solo i metadati delle pagine e il numero di parole (come ia07); il testo e' latino nella stessa disposizione e
i vettori visivi delle pagine sono quelli del controllo Fuchs assegnati a caso (immagini finte): nessuna immagine e nessuna parola del Voynich.

Variabili (oltre a FASI, PROCESSI, RIPRENDI, SOLO_CONTROLLI): USCITA, CACHE29, MODELLI29 (dino oppure dinoclip, senza virgole), PERM29 (permutazioni
della prova principale), RIP_POT29, RIP_NEG29, SOTTO29 (sottocampioni del controllo), DIREZIONE29 (prima o dopo), PICCOLO29 (solo prove).
I valori predefiniti sono quelli preregistrati.
"""
import json, math, os, random, statistics, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import immagini_dati as ID  # noqa: E402
import immagini_legame as L  # noqa: E402

NOME = 'ia29_immagini_vocabolario'
SOLO = os.environ.get('SOLO_CONTROLLI') == '1'
PICCOLO = os.environ.get('PICCOLO29') == '1'
RADICE = os.path.join(QUI, '..')
RISULTATI = os.path.join(RADICE, 'risultati')
USCITA = os.environ.get('USCITA', RISULTATI)
BASE29 = os.path.join(RADICE, 'dati', 'cache', 'ia29')                     # modelli e controllo Fuchs (nessun dato del Voynich)
CACHE29 = os.environ.get('CACHE29', os.path.join(USCITA, 'ia29_cache') if SOLO else BASE29)  # vettori del Voynich e risultati intermedi
FASI = os.environ.get('FASI', 'EKNPVS')
PROCESSI = int(os.environ.get('PROCESSI', 2))
RIPRENDI = os.environ.get('RIPRENDI') == '1'
MODELLI29 = os.environ.get('MODELLI29', 'dino')
DIREZIONE = os.environ.get('DIREZIONE29', 'prima')
SEME = 29
PERM = int(os.environ.get('PERM29', 99 if PICCOLO else 9999))          # permutazioni della prova principale sul Voynich
PERM_VAR = 99 if PICCOLO else 999                                       # permutazioni delle varianti
RIP_POT = int(os.environ.get('RIP_POT29', 3 if PICCOLO else 100))
RIP_NEG = int(os.environ.get('RIP_NEG29', 6 if PICCOLO else 200))
RIP_LAT = 4 if PICCOLO else 20
SOTTO = int(os.environ.get('SOTTO29', 3 if PICCOLO else 30))
B_POT = 49 if PICCOLO else 499                                          # permutazioni per replica nelle simulazioni di potenza e nei controlli negativi
B_CTRL = 99 if PICCOLO else 999                                         # permutazioni nel controllo positivo
NK = 240                                                                # unita' dei sottocampioni del controllo positivo
QS = (0.0, 0.02, 0.03, 0.05, 0.10, 0.20, 0.40)                                # forza dei legami piantati
DEGRADAZIONI = (('puro', None), ('diluito 0,3', ('dil', 0.3)), ('diluito 0,6', ('dil', 0.6)), ('diluito 0,85', ('dil', 0.85)),
                ('omofoni 3', ('omo', 3)), ('omofoni 3 e diluito 0,5', ('omo+dil', (3, 0.5))))
VARIANTI = (('dino', 'grigio', 'cls'), ('dino', 'colore', 'cls'), ('dino', 'grigio', 'patch'), ('clip', 'grigio', 'proj'))
PRINCIPALE = ('dino', 'grigio', 'cls')
SOGLIE = OrderedDict([('controllo_positivo_rilevazioni', 0.80), ('negativo_rifiuti_005', 0.09), ('negativo_latino_su_20', 2), ('alfa_principale', 0.01),
                      ('alfa_grigia', 0.05), ('potenza', 0.80), ('limite_superiore', 0.05)])


def ora():
    return time.strftime('%H:%M:%S')


def log(*a):
    print(ora(), *a, flush=True)


def nome_var(v):
    return '%s_%s_%s' % v


# ---------------------------------------------------------------- lavori per i processi
def lavoro_controllo(arg):
    """Un sottocampione del controllo positivo: n_sub unita' a caso, testo eventualmente degradato, prova libera e ciclica."""
    nome, var, pagine, E, meta, n_sub, degrada, seme, B = arg
    rng = np.random.default_rng(seme)
    N = len(pagine)
    ix = np.sort(rng.choice(N, size=min(n_sub, N), replace=False))
    pg = [pagine[i] for i in ix]
    if degrada:
        tipo, v = degrada
        if tipo == 'dil':
            pg = L.diluisci(pg, v, rng)
        elif tipo == 'omo':
            pg = L.omofoni(pg, v, rng)
        else:
            pg = L.diluisci(L.omofoni(pg, v[0], rng), v[1], rng)
    ms = [meta[i] for i in ix]
    Dy = L.distanza_vocabolario(L.matrice_conteggi(pg)[0])
    Dx = L.distanza_visiva(np.asarray(E)[ix])
    a = L.prova(Dy, Dx, ms, rng, B=B, nulla='libera')
    b = L.prova(Dy, Dx, ms, rng, B=B, nulla='ciclica')
    return {'nome': nome, 'variante': var, 'n': int(len(ix)), 'seme': seme, 'r': a['r'], 'p_libera': a['p'], 'p_ciclica': b['p']}


def esegui(funzione, lavori):
    if PROCESSI <= 1 or len(lavori) <= 1:
        return [funzione(a) for a in lavori]
    with get_context('spawn').Pool(PROCESSI) as pool:
        return pool.map(funzione, lavori, chunksize=1)


# ---------------------------------------------------------------- dati e vettori
def carica_controllo():
    """Unita' del controllo positivo (Fuchs) e loro vettori visivi per ogni variante disponibile."""
    import immagini_controllo as C
    import immagini_vettori as V
    o = C.ocr(BASE29)
    unita = C.costruisci(BASE29, DIREZIONE)
    meta = C.meta_controllo(unita)
    pagine = [u['parole'] for u in unita]
    chiavi = ['n%d' % u['k'] for u in unita]
    vett = {}
    for v in VARIANTI:
        if v[0] == 'clip' and 'clip' not in MODELLI29:
            continue

        def crea(_chiavi, v=v):
            ims = [C.immagine_mascherata(BASE29, o, u['k']) for u in unita]
            return V.vettori(ims, v[0], v[1], fili=PROCESSI)
        nome = 'fuchs_%s_%s_%s' % (DIREZIONE, v[0], v[1])
        r = V.con_cache(os.path.join(BASE29, 'vettori'), nome, chiavi, crea, 'Fuchs, direzione %s, modello %s, variante %s' % (DIREZIONE, v[0], v[1]))
        vett[nome_var(v)] = r[v[2]]
    return unita, meta, pagine, vett


def carica_voynich():
    """Testo, metadati e (se non SOLO) vettori visivi del campione principale; con SOLO, testo latino e vettori finti da `vettori_finti`."""
    import ia07_voynich_neurale as I7
    righe = ID.righe_voynich(SOLO)
    if SOLO:
        righe = ID.latino_nel_layout(righe, SEME, I7)
    elenco = ID.elenco_pagine(SOLO, righe)
    par = ID.pagine_con_parole(righe)
    pagine = [par[x['pagina']] for x in elenco]
    meta = [dict(sezione=x['sezione'], lingua=x['lingua'], mano=x['mano'], fascicolo=x['fascicolo'], bifoglio=x['bifoglio'], pos=x['pos'], n=x['n']) for x in elenco]
    return righe, elenco, pagine, meta


def vettori_voynich(elenco, v, sorgente='voynichese'):
    import immagini_vettori as V
    chiavi = [x['pagina'] for x in elenco]

    def crea(_c):
        ims = []
        for x in elenco:
            from PIL import Image
            if sorgente in ('voynichese', 'cornice'):
                im = Image.open(ID.percorso_voynichese(x['pagina'])).convert('RGB')
                bb = ID.riquadri_voynichese(x['pagina'])
            else:
                im = Image.open(ID.percorso_iiif(x['pagina'])).convert('RGB')
                bb = ID.riquadri_iiif(x['pagina'])
            ims.append(ID.mascherata(im, bb))
        if sorgente == 'cornice':
            ims = [ID.cornice_vuota(im) for im in ims]
        return V.vettori(ims, v[0], v[1], fili=PROCESSI)
    r = V.con_cache(os.path.join(CACHE29, 'vettori'), 'voynich_%s_%s_%s' % (sorgente, v[0], v[1]), chiavi, crea,
                    'Voynich (%s), modello %s, variante %s, testo coperto con i riquadri' % (sorgente, v[0], v[1]))
    return r[v[2]]


def vettori_finti(n, Efuchs, seme):
    """Per le prove (SOLO_CONTROLLI): n vettori presi a caso dal controllo Fuchs (nessuna immagine del Voynich)."""
    rng = np.random.default_rng(seme)
    return np.asarray(Efuchs)[rng.integers(0, len(Efuchs), size=n)]


def mediana(x):
    return float(np.median(x)) if len(x) else None


def tasso(x):
    return float(np.mean(x)) if len(x) else None


# ---------------------------------------------------------------- fasi
def fase_K(unita, meta, pagine, vett):
    """Controllo positivo: legame in un erbario vero e curva di diluizione."""
    out = OrderedDict()
    N = len(pagine)
    out['unita_totali'] = N
    out['parole_per_unita_mediana'] = mediana([len(p) for p in pagine])
    out['direzione'] = DIREZIONE
    n120 = min(NK, N)     # (il nome e' rimasto: sono NK unita', 240)
    for var, E in vett.items():
        lavori = [('puro', var, pagine, E, meta, n120, None, SEME * 1000 + s, B_CTRL) for s in range(SOTTO)]
        ris = esegui(lavoro_controllo, lavori)
        out['principale_%s' % var] = OrderedDict([('n', n120), ('r_mediana', mediana([r['r'] for r in ris])), ('rilevazioni_libera_001', tasso([r['p_libera'] <= 0.01 and r['r'] > 0 for r in ris])),
                                                  ('rilevazioni_ciclica_001', tasso([r['p_ciclica'] <= 0.01 and r['r'] > 0 for r in ris])),
                                                  ('rilevazioni_libera_005', tasso([r['p_libera'] <= 0.05 and r['r'] > 0 for r in ris]))])
        log('K', var, out['principale_%s' % var])
    var = nome_var(PRINCIPALE)
    E = vett[var]
    curva = OrderedDict()
    for nome, deg in DEGRADAZIONI:
        lavori = [(nome, var, pagine, E, meta, n120, deg, SEME * 2000 + s, B_CTRL) for s in range(SOTTO)]
        ris = esegui(lavoro_controllo, lavori)
        curva[nome] = OrderedDict([('r_mediana', mediana([r['r'] for r in ris])), ('rilevazioni_libera_001', tasso([r['p_libera'] <= 0.01 and r['r'] > 0 for r in ris])),
                                   ('rilevazioni_ciclica_001', tasso([r['p_ciclica'] <= 0.01 and r['r'] > 0 for r in ris]))])
        log('K', nome, curva[nome])
    out['curva_diluizione'] = curva
    curva_n = OrderedDict()
    for n in sorted({min(60, N), min(120, N), min(178, N), min(NK, N), N}):
        k = SOTTO if n < N else max(2, SOTTO // 4)
        lavori = [('N=%d' % n, var, pagine, E, meta, n, None, SEME * 3000 + s, B_CTRL) for s in range(k)]
        ris = esegui(lavoro_controllo, lavori)
        curva_n[str(n)] = OrderedDict([('r_mediana', mediana([r['r'] for r in ris])), ('rilevazioni_libera_001', tasso([r['p_libera'] <= 0.01 and r['r'] > 0 for r in ris])),
                                       ('sottocampioni', k)])
        log('K', 'N', n, curva_n[str(n)])
    out['curva_numero_pagine'] = curva_n
    return out


def fase_N(unita, meta_c, pagine_c, vett_c, elenco, meta, pagine, E, Dy, Dx, righe):
    """Controlli negativi: (N1) vettori visivi rimescolati dentro la sezione (Voynich) o liberamente (Fuchs); (N2) latino nella disposizione del Voynich."""
    import ia07_voynich_neurale as I7
    out = OrderedDict()
    Ec = vett_c[nome_var(PRINCIPALE)]
    Dyc = L.distanza_vocabolario(L.matrice_conteggi(pagine_c)[0])
    Dxc = L.distanza_visiva(Ec)
    # N1 su Fuchs: tutte le unita' in un solo gruppo di sezione -> permutazione libera
    lav = [('fuchs', Dyc, Dxc, meta_c, SEME * 4000 + s, B_POT) for s in range(RIP_NEG)]
    ris = esegui(L.lavoro_negativo_libero, lav)
    out['N1_fuchs'] = OrderedDict([('repliche', len(ris)), ('rifiuti_005_ciclica', tasso([r['p_ciclica'] <= 0.05 for r in ris])), ('rifiuti_005_libera', tasso([r['p_libera'] <= 0.05 for r in ris])),
                                   ('rifiuti_001_ciclica', tasso([r['p_ciclica'] <= 0.01 for r in ris])), ('r_media', float(np.mean([r['r'] for r in ris])))])
    log('N1 fuchs', out['N1_fuchs'])
    lav = [('voynich', Dy, Dx, meta, SEME * 5000 + s, B_POT) for s in range(RIP_NEG)]
    ris = esegui(L.lavoro_negativo_libero, lav)
    out['N1_voynich'] = OrderedDict([('repliche', len(ris)), ('rifiuti_005_ciclica', tasso([r['p_ciclica'] <= 0.05 for r in ris])), ('rifiuti_005_libera', tasso([r['p_libera'] <= 0.05 for r in ris])),
                                     ('rifiuti_001_ciclica', tasso([r['p_ciclica'] <= 0.01 for r in ris])), ('r_media', float(np.mean([r['r'] for r in ris])))])
    log('N1 voynich', out['N1_voynich'])
    # N2: latino nella disposizione del Voynich con i vettori veri (o finti) delle pagine
    base = ID.righe_voynich(True)
    lav = []
    for s in range(RIP_LAT):
        rr = ID.latino_nel_layout(base, SEME * 6000 + s, I7)
        par = ID.pagine_con_parole(rr)
        pg = [par[x['pagina']] for x in elenco]
        lav.append(('latino', pg, Dx, meta, SEME * 6000 + s, B_POT))
    ris = esegui(L.lavoro_testo, lav)
    out['N2_latino'] = OrderedDict([('repliche', len(ris)), ('rifiuti_005', int(sum(r['p'] <= 0.05 for r in ris))), ('rifiuti_001', int(sum(r['p'] <= 0.01 for r in ris))),
                                    ('r_media', float(np.mean([r['r'] for r in ris])))])
    log('N2 latino', out['N2_latino'])
    return out


def fase_P(elenco, meta, pagine, E, Dx):
    """Potenza: legami piantati di forza q sul disegno del Voynich (testo vero, o latino in prova)."""
    lav = [('pot', pagine, E, meta, Dx, q, SEME * 7000 + int(q * 1000) * 100 + s, B_POT) for q in QS for s in range(RIP_POT)]
    ris = esegui(L.lavoro_potenza, lav)
    out = OrderedDict()
    for q in QS:
        rr = [r for r in ris if r['q'] == q]
        out['%.2f' % q] = OrderedDict([('repliche', len(rr)), ('r_mediana', mediana([r['r'] for r in rr])), ('r_valori', sorted(r['r'] for r in rr)),
                                       ('potenza_001', tasso([r['p'] <= 0.01 and r['r'] > 0 for r in rr])), ('potenza_005', tasso([r['p'] <= 0.05 and r['r'] > 0 for r in rr]))])
        log('P', q, {k: v for k, v in out['%.2f' % q].items() if k != 'r_valori'})
    q80 = next((q for q in QS if q > 0 and out['%.2f' % q]['potenza_001'] >= SOGLIE['potenza']), None)
    return OrderedDict([('per_q', out), ('q_potenza_80', q80), ('r_a_q_potenza_80', out['%.2f' % q80]['r_mediana'] if q80 else None)])


def fase_V(elenco, meta, pagine, vett_voy, righe):
    """Prova sul Voynich: principale (vocabolario a parole, DINOv2 small in grigio, tutte le pagine) e varianti."""
    out = OrderedDict()
    rng = np.random.default_rng(SEME * 8000)
    Dy = L.distanza_vocabolario(L.matrice_conteggi(pagine)[0])
    for var, E in vett_voy.items():
        Dx = L.distanza_visiva(E)
        B = PERM if var == nome_var(PRINCIPALE) else PERM_VAR
        a = L.prova(Dy, Dx, meta, rng, B=B, nulla='ciclica')
        b = L.prova(Dy, Dx, meta, rng, B=PERM_VAR, nulla='libera')
        out['variante_%s' % var] = OrderedDict([('pagine', len(pagine)), ('coppie', a['coppie']), ('r', a['r']), ('p_ciclica', a['p']), ('p_libera', b['p']),
                                                ('nulla_media', a['media_nulla']), ('nulla_sd', a['sd_nulla'])])
        log('V', var, out['variante_%s' % var])
    var = nome_var(PRINCIPALE)
    E = vett_voy[var]
    Dx = L.distanza_visiva(E)
    # testo a "pezzi di parola"
    Dyb = L.distanza_vocabolario(L.matrice_conteggi(L.bigrammi_pagine(pagine), minimo=3)[0], minimo_pagine=3, massimo_quota=0.9)
    Dyj = L.distanza_testo(L.matrice_conteggi(pagine)[0])
    a = L.prova(Dyb, Dx, meta, rng, B=PERM_VAR, nulla='ciclica')
    out['testo_bigrammi'] = OrderedDict([('r', a['r']), ('p_ciclica', a['p'])])
    a = L.prova(Dyj, Dx, meta, rng, B=PERM_VAR, nulla='ciclica')
    out['testo_jsd'] = OrderedDict([('r', a['r']), ('p_ciclica', a['p'])])
    # immagini IIIF a 1500 pixel (solo per le pagine con riquadri registrati)
    if not SOLO:
        sub = [i for i, x in enumerate(elenco) if ID.percorso_iiif(x['pagina']) and ID.riquadri_iiif(x['pagina']) is not None]
        if len(sub) >= 40:
            Eg = vettori_voynich([elenco[i] for i in sub], PRINCIPALE, 'iiif')
            ms = [meta[i] for i in sub]
            Dys = L.distanza_vocabolario(L.matrice_conteggi([pagine[i] for i in sub])[0])
            a = L.prova(Dys, L.distanza_visiva(Eg), ms, rng, B=PERM_VAR, nulla='ciclica')
            out['immagini_iiif'] = OrderedDict([('pagine', len(sub)), ('r', a['r']), ('p_ciclica', a['p'])])
            log('V iiif', out['immagini_iiif'])
    # senza una sezione alla volta, solo r (nessuna permutazione), e solo una sezione per volta con prova
    sez = sorted({m['sezione'] for m in meta})
    loso = OrderedDict()
    for s in sez:
        ix = [i for i, m in enumerate(meta) if m['sezione'] != s]
        if len(ix) < 20:
            continue
        ms = [meta[i] for i in ix]
        Dys = L.distanza_vocabolario(L.matrice_conteggi([pagine[i] for i in ix])[0])
        loso[s] = OrderedDict([('pagine', len(ix)), ('r', L.r_osservato(Dys, L.distanza_visiva(np.asarray(E)[ix]), ms))])
    out['senza_una_sezione'] = loso
    solo = OrderedDict()
    for s in sez:
        ix = [i for i, m in enumerate(meta) if m['sezione'] == s]
        if len(ix) < 25:
            continue
        ms = [meta[i] for i in ix]
        Dys = L.distanza_vocabolario(L.matrice_conteggi([pagine[i] for i in ix])[0])
        a = L.prova(Dys, L.distanza_visiva(np.asarray(E)[ix]), ms, rng, B=PERM_VAR, nulla='ciclica')
        solo[s] = OrderedDict([('pagine', len(ix)), ('r', a['r']), ('p_ciclica', a['p'])])
    out['solo_una_sezione'] = solo
    return out


def sintesi(K, Nn, P, V, meta):
    """Letture preregistrate (vedi preregistrazioni/ia29.md)."""
    S = OrderedDict()
    prin = 'principale_%s' % nome_var(PRINCIPALE)
    S['controllo_positivo_riuscito'] = bool(K and K[prin]['rilevazioni_libera_001'] is not None and K[prin]['rilevazioni_libera_001'] >= SOGLIE['controllo_positivo_rilevazioni'])
    S['controllo_positivo_rilevazioni_a_NK'] = K[prin]['rilevazioni_libera_001'] if K else None
    neg_ok = None
    if Nn:
        neg_ok = (Nn['N1_fuchs']['rifiuti_005_ciclica'] <= SOGLIE['negativo_rifiuti_005'] and Nn['N1_voynich']['rifiuti_005_ciclica'] <= SOGLIE['negativo_rifiuti_005']
                  and Nn['N2_latino']['rifiuti_005'] <= SOGLIE['negativo_latino_su_20'] * Nn['N2_latino']['repliche'] / 20.0)
    S['controlli_negativi_riusciti'] = neg_ok
    rK = K[prin]['r_mediana'] if K else None
    S['r_controllo_erbario'] = rK
    if P:
        S['q_potenza_80'] = P['q_potenza_80']
        S['r_a_q_potenza_80'] = P['r_a_q_potenza_80']
    if V and P:
        v = V['variante_%s' % nome_var(PRINCIPALE)]
        robusto = all(x['r'] > 0 for x in V['senza_una_sezione'].values()) if V['senza_una_sezione'] else False
        cor = V.get('variante_cornice')
        cornice_ok = cor is None or cor['p_ciclica'] > SOGLIE['alfa_grigia']
        S['cornice_vuota_p'] = cor['p_ciclica'] if cor else None
        S['robusto_senza_una_sezione'] = robusto
        q_sup = None
        for q in QS:
            if q == 0:
                continue
            rv = P['per_q']['%.2f' % q]['r_valori']
            if np.mean([x <= v['r'] for x in rv]) <= SOGLIE['limite_superiore']:
                q_sup = q
                break
        S['r_osservato'] = v['r']
        S['p_principale'] = v['p_ciclica']
        S['q_limite_superiore_95'] = q_sup
        S['r_a_q_limite'] = P['per_q']['%.2f' % q_sup]['r_mediana'] if q_sup else None
        controlli = bool(S['controllo_positivo_riuscito'] and neg_ok)
        if not controlli:
            lettura = 'non leggibile (un controllo non e\' riuscito)'
        elif v['p_ciclica'] <= SOGLIE['alfa_principale'] and v['r'] > 0 and robusto and cornice_ok:
            lettura = 'legame presente'
        elif v['p_ciclica'] > SOGLIE['alfa_grigia']:
            if q_sup is not None and S['r_a_q_limite'] is not None and rK is not None and S['r_a_q_limite'] <= rK:
                lettura = 'legame assente (sotto la soglia di potenza): nessun legame piu\' forte di q=%.2f' % q_sup
            else:
                lettura = 'non leggibile (potenza insufficiente per un legame della forza dell\'erbario)'
        else:
            lettura = 'zona grigia'
        S['lettura'] = lettura
    return S


def scrivi(ris):
    os.makedirs(USCITA, exist_ok=True)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    o = ['# ia29 — Immagini e vocabolario della pagina', '',
         'Solo numeri e aggregati. Preregistrazione: `preregistrazioni/ia29.md`.%s' % (' **PROVA SOLO SU CONTROLLI (testo latino, immagini finte): non e\' un risultato.**' if SOLO else ''), '']
    S = ris.get('sintesi')
    if S:
        o += ['## Sintesi', ''] + ['- %s: %s' % (k, v) for k, v in S.items()] + ['']
    for k in ('controllo_positivo', 'controlli_negativi', 'potenza', 'voynich'):
        if k in ris:
            o += ['## %s' % k, '', '```', json.dumps(ris[k], ensure_ascii=False, indent=1), '```', '']
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(o) + '\n')


def main():
    t0 = time.time()
    os.makedirs(CACHE29, exist_ok=True)
    fasi_dir = os.path.join(CACHE29, 'fasi')
    os.makedirs(fasi_dir, exist_ok=True)
    ris = OrderedDict([('esperimento', 'ia29'), ('solo_controlli', SOLO), ('piccolo', PICCOLO), ('fasi', FASI), ('modelli', MODELLI29), ('soglie', SOGLIE),
                       ('direzione_controllo', DIREZIONE), ('permutazioni', PERM), ('tempi_s', OrderedDict())])

    def fatta(nome):
        p = os.path.join(fasi_dir, nome + '.json')
        return json.load(open(p, encoding='utf-8')) if RIPRENDI and os.path.exists(p) else None

    def salva(nome, v):
        json.dump(v, open(os.path.join(fasi_dir, nome + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    def cronometra(nome, f):
        t = time.time()
        r = f()
        ris['tempi_s'][nome] = round(time.time() - t, 1)
        return r

    log('ia29', 'SOLO_CONTROLLI' if SOLO else 'Voynich', 'fasi', FASI, 'processi', PROCESSI)
    unita, meta_c, pagine_c, vett_c = cronometra('E_controllo', carica_controllo)
    ris['controllo_unita'] = len(unita)
    righe, elenco, pagine, meta = carica_voynich()
    log('pagine del campione', len(elenco), 'unita del controllo', len(unita))
    if SOLO:
        E = vettori_finti(len(elenco), vett_c[nome_var(PRINCIPALE)], SEME)
        vett_voy = {nome_var(PRINCIPALE): E, 'cornice': vettori_finti(len(elenco), vett_c[nome_var(PRINCIPALE)], SEME + 1)}
    else:
        vett_voy = OrderedDict()
        for v in VARIANTI:
            if v[0] == 'clip' and 'clip' not in MODELLI29:
                continue
            vett_voy[nome_var(v)] = cronometra('E_voynich_' + nome_var(v), lambda v=v: vettori_voynich(elenco, v))
        vett_voy['cornice'] = cronometra('E_voynich_cornice', lambda: vettori_voynich(elenco, PRINCIPALE, 'cornice'))
        E = vett_voy[nome_var(PRINCIPALE)]
    ris['campione'] = OrderedDict([('pagine', len(elenco)), ('per_sezione', OrderedDict(sorted(((s, sum(1 for m in meta if m['sezione'] == s)) for s in {m['sezione'] for m in meta})))),
                                   ('parole_per_pagina_mediana', mediana([m['n'] for m in meta]))])
    Dy = L.distanza_vocabolario(L.matrice_conteggi(pagine)[0])
    Dx = L.distanza_visiva(E)
    K = Nn = P = V = None
    if 'K' in FASI:
        K = fatta('K') or cronometra('K', lambda: fase_K(unita, meta_c, pagine_c, vett_c))
        salva('K', K)
        ris['controllo_positivo'] = K
    if 'N' in FASI:
        Nn = fatta('N') or cronometra('N', lambda: fase_N(unita, meta_c, pagine_c, vett_c, elenco, meta, pagine, E, Dy, Dx, righe))
        salva('N', Nn)
        ris['controlli_negativi'] = Nn
    if 'P' in FASI:
        P = fatta('P') or cronometra('P', lambda: fase_P(elenco, meta, pagine, E, Dx))
        salva('P', P)
        ris['potenza'] = P
    if 'V' in FASI:
        V = fatta('V') or cronometra('V', lambda: fase_V(elenco, meta, pagine, vett_voy, righe))
        salva('V', V)
        ris['voynich'] = V
    if 'S' in FASI:
        ris['sintesi'] = sintesi(K or fatta('K'), Nn or fatta('N'), P or fatta('P'), V or fatta('V'), meta)
    ris['tempi_s']['totale'] = round(time.time() - t0, 1)
    scrivi(ris)
    log('fatto in %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
