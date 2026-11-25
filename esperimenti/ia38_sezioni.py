# -*- coding: utf-8 -*-
"""Esperimento IA38 (ia38): chiedere all'IA i giudici e le sezioni insieme.

Domanda (seguito di IA37): in IA37 la divergenza fra sezioni (bit, bigrammi di glifi / parole) e': Voynich vero 0,068 / 0,208; rete con manopole neutre 0,063 / 0,201; punti scelti dal ciclo in IA35-IA37
0,043-0,050 / 0,112-0,126. Le correzioni che portano i giudici al livello dell'oracolo tagliano circa il 40% della differenza fra sezioni; il ciclo non la vede e spegne `a_sez` sul Voynich. Se il ciclo
VEDE anche la differenza fra sezioni, trova un punto che la tiene E tiene i giudici al livello dell'oracolo? O e' un compromesso vero di questo imitatore?
L'unica novita': nell'obiettivo del ciclo entrano due grandezze, `div_bigr` e `div_par` (divergenza fra sezioni dei bigrammi di glifi e delle parole, come in IA37, z contro il vero e min(|z|, 10) come le altre),
con riferimento sui SOLI fogli d'addestramento. Tutto il resto come IA37: rete `Cb` di IA35 dalla cache, conteggi per sezione con `a_sez` nel ciclo (stesso K scelto sulla validazione), scelta prudente di IA36 con le
stesse soglie, `riuso_sez` nell'obiettivo, memoria di sezione spenta, esame identico. La misura d'esame `sezione` diventa in parte insegnata (tocca la stessa materia): dichiarato, e nelle letture e' separata dalle altre nove.
Lettura nuova, descrittiva: la curva del compromesso (frontiera fra la parte "giudici" e la parte "sezioni" dell'obiettivo) sulle valutazioni del ciclo.
Preregistrazione: preregistrazioni/ia38.md. Moduli di supporto (prefisso `sezobi_`): sezobi_misure (differenza fra sezioni come grandezza dell'obiettivo, riferimento sui fogli d'addestramento), sezobi_lavori
(la valutazione del ciclo con le due grandezze nuove), sezobi_prove (prove di unita'); e quelli di IA37 (`freqsez_*`), IA36 (`prudente_*`), IA35 (`sezione_*`), IA34 (`piano_*`), IA33 (`oracolo_*`), IA32 (`rifare_*`)
e il banco di IA26, importati senza modificarli.

Fasi (variabile FASI, predefinita PCES), per ogni mondo di MONDI38 (1 = struttura2, controllo positivo e oracolo; 2 = il libro vero), **un processo figlio per mondo**:
  P  preparazione: dalla cache di IA37 si copiano rete condizionata, riferimento, modelli di misura, "naturale", otto misure di struttura, guardie, ripiego K e divergenza del vero; si calcola il riferimento
     della differenza fra sezioni sui soli fogli d'addestramento
  C  partenza prudente (punto di IA37, IA35, IA33, neutro), ciclo (CMA-ES, 15 manopole, obiettivo a 15 grandezze: le 13 di IA37 piu' div_bigr e div_par; penalita' di guardia), scelta prudente fra i finalisti,
     curva del compromesso
  E  l'esame: libri di tutti gli insiemi, giudici mai visti (b mediato su 8 divisioni), dieci misure tenute fuori, guardie, divergenza fra sezioni, criteri, letture
  S  sintesi -> risultati/ia38_sezioni.json e .md, e i grafici ia38_compromesso_<mondo>.png (solo numeri)

    nohup bash strumenti/coda.sh ia38 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia38" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO32=1 USCITA=<cartella nel repo> CACHE38=<cartella nel repo> python esperimenti/ia38_sezioni.py     (prova sul libro latino)

Variabili nuove (valori senza virgole e senza due punti): MONDI38 (cifre: 1 struttura2, 2 vero; predefinito 12), CACHE38, LAMBDA38 (12), GEN38 (10), NSPLIT38 (6), SIGMA38 (0,25), RIV38 (3), RIV0_38 (2),
RIV_G38 (2), N_ESAME38 (16), N_NEUTRO38 (4), N_IA33_38 (8), N_IA35_38 (8), N_IA37_38 (8), N_CASUALI38 (3), N_CAS_LIBRI38 (4), N_ORACOLO38 (16), N_ORACOLO_PIU38 (8), N_GEM38 (16), N_GRU38 (8),
GRU38 (1), K90_38 (1), INSIEMI38 (L, O; predefinito LO), PARTENZA38 (ia37 o neutro o stress: stress e' solo per il mondo di sviluppo), FORZA_PARTENZA38 (solo prove), PESO_SEZ38 (1: peso di ciascuna delle due
grandezze nuove; 0 = nessuna, identico a IA37). Valgono ancora quelle di IA36 per la scelta prudente (ZG_ABS36, DELTA_G36, ZG_TETTO36, W_G36, PEN_MAX36, ZCAP_G36, PRUDENTE36, RIUSO_OBIETTIVO38), quelle di
IA32-IA35 (KAPPA33, RIP_B35, PERM_B35, ...) e di IA26.
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

NOME = 'ia38_sezioni'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE38 = os.environ.get('CACHE38', os.path.join(USCITA, 'ia38_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia38'))
CACHE35_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia35')
CACHE37_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia37')
CACHE33_ORIG = os.path.join(QUI, '..', 'dati', 'cache', 'ia33')
os.environ['CACHE26'] = os.path.join(CACHE38, 'banco')          # il banco di IA26 scrive qui, mai nella cache di IA26, IA32 ne' IA35
os.environ.setdefault('CHUNK26', '500')                         # un solo gruppo di testi per i lavori K, KN e D
os.environ.setdefault('S_GRU_MONDO26', '6')
import righello_banco as B  # noqa: E402
import righello_testi as RT  # noqa: E402
import rifare_dati as RD  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_cma as CMA  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_giudice as RGB  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import piano_lavori as PL  # noqa: E402
import sezione_mondo as SMO  # noqa: E402
import sezione_misure as SM  # noqa: E402
import sezione_rete as SR  # noqa: E402
import sezione_lavori as SL  # noqa: E402
import prudente_misure as PMG  # noqa: E402
import prudente_scelta as PSC  # noqa: E402
import prudente_scrittura as PW  # noqa: E402
import prudente_lavori as PLV  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402
import freqsez_scrittura as FW  # noqa: E402
import sezobi_misure as SO  # noqa: E402
import sezobi_lavori as SOL  # noqa: E402
import freqsez_lavori as FL  # noqa: E402   (sostituisce lo scrittore di `prudente_lavori` con quello a frequenze per sezione)
if os.environ.get('SOLO_CONTROLLI') == '1':
    import prudente_mondo  # noqa: E402,F401   (il mondo di sviluppo `struttura3`: solo prove)

NEUTRO37 = FW.da_cubo37(FW.neutro_cubo37())
MONDI_ELENCO = ['struttura2', 'vero', 'struttura3']                 # `struttura3` (3): mondo di sviluppo, solo con SOLO_CONTROLLI=1
MONDI38 = [MONDI_ELENCO[int(x) - 1] for x in os.environ.get('MONDI38', '12') if x.isdigit() and 1 <= int(x) <= (3 if SOLO_CONTROLLI else 2)]
LAMBDA = int(os.environ.get('LAMBDA38', 12))
GEN = int(os.environ.get('GEN38', 10))
SIGMA0 = float(os.environ.get('SIGMA38', 0.25))
RIV = int(os.environ.get('RIV38', 3))
RIV0 = int(os.environ.get('RIV0_38', 2))
RIV_G = int(os.environ.get('RIV_G38', 2))                      # libri interi per finalista nel controllo di guardia
N_ESAME = int(os.environ.get('N_ESAME38', 16))
N_NEUTRO = int(os.environ.get('N_NEUTRO38', 4))
N_IA33 = int(os.environ.get('N_IA33_38', 8))
N_IA35 = int(os.environ.get('N_IA35_38', 8))
N_IA37 = int(os.environ.get('N_IA37_38', 8))
N_CASUALI = int(os.environ.get('N_CASUALI38', 3))
N_CAS_LIBRI = int(os.environ.get('N_CAS_LIBRI38', 4))
N_ORACOLO = int(os.environ.get('N_ORACOLO38', 16))
N_ORACOLO_PIU = int(os.environ.get('N_ORACOLO_PIU38', 8))
N_GEM = int(os.environ.get('N_GEM38', 16))
N_GRU = int(os.environ.get('N_GRU38', 8))
GRU = os.environ.get('GRU38', '1') == '1'
K90 = os.environ.get('K90_38', '1') == '1'                     # solo prove di sviluppo: 0 salta il calcolo di k90 nei mezzi libri (senza scala k90 non entra comunque nell'obiettivo)
INSIEMI = os.environ.get('INSIEMI38', 'LO')
PARTENZA = os.environ.get('PARTENZA38', 'ia37')
PIEGHE = I7.PIEGHE
NSPLIT = int(os.environ.get('NSPLIT38', 6))
OBIETTIVO38 = SOL.OBIETTIVO38
GUARDIE36 = PMG.GUARDIE36

# ---- criteri (scritti nella preregistrazione prima di ogni corsa sul Voynich; come IA35)
AUC_MAX = 0.60                     # giudici mai visti: al massimo cosi' (e almeno 1 - AUC_MAX)
QUOTA_ENTRO_2S = 0.80              # almeno l'80% delle misure tenute fuori entro 2 sigma del vero
SIGMA_DA_SCALA = 1.0 / math.sqrt(2.0)
MARGINE_AUC = 0.05                 # "al livello dell'oracolo": AUC <= oracolo + max(2 errori, 0,05)
N_ERRORI = 2.0
V21_NOMI = ['V21:%d' % k for k in range(13, 23)]
GIUDICI3 = ('N', 'KN', 'b')
# punto di STRESS del solo mondo di sviluppo (PARTENZA38=stress): un punto estremo scritto a mano (non viene da nessun risultato), per provare che la protezione lo riconosce
VALORI_STRESS = OrderedDict([('T_eol', 0.7), ('T_riga', 0.7), ('w_cont', 5.0), ('w_tri', 5.0), ('w_quad', 5.0), ('s', 1.0), ('w_uni', 2.0), ('w_bi', 1.5), ('b_nuove', -1.5), ('w_pag', 0.6)])


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def cart38(mondo, *p):
    return os.path.join(CACHE38, mondo, *p)


def percorso_corse(mondo):
    return os.path.join(USCITA, 'ia38_corse_%s.jsonl' % mondo)


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
    RM.prepara(mondo, cart38(mondo), nomi)
    PLV.carica_guardie()
    SOL.carica_div()


def lavoro36(args):
    if args[0] == 'addestra':
        t = time.time()
        try:                                                # solo se la rete di IA35 non c'e' (prove di sviluppo): variante `Cb`
            ris = SR.addestra_pieno35(cart38(RM._W['mondo'], 'rete_C'), cond=True, var=SR.VARIANTI['Cb'], messaggi=lambda s: print('[addestra %s] %s' % (RM._W['mondo'], s), flush=True))
            ris = OrderedDict((a, v) for a, v in ris.items() if not a.startswith('curva'))
            ris['lavoro'] = 'addestra|C'
            ris['secondi'] = round(time.time() - t, 1)
            return ris
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'addestra|C'), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    r = SOL.lavoro_banco38(args)
    for k in ('pesanti_e231', 'pesanti_e266'):
        r.pop(k, None)
    return r


def ident(a):
    if a[0] == 'B35':
        return 'B35|%s' % a[1]
    if a[0] == 'libro36':
        return 'libro|%s|%s' % (a[1], a[2])
    if a[0] == 'valuta':
        return 'ciclo|%d|%d' % (a[1], a[2])
    if a[0] == 'GI':
        return 'GI|%s|%d' % (a[1], a[2])
    return '|'.join(str(x) for x in a)


def esegui(mondo, nomi, lavori, processi, fatte, scrivi=True):
    """Fa girare i lavori in un gruppo di processi che hanno preparato il mondo. Una riga per lavoro in ia38_corse_<mondo>.jsonl. -> lista dei risultati."""
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if ident(a) not in fatte and (not filtro or any(x in ident(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia, initargs=(mondo, nomi)) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro36, da_fare), 1):
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
    """Attiva il mondo nel processo principale UNA volta sola (come in IA35: un solo mondo per processo, gli altri in un processo figlio)."""
    if _ATTIVO.get('mondo') == mondo:
        B._S['nomi'] = [n for n in nomi if n != 'vero']
        return B._S
    if _ATTIVO:
        raise RuntimeError('un solo mondo per processo: %s e poi %s' % (_ATTIVO['mondo'], mondo))
    _ATTIVO['mondo'] = mondo
    return B.imposta_mondo(mondo, list(nomi))


def copia_da_ia37(mondo):
    """Dalla cache di IA37 (solo corsa vera; sono le stesse cose di IA35 e IA36): la rete condizionata `rete_C`, il riferimento e i modelli di misura del banco, il riferimento "naturale", le otto misure di struttura,
    il riferimento delle guardie, il ripiego K (scelto sulla validazione in IA37: stesso K) e la divergenza fra sezioni del vero. NON si copiano `libri`, `misure` (profili K e KN dei libri di IA37) ne' i risultati.
    -> True se ha copiato qualcosa."""
    if SOLO_CONTROLLI:
        return False
    ok = False
    o_banco = os.path.join(CACHE37_ORIG, 'banco', mondo)
    d_banco = os.path.join(CACHE38, 'banco', mondo)
    if os.path.exists(os.path.join(o_banco, 'riferimento.json')) and not os.path.exists(os.path.join(d_banco, 'riferimento.json')):
        os.makedirs(os.path.join(d_banco, 'modelli_misura'), exist_ok=True)
        for f in os.listdir(os.path.join(o_banco, 'modelli_misura')):
            if not os.path.exists(os.path.join(d_banco, 'modelli_misura', f)):
                shutil.copy(os.path.join(o_banco, 'modelli_misura', f), os.path.join(d_banco, 'modelli_misura', f))
        shutil.copy(os.path.join(o_banco, 'riferimento.json'), os.path.join(d_banco, 'riferimento.json'))
        print('riferimento e modelli di misura di %s copiati da IA37' % mondo, flush=True)
        ok = True
    os.makedirs(cart38(mondo), exist_ok=True)
    for nome in ('naturale.json', 'nuove_misure.json', 'guardie.json', 'ripiego.json', 'diagnosi.json'):
        if os.path.exists(os.path.join(CACHE37_ORIG, mondo, nome)) and not os.path.exists(cart38(mondo, nome)):
            shutil.copy(os.path.join(CACHE37_ORIG, mondo, nome), cart38(mondo, nome))
            ok = True
    o_rete = os.path.join(CACHE37_ORIG, mondo, 'rete_C')
    if os.path.exists(os.path.join(o_rete, 'pieno.pt')) and not os.path.exists(cart38(mondo, 'rete_C', 'pieno.pt')):
        shutil.copytree(o_rete, cart38(mondo, 'rete_C'), dirs_exist_ok=True)
        print('rete condizionata di %s copiata da IA37 (la variante scelta in IA35)' % mondo, flush=True)
        ok = True
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
    """Il riferimento del mondo: copiato da IA35 (corsa vera) o costruito con i lavori del banco (prove)."""
    dest = os.path.join(CACHE38, 'banco', mondo)
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


def fase_P(mondo, processi, addestra=True):
    os.makedirs(cart38(mondo), exist_ok=True)
    rif = costruisci_riferimento(mondo, processi)
    attiva_main(mondo, [])
    f_add, f_val, f_fuori = RD.divisione_fogli()
    nat_p = cart38(mondo, 'naturale.json')
    if not os.path.exists(nat_p):
        nat = OrderedDict(conti=RS.conti_naturali(f_add, f_fuori), fogli=[len(f_add), len(f_val), len(f_fuori)])
        json.dump(nat, open(nat_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    mancano = [m for m in ('lam', 'bordi_fine', 'k90') if not rif['scala'].get(m)]
    if mancano and not SOLO_CONTROLLI:
        raise RuntimeError('il riferimento di %s non ha la scala di %s: servono per l obiettivo (S_GRU_MONDO26 almeno 2)' % (mondo, ', '.join(mancano)))
    if mancano:
        print('ATTENZIONE (prova): senza scala per %s: queste grandezze non entrano nell obiettivo' % ', '.join(mancano), flush=True)
    nm_p = cart38(mondo, 'nuove_misure.json')
    if not os.path.exists(nm_p):
        r = SL.lavoro_riferimento_NM8()
        json.dump(r, open(nm_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    gu_p = cart38(mondo, 'guardie.json')
    if not os.path.exists(gu_p):                           # il riferimento delle guardie e di riuso_sez: valore sul testo vero e scala (100 divisioni per fogli)
        r = PLV.lavoro_riferimento_guardie()
        json.dump(r, open(gu_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
        print('riferimento delle guardie di %s: %s' % (mondo, {k: (round(v, 4) if v is not None else None) for k, v in r['scala'].items()}), flush=True)
    dr_p = cart38(mondo, 'div_ref38.json')
    if not os.path.exists(dr_p):                           # la differenza fra sezioni del vero e la sua scala, SOLO sui fogli d'addestramento
        r = SOL.lavoro_riferimento_div38()
        json.dump(r, open(dr_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
        print('differenza fra sezioni del vero sui fogli d\'addestramento (%d pagine) di %s: bigrammi %.4f (scala %.4f), parole %.4f (scala %.4f); sezioni %s' % (
            r['pagine_addestramento'], mondo, r['vero']['div_bigr'], r['scala']['div_bigr'], r['vero']['div_par'], r['scala']['div_par'], ','.join(r['sezioni_bigr'])), flush=True)
    rp_p = cart38(mondo, 'ripiego.json')
    if not os.path.exists(rp_p):                           # il ripiego K: scelto sui fogli di VALIDAZIONE (mai sui tenuti fuori), una volta per mondo, prima del ciclo
        import types
        r = FT.scegli_ripiego(types.SimpleNamespace(T3=RS.tabella_trigrammi(f_add)), f_add, f_val)
        json.dump(r, open(rp_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
        print('ripiego di %s: K = %g (la tabella di sezione batte la globale in validazione: %s; bit per segno globale %.4f, per K %s)' % (
            mondo, r['K'], r['batte_globale'], r['bit_globale'], {k: round(v, 4) for k, v in r['bit_per_K'].items()}), flush=True)
    dv_p = cart38(mondo, 'diagnosi.json')
    if not os.path.exists(dv_p):                           # la divergenza fra sezioni del testo vero del mondo
        r = FL.lavoro_riferimento_DV()
        json.dump(r, open(dv_p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
        print('divergenza fra sezioni del testo vero di %s: bigrammi %.4f bit, parole %.4f bit (sezioni %s)' % (mondo, r['bigr'], r['parole'], ','.join(r['sezioni_bigr'])), flush=True)
    print('mondo %s: riferimento con %d misure e %d giudici; fogli addestramento/validazione/fuori %d/%d/%d' % (mondo, len(rif['vero']), len(rif['nullo']), len(f_add), len(f_val), len(f_fuori)), flush=True)
    if addestra and not os.path.exists(cart38(mondo, 'rete_C', 'pieno.pt')):
        print('la rete condizionata di %s non e\' nella cache di IA37: si addestra la variante Cb (solo prove di sviluppo)' % mondo, flush=True)
        esegui(mondo, [], [('addestra', 'C')], 1, fatte_di(mondo))
    return rif


# ---------------------------------------------------------------- C: partenza, ciclo, scelta prudente

def valori_ia33(mondo):
    """Le manopole scelte da IA33 per il mondo (dizionario di 14) o None (corsa vera; per `struttura2` il punto del mondo `markov2`, il piu' vicino)."""
    p = os.path.join(CACHE33_ORIG, 'vero' if mondo == 'vero' else 'markov2', 'ciclo_esito.json')
    if SOLO_CONTROLLI or not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding='utf-8'))['manopole_migliori']
    except (OSError, ValueError, KeyError):
        return None


VALORI_STRESS2 = OrderedDict([('T_eol', 0.8), ('w_cont', 3.0), ('w_tri', 3.0), ('w_quad', 3.0), ('s', 0.8), ('w_uni', 1.0), ('w_bi', 1.0), ('b_nuove', -0.8), ('w_pag', 0.3)])


def _cubo_da_cache(cartella, mondo):
    p = os.path.join(cartella, mondo, 'ciclo_esito.json')
    if not SOLO_CONTROLLI and os.path.exists(p):
        try:
            return FW.da_cubo36(np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float))
        except (OSError, ValueError, KeyError):
            return None
    return None


def cubo_ia37(mondo):
    """Il punto scelto da IA37 (cubo a 15, `a_sez` compresa) o, solo nel mondo di sviluppo con PARTENZA38=stress, il punto di stress con `a_sez` 0,5."""
    p = os.path.join(CACHE37_ORIG, mondo, 'ciclo_esito.json')
    if not SOLO_CONTROLLI and os.path.exists(p):
        try:
            return np.clip(np.array(json.load(open(p, encoding='utf-8'))['u_migliore'], float)[:FW.DIM37], 0.0, 1.0)
        except (OSError, ValueError, KeyError):
            return None
    if SOLO_CONTROLLI and PARTENZA == 'stress':
        return FW.da_cubo36(OS.cubo_da_valori(VALORI_STRESS), a_sez=0.5)
    return None


def cubo_ia35(mondo):
    """Il punto scelto da IA35 (cubo a 14) con `a_sez` al bordo spento o, solo nel mondo di sviluppo con PARTENZA38=stress, un secondo punto di stress (piu' moderato)."""
    u = _cubo_da_cache(CACHE35_ORIG, mondo)
    if u is None and SOLO_CONTROLLI and PARTENZA == 'stress':
        u = FW.da_cubo36(OS.cubo_da_valori(VALORI_STRESS2))
    return u


def cubi_riferimento(mondo):
    """I punti di riferimento (cubi a 15 manopole): `ia37`, `ia35`, `ia33` (se ci sono), `neutro`. L'ordine e' quello di preferenza per la partenza."""
    out = OrderedDict()
    if PARTENZA != 'neutro':
        for nome, f in (('ia37', cubo_ia37), ('ia35', cubo_ia35)):
            u = f(mondo)
            if u is not None:
                out[nome] = u
    v = valori_ia33(mondo)
    if v is not None:
        out['ia33'] = FW.da_cubo36(OS.cubo_da_valori(v))
    out['neutro'] = FW.neutro_cubo37()
    return out


def scegli_partenza38(cand):
    """La partenza di IA38: il punto di IA37 se e' prudente (penalita' di guardia <= PEN_MAX); il punto di IA35 lo sostituisce solo se e' prudente E ha l'obiettivo prudente migliore (regola di IA37);
    altrimenti, se IA37 non e' prudente, il migliore per obiettivo prudente (regola di IA36). `cand`: nome -> dict(obiettivo_prudente, penalita_guardia). -> (nome, motivo)."""
    if not PSC.PRUDENTE:
        return list(cand)[0], 'senza protezione: si parte dal primo punto'
    primo = list(cand)[0]
    ok = [n for n in ('ia37', 'ia35') if n in cand and cand[n]['penalita_guardia'] <= PSC.PEN_MAX]
    if ok:
        n = min(ok, key=lambda m: (cand[m]['obiettivo_prudente'], ok.index(m)))
        return n, 'punto di %s: prudente (penalita\' di guardia %.2f <= %.2f) e con il migliore obiettivo prudente fra i punti di IA37 e IA35 prudenti' % (n.upper(), cand[n]['penalita_guardia'], PSC.PEN_MAX)
    n = min(cand, key=lambda m: cand[m]['obiettivo_prudente'])
    return n, 'ne\' il punto di IA37 ne\' quello di IA35 sono prudenti: si parte dal migliore per obiettivo prudente'


def meta_fogli(mondo, gen, rep=0):
    ff = sorted({x['foglio'] for x in I7.libro_vero()})
    import random
    rnd = random.Random(seme_str('ia38mezzi', mondo, gen, rep))
    rnd.shuffle(ff)
    h = len(ff) // 2
    return sorted(ff[:h]), sorted(ff[h:])


def raccogli(mondo, da, a, indici=None):
    """Le valutazioni del ciclo con `da <= gen < a` (e, se dato, `i` in `indici`) dal file delle corse."""
    return [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('ciclo|') and not c.get('errore') and da <= c['gen'] < a and (indici is None or c['i'] in indici)]


def fase_partenza(mondo, processi):
    """La partenza prudente: si rivalutano (RIV0_38 ripetizioni di due mezzi libri) il punto di IA35, quello di IA33 e il neutro; dal neutro vengono i z di guardia di riferimento (`zn`),
    che fissano il permesso delle guardie; si parte dal punto di IA35 se e' prudente, altrimenti dal migliore per obiettivo prudente. -> dict (con `cubo` e `zn`)."""
    p = cart38(mondo, 'partenza.json')
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    attiva_main(mondo, [])
    cub = cubi_riferimento(mondo)
    nomi = list(cub)
    fatte = fatte_di(mondo)
    lavori = []
    for r in range(RIV0):
        mA, mB = meta_fogli(mondo, r % NSPLIT)           # le stesse divisioni dei fogli delle prime generazioni del ciclo: il vero degli stessi fogli (e k90 del vero) e' gia' in cache
        for ci, nome in enumerate(nomi):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', 7000 + r * 10 + h, ci, list(map(float, cub[nome])), seme_str('ia38par', mondo, r, ci, h), fogli, h == 0 and K90, 'C'))
    esegui(mondo, [], lavori, processi, fatte)
    tutti = raccogli(mondo, 7000, 8000)
    ni = nomi.index('neutro')
    zn = PSC.media_z([c['zg'] for c in tutti if c['i'] == ni])
    info = OrderedDict()
    for ci, nome in enumerate(nomi):
        rs = [c for c in tutti if c['i'] == ci]
        vp = PSC.valore_candidato(rs, zn, GUARDIE36)
        info[nome] = OrderedDict([('n', len(rs)), ('obiettivo', vp[1] if vp else None), ('penalita_guardia', vp[2] if vp else None), ('obiettivo_prudente', vp[0] if vp else None),
                                  ('zg', PSC.media_z([c['zg'] for c in rs])), ('eccessi', PSC.eccessi(PSC.media_z([c['zg'] for c in rs]), zn))])
    valide = OrderedDict((n, x) for n, x in info.items() if x['obiettivo'] is not None)
    scelto, motivo = scegli_partenza38(valide)
    if os.environ.get('FORZA_PARTENZA38') == '1':                       # solo prove di sviluppo: si parte dal primo punto qualunque cosa dicano le guardie
        scelto, motivo = list(valide)[0], 'partenza forzata (prova di sviluppo)'
    ris = OrderedDict([('scelto', scelto), ('motivo', motivo), ('zn', zn), ('candidati', info), ('cubo', list(map(float, cub[scelto]))), ('cubi', OrderedDict((n, list(map(float, u))) for n, u in cub.items())),
                       ('protezione', PSC.PRUDENTE), ('parametri', OrderedDict([('ZG_ABS', PSC.ZG_ABS), ('DELTA_G', PSC.DELTA_G), ('W_G', PSC.W_G), ('PEN_MAX', PSC.PEN_MAX), ('ZCAP_G', PSC.ZCAP_G)]))])
    json.dump(ris, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('partenza: %s (%s)' % (scelto, motivo), flush=True)
    return ris


def fase_C(mondo, processi):
    attiva_main(mondo, [])
    par = fase_partenza(mondo, processi)
    zn = par['zn']
    x0 = np.array(par['cubo'], float)
    cubi = OrderedDict((n, np.array(u, float)) for n, u in par['cubi'].items())
    st_p = cart38(mondo, 'ciclo.json')
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(st_p):
        stato = json.load(open(st_p, encoding='utf-8'))
        cma = CMA.CMA.da_stato(stato['cma'])
        storia = stato['storia']
    else:
        cma = CMA.CMA(x0, SIGMA0, LAMBDA, seme=seme_str('ia38cma', mondo))
        storia = []
    fatte = fatte_di(mondo)
    while cma.gen < GEN:
        g = cma.gen
        xs, _ = cma.ask()
        mA, mB = meta_fogli(mondo, g % NSPLIT)          # le divisioni dei fogli girano su NSPLIT38 (6): il vero degli stessi fogli (e k90 del vero) si calcola una volta per processo e per divisione
        lavori = []
        for i, u in enumerate(xs):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', g * 10 + h, i, list(map(float, u)), seme_str('ia38ciclo', mondo, g, i, h), fogli, h == 0 and K90, 'C'))
        esegui(mondo, [], lavori, processi, fatte)
        tutti = raccogli(mondo, g * 10, g * 10 + 2)
        vals, obs, pens = [], [], []
        for i in range(len(xs)):
            rs = [c for c in tutti if c['i'] == i]
            v = PSC.valore_candidato(rs, zn, GUARDIE36) if len(rs) == 2 else None
            vals.append(v[0] if v else 99.0)
            obs.append(v[1] if v else 99.0)
            pens.append(v[2] if v else 0.0)
        cma.tell(xs, vals)
        storia.append(OrderedDict([('gen', g), ('valori', vals), ('obiettivi', obs), ('penalita_guardia', pens), ('minimo', float(min(vals))), ('media', float(np.mean(vals))), ('sigma', cma.sigma),
                                   ('punti', [list(map(float, u)) for u in xs])]))
        json.dump(dict(cma=cma.stato(), storia=storia), open(st_p, 'w', encoding='utf-8', newline='\n'), default=float)
        print('generazione %d: minimo %.3f (obiettivo %.3f, penalita\' di guardia %.2f), media %.3f, sigma %.3f' % (g, min(vals), obs[int(np.argmin(vals))], pens[int(np.argmin(vals))], float(np.mean(vals)), cma.sigma), flush=True)
    # finalisti: nome -> (cubo, rete). Il punto di IA35 e quello di IA33 si rivalutano come riferimento.
    cand = OrderedDict()
    cand['neutro'] = (cubi['neutro'], 'C')
    if 'ia37' in cubi:
        cand['ia37_C'] = (cubi['ia37'], 'C')
    if 'ia35' in cubi:
        cand['ia35_C'] = (cubi['ia35'], 'C')
    if 'ia33' in cubi:
        cand['ia33_C'] = (cubi['ia33'], 'C')
    cand['media_finale'] = (cma.mean, 'C')
    best_v, best_u, graz_v, graz_u = 1e9, None, 1e9, None
    for h in storia:
        for u, v, o in zip(h['punti'], h['valori'], h['obiettivi']):
            if v < best_v:
                best_v, best_u = v, np.array(u)
            if o < graz_v:
                graz_v, graz_u = o, np.array(u)
    cand['migliore_di_sempre'] = (best_u, 'C')                         # minimo dell'obiettivo prudente di tutte le valutazioni
    if graz_u is not None and not np.allclose(graz_u, best_u):
        cand['migliore_grezzo'] = (graz_u, 'C')                        # minimo dell'obiettivo senza penalita' (quello che sceglierebbe IA35): riferimento
    cand['migliore_ultima'] = (np.array(storia[-1]['punti'][int(np.argmin(storia[-1]['valori']))]), 'C')
    lavori = []
    for r in range(RIV):
        mA, mB = meta_fogli(mondo, 1000 + r, r)
        for ci, (nome, (u, rete)) in enumerate(cand.items()):
            for h, fogli in ((0, mA), (1, mB)):
                lavori.append(('valuta', 9000 + r * 10 + h, ci, list(map(float, np.clip(u, 0, 1))), seme_str('ia38riv', mondo, r, ci, h), fogli, h == 0 and K90, rete))
    esegui(mondo, [], lavori, processi, fatte)
    tutti = raccogli(mondo, 9000, 10000)
    # il CONTROLLO DI GUARDIA SUL LIBRO INTERO: l'obiettivo si calcola su mezzi libri (meta' dei fogli), l'esame su libri interi; le correzioni a conteggi accumulano su tutto il libro e un punto puo'
    # stare entro il permesso su un mezzo libro e uscirne su un libro intero. Ogni finalista scrive RIV_G38 libri interi (senza giudici: solo guardie, pochi secondi in piu' del solo scrivere);
    # il permesso e' quello di sempre (max(ZG_ABS, |z del neutro| + DELTA_G)) ma con z in sigma del vero intero e il neutro misurato sugli stessi libri interi.
    lavori_gi = [('GI', nome, r, list(map(float, np.clip(u, 0, 1))), seme_str('ia38gi', mondo, nome, r), rete) for nome, (u, rete) in cand.items() for r in range(RIV_G)]
    esegui(mondo, [], lavori_gi, processi, fatte)
    gi = [c for c in leggi_corse(percorso_corse(mondo)) if str(c.get('lavoro', '')).startswith('GI|') and not c.get('errore')]
    gu_rif = json.load(open(cart38(mondo, 'guardie.json'), encoding='utf-8'))

    def z_intero(valori):
        return OrderedDict((m, (valori[m] - gu_rif['vero'][m]) / gu_rif['sigma'][m]) for m in GUARDIE36 if valori.get(m) is not None and gu_rif['sigma'].get(m))
    zg_int = OrderedDict((nome, PSC.media_z([z_intero(c['valori']) for c in gi if c['nome'] == nome])) for nome in cand)
    zn_int = zg_int.get('neutro', {})
    fin = OrderedDict()
    for ci, nome in enumerate(cand):
        u, rete = cand[nome]
        rs = [c for c in tutti if c['i'] == ci]
        vp = PSC.valore_candidato(rs, zn, GUARDIE36)
        zg = PSC.media_z([c['zg'] for c in rs])
        pen_int = PSC.penalita_guardie(zg_int[nome], zn_int) if zg_int.get(nome) else None
        pen_sc = vp[2] if (vp and pen_int is None) else (max(vp[2], pen_int) if vp else None)           # la penalita' che conta: la piu' alta fra mezzo libro e libro intero
        fin[nome] = OrderedDict([('rete', rete), ('obiettivo', vp[1] if vp else None), ('penalita_guardia_mezzi', vp[2] if vp else None), ('penalita_guardia_intero', pen_int), ('penalita_guardia', pen_sc),
                                 ('obiettivo_prudente', PSC.obiettivo_prudente(vp[1], pen_sc) if vp else None), ('n', len(rs)), ('zg_intero', zg_int[nome]), ('eccessi_intero', PSC.eccessi(zg_int[nome], zn_int)),
                                 ('u', list(map(float, np.clip(u, 0, 1)))), ('manopole', FW.da_cubo37(np.clip(u, 0, 1))), ('zg', zg), ('eccessi', PSC.eccessi(zg, zn)),
                                 ('z', OrderedDict((m, float(np.mean([c['z'][m] for c in rs if m in c['z']]))) for m in OBIETTIVO38 if any(m in c['z'] for c in rs)) if rs else None),
                                 ('copia_violazioni', OrderedDict((k, float(np.mean([c['copia_violazioni'].get(k, 0.0) for c in rs]))) for k in RM.SOGLIE_COPIA) if rs else None)])
    scelto, motivo = PSC.scegli_finalista(fin)
    ris = OrderedDict([('storia', storia), ('finalisti', fin), ('scelto', scelto), ('motivo_scelta', motivo), ('u_migliore', fin[scelto]['u']), ('manopole_migliori', fin[scelto]['manopole']),
                       ('u_partenza', list(map(float, x0))), ('partenza', par['scelto']), ('motivo_partenza', par['motivo']), ('zn', zn), ('protezione', PSC.PRUDENTE),
                       ('parametri', par['parametri']), ('cubi', par['cubi']), ('compromesso', curva_compromesso(mondo, list(cand)))])
    json.dump(ris, open(cart38(mondo, 'ciclo_esito.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    print('ciclo finito: scelto %s (%s), obiettivo %.3f, penalita\' di guardia %.2f (neutro %.3f)' % (scelto, motivo, fin[scelto]['obiettivo'], fin[scelto]['penalita_guardia'], fin['neutro']['obiettivo']), flush=True)
    return ris


# ---------------------------------------------------------------- E: l'esame

def insiemi_esame(mondo, ris_ciclo):
    """I libri dell'esame: nome -> dict(n, spec, gru (quanti libri con k90 e R_rel), gruppo, ruolo). spec = ['L', cubo16, rete] | ['ORA', m] | ['GEMS']."""
    out = OrderedDict()
    neutro = list(map(float, FW.neutro_cubo37()))
    if 'L' in INSIEMI and ris_ciclo is not None:
        ub = list(map(float, ris_ciclo['u_migliore']))
        out['best'] = dict(n=N_ESAME, spec=['L', ub, 'C'], gru=N_GRU, gruppo='L', ruolo='IA38: punto scelto dal ciclo prudente, con le sezioni nell\'obiettivo')
        u37 = ris_ciclo.get('cubi', {}).get('ia37')
        if u37 is not None and N_IA37 > 0:
            out['ia37C'] = dict(n=N_IA37, spec=['L', list(map(float, u37)), 'C'], gru=min(N_GRU, 4), gruppo='L', ruolo='il punto scelto da IA37 (stessa rete), riscritto con semi nuovi')
        u35 = ris_ciclo.get('cubi', {}).get('ia35')
        if u35 is not None and N_IA35 > 0:
            out['ia35C'] = dict(n=N_IA35, spec=['L', list(map(float, u35)), 'C'], gru=min(N_GRU, 4), gruppo='L', ruolo='il punto scelto da IA35 (stessa rete), riscritto con semi nuovi')
        out['neuC'] = dict(n=N_NEUTRO, spec=['L', neutro, 'C'], gru=N_NEUTRO, gruppo='L', ruolo='manopole neutre (validita\' del giudice b)')
        u33 = ris_ciclo.get('cubi', {}).get('ia33')
        if u33 is not None and N_IA33 > 0:
            out['ia33C'] = dict(n=N_IA33, spec=['L', list(map(float, u33)), 'C'], gru=min(N_GRU, 4), gruppo='L', ruolo='il punto di IA33 sulla stessa rete')
        rnd = np.random.default_rng(seme_str('ia38casuali', mondo))
        for c in range(1, N_CASUALI + 1):
            u = np.clip(np.array(neutro) + rnd.uniform(-0.45, 0.45, FW.DIM37), 0.0, 1.0)
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
    p_ciclo = cart38(mondo, 'ciclo_esito.json')
    ris_ciclo = json.load(open(p_ciclo, encoding='utf-8')) if os.path.exists(p_ciclo) else None
    ins = insiemi_esame(mondo, ris_ciclo)
    attiva_main(mondo, [])
    v21 = v21_disponibili() if mondo == 'vero' and 'L' in INSIEMI else []
    nomi = [nome_libro(t, i) for t, d in ins.items() for i in range(1, d['n'] + 1)] + v21
    attiva_main(mondo, nomi)
    fatte = fatte_di(mondo)
    libri = [('libro36', t, i, d['spec'], seme_str('ia38esame', mondo, t, i)) for t, d in ins.items() for i in range(1, d['n'] + 1)]
    print('== esame %s: %d libri da scrivere' % (mondo, len(libri)), flush=True)
    esegui(mondo, nomi, libri, processi, fatte)
    lavori = [('M', n) for n in nomi] + [('J32', n) for n in nomi] + [('NM', n) for n in nomi] + [('GU', n) for n in nomi] + [('DV', n) for n in nomi]
    lavori += [(t, f, 0) for t in ('K', 'KN', 'D') for f in range(PIEGHE)]
    if GRU:
        for t, d in ins.items():
            for i in range(1, min(d['gru'], d['n']) + 1):
                lavori += [('G', tp, nome_libro(t, i), 1) for tp in ('K', 'R')]
        for n in v21[:4]:
            lavori += [('G', tp, n, 1) for tp in ('K', 'R')]
    lavori = sorted(lavori, key=lambda a: {'G': 0, 'D': 1, 'K': 2, 'KN': 2, 'J32': 3, 'M': 4, 'NM': 4, 'GU': 4, 'DV': 4}.get(a[0], 5))
    # il giudice b mediato: un lavoro per insieme (processi diversi)
    gruppi = [(t, [nome_libro(t, i) for i in range(1, d['n'] + 1)]) for t, d in ins.items()] + ([('v21', v21)] if v21 else [])
    lavori = [('B35', t, ns, seme_str('b35', mondo, t) % 1000) for t, ns in gruppi] + lavori
    print('== esame %s: %d lavori del banco' % (mondo, len(lavori)), flush=True)
    esegui(mondo, nomi, lavori, processi, fatte)
    return analisi_esame(mondo, ins, nomi, v21)


def analisi_esame(mondo, ins, nomi, v21):
    attiva_main(mondo, nomi)
    c = I7.contesto_A()
    rif = json.load(open(B.dir_mondo('riferimento.json'), encoding='utf-8'))
    nm_rif = json.load(open(cart38(mondo, 'nuove_misure.json'), encoding='utf-8'))
    gu_rif = json.load(open(cart38(mondo, 'guardie.json'), encoding='utf-8'))
    corse = leggi_corse(percorso_corse(mondo))
    C = B.indice_corse(corse)
    nm = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('NM|') and not r.get('errore')}
    gu = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('GU|') and not r.get('errore')}
    dv = {r['lavoro'][3:]: r for r in corse if str(r.get('lavoro', '')).startswith('DV|') and not r.get('errore')}
    dv_rif = json.load(open(cart38(mondo, 'diagnosi.json'), encoding='utf-8'))
    giudice_b = OrderedDict((r['lavoro'][4:], r) for r in corse if str(r.get('lavoro', '')).startswith('B35|') and not r.get('errore'))
    pK, pKN = B.profili_uniti('K'), B.profili_uniti('KN')
    n_pag = len(c['ids'])
    prof = OrderedDict((n, RM.valori_libro(n, C, pK, pKN, n_pag)) for n in nomi)
    corse_libro = {r['lavoro']: r for r in corse if str(r.get('lavoro', '')).startswith('libro|') and not r.get('errore')}
    return dict(rif=rif, nm_rif=nm_rif, gu_rif=gu_rif, nm=nm, gu=gu, dv=dv, dv_rif=dv_rif, prof=prof, giudice_b=giudice_b, ins=ins, nomi=nomi, v21=v21, corse_libro=corse_libro, n_pag=n_pag)


def media(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.mean(xs)) if xs else None


def sd(xs):
    xs = [x for x in xs if x is not None and x == x]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def riassunto_insieme(mondo, A, tipo):
    """Per un insieme di libri: AUC dei tre giudici mai visti (media, deviazione standard fra libri, errore), giudici di allenamento, misure tenute fuori (D, R_rel e le otto di struttura), guardie, copia."""
    rif, prof, nm_rif, nm, gu_rif, gu = A['rif'], A['prof'], A['nm_rif'], A['nm'], A['gu_rif'], A['gu']
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
    nove = [x['entro_2sigma'] for m, x in mis.items() if m != 'sezione']                # `sezione` e' in parte insegnata (tocca la materia delle grandezze nuove): si riporta a parte
    out['nove_senza_sezione'] = OrderedDict([('entro_2sigma', int(sum(nove))), ('su', len(nove)), ('quota', float(np.mean(nove)) if nove else None),
                                             ('fuori', [m for m, x in mis.items() if m != 'sezione' and not x['entro_2sigma']]), ('sezione_z', (mis.get('sezione') or {}).get('z'))])
    ali = OrderedDict()
    for m in PL.OBI_MISURE34:
        if m in rif['vero'] and rif['scala'].get(m):
            val = media([prof[l].get(m) for l in ls])
            if val is not None:
                ali[m] = OrderedDict([('valore', val), ('vero', rif['vero'][m]), ('z_sigma', (val - rif['vero'][m]) / (rif['scala'][m] * SIGMA_DA_SCALA))])
    out['misure_di_allenamento'] = ali
    gua = OrderedDict()                                             # guardie e riuso_sez (descrittive all'esame; mai nei criteri)
    for m in PMG.NOMI36:
        vero, s_ = (gu_rif['vero'] or {}).get(m), (gu_rif['sigma'] or {}).get(m)
        val = media([(gu.get('GU|%s' % l) or gu.get(l) or {}).get(m) for l in ls])
        if val is None or not s_ or vero is None:
            continue
        gua[m] = OrderedDict([('valore', val), ('vero', vero), ('sigma', s_), ('z', (val - vero) / s_), ('guardia', m in PMG.GUARDIE36)])
    out['guardie'] = gua
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


def lettura_O(R):
    """La lettura dell'oracolo del mondo `struttura2` (stessa regola di IA35). `R` = riassunti per insieme. -> dict."""
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
    out['misure_fuori_oracolo'] = R['orac']['misure_fuori']
    out['misure_fuori_gemello'] = R['gem']['misure_fuori'] if 'gem' in R else None
    return out


def esito_L(mondo, R, v21, O):
    """L'esito della parte L per il mondo: riuscito assoluto, al livello dell'oracolo (di `struttura2`), batte il riferimento (v21 nel mondo `vero`, il punto di IA35 sulla stessa rete nel mondo
    `struttura2`), non riuscito, non valido. Stesse regole di IA35."""
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
    elif R.get('ia37C'):
        base, nome = R['ia37C']['giudici_mai_visti'], 'IA37 (stesso punto sulla stessa rete)'
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
    # lettura (6): quanto si perde sui giudici e quanto si guadagna sulla struttura rispetto a IA35 (stesso esame, stessa rete)
    conf = None
    if R.get('ia37C'):
        k = R['ia37C']
        cj = OrderedDict((j, OrderedDict([('ia38', jb[j]['media']), ('ia37', k['giudici_mai_visti'][j]['media']),
                                          ('differenza_distanza_da_0_5', (abs(jb[j]['media'] - 0.5) - abs(k['giudici_mai_visti'][j]['media'] - 0.5)) if jb[j]['media'] is not None and k['giudici_mai_visti'][j]['media'] is not None else None)])) for j in GIUDICI3)
        cm = OrderedDict()
        for m in sorted(set(best['misure_tenute_fuori']) | set(k['misure_tenute_fuori'])):
            a, b2 = best['misure_tenute_fuori'].get(m), k['misure_tenute_fuori'].get(m)
            cm[m] = OrderedDict([('z_ia38', a['z'] if a else None), ('z_ia37', b2['z'] if b2 else None)])
        conf = OrderedDict([('giudici', cj), ('misure_tenute_fuori', cm), ('quota_entro_2sigma', OrderedDict([('ia38', best['quota_entro_2sigma']), ('ia37', k['quota_entro_2sigma'])]))])
    out['confronto_con_ia37'] = conf
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


def lettura_sezioni(mondo, R, ciclo, dv_rif):
    """Lettura (2), che cosa cambia vedendo le sezioni nell'obiettivo: `best` contro `ia37C` (il punto scelto da IA37, stessa rete): AUC dei tre giudici con l'errore della differenza, z delle misure tenute fuori
    (con `sezione` SEPARATA dalle altre nove: e' in parte insegnata), z di allenamento; la divergenza fra sezioni (bit, bigrammi di glifi e parole) di `best`, `ia37C`, `ia35C`, `neuC` e del vero; il valore di `a_sez`."""
    if 'best' not in R or 'ia37C' not in R:
        return None
    rc, ra = R['best'], R['ia37C']
    gi = OrderedDict((j, OrderedDict([('ia38', rc['giudici_mai_visti'][j]['media']), ('ia37', ra['giudici_mai_visti'][j]['media']),
                                      ('errore_differenza', math.sqrt(rc['giudici_mai_visti'][j]['errore'] ** 2 + ra['giudici_mai_visti'][j]['errore'] ** 2))])) for j in GIUDICI3)
    ms = OrderedDict()
    for m in sorted(set(rc['misure_tenute_fuori']) | set(ra['misure_tenute_fuori'])):
        x, y = rc['misure_tenute_fuori'].get(m), ra['misure_tenute_fuori'].get(m)
        ms[m] = OrderedDict([('z_ia38', x['z'] if x else None), ('z_ia37', y['z'] if y else None), ('insegnata', m == 'sezione')])
    al = OrderedDict()
    for m in sorted(set(rc['misure_di_allenamento']) | set(ra['misure_di_allenamento'])):
        x, y = rc['misure_di_allenamento'].get(m), ra['misure_di_allenamento'].get(m)
        al[m] = OrderedDict([('z_ia38', x['z_sigma'] if x else None), ('z_ia37', y['z_sigma'] if y else None)])
    man = (ciclo or {}).get('manopole_migliori') or {}
    diag = OrderedDict((t, OrderedDict((m, (R[t].get('diagnosi') or {}).get(m, {}).get('valore')) for m in ('bigr', 'parole'))) for t in R if not t.startswith('cas') and R[t].get('diagnosi'))
    diag['vero'] = OrderedDict((m, (dv_rif or {}).get(m)) for m in ('bigr', 'parole'))
    return OrderedDict([('a_sez', man.get('a_sez')), ('giudici', gi), ('misure_tenute_fuori', ms), ('misure_di_allenamento', al), ('quota_entro_2sigma', OrderedDict([('ia38', rc['quota_entro_2sigma']), ('ia37', ra['quota_entro_2sigma'])])),
                        ('nove_senza_sezione', OrderedDict((t, R[t].get('nove_senza_sezione')) for t in R if not t.startswith('cas'))), ('diagnosi', diag),
                        ('sezione_z', OrderedDict((t, (R[t]['misure_tenute_fuori'].get('sezione') or {}).get('z')) for t in R if not t.startswith('cas')))])


GIUDICI_OBI = ('e231', 'e266', 'K')


def curva_compromesso(mondo, nomi_finalisti):
    """Lettura (3), la curva del compromesso (descrittiva, nessun costo in piu'): per ogni candidato valutato nel ciclo, nella partenza e fra i finalisti (le due meta' mediate) la parte "giudici" J dell'obiettivo
    (media di min(|z|, 10) di e231, e266, K) e la parte "sezioni" S (media di min(|z|, 10) di div_bigr e div_par, anche se il peso e' zero); la frontiera = i candidati che nessun altro batte su entrambe. -> dict."""
    cap = RM.ZCAP32
    g = {}
    for c in leggi_corse(percorso_corse(mondo)):
        if not str(c.get('lavoro', '')).startswith('ciclo|') or c.get('errore') or not c.get('zdiv'):
            continue
        gen = c['gen']
        blocco = 'ciclo' if gen < 7000 else ('partenza' if gen < 9000 else 'finalisti')
        g.setdefault((blocco, gen // 10, c['i']), []).append(c)
    punti = []
    for (blocco, gg, i), rs in sorted(g.items()):
        if len(rs) != 2:
            continue
        J = float(np.mean([min(abs(r['z'][m]), cap) for r in rs for m in GIUDICI_OBI if m in r['z']]))
        S = float(np.mean([min(abs(r['zdiv'][m]), cap) for r in rs for m in SO.NOMI_OBI if m in r['zdiv']]))
        punti.append(OrderedDict([('blocco', blocco), ('gen', gg), ('i', i), ('J', J), ('S', S), ('obiettivo', float(np.mean([r['obiettivo'] for r in rs]))),
                                  ('a_sez', rs[0]['manopole'].get('a_sez')), ('nome', (nomi_finalisti[i] if blocco == 'finalisti' and i < len(nomi_finalisti) else None))]))
    fr, migliore = [], 1e18
    for pt in sorted(punti, key=lambda x: (x['J'], x['S'])):
        if pt['S'] < migliore - 1e-12:
            fr.append(pt)
            migliore = pt['S']
    return OrderedDict([('n', len(punti)), ('punti', punti), ('frontiera', fr)])


def disegna_compromesso(mondo, comp, percorso):
    """Grafico PNG (solo numeri): J contro S dei candidati, la frontiera e i finalisti con il nome."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=110)
    for blocco, colore, marc, et in (('ciclo', '#8a8a8a', 'o', 'ciclo'), ('partenza', '#1f6fb2', 's', 'partenza'), ('finalisti', '#c2410c', 'D', 'finalisti')):
        pt = [p for p in comp['punti'] if p['blocco'] == blocco]
        if pt:
            ax.scatter([p['J'] for p in pt], [p['S'] for p in pt], s=18 if blocco == 'ciclo' else 40, c=colore, marker=marc, label=et, zorder=2 if blocco == 'ciclo' else 3)
    for p in comp['punti']:
        if p['blocco'] == 'finalisti' and p.get('nome'):
            ax.annotate(p['nome'], (p['J'], p['S']), fontsize=6, xytext=(3, 3), textcoords='offset points')
    fr = comp['frontiera']
    ax.step([p['J'] for p in fr], [p['S'] for p in fr], where='post', color='black', lw=1, label='frontiera', zorder=4)
    ax.set_xlabel('parte giudici dell\'obiettivo (e231, e266, K): media di min(|z|, 10)')
    ax.set_ylabel('parte sezioni (div_bigr, div_par): media di min(|z|, 10)')
    ax.set_title('Mondo %s: compromesso fra giudici e sezioni (%d candidati)' % (mondo, comp['n']), fontsize=9)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(percorso)
    plt.close(fig)


def lettura_protezione(mondo, R, ciclo):
    """Lettura (3), la protezione: i finalisti (obiettivo, penalita' di guardia, z di guardia), chi ha vinto e perche', se il minimo grezzo sarebbe stato scartato; le guardie all'esame del punto scelto,
    del punto di IA35 e del neutro."""
    if not ciclo:
        return None
    fin = OrderedDict((n, OrderedDict([('obiettivo', x['obiettivo']), ('penalita_guardia', x['penalita_guardia']), ('penalita_guardia_mezzi', x.get('penalita_guardia_mezzi')), ('penalita_guardia_intero', x.get('penalita_guardia_intero')),
                                       ('obiettivo_prudente', x['obiettivo_prudente']), ('zg', x['zg']), ('zg_intero', x.get('zg_intero')), ('eccessi', x['eccessi'])]))
                      for n, x in ciclo['finalisti'].items())
    es = OrderedDict()
    for t in ('best', 'ia37C', 'ia35C', 'neuC', 'ia33C'):
        if R and t in R:
            es[t] = OrderedDict((m, x['z']) for m, x in R[t].get('guardie', {}).items())
    return OrderedDict([('protezione', ciclo.get('protezione')), ('parametri', ciclo.get('parametri')), ('partenza', ciclo.get('partenza')), ('motivo_partenza', ciclo.get('motivo_partenza')),
                        ('zn', ciclo.get('zn')), ('scelto', ciclo['scelto']), ('motivo_scelta', ciclo.get('motivo_scelta')), ('finalisti', fin), ('guardie_all_esame', es)])


def fase_S(mondi, sintesi):
    os.makedirs(USCITA, exist_ok=True)
    ins_s = (sintesi.get('struttura2') or {}).get('insiemi')
    if not ins_s and os.path.exists(cart38('struttura2', 'esame.json')):
        ins_s = json.load(open(cart38('struttura2', 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict).get('insiemi')
    O = lettura_O(ins_s) if ins_s else None
    for mondo, s in sintesi.items():
        R = s.get('insiemi')
        if not R:
            continue
        s['esito_L'] = esito_L(mondo, R, s.get('v21'), O)
        dr = cart38(mondo, 'diagnosi.json')
        s['sezioni'] = lettura_sezioni(mondo, R, s.get('ciclo'), json.load(open(dr, encoding='utf-8')) if os.path.exists(dr) else None)
        s['protezione'] = lettura_protezione(mondo, R, s.get('ciclo'))
    out = OrderedDict([('esperimento', NOME), ('lettura_oracolo_struttura', O), ('mondi', sintesi)])
    json.dump(out, open(os.path.join(USCITA, 'ia38_sezioni.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    md = ['# IA38 (ia38) — Giudici e sezioni insieme', '', 'Preregistrazione: `preregistrazioni/ia38.md`. Solo numeri e aggregati.', '']
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
            md += ['Protezione: %s. Partenza: %s (%s). Ciclo di %d generazioni; scelto **%s** (%s): obiettivo %s, penalita\' di guardia %s (neutro: obiettivo %s).' % (
                'accesa' if c.get('protezione') else 'SPENTA', c.get('partenza'), c.get('motivo_partenza'), len(c['storia']), c['scelto'], c.get('motivo_scelta'),
                mf(c['finalisti'][c['scelto']]['obiettivo']), mf(c['finalisti'][c['scelto']]['penalita_guardia'], 2), mf(c['finalisti']['neutro']['obiettivo'])), '']
            md += ['| generazione | valore minimo | obiettivo del minimo | penalita\' di guardia | media | passo CMA-ES |', '|---|---|---|---|---|---|']
            for h in c['storia']:
                k = int(np.argmin(h['valori']))
                md.append('| %d | %s | %s | %s | %s | %s |' % (h['gen'], mf(h['minimo']), mf(h['obiettivi'][k]), mf(h['penalita_guardia'][k], 2), mf(h['media']), mf(h['sigma'], 3)))
            md += ['', '| finalista | obiettivo | penalita mezzi libri | penalita libro intero | obiettivo prudente | ' + ' | '.join(GUARDIE36) + ' (z in sigma, libro intero) |', '|---|---|---|---|---|' + '---|' * len(GUARDIE36)]
            for n, x in c['finalisti'].items():
                md.append('| %s | %s | %s | %s | %s | %s |' % (n, mf(x['obiettivo']), mf(x.get('penalita_guardia_mezzi'), 2), mf(x.get('penalita_guardia_intero'), 2), mf(x['obiettivo_prudente']), ' | '.join(mf((x.get('zg_intero') or {}).get(m), 1) for m in GUARDIE36)))
            md += ['', 'z di guardia delle manopole neutre (fissano il permesso): ' + ', '.join('%s %s' % (m, mf(v, 1)) for m, v in (c.get('zn') or {}).items()), '']
            md += ['| finalista | ' + ' | '.join(OBIETTIVO38) + ' |', '|---|' + '---|' * len(OBIETTIVO38)]
            for n, x in c['finalisti'].items():
                md.append('| %s | %s |' % (n, ' | '.join(mf((x['z'] or {}).get(m), 1) for m in OBIETTIVO38)))
            md += ['', '| manopola | valore scelto | neutro | partenza |', '|---|---|---|---|']
            xp = FW.da_cubo37(c['u_partenza']) if c.get('u_partenza') else {}
            for k, v in c['manopole_migliori'].items():
                md.append('| %s | %s | %s | %s |' % (k, mf(v), mf(NEUTRO37[k]), mf(xp.get(k))))
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
            for t in ('best', 'ia37C', 'ia35C', 'ia33C', 'neuC'):
                if t in R:
                    md += ['Misure tenute fuori, `%s` (z in sigma): ' % t + ', '.join('%s %s' % (m, mf(x['z'], 1)) for m, x in R[t]['misure_tenute_fuori'].items()), '']
            for t in ('best', 'ia37C', 'ia35C', 'neuC', 'gem', 'orac'):
                if t in R and R[t].get('guardie'):
                    md += ['Guardie e riuso_sez, `%s` (z in sigma): ' % t + ', '.join('%s %s' % (m, mf(x['z'], 1)) for m, x in R[t]['guardie'].items()), '']
        e = s.get('esito_L')
        if e:
            md += ["**Esito: %s** (giudice b valido: %s; controllo negativo riuscito: %s)." % (e['esito'], e['giudice_b_valido'], e['controllo_negativo_riuscito']), '']
            if e['esito'] in ('non riuscito', 'non valido'):
                md += ['Resta fuori: giudici oltre 0,60: %s; misure fuori 2 sigma: %s; copia superata: %s.' % (', '.join(e['resta_fuori']['giudici_oltre_0_60']) or 'nessuno',
                                                                  ', '.join(e['resta_fuori']['misure_fuori_2sigma']) or 'nessuna', e['resta_fuori']['copia_superata']), '']
    md += ['## Che cosa cambia vedendo le sezioni nell\'obiettivo (`best` contro `ia37C`) e la diagnosi', '']
    for mondo, s in sintesi.items():
        c = s.get('sezioni')
        if not c:
            continue
        md += ['Mondo `%s`: a_sez %s. Giudici (IA38 / IA37): ' % (mondo, mf(c['a_sez'])) + ', '.join('%s %s / %s' % (j, mf(x['ia38']), mf(x['ia37'])) for j, x in c['giudici'].items()) +
               '; misure tenute fuori z (IA38 / IA37; **`sezione` in parte insegnata**): ' + ', '.join('%s %s / %s%s' % (m, mf(x['z_ia38'], 1), mf(x['z_ia37'], 1), ' (insegnata)' if x['insegnata'] else '') for m, x in c['misure_tenute_fuori'].items()), '']
        md += ['Le altre nove misure entro 2 sigma (senza `sezione`): ' + '; '.join('%s %s su %s' % (t, v['entro_2sigma'], v['su']) for t, v in c['nove_senza_sezione'].items() if v) + '. `sezione` z: ' +
               ', '.join('%s %s' % (t, mf(v, 1)) for t, v in c['sezione_z'].items()), '']
        md += ['Divergenza fra sezioni (bit; bigrammi di glifi / parole): ' + '; '.join('%s %s / %s' % (t, mf(v.get('bigr'), 4), mf(v.get('parole'), 4)) for t, v in c['diagnosi'].items()), '']
    md += ['## La curva del compromesso (frontiera fra la parte giudici e la parte sezioni dell\'obiettivo)', '']
    for mondo, s in sintesi.items():
        cc = (s.get('ciclo') or {}).get('compromesso')
        if not cc:
            continue
        md += ['Mondo `%s`: %d candidati; frontiera (nessun altro candidato e\' migliore su entrambe):' % (mondo, cc['n']), '', '| blocco | gen | i | nome | J (giudici) | S (sezioni) | obiettivo | a_sez |', '|---|---|---|---|---|---|---|---|']
        for p in cc['frontiera']:
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (p['blocco'], p['gen'], p['i'], p.get('nome') or '-', mf(p['J'], 2), mf(p['S'], 2), mf(p['obiettivo'], 2), mf(p.get('a_sez'), 2)))
        md.append('')
        try:
            disegna_compromesso(mondo, cc, os.path.join(USCITA, 'ia38_compromesso_%s.png' % mondo))
        except Exception as e:                                                # noqa: BLE001
            md += ['(grafico non disegnato: %s)' % type(e).__name__, '']
    open(os.path.join(USCITA, 'ia38_sezioni.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


def main():
    import numpy  # noqa: F401
    import torch  # noqa: F401
    print('ia38: mondi %s, insiemi %s, libro (%s), protezione %s' % (MONDI38, INSIEMI, 'controlli: latino' if SOLO_CONTROLLI else 'Voynich', 'accesa' if PSC.PRUDENTE else 'SPENTA'), flush=True)
    os.makedirs(CACHE38, exist_ok=True)
    os.makedirs(USCITA, exist_ok=True)
    processi = int(os.environ.get('PROCESSI', 3))
    fasi = os.environ.get('FASI', 'PCES')
    if len(MONDI38) > 1 and os.environ.get('IA38_FIGLIO') != '1':
        # un processo nuovo per ogni mondo (il testo del mondo si costruisce una volta sola per processo); la sintesi poi legge i file
        import subprocess
        senza_s = ''.join(ch for ch in fasi if ch != 'S')
        for mondo in MONDI38:
            if senza_s:
                rc = subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, MONDI38=str(MONDI_ELENCO.index(mondo) + 1), FASI=senza_s, IA38_FIGLIO='1'))
                if rc != 0:
                    sys.exit(rc)
        if 'S' in fasi:
            sys.exit(subprocess.call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, FASI='S', IA38_FIGLIO='1')))
        return
    sintesi = OrderedDict()
    for mondo in MONDI38:
        if os.environ.get('RIPRENDI') != '1' and 'P' in fasi:
            azzera_corse(mondo)
        s = OrderedDict()
        if 'P' in fasi:
            fase_P(mondo, processi, addestra='L' in INSIEMI)
        if 'C' in fasi and 'L' in INSIEMI:
            s['ciclo'] = fase_C(mondo, processi)
        elif os.path.exists(cart38(mondo, 'ciclo_esito.json')):
            s['ciclo'] = json.load(open(cart38(mondo, 'ciclo_esito.json'), encoding='utf-8'), object_pairs_hook=OrderedDict)
        if 'E' in fasi:
            A = fase_E(mondo, processi)
            s['insiemi'] = OrderedDict((t, riassunto_insieme(mondo, A, t)) for t in A['ins'])
            s['v21'] = riassunto_v21(A)
            s['v21_libri'] = A['v21']
            s['giudice_b'] = A['giudice_b']
            json.dump(OrderedDict((k, s[k]) for k in ('insiemi', 'v21', 'v21_libri', 'giudice_b')), open(cart38(mondo, 'esame.json'), 'w', encoding='utf-8', newline='\n'),
                      ensure_ascii=False, indent=1, default=float)
        elif 'S' in fasi and os.path.exists(cart38(mondo, 'esame.json')):
            s.update(json.load(open(cart38(mondo, 'esame.json'), encoding='utf-8'), object_pairs_hook=OrderedDict))
        sintesi[mondo] = s
    if 'S' in fasi:
        fase_S(MONDI38, sintesi)


if __name__ == '__main__':
    main()
