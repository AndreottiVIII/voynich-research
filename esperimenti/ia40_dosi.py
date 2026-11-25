# -*- coding: utf-8 -*-
"""Esperimento IA40 (ia40): tavola a dosi forzate sul Voynich. Niente ottimizzatore.

Domanda: in IA34, IA36 e IA37 l'ottimizzatore non ha mai acceso sul Voynich i meccanismi nuovi (memoria di sezione 0-0,03, `a_sez` 0): non vedeva la misura da aggiustare, era rumoroso e partiva dal meccanismo
spento. Quindi i tentativi sulla sezione non sono mai stati provati davvero. Esiste una regolazione scelta a mano, a dosi fisse, con `sezione` entro 2 sigma e giudice b sotto 0,65?
Si parte dal punto di IA35 sul Voynich (`dati/cache/ia35/vero/ciclo_esito.json`), rete `Cb` di IA35 (cache di IA37), scrittore di IA37 (`freqsez_scrittura.ScrittoreFreq`; per la memoria di sezione la sua classe
madre di IA36, `prudente_scrittura.ScrittoreSez`: con `w_sez` = 0 e `a_sez` = 0 danno lo stesso libro, provato in IA37). Una riga = un punto di manopole fisso, 8 libri interi con semi nuovi; esame di IA37
(giudici N, KN, b mediato su 8 divisioni, dieci misure, divergenza fra sezioni, guardia anti-copia), `sezione` riportata a parte (non e' piu' tenuta fuori). Solo il mondo `vero`.
Preregistrazione: preregistrazioni/ia40.md. Nessun modulo nuovo: si riusano quelli di IA32-IA37.

Righe (`RIGHE40` ne sceglie un sottoinsieme, `ETICHETTA40` e `SEMI40` cambiano nome delle uscite e semi per rifare una riga con altri semi):
  t000 t025 t050 t075 t100    termostato globale a forza 0, 0,25, 0,5, 0,75, 1 (moltiplica `w_cont`, `w_tri`, `w_quad`, `w_uni`, `w_bi` del punto di IA35; il resto fermo; t100 = punto di IA35)
  s50k30 s50k100 s50k300 s100k30 s100k100 s100k300   termostato per sezione acceso al punto di IA35: `a_sez` 0,5 e 1, ripiego K 30, 100, 300
  m20 m50                     memoria di sezione di IA36 al punto di IA35: `w_sez` 0,2 e 0,5 (decadimento neutro)
  neu                         manopole neutre (rete sola)
  t100r s100k100r             ripetizioni con altri semi di due righe scelte prima: il rumore

    nohup bash strumenti/coda.sh ia40 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia40" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella nel repo> CACHE40=<cartella nel repo> python esperimenti/ia40_dosi.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): MONDI40 (2 = vero, predefinito; 3 = mondo di sviluppo, solo con SOLO_CONTROLLI=1), CACHE40, N_LIBRI40 (8), N_GRU40 (3: libri per riga con k90 e R_rel),
RIGHE40 (elenco di righe separate da barre verticali, vuoto = tutte), ETICHETTA40, SEMI40, PUNTO_BASE40 (ia35 o stress: stress solo per il mondo di sviluppo), FASI (P, E, S; predefinito PES). Valgono quelle di IA26 e IA32-IA35.
"""
import json
import math
import os
import shutil
import sys
import time
import zlib
from collections import OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402

NOME = 'ia40_dosi'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE40 = os.environ.get('CACHE40', os.path.join(USCITA, 'ia40_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia40'))
CACHE37_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia37')
CACHE35_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia35')
os.environ['CACHE26'] = os.path.join(CACHE40, 'banco')          # il banco di IA26 scrive qui, mai nella cache di IA26, IA32, IA35, IA37 ne' IA38
os.environ.setdefault('CHUNK26', '500')                         # un solo gruppo di testi per i lavori K, KN e D
os.environ.setdefault('S_GRU_MONDO26', '6')
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_giudice as RGB  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import piano_lavori as PL  # noqa: E402
import sezione_mondo as SMO  # noqa: E402
import sezione_misure as SM  # noqa: E402
import sezione_rete as SR  # noqa: E402
import sezione_lavori as SL  # noqa: E402
import prudente_lavori as PLV  # noqa: E402
import prudente_scrittura as PW  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402
import freqsez_scrittura as FW  # noqa: E402
import freqsez_lavori as FL  # noqa: E402
if os.environ.get('SOLO_CONTROLLI') == '1':
    import prudente_mondo  # noqa: E402,F401   (il mondo di sviluppo `struttura3`: solo prove)

_ATTIVO = {}
MONDI_ELENCO = ['struttura2', 'vero', 'struttura3']
MONDI40 = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI40', '2') if x.isdigit() and 1 <= int(x) <= (3 if SOLO_CONTROLLI else 2)]
N_LIBRI = int(os.environ.get('N_LIBRI40', 8))
N_GRU = int(os.environ.get('N_GRU40', 3))
RIGHE_SCELTE = [x for x in os.environ.get('RIGHE40', '').split('|') if x]
ETICHETTA = os.environ.get('ETICHETTA40', '')
SEMI = os.environ.get('SEMI40', '')
PUNTO_BASE = os.environ.get('PUNTO_BASE40', 'ia35')
PIEGHE = I7.PIEGHE
GRU = os.environ.get('GRU40', '1') == '1'

# ---- criteri e soglie dell'esame (quelle di IA35-IA37)
AUC_MAX = 0.60
SIGMA_DA_SCALA = 1.0 / math.sqrt(2.0)
GIUDICI3 = ('N', 'KN', 'b')
# gli esiti scritti prima (preregistrazione): una riga e' "buona" se `sezione` e' entro 2 sigma, b <= B_MAX e almeno NOVE_MIN delle altre nove misure sono entro 2 sigma
B_MAX = 0.65
NOVE_MIN = 7
# punto di sviluppo (solo con SOLO_CONTROLLI=1 e PUNTO_BASE40=stress): un punto moderato scritto a mano al posto del punto di IA35, che c'e' solo in `dati/cache`
VALORI_STRESS2 = OrderedDict([('T_eol', 0.8), ('w_cont', 3.0), ('w_tri', 3.0), ('w_quad', 3.0), ('s', 0.8), ('w_uni', 1.0), ('w_bi', 1.0), ('b_nuove', -0.8), ('w_pag', 0.3)])


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia40_corse_%s%s.jsonl' % (mondo, ('_' + ETICHETTA) if ETICHETTA else ''))


def leggi_corse(percorso):
    if not os.path.exists(percorso):
        return []
    out = []
    for l in open(percorso, encoding='utf-8'):
        if l.strip():
            try:
                out.append(json.loads(l))
            except ValueError:
                pass
    return out


def fatte_di(mondo):
    if os.environ.get('RIPRENDI') == '1':
        return {c['lavoro'] for c in leggi_corse(percorso_corse(mondo)) if not c.get('errore')}
    return set()


def azzera_corse(mondo):
    if os.environ.get('RIPRENDI') != '1':
        os.makedirs(USCITA, exist_ok=True)
        open(percorso_corse(mondo), 'w').close()


def avvia(mondo, nomi):
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    RM.prepara(mondo, cart40(mondo), nomi)
    PLV.carica_guardie()


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia36_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro40, da_fare), 1):
            out.append(r)
            if scrivi:
                with open(percorso_corse(mondo), 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: (round(r[x], 3) if isinstance(r[x], float) else r[x]) for x in ('obiettivo', 'obiettivo_puro', 'penalita', 'AUC_e231', 'AUC_N', 'copia_netta', 'k90') if x in r}
                print('[%s %d/%d %.1f min] %s: %s (%.0f s)' % (mondo, k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def attiva_main(mondo, nomi=()):
    """Attiva il mondo nel processo principale UNA volta sola (come in IA35: un solo mondo per processo, gli altri in un processo figlio)."""
    if _ATTIVO.get('mondo') == mondo:
        B._S['nomi'] = [n for n in nomi if n != 'vero']
        return B._S
    if _ATTIVO:
        raise RuntimeError('un solo mondo per processo: %s e poi %s' % (_ATTIVO['mondo'], mondo))
    _ATTIVO['mondo'] = mondo
    return B.imposta_mondo(mondo, list(nomi))


def esegui_rif(mondo, lavori, processi, fatte, corse):
    da_fare = [a for a in lavori if ident(a) not in fatte]
    out = []
    if not da_fare:
        return out
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_banco, initargs=(mondo,)) as pool:
        for k, r in enumerate(pool.imap_unordered(B.lavoro, da_fare), 1):
            out.append(r)
            with open(corse, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                print('[rif %s %d/%d] %s (%.0f s)' % (mondo, k, len(da_fare), r['lavoro'], r.get('secondi', 0)), flush=True)
    return out


def avvia_banco(mondo):
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    B.imposta_mondo(mondo, [])


def costruisci_riferimento(mondo, processi):
    """Il riferimento del mondo: copiato da IA35 (corsa vera) o costruito con i lavori del banco (prove)."""
    dest = os.path.join(CACHE40, 'banco', mondo)
    os.makedirs(os.path.join(dest, 'modelli_misura'), exist_ok=True)
    rif_p = os.path.join(dest, 'riferimento.json')
    copia_da_ia37(mondo)
    if os.path.exists(rif_p):
        return completa_gru(mondo, json.load(open(rif_p, encoding='utf-8')), rif_p, processi)
    print('riferimento di %s: costruzione con i lavori del banco' % mondo, flush=True)
    attiva_main(mondo, [])
    fasi = B.fasi_banco([], con_gru=GRU, con_vero=True, mondo=mondo)
    fn = [a for a in fasi['N'] if a[1] != 'A']
    corse = percorso_corse(mondo + '_rif')
    fatte, ris = set(), []
    for lst in (fasi['B'], fn):
        ris += esegui_rif(mondo, lst, processi, fatte, corse)
    C = B.indice_corse(ris + [c for c in leggi_corse(corse) if not c.get('errore')])
    rif = B.riferimento_da_corse(C)
    json.dump(rif, open(rif_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return rif


def completa_gru(mondo, rif, rif_p, processi):
    if not GRU or 'k90' in rif['vero']:
        return rif
    print('riferimento di %s: aggiungo k90 e R_rel (reti piccole)' % mondo, flush=True)
    attiva_main(mondo, [])
    n_split = B.S_GRU if mondo == 'vero' else B.S_GRU_MONDO
    lavori = [('G', tp, 'vero', s) for s in B.SEMI_GRU_VERO[:1] for tp in ('K', 'R')]
    lavori += [('gm', tp, s, m) for s in range(1, n_split + 1) for m in (1, 2) for tp in ('K', 'R')]
    corse = percorso_corse(mondo + '_rif')
    ris = esegui_rif(mondo, lavori, processi, set(), corse)
    r2 = B.riferimento_da_corse(B.indice_corse(ris))
    for blocco in ('vero', 'scala', 'fascia'):
        for m in ('k90', 'R_rel'):
            if m in r2[blocco]:
                rif[blocco][m] = r2[blocco][m]
    for k in ('seme_sd', 'divisioni_rete'):
        if k in r2:
            rif[k] = r2[k]
    with open(rif_p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rif, f, ensure_ascii=False, indent=1, default=float)
    return rif


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def riassunto_insieme(mondo, A, tipo):
    """Per un insieme di libri: AUC dei tre giudici mai visti (media, deviazione standard fra libri, errore), giudici di allenamento, misure tenute fuori (D, R_rel e le otto di struttura), guardie, copia."""
    rif, prof, nm_rif, nm = A['rif'], A['prof'], A['nm_rif'], A['nm']
    ls = [nome_libro(tipo, i) for i in range(1, A['ins'][tipo]['n'] + 1)]
    out = OrderedDict([('n', len(ls)), ('ruolo', A['ins'][tipo]['ruolo'])])
    jud = OrderedDict()
    for j in ('N', 'KN'):
        vs = [prof[l].get(j) for l in ls]
        vs = [x for x in vs if x is not None]
        nu = (rif['nullo'].get(j) or {}).get('sd') or 0.0
        s = sd(vs) or 0.0
        jud[j] = OrderedDict([('media', media(vs)), ('sd_libri', s), ('n', len(vs)), ('errore', math.sqrt(s * s / max(len(vs), 1) + nu * nu))])
    b = A['giudice_b'].get(tipo) or {}
    nb = len(b.get('per_libro') or [])
    s = b.get('sd_libri') or 0.0
    jud['b'] = OrderedDict([('media', b.get('auc')), ('sd_libri', s), ('n', nb), ('errore', math.sqrt(s * s / max(nb, 1) + (b.get('nullo_sd') or 0.0) ** 2)),
                            ('nullo_media', b.get('nullo_media')), ('nullo_sd', b.get('nullo_sd'))])
    out['giudici_mai_visti'] = jud
    out['giudici_ok'] = bool(all(v['media'] is not None and (1 - AUC_MAX) <= v['media'] <= AUC_MAX for v in jud.values()))
    out['giudici_di_allenamento'] = OrderedDict((j, media([prof[l].get(j) for l in ls])) for j in PL.OBI_GIUDICI34)
    mis = OrderedDict()
    for m in PLV.FUORI_MISURE36:
        if m in SM.NOMI_NM8:
            vero, s_ = (nm_rif['vero'] or {}).get(m), (nm_rif['sigma'] or {}).get(m)
            val = media([(nm.get('NM|%s' % l) or nm.get(l) or {}).get(m) for l in ls])
        else:
            if m not in rif['vero'] or rif['scala'].get(m) is None:
                continue
            vero, s_ = rif['vero'][m], rif['scala'][m] * SIGMA_DA_SCALA
            val = media([prof[l].get(m) for l in ls])
        if val is None or not s_ or vero is None:
            continue
        z = (val - vero) / s_
        mis[m] = OrderedDict([('valore', val), ('vero', vero), ('sigma', s_), ('z', z), ('entro_2sigma', bool(abs(z) <= 2.0))])
    out['misure_tenute_fuori'] = mis
    out['quota_entro_2sigma'] = float(np.mean([x['entro_2sigma'] for x in mis.values()])) if mis else None
    out['misure_fuori'] = [m for m, x in mis.items() if not x['entro_2sigma']]
    ali = OrderedDict()
    for m in PL.OBI_MISURE34:
        if m in rif['vero'] and rif['scala'].get(m):
            val = media([prof[l].get(m) for l in ls])
            if val is not None:
                ali[m] = OrderedDict([('valore', val), ('vero', rif['vero'][m]), ('z_sigma', (val - rif['vero'][m]) / (rif['scala'][m] * SIGMA_DA_SCALA))])
    out['misure_di_allenamento'] = ali
    dvv = OrderedDict()                                             # la diagnosi: divergenza fra sezioni (bit); descrittiva, mai nei criteri
    for m in ('bigr', 'parole'):
        val = media([(A['dv'].get('DV|%s' % l) or A['dv'].get(l) or {}).get(m) for l in ls])
        dvv[m] = OrderedDict([('valore', val), ('vero', A['dv_rif'].get(m))])
    out['diagnosi'] = dvv
    cop = A['corse_libro']
    viol = [max(cop['libro|%s|%d' % (tipo, i)]['copia_violazioni'].values() or [0.0]) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]
    out['copia_ok'] = bool(viol) and max(viol) <= 0.0
    out['copia_violazione_max'] = max(viol) if viol else None
    out['copia_quote'] = OrderedDict((k, media([cop['libro|%s|%d' % (tipo, i)]['copia'].get(k) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]))
                                     for k in RM.SOGLIE_COPIA)
    return out


def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def cart40(mondo, *p):
    return os.path.join(CACHE40, mondo, *p)


def ident(a):
    if a[0] == 'B35':
        return 'B35|%s' % a[1]
    if a[0] == 'libro40':
        return 'libro|%s|%s' % (a[1], a[2])
    return '|'.join(str(x) for x in a)


# ---------------------------------------------------------------- lo scrittore e i libri

def scrittore40(spec):
    """Lo scrittore di una riga: `['L', cubo a 15, K]` -> scrittore di IA37 (`ScrittoreFreq`; K = ripiego, None = quello del file o 20: non conta con `a_sez` = 0);
    `['M', cubo a 16]` -> lo scrittore di IA36 con la memoria di sezione (`ScrittoreSez`), da cui IA37 discende."""
    cart = os.path.join(RM._W['cart'], 'rete_C')
    if spec[0] == 'M':
        k = ('M',)
        if k not in RM._W:
            RM._W[k] = PW.ScrittoreSez(cart)
        return RM._W[k]
    K = spec[2]
    k = ('L', K)
    if k not in RM._W:
        S = FW.ScrittoreFreq(cart)
        if K:
            S.K = float(K)
            S.tab = FT.TabelleSezione(S, S.P.f_add, S.K)
            S._lex_sez = {}
        RM._W[k] = S
    return RM._W[k]


def scrivi_libro40(tipo, i, spec, seme):
    """Un libro intero della riga `tipo` (nel formato del banco). -> dict (come `prudente_lavori.scrivi_libro36`)."""
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    man = None
    if os.path.exists(p):
        t = I7.leggi_file(p)
    else:
        t, man = scrittore40(spec).libro33(np.asarray(spec[1], float), seme, None)
        I7.scrivi_file(t, p + '.tmp', 'ia40, libro %s %d, mondo %s' % (tipo, i, RM._W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro40(args):
    if args[0] == 'libro40':
        try:
            return scrivi_libro40(args[1], int(args[2]), args[3], int(args[4]))
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'libro|%s|%s' % (args[1], args[2])), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = FL.lavoro_banco37(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


# ---------------------------------------------------------------- le righe

IDX_CONTI = (6, 7, 8, 10, 11)                       # w_cont, w_tri, w_quad, w_uni, w_bi nel cubo
U_PIATTO = 0.2                                      # sotto 0,2 la manopola e' zero: il peso vale max(0, c (u - 0,2)) e si scala con u' = 0,2 + f (u - 0,2)


def punto_base(mondo):
    """Il punto di IA35 per il mondo (cubo a 14); nel mondo di sviluppo con PUNTO_BASE40=stress un punto moderato scritto a mano."""
    p = os.path.join(CACHE35_ORIG, mondo, 'ciclo_esito.json')
    if not SOLO_CONTROLLI and os.path.exists(p):
        return np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float)[:14]
    if SOLO_CONTROLLI and PUNTO_BASE == 'stress':
        return np.array(OS.cubo_da_valori(VALORI_STRESS2), float)
    raise RuntimeError('manca il punto di IA35 per il mondo %s (dati/cache/ia35/%s/ciclo_esito.json)' % (mondo, mondo))


def u_dose(u14, f):
    """Il termostato a forza `f`: moltiplica insieme `w_cont`, `w_tri`, `w_quad`, `w_uni`, `w_bi` (esatto, perche' il peso e' lineare sopra 0,2); il resto fermo."""
    u = np.array(u14, float)
    for i in IDX_CONTI:
        if u[i] > U_PIATTO:
            u[i] = U_PIATTO + f * (u[i] - U_PIATTO)
        else:
            u[i] = u[i]
    return u


def cubo15(u14, a_sez=0.0):
    return np.concatenate([np.asarray(u14, float), [U_PIATTO + 0.8 * a_sez]])


def cubo16(u14, w_sez):
    """Il cubo di IA36 (16 manopole) con la memoria di sezione `w_sez` e il decadimento neutro."""
    return np.concatenate([np.asarray(u14, float), [U_PIATTO + w_sez, PW.U_T_NEUTRO]])


def righe(u14):
    R = OrderedDict()
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        R['t%03d' % round(100 * f)] = dict(gruppo='termostato globale', descr='termostato globale a forza %g%s' % (f, ' (punto di IA35)' if f == 1.0 else ''), spec=['L', list(map(float, cubo15(u_dose(u14, f)))), None])
    for a in (0.5, 1.0):
        for K in (30, 100, 300):
            R['s%dk%d' % (round(100 * a), K)] = dict(gruppo='termostato per sezione', descr='punto di IA35 con a_sez %g, ripiego K %d' % (a, K), spec=['L', list(map(float, cubo15(u14, a))), K])
    for w in (0.2, 0.5):
        R['m%d' % round(100 * w)] = dict(gruppo='memoria di sezione', descr='punto di IA35 con w_sez %g (decadimento neutro)' % w, spec=['M', list(map(float, cubo16(u14, w)))])
    R['neu'] = dict(gruppo='riferimento', descr='manopole neutre (rete sola)', spec=['L', list(map(float, FW.neutro_cubo37())), None])
    R['t100r'] = dict(gruppo='rumore', descr='ripetizione di t100 con altri semi', spec=R['t100']['spec'])
    R['s100k100r'] = dict(gruppo='rumore', descr='ripetizione di s100k100 con altri semi', spec=R['s100k100']['spec'])
    if RIGHE_SCELTE:
        R = OrderedDict((k, v) for k, v in R.items() if k in RIGHE_SCELTE)
    return R


def nome_libro(tipo, i):
    return 'tar:%s:%d' % (tipo, i)


# ---------------------------------------------------------------- P: preparazione

def copia_da_ia37(mondo):
    """Dalla cache di IA37 (solo corsa vera): rete condizionata `rete_C`, riferimento e modelli di misura del banco, "naturale", otto misure di struttura, divergenza fra sezioni del vero.
    NON si copiano `libri`, `misure` ne' i risultati. -> True se ha copiato qualcosa."""
    if SOLO_CONTROLLI:
        return False
    ok = False
    o_banco = os.path.join(CACHE37_ORIG, 'banco', mondo)
    d_banco = os.path.join(CACHE40, 'banco', mondo)
    if os.path.exists(os.path.join(o_banco, 'riferimento.json')) and not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        os.makedirs(os.path.join(d_banco, 'modelli_misura'), exist_ok=True)
        for f in os.listdir(os.path.join(o_banco, 'modelli_misura')):
            if not os.path.exists(os.path.join(d_banco, 'modelli_misura', f)):
                shutil.copy(os.path.join(o_banco, 'modelli_misura', f), os.path.join(d_banco, 'modelli_misura', f))
        shutil.copy(os.path.join(o_banco, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
        print('riferimento e modelli di misura di %s copiati da IA37' % mondo, flush=True)
        ok = True
    os.makedirs(cart40(mondo), exist_ok=True)
    for nome in ('naturale.json', 'nuove_misure.json', 'diagnosi.json'):
        if os.path.exists(os.path.join(CACHE37_ORIG, mondo, nome)) and not os.path.exists(cart40(mondo, nome)):
            shutil.copy(os.path.join(CACHE37_ORIG, mondo, nome), cart40(mondo, nome))
            ok = True
    o_rete = os.path.join(CACHE37_ORIG, mondo, 'rete_C')
    if os.path.exists(os.path.join(o_rete, 'pieno.pt')) and not os.path.exists(cart40(mondo, 'rete_C', 'pieno.pt')):
        shutil.copytree(o_rete, cart40(mondo, 'rete_C'), dirs_exist_ok=True)
        print('rete condizionata di %s copiata da IA37 (la variante scelta in IA35)' % mondo, flush=True)
        ok = True
    return ok


def fase_P(mondo, processi):
    os.makedirs(cart40(mondo), exist_ok=True)
    rif = costruisci_riferimento(mondo, processi)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    nat_p = cart40(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    nm_p = cart40(mondo, 'nuove_misure.json')
    if not os.path.exists(nm_p):
        json.dump(SL.lavoro_riferimento_NM8(), open(nm_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    dv_p = cart40(mondo, 'diagnosi.json')
    if not os.path.exists(dv_p):
        json.dump(FL.lavoro_riferimento_DV(), open(dv_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    if SOLO_CONTROLLI and not os.path.exists(cart40(mondo, 'rete_C', 'pieno.pt')):         # solo prove: una rete piccola (variante Cb) se non c'e'
        SR.addestra_pieno35(cart40(mondo, 'rete_C'), cond=True, var=SR.VARIANTI['Cb'])
    if not os.path.exists(cart40(mondo, 'rete_C', 'pieno.pt')):
        raise RuntimeError('la rete condizionata di %s non e\' nella cache (si copia da dati/cache/ia37/%s/rete_C)' % (mondo, mondo))
    print('mondo %s: riferimento con %d misure e %d giudici; fogli addestramento/validazione/fuori %d/%d/%d' % (mondo, len(rif['vero']), len(rif['nullo']), len(f_add), len(f_val), len(f_fuori)), flush=True)
    return rif


# ---------------------------------------------------------------- E: l'esame

def insiemi(mondo):
    R = righe(punto_base(mondo))
    return OrderedDict((t, dict(n=N_LIBRI, spec=r['spec'], gru=N_GRU, gruppo=r['gruppo'], ruolo=r['descr'])) for t, r in R.items())


def fase_E(mondo, processi):
    ins = insiemi(mondo)
    nomi = [nome_libro(t, i) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    attiva_main(mondo, nomi)
    fatte = fatte_di(mondo)
    libri = [('libro40', t, i, d['spec'], seme_str('ia40esame' + SEMI, mondo, t, i)) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    print('== esame %s: %d righe, %d libri da scrivere' % (mondo, len(ins), len(libri)), flush=True)
    esegui(mondo, nomi, libri, processi, fatte)
    lavori = [('M', n) for n in nomi] + [('J32', n) for n in nomi] + [('NM', n) for n in nomi] + [('DV', n) for n in nomi]
    lavori += [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    if GRU:
        for t, d in ins.items():
            for i in range(1, min(d['gru'], d['n']) + 1):
                lavori += [('G', tp, nome_libro(t, i), 1) for tp in ('K', 'R')]
    lavori = sorted(lavori, key=lambda a: {'G': 0, 'D': 1, 'K': 2, 'KN': 2, 'J32': 3, 'M': 4, 'NM': 4, 'DV': 4}.get(a[0], 5))
    lavori = [('B35', t, [nome_libro(t, i) for i in range(1, d['n'] + 1)], seme_str('b35', mondo, t) % 1000) for t, d in ins.items()] + lavori
    print('== esame %s: %d lavori del banco' % (mondo, len(lavori)), flush=True)
    esegui(mondo, nomi, lavori, processi, fatte)
    return analisi_esame(mondo, ins, nomi)


def analisi_esame(mondo, ins, nomi):
    attiva_main(mondo, nomi)
    c = I7.contesto_A()
    rif = json.load(open(B.dir_mondo('riferimento.json'), encoding='utf-8'))
    nm_rif = json.load(open(cart40(mondo, 'nuove_misure.json'), encoding='utf-8'))
    corse = leggi_corse(percorso_corse(mondo))
    C = B.indice_corse(corse)
    nm = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('NM|') and not r.get('errore')}
    dv = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('DV|') and not r.get('errore')}
    dv_rif = json.load(open(cart40(mondo, 'diagnosi.json'), encoding='utf-8'))
    giudice_b = OrderedDict((r['lavoro'][4:], r) for r in corse if str(r.get('lavoro', '')).startswith('B35|') and not r.get('errore'))
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    n_pag = len(c['ids'])
    prof = OrderedDict((n, RM.valori_libro(n, C, pK, pKN, n_pag)) for n in nomi)
    corse_libro = {r['lavoro']: r for r in corse if str(r.get('lavoro', '')).startswith('libro|') and not r.get('errore')}
    return dict(rif=rif, nm_rif=nm_rif, nm=nm, dv=dv, dv_rif=dv_rif, prof=prof, giudice_b=giudice_b, ins=ins, nomi=nomi, corse_libro=corse_libro, n_pag=n_pag)


def verdetto(r):
    """Gli esiti scritti prima, per una riga: `sezione` entro 2 sigma, b <= 0,65, almeno 7 delle altre nove misure entro 2 sigma, guardia anti-copia a posto."""
    mis = r['misure_tenute_fuori']
    sez = mis.get('sezione')
    nove = [x['entro_2sigma'] for m, x in mis.items() if m != 'sezione']
    b = r['giudici_mai_visti']['b']['media']
    c1 = bool(sez is not None and abs(sez['z']) <= 2.0)
    c2 = bool(b is not None and b <= B_MAX)
    c3 = bool(sum(nove) >= NOVE_MIN)
    return OrderedDict([('sezione_z', sez['z'] if sez else None), ('sezione_entro_2sigma', c1), ('b', b), ('b_sotto_soglia', c2), ('nove_entro_2sigma', int(sum(nove))), ('nove_su', len(nove)),
                        ('nove_fuori', [m for m, x in mis.items() if m != 'sezione' and not x['entro_2sigma']]), ('nove_ok', c3), ('copia_ok', bool(r['copia_ok'])), ('buona', bool(c1 and c2 and c3 and r['copia_ok']))])


def fase_S(mondo, riassunti, A):
    os.makedirs(USCITA, exist_ok=True)
    ver = OrderedDict((t, verdetto(r)) for t, r in riassunti.items())
    buone = [t for t, v in ver.items() if v['buona']]
    rumore = OrderedDict()
    for base, rip in (('t100', 't100r'), ('s100k100', 's100k100r')):
        if base in ver and rip in ver:
            rumore[base] = OrderedDict([('delta_b', abs(ver[base]['b'] - ver[rip]['b']) if ver[base]['b'] is not None and ver[rip]['b'] is not None else None),
                                        ('delta_sezione_z', abs(ver[base]['sezione_z'] - ver[rip]['sezione_z']) if ver[base]['sezione_z'] is not None and ver[rip]['sezione_z'] is not None else None),
                                        ('delta_nove', abs(ver[base]['nove_entro_2sigma'] - ver[rip]['nove_entro_2sigma']))])
    esito = 'ESISTE una riga buona: %s' % ', '.join(buone) if buone else 'NESSUNA riga buona: la tavola e\' la curva del compromesso fra giudice b e `sezione` a dosi fisse'
    out = OrderedDict([('esperimento', NOME), ('mondo', mondo), ('esito', esito), ('righe_buone', buone), ('soglie', OrderedDict([('b_max', B_MAX), ('nove_min', NOVE_MIN), ('sezione', '|z| <= 2')])),
                       ('verdetti', ver), ('rumore', rumore), ('righe', riassunti)])
    suf = ('_' + ETICHETTA) if ETICHETTA else ''
    json.dump(out, open(os.path.join(USCITA, 'ia40_dosi%s.json' % suf), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ['# IA40 (ia40) — Tavola a dosi forzate%s' % (' (' + ETICHETTA + ')' if ETICHETTA else ''), '', 'Preregistrazione: `preregistrazioni/ia40.md`. Mondo `%s`. Solo numeri e aggregati. `sezione` non e\' piu\' tenuta fuori: e\' riportata a parte.' % mondo, '',
          '**Esito: %s.** Riga buona = `sezione` entro 2σ, b ≤ %.2f, almeno %d delle altre 9 misure entro 2σ, guardia anti-copia a posto.' % (esito, B_MAX, NOVE_MIN), '',
          '| riga | che cos\'e\' | N | KN | b | `sezione` z | altre 9 entro 2σ | fuori (delle 9) | div. sezioni bigr / parole | copia | buona |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for t, r in riassunti.items():
        g, v = r['giudici_mai_visti'], ver[t]
        md.append('| %s | %s | %s | %s | %s (%s) | %s | %s su %s | %s | %s / %s | %s | %s |' % (
            t, A['ins'][t]['ruolo'], mf(g['N']['media'], 3), mf(g['KN']['media'], 3), mf(g['b']['media'], 3), mf(g['b']['errore'], 3), mf(v['sezione_z'], 1), v['nove_entro_2sigma'], v['nove_su'],
            ', '.join(v['nove_fuori']) or '-', mf(r['diagnosi']['bigr']['valore'], 4), mf(r['diagnosi']['parole']['valore'], 4), 'ok' if v['copia_ok'] else 'SUPERATA', 'SI' if v['buona'] else 'no'))
    md += ['', 'Divergenza fra sezioni del testo vero: bigrammi %s, parole %s.' % (mf(A['dv_rif'].get('bigr'), 4), mf(A['dv_rif'].get('parole'), 4)), '']
    if rumore:
        md += ['**Rumore (righe ripetute con altri semi):** ' + '; '.join('%s: |Δb| %s, |Δz `sezione`| %s, |Δ altre nove| %s' % (k, mf(v['delta_b'], 3), mf(v['delta_sezione_z'], 1), v['delta_nove']) for k, v in rumore.items()) + '. Le differenze piu\' piccole di queste non si leggono.', '']
    md += ['Misure tenute fuori (z in sigma) per riga:', '']
    for t, r in riassunti.items():
        md.append('- `%s`: ' % t + ', '.join('%s %s' % (m, mf(x['z'], 1)) for m, x in r['misure_tenute_fuori'].items()))
    open(os.path.join(USCITA, 'ia40_dosi%s.md' % suf), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
    print('esito: %s' % esito, flush=True)


def main():
    import numpy  # noqa: F401
    import torch  # noqa: F401
    if len(MONDI40) != 1:
        raise SystemExit('ia40 gira su un mondo solo (un mondo per processo): MONDI40=2 (vero)')
    mondo = MONDI40[0]
    print('ia40: mondo %s, righe %s, libro (%s)' % (mondo, list(righe(punto_base(mondo))), 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    os.makedirs(CACHE40, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    processi = int(os.environ.get('PROCESSI', 3))
    fasi = os.environ.get('FASI', 'PES')
    if os.environ.get('RIPRENDI') != '1' and 'P' in fasi:
        azzera_corse(mondo)
    if 'P' in fasi:
        fase_P(mondo, processi)
    if 'E' in fasi:
        A = fase_E(mondo, processi)
        riass = OrderedDict((t, riassunto_insieme(mondo, A, t)) for t in A['ins'])
        json.dump(OrderedDict([('insiemi', riass)]), open(cart40(mondo, 'esame%s.json' % (('_' + ETICHETTA) if ETICHETTA else '')), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
        if 'S' in fasi:
            fase_S(mondo, riass, A)


if __name__ == '__main__':
    main()
