# -*- coding: utf-8 -*-
"""Esperimento IA31 (ia31): l'automa minimo della forma delle parole.

Domanda: qual e' la macchina piu' piccola (un automa a stati finiti probabilistico, oppure una grammatica a caselle imparata dai dati) che genera le parole del
Voynich? Quanto e' piu' piccola di quella che serve per una lingua, un cifrario, il v21 o un imitatore? E quanto dello scarto di forma che gli imitatori mancano nel
secondo e nel terzo glifo (ia24) sta dentro quella macchina? Proposte: C4 di REVIEW_FABLE.md e la 4 di PROPOSTA_METODI_OPUS.md. Nessuna rete neurale.

Preregistrazione: preregistrazioni/ia31.md. Moduli: automa_hmm.py (automi, EM, BIC, costi per posizione), automa_testi.py (testi, generatori sintetici, costi).

Che cosa fa il codice (in parole semplici)
- Fase A: per ogni testo e per ognuna delle 5 pieghe (per foglio, come ia07) si stimano automi di taglia crescente (1, 2, 3, ... 128 stati; famiglia "libero" e "caselle") sul lessico
  delle altre quattro pieghe, due volte: pesato per frequenza (P) e sulle sole parole distinte (D). Per ogni taglia si misura la lunghezza di descrizione (BIC) sul lessico di
  addestramento e il costo (bit per glifo, fine parola compresa) sui fogli tenuti fuori: per tutte le parole e per le parole nuove, scomposto per posto (primo, secondo, terzo, dal
  quarto, fine), come la fase 0 di ia24. Per `vero` (e per `sint_vero`) si misura anche il costo delle parole nuove dei libri degli imitatori e del v21 sotto l'automa del vero.
- Fase S: sintesi e letture preregistrate (L1-L4) e controlli (positivo: automa noto; negativo: glifi rimescolati dentro le parole; positivo dello scarto).
Uscite (solo numeri e aggregati): risultati/ia31_automa_minimo.json e .md e, una riga per lavoro, risultati/ia31_corse.jsonl.

    nohup bash strumenti/coda.sh ia31 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia31" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO31=1 USCITA=<cartella fuori dal repo> python esperimenti/ia31_automa_minimo.py   (prova sul latino)

Variabili: PROCESSI (non cambia i risultati), RIPRENDI, FASI (lettere A S; predefinito AS), FILTRO. Nuove: GIRI31 (60), RIAVVII31 (4), ISTANZE31 (1), N_LIBRI31 (10),
PROPRI31 (cifre dei libri con automa proprio, predefinito 16), PICCOLO31 (solo prove). Nessun valore contiene virgole o due punti.
"""
import json, math, os, random, statistics, sys, time, zlib
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import Counter, OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import automa_hmm as H  # noqa: E402
import automa_testi as AT  # noqa: E402

NOME = 'ia31_automa_minimo'
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
PICCOLO = os.environ.get('PICCOLO31') == '1'
GIRI = int(os.environ.get('GIRI31', 6 if PICCOLO else 60))              # giri di EM per K <= 16 (meno per K piu' grandi: vedi piano_em)
RIAVVII = int(os.environ.get('RIAVVII31', 1 if PICCOLO else 4))          # partenze casuali per K <= 8 (meno per K piu' grandi)
ISTANZE = int(os.environ.get('ISTANZE31', 1))
N_LIBRI = int(os.environ.get('N_LIBRI31', 2 if PICCOLO else 10))
PROPRI = [int(x) for x in os.environ.get('PROPRI31', '1' if PICCOLO else '16') if x.isdigit()]
PIEGHE = 5

PESI = ('P', 'D')                                              # P: pesato per frequenza; D: parole distinte
GRIGLIA = OrderedDict([('libero', (1, 2, 4, 8) if PICCOLO else (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128)),
                       ('caselle', (1, 2, 4, 8) if PICCOLO else (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64))])
K_FISSI = (2, 4) if PICCOLO else (4, 16, 64)                   # tagli fissi per i confronti incrociati, oltre a K scelto con il BIC
GRANDE = max(GRIGLIA['libero'])
SALITE_STOP = 2                                                # uscita anticipata (solo testi non principali): dopo K >= 8, due tagli di fila senza migliorare la lunghezza di descrizione

# soglie preregistrate (preregistrazioni/ia31.md); fissate dopo le prove su testi non Voynich dove la preregistrazione lo dichiara
TOL_HO = 0.005                                                 # K_ho: il piu' piccolo K con costo fuori entro lo 0,5% del minimo
FRAZ_K90 = 0.90                                                # K90: il piu' piccolo K che raggiunge il 90% del guadagno massimo sui fogli tenuti fuori
TOL_TRIGRAMMI = 0.05                                           # l'automa spiega le parole nuove "come il trigramma" se costa al piu' cosi' di piu' (bit per glifo)
ERRORI_SI, ERRORI_NO = 3.0, 2.0                                # "presente/spiega" oltre 3 errori; "assente/non spiega" entro 2 errori
RAPPORTO_SPIEGA, RAPPORTO_NON = 0.80, 0.40                     # L2: scarto sotto l'automa / scarto sotto il trigramma
FUORI_PERC = 0.95                                              # L4: soglia di "fuori grammatica" = 95-esimo percentile del costo delle parole nuove vere
FUORI_MIN = 0.03                                               # e quota in eccesso almeno cosi' (oltre 3 errori)
DIFF_MIN_LOG2 = 1.0                                            # L3: oltre l'errore, la differenza deve valere almeno un fattore 2 nel numero di stati (due testi latini diversi, nella prova, differiscono di un fattore 2)
ERR_GRIGLIA = 0.29                                            # errore di discretizzazione della griglia dei K (meta' di log2 1,5), sempre sommato in quadratura negli errori di L3
FATTORE_K0 = 1.5                                               # controllo positivo: K stimato entro una volta e mezza di K0
CTRL_POS_MIN = 7                                               # almeno 7 su 8 testi sintetici
CTRL_NEUTRO_TOL = 0.01                                        # controllo dello scarto, testo senza rumore: lo scarto 2+3 stimato dista dall'esatto al piu' cosi' (bit per glifo)
CTRL_SCARTO_TOL = 0.25                                         # controllo positivo dello scarto: entro il 25% dello scarto esatto
CTRL_NEG_GUADAGNO = 0.5                                        # controllo negativo: il guadagno sulle parole nuove dei testi rimescolati e' meno della meta' di quello del vero

IMIT = ('M1', 'E2', 'W1')
SIGLE_LIBRI = ('V21',) + IMIT


# ---------------------------------------------------------------- catalogo dei lavori

def testi_propri():
    """Nomi dei testi con automa proprio (cinque lavori ciascuno, uno per piega), in ordine di costo decrescente."""
    nomi = ['vero', 'sint_vero']
    if not PICCOLO:
        nomi += ['neg_N1', 'neg_N2'] + ['sint_L%d_%d' % (k, s) for k in (4, 8, 16) for s in (1, 2)] + ['sint_C6_1', 'sint_C6_2']
        nomi += ['lingua_' + k for k in AT.LINGUE_CHIAVI] + ['nat_naibbe', 'nat_ts']
        from cifrari_procedimenti import PROCEDIMENTI, nome_istanza
        for cod, p in PROCEDIMENTI.items():
            for v in p['valori']:
                for i in range(1, ISTANZE + 1):
                    nomi.append('cif_' + nome_istanza(cod, v, i))
        nomi += ['lib_V21_%d' % AT.CHIAVI_V21[i - 1] for i in PROPRI]
        nomi += ['lib_%s_%d' % (s, i) for s in IMIT for i in PROPRI]
    else:
        nomi += ['neg_N1', 'sint_L4_1', 'sint_C6_1', 'lingua_latino', 'lib_V21_%d' % AT.CHIAVI_V21[0], 'lib_M1_1']
        if os.environ.get('CON_NATIVI31') == '1':
            nomi += ['nat_ts']                                   # Naibbe non si prova: la sua impaginazione legge le larghezze delle righe del Voynich
    return nomi


def nomi_libri(classe):
    """I libri di una sigla (V21, M1, E2, W1) usati negli incroci."""
    if classe == 'V21':
        return ['lib_V21_%d' % k for k in AT.CHIAVI_V21[:N_LIBRI]]
    return ['lib_%s_%d' % (classe, i) for i in range(1, N_LIBRI + 1)]


def libri_incrocio():
    """I libri dei quali si misura il costo delle parole nuove sotto l'automa del vero: v21 (10) e imitatori (N_LIBRI per sigla)."""
    nomi = ['lib_V21_%d' % k for k in AT.CHIAVI_V21[:N_LIBRI]]
    nomi += ['lib_%s_%d' % (s, i) for s in IMIT for i in range(1, N_LIBRI + 1)]
    return nomi


def configura(nome):
    """famiglie, griglie, uscita anticipata, libri da incrociare."""
    principale = nome in ('vero', 'sint_vero') or nome.startswith(('neg_', 'sint_'))
    fam_due = principale                                          # lingue, cifrari, generatori esterni e libri: solo la famiglia libera (la famiglia a caselle si confronta sul vero e sui controlli)
    cfg = dict(famiglie=('libero', 'caselle') if fam_due else ('libero',), early=(nome != 'vero'), pazienza=(3 if principale else SALITE_STOP), pesi=PESI)
    cfg['griglie'] = {f: tuple(k for k in GRIGLIA[f] if (principale or k <= 64)) for f in cfg['famiglie']}
    if nome == 'sint_vero':                                   # controllo dello scarto: solo il peso P e la famiglia libera, fino a 32 stati, uscita anticipata
        cfg.update(early=True, pazienza=SALITE_STOP, pesi=('P',), famiglie=('libero',))
        cfg['griglie'] = {'libero': tuple(k for k in GRIGLIA['libero'] if k <= 32)}
    if nome.startswith('neg_'):                                # controllo negativo: i due pesi, famiglia libera, fino a 32 stati, uscita anticipata
        cfg.update(early=True, pazienza=SALITE_STOP, famiglie=('libero',))
        cfg['griglie'] = {'libero': tuple(k for k in GRIGLIA['libero'] if k <= 32)}
    if nome.startswith(('sint_L', 'sint_C')):                  # controlli di taglia: solo il peso P, solo la famiglia che ha generato il testo, griglie corte, uscita anticipata
        fam = 'libero' if nome.startswith('sint_L') else 'caselle'
        cfg.update(early=True, pazienza=SALITE_STOP, pesi=('P',), famiglie=(fam,))
        cfg['griglie'] = {fam: tuple(k for k in GRIGLIA[fam] if k <= (64 if fam == 'libero' else 32))}
    cfg['incroci'] = libri_incrocio() if nome == 'vero' else (['sint_gap', 'sint_neutro'] if nome == 'sint_vero' else [])
    return cfg


def lavori_fase(fase):
    if fase == 'A':
        return [('T', nome, f) for nome in testi_propri() for f in range(PIEGHE)]
    return []


# ---------------------------------------------------------------- un lavoro: un testo, una piega

def quantile_pesato(costi, q):
    """Quantile q di una lista (valore, peso)."""
    v = sorted(costi)
    tot = sum(w for _, w in v)
    acc = 0.0
    for x, w in v:
        acc += w
        if acc >= q * tot:
            return x
    return v[-1][0]


def quota_sopra(costi, soglia):
    tot = sum(w for _, w in costi)
    return sum(w for x, w in costi if x > soglia) / tot if tot else 0.0


def parti_lista(parti, gl, n):
    return [round(float(x), 4) for x in parti] + [round(float(gl), 1), round(float(n), 1)]


def insiemi_parole(conti, al):
    parole = list(conti)
    return H.gruppi_da_parole(parole, [float(conti[w]) for w in parole], al)


def piano_em(K):
    """(partenze casuali, giri di EM) per taglia: tante dove costa poco (la verosimiglianza ha molti massimi locali e un EM corto fa scegliere K troppo grandi: provato sui sintetici),
    una sola e meno giri dove costa molto."""
    if K <= 8:
        return RIAVVII, GIRI
    if K <= 16:
        return max(1, RIAVVII - 1), GIRI
    if K <= 32:
        return max(1, RIAVVII // 2), max(6, (2 * GIRI) // 3)
    return 1, max(6, GIRI // 2)


def lavoro_testo(nome, f):
    inizio = time.time()
    cfg = configura(nome)
    T = AT.testo(nome)
    pag, fold = T['pagine'], T['fold']
    tr, te = AT.conti_piega(pag, fold, f)
    al = AT.alfabeto_di(pag)
    noti = set(tr)
    nuove = Counter({w: k for w, k in te.items() if w not in noti})
    parole_tr = sorted(tr, key=lambda w: (-tr[w], w))
    gr_te, gr_nu = insiemi_parole(te, al), insiemi_parole(nuove, al)
    forma = AT.forma_trigrammi(tr)
    ris = OrderedDict([('lavoro', 'T|%s|%d' % (nome, f)), ('nome', nome), ('piega', f), ('tipi_addestramento', len(tr)), ('token_addestramento', sum(tr.values())),
                       ('glifi', al.V), ('token_fuori', sum(te.values())), ('nuove_token', sum(nuove.values())), ('nuove_tipi', len(nuove))])
    ris['tri'] = OrderedDict([('tutti', parti_lista(*AT.parti_trigrammi(forma, te))), ('nuove', parti_lista(*AT.parti_trigrammi(forma, nuove)))])
    curve, scelte, modelli = OrderedDict(), OrderedDict(), {}
    for peso in cfg['pesi']:
        pesi = [float(tr[w]) for w in parole_tr] if peso == 'P' else [1.0] * len(parole_tr)
        gr = H.gruppi_da_parole(parole_tr, pesi, al)
        un, pm = H.statistiche(gr, al)
        n_eff = float(sum(pesi))
        for fam in cfg['famiglie']:
            voci, migliore, salite = [], None, 0
            for K in cfg['griglie'][fam]:
                seme = AT.seme_di('fit', nome, f, peso, fam, K)
                riav, giri = piano_em(K)
                a, info = H.fit(gr, al, K, fam, seme, giri=giri, riavvii=riav, unigramma=un, pos_media=pm)
                ll = a.ll_bit(gr)
                dl = H.bic_bit(ll, K, al.V, fam, n_eff)
                voce = OrderedDict([('K', K), ('p', a.parametri()), ('ll_bit', round(ll, 2)), ('n_eff', n_eff), ('DL', round(dl, 2)), ('giri', info['giri']),
                                    ('tutti', parti_lista(*AT.parti_gruppi(a, gr_te))), ('nuove', parti_lista(*AT.parti_gruppi(a, gr_nu)))])
                voci.append(voce)
                if os.environ.get('VERBOSO31') == '1':
                    print('  %s f%d %s %s K=%d: %.1f s dall inizio, DL/token %.3f' % (nome, f, peso, fam, K, time.time() - inizio, dl / n_eff), flush=True)
                if cfg['incroci']:
                    modelli[(peso, fam, K)] = a
                if migliore is None or dl < migliore:
                    migliore, salite = dl, 0
                elif K >= 8:
                    salite += 1
                if cfg['early'] and salite >= cfg['pazienza']:
                    break
            curve['%s|%s' % (peso, fam)] = voci
            scelte['%s|%s' % (peso, fam)] = min(voci, key=lambda v: v['DL'])['K']
    ris['curve'], ris['K_bic'] = curve, scelte
    if os.environ.get('VERBOSO31') == '1':
        print('  adattamenti finiti dopo %.1f s' % (time.time() - inizio), flush=True)
    if cfg['incroci']:
        ris['incroci'] = incroci(nome, f, cfg, al, nuove, noti, modelli, scelte, forma)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def incroci(nome, f, cfg, al, nuove_vero, noti, modelli, scelte, forma):
    """Costo delle parole nuove di altri testi (libri degli imitatori, v21) sotto gli automi del vero della piega `f`, alla taglia scelta con il BIC (e a tagli fissi).
    Per `sint_vero` anche il costo sotto l'automa che ha generato il testo (esatto)."""
    out = OrderedDict()
    esatto = AT.automa_sintetico(nome) if nome.startswith('sint_') else None
    # soglia di "fuori grammatica": 95-esimo percentile del costo per glifo delle parole nuove vere, sotto lo stesso automa
    soglie = {}
    for (peso, fam, K), a in modelli.items():
        if fam == 'libero' and (K == scelte['%s|%s' % (peso, fam)] or K in K_FISSI):
            soglie[(peso, fam, K)] = quantile_pesato(AT.costi_per_parola(a, nuove_vero, al), FUORI_PERC)
    for b in cfg['incroci']:
        B = AT.testo(b)
        _, teb = AT.conti_piega(B['pagine'], B['fold'], f)
        nu = Counter({w: k for w, k in teb.items() if w not in noti})
        if not nu:
            continue
        g = insiemi_parole(nu, al)
        voce = OrderedDict([('tri', parti_lista(*AT.parti_trigrammi(forma, nu))), ('n_token', sum(nu.values()))])
        mod = OrderedDict()
        for (peso, fam, K), a in modelli.items():
            chiave = '%s|%s|%d' % (peso, fam, K)
            scelto = (K == scelte['%s|%s' % (peso, fam)])
            if not (scelto or (fam == 'libero' and K in K_FISSI)):
                continue
            m = OrderedDict([('parti', parti_lista(*AT.parti_gruppi(a, g))), ('scelto', scelto)])
            if (peso, fam, K) in soglie:
                m['fuori'] = round(quota_sopra(AT.costi_per_parola(a, nu, al), soglie[(peso, fam, K)]), 4)
            mod[chiave] = m
        voce['mod'] = mod
        if esatto is not None:
            voce['esatto'] = parti_lista(*AT.parti_gruppi(esatto, insiemi_parole(nu, esatto.al)))
        out[b] = voce
    if esatto is not None:
        out['_esatto_vero'] = parti_lista(*AT.parti_gruppi(esatto, insiemi_parole(nuove_vero, esatto.al)))
    return out


def lavoro(args):
    inizio = time.time()
    ident = '|'.join(str(a) for a in args)
    try:
        if args[0] == 'T':
            return lavoro_testo(args[1], int(args[2]))
        raise ValueError(args[0])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', ident), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    pass


def esegui(lavori, processi, percorso, fatte):
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if '|'.join(str(x) for x in a) not in fatte and (not filtro or any(x in '|'.join(str(y) for y in a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as fh:
                fh.write(json.dumps(r, ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                print('[%d/%d %.1f min] %s: K_bic %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], dict(r.get('K_bic', {})), r.get('secondi', 0)), flush=True)
        pool.close()
        pool.join()
    return out


def leggi_corse(percorso):
    out = []
    if os.path.exists(percorso):
        for riga in open(percorso, encoding='utf-8'):
            riga = riga.strip()
            if riga:
                out.append(json.loads(riga))
    return out


# ---------------------------------------------------------------- analisi

def per_testo(corse):
    """nome -> {piega: lavoro} (l'ultimo lavoro riuscito per piega)."""
    out = OrderedDict()
    for r in corse:
        if r.get('errore') or r.get('nome') is None:
            continue
        out.setdefault(r['nome'], {})[r['piega']] = r
    return out


def jack_se(valori):
    n = len(valori)
    if n < 2:
        return None
    m = sum(valori) / n
    return math.sqrt((n - 1) / n * sum((v - m) ** 2 for v in valori))


def curva_testo(jobs, chiave):
    """Curve aggregate sulle pieghe per (peso|famiglia): K_bic (aggregato e per piega), K_ho, K90, costi per K. None se il testo non ha tutte le pieghe."""
    if len(jobs) < PIEGHE or any(chiave not in j['curve'] for j in jobs.values()):
        return None
    comuni = sorted(set.intersection(*[{v['K'] for v in j['curve'][chiave]} for j in jobs.values()]))
    per = {f: {v['K']: v for v in j['curve'][chiave]} for f, j in jobs.items()}
    dl = {K: sum(per[f][K]['DL'] for f in per) for K in comuni}
    K_bic = min(comuni, key=lambda K: dl[K])
    K_bic_f = [min(j['curve'][chiave], key=lambda v: v['DL'])['K'] for _, j in sorted(jobs.items())]
    cost = {}
    nuove = {}
    for K in comuni:
        bit = sum(sum(per[f][K]['tutti'][:5]) for f in per)
        gl = sum(per[f][K]['tutti'][5] for f in per)
        pn = np.sum([per[f][K]['nuove'][:5] for f in per], axis=0)
        gn = sum(per[f][K]['nuove'][5] for f in per)
        cost[K] = bit / gl
        nuove[K] = dict(parti=[float(x / gn) for x in pn], costo=float(pn.sum() / gn), glifi=gn)
    mn = min(cost.values())
    K_ho = min(K for K in comuni if cost[K] <= mn * (1 + TOL_HO))
    gain = {K: cost[comuni[0]] - cost[K] for K in comuni}
    gmax = max(gain.values())
    K90 = min(K for K in comuni if gain[K] >= FRAZ_K90 * gmax) if gmax > 0 else comuni[0]
    p_bic = per[0][K_bic]['p'] if K_bic in per[0] else None
    return OrderedDict([('K_bic', K_bic), ('K_bic_pieghe', K_bic_f), ('K_ho', K_ho), ('K90', K90), ('DL', {K: round(dl[K], 1) for K in comuni}),
                        ('costo_fuori', {K: round(cost[K], 4) for K in comuni}), ('nuove', {K: nuove[K] for K in comuni}), ('parametri_bic', p_bic),
                        ('guadagno_max', round(gmax, 4)), ('a_fondo_griglia', bool(K_bic == comuni[-1] and len(comuni) > 3)), ('K', comuni)])


def tri_testo(jobs):
    if len(jobs) < PIEGHE:
        return None
    bit = sum(sum(j['tri']['tutti'][:5]) for j in jobs.values())
    gl = sum(j['tri']['tutti'][5] for j in jobs.values())
    pn = np.sum([j['tri']['nuove'][:5] for j in jobs.values()], axis=0)
    gn = sum(j['tri']['nuove'][5] for j in jobs.values())
    return OrderedDict([('tutti', bit / gl), ('nuove', float(pn.sum() / gn)), ('nuove_parti', [float(x / gn) for x in pn]), ('glifi_nuove', gn)])


def se_log2(vals):
    x = [math.log2(v) for v in vals]
    return statistics.stdev(x) / math.sqrt(len(x)) if len(x) > 1 else None


def lettura_confronto(m_voy, se_voy, gruppo):
    """gruppo: lista di (K_bic) per testo. Differenza in log2 (gruppo - Voynich), errore combinato, lettura a 2 errori."""
    xs = [math.log2(k) for k in gruppo]
    mg = sum(xs) / len(xs)
    sg = statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else None
    es = [e for e in (se_voy, sg) if e is not None] + [ERR_GRIGLIA]
    e = math.sqrt(sum(x * x for x in es))
    d = mg - math.log2(m_voy)
    soglia = max(ERRORI_NO * e, DIFF_MIN_LOG2)
    if d > soglia:
        lett = 'il Voynich e\' piu\' piccolo'
    elif d < -soglia:
        lett = 'il Voynich e\' piu\' grande'
    else:
        lett = 'simile (entro l\'errore)'
    return OrderedDict([('n', len(gruppo)), ('K_medio_log2', round(mg, 3)), ('differenza_log2', round(d, 3)), ('errore', round(e, 3)), ('lettura', lett)])


def parti23(parti, gl):
    return (parti[1] + parti[2]) / gl


def scarto_classe(jobs_vero, libri_di, chiave):
    """Scarto (libri meno vero) del costo per glifo delle parole nuove, nelle parti secondo+terzo glifo e totale, sotto l'automa del vero alla taglia BIC di ogni piega
    (`chiave` 'P|libero|scelto') o sotto il trigramma ('tri'). Errore: jackknife sulle pieghe e variabilita' fra libri. Restituisce un dict o None."""
    pieghe = sorted(jobs_vero)
    def parti_vero(f):
        j = jobs_vero[f]
        if chiave == 'tri':
            return j['tri']['nuove']
        peso, fam = chiave.split('|')[:2]
        K = j['K_bic']['%s|%s' % (peso, fam)]
        return [v for v in j['curve']['%s|%s' % (peso, fam)] if v['K'] == K][0]['nuove']
    def parti_libro(f, b):
        voce = jobs_vero[f].get('incroci', {}).get(b)
        if voce is None:
            return None
        if chiave == 'tri':
            return voce['tri']
        peso, fam = chiave.split('|')[:2]
        for k, m in voce['mod'].items():
            if k.startswith('%s|%s|' % (peso, fam)) and m['scelto']:
                return m['parti']
        return None
    liste = {b: [parti_libro(f, b) for f in pieghe] for b in libri_di}
    liste = {b: v for b, v in liste.items() if all(x is not None for x in v)}
    if not liste:
        return None
    pv = [parti_vero(f) for f in pieghe]
    def calcola(fs):
        v = np.sum([pv[f][:5] for f in fs], axis=0)
        gv = sum(pv[f][5] for f in fs)
        c_v = (v[1] + v[2]) / gv, v.sum() / gv
        per_libro = []
        for b, L in liste.items():
            s = np.sum([L[f][:5] for f in fs], axis=0)
            g = sum(L[f][5] for f in fs)
            per_libro.append(((s[1] + s[2]) / g - c_v[0], s.sum() / g - c_v[1], (s[1] + s[2]) / g, s.sum() / g))
        return c_v, per_libro
    c_v, per_libro = calcola(list(range(len(pieghe))))
    d23 = [x[0] for x in per_libro]
    dtot = [x[1] for x in per_libro]
    jk = []
    for omit in range(len(pieghe)):
        cv, pl = calcola([i for i in range(len(pieghe)) if i != omit])
        jk.append(sum(x[0] for x in pl) / len(pl))
    se_jack = jack_se(jk)
    se_libri = statistics.stdev(d23) / math.sqrt(len(d23)) if len(d23) > 1 else 0.0
    e = math.sqrt((se_jack or 0.0) ** 2 + se_libri ** 2)
    return OrderedDict([('n_libri', len(per_libro)), ('vero_23', round(c_v[0], 4)), ('vero_tot', round(c_v[1], 4)), ('scarto_23', round(sum(d23) / len(d23), 4)),
                        ('scarto_tot', round(sum(dtot) / len(dtot), 4)), ('errore', round(e, 4)), ('libri_23', round(sum(x[2] for x in per_libro) / len(per_libro), 4))])


def lettura_scarto(auto, tri):
    """L2: l'automa spiega lo scarto del secondo e terzo glifo?"""
    if auto is None or tri is None:
        return 'dati mancanti'
    if tri['scarto_23'] <= ERRORI_SI * tri['errore']:
        return 'niente da spiegare (il trigramma non vede scarto nei posti 2+3; per l\'automa vale %s)' % mf(auto['scarto_23'], 4)
    rapporto = auto['scarto_23'] / tri['scarto_23']
    e = auto['errore']
    if rapporto >= RAPPORTO_SPIEGA and auto['scarto_23'] > ERRORI_SI * e:
        return 'spiega (rapporto %.2f)' % rapporto
    if rapporto < RAPPORTO_NON or auto['scarto_23'] <= ERRORI_NO * e:
        return 'non spiega (rapporto %.2f)' % rapporto
    return 'in parte (rapporto %.2f)' % rapporto


def quota_fuori(jobs_vero, libri_di, peso):
    """Quota di parole nuove dei libri sopra il 95-esimo percentile del costo delle parole nuove vere (automa del vero a taglia BIC)."""
    pieghe = sorted(jobs_vero)
    valori = []
    for b in libri_di:
        num = den = 0.0
        ok = True
        for f in pieghe:
            voce = jobs_vero[f].get('incroci', {}).get(b)
            if voce is None:
                ok = False
                break
            for k, m in voce['mod'].items():
                if k.startswith('%s|libero|' % peso) and m['scelto'] and 'fuori' in m:
                    num += m['fuori'] * voce['n_token']
                    den += voce['n_token']
        if ok and den:
            valori.append(num / den)
    if not valori:
        return None
    mu = sum(valori) / len(valori)
    se = statistics.stdev(valori) / math.sqrt(len(valori)) if len(valori) > 1 else None
    eccesso = mu - (1 - FUORI_PERC)
    if se is None:
        lett = 'non leggibile (un solo libro)'
    elif eccesso > ERRORI_SI * se and eccesso > FUORI_MIN:
        lett = 'fuori grammatica'
    elif eccesso <= ERRORI_NO * se or eccesso <= 0:
        lett = 'dentro la grammatica'
    else:
        lett = 'zona grigia'
    return OrderedDict([('n_libri', len(valori)), ('quota', round(mu, 4)), ('errore', None if se is None else round(se, 4)), ('attesa', round(1 - FUORI_PERC, 3)), ('lettura', lett)])


def analisi(corse, versioni):
    T = per_testo(corse)
    out = OrderedDict([('esperimento', 'ia31'), ('versioni', versioni), ('solo_controlli', SOLO_CONTROLLI), ('piccolo', PICCOLO)])
    chiavi = [('%s|%s' % (p, f)) for p in PESI for f in ('libero', 'caselle')]
    # --- curve e taglie per testo
    testi = OrderedDict()
    for nome, jobs in T.items():
        r = OrderedDict([('pieghe', len(jobs)), ('tri', tri_testo(jobs))])
        for ch in chiavi:
            c = curva_testo(jobs, ch)
            if c is not None:
                r[ch] = c
        j0 = next(iter(jobs.values()))
        r['glifi'] = j0['glifi']
        r['token'] = sum(j['token_addestramento'] + j['token_fuori'] for j in jobs.values())
        testi[nome] = r
    out['testi'] = testi
    vero = testi.get('vero')
    # --- controlli
    ctrl = OrderedDict()
    pos = []
    for nome, r in testi.items():
        if not nome.startswith('sint_') or nome.split('_')[1] in ('vero', 'gap', 'neutro'):
            continue
        tipo, K0 = nome.split('_')[1][0], int(nome.split('_')[1][1:])
        ch = 'P|libero' if tipo == 'L' else 'P|caselle'
        if ch not in r:
            continue
        K = r[ch]['K_bic']
        pos.append(OrderedDict([('testo', nome), ('K0', K0), ('famiglia', 'libero' if tipo == 'L' else 'caselle'), ('K_stimato', K), ('K_bic_pieghe', r[ch]['K_bic_pieghe']),
                                ('dentro', bool(K0 / FATTORE_K0 <= K <= K0 * FATTORE_K0))]))
    if pos:
        n_ok = sum(1 for x in pos if x['dentro'])
        ctrl['positivo_taglia'] = OrderedDict([('casi', pos), ('riusciti', n_ok), ('su', len(pos)), ('soglia', CTRL_POS_MIN if len(pos) >= 8 else math.ceil(0.85 * len(pos))),
                                               ('riuscito', n_ok >= (CTRL_POS_MIN if len(pos) >= 8 else math.ceil(0.85 * len(pos))))])
    neg = []
    for nome in ('neg_N1', 'neg_N2'):
        r = testi.get(nome)
        if r is None or vero is None:
            continue
        voce = OrderedDict([('testo', nome)])
        for peso in PESI:
            ch = '%s|libero' % peso
            if ch in r and ch in vero:
                gn = lambda c: 1 - c['nuove'][c['K_bic']]['costo'] / c['nuove'][c['K'][0]]['costo']
                voce['guadagno_nuove_%s' % peso] = round(gn(r[ch]), 4)
                voce['guadagno_nuove_vero_%s' % peso] = round(gn(vero[ch]), 4)
                voce['K_bic_%s' % peso] = r[ch]['K_bic']
                voce['K_bic_vero_%s' % peso] = vero[ch]['K_bic']
                voce['crolla_%s' % peso] = bool(gn(r[ch]) < CTRL_NEG_GUADAGNO * gn(vero[ch]))
        neg.append(voce)
    if neg:
        ctrl['negativo'] = OrderedDict([('casi', neg), ('riuscito', all(v.get('crolla_P', False) and v.get('crolla_D', False) for v in neg))])
    # --- controllo positivo dello scarto (sint_vero contro sint_gap e sint_neutro)
    sv = T.get('sint_vero')
    if sv and len(sv) == PIEGHE:
        sc = OrderedDict()
        for b in ('sint_gap', 'sint_neutro'):
            auto = scarto_classe(sv, [b], 'P|libero|scelto')
            tri = scarto_classe(sv, [b], 'tri')
            esatto = None
            try:
                pv = np.sum([j['incroci']['_esatto_vero'][:5] for j in sv.values()], axis=0)
                gv = sum(j['incroci']['_esatto_vero'][5] for j in sv.values())
                pb = np.sum([j['incroci'][b]['esatto'][:5] for j in sv.values()], axis=0)
                gb = sum(j['incroci'][b]['esatto'][5] for j in sv.values())
                esatto = OrderedDict([('scarto_23', round(float((pb[1] + pb[2]) / gb - (pv[1] + pv[2]) / gv), 4)), ('scarto_tot', round(float(pb.sum() / gb - pv.sum() / gv), 4))])
            except Exception:                                                  # noqa: BLE001
                esatto = None
            sc[b] = OrderedDict([('stimato', auto), ('trigramma', tri), ('esatto', esatto)])
        ok_gap = ok_neu = None
        g = sc['sint_gap']
        if g['stimato'] and g['esatto'] and g['esatto']['scarto_23'] > 0:
            ok_gap = abs(g['stimato']['scarto_23'] - g['esatto']['scarto_23']) <= CTRL_SCARTO_TOL * g['esatto']['scarto_23']
        n_ = sc['sint_neutro']
        if n_['stimato'] and n_['esatto']:
            ok_neu = abs(n_['stimato']['scarto_23'] - n_['esatto']['scarto_23']) <= CTRL_NEUTRO_TOL
        ctrl['positivo_scarto'] = OrderedDict([('casi', sc), ('gap_riuscito', ok_gap), ('neutro_riuscito', ok_neu), ('riuscito', bool(ok_gap) and bool(ok_neu))])
    out['controlli'] = ctrl
    validi = OrderedDict((k, v.get('riuscito')) for k, v in ctrl.items())
    out['controlli_ok'] = all(validi.values()) if validi else False
    # --- L1: taglia minima
    L1 = OrderedDict()
    if vero:
        for ch in chiavi:
            if ch in vero:
                c = vero[ch]
                tri = vero['tri']
                cn = c['nuove'][c['K_bic']]['costo']
                L1[ch] = OrderedDict([('K_bic', c['K_bic']), ('a_fondo_griglia', c['a_fondo_griglia']), ('pianoro', bool(c['K90'] <= c['K_bic'])), ('K_bic_pieghe', c['K_bic_pieghe']), ('K_ho', c['K_ho']), ('K90', c['K90']), ('parametri', c['parametri_bic']),
                                      ('costo_nuove_automa', round(cn, 4)), ('costo_nuove_trigramma', round(tri['nuove'], 4)),
                                      ('automa_come_trigramma', bool(cn <= tri['nuove'] + TOL_TRIGRAMMI)),
                                      ('costo_nuove_K_grande', round(c['nuove'][max(c['K'])]['costo'], 4))])
    out['L1_taglia'] = L1
    L1c = OrderedDict()
    for peso in PESI:                                                       # le caselle bastano? (K al piu' una volta e mezza e costo sulle parole nuove entro 0,05 bit per glifo)
        cl, cc = L1.get('%s|libero' % peso), L1.get('%s|caselle' % peso)
        if cl and cc:
            L1c[peso] = OrderedDict([('K_libero', cl['K_bic']), ('K_caselle', cc['K_bic']), ('costo_nuove_libero', cl['costo_nuove_automa']), ('costo_nuove_caselle', cc['costo_nuove_automa']),
                                     ('bastano', bool(cc['K_bic'] <= FATTORE_K0 * cl['K_bic'] and cc['costo_nuove_automa'] <= cl['costo_nuove_automa'] + TOL_TRIGRAMMI))])
    out['L1_caselle'] = L1c
    # --- L2: scarto del secondo e terzo glifo
    L2 = OrderedDict()
    if vero and len(T['vero']) == PIEGHE:
        for peso in PESI:
            for classe in SIGLE_LIBRI:
                libri = nomi_libri(classe)
                auto = scarto_classe(T['vero'], libri, '%s|libero|scelto' % peso)
                tri = scarto_classe(T['vero'], libri, 'tri')
                L2['%s|%s' % (peso, classe)] = OrderedDict([('automa', auto), ('trigramma', tri), ('lettura', lettura_scarto(auto, tri))])
    for peso in PESI:                                                       # sintesi: la media di M1, E2 e W1
        cl = [L2.get('%s|%s' % (peso, c)) for c in IMIT]
        if cl and all(x and x['automa'] and x['trigramma'] for x in cl):
            med = lambda k, s: sum(x[k][s] for x in cl) / len(cl)
            err = lambda k: math.sqrt(sum(x[k]['errore'] ** 2 for x in cl)) / len(cl)
            auto = OrderedDict([('scarto_23', round(med('automa', 'scarto_23'), 4)), ('scarto_tot', round(med('automa', 'scarto_tot'), 4)), ('errore', round(err('automa'), 4))])
            tri = OrderedDict([('scarto_23', round(med('trigramma', 'scarto_23'), 4)), ('scarto_tot', round(med('trigramma', 'scarto_tot'), 4)), ('errore', round(err('trigramma'), 4))])
            L2['%s|sintesi M1 E2 W1' % peso] = OrderedDict([('automa', auto), ('trigramma', tri), ('lettura', lettura_scarto(auto, tri))])
    out['L2_scarto'] = L2
    # --- L3: il Voynich e' piu' piccolo?
    L3 = OrderedDict()
    if vero:
        gruppi = OrderedDict([('lingue', [n for n in testi if n.startswith('lingua_')]), ('cifrari', [n for n in testi if n.startswith('cif_')]),
                              ('Naibbe e Timm-Schinner', [n for n in testi if n.startswith('nat_')]), ('v21', [n for n in testi if n.startswith('lib_V21')]),
                              ('M1', [n for n in testi if n.startswith('lib_M1')]), ('E2', [n for n in testi if n.startswith('lib_E2')]), ('W1', [n for n in testi if n.startswith('lib_W1')])])
        for cod in ('V', 'S', 'N', 'C', 'R', 'F', 'P'):                        # i cifrari anche per procedimento
            nomi_cod = [n for n in testi if n.startswith('cif_%s_' % cod)]
            if nomi_cod:
                gruppi['cifrario %s' % cod] = nomi_cod
        for fam in ('libero', 'caselle'):
            for peso in PESI:
                ch = '%s|%s' % (peso, fam)
                if ch not in vero:
                    continue
                se_voy = se_log2(vero[ch]['K_bic_pieghe'])
                for g, nomi in gruppi.items():
                    ks = [testi[n][ch]['K_bic'] for n in nomi if ch in testi[n]]
                    if ks:
                        L3['%s|%s' % (ch, g)] = lettura_confronto(vero[ch]['K_bic'], se_voy, ks)
        # lettura riassuntiva: piu' piccolo se P e D concordano
        riass = OrderedDict()
        for fam in ('libero', 'caselle'):
            for g in gruppi:
                lp, ld = L3.get('P|%s|%s' % (fam, g)), L3.get('D|%s|%s' % (fam, g))
                if lp and ld:
                    riass['%s|%s' % (fam, g)] = lp['lettura'] if lp['lettura'] == ld['lettura'] else 'dipende dal peso (P: %s; D: %s)' % (lp['lettura'], ld['lettura'])
        L3['riassunto'] = riass
    out['L3_confronti'] = L3
    # --- L4: gli imitatori inventano parole fuori grammatica?
    L4 = OrderedDict()
    if vero and len(T['vero']) == PIEGHE:
        for peso in PESI:
            for classe in SIGLE_LIBRI:
                libri = nomi_libri(classe)
                L4['%s|%s' % (peso, classe)] = quota_fuori(T['vero'], libri, peso)
    out['L4_fuori_grammatica'] = L4
    return out


def mf(x, d=3):
    return 'n/d' if x is None else ('%.*f' % (d, x)).replace('.', ',')


def scrivi_md(o):
    L = ['# IA31 (ia31) — l\'automa minimo della forma delle parole', '', 'Preregistrazione: `preregistrazioni/ia31.md`.', '',
         '- Versioni: %s.' % ', '.join('%s %s' % (k, v) for k, v in o['versioni'].items()),
         '- Controlli: %s.' % ('tutti riusciti' if o.get('controlli_ok') else 'NON tutti riusciti: le letture L1-L4 si riportano ma non si leggono'), '']
    L += ['## Controlli', '']
    c = o['controlli']
    if 'positivo_taglia' in c:
        p = c['positivo_taglia']
        L += ['**Positivo (automa noto):** %d su %d entro una volta e mezza (soglia %d) -> %s.' % (p['riusciti'], p['su'], p['soglia'], 'riuscito' if p['riuscito'] else 'FALLITO'), '',
              '| testo | K0 | famiglia | K stimato | per piega | dentro |', '|---|---|---|---|---|---|']
        for x in p['casi']:
            L.append('| %s | %d | %s | %d | %s | %s |' % (x['testo'], x['K0'], x['famiglia'], x['K_stimato'], x['K_bic_pieghe'], 'si' if x['dentro'] else 'NO'))
        L.append('')
    if 'negativo' in c:
        L += ['**Negativo (glifi rimescolati dentro le parole):** %s.' % ('riuscito' if c['negativo']['riuscito'] else 'FALLITO'), '',
              '| testo | K P | K vero P | guadagno P | guadagno vero P | crolla P | K D | K vero D | guadagno D | guadagno vero D | crolla D |', '|---|---|---|---|---|---|---|---|---|---|---|']
        for x in c['negativo']['casi']:
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (x['testo'], x.get('K_bic_P'), x.get('K_bic_vero_P'), mf(x.get('guadagno_nuove_P')), mf(x.get('guadagno_nuove_vero_P')),
                                                                           x.get('crolla_P'), x.get('K_bic_D'), x.get('K_bic_vero_D'), mf(x.get('guadagno_nuove_D')), mf(x.get('guadagno_nuove_vero_D')), x.get('crolla_D')))
        L.append('')
    if 'positivo_scarto' in c:
        p = c['positivo_scarto']
        L += ['**Positivo dello scarto (rumore sul secondo e terzo glifo):** gap %s, neutro %s -> %s.' % (p['gap_riuscito'], p['neutro_riuscito'], 'riuscito' if p['riuscito'] else 'FALLITO'), '',
              '| testo | scarto 2+3 stimato (automa) | errore | scarto 2+3 esatto | scarto 2+3 trigramma |', '|---|---|---|---|---|']
        for b, x in p['casi'].items():
            L.append('| %s | %s | %s | %s | %s |' % (b, mf(x['stimato'] and x['stimato']['scarto_23'], 4), mf(x['stimato'] and x['stimato']['errore'], 4), mf(x['esatto'] and x['esatto']['scarto_23'], 4),
                                                 mf(x['trigramma'] and x['trigramma']['scarto_23'], 4)))
        L.append('')
    L += ['## L1: la taglia minima del vero', '', '| peso e famiglia | K (BIC) | per piega | K (fuori) | K90 | parametri | costo parole nuove automa | trigramma | come il trigramma | K grande |', '|---|---|---|---|---|---|---|---|---|---|']
    for ch, x in o['L1_taglia'].items():
        L.append('| %s | %s | %s | %d | %d | %s | %s | %s | %s | %s |' % (ch, ('%d%s' % (x['K_bic'], ' (fondo della griglia)' if x['a_fondo_griglia'] else '')), x['K_bic_pieghe'], x['K_ho'], x['K90'], x['parametri'], mf(x['costo_nuove_automa']),
                                                                    mf(x['costo_nuove_trigramma']), 'si' if x['automa_come_trigramma'] else 'no', mf(x['costo_nuove_K_grande'])))
    L.append('')
    for peso, x in o.get('L1_caselle', {}).items():
        L.append('- Peso %s: le caselle bastano? K libero %d, K caselle %d, costo parole nuove %s contro %s -> **%s**.' % (peso, x['K_libero'], x['K_caselle'], mf(x['costo_nuove_caselle']), mf(x['costo_nuove_libero']), 'si' if x['bastano'] else 'no'))
    for ch, x in o['L1_taglia'].items():
        L.append('- %s: pianoro della curva fuori (K90 <= K scelto) -> %s.' % (ch, 'si' if x['pianoro'] else 'no'))
    L += ['', '## L2: lo scarto del secondo e terzo glifo (parole nuove, bit per glifo; scarto = libri meno vero)', '',
          '| peso, libri | scarto 2+3 sotto l\'automa | errore | scarto 2+3 sotto il trigramma | scarto totale automa | scarto totale trigramma | lettura |', '|---|---|---|---|---|---|---|']
    for k, x in o['L2_scarto'].items():
        a, t = x['automa'], x['trigramma']
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (k, mf(a and a['scarto_23'], 4), mf(a and a['errore'], 4), mf(t and t['scarto_23'], 4), mf(a and a['scarto_tot'], 4), mf(t and t['scarto_tot'], 4), x['lettura']))
    L += ['', '## L3: il Voynich e\' piu\' piccolo? (differenza in log2 del numero di stati, gruppo meno Voynich)', '', '| peso, famiglia, gruppo | n | differenza | errore | lettura |', '|---|---|---|---|---|']
    for k, x in o['L3_confronti'].items():
        if k == 'riassunto':
            continue
        L.append('| %s | %d | %s | %s | %s |' % (k, x['n'], mf(x['differenza_log2']), mf(x['errore']), x['lettura']))
    L += ['', 'Riassunto (piu\' piccolo solo se P e D concordano):', '']
    for k, v in o['L3_confronti'].get('riassunto', {}).items():
        L.append('- %s: %s' % (k, v))
    L += ['', '## L4: parole nuove dei libri fuori dalla grammatica del vero', '', '| peso, libri | n | quota sopra il 95-esimo percentile | errore | lettura |', '|---|---|---|---|---|']
    for k, x in o['L4_fuori_grammatica'].items():
        if x:
            L.append('| %s | %d | %s | %s | %s |' % (k, x['n_libri'], mf(x['quota']), mf(x['errore']), x['lettura']))
    L += ['', "## Taglie di tutti i testi (K scelto con il BIC; per piega fra parentesi; * = K scelto all'ultimo taglio comune a tutte le pieghe: il minimo potrebbe stare oltre)", '', '| testo | P libero | D libero | P caselle | D caselle | trigramma: costo parole nuove |', '|---|---|---|---|---|---|']
    for nome, r in o['testi'].items():
        cel = lambda ch: ('%d%s %s' % (r[ch]['K_bic'], '*' if r[ch]['a_fondo_griglia'] else '', r[ch]['K_bic_pieghe'])) if ch in r else '—'
        L.append('| %s | %s | %s | %s | %s | %s |' % (nome, cel('P|libero'), cel('D|libero'), cel('P|caselle'), cel('D|caselle'), mf(r['tri'] and r['tri']['nuove'])))
    return '\n'.join(L) + '\n'


def main():
    import numpy
    versioni = OrderedDict([('python', sys.version.split()[0]), ('numpy', numpy.__version__), ('automa', H.VERSIONE), ('testi', AT.VERSIONE)])
    os.makedirs(USCITA, exist_ok=True)
    percorso = os.path.join(USCITA, 'ia31_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    fasi = os.environ.get('FASI', 'AS')
    print('ia31: %s; testi con automa proprio %d; libri incrociati %d; PICCOLO %s' % ('controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(testi_propri()), len(libri_incrocio()), PICCOLO), flush=True)
    if 'A' in fasi:
        lavori = lavori_fase('A')
        print('== fase A: %d lavori' % len(lavori), flush=True)
        esegui(lavori, processi, percorso, fatte)
    if 'S' in fasi:
        o = analisi(leggi_corse(percorso), versioni)
        with open(os.path.join(USCITA, 'ia31_automa_minimo.json'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(o, fh, ensure_ascii=False, indent=1, default=float)
        with open(os.path.join(USCITA, 'ia31_automa_minimo.md'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(scrivi_md(o))
        print('controlli riusciti: %s' % o['controlli_ok'], flush=True)
        for ch, x in o['L1_taglia'].items():
            print('L1 %s: K_bic %s, K_ho %s, K90 %s' % (ch, x['K_bic'], x['K_ho'], x['K90']), flush=True)


if __name__ == '__main__':
    main()
