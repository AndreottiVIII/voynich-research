# -*- coding: utf-8 -*-
"""Esperimento IA33 (ia33): l'oracolo e l'IA piu' libera.

Domanda (seguito di IA32): con circa 150.000 segni d'addestramento, QUALUNQUE modello stimato resta distinguibile da giudici addestrati su libri interi? Se si', il traguardo
"indistinguibile" e' impossibile e ne serve uno raggiungibile; se no, il limite di IA32 era dell'imitatore. Tre parti:
  O  l'oracolo: nel mondo `markov2` di IA26 la catena di Markov di ordine 2 (la FAMIGLIA GIUSTA) stimata dai conteggi dei fogli d'addestramento di IA32, con Kneser-Ney (ufficiale)
     o con i conteggi grezzi (secondario); con 2 e 4 volte il testo; e il gemello (la vera catena, semi nuovi) come pavimento. Esame identico a quello di IA32.
  V  un baseline classico sul Voynich: n-grammi di glifi con Kneser-Ney (ordine scelto sulla validazione), senza rete, stimato sui fogli d'addestramento.
  L  l'IA piu' libera: lo stesso percorso di IA32 (modello pieno, CMA-ES, esame con giudici mai visti) con intervalli piu' larghi delle correzioni a conteggi, quadrigrammi,
     correzione a conteggi di parole, manopola delle parole nuove e ripresa dalla pagina. Controllo positivo: lo stesso ciclo sul mondo `markov2`.
Preregistrazione: preregistrazioni/ia33.md. Moduli di supporto (prefisso `oracolo_`): oracolo_catene (catene e Kneser-Ney), oracolo_scrittura (lo scrittore piu' libero), oracolo_misure
(obiettivo, libri dell'esame, lavori del banco), oracolo_giudice (giudice b libro per libro). Si importano, senza modificarli, i moduli di IA32 (`rifare_*`) e il banco di IA26 (`righello_*`).

Fasi (variabile FASI, predefinita PCES), per ogni mondo di MONDI33 (1 = markov2, il controllo positivo e l'oracolo; 2 = il libro vero):
  P  preparazione: riferimento del mondo, riferimento "naturale" della copia e modello pieno (copiati da dati/cache/ia32 se il protocollo coincide, altrimenti costruiti)
  C  il ciclo a prove ed errori (CMA-ES, 14 manopole) con rivalutazione dei finalisti
  E  l'esame: libri di tutti gli insiemi (INSIEMI33: L, O, V), giudici mai visti, misure tenute fuori, criteri
  S  sintesi -> risultati/ia33_oracolo.json e .md (solo numeri e aggregati)

    nohup bash strumenti/coda.sh ia33 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia33" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella fuori dal repo> CACHE33=<cartella fuori dal repo> python esperimenti/ia33_oracolo.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): MONDI33 (cifre: 1 markov2, 2 vero; predefinito 12), CACHE33 (cartella dei modelli e dei libri), LAMBDA33 (candidati per
generazione, 12), GEN33 (generazioni, 24), SIGMA33 (0,25), RIV33 (coppie di mezzi libri per rivalutare i finalisti, 3), N_ESAME33 (libri "migliore", 16), N_NEUTRO33 (4), N_IA32K33
(8), N_CASUALI33 (insiemi di manopole a caso, 4), N_CAS_LIBRI33 (4), N_ORACOLO33 (16), N_ORACOLO_PIU33 (8), N_GEM33 (16), N_NGR33 (16), N_GRU33 (libri per insieme con k90 e R_rel,
8), GRU33 (1), PERM33 (12), INSIEMI33 (lettere L, O, V; predefinito LOV), PARTENZA33 (ia32 o neutro), RIV_IA32 non c'e'. Quelle di IA32 (FUORI32, VAL32, NASCOSTO32, ..., KAPPA32,
ZCAP32, C_B32, AUC_NEUTRO_MIN32) e di IA26 valgono per il modello e per il banco; KAPPA33, KAPPA_P33, LAMBDA_B33, NU_PAG33 per lo scrittore piu' libero.
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

NOME = 'ia33_oracolo'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE33 = os.environ.get('CACHE33', os.path.join(USCITA, 'ia33_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia33'))
CACHE32_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia32')
CACHE26_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia26')
os.environ['CACHE26'] = os.path.join(CACHE33, 'banco')          # il banco di IA26 scrive qui, mai nella cache di IA26 ne' di IA32
os.environ.setdefault('CHUNK26', '500')                         # un solo gruppo di testi per i lavori K, KN e D
os.environ.setdefault('S_GRU_MONDO26', '6')
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import righello_giudici as RG  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_cma as CMA  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_giudice as RGB  # noqa: E402
import oracolo_catene as OC  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import oracolo_misure as OM  # noqa: E402
import oracolo_giudice as OG  # noqa: E402

MONDI_ELENCO = ['markov2', 'vero']
MONDI33 = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI33', '12') if x.isdigit() and 1 <= int(x) <= 2]
LAMBDA = int(os.environ.get('LAMBDA33', 12))
GEN = int(os.environ.get('GEN33', 24))
SIGMA0 = float(os.environ.get('SIGMA33', 0.25))
RIV = int(os.environ.get('RIV33', 3))
N_ESAME = int(os.environ.get('N_ESAME33', 16))
N_NEUTRO = int(os.environ.get('N_NEUTRO33', 4))
N_IA32K = int(os.environ.get('N_IA32K33', 8))
N_CASUALI = int(os.environ.get('N_CASUALI33', 4))
N_CAS_LIBRI = int(os.environ.get('N_CAS_LIBRI33', 4))
N_ORACOLO = int(os.environ.get('N_ORACOLO33', 16))
N_ORACOLO_PIU = int(os.environ.get('N_ORACOLO_PIU33', 8))
N_GEM = int(os.environ.get('N_GEM33', 16))
N_NGR = int(os.environ.get('N_NGR33', 16))
N_GRU = int(os.environ.get('N_GRU33', 8))
GRU = os.environ.get('GRU33', '1') == '1'
PERM = int(os.environ.get('PERM33', 12))
INSIEMI = os.environ.get('INSIEMI33', 'LOV')
PARTENZA = os.environ.get('PARTENZA33', 'ia32')
PIEGHE = I7.PIEGHE

# ---- criteri (scritti nella preregistrazione prima di ogni corsa sul Voynich)
AUC_MAX = 0.60                     # giudici mai visti: al massimo cosi' (e almeno 1 - AUC_MAX)
QUOTA_ENTRO_2S = 0.80              # almeno l'80% delle misure tenute fuori entro 2 sigma del vero
SIGMA_DA_SCALA = 1.0 / math.sqrt(2.0)
MARGINE_AUC = 0.05                 # "al livello dell'oracolo": AUC <= oracolo + max(2 errori, 0,05)
N_ERRORI = 2.0
V21_NOMI = ['V21:%d' % k for k in range(13, 23)]
GIUDICI3 = ('N', 'KN', 'b')


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def cart33(mondo, *p):
    return os.path.join(CACHE33, mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia33_corse_%s.jsonl' % mondo)


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


# ---------------------------------------------------------------- il pool

def avvia(mondo, nomi):
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    RM.prepara(mondo, cart33(mondo), nomi)


def lavoro33(args):
    if args[0] == 'addestra':
        t = time.time()
        try:
            ris = RD.addestra_pieno(cart33(RM._W['mondo'], 'modello'), messaggi=lambda s: print('[addestra %s] %s' % (RM._W['mondo'], s), flush=True))
            ris = OrderedDict((a, v) for a, v in ris.items() if not a.startswith('curva'))
            ris['lavoro'] = 'addestra|pieno'
            ris['secondi'] = round(time.time() - t, 1)
            return ris
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'addestra|pieno'), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = OM.lavoro_banco33(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


def ident(a):
    if a[0] == 'libro33':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'valuta':
        return 'ciclo|%d|%d' % (a[1], a[2])
    return '|'.join(str(x) for x in a)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia33_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro33, da_fare), 1):
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


# ---------------------------------------------------------------- P: preparazione

_ATTIVO = {}


def attiva_main(mondo, nomi=()):
    """Attiva il mondo nel processo principale UNA volta sola. `righello_testi.attiva_mondo` costruisce il mondo a partire dal libro che trova in `ia07._C`: richiamata, cambia il testo
    (un mondo di seconda generazione) e per il mondo `vero` non fa niente e lascia il testo del mondo precedente. In IA32 il processo principale lo faceva (fase P, C, E, analisi, e poi
    `vero` dopo `markov2`): il giudice b e il riferimento "naturale" della copia vennero calcolati su quel testo sbagliato. Qui: un solo mondo per processo (gli altri mondi in un processo figlio)
    e le richiamate successive cambiano solo l'elenco dei testi."""
    if _ATTIVO.get('mondo') == mondo:
        B._S['nomi'] = [n for n in nomi if n != 'vero']
        return B._S
    if _ATTIVO:
        raise RuntimeError('un solo mondo per processo: %s e poi %s' % (_ATTIVO['mondo'], mondo))
    _ATTIVO['mondo'] = mondo
    return B.imposta_mondo(mondo, list(nomi))


def copia_da_ia32(mondo):
    """Dalla cache di IA32 (solo corsa vera): riferimento e modelli di misura del banco, riferimento "naturale" e modello pieno, se il protocollo coincide."""
    if SOLO_CONTROLLI:
        return False
    ok = False
    o_banco = os.path.join(CACHE32_ORIG, 'banco', mondo)
    d_banco = os.path.join(CACHE33, 'banco', mondo)
    if os.path.exists(os.path.join(o_banco, 'riferimento.json')) and not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        os.makedirs(os.path.join(d_banco, 'modelli_misura'), exist_ok=True)
        shutil.copy(os.path.join(o_banco, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
        for f in os.listdir(os.path.join(o_banco, 'modelli_misura')):
            if not os.path.exists(os.path.join(d_banco, 'modelli_misura', f)):
                shutil.copy(os.path.join(o_banco, 'modelli_misura', f), os.path.join(d_banco, 'modelli_misura', f))
        print('riferimento e modelli di misura di %s copiati da IA32' % mondo, flush=True)
        ok = True
    return ok                      # `naturale.json` di IA32 NON si copia: era calcolato sul testo sbagliato (vedi `attiva_main`); si rifa qui


def copia_modello_ia32(mondo):
    """Il modello pieno di IA32, se i fogli d'addestramento coincidono (stesso protocollo): True se copiato (o gia' presente)."""
    dest = cart33(mondo, 'modello')
    if os.path.exists(os.path.join(dest, 'pieno.pt')):
        return True
    orig = os.path.join(CACHE32_ORIG, mondo, 'modello')
    if SOLO_CONTROLLI or not os.path.exists(os.path.join(orig, 'pieno.pt')):
        return False
    import torch
    d = torch.load(os.path.join(orig, 'pieno.pt'), weights_only=False)
    f_add, f_val, f_fuori = RD.divisione_fogli()
    if d['f_add'] != f_add or d['f_val'] != f_val or d['f_fuori'] != f_fuori:
        print('il modello di IA32 ha una divisione dei fogli diversa: non si riusa', flush=True)
        return False
    os.makedirs(dest, exist_ok=True)
    for f in ('pieno.pt', 'pieno.json'):
        shutil.copy(os.path.join(orig, f), os.path.join(dest, f))
    print('modello pieno di %s copiato da IA32 (stessi fogli)' % mondo, flush=True)
    return True


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
    """Il riferimento del mondo: copiato da IA32 (corsa vera) o costruito con i lavori del banco (prove)."""
    dest = os.path.join(CACHE33, 'banco', mondo)
    os.makedirs(os.path.join(dest, 'modelli_misura'), exist_ok=True)
    rif_p = os.path.join(dest, 'riferimento.json')
    copia_da_ia32(mondo)
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


def fase_P(mondo, processi, addestra=True):
    os.makedirs(cart33(mondo), exist_ok=True)
    rif = costruisci_riferimento(mondo, processi)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    nat_p = cart33(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('mondo %s: riferimento con %d misure e %d giudici; fogli addestramento/validazione/fuori %d/%d/%d' % (mondo, len(rif['vero']), len(rif['nullo']),
                                                                                                    len(f_add), len(f_val), len(f_fuori)), flush=True)
    if addestra and not copia_modello_ia32(mondo):
        esegui(mondo, [], [('addestra',)], 1, fatte_di(mondo))
    return rif


# ---------------------------------------------------------------- C: il ciclo

def valori_ia32(mondo):
    """Le manopole scelte da IA32 per il mondo (dizionario) o None."""
    p = os.path.join(CACHE32_ORIG, mondo, 'ciclo_esito.json')
    if SOLO_CONTROLLI or not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding='utf-8'))['manopole_migliori']
    except (OSError, ValueError, KeyError):
        return None


def cubo_partenza(mondo):
    """Il cubo di partenza del ciclo: le manopole scelte da IA32 (`PARTENZA33=ia32`, se ci sono) con le manopole nuove a valore neutro; altrimenti il neutro."""
    v = valori_ia32(mondo) if PARTENZA == 'ia32' else None
    return OS.neutro_cubo33() if v is None else OS.cubo_da_valori(v)


def meta_fogli(mondo, gen, rep=0):
    ff = sorted({x['foglio'] for x in I7.libro_vero()})
    import random
    rnd = random.Random(seme_str('ia33mezzi', mondo, gen, rep))
    rnd.shuffle(ff)
    h = len(ff) // 2
    return sorted(ff[:h]), sorted(ff[h:])


def media_valutazioni(rs):
    ok = [r for r in rs if not r.get('errore')]
    if not ok:
        return None
    return float(np.mean([r['obiettivo'] for r in ok]))


def fase_C(mondo, processi):
    attiva_main(mondo, [])
    st_p = cart33(mondo, 'ciclo.json')
    x0 = cubo_partenza(mondo)
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(st_p):
        stato = json.load(open(st_p, encoding='utf-8'))
        cma = CMA.CMA.da_stato(stato['cma'])
        storia = stato['storia']
    else:
        cma = CMA.CMA(x0, SIGMA0, LAMBDA, seme=seme_str('ia33cma', mondo))
        storia = []
    fatte = fatte_di(mondo)
    while cma.gen < GEN:
        g = cma.gen
        xs, _ = cma.ask()
        mA, mB = meta_fogli(mondo, g)
        lavori = []
        for i, u in enumerate(xs):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', g * 10 + h, i, list(map(float, u)), seme_str('ia33ciclo', mondo, g, i, h), fogli))
        esegui(mondo, [], lavori, processi, fatte)
        tutti = [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('ciclo|') and not c.get('errore')]
        vals = []
        for i in range(len(xs)):
            rs = [c for c in tutti if c['gen'] in (g * 10, g * 10 + 1) and c['i'] == i]
            v = media_valutazioni(rs) if len(rs) == 2 else None
            vals.append(v if v is not None else 99.0)
        cma.tell(xs, vals)
        storia.append(OrderedDict([('gen', g), ('valori', vals), ('minimo', float(min(vals))), ('media', float(np.mean(vals))), ('sigma', cma.sigma),
                                   ('punti', [list(map(float, u)) for u in xs])]))
        json.dump(dict(cma=cma.stato(), storia=storia), open(st_p, 'w', encoding='utf-8', newline='\n'), default=float)
        print('generazione %d: minimo %.3f, media %.3f, sigma %.3f' % (g, min(vals), float(np.mean(vals)), cma.sigma), flush=True)
    cand = OrderedDict()
    cand['neutro'] = OS.neutro_cubo33()
    if valori_ia32(mondo) is not None:
        cand['ia32'] = x0
    cand['media_finale'] = cma.mean
    best_v, best_u = 1e9, None
    for h in storia:
        for u, v in zip(h['punti'], h['valori']):
            if v < best_v:
                best_v, best_u = v, np.array(u)
    cand['migliore_di_sempre'] = best_u
    cand['migliore_ultima'] = np.array(storia[-1]['punti'][int(np.argmin(storia[-1]['valori']))])
    lavori = []
    for r in range(RIV):
        mA, mB = meta_fogli(mondo, 1000 + r, r)
        for ci, (nome, u) in enumerate(cand.items()):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', 9000 + r * 10 + h, ci, list(map(float, np.clip(u, 0, 1))), seme_str('ia33riv', mondo, r, ci, h), fogli))
    esegui(mondo, [], lavori, processi, fatte)
    tutti = [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('ciclo|9') and not c.get('errore')]
    fin = OrderedDict()
    for ci, nome in enumerate(cand):
        rs = [c for c in tutti if c['i'] == ci and c['gen'] >= 9000]
        fin[nome] = OrderedDict([('obiettivo', media_valutazioni(rs)), ('n', len(rs)), ('u', list(map(float, np.clip(cand[nome], 0, 1)))),
                                 ('manopole', OS.da_cubo33(np.clip(cand[nome], 0, 1))),
                                 ('z', OrderedDict((m, float(np.mean([c['z'][m] for c in rs if m in c['z']]))) for m in OM.OBIETTIVO33) if rs else None),
                                 ('copia_violazioni', OrderedDict((k, float(np.mean([c['copia_violazioni'].get(k, 0.0) for c in rs]))) for k in RM.SOGLIE_COPIA) if rs else None)])
    scelto = min((n for n in fin if fin[n]['obiettivo'] is not None), key=lambda n: fin[n]['obiettivo'])
    ris = OrderedDict([('storia', storia), ('finalisti', fin), ('scelto', scelto), ('u_migliore', fin[scelto]['u']), ('manopole_migliori', fin[scelto]['manopole']),
                       ('u_partenza', list(map(float, x0))), ('partenza', 'ia32' if valori_ia32(mondo) is not None else 'neutro')])
    json.dump(ris, open(cart33(mondo, 'ciclo_esito.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('ciclo finito: scelto %s, obiettivo %.3f (neutro %.3f)' % (scelto, fin[scelto]['obiettivo'], fin['neutro']['obiettivo']), flush=True)
    return ris


# ---------------------------------------------------------------- E: l'esame

def insiemi_esame(mondo, ris_ciclo):
    """I libri dell'esame: nome -> dict(n, spec, gru (quanti libri con k90 e R_rel), gruppo, ruolo)."""
    out = OrderedDict()
    neutro = OS.neutro_cubo33()
    if 'L' in INSIEMI and ris_ciclo is not None:
        out['best'] = dict(n=N_ESAME, spec=['L', list(map(float, ris_ciclo['u_migliore']))], gru=N_GRU, gruppo='L', ruolo='L: migliore del ciclo')
        out['neu'] = dict(n=N_NEUTRO, spec=['L', list(map(float, neutro))], gru=N_NEUTRO, gruppo='L', ruolo='manopole neutre (la rete a temperatura 1)')
        v = valori_ia32(mondo)
        if v is not None and N_IA32K > 0:
            out['ia32k'] = dict(n=N_IA32K, spec=['L', list(map(float, OS.cubo_da_valori(v)))], gru=min(N_GRU, 4), gruppo='L', ruolo='le manopole scelte da IA32 (nello scrittore nuovo)')
        rnd = np.random.default_rng(seme_str('ia33casuali', mondo))
        for c in range(1, N_CASUALI + 1):
            u = np.clip(neutro + rnd.uniform(-0.45, 0.45, OS.DIM33), 0.0, 1.0)
            out['cas%d' % c] = dict(n=N_CAS_LIBRI, spec=['L', list(map(float, u))], gru=0, gruppo='L', ruolo='manopole a caso (controllo negativo)')
    if mondo == 'markov2' and 'O' in INSIEMI:
        out['orkn'] = dict(n=N_ORACOLO, spec=['KN', 1], gru=N_GRU, gruppo='O', ruolo="l'oracolo stimato (Kneser-Ney, ufficiale)")
        out['ormle'] = dict(n=N_ORACOLO_PIU, spec=['MLE', 1], gru=0, gruppo='O', ruolo="l'oracolo con i conteggi grezzi (secondario)")
        out['orkn2'] = dict(n=N_ORACOLO_PIU, spec=['KN', 2], gru=0, gruppo='O', ruolo="l'oracolo con il doppio del testo")
        out['orkn4'] = dict(n=N_ORACOLO_PIU, spec=['KN', 4], gru=0, gruppo='O', ruolo="l'oracolo con il quadruplo del testo")
        out['gem'] = dict(n=N_GEM, spec=['GEM'], gru=N_GRU, gruppo='O', ruolo='il gemello (la vera catena, semi nuovi): il pavimento')
    if mondo == 'vero' and 'V' in INSIEMI:
        out['ngr'] = dict(n=N_NGR, spec=['NGR'], gru=N_GRU, gruppo='V', ruolo='il baseline classico (n-grammi di glifi con Kneser-Ney)')
    return out


def nome_libro(tipo, i):
    return 'tar:%s:%d' % (tipo, i)


def v21_disponibili():
    out = []
    if SOLO_CONTROLLI:
        return out
    for n in V21_NOMI:
        try:
            if RT.rows_di(n) is not None:
                out.append(n)
        except Exception:                                                 # noqa: BLE001
            pass
    return out


def fase_E(mondo, processi):
    p_ciclo = cart33(mondo, 'ciclo_esito.json')
    ris_ciclo = json.load(open(p_ciclo, encoding='utf-8')) if os.path.exists(p_ciclo) else None
    ins = insiemi_esame(mondo, ris_ciclo)
    attiva_main(mondo, [])
    v21 = v21_disponibili() if mondo == 'vero' and 'L' in INSIEMI else []
    nomi = [nome_libro(t, i) for t, d in ins.items() for i in range(1, d['n'] + 1)] + v21
    attiva_main(mondo, nomi)
    fatte = fatte_di(mondo)
    libri = [('libro33', t, i, d['spec'], seme_str('ia33esame', mondo, t, i)) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    print('== esame %s: %d libri da scrivere' % (mondo, len(libri)), flush=True)
    esegui(mondo, nomi, libri, processi, fatte)
    lavori = [('M', n) for n in nomi] + [('J32', n) for n in nomi]
    lavori += [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    if GRU:
        for t, d in ins.items():
            for i in range(1, min(d['gru'], d['n']) + 1):
                lavori += [('G', tp, nome_libro(t, i), 1) for tp in ('K', 'R')]
        for n in v21[:4]:
            lavori += [('G', tp, n, 1) for tp in ('K', 'R')]
    lavori = sorted(lavori, key=lambda a: {'G': 0, 'D': 1, 'K': 2, 'KN': 2, 'J32': 3, 'M': 4}.get(a[0], 5))
    print('== esame %s: %d lavori del banco' % (mondo, len(lavori)), flush=True)
    esegui(mondo, nomi, lavori, processi, fatte)
    return analisi_esame(mondo, ins, nomi, v21)


def libri_rows(nomi):
    return [B.rows_testo(n) for n in nomi]


def analisi_esame(mondo, ins, nomi, v21):
    attiva_main(mondo, nomi)
    c = I7.contesto_A()
    rif = json.load(open(B.dir_mondo('riferimento.json'), encoding='utf-8'))
    C = B.indice_corse(leggi_corse(percorso_corse(mondo)))
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    n_pag = len(c['ids'])
    prof = OrderedDict((n, RM.valori_libro(n, C, pK, pKN, n_pag)) for n in nomi)
    S_f = RD.divisione_fogli()[2]
    fuori = set(S_f)
    pagine = [p for p in c['ids'] if I7.foglio_di(p) in fuori]
    voc = RG.vocabolario_N(c['vere'])
    giudice_b = OrderedDict()
    for t, d in ins.items():
        ls = [nome_libro(t, i) for i in range(1, d['n'] + 1)]
        giudice_b[t] = OG.esame_b_libri(c['vere'], libri_rows(ls), pagine, I7.foglio_di, voc, n_train=len(ls) // 2, permutazioni=PERM, seme=seme_str('b', mondo, t) % 1000)
    if v21:
        giudice_b['v21'] = OG.esame_b_libri(c['vere'], libri_rows(v21), pagine, I7.foglio_di, voc, n_train=len(v21) // 2, permutazioni=PERM, seme=seme_str('b', mondo, 'v21') % 1000)
    corse_libro = {r['lavoro']: r for r in leggi_corse(percorso_corse(mondo)) if str(r.get('lavoro', '')).startswith('libro|') and not r.get('errore')}
    return dict(rif=rif, prof=prof, giudice_b=giudice_b, ins=ins, nomi=nomi, v21=v21, corse_libro=corse_libro, n_pag=n_pag)


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def riassunto_insieme(mondo, A, tipo):
    """Per un insieme di libri: AUC dei tre giudici mai visti (media, deviazione standard fra libri, errore), giudici di allenamento, misure tenute fuori, copia."""
    rif, prof = A['rif'], A['prof']
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
    out['giudici_di_allenamento'] = OrderedDict((j, media([prof[l].get(j) for l in ls])) for j in OM.OBI_GIUDICI33)
    mis = OrderedDict()
    for m in OM.FUORI_MISURE33:
        if m not in rif['vero'] or rif['scala'].get(m) is None:
            continue
        val = media([prof[l].get(m) for l in ls])
        s_ = rif['scala'][m] * SIGMA_DA_SCALA
        if val is None or not s_:
            continue
        z = (val - rif['vero'][m]) / s_
        mis[m] = OrderedDict([('valore', val), ('vero', rif['vero'][m]), ('sigma', s_), ('z', z), ('entro_2sigma', bool(abs(z) <= 2.0))])
    out['misure_tenute_fuori'] = mis
    out['quota_entro_2sigma'] = float(np.mean([x['entro_2sigma'] for x in mis.values()])) if mis else None
    out['misure_fuori'] = [m for m, x in mis.items() if not x['entro_2sigma']]
    ali = OrderedDict()
    for m in OM.OBI_MISURE33:
        if m in rif['vero'] and rif['scala'].get(m):
            val = media([prof[l].get(m) for l in ls])
            if val is not None:
                ali[m] = OrderedDict([('valore', val), ('vero', rif['vero'][m]), ('z_sigma', (val - rif['vero'][m]) / (rif['scala'][m] * SIGMA_DA_SCALA))])
    out['misure_di_allenamento'] = ali
    cop = A['corse_libro']
    viol = [max(cop['libro|%s|%d' % (tipo, i)]['copia_violazioni'].values() or [0.0]) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]
    out['copia_ok'] = bool(viol) and max(viol) <= 0.0
    out['copia_violazione_max'] = max(viol) if viol else None
    out['copia_quote'] = OrderedDict((k, media([cop['libro|%s|%d' % (tipo, i)]['copia'].get(k) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]))
                                     for k in RM.SOGLIE_COPIA)
    return out


def riassunto_v21(A):
    if not A['v21']:
        return None
    prof = A['prof']
    jud = OrderedDict()
    for j in ('N', 'KN'):
        vs = [prof[n].get(j) for n in A['v21'] if prof[n].get(j) is not None]
        nu = (A['rif']['nullo'].get(j) or {}).get('sd') or 0.0
        s = sd(vs) or 0.0
        jud[j] = OrderedDict([('media', media(vs)), ('sd_libri', s), ('n', len(vs)), ('errore', math.sqrt(s * s / max(len(vs), 1) + nu * nu))])
    b = A['giudice_b'].get('v21') or {}
    nb = len(b.get('per_libro') or [])
    s = b.get('sd_libri') or 0.0
    jud['b'] = OrderedDict([('media', b.get('auc')), ('sd_libri', s), ('n', nb), ('errore', math.sqrt(s * s / max(nb, 1) + (b.get('nullo_sd') or 0.0) ** 2))])
    return jud


def diff_err(a, b):
    return math.sqrt(a['errore'] ** 2 + b['errore'] ** 2)


def lettura_O(R):
    """La lettura della parte O (mondo markov2): `R` = riassunti per insieme. -> dict."""
    if 'orkn' not in R:
        return None
    o, g = R['orkn']['giudici_mai_visti'], R['gem']['giudici_mai_visti'] if 'gem' in R else None
    out = OrderedDict()
    def fuori(x, e=0.0):
        """Fuori dalla fascia 0,40-0,60 (con `e`: di piu' di `e` oltre il bordo)."""
        return bool(x is not None and (x - e > AUC_MAX or x + e < 1 - AUC_MAX))
    out['oracolo'] = OrderedDict((j, OrderedDict([('media', o[j]['media']), ('errore', o[j]['errore']), ('sopra_0_60', bool(o[j]['media'] is not None and o[j]['media'] > AUC_MAX)),
                                                  ('sotto_0_40', bool(o[j]['media'] is not None and o[j]['media'] < 1 - AUC_MAX)), ('riconosciuto', fuori(o[j]['media'])),
                                                  ('riconosciuto_netto', fuori(o[j]['media'], N_ERRORI * o[j]['errore']))])) for j in GIUDICI3)
    out['gemello_ok'] = bool(g is not None and all(g[j]['media'] is not None and (1 - AUC_MAX) <= g[j]['media'] <= AUC_MAX for j in GIUDICI3)) if g else None
    b_neu = (R.get('neu') or {}).get('giudici_mai_visti', {}).get('b', {}).get('media')
    out['giudice_b_valido'] = bool(b_neu is not None and b_neu >= RGB.AUC_NEUTRO_MIN) if b_neu is not None else None
    sopra = [j for j in GIUDICI3 if out['oracolo'][j]['riconosciuto']]
    if out['gemello_ok'] is False or out['giudice_b_valido'] is False:
        out['verdetto'] = 'non valido'
    elif sopra:
        out['verdetto'] = 'irraggiungibile'
    else:
        out['verdetto'] = 'raggiungibile'
    out['giudici_oltre_0_60'] = sopra
    out['giudici_sopra_0_60_lettera'] = [j for j in GIUDICI3 if out['oracolo'][j]['sopra_0_60']]
    # andamento con il testo
    tr = OrderedDict()
    for nome, mult in (('orkn', 1), ('orkn2', 2), ('orkn4', 4)):
        if nome in R:
            tr[mult] = OrderedDict((j, R[nome]['giudici_mai_visti'][j]['media']) for j in GIUDICI3)
    out['andamento_con_il_testo'] = tr
    stime = OrderedDict()
    for j in GIUDICI3:
        xs = [(m, tr[m][j] - 0.5) for m in tr if tr[m][j] is not None and tr[m][j] > 0.5]
        if len(xs) >= 2 and all(xs[i][1] > xs[i + 1][1] for i in range(len(xs) - 1)):
            lx = np.log([m for m, _ in xs])
            ly = np.log([y for _, y in xs])
            a, b0 = np.polyfit(lx, ly, 1)
            if a < 0:
                stime[j] = OrderedDict([('esponente', float(a)), ('volte_testo_per_0_60', float(math.exp((math.log(0.10) - b0) / a))), ('volte_testo_per_0_55', float(math.exp((math.log(0.05) - b0) / a)))])
    out['stima_testo_necessario_descrittiva'] = stime
    if 'ormle' in R:
        out['oracolo_conteggi_grezzi'] = OrderedDict((j, R['ormle']['giudici_mai_visti'][j]['media']) for j in GIUDICI3)
    return out


def esito_L(mondo, R, v21, O):
    """L'esito della parte L per il mondo: riuscito assoluto, al livello dell'oracolo, batte il riferimento (v21 o le manopole di IA32), non riuscito, non valido."""
    if 'best' not in R:
        return None
    best, neu = R['best'], R.get('neu')
    jb = best['giudici_mai_visti']
    b_neu = neu['giudici_mai_visti']['b']['media'] if neu else None
    valido = bool(b_neu is not None and b_neu >= RGB.AUC_NEUTRO_MIN)
    quota_ok = bool(best['quota_entro_2sigma'] is not None and best['quota_entro_2sigma'] >= QUOTA_ENTRO_2S)
    out = OrderedDict([('giudice_b_valido', valido), ('giudice_b_neutro', b_neu), ('giudici_mai_visti', jb), ('quota_entro_2sigma', best['quota_entro_2sigma']),
                       ('misure_fuori', best['misure_fuori']), ('copia_ok', best['copia_ok'])])
    # al livello dell'oracolo
    livello = None
    if O is not None and O['verdetto'] == 'irraggiungibile':
        det = OrderedDict()
        for j in GIUDICI3:
            e = math.sqrt(jb[j]['errore'] ** 2 + O['oracolo'][j]['errore'] ** 2)
            lim = abs(O['oracolo'][j]['media'] - 0.5) + max(N_ERRORI * e, MARGINE_AUC)                 # distanza da 0,5 (un AUC molto sotto 0,5 e' una differenza come uno sopra)
            det[j] = OrderedDict([('AUC', jb[j]['media']), ('distanza_da_0_5', abs(jb[j]['media'] - 0.5) if jb[j]['media'] is not None else None), ('limite_distanza', lim),
                                  ('dentro', bool(jb[j]['media'] is not None and abs(jb[j]['media'] - 0.5) <= lim))])
        livello = OrderedDict([('dettaglio', det), ('giudici_dentro', bool(all(x['dentro'] for x in det.values())))])
    out['al_livello_dell_oracolo'] = livello
    # confronto con il riferimento
    if v21 is not None:
        base, nome = v21, 'v21'
    elif R.get('ia32k'):
        base, nome = R['ia32k']['giudici_mai_visti'], 'manopole di IA32'
    else:
        base, nome = None, None
    batte = None
    if base is not None:
        det = OrderedDict()
        for j in GIUDICI3:
            e = math.sqrt(jb[j]['errore'] ** 2 + base[j]['errore'] ** 2)
            piu_vicino = bool(jb[j]['media'] is not None and base[j]['media'] is not None and abs(jb[j]['media'] - 0.5) < abs(base[j]['media'] - 0.5))
            netto = bool(piu_vicino and abs(base[j]['media'] - 0.5) - abs(jb[j]['media'] - 0.5) >= N_ERRORI * e)
            det[j] = OrderedDict([('AUC', jb[j]['media']), ('riferimento', base[j]['media']), ('errore_differenza', e), ('piu_vicino', piu_vicino), ('a_2_errori', netto)])
        batte = OrderedDict([('riferimento', nome), ('dettaglio', det), ('piu_vicino_su_tutti', bool(all(x['piu_vicino'] for x in det.values()))),
                             ('batte_a_2_errori', bool(all(x['a_2_errori'] for x in det.values())))])
    out['batte_il_riferimento'] = batte
    rimaste = [j for j in GIUDICI3 if not (jb[j]['media'] is not None and (1 - AUC_MAX) <= jb[j]['media'] <= AUC_MAX)]
    if not valido:
        e = 'non valido'
    elif best['giudici_ok'] and quota_ok and best['copia_ok']:
        e = 'riuscito assoluto'
    elif livello and livello['giudici_dentro'] and quota_ok and best['copia_ok']:
        e = "al livello dell'oracolo"
    elif batte and batte['batte_a_2_errori'] and best['copia_ok']:
        e = 'batte il %s' % batte['riferimento']
    else:
        e = 'non riuscito'
    out['esito'] = e
    out['resta_fuori'] = OrderedDict([('giudici_oltre_0_60', rimaste), ('misure_fuori_2sigma', best['misure_fuori']), ('copia_superata', not best['copia_ok'])])
    # controllo negativo: nessuno degli insiemi a caso supera l'esame (criteri assoluti)
    cas = OrderedDict()
    for t, r in R.items():
        if t.startswith('cas'):
            sup = bool(r['giudici_ok'] and r['quota_entro_2sigma'] is not None and r['quota_entro_2sigma'] >= QUOTA_ENTRO_2S and r['copia_ok'])
            cas[t] = OrderedDict([('giudici', OrderedDict((j, r['giudici_mai_visti'][j]['media']) for j in GIUDICI3)), ('quota_entro_2sigma', r['quota_entro_2sigma']), ('supera', sup)])
    out['casuali'] = cas
    out['controllo_negativo_riuscito'] = bool(cas) and not any(x['supera'] for x in cas.values())
    return out


def lettura_V(R, ia32):
    """La parte V: l'AUC del baseline classico accanto al v21, al neutro e al migliore di IA32 (numeri di IA32 dal suo file di risultati, se c'e')."""
    if 'ngr' not in R:
        return None
    out = OrderedDict([('baseline', OrderedDict((j, R['ngr']['giudici_mai_visti'][j]['media']) for j in GIUDICI3))])
    if ia32:
        e = ia32.get('esame') or {}
        mig = (e.get('migliore') or {}).get('giudici_mai_visti') or {}
        neu = (e.get('neutro') or {}).get('giudici_mai_visti') or {}
        out['ia32_migliore'] = OrderedDict((j, mig.get(j)) for j in GIUDICI3)
        out['ia32_neutro'] = OrderedDict((j, neu.get(j)) for j in GIUDICI3)
        out['v21'] = OrderedDict((j, (e.get('base') or {}).get(j)) for j in GIUDICI3)
        q = OrderedDict()
        for j in GIUDICI3:
            a, b_, c = neu.get(j), out['baseline'][j], mig.get(j)
            if None not in (a, b_, c) and a - c > 1e-9:
                q[j] = float((a - b_) / (a - c))
        out['quota_del_progresso_di_ia32_fatta_dai_soli_conteggi'] = q
    return out


def carica_ia32():
    p = os.path.join(QUI, '..', 'risultati', 'ia32_rifare_il_voynich.json')
    if SOLO_CONTROLLI or not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding='utf-8'))['mondi']
    except (OSError, ValueError, KeyError):
        return {}


# ---------------------------------------------------------------- S: sintesi

def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def fase_S(mondi, sintesi):
    os.makedirs(USCITA, exist_ok=True)
    ia32 = carica_ia32()
    ins_m2 = (sintesi.get('markov2') or {}).get('insiemi')
    if not ins_m2 and os.path.exists(cart33('markov2', 'esame.json')):          # corsa solo sul mondo vero: l'oracolo viene dal mondo markov2 gia' fatto
        ins_m2 = json.load(open(cart33('markov2', 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict).get('insiemi')
    O = lettura_O(ins_m2) if ins_m2 else None
    for mondo, s in sintesi.items():
        R = s.get('insiemi')
        if not R:
            continue
        s['esito_L'] = esito_L(mondo, R, s.get('v21'), O)
        if mondo == 'vero':
            s['lettura_V'] = lettura_V(R, ia32.get('vero'))
    out = OrderedDict([('esperimento', NOME), ('lettura_O', O), ('mondi', sintesi)])
    json.dump(out, open(os.path.join(USCITA, 'ia33_oracolo.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ["# IA33 (ia33) — L'oracolo e l'IA piu' libera", '', 'Preregistrazione: `preregistrazioni/ia33.md`. Solo numeri e aggregati.', '']
    if O:
        md += ["## Parte O — l'oracolo (mondo `markov2`)", '', '**Verdetto: %s** (pavimento valido: %s; giudice b valido: %s). Giudici che lo riconoscono (fuori 0,40-0,60): %s; oltre 0,60 alla lettera: %s.' % (
            O['verdetto'], O['gemello_ok'], O['giudice_b_valido'], ', '.join(O['giudici_oltre_0_60']) or 'nessuno', ', '.join(O['giudici_sopra_0_60_lettera']) or 'nessuno'), '']
        md += ['| giudice | oracolo ufficiale (KN) | errore | riconosciuto (fuori 0,40-0,60) | netto (2 errori) | oltre 0,60 |', '|---|---|---|---|---|---|']
        for j in GIUDICI3:
            x = O['oracolo'][j]
            md.append('| %s | %s | %s | %s | %s | %s |' % (j, mf(x['media']), mf(x['errore']), 'si' if x['riconosciuto'] else 'no', 'si' if x['riconosciuto_netto'] else 'no', 'si' if x['sopra_0_60'] else 'no'))
        md += ['', '| testo (volte) | ' + ' | '.join(GIUDICI3) + ' |', '|---|---|---|---|']
        for m, v in O['andamento_con_il_testo'].items():
            md.append('| %s | %s |' % (m, ' | '.join(mf(v[j]) for j in GIUDICI3)))
        if O.get('stima_testo_necessario_descrittiva'):
            md += ['', 'Stima descrittiva (legge di potenza sui punti sopra, da prendere con cautela): ' + '; '.join(
                '%s: %.1f volte il testo per 0,60, %.1f per 0,55' % (j, x['volte_testo_per_0_60'], x['volte_testo_per_0_55']) for j, x in O['stima_testo_necessario_descrittiva'].items())]
        md.append('')
    for mondo, s in sintesi.items():
        md += ['## Mondo `%s`' % mondo, '']
        if s.get('ciclo'):
            c = s['ciclo']
            md += ['Ciclo: %d generazioni, partenza %s, obiettivo del migliore %s contro %s delle manopole neutre (scelto: %s).' % (
                len(c['storia']), c.get('partenza'), mf(c['finalisti'][c['scelto']]['obiettivo']), mf(c['finalisti']['neutro']['obiettivo']), c['scelto']), '']
            md += ['| generazione | obiettivo minimo | media | passo CMA-ES |', '|---|---|---|---|']
            for h in c['storia']:
                md.append('| %d | %s | %s | %s |' % (h['gen'], mf(h['minimo']), mf(h['media']), mf(h['sigma'], 3)))
            md += ['', '| finalista | obiettivo rivalutato | ' + ' | '.join(OM.OBIETTIVO33) + ' |', '|---|---|' + '---|' * len(OM.OBIETTIVO33)]
            for n, x in c['finalisti'].items():
                md.append('| %s | %s | %s |' % (n, mf(x['obiettivo']), ' | '.join(mf((x['z'] or {}).get(m), 1) for m in OM.OBIETTIVO33)))
            md += ['', '| manopola | valore scelto | neutro |', '|---|---|---|']
            for k, v in c['manopole_migliori'].items():
                md.append('| %s | %s | %s |' % (k, mf(v), mf(OS.NEUTRO33[k])))
            md.append('')
        R = s.get('insiemi')
        if R:
            md += ['| insieme | libri | ' + ' | '.join(GIUDICI3) + ' | quota entro 2 sigma | misure fuori | copia |', '|---|---|---|---|---|---|---|---|']
            for t, r in R.items():
                md.append('| %s | %d | %s | %s | %s | %s |' % (t, r['n'], ' | '.join('%s (%s)' % (mf(r['giudici_mai_visti'][j]['media']), mf(r['giudici_mai_visti'][j]['errore'], 3)) for j in GIUDICI3),
                                                         mf(r['quota_entro_2sigma'], 2), ', '.join(r['misure_fuori']) or '-', 'ok' if r['copia_ok'] else 'superata'))
            if s.get('v21'):
                md.append('| v21 | %d | %s | | | | |' % (len(s['v21_libri']) if s.get('v21_libri') else 0, ' | '.join('%s (%s)' % (mf(s['v21'][j]['media']), mf(s['v21'][j]['errore'], 3)) for j in GIUDICI3)))
            md.append('')
        e = s.get('esito_L')
        if e:
            md += ["**Esito L: %s** (giudice b valido: %s; controllo negativo riuscito: %s)." % (e['esito'], e['giudice_b_valido'], e['controllo_negativo_riuscito']), '']
            if e['esito'] in ('non riuscito', 'non valido'):
                md += ['Resta fuori: giudici oltre 0,60: %s; misure fuori 2 sigma: %s; copia superata: %s.' % (', '.join(e['resta_fuori']['giudici_oltre_0_60']) or 'nessuno',
                                                                  ', '.join(e['resta_fuori']['misure_fuori_2sigma']) or 'nessuna', e['resta_fuori']['copia_superata']), '']
        if s.get('lettura_V'):
            v = s['lettura_V']
            md += ['Parte V: baseline ' + ', '.join('%s %s' % (j, mf(x)) for j, x in v['baseline'].items()) +
                   ('; quota del progresso di IA32 fatta dai soli conteggi: ' + ', '.join('%s %s' % (j, mf(x, 2)) for j, x in v.get('quota_del_progresso_di_ia32_fatta_dai_soli_conteggi', {}).items())
                    if v.get('quota_del_progresso_di_ia32_fatta_dai_soli_conteggi') else ''), '']
    open(os.path.join(USCITA, 'ia33_oracolo.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


def main():
    import numpy
    import torch
    print('ia33: mondi %s, insiemi %s, libro (%s)' % (MONDI33, INSIEMI, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    os.makedirs(CACHE33, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    processi = int(os.environ.get('PROCESSI', 3))
    fasi = os.environ.get('FASI', 'PCES')
    if len(MONDI33) > 1 and os.environ.get('IA33_FIGLIO') != '1':
        # un processo nuovo per ogni mondo (il testo del mondo si costruisce una volta sola per processo); la sintesi poi legge i file
        import subprocess
        senza_s = ''.join(ch for ch in fasi if ch != 'S')
        for mondo in MONDI33:
            if senza_s:
                rc = subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, MONDI33=str(MONDI_ELENCO.index(mondo) + 1), FASI=senza_s, IA33_FIGLIO='1'))
                if rc != 0:
                    sys.exit(rc)
        if 'S' in fasi:
            sys.exit(subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, FASI='S', IA33_FIGLIO='1')))
        return
    sintesi = OrderedDict()
    for mondo in MONDI33:
        if os.environ.get('RIPRENDI') != '1' and 'P' in fasi:
            azzera_corse(mondo)
        s = OrderedDict()
        if 'P' in fasi:
            fase_P(mondo, processi, addestra='L' in INSIEMI)
        if 'C' in fasi and 'L' in INSIEMI:
            s['ciclo'] = fase_C(mondo, processi)
        elif os.path.exists(cart33(mondo, 'ciclo_esito.json')):
            s['ciclo'] = json.load(open(cart33(mondo, 'ciclo_esito.json'), encoding='utf-8'))
        if 'E' in fasi:
            A = fase_E(mondo, processi)
            s['insiemi'] = OrderedDict((t, riassunto_insieme(mondo, A, t)) for t in A['ins'])
            s['v21'] = riassunto_v21(A)
            s['v21_libri'] = A['v21']
            s['giudice_b'] = A['giudice_b']
            s['ngr_ordine'] = (A['corse_libro'].get('libro|ngr|1') or {}).get('ngr')
            json.dump(OrderedDict((k, s[k]) for k in ('insiemi', 'v21', 'v21_libri', 'giudice_b', 'ngr_ordine')), open(cart33(mondo, 'esame.json'), 'w', encoding='utf-8', newline='\n'),
                      ensure_ascii=False, indent=1, default=float)
        elif 'S' in fasi and os.path.exists(cart33(mondo, 'esame.json')):
            s.update(json.load(open(cart33(mondo, 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict))
        sintesi[mondo] = s
    if 'S' in fasi:
        fase_S(MONDI33, sintesi)


if __name__ == '__main__':
    main()
