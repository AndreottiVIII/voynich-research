# -*- coding: utf-8 -*-
"""Esperimento IA32 (ia32): l'IA che si allena finche' non riesce a rifare il Voynich.

Domanda (richiesta di Davide, 22/11/2026; revisione di Fable, A1 e A11, proposte C1 e C8): una rete che ha letto TUTTO il libro (meno una piccola parte tenuta fuori) e
che scrive con poche manopole continue, regolate da un ottimizzatore senza gradiente (CMA-ES) che prova e sbaglia contro giudici e misure di ALLENAMENTO, arriva a
scrivere libri che giudici MAI VISTI (N e KN di IA26 ricalcolati, e un giudice nuovo addestrato dopo il ciclo) non distinguono dal vero e che hanno al vero le misure
TENUTE FUORI? Se no, il registro dei tentativi dice che cosa non si lascia rifare.
Preregistrazione: preregistrazioni/ia32.md. Moduli di supporto (prefisso `rifare_`): rifare_dati (modello pieno), rifare_scrittura (manopole di scrittura e guardia
anti-copia), rifare_cma (CMA-ES), rifare_misure (obiettivo e misure), rifare_giudice (giudice nuovo b). Il banco e' quello di IA26 (`righello_banco`, importato senza modificarlo).

Fasi (variabile FASI, predefinita PCENS), per ogni mondo di MONDI32 (1 = markov2, il controllo positivo; 2 = il libro vero):
  P  preparazione (R: solo il riferimento e il naturale, senza addestrare): riferimento del mondo (copiato da dati/cache/ia26 se c'e', altrimenti costruito), riferimento "naturale" della copia, modello pieno
  C  il ciclo a prove ed errori (CMA-ES) con rivalutazione dei finalisti -> manopole migliori
  E  l'esame: libri nuovi con le manopole migliori, con manopole neutre e con manopole a caso (controllo negativo economico); giudici mai visti; misure tenute fuori; criteri
  S  sintesi -> risultati/ia32_rifare_il_voynich.json e .md (solo numeri e aggregati)

    nohup bash strumenti/coda.sh ia32 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia32" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella fuori dal repo> CACHE32=<cartella fuori dal repo> python esperimenti/ia32_rifare_il_voynich.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): MONDI32 (cifre: 1 markov2, 2 vero; predefinito 12), FASI32 non c'e': si usa FASI; CACHE32 (cartella dei modelli e
dei libri), LAMBDA32 (candidati per generazione, 12), GEN32 (generazioni, 20), SIGMA32 (0,25), RIV32 (coppie di mezzi libri per rivalutare i finalisti, 3), N_ESAME32 (libri
dell'esame, 16), N_NEUTRO32 (4), N_CASUALI32 (insiemi di manopole a caso, 8), N_CAS_LIBRI32 (4), GRU32 (1: k90 e R_rel nell'esame), PERM32 (permutazioni del nullo di b, 12),
FUORI32, VAL32, NASCOSTO32, EPOCHE32, PAZIENZA32, EXTRA32, EXTRA_MIN32, SEME_FOGLI32, PICCOLO32 (solo prove), KAPPA32, ZCAP32, C_B32, AUC_NEUTRO_MIN32, RIPRENDI, PROCESSI, FILTRO.
Quelle di IA26 (S_META26, S_NULLO26, S_NULLO_N26, S_GRU26, S_GRU_MONDO26, CHUNK26, ...) valgono per il riferimento costruito qui.
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

NOME = 'ia32_rifare_il_voynich'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE32 = os.environ.get('CACHE32', os.path.join(USCITA, 'ia32_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia32'))
CACHE26_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia26')
os.environ['CACHE26'] = os.path.join(CACHE32, 'banco')          # il banco di IA26 scrive qui, mai nella cache di IA26
os.environ.setdefault('CHUNK26', '500')                         # un solo gruppo di testi per i lavori K, KN e D
os.environ.setdefault('S_GRU_MONDO26', '6')                     # divisioni a meta' per k90 e R_rel nel mondo markov2 (IA26 ne usa 3 nei mondi: con 3 la scala e' troppo incerta)
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_cma as CMA  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_giudice as RGB  # noqa: E402
import righello_giudici as RG  # noqa: E402

MONDI_ELENCO = ['markov2', 'vero']
MONDI32 = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI32', '12') if x.isdigit() and 1 <= int(x) <= 2]
LAMBDA = int(os.environ.get('LAMBDA32', 12))
GEN = int(os.environ.get('GEN32', 20))
SIGMA0 = float(os.environ.get('SIGMA32', 0.25))
RIV = int(os.environ.get('RIV32', 3))
N_ESAME = int(os.environ.get('N_ESAME32', 16))
N_NEUTRO = int(os.environ.get('N_NEUTRO32', 4))
N_CASUALI = int(os.environ.get('N_CASUALI32', 8))
N_CAS_LIBRI = int(os.environ.get('N_CAS_LIBRI32', 4))
GRU = os.environ.get('GRU32', '1') == '1'
PERM = int(os.environ.get('PERM32', 12))
PIEGHE = I7.PIEGHE

# ---- criteri (scritti nella preregistrazione prima di ogni corsa sul Voynich)
AUC_MAX = 0.60                     # giudici mai visti: al massimo cosi' (e almeno 1 - AUC_MAX: un AUC sotto 0,40 non e' "indistinguibile")
QUOTA_ENTRO_2S = 0.80              # almeno l'80% delle misure tenute fuori entro 2 sigma del vero
SIGMA_DA_SCALA = 1.0 / math.sqrt(2.0)   # sigma di un libro intero ~ scala (deviazione standard della differenza fra meta') / radice di 2
SIGMA_IA25 = OrderedDict([('copia_netta', 0.0098), ('lam', 0.039), ('contatto', 0.0097), ('D', 0.0122), ('G9', 0.0019), ('bordi_inizio', 0.0048), ('bordi_fine', 0.0025),
                          ('parole_nuove', 0.0051), ('costo_forma', 0.034)])   # IA25, parte 5 (solo per il confronto sul Voynich)
V21_NOMI = ['V21:%d' % k for k in range(13, 23)]


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def cart32(mondo, *p):
    return os.path.join(CACHE32, mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia32_corse_%s.jsonl' % mondo)


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


def fatte_di(mondo, fasi_chiave=None):
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
    RM.prepara(mondo, cart32(mondo), nomi)


def lavoro32(args):
    if args[0] == 'addestra':
        t = time.time()
        try:
            ris = RD.addestra_pieno(cart32(RM._W['mondo'], 'modello'), messaggi=lambda s: print('[addestra %s] %s' % (RM._W['mondo'], s), flush=True))
            ris = OrderedDict((a, v) for a, v in ris.items() if not a.startswith('curva'))
            ris['lavoro'] = 'addestra|pieno'
            ris['secondi'] = round(time.time() - t, 1)
            return ris
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'addestra|pieno'), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = RM.lavoro_banco(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


def ident(a):
    if a[0] == 'libro':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'valuta':
        return 'ciclo|%d|%d' % (a[1], a[2])
    return '|'.join(str(x) for x in a)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia32_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro32, da_fare), 1):
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

def attiva_main(mondo, nomi=()):
    B.imposta_mondo(mondo, list(nomi))


def costruisci_riferimento(mondo, processi):
    """Il riferimento del mondo: dal cache di IA26 se c'e' (copia di riferimento.json e dei modelli di misura), altrimenti costruito con i lavori del banco."""
    dest = os.path.join(CACHE32, 'banco', mondo)
    os.makedirs(os.path.join(dest, 'modelli_misura'), exist_ok=True)
    rif_p = os.path.join(dest, 'riferimento.json')
    if os.path.exists(rif_p):
        return completa_gru(mondo, json.load(open(rif_p, encoding='utf-8')), rif_p, processi)
    orig = os.path.join(CACHE26_ORIG, mondo)
    if not SOLO_CONTROLLI and os.path.exists(os.path.join(orig, 'riferimento.json')):
        shutil.copy(os.path.join(orig, 'riferimento.json'), rif_p)
        for f in os.listdir(os.path.join(orig, 'modelli_misura')):
            if not os.path.exists(os.path.join(dest, 'modelli_misura', f)):
                shutil.copy(os.path.join(orig, 'modelli_misura', f), os.path.join(dest, 'modelli_misura', f))
        print('riferimento di %s copiato da IA26' % mondo, flush=True)
        return completa_gru(mondo, json.load(open(rif_p, encoding='utf-8')), rif_p, processi)
    print('riferimento di %s: costruzione con i lavori del banco' % mondo, flush=True)
    attiva_main(mondo, [])
    fasi = B.fasi_banco([], con_gru=GRU, con_vero=True, mondo=mondo)
    fn = [a for a in fasi['N'] if a[1] != 'A']
    lavori = [a for a in fasi['B'] if a[0] != 'J'] + fn
    corse = percorso_corse(mondo + '_rif')
    fatte = set()
    ris = []
    nome_precedente = percorso_corse
    for nf, lst in (('B', [a for a in fasi['B']]), ('N', fn)):
        ris += esegui_rif(mondo, lst, processi, fatte, corse)
    C = B.indice_corse(ris + [c for c in leggi_corse(corse) if not c.get('errore')])
    rif = B.riferimento_da_corse(C)
    json.dump(rif, open(rif_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    return rif


def completa_gru(mondo, rif, rif_p, processi):
    """Se si vogliono k90 e R_rel (GRU32=1) e il riferimento non li ha (IA26 li misura solo nel mondo vero e in `calibrato`), costruisce solo quelli: k90 e R_rel del
    mondo sul testo intero (un seme) e su `S_GRU_MONDO26` divisioni a meta' (due corse a divisione); poi li aggiunge al riferimento."""
    if not GRU or 'k90' in rif['vero']:
        return rif
    print('riferimento di %s: aggiungo k90 e R_rel (reti piccole)' % mondo, flush=True)
    attiva_main(mondo, [])
    n_split = B.S_GRU if mondo == 'vero' else B.S_GRU_MONDO
    lavori = [('G', tp, 'vero', s) for s in B.SEMI_GRU_VERO[:1] for tp in ('K', 'R')]
    lavori += [('gm', tp, s, m) for s in range(1, n_split + 1) for m in (1, 2) for tp in ('K', 'R')]
    corse = percorso_corse(mondo + '_rif')
    ris = esegui_rif(mondo, lavori, processi, set(), corse)
    C = B.indice_corse(ris)
    r2 = B.riferimento_da_corse(C)
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


def esegui_rif(mondo, lavori, processi, fatte, corse):
    da_fare = [a for a in lavori if ident(a) not in fatte]
    out = []
    if not da_fare:
        return out
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_banco, initargs=(mondo,)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro_banco_puro, da_fare), 1):
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


def lavoro_banco_puro(args):
    return B.lavoro(args)


def fase_P(mondo, processi, addestra=True):
    os.makedirs(cart32(mondo), exist_ok=True)
    rif = costruisci_riferimento(mondo, processi)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    nat_p = cart32(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('mondo %s: riferimento con %d misure e %d giudici; fogli addestramento/validazione/fuori %d/%d/%d' % (mondo, len(rif['vero']), len(rif['nullo']),
                                                                                                    len(f_add), len(f_val), len(f_fuori)), flush=True)
    if addestra:
        esegui(mondo, [], [('addestra',)], 1, fatte_di(mondo))
    return rif


# ---------------------------------------------------------------- C: il ciclo

def meta_fogli(mondo, gen, rep=0):
    """Due meta' complementari dei fogli per la generazione `gen` (uguali per tutti i candidati). -> (meta' A, meta' B)."""
    ff = sorted({x['foglio'] for x in I7.libro_vero()})
    import random
    rnd = random.Random(seme_str('ia32mezzi', mondo, gen, rep))
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
    st_p = cart32(mondo, 'ciclo.json')
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(st_p):
        stato = json.load(open(st_p, encoding='utf-8'))
        cma = CMA.CMA.da_stato(stato['cma'])
        storia = stato['storia']
    else:
        cma = CMA.CMA(RS.neutro_cubo(), SIGMA0, LAMBDA, seme=seme_str('ia32cma', mondo))
        storia = []
        azzera_corse_ciclo(mondo)
    fatte = fatte_di(mondo)
    while cma.gen < GEN:
        g = cma.gen
        xs, _ = cma.ask()
        mA, mB = meta_fogli(mondo, g)
        lavori = []
        for i, u in enumerate(xs):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', g * 10 + h, i, list(map(float, u)), seme_str('ia32ciclo', mondo, g, i, h), fogli))
        ris = esegui(mondo, [], lavori, processi, fatte)
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
    # finalisti: media finale, il migliore di sempre, il migliore dell'ultima generazione, e il neutro come riferimento
    cand = OrderedDict()
    cand['neutro'] = RS.neutro_cubo()
    cand['media_finale'] = cma.mean
    best_i, best_v, best_u = None, 1e9, None
    for h in storia:
        for u, v in zip(h['punti'], h['valori']):
            if v < best_v:
                best_v, best_u = v, np.array(u)
    cand['migliore_di_sempre'] = best_u
    u_ult = np.array(storia[-1]['punti'][int(np.argmin(storia[-1]['valori']))])
    cand['migliore_ultima'] = u_ult
    lavori = []
    for r in range(RIV):
        mA, mB = meta_fogli(mondo, 1000 + r, r)
        for ci, (nome, u) in enumerate(cand.items()):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', 9000 + r * 10 + h, ci, list(map(float, np.clip(u, 0, 1))), seme_str('ia32riv', mondo, r, ci, h), fogli))
    esegui(mondo, [], lavori, processi, fatte)
    tutti = [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('ciclo|9') and not c.get('errore')]
    fin = OrderedDict()
    for ci, nome in enumerate(cand):
        rs = [c for c in tutti if c['i'] == ci and c['gen'] >= 9000]
        fin[nome] = OrderedDict([('obiettivo', media_valutazioni(rs)), ('n', len(rs)), ('u', list(map(float, np.clip(cand[nome], 0, 1)))),
                                 ('manopole', RS.da_cubo(np.clip(cand[nome], 0, 1))),
                                 ('z', OrderedDict((m, float(np.mean([c['z'][m] for c in rs if m in c['z']]))) for m in RM.OBIETTIVO) if rs else None),
                                 ('copia_violazioni', OrderedDict((k, float(np.mean([c['copia_violazioni'].get(k, 0.0) for c in rs]))) for k in RM.SOGLIE_COPIA) if rs else None)])
    scelto = min((n for n in fin if fin[n]['obiettivo'] is not None), key=lambda n: fin[n]['obiettivo'])
    ris = OrderedDict([('storia', storia), ('finalisti', fin), ('scelto', scelto), ('u_migliore', fin[scelto]['u']), ('manopole_migliori', fin[scelto]['manopole'])])
    json.dump(ris, open(cart32(mondo, 'ciclo_esito.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('ciclo finito: scelto %s, obiettivo %.3f (neutro %.3f)' % (scelto, fin[scelto]['obiettivo'], fin['neutro']['obiettivo']), flush=True)
    return ris


def azzera_corse_ciclo(mondo):
    if os.environ.get('RIPRENDI') != '1':
        os.makedirs(USCITA, exist_ok=True)
        open(percorso_corse(mondo), 'w').close()


# ---------------------------------------------------------------- E: l'esame

def insiemi_esame(mondo, ris_ciclo):
    """I libri dell'esame: tipo -> (lista di nomi, u, descrizione)."""
    out = OrderedDict()
    u = np.array(ris_ciclo['u_migliore'])
    out['ia32best'] = dict(n=N_ESAME, u=u, kind='migliore')
    out['ia32neu'] = dict(n=N_NEUTRO, u=RS.neutro_cubo(), kind='neutro')
    rnd = np.random.default_rng(seme_str('ia32casuali', mondo))
    for c in range(1, N_CASUALI + 1):
        out['ia32c%d' % c] = dict(n=N_CAS_LIBRI, u=np.clip(RS.neutro_cubo() + rnd.uniform(-0.45, 0.45, RS.DIM), 0.0, 1.0), kind='casuale')
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
    ris_ciclo = json.load(open(cart32(mondo, 'ciclo_esito.json'), encoding='utf-8'))
    ins = insiemi_esame(mondo, ris_ciclo)
    attiva_main(mondo, [])
    v21 = v21_disponibili() if mondo == 'vero' else []
    nomi = [nome_libro(t, i) for t, d in ins.items() for i in range(1, d['n'] + 1)] + v21
    attiva_main(mondo, nomi)
    fatte = fatte_di(mondo)
    libri = [('libro', t, i, list(map(float, d['u'])), seme_str('ia32esame', mondo, t, i)) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    print('== esame %s: %d libri da scrivere' % (mondo, len(libri)), flush=True)
    esegui(mondo, nomi, libri, processi, fatte)
    lavori = [('M', n) for n in nomi] + [('J32', n) for n in nomi]
    lavori += [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    if GRU:
        for t in ('ia32best', 'ia32neu'):
            for i in range(1, ins[t]['n'] + 1):
                lavori += [('G', tp, nome_libro(t, i), 1) for tp in ('K', 'R')]
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
    # le corse del banco di questo esame sono nel file del mondo (stessi nomi di lavoro): il profilo si compone con valori_libro
    for k in list(C):
        pass
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    n_pag = len(c['ids'])
    prof = OrderedDict((n, RM.valori_libro(n, C, pK, pKN, n_pag)) for n in nomi)
    # giudice nuovo b: pagine dei fogli tenuti fuori
    S_f = RD.divisione_fogli()[2]
    fuori = set(S_f)
    pagine = [p for p in c['ids'] if I7.foglio_di(p) in fuori]
    voc = RG.vocabolario_N(c['vere'])
    giudice_b = OrderedDict()
    for t, d in ins.items():
        ls = [nome_libro(t, i) for i in range(1, d['n'] + 1)]
        giudice_b[t] = RGB.esame_b(c['vere'], libri_rows(ls), pagine, I7.foglio_di, voc, n_train=len(ls) // 2, permutazioni=PERM, seme=seme_str('b', mondo, t) % 1000)
    if v21:
        giudice_b['v21'] = RGB.esame_b(c['vere'], libri_rows(v21), pagine, I7.foglio_di, voc, n_train=len(v21) // 2, permutazioni=PERM, seme=seme_str('b', mondo, 'v21') % 1000)
    for t in ins:
        for n in [nome_libro(t, i) for i in range(1, ins[t]['n'] + 1)]:
            prof[n]['b'] = giudice_b[t]['auc']
    # corse dei libri
    corse_libro = {r['lavoro']: r for r in leggi_corse(percorso_corse(mondo)) if str(r.get('lavoro', '')).startswith('libro|') and not r.get('errore')}
    return dict(rif=rif, prof=prof, giudice_b=giudice_b, ins=ins, nomi=nomi, v21=v21, corse_libro=corse_libro, n_pag=n_pag)


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sigma_di(rif, m, mondo):
    s = rif['scala'].get(m)
    return None if s is None else s * SIGMA_DA_SCALA


def criteri(mondo, A, tipo):
    """I criteri preregistrati per l'insieme di libri `tipo`. -> dict con l'esito ('riuscito', 'in parte', 'non riuscito', 'non valido'), i giudici, le misure e la copia."""
    rif, prof = A['rif'], A['prof']
    ls = [nome_libro(tipo, i) for i in range(1, A['ins'][tipo]['n'] + 1)]
    out = OrderedDict()
    jud = OrderedDict((j, media([prof[l].get(j) for l in ls])) for j in ('N', 'KN', 'b'))
    out['giudici_mai_visti'] = jud
    out['giudici_di_allenamento'] = OrderedDict((j, media([prof[l].get(j) for l in ls])) for j in ('e231', 'e266', 'K'))
    out['giudici_ok'] = bool(all(v is not None and (1 - AUC_MAX) <= v <= AUC_MAX for v in jud.values()))
    mis = OrderedDict()
    for m in RM.FUORI_MISURE:
        if m not in rif['vero'] or rif['scala'].get(m) is None:
            continue
        val = media([prof[l].get(m) for l in ls])
        s = sigma_di(rif, m, mondo)
        if val is None or not s:
            continue
        z = (val - rif['vero'][m]) / s
        mis[m] = OrderedDict([('valore', val), ('vero', rif['vero'][m]), ('sigma', s), ('z', z), ('entro_2sigma', bool(abs(z) <= 2.0)),
                              ('sigma_ia25', SIGMA_IA25.get(m) if mondo == 'vero' else None)])
    out['misure_tenute_fuori'] = mis
    out['quota_entro_2sigma'] = float(np.mean([x['entro_2sigma'] for x in mis.values()])) if mis else None
    out['misure_fuori'] = [m for m, x in mis.items() if not x['entro_2sigma']]
    cop = A['corse_libro']
    viol = [max(cop['libro|%s|%d' % (tipo, i)]['copia_violazioni'].values() or [0.0]) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]
    out['copia_ok'] = bool(viol) and max(viol) <= 0.0
    out['copia_violazione_max'] = max(viol) if viol else None
    out['copia_quote'] = OrderedDict((k, media([cop['libro|%s|%d' % (tipo, i)]['copia'].get(k) for i in range(1, A['ins'][tipo]['n'] + 1) if 'libro|%s|%d' % (tipo, i) in cop]))
                                     for k in RM.SOGLIE_COPIA)
    return out


def esito(mondo, A):
    """Esito per il migliore e per ogni confronto. Criteri scritti prima: riuscito / in parte / non riuscito; non valido se il giudice b non vede l'imitatore neutro."""
    migliore = criteri(mondo, A, 'ia32best')
    neutro = criteri(mondo, A, 'ia32neu')
    b_neutro = A['giudice_b']['ia32neu']['auc']
    valido = bool(b_neutro is not None and b_neutro >= RGB.AUC_NEUTRO_MIN)
    # riferimento per "in parte": il v21 (sul Voynich) o il neutro (nei mondi sintetici)
    if A['v21']:
        base = OrderedDict((j, media([A['prof'][n].get(j) for n in A['v21']])) for j in ('N', 'KN'))
        base['b'] = A['giudice_b'].get('v21', {}).get('auc')
        base_nome = 'v21'
    else:
        base = neutro['giudici_mai_visti']
        base_nome = 'manopole neutre'
    migliora = OrderedDict((j, bool(migliore['giudici_mai_visti'][j] is not None and base.get(j) is not None and abs(migliore['giudici_mai_visti'][j] - 0.5) < abs(base[j] - 0.5)))
                           for j in ('N', 'KN', 'b'))
    if not valido:
        e = 'non valido'
    elif migliore['giudici_ok'] and migliore['quota_entro_2sigma'] is not None and migliore['quota_entro_2sigma'] >= QUOTA_ENTRO_2S and migliore['copia_ok']:
        e = 'riuscito'
    elif all(migliora.values()):
        e = 'in parte'
    else:
        e = 'non riuscito'
    # controllo negativo economico: nessuno degli insiemi a caso supera l'esame
    cas = OrderedDict()
    for t in A['ins']:
        if not t.startswith('ia32c'):
            continue
        cr = criteri(mondo, A, t)
        sup = bool(cr['giudici_ok'] and cr['quota_entro_2sigma'] is not None and cr['quota_entro_2sigma'] >= QUOTA_ENTRO_2S and cr['copia_ok'])
        cas[t] = OrderedDict([('giudici', cr['giudici_mai_visti']), ('quota_entro_2sigma', cr['quota_entro_2sigma']), ('copia_ok', cr['copia_ok']), ('supera', sup),
                              ('manopole', RS.da_cubo(A['ins'][t]['u']))])
    neg_ok = bool(cas) and not any(x['supera'] for x in cas.values())
    return OrderedDict([('esito', e), ('valido', valido), ('giudice_b_neutro', b_neutro), ('migliore', migliore), ('neutro', neutro), ('base_confronto', base_nome),
                        ('base', base), ('migliora_sulla_base', migliora), ('casuali', cas), ('controllo_negativo_riuscito', neg_ok)])


# ---------------------------------------------------------------- S: sintesi

def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def fase_S(mondi, sintesi):
    os.makedirs(USCITA, exist_ok=True)
    out = OrderedDict([('esperimento', NOME), ('mondi', sintesi)])
    json.dump(out, open(os.path.join(USCITA, 'ia32_rifare_il_voynich.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ['# IA32 (ia32) — L\'IA che si allena finche\' non riesce', '', 'Preregistrazione: `preregistrazioni/ia32.md`. Solo numeri e aggregati.', '']
    for mondo, s in sintesi.items():
        md += ['## Mondo `%s`' % mondo, '']
        if 'ciclo' in s and s['ciclo']:
            c = s['ciclo']
            md += ['Ciclo: %d generazioni, obiettivo del migliore %s contro %s delle manopole neutre (scelto: %s).' % (len(c['storia']), mf(c['finalisti'][c['scelto']]['obiettivo']),
                                                                                                       mf(c['finalisti']['neutro']['obiettivo']), c['scelto']), '']
            md += ['| generazione | obiettivo minimo | media | passo CMA-ES |', '|---|---|---|---|']
            for h in c['storia']:
                md.append('| %d | %s | %s | %s |' % (h['gen'], mf(h['minimo']), mf(h['media']), mf(h['sigma'], 3)))
            md += ['', '| finalista | obiettivo rivalutato | ' + ' | '.join(RM.OBIETTIVO) + ' |', '|---|---|' + '---|' * len(RM.OBIETTIVO)]
            for n, x in c['finalisti'].items():
                md.append('| %s | %s | %s |' % (n, mf(x['obiettivo']), ' | '.join(mf((x['z'] or {}).get(m), 1) for m in RM.OBIETTIVO)))
            md += ['', '(z delle grandezze di allenamento: misure rispetto al vero degli stessi fogli, giudici rispetto al nullo.)', '']
            md += ['| manopola | valore scelto | neutro |', '|---|---|---|']
            for k, v in c['manopole_migliori'].items():
                md.append('| %s | %s | %s |' % (k, mf(v), mf(RS.NEUTRO[k])))
            md.append('')
        if 'esame' in s and s['esame']:
            e = s['esame']
            md += ['**Esito: %s** (giudice b valido: %s; controllo negativo riuscito: %s).' % (e['esito'], e['valido'], e['controllo_negativo_riuscito']), '']
            m = e['migliore']
            md += ['| giudice mai visto | migliore | neutro | %s |' % e['base_confronto'], '|---|---|---|---|']
            for j in ('N', 'KN', 'b'):
                md.append('| %s | %s | %s | %s |' % (j, mf(m['giudici_mai_visti'][j]), mf(e['neutro']['giudici_mai_visti'][j]), mf(e['base'].get(j))))
            md += ['', '| misura tenuta fuori | valore | vero | z (sigma = scala / radice 2) | entro 2 sigma |', '|---|---|---|---|---|']
            for k, x in m['misure_tenute_fuori'].items():
                md.append('| %s | %s | %s | %s | %s |' % (k, mf(x['valore'], 4), mf(x['vero'], 4), mf(x['z'], 2), 'si' if x['entro_2sigma'] else 'NO'))
            md += ['', 'Quota entro 2 sigma: %s; misure fuori: %s; copia: %s.' % (mf(m['quota_entro_2sigma'], 2), ', '.join(m['misure_fuori']) or 'nessuna', 'ok' if m['copia_ok'] else 'superata'), '']
            md += ['Controllo negativo (manopole a caso): ' + '; '.join('%s: giudici %s, supera %s' % (t, {j: mf(v) for j, v in x['giudici'].items()}, x['supera']) for t, x in e['casuali'].items()), '']
    open(os.path.join(USCITA, 'ia32_rifare_il_voynich.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


def main():
    import numpy
    import torch
    print('ia32: mondi %s, libro (%s)' % (MONDI32, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    os.makedirs(CACHE32, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    processi = int(os.environ.get('PROCESSI', 3))
    fasi = os.environ.get('FASI', 'PCENS')
    sintesi = OrderedDict()
    for mondo in MONDI32:
        if os.environ.get('RIPRENDI') != '1' and 'P' in fasi:
            azzera_corse(mondo)
        s = OrderedDict()
        if 'P' in fasi or 'R' in fasi:
            fase_P(mondo, processi, addestra='P' in fasi)
        if 'C' in fasi:
            s['ciclo'] = fase_C(mondo, processi)
        elif os.path.exists(cart32(mondo, 'ciclo_esito.json')):
            s['ciclo'] = json.load(open(cart32(mondo, 'ciclo_esito.json'), encoding='utf-8'))
        if 'E' in fasi:
            A = fase_E(mondo, processi)
            s['esame'] = esito(mondo, A)
            s['giudice_b'] = A['giudice_b']
        sintesi[mondo] = s
    if 'S' in fasi:
        fase_S(MONDI32, sintesi)


if __name__ == '__main__':
    main()
