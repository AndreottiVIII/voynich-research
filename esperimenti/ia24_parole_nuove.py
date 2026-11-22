# -*- coding: utf-8 -*-
"""Esperimento IA24 (ia24): che cosa distingue le parole NUOVE del Voynich da quelle inventate dagli imitatori?

Domanda (Davide, 22/11/2026, dopo IA20-IA22): in tutti gli imitatori il costo di forma delle parole nuove (bit per glifo, trigrammi di glifi) non arriva al vero (vero 3,48;
imitatori 3,67-3,82; v21 3,66) mentre la quota di parole nuove e' al vero. Un imitatore che costruisce le parole nuove in modo diverso le porta al vero senza rompere il resto?
Ipotesi (non vincolanti): (1) le parole nuove del Voynich sono ritocchi (una o due modifiche) di parole del lessico, non inventate segno per segno; (2) seguono una
grammatica a caselle piu' rigida di quella che la rete impara.
Preregistrazione: preregistrazioni/ia24.md. I modelli stanno in nuove_modelli.py, la fase 0 descrittiva in nuove_fase0.py, le prove di unita' in nuove_prove.py.

Che cosa fa il codice (in parole semplici)
- Fase A: 30 addestramenti (3 imitatori W1-W3 x 5 pieghe per foglio x 2 repliche) + eventuali modelli del giudice A mancanti.
    W1 parola nuova = ritocco del lessico (miscela esatta: libero / parola del lessico con 0, 1 o 2 modifiche); W2 = W1 piu' il puntatore di pagina di E2;
    W3 la GRU con un modello di forma a caselle come secondo esperto sul segno.
- Fase Q: controlli di sensibilita' su testi sintetici (parole nuove piantate come ritocchi; piantate a caselle; "senza niente").
- Fase C: libri onesti (N_LIBRI24 per tipo, meta' per replica) con giudici del paper, giudice A (riportato), copia a memoria e ripetizioni; e le stesse misure sui libri
  di M1 e M5 (ia20) e di E2 (ia22) letti dalla cache (mai riaddestrati).
- Fase F: fase 0 sulle parole nuove (vero, v21, riferimenti) e i controlli con parole nuove piantate.
- Fase D: controlli dei giudici, giudice K, misure di struttura (copia netta, Λ, contatto, D, G9, bordi, parole nuove, costo di forma), fase 0 sui libri W.
- Fase S: sintesi e letture preregistrate (L1-L4).
Uscite (solo numeri e aggregati): risultati/ia24_parole_nuove.json e .md e, una riga per lavoro, risultati/ia24_corse.jsonl. Modelli, libri e profili in dati/cache/ia24
(CACHE24, protetti: non si committano).

    nohup bash strumenti/coda.sh ia24 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia24" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO24=1 RIF24=ricalcola USCITA=<cartella fuori dal repo> python esperimenti/ia24_parole_nuove.py   (prova sul latino)

Variabili (oltre a quelle di ia07, ia20 e ia22, che si importano): PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere A Q C F D S; predefinito AQCFDS), FILTRO.
Nuove: CACHE24, EPOCHE24 (150), PAZIENZA24 (10), N_LIBRI24 (10), PICCOLO24 (solo prove; deve coincidere con PICCOLO20), EPOCHE_SENS24 (60), TIPI24 (cifre, senza virgole:
123 = W1 W2 W3), RIF24 ('cache' = riferimenti letti dalle cache di ia20 e ia22; 'ricalcola' = solo prove del codice). I valori predefiniti sono quelli preregistrati.
Nessun valore contiene virgole o due punti (la coda li dividerebbe).
"""
import json, math, os, pickle, random, statistics, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
# ia22 vuole PICCOLO22 == PICCOLO20 (le prove usano la taglia piccola in tutti e due): qui lo si fa coincidere
os.environ.setdefault('PICCOLO22', os.environ.get('PICCOLO20', '0'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import ia20_imitatore_gradini as I20  # noqa: E402
import ia22_eco_e_legame as I22  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import nuove_modelli as NM  # noqa: E402
import nuove_fase0 as NF  # noqa: E402
import imitatore_misure as MS  # noqa: E402
import aprire_parole as AP  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402

NOME = 'ia24_parole_nuove'
SOLO_CONTROLLI = I7.SOLO_CONTROLLI
USCITA = I7.USCITA
CACHE24 = os.environ.get('CACHE24', os.path.join(USCITA, 'ia24_cache') if SOLO_CONTROLLI else os.path.join(QUI, '..', 'dati', 'cache', 'ia24'))
MOD24, LIBRI24, MISURE24, VICINI24 = (os.path.join(CACHE24, d) for d in ('modelli', 'libri', 'misure', 'vicini'))
PICCOLO = os.environ.get('PICCOLO24') == '1'
if PICCOLO != I20.PICCOLO:
    raise SystemExit('PICCOLO24 e PICCOLO20 devono avere lo stesso valore (le prove del codice usano la taglia piccola in tutti e due)')
IDX = OrderedDict((t, i) for i, t in enumerate(NM.TIPI))                       # W1..W3 -> 0..2
TIPI24 = tuple(NM.TIPI[int(x) - 1] for x in os.environ.get('TIPI24', '123') if x.isdigit())
REPLICHE24 = (0, 1)
EPOCHE24 = int(os.environ.get('EPOCHE24', 150))
PAZIENZA24 = int(os.environ.get('PAZIENZA24', 10))
N_LIBRI24 = int(os.environ.get('N_LIBRI24', 10))              # libri per tipo (meta' dalla replica 0, meta' dalla 1)
EPOCHE_SENS24 = int(os.environ.get('EPOCHE_SENS24', 60))
PAZIENZA_SENS24 = 10
RIF24 = os.environ.get('RIF24', 'cache')
PIEGHE = I7.PIEGHE
N_RIF = I20.N_LIBRI20                                          # libri di riferimento per sigla (10)
RIF_M = (1, 5)                                                 # M1 e M5 di ia20 (cache di ia20)
RIF_E = ('E2',)                                                # E2 di ia22 (cache di ia22)
ETICHETTE = ['M1', 'E2', 'M5', 'W1', 'W2', 'W3']               # ordine nelle tabelle
CHIAVI_V21 = I20.CHIAVI_V21
KTOP = 40 if PICCOLO else GM.K_TIPI                            # "parole piu' frequenti" del lessico (sorgenti delle modifiche doppie e della quota s_top)

# ---- soglie (fissate nella preregistrazione, prima di eseguire sul Voynich)
SOGLIA_ERRORI = I20.SOGLIA_ERRORI                              # 2 errori
VERO_TOL = I20.VERO_TOL                                        # "al vero": entro 2 errori o 5% del vero
# controlli di sensibilita' (fissati dopo le prove su testi non Voynich: vedi la preregistrazione, sezione "Prova del codice")
SENS24 = OrderedDict([('ritocchi_nuove', 0.10),                # W1, W2 sul testo a ritocchi piantati: bit per segno sulle parole PIANTATE dei fogli tenuti fuori, sotto M1 di almeno cosi'
                      ('ritocchi_posteriori', 0.50),           # e quota a posteriori della strada del lessico sulle parole nuove, almeno
                      ('ritocchi_quota', 0.05),                # e quota di parole nuove scritte: distanza massima da quella piantata
                      ('caselle_nuove', -0.02),                # W3 sul testo a caselle piantate: bit per segno sulle parole PIANTATE sotto M1 di almeno cosi' (non peggio: la GRU le impara da sola)
                      ('caselle_porta', 0.10),                 # e la porta di W3 piu' aperta sulle parole piantate che sulle altre di almeno cosi' (W3 riconosce le caselle)
                      ('note_max', 0.10),                      # e (W1, W2, W3) bit per segno sulle parole NOTE al massimo cosi' sopra M1 (non rovinare il resto)
                      ('senza_guadagno_max', 0.02),            # W3 senza niente di piantato: guadagno su M1 al massimo cosi' (bit per segno)
                      ('senza_nuove_max', 0.10)])              # W1, W2 senza niente di piantato: guadagno sulle parole nuove al massimo cosi'
SENS_TESTI = OrderedDict([('ritocchi', dict(modo='ritocchi', p_nuove=0.30)), ('caselle', dict(modo='caselle', p_nuove=0.30)), ('senza', dict(modo='senza', p_nuove=0.0))])
SENS_MODELLI = OrderedDict([('ritocchi', ('M1', 'W1', 'W2')), ('caselle', ('M1', 'W3')), ('senza', ('M1', 'W1', 'W2', 'W3'))])
KTOP_SENS = 100                                                # le sorgenti piantate sono le 100 parole piu' frequenti del testo sintetico
F0_SOGLIE = OrderedDict([('errori', 3.0), ('minimo_top', 0.10), ('minimo_caselle', 0.10), ('assente_errori', 2.0)])
F0C_TESTI = ('ritocco', 'libero', 'caselle')
MISURE_STR = I20.MISURE_STR
MISURE_FORMA = ['costo_forma', 'parole_nuove']                 # bersagli di W contro M1
MISURE_RESTO = ['contatto', 'D']                               # da non rompere
GIUDICI = I20.GIUDICI
F0_MISURE = OrderedDict([('quota_nuove', 'quota di parole nuove'), ('dist1', 'nuove a 1 modifica da una parola nota'), ('dist2', 'a 2 modifiche'), ('dist3', 'a 3 o piu\''),
                         ('dist1_freq5', 'a 1 modifica da una parola con almeno 5 occorrenze'), ('top_1', 'a 1 modifica da una delle K piu\' frequenti'),
                         ('top_2', 'a <= 2 modifiche da una delle K piu\' frequenti'), ('lung_nuove', 'lunghezza media (nuove)'), ('lung_note', 'lunghezza media (note)'),
                         ('js_primo', 'JS primo glifo (bit)'), ('js_interno', 'JS glifi interni (bit)'), ('js_ultimo', 'JS ultimo glifo (bit)'),
                         ('spiega_frequente', 'parola nota + pezzo frequente'), ('spiega_qualsiasi', 'parola nota + pezzo qualsiasi (<= 3 glifi)'),
                         ('costo_forma', 'costo di forma (bit per glifo)'), ('forma_primo', 'di cui primo glifo'), ('forma_secondo', 'secondo'), ('forma_terzo', 'terzo'),
                         ('forma_dopo', 'dal quarto'), ('forma_fine', 'fine parola'), ('costo_caselle', 'costo sotto le caselle (bit per glifo)')])
_C = {}


def nu(v, d=3):
    return I7.nu(v, d)


def seme_str(*a):
    return MS.seme_str(*a)


def mes(xs):
    return MS.media_es(xs)


def etichetta(nome):
    return nome.split(':')[0]


def e_nuovo(nome):
    return nome[0] == 'W' and nome[1].isdigit()


def e_rifE(nome):
    return nome[0] == 'E' and nome[1].isdigit()


def e_rifM(nome):
    return nome[0] == 'M' and nome[1].isdigit()


# ---------------------------------------------------------------- pagine e modelli

def pagine_fold24(piega, tipo, dp=None, tag='reale'):
    """(ctx, lessico, caselle, add, val, fuori): le pagine del modello della piega preparate per il tipo W; `ctx` ha le K parole piu' frequenti dell'addestramento;
    `lessico` le parole dei fogli di addestramento (con i conteggi per foglio) e, per W1 e W2, le parole a una e due modifiche di ogni parola del testo."""
    k = (tag, piega, tipo, PICCOLO)
    if k in _C:
        return _C[k]
    for kk in [x for x in _C if isinstance(x, tuple) and x[0] == tag and x[1] == piega and x[2] != tipo]:
        del _C[kk]                                             # una sola preparazione alla volta per piega: la memoria
    voc = I7.vocabolario()
    dp = dp or I16.dati_pagine()
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    sel = lambda ff: [d for d in dp.values() if d['foglio'] in set(ff)]
    K, S = (40, 12) if PICCOLO else (GM.K_TIPI, GM.S_CAND)
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(sel(f_add), GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    lex = NM.costruisci_lessico(sel(f_add), ctx)
    hmm = NM.adatta_caselle(lex, ctx) if tipo == 'W3' else None
    add, val, fuori = NM.prepara_insiemi([sel(f_add), sel(f_val), sel(f_fuori)], ctx, tipo, lex, hmm)
    if tipo != 'W3':
        memo = os.path.join(VICINI24, 'vicini_%s_f%s.pkl' % ('p' if PICCOLO else 'v', piega)) if tag == 'reale' else None
        if memo and os.path.exists(memo):
            lex.carica_memo(memo)
        lex.riempi(NM.tipi_parole([add, val, fuori]))
        if memo and not os.path.exists(memo):
            lex.salva_memo(memo)
    _C[k] = (ctx, lex, hmm, add, val, fuori)
    return _C[k]


def seme_modello(tipo, piega, replica):
    return 24000 + 1000 * IDX[tipo] + 100 * replica + piega


def percorso_modello(tipo, piega, replica, est):
    return os.path.join(MOD24, 'ia24_%s_%s_%d%s' % (tipo, piega, replica, est))


def addestra(tipo, piega, replica):
    inizio = time.time()
    voc = I7.vocabolario()
    ctx, lex, hmm, add, val, fuori = pagine_fold24(piega, tipo)
    cfg = NM.cfg_completa(tipo, voc, ctx, PICCOLO)
    nome = '%s p%s r%d' % (tipo, piega, replica)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = NM.addestra_modello(cfg, ctx, lex, add, val, seme_modello(tipo, piega, replica), EPOCHE24, PAZIENZA24, messaggi=messaggio)
    ris = OrderedDict([('lavoro', 'addestra|%s|%s|%d' % (tipo, piega, replica)), ('tipo', tipo), ('piega', piega), ('replica', replica),
                       ('parametri', sum(p.numel() for p in m.parameters())), ('pagine', [len(add), len(val), len(fuori)]),
                       ('epoche', len(ca)), ('epoca_scelta', scelta), ('arrivata_al_massimo', len(ca) >= EPOCHE24 and scelta > EPOCHE24 - PAZIENZA24),
                       ('curva_validazione', cv), ('curva_addestramento', ca),
                       ('bpc_addestramento', round(NM.bpc_pagine(m, ctx, add), 5)), ('bpc_validazione', round(NM.bpc_pagine(m, ctx, val), 5)),
                       ('bpc_fuori', round(NM.bpc_pagine(m, ctx, fuori), 5))])
    ris['scarto'] = round(ris['bpc_fuori'] - ris['bpc_addestramento'], 5)
    ris['appresi'] = NM.parametri_appresi(m)
    if tipo != 'W3':
        ris['diagnostica'] = NM.diagnostica(m, ctx, fuori)
    ris['secondi'] = round(time.time() - inizio, 1)
    NM.salva_modello(m, percorso_modello(tipo, piega, replica, '.pt'), voc['segni'], ctx, lex if tipo != 'W3' else None, hmm,
                     dict(tipo=tipo, piega=piega, replica=replica, epoca_scelta=scelta, solo_prova=bool(SOLO_CONTROLLI)))
    json.dump(ris, open(percorso_modello(tipo, piega, replica, '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


def carica(tipo, piega, replica):
    k = ('modello', tipo, piega, replica)
    if k not in _C:
        _C[k] = NM.carica_modello(percorso_modello(tipo, piega, replica, '.pt'), I7.vocabolario())
    return _C[k]


# ---------------------------------------------------------------- scrivere

def parola_da_lessico(pen, k, T, rng, psub, pins, cache):
    """Una parola dalla strada del lessico con `k` modifiche (0, 1, 2): la sorgente si pesca con la frequenza e con la probabilita' GRU dei primi due glifi (`T`),
    le modifiche con i tipi e le tabelle imparati; con due modifiche la parola deve distare 2 dalla sorgente. None se non riesce."""
    lex = pen.lex
    g = 0 if k < 2 else 1
    if g not in cache:
        cache[g] = pen.pesi_sorgenti(T, g)
    p = cache[g]
    i = int(rng.choice(len(p), p=p))
    c = lex.parole[i]
    if k == 0:
        return c
    if 'tau' not in cache:
        cache['tau'] = pen.tabelle_tipo()
    w = c
    for _ in range(k):
        w = GM.campiona_ritocco(w, 1 + int(rng.choice(3, p=cache['tau'])), psub, pins, rng)
        if w is None:
            return None
    if k == 2 and (w == c or w in NM.n1_stringhe(c, lex.U)):
        return None
    return w


def scrivi_pagina24(m, ctx, lex, pen, regole, rp, voc, D, rng, conta):
    """Una pagina con la disposizione `rp`. W3: segno per segno (la spinta delle caselle e' nei logit). W1, W2: a inizio parola la miscela sceglie fra libero, lessico
    (0, 1, 2 modifiche) e, per W2, una parola della riga in corso o di quella sopra con la sua strada (come E2); le parole non valide si scartano e si pesca di nuovo
    (fino a 8 volte, poi libero)."""
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    nt = NM.NT_PUNT.get(m.tipo, 0)
    pen.apri()
    lg = None
    for t in I7.testa_pagina(rp, voc):
        lg = pen.dai(t)
    lessico = m.tipo in ('W1', 'W2')
    if lessico:
        psub, pins = pen.tabelle_ritocco()
    out = []
    for j, x in enumerate(rp):
        for t in I7.testa_riga(x, j, voc, D):
            lg = pen.dai(t)
        parole, lung, prima, fine = [], 0, 'inizio', False
        while not fine:
            w2 = None
            if lessico:
                T = pen.tabella_coppie()
                cand = pen.candidati() if m.tipo == 'W2' else []
                pf, pk, pc = pen.miscela(cand, T)
                pr = np.concatenate([[pf], pk] + ([pc[:len(cand)].reshape(-1)] if pc is not None else []))
                pr = pr / pr.sum()
                cache = {}
                nome = 'libero'
                for _ in range(8):
                    idx = int(rng.choice(len(pr), p=pr))
                    if idx == 0:
                        break
                    if idx <= 3:
                        nome = 'lessico%d' % (idx - 1)
                        w2 = parola_da_lessico(pen, idx - 1, T, rng, psub, pins, cache)
                    else:
                        kk, tipo_r = divmod(idx - 4, nt)
                        nome = 'pagina_' + ('uguale', 'cambia', 'aggiunge', 'toglie')[tipo_r]
                        w2 = GM.campiona_ritocco(cand[kk][0], tipo_r, psub, pins, rng)
                    if w2 is not None and len(w2):
                        stringhe = [unita[u] for u in w2]
                        if D(''.join(stringhe)) == stringhe:
                            break
                    w2 = None
                if w2 is None:
                    nome = 'libero'
                conta[nome] += 1
                if w2 is not None and nome.startswith('lessico'):
                    conta[nome + ('_nuova' if w2 not in lex.idx else '_nota')] += 1
            if w2 is not None:
                for u in w2:
                    lg = pen.dai(u0 + u)
                lung += len(w2)
                ammessi = [SP, EOL] if lung < voc['lmax'] else [EOL]
                z = np.array([lg[a] for a in ammessi])
                z = np.exp(z - z.max())
                s = ammessi[I20.campiona(z / z.sum(), rng)]
                lg = pen.dai(s)
                parole.append(''.join(unita[u] for u in w2))
                prima = 'spazio'
                if s == EOL:
                    fine = True
                else:
                    lung += 1
                continue
            parola = []
            while True:
                amm = regole.ammessi(parola, lung, prima)
                z = np.array([lg[a] for a in amm])
                z = np.exp(z - z.max())
                s = amm[I20.campiona(z / z.sum(), rng)]
                lg = pen.dai(s)
                if s == EOL:
                    parole.append(''.join(parola))
                    fine = True
                    break
                lung += 1
                if s == SP:
                    parole.append(''.join(parola))
                    prima = 'spazio'
                    break
                parola.append(regole.unita[s])
                prima = 'segno'
        out.append((x['pagina'], x['ini'], parole))
    return out


def scrivi_libro24(tipo, replica, seme):
    righe, voc, D = I7.libro_vero(), I7.vocabolario(), I7.divisore()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    pg = I7.pieghe()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())
    regole = I20.RegoleScrittura(voc)
    penne = {}
    conta = Counter()
    out = []
    for pag, rp in pp.items():
        k = pg[I7.foglio_di(pag)]
        if k not in penne:
            m, ctx, lex, hmm = carica(tipo, k, replica)
            penne[k] = (m, ctx, lex, NM.Penna24(m, ctx, lex, hmm, cap + 8))
        m, ctx, lex, pen = penne[k]
        out += scrivi_pagina24(m, ctx, lex, pen, regole, rp, voc, D, rng, conta)
    return out, conta


def percorso_libro(tipo, i):
    return os.path.join(LIBRI24, 'ia24_libro_%s_%d.txt' % (tipo, i))


def lavoro_libro(tipo, i):
    inizio = time.time()
    replica = I7.replica_del_libro(i, N_LIBRI24)
    seme = 2400000 + 10000 * IDX[tipo] + i
    os.makedirs(LIBRI24, exist_ok=True)
    percorso = percorso_libro(tipo, i)
    conta = None
    if os.path.exists(percorso):
        t = I7.leggi_file(percorso)
    else:
        t, conta = scrivi_libro24(tipo, replica, seme)
        I7.scrivi_file(t, percorso + '.tmp', 'ia24, libro %s %d' % (tipo, i), replica)
        os.replace(percorso + '.tmp', percorso)
        assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('replica', replica), ('righe', len(t)), ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    if conta is not None and tipo != 'W3':
        ris['modi_scrittura'] = OrderedDict(conta)
    ris.update(I22.misura_libro(t, os.path.join(LIBRI24, 'ia24_tabella_%s_%d.npz' % (tipo, i))))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def percorso_riferimento(sigla, i):
    """Libro i di un riferimento: M1, M5 (cache di ia20), E2 (cache di ia22)."""
    if sigla[0] == 'M':
        return I20.percorso_libro(int(sigla[1]), i)
    return I22.percorso_libro(sigla, i)


def crea_riferimento(sigla, i):
    """Solo con RIF24=ricalcola (prove del codice): scrive il libro del riferimento con il codice di ia20 o di ia22 nella cache di prova."""
    if sigla[0] == 'M':
        I20.lavoro_libro(int(sigla[1]), i)
    else:
        I22.lavoro_libro(sigla, i)


def lavoro_riflibro(sigla, i):
    """Misure dei giudici sul libro i di un riferimento (M1, M5, E2), letto dalla cache (RIF24=cache). Con RIF24=ricalcola (solo prove) prima si scrive."""
    inizio = time.time()
    percorso = percorso_riferimento(sigla, i)
    if not os.path.exists(percorso):
        if RIF24 != 'ricalcola':
            raise RuntimeError('manca il libro di riferimento %s (RIF24=cache): va fatto con ia20 o ia22' % percorso)
        crea_riferimento(sigla, i)
    t = I7.leggi_file(percorso)
    ris = OrderedDict([('lavoro', 'riflibro|%s|%d' % (sigla, i)), ('sigla', sigla), ('i', i), ('replica', I7.replica_del_libro(i, N_RIF)), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    ris.update(I22.misura_libro(t, None))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- controlli di sensibilita' (testi sintetici con parole nuove piantate)

def misure_sens24(rows, noti, indice_top, caselle, indice_tutti):
    """Numeri del controllo su pagine (pagina -> righe): quota di parole nuove (non fra le `noti` = parole dei fogli di addestramento), fra le nuove la quota a <= 2
    modifiche da una delle parole frequenti (`indice_top`), a 1 e a <= 2 modifiche da una parola nota qualsiasi (`indice_tutti`) e la quota conforme alla grammatica a
    caselle piantata. Dentro il testo le parole nuove sono in parte ritocchi piantati e in parte parole rare del libro mai viste: le quote vanno lette insieme."""
    par = nuove = r2 = cf = d1 = d12 = 0
    for rr in rows.values():
        for _, ws in rr:
            for w in ws:
                par += 1
                if w not in noti:
                    nuove += 1
                    r2 += indice_top.cerca(w)[0] <= 2
                    dd = indice_tutti.cerca(w)[0]
                    d1 += dd <= 1
                    d12 += dd <= 2
                    cf += NM.conforme_caselle(list(w), caselle)
    n = max(nuove, 1)
    return OrderedDict(parole=par, nuove=nuove, quota_nuove=nuove / max(par, 1), rit2=r2 / n, d1=d1 / n, d12=d12 / n, conforme=cf / n)


def lavoro_sens(testo, modello):
    """Un modello addestrato (piega 0) su un testo sintetico; validazione e fuori piega; per W1 e W2 le quote del lessico; per `ritocchi` e `caselle` si scrivono i fogli
    tenuti fuori e si misurano le parole nuove, confrontate con le stesse misure del testo piantato."""
    inizio = time.time()
    voc, D = I7.vocabolario(), I7.divisore()
    info = {}
    sint = NM.sintetico_nuove(I7.libro_vero(), seme_str('ia24sint', testo), D, voc['unita'], info_out=info, n_sorgenti=KTOP_SENS, **SENS_TESTI[testo])
    dps = I20.pagine_sintetiche(sint)
    nome = 'sens %s %s' % (testo, modello)

    def messaggio(s):
        try:
            print('[%s]%s' % (nome, s), flush=True)
        except OSError:
            pass
    seme = 34000 + 10 * list(SENS_TESTI).index(testo) + (['M1', 'W1', 'W2', 'W3'].index(modello))
    tag = 'sint24:' + testo
    diag = None
    if modello == 'M1':
        ctx, add, val, fuori = I20.pagine_fold(0, 1, dps, tag=tag)
        cfg = GM.cfg_completa(1, voc, ctx, PICCOLO)
        m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, seme, EPOCHE_SENS24, PAZIENZA_SENS24, messaggi=messaggio)
        bv, bf = round(GM.bpc_pagine(m, ctx, val), 5), round(GM.bpc_pagine(m, ctx, fuori), 5)
        penna = lambda: GM.Penna20(m, ctx, cap)
        scrivi = lambda pen, regole, rp, rng, conta: I20.scrivi_pagina(m, ctx, pen, regole, rp, voc, D, rng, conta)
    else:
        ctx, lex, hmm, add, val, fuori = pagine_fold24(0, modello, dps, tag=tag)
        cfg = NM.cfg_completa(modello, voc, ctx, PICCOLO)
        m, cv, ca, scelta = NM.addestra_modello(cfg, ctx, lex, add, val, seme, EPOCHE_SENS24, PAZIENZA_SENS24, messaggi=messaggio)
        bv, bf = round(NM.bpc_pagine(m, ctx, val), 5), round(NM.bpc_pagine(m, ctx, fuori), 5)
        if modello != 'W3':
            diag = NM.diagnostica(m, ctx, fuori)
        penna = lambda: NM.Penna24(m, ctx, lex, hmm, cap)
        scrivi = lambda pen, regole, rp, rng, conta: scrivi_pagina24(m, ctx, lex, pen, regole, rp, voc, D, rng, conta)
    ris = OrderedDict([('lavoro', 'sens|%s|%s' % (testo, modello)), ('testo', testo), ('modello', modello), ('epoche', len(ca)), ('epoca_scelta', scelta),
                       ('bpc_validazione', bv), ('bpc_fuori', bf), ('curva_validazione', cv)])
    if modello == 'M1':
        lex_c = NM.costruisci_lessico([d for d in dps.values() if d['foglio'] in set(I7.fogli_della_piega(0)[0])], ctx)
    else:
        lex_c = lex
    ris['bit_parole'] = NM.nat_per_parola(m, ctx, fuori, lex_c, piantate=info['piantate'])
    if diag is not None:
        ris['diagnostica'] = diag
    if modello != 'M1':
        ris['appresi'] = NM.parametri_appresi(m)
    if True:
        f_add, f_val, f_fuori = I7.fogli_della_piega(0)
        pp = I7.per_pagina(sint)
        pag_fuori = [p for p in pp if I7.foglio_di(p) in set(f_fuori)]
        cnt = Counter(tuple(D(w)) for x in sint if I7.foglio_di(x['pagina']) in set(f_add) for w in x['parole'])
        noti = set(cnt)
        top = sorted(cnt, key=lambda w: (-cnt[w], w))[:KTOP_SENS]
        indice_top = NF.IndiceVicini({w: cnt[w] for w in top})
        indice_tutti = NF.IndiceVicini(cnt)
        rng = np.random.default_rng(seme_str('ia24scr', testo, modello))
        regole = I20.RegoleScrittura(voc)
        pen = penna()
        conta = Counter()
        t = []
        for p in pag_fuori:
            t += scrivi(pen, regole, pp[p], rng, conta)
        rows_gen = OrderedDict()
        for pag, ini, ps in t:
            rows_gen.setdefault(pag, []).append((bool(ini), [tuple(D(w)) for w in ps]))
        ris['scritto'] = misure_sens24(rows_gen, noti, indice_top, info['caselle'], indice_tutti)
        ris['piantato'] = misure_sens24(I22.righe_a_rows(sint, D, set(pag_fuori)), noti, indice_top, info['caselle'], indice_tutti)
        ris['modi_scrittura'] = OrderedDict(conta)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


cap = None                                                              # capacita' massima di una pagina (si fissa in avvia_processo)


def fissa_capacita():
    global cap
    voc = I7.vocabolario()
    cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in I7.per_pagina(I7.libro_vero()).values()) + 8
    I22.fissa_capacita()


# ---------------------------------------------------------------- catalogo dei libri da misurare

def nomi_giudicati():
    """Nomi dei libri giudicati: W<k>:i (i nuovi), M1:i e M5:i (ia20), E2:i (ia22), V21:k (v21 senza messaggio di ia01), ctrl:* (controlli)."""
    nomi = []
    for t in TIPI24:
        nomi += ['%s:%d' % (t, i) for i in range(1, N_LIBRI24 + 1) if os.path.exists(percorso_libro(t, i))]
    for p in RIF_M:
        nomi += ['M%d:%d' % (p, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento('M%d' % p, i))]
    for s in RIF_E:
        nomi += ['%s:%d' % (s, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento(s, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21]
    nomi += ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']
    return nomi


def nomi_struttura(nomi):
    """Per le misure di struttura: tutti i libri nuovi e di riferimento giudicati e i primi 10 V21."""
    out = [x for x in nomi if e_nuovo(x) or e_rifM(x) or e_rifE(x)]
    out += [x for x in nomi if x.startswith('V21:')][:10]
    return out


def nomi_f0_testi():
    """Per la fase 0: i riferimenti (M1, M5, E2) e il v21 (10 libri); i libri W si aggiungono nella fase D."""
    nomi = []
    for s in ['M%d' % p for p in RIF_M] + list(RIF_E):
        nomi += ['%s:%d' % (s, i) for i in range(1, N_RIF + 1) if os.path.exists(percorso_riferimento(s, i))]
    nomi += ['V21:%d' % k for k in CHIAVI_V21][:10]
    return nomi


def t_di(nome):
    k = int(nome.split(':')[1]) if ':' in nome and nome.split(':')[1].isdigit() else None
    if e_nuovo(nome):
        return I7.leggi_file(percorso_libro(nome.split(':')[0], k))
    if e_rifM(nome) or e_rifE(nome):
        return I7.leggi_file(percorso_riferimento(nome.split(':')[0], k))
    return I16.t_di(nome)


def rows_di(nome):
    if e_nuovo(nome) or e_rifM(nome) or e_rifE(nome):
        return I7.libro_A_da_righe(t_di(nome))
    return I16.rows_di(nome)


# ---------------------------------------------------------------- lavori di misura (fasi D e F)

def lavoro_K(f):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi_giudicati():
        r = rows_di(n)
        if r is not None:
            libri[n] = r
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(MISURE24, exist_ok=True)
    with open(os.path.join(MISURE24, 'K_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def lavoro_M(nome):
    """Come ia22.lavoro_M, ma i libri si leggono con `rows_di` e `t_di` di ia24."""
    import e266_discriminatore_forte as e266
    inizio = time.time()
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows = c['vere']
        g9 = I16.media_G9(k['vt266'])
    else:
        rows = rows_di(nome)
        g9 = I16.media_G9(e266.tabella(I7.righe_ini(t_di(nome)), k['rif266']))
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    ris = OrderedDict([('lavoro', 'M|%s' % nome), ('G9', g9)])
    ris.update(MS.lavoro_M(nome, pag, {p: c['fold'][p] for p in pag}))
    cp = {p: AP.conti_bordi({p: r}) for p, r in pag.items()}
    ris['bordi'] = AP.firma_da_conti(I20.somma_conti(list(cp.values())))
    if nome == 'vere':
        rng = np.random.default_rng(200024)
        ps = list(cp)
        bs = [AP.firma_da_conti(I20.somma_conti([cp[ps[i]] for i in rng.integers(0, len(ps), len(ps))])) for _ in range(200)]
        ris['bordi_ic'] = OrderedDict((kk, [float(np.nanpercentile([b[kk] for b in bs if b[kk] is not None], q)) for q in (2.5, 97.5)]) for kk in ris['bordi'])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_D(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi_struttura(nomi_giudicati()):
        testi[n] = rows_di(n)
    out, info = MS.lavoro_D(f, c, testi)
    pv = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] != f)
    cnt = Counter(w for rows in pv.values() for _, ws in rows for w in ws)
    forma, noti = R.Forma(cnt), set(cnt)
    fm = OrderedDict()
    for nome, rows in testi.items():
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        fm[nome] = R.costo_nuove(forma, pg, noti) if pg else [0.0, 0.0, 0, 0]
    return OrderedDict([('lavoro', 'D|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('forma', fm), ('secondi', round(time.time() - inizio, 1))])


def oggetti_f0():
    """Le cinque `Piega` della fase 0 (lessico, forma, caselle delle altre pieghe), una volta per processo."""
    if 'f0' not in _C:
        c = I7.contesto_A()
        glifi = I7.vocabolario()['unita']
        _C['f0'] = (OrderedDict((f, NF.Piega(c['vere'], c['fold'], f, glifi, KTOP)) for f in range(PIEGHE)), glifi)
    return _C['f0']


def risultato_f0(rows, nome, boot):
    c = I7.contesto_A()
    ogg, glifi = oggetti_f0()
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    M = NF.conta_pagine(pag, c['fold'], ogg, glifi)
    d, e, S = NF.riassunto(M, len(glifi), boot=NF.BOOT if boot else 0, seme=seme_str('ia24F0', nome))
    return OrderedDict([('derivate', d), ('errori', e), ('somma', [round(float(x), 3) for x in S])])


def lavoro_F0(nome):
    """Fase 0 su un testo (`vere`, un libro): le parole nuove (distanza dalle note, lunghezza, profilo, pezzi, costo di forma per posto, costo a caselle). Solo numeri."""
    inizio = time.time()
    c = I7.contesto_A()
    rows = c['vere'] if nome == 'vere' else rows_di(nome)
    ris = OrderedDict([('lavoro', 'F0|%s' % nome)])
    ris.update(risultato_f0(rows, nome, boot=(nome == 'vere')))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_F0c(modo):
    """Controllo della fase 0: il testo vero (nelle prove: latino) con le parole nuove sostituite da parole piantate ('ritocco', 'libero', 'caselle')."""
    inizio = time.time()
    c = I7.contesto_A()
    ogg, glifi = oggetti_f0()
    rows = NF.pianta(c['vere'], c['fold'], ogg, glifi, modo, seme_str('ia24F0c', modo))
    ris = OrderedDict([('lavoro', 'F0c|%s' % modo), ('piantato', modo)])
    ris.update(risultato_f0(rows, 'c' + modo, boot=True))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        tipo = args[0]
        if tipo == 'addestra':
            return addestra(args[1], args[2], int(args[3]))
        if tipo == 'rifaddestra':
            r = I20.addestra(int(args[1]), args[2], int(args[3]))
            r['lavoro'] = ident
            return r
        if tipo == 'rifaddestraE':
            r = I22.addestra(args[1], args[2], int(args[3]))
            r['lavoro'] = ident
            return r
        if tipo == 'lmA':
            return I7.lavoro_lmA(args[1], args[2])
        if tipo == 'sens':
            return lavoro_sens(args[1], args[2])
        if tipo == 'libro':
            return lavoro_libro(args[1], int(args[2]))
        if tipo == 'riflibro':
            return lavoro_riflibro(args[1], int(args[2]))
        if tipo == 'K':
            return lavoro_K(int(args[1]))
        if tipo == 'M':
            return lavoro_M(args[1])
        if tipo == 'D':
            return lavoro_D(int(args[1]))
        if tipo == 'F0':
            return lavoro_F0(args[1])
        if tipo == 'F0c':
            return lavoro_F0c(args[1])
        if tipo in ('O', 'caso', 'ctrlA', 'casoA'):
            return I7.lavoro(tuple(args))
        raise ValueError(tipo)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    I7.avvia_processo()
    fissa_capacita()


def esegui(lavori, processi, percorso, fatte):
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte and (not filtro or any(x in '|'.join(str(y) for y in a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: r[x] for x in ('epoca_scelta', 'bpc_validazione', 'bpc_fuori', 'AUC_e231', 'AUC_e266', 'AUC_A', 'AUC', 'G9') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


# ---------------------------------------------------------------- analisi e letture

def leggi_corse(percorso):
    return I16.leggi_corse(percorso)


def mf(x, d=3):
    return I20.mf(x, d)


def bpc_riferimento(sigla):
    """Bit per segno dei 10 modelli di un riferimento (M1, M5 di ia20; E2 di ia22), dalle schede json delle cache (solo numeri)."""
    v, f = [], []
    for k in range(PIEGHE):
        for r in (0, 1):
            p = I20.percorso_modello(int(sigla[1]), k, r, '.json') if sigla[0] == 'M' else I22.percorso_modello(sigla, k, r, '.json')
            if os.path.exists(p):
                d = json.load(open(p, encoding='utf-8'))
                v.append(d['bpc_validazione'])
                f.append(d['bpc_fuori'])
    return OrderedDict(modelli=len(v), validazione=mes(v), fuori=mes(f))


def bit_segno(r, chiave):
    """Bit per segno delle parole nuove o note di un controllo di sensibilita'."""
    b = r['bit_parole']
    return b['nat_' + chiave] / max(b['segni_' + chiave], 1) / math.log(2)


def lettura_sens(C):
    """Controlli di sensibilita' (fase Q): guadagno su M1 sulle parole nuove e sulle note, e misure sulle parole nuove scritte; esito per tipo (soglie SENS24)."""
    sv = lambda t, m: C.get('sens|%s|%s' % (t, m))
    ris = OrderedDict()

    def confronto(testo, m):
        b, r = sv(testo, 'M1'), sv(testo, m)
        if not b or not r:
            return None
        gp = (bit_segno(b, 'piantate') - bit_segno(r, 'piantate')) if b['bit_parole']['segni_piantate'] else None
        return OrderedDict(guadagno_validazione=b['bpc_validazione'] - r['bpc_validazione'], bit_nuove_M1=bit_segno(b, 'nuove'), bit_nuove=bit_segno(r, 'nuove'),
                           guadagno_nuove=bit_segno(b, 'nuove') - bit_segno(r, 'nuove'), guadagno_piantate=gp, bit_piantate_M1=bit_segno(b, 'piantate') if gp is not None else None,
                           bit_piantate=bit_segno(r, 'piantate') if gp is not None else None, bit_note_M1=bit_segno(b, 'note'), bit_note=bit_segno(r, 'note'),
                           peggio_note=bit_segno(r, 'note') - bit_segno(b, 'note'),
                           quota_nuove_segni=r['bit_parole']['segni_nuove'] / max(r['bit_parole']['segni_nuove'] + r['bit_parole']['segni_note'], 1))
    rit = OrderedDict()
    b = sv('ritocchi', 'M1')
    if b:
        rit['piantato'] = b['piantato']
        rit['M1'] = OrderedDict(bpc_validazione=b['bpc_validazione'], bit_nuove=bit_segno(b, 'nuove'), bit_note=bit_segno(b, 'note'), scritto=b['scritto'])
        for m in ('W1', 'W2'):
            r = sv('ritocchi', m)
            x = confronto('ritocchi', m)
            if not r or not x:
                continue
            post = (r.get('diagnostica') or {}).get('posteriori_lessico_nuove')
            dq = abs(r['scritto']['quota_nuove'] - r['piantato']['quota_nuove'])
            x.update(posteriori_lessico_nuove=post, scritto=r['scritto'], scarto_quota_nuove=dq, scarto_quota_nuove_M1=abs(b['scritto']['quota_nuove'] - b['piantato']['quota_nuove']),
                     massa_media=(r.get('diagnostica') or {}).get('massa_media'))
            x['riuscito'] = bool(x['guadagno_piantate'] >= SENS24['ritocchi_nuove'] and post is not None and post >= SENS24['ritocchi_posteriori'] and dq <= SENS24['ritocchi_quota']
                                 and x['peggio_note'] <= SENS24['note_max'])
            rit[m] = x
    ris['ritocchi'] = rit
    cas = OrderedDict()
    b = sv('caselle', 'M1')
    if b:
        cas['piantato'] = b['piantato']
        cas['M1'] = OrderedDict(bpc_validazione=b['bpc_validazione'], bit_nuove=bit_segno(b, 'nuove'), bit_note=bit_segno(b, 'note'), scritto=b['scritto'])
        r = sv('caselle', 'W3')
        x = confronto('caselle', 'W3')
        if r and x:
            bp = r['bit_parole']
            pp_, pa_ = bp['porta_piantate'] / max(bp['porta_piantate_n'], 1), bp['porta_altre'] / max(bp['porta_altre_n'], 1)
            x.update(scritto=r['scritto'], appresi=r.get('appresi'), porta_piantate=pp_, porta_altre=pa_, porta_differenza=pp_ - pa_)
            x['riuscito'] = bool(x['guadagno_piantate'] >= SENS24['caselle_nuove'] and x['peggio_note'] <= SENS24['note_max'] and x['porta_differenza'] >= SENS24['caselle_porta'])
            cas['W3'] = x
    ris['caselle'] = cas
    sen = OrderedDict()
    for m in ('W1', 'W2', 'W3'):
        x = confronto('senza', m)
        if x:
            r = sv('senza', m)
            x['posteriori_lessico_nuove'] = (r.get('diagnostica') or {}).get('posteriori_lessico_nuove')
            x['riuscito'] = bool(x['guadagno_validazione'] <= SENS24['senza_guadagno_max']) if m == 'W3' else bool(x['guadagno_nuove'] <= SENS24['senza_nuove_max'])
            sen[m] = x
    ris['senza'] = sen
    ok = {}
    for t in ('W1', 'W2'):
        ok[t] = bool(rit.get(t, {}).get('riuscito') and sen.get(t, {}).get('riuscito'))
    ok['W3'] = bool(cas.get('W3', {}).get('riuscito') and sen.get('W3', {}).get('riuscito'))
    return ris, ok


def lettura_f0(C, nomi_insiemi):
    """Dai risultati F0 (`C`: lavoro -> risultato) le statistiche per insieme di testi: media e errore sui libri (o l'errore da ricampionamento delle pagine per un solo testo)."""
    out = OrderedDict()
    for etich, nomi in nomi_insiemi.items():
        rs = [C[n] for n in nomi if n in C]
        if not rs:
            continue
        riga = OrderedDict(testi=len(rs))
        for k in F0_MISURE:
            xs = [r['derivate'][k] for r in rs]
            if len(rs) == 1:
                riga[k] = (xs[0], rs[0]['errori'].get(k))
            else:
                riga[k] = mes(xs)
        out[etich] = riga
    return out


def differenza(a, b, segno=1):
    """segno * (a - b), errore: a e b sono coppie (valore, errore)."""
    if a is None or b is None or a[0] is None or b[0] is None:
        return None, None
    return segno * (a[0] - b[0]), math.sqrt((a[1] or 0.0) ** 2 + (b[1] or 0.0) ** 2)


def lettura_soglia(d, e, minimo):
    """'presente' se d > 3 e e d > minimo; 'assente' se d <= 2 e; altrimenti 'zona grigia'."""
    if d is None:
        return 'non calcolabile'
    if d > F0_SOGLIE['errori'] * e and d > minimo:
        return 'presente'
    if d <= F0_SOGLIE['assente_errori'] * e:
        return 'assente'
    return 'zona grigia'


def analisi(corse, versioni):
    C = {c['lavoro']: c for c in corse if not c.get('errore')}
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in corse if c.get('errore') and c['lavoro'] not in C]
    c_ctx = I7.contesto_A()
    n_pag = len(c_ctx['ids'])
    out = OrderedDict(esperimento='ia24', solo_controlli=SOLO_CONTROLLI, versioni=versioni, errori=errori, tipi=list(TIPI24))
    # ---- modelli
    modelli = [C[k] for k in sorted(C) if k.startswith('addestra|')]
    out['modelli'] = [OrderedDict((k, v) for k, v in m.items() if k not in ('curva_validazione', 'curva_addestramento')) for m in modelli]
    bpc = OrderedDict()
    for t in TIPI24:
        ms = [m for m in modelli if m['tipo'] == t]
        if ms:
            bpc[t] = OrderedDict(modelli=len(ms), parametri=ms[0]['parametri'], validazione=mes([x['bpc_validazione'] for x in ms]), fuori=mes([x['bpc_fuori'] for x in ms]),
                                 epoche_scelte=mes([x['epoca_scelta'] for x in ms])[0], al_massimo=sum(bool(x['arrivata_al_massimo']) for x in ms),
                                 secondi_medi=statistics.mean(x['secondi'] for x in ms))
            if t != 'W3':
                dg = [x['diagnostica'] for x in ms if x.get('diagnostica')]
                bpc[t]['massa_lessico_media'] = mes([d['massa_media'] for d in dg])[0]
                bpc[t]['posteriori_lessico_nuove'] = mes([d['posteriori_lessico_nuove'] for d in dg])[0]
                bpc[t]['posteriori_lessico_note'] = mes([d['posteriori_lessico_note'] for d in dg])[0]
                bpc[t]['quota_nuove_fuori'] = mes([d['quota_nuove'] for d in dg])[0]
                bpc[t]['miscela'] = [mes([d['miscela'][k] for d in dg])[0] for k in range(4)]
    out['bpc'] = bpc
    out['bpc_riferimenti'] = OrderedDict((s, bpc_riferimento(s)) for s in ['M%d' % p for p in RIF_M] + list(RIF_E))
    out['appresi'] = OrderedDict((t, [m['appresi'] for m in modelli if m['tipo'] == t and m.get('appresi')]) for t in TIPI24)
    # ---- controlli dei giudici (come ia20)
    ctr = OrderedDict()
    pos = [C['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in C]
    caso = C.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=mes(pos)[0], soglia=I20.POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= I20.POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=I20.NEG_BANDA,
                                        riuscito=bool(caso) and all(I20.NEG_BANDA[0] <= caso[k] <= I20.NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    pa = OrderedDict((n, C['ctrlA|%s' % n].get('AUC_A') if 'ctrlA|%s' % n in C else None) for n in I7.NOMI_CTRL_A if n != 'righe')
    na = C['casoA|0']['AUC_A'] if 'casoA|0' in C else None
    ctr['A_positivo'] = OrderedDict(AUC=pa, soglia=I7.SOGLIA_POSITIVO_A, riuscito=pa.get('parole') is not None and all(v >= I7.SOGLIA_POSITIVO_A for v in pa.values() if v is not None))
    ctr['A_negativo'] = OrderedDict(AUC=na, banda=I20.NEG_BANDA, riuscito=na is not None and I20.NEG_BANDA[0] <= na <= I20.NEG_BANDA[1])
    profs = []
    for f in range(PIEGHE):
        p = os.path.join(MISURE24, 'K_f%d.pkl' % f)
        if os.path.exists(p):
            profs.append(pickle.load(open(p, 'rb')))
    prof = MS.unisci_profili(profs) if len(profs) == PIEGHE else None
    aucK = OrderedDict()
    if prof:
        for n in prof:
            if n != 'vere':
                a = MS.auc_da_profili(prof, n, n_pag)
                if a is not None:
                    aucK[n] = a
        neg = [MS.negativo_K(prof, s) for s in range(1, MS.NEG + 1)]
        v21K = [aucK[n] for n in aucK if n.startswith('V21:')]
        posK = OrderedDict((n[5:], aucK[n]) for n in aucK if n.startswith('ctrl:') and n != 'ctrl:righe')
        ctr['K_positivo'] = OrderedDict(AUC=posK, soglia=I20.POS_K, riuscito=bool(posK) and all(v >= I20.POS_K for v in posK.values()))
        ctr['K_negativo'] = OrderedDict(AUC=statistics.mean(neg), valori=neg, banda=I20.NEG_BANDA, riuscito=I20.NEG_BANDA[0] <= statistics.mean(neg) <= I20.NEG_BANDA[1])
        ctr['K_vede_v21'] = OrderedDict(AUC=mes(v21K)[0], soglia=I20.K_VEDE_V21, riuscito=bool(v21K) and statistics.mean(v21K) >= I20.K_VEDE_V21)
    ok_paper = ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito']
    ok_K = bool(prof) and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito'] and ctr['K_vede_v21']['riuscito']
    ok_A = ctr['A_positivo']['riuscito'] and ctr['A_negativo']['riuscito']
    out['controlli'] = ctr
    # ---- controlli di sensibilita' (fase Q)
    sens, sens_ok = lettura_sens(C)
    out['sensibilita'] = sens
    # ---- libri e giudici per etichetta
    lib = OrderedDict()
    for t in TIPI24:
        lib[t] = [C['libro|%s|%d' % (t, i)] for i in range(1, N_LIBRI24 + 1) if 'libro|%s|%d' % (t, i) in C]
    for p in RIF_M:
        lib['M%d' % p] = [C['riflibro|M%d|%d' % (p, i)] for i in range(1, N_RIF + 1) if 'riflibro|M%d|%d' % (p, i) in C]
    for s in RIF_E:
        lib[s] = [C['riflibro|%s|%d' % (s, i)] for i in range(1, N_RIF + 1) if 'riflibro|%s|%d' % (s, i) in C]
    giud, val = OrderedDict(), OrderedDict()
    for lab in ETICHETTE:
        rs = lib.get(lab) or []
        if not rs:
            continue
        v = OrderedDict()
        v['e231'], v['e266'] = mes([r['AUC_e231'] for r in rs]), mes([r['AUC_e266'] for r in rs])
        v['K'] = mes([aucK.get('%s:%d' % (lab, r['i'])) for r in rs])
        v['A'] = mes([r.get('AUC_A') for r in rs])
        g = OrderedDict(libri=len(rs), e231=v['e231'], e266=v['e266'], K=v['K'], A=v['A'])
        g['per_replica'] = OrderedDict((j, [mes([r[k] for r in rs if r['replica'] == rp]) for rp in (0, 1)]) for j, k in (('e231', 'AUC_e231'), ('e266', 'AUC_e266')))
        g['repliche_diverse'] = OrderedDict((j, bool(all(x[0] is not None and x[1] is not None for x in pr) and abs(pr[0][0] - pr[1][0]) > 2 * math.sqrt(pr[0][1] ** 2 + pr[1][1] ** 2)))
                                            for j, pr in g['per_replica'].items())
        g['gruppi_e266'] = OrderedDict((n, statistics.mean(r['gruppi_e266'][n] for r in rs)) for n in rs[0]['gruppi_e266'] if rs[0]['gruppi_e266'][n] is not None)
        giud[lab] = g
        val[lab] = v
    R07 = OrderedDict(v21_A=[])
    C07 = {x['lavoro']: x for x in leggi_corse(I20.CORSE_IA07)}
    for k in CHIAVI_V21:
        r = C07.get('rifA|%d' % k)
        if r and r.get('AUC_A_b') is not None:
            R07['v21_A'].append(r['AUC_A_b'])
    v21 = OrderedDict(libri=len(CHIAVI_V21), e231=(I7.V21['AUC_e231'][0], I7.V21['AUC_e231'][1]), e266=(I7.V21['AUC_e266'][0], I7.V21['AUC_e266'][1]),
                      K=mes([aucK[n] for n in aucK if n.startswith('V21:')]), A=mes(R07['v21_A']))
    out['giudici'] = OrderedDict(tipi=giud, v21=v21)
    # ---- copia a memoria e ripetizioni
    rif_copia = I7.copia_riferimenti()
    nat = I7.quote(rif_copia['naturale'])
    rep_nat = MS.ripetizioni_interne(OrderedDict((p, [x['parole'] for x in rr]) for p, rr in I7.per_pagina(I7.libro_vero()).items()))
    k4 = 'righe uguali a una precedente nella pagina (>= 4 parole)'
    ks = 'righe uguali alla riga sopra (>= 2 parole)'
    kp = 'parole uguali alla parola prima'
    nat4 = rep_nat[k4][0] / rep_nat[k4][1] if rep_nat[k4][1] else 0.0
    natp = rep_nat[kp][0] / rep_nat[kp][1] if rep_nat[kp][1] else 0.0
    cop, rip, lett_copia = OrderedDict(), OrderedDict(), OrderedDict()
    for lab in ETICHETTE:
        rs = lib.get(lab) or []
        if not rs:
            continue
        qs = [I7.quote(r['copia']) for r in rs]
        cop[lab] = OrderedDict((k, mes([q[k] for q in qs])) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))
        rip[lab] = OrderedDict((k, mes([r['ripetizioni'][k][0] / r['ripetizioni'][k][1] if r['ripetizioni'][k][1] else None for r in rs])) for k in rep_nat)
        m5, mr = cop[lab]['5-grammi'][0], cop[lab]['righe intere'][0]
        l5 = 'nessuna copia rilevante' if m5 is not None and m5 <= I20.COPIA_5GRAMMI[0] else 'copia' if m5 is not None and m5 > I20.COPIA_5GRAMMI[1] else 'zona grigia'
        lr = 'nessuna copia rilevante' if mr is not None and mr <= I20.COPIA_RIGHE[0] else 'copia' if mr is not None and mr > I20.COPIA_RIGHE[1] else 'zona grigia'
        r4, rsopra, rpp = rip[lab][k4][0], rip[lab][ks][0], rip[lab][kp][0]
        avvita = bool((r4 is not None and r4 > I20.AVVITA_MIN and r4 > I20.AVVITA_VOLTE * max(nat4, 1e-9)) or (rsopra is not None and rsopra > I20.RIGA_SOPRA_MAX))
        nuove, rn = cop[lab]['parole nuove'][0], nat['parole nuove']
        lett_copia[lab] = OrderedDict([('5-grammi', l5), ('righe', lr), ('copia', 'copia' in (l5, lr)), ('zona_grigia', 'zona grigia' in (l5, lr)), ('si_avvita', avvita),
                                       ('parola_prima_alta', bool(rpp is not None and natp and rpp > I20.PAROLA_PRIMA_VOLTE * natp)),
                                       ('parole_nuove_ok', bool(nuove is not None and rn and I20.NUOVE_FASCIA[0] * rn <= nuove <= I20.NUOVE_FASCIA[1] * rn))])
    modi = OrderedDict()
    for t in TIPI24:
        tot = Counter()
        for r in lib.get(t) or []:
            tot.update(r.get('modi_scrittura', {}))
        if tot:
            modi[t] = OrderedDict(tot)
    out['copia'] = OrderedDict(tipi=cop, naturale=nat, ripetizioni=rip, ripetizioni_naturali=OrderedDict((k, v[0] / v[1] if v[1] else None) for k, v in rep_nat.items()),
                               letture=lett_copia, modi_scrittura=modi)
    # ---- struttura
    M = {k[2:]: v for k, v in C.items() if k.startswith('M|')}
    Dj = [C['D|%d' % f] for f in range(PIEGHE) if 'D|%d' % f in C]
    struttura, vero = OrderedDict(), OrderedDict()
    if 'vere' in M and len(Dj) == PIEGHE:
        Mv = MS.copia_netta_lambda(M['vere'], con_intervallo=True)
        b = M['vere']['bordi']
        vero = OrderedDict(copia_netta=Mv['copia_netta'], lam=Mv['lam'], contatto=Mv['contatto'], D=MS.D_da_pieghe([x['D']['vere'] for x in Dj]), G9=M['vere'].get('G9'),
                           bordi_inizio=statistics.mean(b['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung')), bordi_fine=statistics.mean(b['fine_%s' % f] for f in ('primo', 'ultimo', 'lung')),
                           parole_nuove=nat['parole nuove'])
        fv = [x['forma']['vere'] for x in Dj]
        vero['costo_forma'] = sum(x[0] for x in fv) / max(sum(x[1] for x in fv), 1)
        vero['intervalli'] = OrderedDict(copia_netta=Mv['copia_netta_ic'], lam=Mv['lam_ic'], bordi=M['vere'].get('bordi_ic'))
        per_set = OrderedDict()
        for nome, r in M.items():
            if nome == 'vere':
                continue
            s = etichetta(nome)
            x = MS.copia_netta_lambda(r)
            x['D'] = MS.D_da_pieghe([d['D'][nome] for d in Dj]) if all(nome in d['D'] for d in Dj) else None
            x['G9'] = r.get('G9')
            x['bordi_inizio'] = statistics.mean(r['bordi']['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung'))
            x['bordi_fine'] = statistics.mean(r['bordi']['fine_%s' % f] for f in ('primo', 'ultimo', 'lung'))
            fm = [d['forma'][nome] for d in Dj if nome in d['forma']]
            x['parole_nuove'] = sum(y[2] for y in fm) / max(sum(y[3] for y in fm), 1) if fm else None
            x['costo_forma'] = sum(y[0] for y in fm) / max(sum(y[1] for y in fm), 1) if fm else None
            per_set.setdefault(s, []).append(x)
        for s, xs in per_set.items():
            struttura[s] = OrderedDict((m_, mes([x[m_] for x in xs])) for m_ in MISURE_STR)
            struttura[s]['libri'] = len(xs)
    out['vero'] = vero
    out['struttura'] = struttura
    # ---- letture: validita'
    letture = OrderedDict()
    letture['validita'] = OrderedDict(paper=ok_paper, K=ok_K, A=ok_A, sensibilita=OrderedDict((t, bool(o)) for t, o in sens_ok.items()))
    for lab in val:
        s = struttura.get(lab, {})
        for m_ in MISURE_STR:
            val[lab][m_] = s.get(m_, (None, None))
    # ---- L1: il costo di forma al vero, senza rompere contatto, D e quota di parole nuove
    L1 = OrderedDict()
    chiavi = ['costo_forma', 'contatto', 'D', 'parole_nuove']
    for lab in ETICHETTE:
        if lab not in val or not vero:
            continue
        fl = OrderedDict((m_, I20.al_vero(val[lab][m_], vero.get(m_))) for m_ in chiavi)
        dist = OrderedDict((m_, (abs(val[lab][m_][0] - vero[m_]) / abs(vero[m_])) if val[lab][m_][0] is not None and vero.get(m_) else None) for m_ in chiavi)
        L1[lab] = OrderedDict(al_vero=fl, distanza_relativa=dist, forma_al_vero=bool(fl['costo_forma']), resto_al_vero=bool(all(fl[m_] for m_ in ('contatto', 'D', 'parole_nuove'))),
                              tutti_al_vero=bool(all(fl.values())), valori=OrderedDict((m_, val[lab][m_][0]) for m_ in chiavi))
    letture['L1_forma'] = OrderedDict(per_tipo=L1, forma_al_vero=[t for t in TIPI24 if t in L1 and L1[t]['forma_al_vero']], esiste=[t for t in TIPI24 if t in L1 and L1[t]['tutti_al_vero']],
                                      vero=OrderedDict((m_, vero.get(m_)) for m_ in chiavi))
    # ---- L2: ogni W contro M1 (e W2 contro E2)
    L2 = OrderedDict()
    confronti = [(t, 'M1') for t in TIPI24] + ([('W2', 'E2')] if 'W2' in TIPI24 else [])
    for t, rif in confronti:
        if t not in val or rif not in val or not vero:
            continue
        cl = OrderedDict()
        for m_ in MISURE_STR:
            cl[m_] = I20.classe_misura(val[rif][m_], val[t][m_], vero.get(m_))
        for j in GIUDICI:
            cl[j] = I20.classe_misura(val[rif][j], val[t][j], None)
        x = I20.lettura_ingrediente(0, cl, MISURE_FORMA)
        x['classi'] = cl
        x['sensibilita'] = 'provata' if sens_ok.get(t) else 'NON provata (con riserva)'
        if not (ok_paper and ok_K):
            x['nota_giudici'] = 'giudici non validi: le colonne dei giudici non si leggono'
        L2['%s contro %s' % (t, rif)] = x
    letture['L2_contro_M1'] = L2
    # ---- L3: contro il v21 (regola di ia16/ia20)
    L3 = OrderedDict()
    for lab in val:
        cl = I16.classe_giudici({j: val[lab][j] for j in ('e231', 'e266', 'K')}, v21)
        L3[lab] = OrderedDict(esito=I16.esito_v21(cl), giudici=cl, media_tre=statistics.mean(val[lab][j][0] for j in ('e231', 'e266', 'K') if val[lab][j][0] is not None)
                              if all(val[lab][j][0] is not None for j in ('e231', 'e266', 'K')) else None)
    if not (ok_paper and ok_K):
        for x in L3.values():
            x['esito'] = 'lettura non valida (controllo dei giudici fallito: ' + ', '.join(n for n, o in (('paper', ok_paper), ('K', ok_K)) if not o) + ')'
    else:
        for nm, x in L3.items():
            lc = lett_copia.get(nm)
            if lc and lc['copia']:
                x['esito'] += ' ma NON VALE: copia a memoria sopra la soglia'
            elif lc and (lc['zona_grigia'] or lc['si_avvita']):
                x['esito'] += ' (con riserva: copia in zona grigia o scrittura che si avvita)'
    mig = [(x['media_tre'], lab) for lab, x in L3.items() if x['media_tre'] is not None]
    letture['L3_contro_v21'] = OrderedDict(migliore=min(mig)[1] if mig else None, per_tipo=L3)
    # ---- L4: fase 0 sulle parole nuove
    nomi_ins = OrderedDict([('vero', ['F0|vere']), ('v21', ['F0|V21:%d' % k for k in CHIAVI_V21][:10]), ('M1', ['F0|M1:%d' % i for i in range(1, N_RIF + 1)]),
                            ('M5', ['F0|M5:%d' % i for i in range(1, N_RIF + 1)]), ('E2', ['F0|E2:%d' % i for i in range(1, N_RIF + 1)])])
    for t in TIPI24:
        nomi_ins[t] = ['F0|%s:%d' % (t, i) for i in range(1, N_LIBRI24 + 1)]
    for md in F0C_TESTI:
        nomi_ins['piantato_' + md] = ['F0c|' + md]
    F = {k: v for k, v in C.items() if k.startswith('F0|') or k.startswith('F0c|')}
    f0 = lettura_f0(F, nomi_ins)
    ctrl = OrderedDict()
    if all('piantato_' + m in f0 for m in ('ritocco', 'libero')):
        d, e = differenza(f0['piantato_ritocco']['top_2'], f0['piantato_libero']['top_2'])
        ctrl['ritocco'] = OrderedDict(differenza=d, errore=e, lettura=lettura_soglia(d, e, F0_SOGLIE['minimo_top']))
    if all('piantato_' + m in f0 for m in ('caselle', 'libero')):
        d, e = differenza(f0['piantato_libero']['costo_caselle'], f0['piantato_caselle']['costo_caselle'])
        ctrl['caselle'] = OrderedDict(differenza=d, errore=e, lettura=lettura_soglia(d, e, F0_SOGLIE['minimo_caselle']))
    ok0 = bool(ctrl.get('ritocco', {}).get('lettura') == 'presente' and ctrl.get('caselle', {}).get('lettura') == 'presente')
    lett4 = OrderedDict()
    rif = [x for x in ('M1', 'E2') if x in f0]
    if 'vero' in f0 and rif:
        def media_rif(k):
            xs = [f0[x][k] for x in rif if f0[x][k][0] is not None]
            return (statistics.mean(x[0] for x in xs), math.sqrt(sum((x[1] or 0.0) ** 2 for x in xs)) / len(xs)) if xs else (None, None)
        d, e = differenza(f0['vero']['top_2'], media_rif('top_2'))
        lett4['ritocco'] = OrderedDict(differenza=d, errore=e, lettura=lettura_soglia(d, e, F0_SOGLIE['minimo_top']))
        d, e = differenza(media_rif('costo_caselle'), f0['vero']['costo_caselle'])
        lett4['caselle'] = OrderedDict(differenza=d, errore=e, lettura=lettura_soglia(d, e, F0_SOGLIE['minimo_caselle']))
        a, b = lett4['ritocco']['lettura'], lett4['caselle']['lettura']
        if not ok0:
            lett4['esito'] = 'lettura non valida (controlli della fase 0 falliti)'
        elif a == 'presente' and b != 'presente':
            lett4['esito'] = 'regge il ritocco del lessico'
        elif b == 'presente' and a != 'presente':
            lett4['esito'] = 'reggono le caselle'
        elif a == 'presente' and b == 'presente':
            lett4['esito'] = 'reggono tutte e due'
        elif a == 'assente' and b == 'assente':
            lett4['esito'] = 'nessuna delle due'
        else:
            lett4['esito'] = 'zona grigia'
        lett4['rif'] = rif
    letture['L4_fase0'] = OrderedDict(controlli=ctrl, controlli_ok=ok0, lettura=lett4, insiemi=f0)
    out['valori'] = OrderedDict((lab, OrderedDict((k, x) for k, x in v.items())) for lab, v in val.items())
    out['letture'] = letture
    out['tempi_minuti'] = OrderedDict()
    for tipo in ('addestra', 'sens', 'libro', 'riflibro', 'K', 'M', 'D', 'F0'):
        s = [v['secondi'] for k, v in C.items() if k.startswith(tipo + '|') and v.get('secondi')]
        if s:
            out['tempi_minuti'][tipo] = OrderedDict(lavori=len(s), media=round(statistics.mean(s) / 60, 1), massimo=round(max(s) / 60, 1), totale=round(sum(s) / 60, 1))
    json.dump(out, open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(out)
    return out


def scrivi_md(o):
    L = o['letture']
    md = ['# IA24 (ia24) — Che cosa distingue le parole nuove del Voynich da quelle degli imitatori', '',
          'Preregistrazione: `preregistrazioni/ia24.md`.%s' % (' **Prova sui soli controlli (libro latino), non sul Voynich.**' if o['solo_controlli'] else ''), '',
          '- Versioni: %s.' % ', '.join('%s %s' % kv for kv in o['versioni'].items()), '']
    if o['errori']:
        md += ['**Lavori falliti:** ' + '; '.join('%s (%s)' % (e['lavoro'], e['errore']) for e in o['errori']), '']
    c = o['controlli']
    md += ['## Controlli dei giudici', '']
    md.append('- Giudici del paper, positivo: AUC %s, soglia ≥ %s → %s. Negativo: giudice 1 %s, giudice 2 %s → %s.' % (
        nu(c['paper_positivo']['AUC']), nu(I20.POS_PAPER, 2), nu(c['paper_positivo']['riuscito']), nu(c['paper_negativo']['AUC_e231']), nu(c['paper_negativo']['AUC_e266']), nu(c['paper_negativo']['riuscito'])))
    if 'K_positivo' in c:
        md.append('- K, positivo: %s → %s. Negativo: %s → %s. K vede il v21 (AUC %s) → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['K_positivo']['AUC'].items()), nu(c['K_positivo']['riuscito']),
                                                                                              nu(c['K_negativo']['AUC']), nu(c['K_negativo']['riuscito']), nu(c['K_vede_v21']['AUC']), nu(c['K_vede_v21']['riuscito'])))
    md.append('- A (riportato, non decide), positivo: %s → %s. Negativo: %s → %s.' % (', '.join('%s %s' % (k, nu(v)) for k, v in c['A_positivo']['AUC'].items()), nu(c['A_positivo']['riuscito']),
                                                                                   nu(c['A_negativo']['AUC']), nu(c['A_negativo']['riuscito'])))
    s = o['sensibilita']
    md += ['', '## Controlli di sensibilità (testi sintetici)', '']
    for t, x in s['ritocchi'].items():
        if t == 'piantato':
            md.append('Testo con ritocchi piantati (fogli tenuti fuori della piega 0): quota di parole nuove %s; fra le nuove a 1 modifica da una parola nota %s, a <= 2 %s.' % (nu(x['quota_nuove']), nu(x['d1']), nu(x['d12'])))
        elif t == 'M1':
            md.append('- M1: validazione %s; bit per segno sulle parole nuove %s, sulle note %s; nuove scritte %s (a 1 modifica %s).' % (
                nu(x['bpc_validazione']), nu(x['bit_nuove']), nu(x['bit_note']), nu(x['scritto']['quota_nuove']), nu(x['scritto']['d1'])))
        else:
            md.append('- %s: guadagno su M1 sulle parole piantate %s bit per segno (soglia >= %s; sulle nuove %s), sulle note %s rispetto a M1 (al massimo +%s); quota a posteriori del lessico sulle nuove %s (>= %s); nuove scritte %s, scarto dal piantato %s (<= %s; M1 %s) -> %s.' % (
                t, nu(x['guadagno_piantate']), nu(SENS24['ritocchi_nuove']), nu(x['guadagno_nuove']), nu(x['peggio_note']), nu(SENS24['note_max']), nu(x['posteriori_lessico_nuove']), nu(SENS24['ritocchi_posteriori']),
                nu(x['scritto']['quota_nuove']), nu(x['scarto_quota_nuove']), nu(SENS24['ritocchi_quota']), nu(x['scarto_quota_nuove_M1']), nu(x['riuscito'])))
    for t, x in s['caselle'].items():
        if t == 'piantato':
            md.append('Testo con parole a caselle piantate: quota di nuove %s, conformi alla grammatica %s.' % (nu(x['quota_nuove']), nu(x['conforme'])))
        elif t == 'M1':
            md.append('- M1: validazione %s; bit per segno sulle parole nuove %s, sulle note %s; nuove scritte conformi %s.' % (nu(x['bpc_validazione']), nu(x['bit_nuove']), nu(x['bit_note']), nu(x['scritto']['conforme'])))
        else:
            md.append('- %s: guadagno su M1 sulle parole piantate %s bit per segno (soglia >= %s; sulle nuove %s), sulle note %s rispetto a M1 (al massimo +%s); porta aperta %s sulle piantate contro %s sulle altre (differenza >= %s); nuove scritte conformi %s -> %s.' % (
                t, nu(x['guadagno_piantate']), nu(SENS24['caselle_nuove']), nu(x['guadagno_nuove']), nu(x['peggio_note']), nu(SENS24['note_max']), nu(x['porta_piantate']), nu(x['porta_altre']), nu(SENS24['caselle_porta']),
                nu(x['scritto']['conforme']), nu(x['riuscito'])))
    md.append('- Testo senza niente di piantato: ' + '; '.join('%s guadagno in validazione %s, sulle nuove %s (%s)' % (
        m, nu(x['guadagno_validazione']), nu(x['guadagno_nuove']), ('<= %s per W3: %s' % (nu(SENS24['senza_guadagno_max']), nu(x['riuscito']))) if m == 'W3' else ('nuove <= %s: %s' % (nu(SENS24['senza_nuove_max']), nu(x['riuscito'])))) for m, x in s['senza'].items()) + '.')
    md += ['', '## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)', '', '| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa del lessico | posteriori del lessico: nuove / note | miscela (libero, 0, 1, 2 modifiche) | minuti per modello |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for nm, x in o['bpc'].items():
        md.append('| %s | %d | %s | %s | %s | %d | %s | %s / %s | %s | %.1f |' % (nm, x['parametri'], mf(x['validazione']), mf(x['fuori']), nu(x['epoche_scelte'], 1), x['al_massimo'], nu(x.get('massa_lessico_media')),
                                                                                  nu(x.get('posteriori_lessico_nuove')), nu(x.get('posteriori_lessico_note')),
                                                                                  ', '.join(nu(y, 3) for y in x['miscela']) if x.get('miscela') else '—', x['secondi_medi'] / 60))
    for nm, x in o['bpc_riferimenti'].items():
        md.append('| %s (cache) | — | %s | %s | — | — | — | — | — | — |' % (nm, mf(x['validazione']), mf(x['fuori'])))
    md += ['', 'Numeri imparati (medie): ' + '; '.join('%s %s' % (t, json.dumps(x[:2], default=float)) for t, x in o['appresi'].items() if x) + ' (prime due repliche).']
    g = o['giudici']
    md += ['', '## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)', '', '| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |', '|---|---|---|---|---|---|']
    for nm, x in g['tipi'].items():
        md.append('| %s | %d | %s | %s | %s | %s |' % (nm, x['libri'], mf(x['e231']), mf(x['e266']), mf(x['K']), mf(x['A'])))
    md.append('| v21 | %d | %s (paper) | %s (paper) | %s | %s |' % (g['v21']['libri'], mf(g['v21']['e231']), mf(g['v21']['e266']), mf(g['v21']['K']), mf(g['v21']['A'])))
    md += ['', 'Repliche diverse (più di 2 errori): ' + '; '.join('%s: %s' % (nm, ', '.join('%s %s' % (j, nu(b)) for j, b in x['repliche_diverse'].items())) for nm, x in g['tipi'].items()) + '.']
    md += ['', '## Struttura (media ± errore standard sui libri)', '', '| testo | ' + ' | '.join(MISURE_STR.values()) + ' |', '|' + '---|' * (len(MISURE_STR) + 1)]
    v = o['vero']
    if v:
        md.append('| **vero** | ' + ' | '.join(nu(v.get(m_), 4) for m_ in MISURE_STR) + ' |')
        for nm in ETICHETTE + ['V21']:
            x = o['struttura'].get(nm)
            if x:
                md.append('| %s (%d libri) | ' % (nm, x['libri']) + ' | '.join(mf(x[m_], 4) for m_ in MISURE_STR) + ' |')
    md += ['', '## Letture preregistrate', '']
    va = L['validita']
    md.append('- Validità: giudici del paper %s, K %s, A %s; sensibilità: %s; controlli della fase 0 %s.' % (nu(va['paper']), nu(va['K']), nu(va['A']), ', '.join('%s %s' % (k, nu(b)) for k, b in va['sensibilita'].items()), nu(L['L4_fase0']['controlli_ok'])))
    l1 = L['L1_forma']
    md += ['', '### L1: il costo di forma delle parole nuove al vero, senza rompere contatto, D e quota di parole nuove?', '',
           '**Imitatori con costo di forma al vero: %s. Con anche contatto, D e parole nuove al vero: %s.**' % (', '.join(l1['forma_al_vero']) or 'nessuno', ', '.join(l1['esiste']) or 'nessuno'), '',
           '| tipo | costo di forma | contatto | D | parole nuove | forma al vero | resto al vero | tutti |', '|---|---|---|---|---|---|---|---|',
           '| vero | ' + ' | '.join(nu(l1['vero'][m_], 3) for m_ in ('costo_forma', 'contatto', 'D', 'parole_nuove')) + ' | | | |']
    for t, x in l1['per_tipo'].items():
        md.append('| %s | ' % t + ' | '.join('%s%s' % (nu(x['valori'][m_], 3), ' ✓' if x['al_vero'][m_] else '') for m_ in ('costo_forma', 'contatto', 'D', 'parole_nuove')) +
                  ' | %s | %s | %s |' % (nu(x['forma_al_vero']), nu(x['resto_al_vero']), nu(x['tutti_al_vero'])))
    md += ['', '### L2: ogni imitatore contro M1 (bersagli: costo di forma e parole nuove)', '', '| confronto | lettura | misure corrette | misure rotte | sensibilità |', '|---|---|---|---|---|']
    nomi_m = dict(MISURE_STR, **GIUDICI)
    for k, x in L['L2_contro_M1'].items():
        md.append('| %s | **%s** | %s | %s | %s |' % (k, x['esito'], ', '.join(nomi_m[m_] for m_ in x['corrette']) or '—', ', '.join(nomi_m[m_] for m_ in x['rotte']) or '—', x['sensibilita']))
    l3 = L['L3_contro_v21']
    md += ['', '### L3: contro il v21', '', '- **Tipo migliore (AUC media di e231, e266, K): %s.**' % l3['migliore']]
    for nm, x in l3['per_tipo'].items():
        md.append('  - %s: %s (%s).' % (nm, x['esito'], '; '.join('%s %s (diff. %s ± %s)' % (j, y['lettura'], nu(y['differenza']), nu(y['errore'])) for j, y in x['giudici'].items())))
    f4 = L['L4_fase0']
    md += ['', '### L4: fase 0 — dove nasce lo scarto delle parole nuove', '']
    for sg, x in f4['controlli'].items():
        md.append('- Controllo %s: differenza %s ± %s → **%s**.' % (sg, nu(x['differenza']), nu(x['errore']), x['lettura']))
    if f4['lettura']:
        for k in ('ritocco', 'caselle'):
            x = f4['lettura'][k]
            md.append('- Vero contro M1 e E2, %s: differenza %s ± %s → **%s**.' % (k, nu(x['differenza']), nu(x['errore']), x['lettura']))
        md.append('- **Esito: %s.**' % f4['lettura']['esito'])
    nomi_ins = list(f4['insiemi'])
    md += ['', '| misura | ' + ' | '.join(nomi_ins) + ' |', '|' + '---|' * (len(nomi_ins) + 1)]
    for k, nm in F0_MISURE.items():
        md.append('| %s | ' % nm + ' | '.join(mf(f4['insiemi'][e][k], 3) for e in nomi_ins) + ' |')
    cp = o['copia']
    md += ['', '## Copia a memoria e ripetizioni (soglie severe di ia20)', '', '| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |', '|---|---|---|---|---|']
    for nm, q in cp['tipi'].items():
        md.append('| %s | %s |' % (nm, ' | '.join(mf(q[k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove'))))
    md.append('| naturale | %s |' % ' | '.join(nu(cp['naturale'][k], 4) for k in ('5-grammi', '3-grammi', 'righe intere', 'parole nuove')))
    for nm, x in cp['letture'].items():
        md.append('- %s: 5-grammi → %s, righe → %s; si avvita: %s; parola uguale alla prima alta: %s; parole nuove %s.' % (nm, x['5-grammi'], x['righe'], nu(x['si_avvita']), nu(x['parola_prima_alta']), 'nella fascia' if x['parole_nuove_ok'] else 'FUORI fascia'))
    if cp['modi_scrittura']:
        md.append('\nModi di scrittura delle parole (conti sui libri): ' + '; '.join('%s: %s' % (t, ', '.join('%s %d' % kv for kv in x.items())) for t, x in cp['modi_scrittura'].items()) + '.')
    md += ['', '## Tempi (minuti per lavoro)', '']
    for k, x in o['tempi_minuti'].items():
        md.append('- %s: %d lavori, media %s, massimo %s, totale %s.' % (k, x['lavori'], x['media'], x['massimo'], x['totale']))
    open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')


# ---------------------------------------------------------------- principale

def lavori_fase(fase):
    if fase == 'A':
        mancanti = [('lmA', s, k) for s in I7.SEMI_A for k in range(PIEGHE) if not os.path.exists(I7.percorso_lmA(s, k))]
        rif = []
        if RIF24 == 'ricalcola':
            rif = [('rifaddestra', p, k, r) for p in RIF_M for r in REPLICHE24 for k in range(PIEGHE)]
            rif += [('rifaddestraE', t, k, r) for t in RIF_E for r in REPLICHE24 for k in range(PIEGHE)]
        # i piu' lenti per primi (W2, W1, W3), a pari tipo prima la replica 0
        ordine = [t for t in ('W2', 'W1', 'W3') if t in TIPI24]
        return mancanti + rif + [('addestra', t, k, r) for t in ordine for r in REPLICHE24 for k in range(PIEGHE)]
    if fase == 'Q':
        return [('sens', t, m) for t, ms in SENS_MODELLI.items() for m in ms if m == 'M1' or m in TIPI24]
    if fase == 'C':
        rif = [('riflibro', 'M%d' % p, i) for p in RIF_M for i in range(1, N_RIF + 1)] + [('riflibro', s, i) for s in RIF_E for i in range(1, N_RIF + 1)]
        return rif + [('libro', t, i) for t in [x for x in ('W2', 'W1', 'W3') if x in TIPI24] for i in range(1, N_LIBRI24 + 1)]
    if fase == 'F':
        return [('F0c', n) for n in F0C_TESTI] + [('F0', 'vere')] + [('F0', n) for n in nomi_f0_testi()]
    if fase == 'D':
        nomi = nomi_giudicati()
        return ([('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0), ('casoA', 0)] + [('ctrlA', n) for n in I7.NOMI_CTRL_A] + [('K', f) for f in range(PIEGHE)] +
                [('D', f) for f in range(PIEGHE)] + [('M', 'vere')] + [('M', n) for n in nomi_struttura(nomi)] + [('F0', n) for n in nomi if e_nuovo(n)])
    return []


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__), ('nuove', NM.VERSIONE), ('echi', EM.VERSIONE), ('gradini', GM.VERSIONE)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    for d in (MOD24, LIBRI24, MISURE24, VICINI24):
        os.makedirs(d, exist_ok=True)
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni, riga massima %d; tipi %s; PICCOLO %s; riferimenti %s' % (
        'controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe), len(I7.per_pagina(righe)), len(voc['unita']), voc['lmax'], TIPI24, PICCOLO, RIF24), flush=True)
    percorso = os.path.join(USCITA, 'ia24_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AQCFDS')
    for fase in 'AQCFD':
        if fase in fasi:
            lavori = lavori_fase(fase)
            if fase == 'A' and 'Q' in fasi:        # i controlli di sensibilita' girano insieme ai modelli (stesso gruppo di processi)
                lavori = lavori_fase('Q') + lavori
            if fase == 'Q' and 'A' in fasi:
                continue
            print('== fase %s: %d lavori' % (fase, len(lavori)), flush=True)
            esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        l1 = o['letture']['L1_forma']
        print('L1: costo di forma al vero: %s; con anche contatto, D e parole nuove: %s' % (', '.join(l1['forma_al_vero']) or 'nessuno', ', '.join(l1['esiste']) or 'nessuno'), flush=True)


if __name__ == '__main__':
    main()
