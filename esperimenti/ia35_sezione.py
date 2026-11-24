# -*- coding: utf-8 -*-
"""Esperimento IA35 (ia35): la rete che sa dove scrive.

Domanda (seguito di IA34): IA34 ha mostrato che estrarre parole intere dal vocabolario di sezione scavalcando la rete costa sui giudici piu' di quanto rende (la sorgente di sezione e' rimasta
spenta) e che lo scarto residuo del Voynich e' il vocabolario condiviso fra pagine della stessa sezione e l'inizio dei paragrafi. Una rete GRU che riceve a OGNI passo la sezione, la lingua, la
mano, il tipo di riga (inizio di paragrafo), la posizione della riga e la posizione nella riga (rete condizionata), riaddestrata sugli stessi 78/7/15 fogli di IA32-IA34, impara da sola
vocabolario di sezione e aperture? Ablazione: la stessa rete, stesso seme e addestramento, senza condizionamento persistente (le teste restano nel flusso, come in IA32).
Mondi: `struttura2` (controllo positivo di regola nota con vocabolario di sezione, riga sopra, chiusure e aperture, senza parole di tema: oracolo e gemello da validare) e `vero`.
Preregistrazione: preregistrazioni/ia35.md. Moduli di supporto (prefisso `sezione_`): sezione_rete (rete condizionata e ablazione), sezione_scrittura (scrittore di IA33 sopra la rete),
sezione_lavori (obiettivo, libri, lavori), sezione_mondo (mondo `struttura2`), sezione_misure (otto misure di struttura), sezione_giudice (giudice b mediato). Si importano, senza modificarli, i moduli di
IA34 (`piano_*`), IA33 (`oracolo_*`), IA32 (`rifare_*`) e il banco di IA26.

Fasi (variabile FASI, predefinita PCES), per ogni mondo di MONDI35 (1 = struttura2, controllo positivo e oracolo; 2 = il libro vero), **un processo figlio per mondo**:
  P  preparazione: riferimento del mondo (mondo `vero`: copiato da dati/cache/ia33), "naturale", otto misure di struttura (valore e scala), addestramento delle DUE reti (condizionata `C` e ablazione `A`)
  C  il ciclo a prove ed errori (CMA-ES, 14 manopole di IA33, obiettivo a 12 grandezze di IA34) sulla rete condizionata, con rivalutazione dei finalisti (anche il punto di IA33 sull'ablazione)
  E  l'esame: libri di tutti gli insiemi, giudici mai visti (b mediato su 8 divisioni), misure tenute fuori (D, R_rel e otto di struttura), criteri, lettura "che cosa porta il condizionamento"
  S  sintesi -> risultati/ia35_sezione.json e .md (solo numeri e aggregati)

    nohup bash strumenti/coda.sh ia35 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia35" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella fuori dal repo> CACHE35=<cartella fuori dal repo> python esperimenti/ia35_sezione.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): MONDI35 (cifre: 1 struttura2, 2 vero; predefinito 12), CACHE35, LAMBDA35 (12), GEN35 (10), NSPLIT35 (6), SIGMA35 (0,25), RIV35 (3), N_ESAME35 (16),
N_NEUTRO35 (4), N_IA33_35 (8), N_BESTA35 (8), N_CASUALI35 (3), N_CAS_LIBRI35 (4), N_ORACOLO35 (16), N_ORACOLO_PIU35 (8), N_GEM35 (16), N_GRU35 (8), GRU35 (1), PERM35 (inutilizzata: vedi PERM_B35), INSIEMI35 (L, O;
predefinito LO), PARTENZA35 (ia33 o neutro), SEME_RETE35 (35001), RIP_B35 (8), PERM_B35 (8). Quelle di IA32-IA34 (S_NM34, NU_RIGA34 non usata, KAPPA33, ...) e di IA26 valgono per il banco e per lo scrittore.
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

NOME = 'ia35_sezione'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE35 = os.environ.get('CACHE35', os.path.join(USCITA, 'ia35_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia35'))
CACHE33_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia33')
CACHE26_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia26')
os.environ['CACHE26'] = os.path.join(CACHE35, 'banco')          # il banco di IA26 scrive qui, mai nella cache di IA26 ne' di IA32
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
import piano_mondo as PM  # noqa: E402
import piano_misure as PMS  # noqa: E402
import piano_scrittura as PS  # noqa: E402
import piano_lavori as PL  # noqa: E402
import sezione_mondo as SMO  # noqa: E402
import sezione_misure as SM  # noqa: E402
import sezione_rete as SR  # noqa: E402
import sezione_lavori as SL  # noqa: E402

MONDI_ELENCO = ['struttura2', 'vero']
MONDI35 = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI35', '12') if x.isdigit() and 1 <= int(x) <= 2]
LAMBDA = int(os.environ.get('LAMBDA35', 12))
GEN = int(os.environ.get('GEN35', 10))
SIGMA0 = float(os.environ.get('SIGMA35', 0.25))
RIV = int(os.environ.get('RIV35', 3))
N_ESAME = int(os.environ.get('N_ESAME35', 16))
N_NEUTRO = int(os.environ.get('N_NEUTRO35', 4))
N_IA33 = int(os.environ.get('N_IA33_35', 8))
N_BESTA = int(os.environ.get('N_BESTA35', 8))
N_CASUALI = int(os.environ.get('N_CASUALI35', 4))
N_CAS_LIBRI = int(os.environ.get('N_CAS_LIBRI35', 4))
N_ORACOLO = int(os.environ.get('N_ORACOLO35', 16))
N_ORACOLO_PIU = int(os.environ.get('N_ORACOLO_PIU35', 8))
N_GEM = int(os.environ.get('N_GEM35', 16))
N_GRU = int(os.environ.get('N_GRU35', 8))
GRU = os.environ.get('GRU35', '1') == '1'
PERM = int(os.environ.get('PERM35', 12))
INSIEMI = os.environ.get('INSIEMI35', 'LO')
PARTENZA = os.environ.get('PARTENZA35', 'ia33')
PIEGHE = I7.PIEGHE
NSPLIT = int(os.environ.get('NSPLIT35', 6))

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


def cart35(mondo, *p):
    return os.path.join(CACHE35, mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia35_corse_%s.jsonl' % mondo)


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
    RM.prepara(mondo, cart35(mondo), nomi)


def lavoro33(args):
    if args[0] == 'addestra':
        rete = args[1]
        t = time.time()
        try:
            ris = SR.addestra_pieno35(cart35(RM._W['mondo'], 'rete_' + rete), cond=(rete != 'A'), var=SR.VARIANTI.get(rete), messaggi=lambda s: print('[addestra %s %s] %s' % (RM._W['mondo'], rete, s), flush=True))
            ris = OrderedDict((a, v) for a, v in ris.items() if not a.startswith('curva'))
            ris['lavoro'] = 'addestra|' + rete
            ris['secondi'] = round(time.time() - t, 1)
            return ris
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'addestra|' + rete), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = SL.lavoro_banco35(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


def ident(a):
    if a[0] == 'B35':
        return 'B35|%s' % a[1]
    if a[0] == 'libro35':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'valuta':
        return 'ciclo|%d|%d' % (a[1], a[2])
    return '|'.join(str(x) for x in a)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia35_corse_<mondo>.jsonl. -> lista dei risultati."""
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


def copia_da_ia33(mondo):
    """Dalla cache di IA33 (solo corsa vera, solo mondo `vero`): riferimento e modelli di misura del banco e riferimento "naturale" (calcolato in IA33 in un processo pulito). -> True se copiato."""
    if SOLO_CONTROLLI or mondo != 'vero':
        return False
    ok = False
    o_banco = os.path.join(CACHE33_ORIG, 'banco', mondo)
    d_banco = os.path.join(CACHE35, 'banco', mondo)
    if os.path.exists(os.path.join(o_banco, 'riferimento.json')) and not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        os.makedirs(os.path.join(d_banco, 'modelli_misura'), exist_ok=True)
        shutil.copy(os.path.join(o_banco, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
        for f in os.listdir(os.path.join(o_banco, 'modelli_misura')):
            if not os.path.exists(os.path.join(d_banco, 'modelli_misura', f)):
                shutil.copy(os.path.join(o_banco, 'modelli_misura', f), os.path.join(d_banco, 'modelli_misura', f))
        print('riferimento e modelli di misura di %s copiati da IA33' % mondo, flush=True)
        ok = True
    if os.path.exists(os.path.join(CACHE33_ORIG, mondo, 'naturale.json')) and not os.path.exists(cart35(mondo, 'naturale.json')):
        os.makedirs(cart35(mondo), exist_ok=True)
        shutil.copy(os.path.join(CACHE33_ORIG, mondo, 'naturale.json'), cart35(mondo, 'naturale.json'))
    return ok


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
    dest = os.path.join(CACHE35, 'banco', mondo)
    os.makedirs(os.path.join(dest, 'modelli_misura'), exist_ok=True)
    rif_p = os.path.join(dest, 'riferimento.json')
    copia_da_ia33(mondo)
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
    os.makedirs(cart35(mondo), exist_ok=True)
    rif = costruisci_riferimento(mondo, processi)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    nat_p = cart35(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    mancano = [m for m in ('lam', 'bordi_fine', 'k90') if not rif['scala'].get(m)]
    if mancano and not SOLO_CONTROLLI:
        raise RuntimeError('il riferimento di %s non ha la scala di %s: servono per l obiettivo (S_GRU_MONDO26 almeno 2)' % (mondo, ', '.join(mancano)))
    if mancano:
        print('ATTENZIONE (prova): senza scala per %s: queste grandezze non entrano nell obiettivo' % ', '.join(mancano), flush=True)
    nm_p = cart35(mondo, 'nuove_misure.json')
    if not os.path.exists(nm_p):
        r = SL.lavoro_riferimento_NM8()
        json.dump(r, open(nm_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('mondo %s: riferimento con %d misure e %d giudici; otto misure di struttura; fogli addestramento/validazione/fuori %d/%d/%d' % (mondo, len(rif['vero']), len(rif['nullo']),
                                                                                                                          len(f_add), len(f_val), len(f_fuori)), flush=True)
    if addestra:
        esegui(mondo, [], [('addestra', n) for n in list(SR.VARIANTI) + ['A']], min(len(SR.VARIANTI) + 1, processi), fatte_di(mondo))
        sc = SR.scegli_variante(cart35(mondo))
        print('rete condizionata scelta sulla validazione: %s (batte l ablazione in validazione: %s)' % (sc['scelta'], sc['batte_ablazione_in_validazione']), flush=True)
    return rif


# ---------------------------------------------------------------- C: il ciclo

def valori_ia33(mondo):
    """Le manopole scelte da IA33 per il mondo (dizionario di 14) o None. Per il mondo `struttura` (che IA33 non aveva) il punto di IA33 del mondo `markov2`, il piu' vicino."""
    p = os.path.join(CACHE33_ORIG, 'vero' if mondo == 'vero' else 'markov2', 'ciclo_esito.json')
    if SOLO_CONTROLLI or not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding='utf-8'))['manopole_migliori']
    except (OSError, ValueError, KeyError):
        return None


def cubo_partenza(mondo):
    """Il cubo di partenza del ciclo: le manopole di IA33 (`PARTENZA35=ia33`, se ci sono); altrimenti il neutro."""
    v = valori_ia33(mondo) if PARTENZA == 'ia33' else None
    return OS.neutro_cubo33() if v is None else OS.cubo_da_valori(v)


def meta_fogli(mondo, gen, rep=0):
    ff = sorted({x['foglio'] for x in I7.libro_vero()})
    import random
    rnd = random.Random(seme_str('ia35mezzi', mondo, gen, rep))
    rnd.shuffle(ff)
    h = len(ff) // 2
    return sorted(ff[:h]), sorted(ff[h:])


def media_valutazioni(rs):
    """L'obiettivo di un candidato: somma dei z con tetto delle sue meta' / numero dei z (k90 e' solo in una meta'); piu' la penalita' media di copia."""
    ok = [r for r in rs if not r.get('errore')]
    if not ok:
        return None
    return float(sum(r['somma'] for r in ok) / sum(r['n'] for r in ok) + np.mean([r['penalita'] for r in ok]))


def fase_C(mondo, processi):
    attiva_main(mondo, [])
    st_p = cart35(mondo, 'ciclo.json')
    x0 = cubo_partenza(mondo)
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(st_p):
        stato = json.load(open(st_p, encoding='utf-8'))
        cma = CMA.CMA.da_stato(stato['cma'])
        storia = stato['storia']
    else:
        cma = CMA.CMA(x0, SIGMA0, LAMBDA, seme=seme_str('ia35cma', mondo))
        storia = []
    fatte = fatte_di(mondo)
    while cma.gen < GEN:
        g = cma.gen
        xs, _ = cma.ask()
        mA, mB = meta_fogli(mondo, g % NSPLIT)          # le divisioni dei fogli girano su NSPLIT35 (6): il vero degli stessi fogli (e k90 del vero) si calcola una volta per processo e per divisione
        lavori = []
        for i, u in enumerate(xs):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', g * 10 + h, i, list(map(float, u)), seme_str('ia35ciclo', mondo, g, i, h), fogli, h == 0, 'C'))
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
    # finalisti: nome -> (cubo, rete). Il punto di IA33 si rivaluta su entrambe le reti: la differenza e' l'effetto del condizionamento a manopole uguali.
    cand = OrderedDict()
    cand['neutro'] = (OS.neutro_cubo33(), 'C')
    if valori_ia33(mondo) is not None:
        cand['ia33_C'] = (x0, 'C')
        cand['ia33_A'] = (x0, 'A')
    cand['media_finale'] = (cma.mean, 'C')
    best_v, best_u = 1e9, None
    for h in storia:
        for u, v in zip(h['punti'], h['valori']):
            if v < best_v:
                best_v, best_u = v, np.array(u)
    cand['migliore_di_sempre'] = (best_u, 'C')
    cand['migliore_ultima'] = (np.array(storia[-1]['punti'][int(np.argmin(storia[-1]['valori']))]), 'C')
    lavori = []
    for r in range(RIV):
        mA, mB = meta_fogli(mondo, 1000 + r, r)
        for ci, (nome, (u, rete)) in enumerate(cand.items()):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', 9000 + r * 10 + h, ci, list(map(float, np.clip(u, 0, 1))), seme_str('ia35riv', mondo, r, ci, h), fogli, h == 0, rete))
    esegui(mondo, [], lavori, processi, fatte)
    tutti = [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('ciclo|9') and not c.get('errore')]
    fin = OrderedDict()
    for ci, nome in enumerate(cand):
        u, rete = cand[nome]
        rs = [c for c in tutti if c['i'] == ci and c['gen'] >= 9000]
        fin[nome] = OrderedDict([('rete', rete), ('obiettivo', media_valutazioni(rs)), ('n', len(rs)), ('u', list(map(float, np.clip(u, 0, 1)))),
                                 ('manopole', OS.da_cubo33(np.clip(u, 0, 1))),
                                 ('z', OrderedDict((m, float(np.mean([c['z'][m] for c in rs if m in c['z']]))) for m in SL.OBIETTIVO35 if any(m in c['z'] for c in rs)) if rs else None),
                                 ('copia_violazioni', OrderedDict((k, float(np.mean([c['copia_violazioni'].get(k, 0.0) for c in rs]))) for k in RM.SOGLIE_COPIA) if rs else None)])
    # si sceglie fra i finalisti sulla rete condizionata (quelli sulla ablazione sono un riferimento)
    scelto = min((n for n in fin if fin[n]['obiettivo'] is not None and fin[n]['rete'] == 'C'), key=lambda n: fin[n]['obiettivo'])
    ris = OrderedDict([('storia', storia), ('finalisti', fin), ('scelto', scelto), ('u_migliore', fin[scelto]['u']), ('manopole_migliori', fin[scelto]['manopole']),
                       ('u_partenza', list(map(float, x0))), ('partenza', 'ia33' if valori_ia33(mondo) is not None else 'neutro')])
    json.dump(ris, open(cart35(mondo, 'ciclo_esito.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('ciclo finito: scelto %s, obiettivo %.3f (neutro %.3f)' % (scelto, fin[scelto]['obiettivo'], fin['neutro']['obiettivo']), flush=True)
    return ris


# ---------------------------------------------------------------- E: l'esame

def insiemi_esame(mondo, ris_ciclo):
    """I libri dell'esame: nome -> dict(n, spec, gru (quanti libri con k90 e R_rel), gruppo, ruolo). spec = ['L', cubo, rete] | ['ORA', m] | ['GEMS']."""
    out = OrderedDict()
    neutro = list(map(float, OS.neutro_cubo33()))
    if 'L' in INSIEMI and ris_ciclo is not None:
        ub = list(map(float, ris_ciclo['u_migliore']))
        out['best'] = dict(n=N_ESAME, spec=['L', ub, 'C'], gru=N_GRU, gruppo='L', ruolo='IA35: migliore del ciclo sulla rete condizionata')
        out['bestA'] = dict(n=N_BESTA, spec=['L', ub, 'A'], gru=min(N_GRU, 4), gruppo='L', ruolo='lo stesso punto di manopole sulla rete senza condizionamento (ablazione)')
        out['neuC'] = dict(n=N_NEUTRO, spec=['L', neutro, 'C'], gru=N_NEUTRO, gruppo='L', ruolo='manopole neutre, rete condizionata')
        out['neuA'] = dict(n=N_NEUTRO, spec=['L', neutro, 'A'], gru=N_NEUTRO, gruppo='L', ruolo='manopole neutre, ablazione (validita\' del giudice b)')
        v = valori_ia33(mondo)
        if v is not None and N_IA33 > 0:
            u33 = list(map(float, OS.cubo_da_valori(v)))
            out['ia33C'] = dict(n=N_IA33, spec=['L', u33, 'C'], gru=min(N_GRU, 4), gruppo='L', ruolo='il punto di IA33 sulla rete condizionata')
            out['ia33A'] = dict(n=N_IA33, spec=['L', u33, 'A'], gru=min(N_GRU, 4), gruppo='L', ruolo='il punto di IA33 sulla rete senza condizionamento (IA33 riaddestrata)')
        rnd = np.random.default_rng(seme_str('ia35casuali', mondo))
        for c in range(1, N_CASUALI + 1):
            u = np.clip(np.array(neutro) + rnd.uniform(-0.45, 0.45, OS.DIM33), 0.0, 1.0)
            out['cas%d' % c] = dict(n=N_CAS_LIBRI, spec=['L', list(map(float, u)), 'C'], gru=0, gruppo='L', ruolo='manopole a caso (controllo negativo)')
    if mondo == 'struttura2' and 'O' in INSIEMI:
        out['orac'] = dict(n=N_ORACOLO, spec=['ORA', 1], gru=N_GRU, gruppo='O', ruolo="l'oracolo stimato del mondo struttura2 (regola nota, frequenze dai 78 fogli)")
        out['orac2'] = dict(n=N_ORACOLO_PIU, spec=['ORA', 2], gru=0, gruppo='O', ruolo="l'oracolo con il doppio del testo")
        out['gem'] = dict(n=N_GEM, spec=['GEMS'], gru=N_GRU, gruppo='O', ruolo='il gemello (la vera regola, semi nuovi): il pavimento')
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
    p_ciclo = cart35(mondo, 'ciclo_esito.json')
    ris_ciclo = json.load(open(p_ciclo, encoding='utf-8')) if os.path.exists(p_ciclo) else None
    ins = insiemi_esame(mondo, ris_ciclo)
    attiva_main(mondo, [])
    v21 = v21_disponibili() if mondo == 'vero' and 'L' in INSIEMI else []
    nomi = [nome_libro(t, i) for t, d in ins.items() for i in range(1, d['n'] + 1)] + v21
    attiva_main(mondo, nomi)
    fatte = fatte_di(mondo)
    libri = [('libro35', t, i, d['spec'], seme_str('ia35esame', mondo, t, i)) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    print('== esame %s: %d libri da scrivere' % (mondo, len(libri)), flush=True)
    esegui(mondo, nomi, libri, processi, fatte)
    lavori = [('M', n) for n in nomi] + [('J32', n) for n in nomi] + [('NM', n) for n in nomi]
    lavori += [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    if GRU:
        for t, d in ins.items():
            for i in range(1, min(d['gru'], d['n']) + 1):
                lavori += [('G', tp, nome_libro(t, i), 1) for tp in ('K', 'R')]
        for n in v21[:4]:
            lavori += [('G', tp, n, 1) for tp in ('K', 'R')]
    lavori = sorted(lavori, key=lambda a: {'G': 0, 'D': 1, 'K': 2, 'KN': 2, 'J32': 3, 'M': 4, 'NM': 4}.get(a[0], 5))
    # il giudice b mediato: un lavoro per insieme (processi diversi)
    gruppi = [(t, [nome_libro(t, i) for i in range(1, d['n'] + 1)]) for t, d in ins.items()] + ([('v21', v21)] if v21 else [])
    lavori = [('B35', t, ns, seme_str('b35', mondo, t) % 1000) for t, ns in gruppi] + lavori
    print('== esame %s: %d lavori del banco' % (mondo, len(lavori)), flush=True)
    esegui(mondo, nomi, lavori, processi, fatte)
    return analisi_esame(mondo, ins, nomi, v21)


def libri_rows(nomi):
    return [B.rows_testo(n) for n in nomi]


def analisi_esame(mondo, ins, nomi, v21):
    attiva_main(mondo, nomi)
    c = I7.contesto_A()
    rif = json.load(open(B.dir_mondo('riferimento.json'), encoding='utf-8'))
    nm_rif = json.load(open(cart35(mondo, 'nuove_misure.json'), encoding='utf-8'))
    corse = leggi_corse(percorso_corse(mondo))
    C = B.indice_corse(corse)
    nm = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('NM|') and not r.get('errore')}
    giudice_b = OrderedDict((r['lavoro'][4:], r) for r in corse if str(r.get('lavoro', '')).startswith('B35|') and not r.get('errore'))
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    n_pag = len(c['ids'])
    prof = OrderedDict((n, RM.valori_libro(n, C, pK, pKN, n_pag)) for n in nomi)
    corse_libro = {r['lavoro']: r for r in corse if str(r.get('lavoro', '')).startswith('libro|') and not r.get('errore')}
    return dict(rif=rif, nm_rif=nm_rif, nm=nm, prof=prof, giudice_b=giudice_b, ins=ins, nomi=nomi, v21=v21, corse_libro=corse_libro, n_pag=n_pag)


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def riassunto_insieme(mondo, A, tipo):
    """Per un insieme di libri: AUC dei tre giudici mai visti (media, deviazione standard fra libri, errore), giudici di allenamento, misure tenute fuori (D, R_rel e le sei nuove), copia."""
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
    for m in SL.FUORI_MISURE35:
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
    """La lettura dell'oracolo del mondo `struttura` (stessa regola di IA33). `R` = riassunti per insieme. -> dict."""
    if 'orac' not in R:
        return None
    o, g = R['orac']['giudici_mai_visti'], R['gem']['giudici_mai_visti'] if 'gem' in R else None
    out = OrderedDict()

    def fuori(x, e=0.0):
        return bool(x is not None and (x - e > AUC_MAX or x + e < 1 - AUC_MAX))
    out['oracolo'] = OrderedDict((j, OrderedDict([('media', o[j]['media']), ('errore', o[j]['errore']), ('sopra_0_60', bool(o[j]['media'] is not None and o[j]['media'] > AUC_MAX)),
                                                  ('sotto_0_40', bool(o[j]['media'] is not None and o[j]['media'] < 1 - AUC_MAX)), ('riconosciuto', fuori(o[j]['media'])),
                                                  ('riconosciuto_netto', fuori(o[j]['media'], N_ERRORI * o[j]['errore']))])) for j in GIUDICI3)
    out['gemello_ok'] = bool(g is not None and all(g[j]['media'] is not None and (1 - AUC_MAX) <= g[j]['media'] <= AUC_MAX for j in GIUDICI3)) if g else None
    b_neu = (R.get('neuC') or {}).get('giudici_mai_visti', {}).get('b', {}).get('media')
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
    tr = OrderedDict()
    for nome, mult in (('orac', 1), ('orac2', 2)):
        if nome in R:
            tr[mult] = OrderedDict((j, R[nome]['giudici_mai_visti'][j]['media']) for j in GIUDICI3)
    out['andamento_con_il_testo'] = tr
    # misure tenute fuori dell'oracolo e del gemello (struttura: la regola nota le riproduce?)
    out['misure_fuori_oracolo'] = R['orac']['misure_fuori']
    out['misure_fuori_gemello'] = R['gem']['misure_fuori'] if 'gem' in R else None
    return out


def esito_L(mondo, R, v21, O):
    """L'esito della parte L per il mondo: riuscito assoluto, al livello dell'oracolo (di `struttura`), batte il riferimento (v21 nel mondo `vero`, il `best` di IA33 nel mondo `struttura`), non riuscito, non valido."""
    if 'best' not in R:
        return None
    best, neu = R['best'], R.get('neuC')
    jb = best['giudici_mai_visti']
    b_neu = neu['giudici_mai_visti']['b']['media'] if neu else None
    valido = bool(b_neu is not None and b_neu >= RGB.AUC_NEUTRO_MIN)
    qmin = QUOTA_ENTRO_2S
    if mondo == 'struttura2' and R.get('gem') and R['gem']['quota_entro_2sigma'] is not None:
        qmin = min(QUOTA_ENTRO_2S, R['gem']['quota_entro_2sigma'])          # nel mondo di regola nota la quota non puo' chiedere piu' di quanto ottiene il gemello (la vera regola)
    quota_ok = bool(best['quota_entro_2sigma'] is not None and best['quota_entro_2sigma'] >= qmin - 1e-9)
    out = OrderedDict([('giudice_b_valido', valido), ('giudice_b_neutro', b_neu), ('giudici_mai_visti', jb), ('quota_entro_2sigma', best['quota_entro_2sigma']), ('quota_richiesta', qmin),
                       ('misure_fuori', best['misure_fuori']), ('copia_ok', best['copia_ok'])])
    livello = None
    if O is not None and O['verdetto'] == 'irraggiungibile':
        det = OrderedDict()
        for j in GIUDICI3:
            e = math.sqrt(jb[j]['errore'] ** 2 + O['oracolo'][j]['errore'] ** 2)
            lim = abs(O['oracolo'][j]['media'] - 0.5) + max(N_ERRORI * e, MARGINE_AUC)
            det[j] = OrderedDict([('AUC', jb[j]['media']), ('distanza_da_0_5', abs(jb[j]['media'] - 0.5) if jb[j]['media'] is not None else None), ('limite_distanza', lim),
                                  ('dentro', bool(jb[j]['media'] is not None and abs(jb[j]['media'] - 0.5) <= lim))])
        livello = OrderedDict([('dettaglio', det), ('giudici_dentro', bool(all(x['dentro'] for x in det.values())))])
    out['al_livello_dell_oracolo'] = livello
    if v21 is not None:
        base, nome = v21, 'v21'
    elif R.get('ia33A'):
        base, nome = R['ia33A']['giudici_mai_visti'], 'IA33 sulla rete senza condizionamento'
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
    # lettura descrittiva: quanto si perde sui giudici e quanto si guadagna sulla struttura rispetto a IA33 (stesso esame)
    conf = None
    if R.get('ia33A'):
        k = R['ia33A']
        cj = OrderedDict((j, OrderedDict([('ia35', jb[j]['media']), ('ia33', k['giudici_mai_visti'][j]['media']),
                                          ('differenza_distanza_da_0_5', (abs(jb[j]['media'] - 0.5) - abs(k['giudici_mai_visti'][j]['media'] - 0.5)) if jb[j]['media'] is not None and k['giudici_mai_visti'][j]['media'] is not None else None)])) for j in GIUDICI3)
        cm = OrderedDict()
        for m in sorted(set(best['misure_tenute_fuori']) | set(k['misure_tenute_fuori'])):
            a, b2 = best['misure_tenute_fuori'].get(m), k['misure_tenute_fuori'].get(m)
            cm[m] = OrderedDict([('z_ia35', a['z'] if a else None), ('z_ia33', b2['z'] if b2 else None)])
        ca = OrderedDict()
        for m in sorted(set(best['misure_di_allenamento']) | set(k['misure_di_allenamento'])):
            a, b2 = best['misure_di_allenamento'].get(m), k['misure_di_allenamento'].get(m)
            ca[m] = OrderedDict([('z_ia35', a['z_sigma'] if a else None), ('z_ia33', b2['z_sigma'] if b2 else None)])
        conf = OrderedDict([('giudici', cj), ('misure_tenute_fuori', cm), ('misure_di_allenamento', ca), ('quota_entro_2sigma', OrderedDict([('ia35', best['quota_entro_2sigma']), ('ia33', k['quota_entro_2sigma'])]))])
    out['confronto_con_ia33'] = conf
    cas = OrderedDict()
    for t, r in R.items():
        if t.startswith('cas'):
            sup = bool(r['giudici_ok'] and r['quota_entro_2sigma'] is not None and r['quota_entro_2sigma'] >= QUOTA_ENTRO_2S and r['copia_ok'])
            cas[t] = OrderedDict([('giudici', OrderedDict((j, r['giudici_mai_visti'][j]['media']) for j in GIUDICI3)), ('quota_entro_2sigma', r['quota_entro_2sigma']), ('supera', sup)])
    out['casuali'] = cas
    out['controllo_negativo_riuscito'] = bool(cas) and not any(x['supera'] for x in cas.values())
    return out


# ---------------------------------------------------------------- S: sintesi

def mf(x, d=3):
    return 'n.d.' if x is None else ('%.*f' % (d, x))


def lettura_condizionamento(mondo, R, ppl):
    """Che cosa porta il condizionamento: rete condizionata contro ablazione, a manopole uguali (best, ia33, neutro), sui giudici e sulle misure; `ppl`: perplessita' delle due reti."""
    out = OrderedDict([('perplessita', ppl)])
    coppie = OrderedDict([('best', ('best', 'bestA')), ('ia33', ('ia33C', 'ia33A')), ('neutro', ('neuC', 'neuA'))])
    for nome, (c, a) in coppie.items():
        if c not in R or a not in R:
            continue
        rc, ra = R[c], R[a]
        gi = OrderedDict((j, OrderedDict([('condizionata', rc['giudici_mai_visti'][j]['media']), ('ablazione', ra['giudici_mai_visti'][j]['media']),
                                          ('errore_differenza', math.sqrt(rc['giudici_mai_visti'][j]['errore'] ** 2 + ra['giudici_mai_visti'][j]['errore'] ** 2))])) for j in GIUDICI3)
        ms = OrderedDict()
        for m in sorted(set(rc['misure_tenute_fuori']) | set(ra['misure_tenute_fuori'])):
            x, y = rc['misure_tenute_fuori'].get(m), ra['misure_tenute_fuori'].get(m)
            ms[m] = OrderedDict([('z_condizionata', x['z'] if x else None), ('z_ablazione', y['z'] if y else None)])
        al = OrderedDict()
        for m in sorted(set(rc['misure_di_allenamento']) | set(ra['misure_di_allenamento'])):
            x, y = rc['misure_di_allenamento'].get(m), ra['misure_di_allenamento'].get(m)
            al[m] = OrderedDict([('z_condizionata', x['z_sigma'] if x else None), ('z_ablazione', y['z_sigma'] if y else None)])
        out[nome] = OrderedDict([('giudici', gi), ('misure_tenute_fuori', ms), ('misure_di_allenamento', al), ('quota_entro_2sigma', OrderedDict([('condizionata', rc['quota_entro_2sigma']), ('ablazione', ra['quota_entro_2sigma'])]))])
    # le due misure sul vocabolario di sezione e sull'inizio dei paragrafi: la domanda dell'idea
    out['misure_chiave'] = OrderedDict((m, OrderedDict((t, (R[t]['misure_tenute_fuori'].get(m) or {}).get('z')) for t in R if not t.startswith('cas'))) for m in ('sezione', 'ini_par'))
    return out


def fase_S(mondi, sintesi):
    os.makedirs(USCITA, exist_ok=True)
    ins_s = (sintesi.get('struttura2') or {}).get('insiemi')
    if not ins_s and os.path.exists(cart35('struttura2', 'esame.json')):
        ins_s = json.load(open(cart35('struttura2', 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict).get('insiemi')
    O = lettura_O(ins_s) if ins_s else None
    for mondo, s in sintesi.items():
        R = s.get('insiemi')
        if not R:
            continue
        s['esito_L'] = esito_L(mondo, R, s.get('v21'), O)
        ppl = OrderedDict()
        for rete in ('C', 'A'):
            pj = cart35(mondo, 'rete_' + rete, 'pieno.json')
            if os.path.exists(pj):
                d = json.load(open(pj, encoding='utf-8'))
                ppl[rete] = OrderedDict((k, d.get(k)) for k in ('epoca_A', 'epoche_totali', 'bpc_val_A', 'bpc_val_C', 'bpc_fuori_A', 'bpc_fuori_C', 'bpc_add_C', 'parametri'))
        s['condizionamento'] = lettura_condizionamento(mondo, R, ppl)
        sr = cart35(mondo, 'scelta_rete.json')
        s['condizionamento']['scelta_rete'] = json.load(open(sr, encoding='utf-8'), object_pairs_hook=OrderedDict) if os.path.exists(sr) else None
    out = OrderedDict([('esperimento', NOME), ('lettura_oracolo_struttura', O), ('mondi', sintesi)])
    json.dump(out, open(os.path.join(USCITA, 'ia35_sezione.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ['# IA35 (ia35) — La rete che sa dove scrive', '', 'Preregistrazione: `preregistrazioni/ia35.md`. Solo numeri e aggregati.', '']
    if O:
        md += ["## Oracolo del mondo `struttura2`", '', '**Verdetto: %s** (pavimento valido: %s; giudice b valido: %s). Giudici che lo riconoscono (fuori 0,40-0,60): %s. Misure tenute fuori che l\'oracolo non rifa: %s; il gemello: %s.' % (
            O['verdetto'], O['gemello_ok'], O['giudice_b_valido'], ', '.join(O['giudici_oltre_0_60']) or 'nessuno', ', '.join(O['misure_fuori_oracolo']) or 'nessuna',
            ', '.join(O['misure_fuori_gemello'] or []) or 'nessuna'), '']
        md += ['| giudice | oracolo | errore | riconosciuto | netto (2 errori) |', '|---|---|---|---|---|']
        for j in GIUDICI3:
            x = O['oracolo'][j]
            md.append('| %s | %s | %s | %s | %s |' % (j, mf(x['media']), mf(x['errore']), 'si' if x['riconosciuto'] else 'no', 'si' if x['riconosciuto_netto'] else 'no'))
        md += ['', '| testo (volte) | ' + ' | '.join(GIUDICI3) + ' |', '|---|---|---|---|']
        for m, v in O['andamento_con_il_testo'].items():
            md.append('| %s | %s |' % (m, ' | '.join(mf(v[j]) for j in GIUDICI3)))
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
            md += ['', '| finalista | obiettivo rivalutato | ' + ' | '.join(PL.OBIETTIVO34) + ' |', '|---|---|' + '---|' * len(PL.OBIETTIVO34)]
            for n, x in c['finalisti'].items():
                md.append('| %s | %s | %s |' % (n, mf(x['obiettivo']), ' | '.join(mf((x['z'] or {}).get(m), 1) for m in PL.OBIETTIVO34)))
            md += ['', '| manopola | valore scelto | neutro | partenza |', '|---|---|---|---|']
            xp = OS.da_cubo33(c['u_partenza']) if c.get('u_partenza') else {}
            for k, v in c['manopole_migliori'].items():
                md.append('| %s | %s | %s | %s |' % (k, mf(v), mf(OS.NEUTRO33[k]), mf(xp.get(k))))
            md.append('')
        R = s.get('insiemi')
        if R:
            md += ['| insieme | libri | ' + ' | '.join(GIUDICI3) + ' | quota entro 2 sigma | misure fuori | copia |', '|---|---|---|---|---|---|---|---|']
            for t, r in R.items():
                md.append('| %s | %d | %s | %s | %s | %s |' % (t, r['n'], ' | '.join('%s (%s)' % (mf(r['giudici_mai_visti'][j]['media']), mf(r['giudici_mai_visti'][j]['errore'], 3)) for j in GIUDICI3),
                                                         mf(r['quota_entro_2sigma'], 2), ', '.join(r['misure_fuori']) or '-', 'ok' if r['copia_ok'] else 'superata'))
            if s.get('v21'):
                md.append('| v21 | %d | %s | | | | |' % (len(s.get('v21_libri') or []), ' | '.join('%s (%s)' % (mf(s['v21'][j]['media']), mf(s['v21'][j]['errore'], 3)) for j in GIUDICI3)))
            md.append('')
            for t in ('best', 'bestA', 'ia33C', 'ia33A', 'neuC', 'neuA'):
                if t in R:
                    md += ['Misure tenute fuori, `%s` (z in sigma): ' % t + ', '.join('%s %s' % (m, mf(x['z'], 1)) for m, x in R[t]['misure_tenute_fuori'].items()), '']
        e = s.get('esito_L')
        if e:
            md += ["**Esito: %s** (giudice b valido: %s; controllo negativo riuscito: %s)." % (e['esito'], e['giudice_b_valido'], e['controllo_negativo_riuscito']), '']
            if e['esito'] in ('non riuscito', 'non valido'):
                md += ['Resta fuori: giudici oltre 0,60: %s; misure fuori 2 sigma: %s; copia superata: %s.' % (', '.join(e['resta_fuori']['giudici_oltre_0_60']) or 'nessuno',
                                                                  ', '.join(e['resta_fuori']['misure_fuori_2sigma']) or 'nessuna', e['resta_fuori']['copia_superata']), '']
    md += ['## Che cosa porta il condizionamento (rete condizionata contro ablazione)', '']
    for mondo, s in sintesi.items():
        c = s.get('condizionamento')
        if not c:
            continue
        sr = c.get('scelta_rete')
        if sr:
            md += ['Mondo `%s`: scelta della rete condizionata sulla validazione (bit per segno, validazione / fuori piega): ' % mondo + '; '.join(
                '%s %s / %s' % (n, mf(x['bpc_val_A']), mf(x['bpc_fuori_A'])) for n, x in sr['varianti'].items()) + '; ablazione %s / %s; scelta: %s; batte l ablazione in validazione: %s' % (
                mf((sr['ablazione'] or {}).get('bpc_val_A')), mf((sr['ablazione'] or {}).get('bpc_fuori_A')), sr['scelta'], 'si' if sr['batte_ablazione_in_validazione'] else 'NO'), '']
        md += ['Mondo `%s`: perplessita` (bit per segno) ' % mondo + '; '.join('%s: validazione %s, fuori piega %s' % (r, mf((x or {}).get('bpc_val_C')), mf((x or {}).get('bpc_fuori_C'))) for r, x in c['perplessita'].items()), '']
        for nome in ('best', 'ia33', 'neutro'):
            if nome in c:
                md += ['A manopole `%s`: giudici (condizionata / ablazione) ' % nome + ', '.join('%s %s / %s' % (j, mf(x['condizionata']), mf(x['ablazione'])) for j, x in c[nome]['giudici'].items()) +
                       '; misure tenute fuori z: ' + ', '.join('%s %s / %s' % (m, mf(x['z_condizionata'], 1), mf(x['z_ablazione'], 1)) for m, x in c[nome]['misure_tenute_fuori'].items()), '']
    open(os.path.join(USCITA, 'ia35_sezione.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


def main():
    import numpy
    import torch
    print('ia35: mondi %s, insiemi %s, libro (%s)' % (MONDI35, INSIEMI, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich'), flush=True)
    os.makedirs(CACHE35, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    processi = int(os.environ.get('PROCESSI', 3))
    fasi = os.environ.get('FASI', 'PCES')
    if len(MONDI35) > 1 and os.environ.get('IA35_FIGLIO') != '1':
        # un processo nuovo per ogni mondo (il testo del mondo si costruisce una volta sola per processo); la sintesi poi legge i file
        import subprocess
        senza_s = ''.join(ch for ch in fasi if ch != 'S')
        for mondo in MONDI35:
            if senza_s:
                rc = subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, MONDI35=str(MONDI_ELENCO.index(mondo) + 1), FASI=senza_s, IA35_FIGLIO='1'))
                if rc != 0:
                    sys.exit(rc)
        if 'S' in fasi:
            sys.exit(subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, FASI='S', IA35_FIGLIO='1')))
        return
    sintesi = OrderedDict()
    for mondo in MONDI35:
        if os.environ.get('RIPRENDI') != '1' and 'P' in fasi:
            azzera_corse(mondo)
        s = OrderedDict()
        if 'P' in fasi:
            fase_P(mondo, processi, addestra='L' in INSIEMI)
        if 'C' in fasi and 'L' in INSIEMI:
            s['ciclo'] = fase_C(mondo, processi)
        elif os.path.exists(cart35(mondo, 'ciclo_esito.json')):
            s['ciclo'] = json.load(open(cart35(mondo, 'ciclo_esito.json'), encoding='utf-8'))
        if 'E' in fasi:
            A = fase_E(mondo, processi)
            s['insiemi'] = OrderedDict((t, riassunto_insieme(mondo, A, t)) for t in A['ins'])
            s['v21'] = riassunto_v21(A)
            s['v21_libri'] = A['v21']
            s['giudice_b'] = A['giudice_b']
            json.dump(OrderedDict((k, s[k]) for k in ('insiemi', 'v21', 'v21_libri', 'giudice_b')), open(cart35(mondo, 'esame.json'), 'w', encoding='utf-8', newline='\n'),
                      ensure_ascii=False, indent=1, default=float)
        elif 'S' in fasi and os.path.exists(cart35(mondo, 'esame.json')):
            s.update(json.load(open(cart35(mondo, 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict))
        sintesi[mondo] = s
    if 'S' in fasi:
        fase_S(MONDI35, sintesi)


if __name__ == '__main__':
    main()
