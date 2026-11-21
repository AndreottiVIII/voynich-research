# -*- coding: utf-8 -*-
"""Esperimento IA19 (ia19): una COMBINAZIONE di procedimenti riproduce le "firme" del Voynich che nessun procedimento semplice
raggiunge? NON e' una decifrazione: si confrontano procedimenti, non si legge il manoscritto.

Idea. ia14 (21/11) ha misurato sette procedimenti semplici (verboso omofonico, sillabario, nomenclatore, auto-citazione, griglia,
sostituzione con spazi riscritti, polialfabetico) sul profilo di nove firme del Voynich (k90, GL, GR, R_rel, Q, rho, Lambda, E, g):
tutti "lontani"; mai raggiunte k90 e rho, quasi mai E. Qui si provano cinque COMBINAZIONI (verboso + eco leggera di pagina,
verboso con alfabeto ridotto, nomenclatore + verboso, verboso con regole di bordo riga, e tutti gli ingredienti a gradini), con le
STESSE misure, la STESSA scala e lo STESSO raggio di ia14. Nessuna taratura sul Voynich: ogni combinazione ha un parametro con tre
valori fissati in `combinati_procedimenti.py` prima di qualsiasi misura, e si guarda dove cadono.

Riuso (per import, senza modificare niente): ia14 (`ia14_quale_cifrario`: misure, lavori, riferimenti, scala, controlli), che a sua volta
richiama ia02, ia03, ia09, ia10; `cifrari_procedimenti` (testi in chiaro, impaginazione, verboso); i controlli (latino in chiaro,
latino rimescolato, 8 lingue, Naibbe, Timm e Schinner) e le celle dei procedimenti semplici si LEGGONO da `risultati/ia14_corse.jsonl`
(stesso codice, stessi semi: identici al bit; `CONTROLLI19=ricalcola` li rifa). Il controllo del latino in chiaro e' CORRETTO rispetto a
ia14 (vedi `controllo_latino`): la correzione e' una modifica fatta dopo aver visto l'esito di ia14, dichiarata nella preregistrazione.

Preregistrazione: preregistrazioni/ia19.md. Scrive risultati/ia19_procedimenti_combinati.json e .md (solo numeri) e, una riga per lavoro,
risultati/ia19_corse.jsonl (solo numeri: nessuna parola, nessuna riga di testo).
Variabili nuove: COMBINATI19, CONTROLLI19, USCITA_CACHE19, CORSE_IA14. Condivise con ia14 e usate: ISTANZE, NATIVI, LINGUE14 (e quelle di
ia01/ia02/ia03/ia09/ia10: SOLO_CONTROLLI, PAGINE, RIGHE_PAGINA, PASSI, OGNI, PAZIENZA, NASCOSTO, CADUTA, BOOT, FASI, FILTRO, RIPRENDI,
PROCESSI, USCITA). NON impostare PROCEDIMENTI (e' di ia14).
"""
import json, math, os, random, statistics, sys, time, zlib
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
from collections import OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import ia14_quale_cifrario as I14  # noqa: E402
import combinati_procedimenti as CB  # noqa: E402

CP, G, I10 = I14.CP, I14.G, I14.I10
NOME = 'ia19_procedimenti_combinati'
USCITA = G.USCITA
RISULTATI = I14.RISULTATI
SOLO_CONTROLLI = G.SOLO_CONTROLLI
COMBINATI_SEL = [x for x in os.environ.get('COMBINATI19', ','.join(CB.COMBINATI)).split(',') if x]
CONTROLLI19 = os.environ.get('CONTROLLI19', 'ia14')            # 'ia14' = si leggono da ia14_corse.jsonl; 'ricalcola' = si rifanno qui
CORSE_IA14 = os.environ.get('CORSE_IA14', os.path.join(RISULTATI, 'ia14_corse.jsonl'))
CACHE19 = os.environ.get('USCITA_CACHE19', os.path.join(QUI, '..', 'dati', 'cache', 'ia19', 'uscite'))
I10.CACHE = CACHE19       # le liste di parole per famiglia di ia10 vanno solo nella cartella protetta di ia19

COMPS, COMPS_GRU, COMPS_SINT, COMPS_AB = I14.COMPS, I14.COMPS_GRU, I14.COMPS_SINT, I14.COMPS_AB
MIN_MISURE_LEGGIBILI = 7          # se il controllo del latino lascia meno di 7 misure su 9, le letture non si fanno
SOGLIA_ECO = I14.SOGLIA_SINTASSI  # l'eco aggiunta deve alzare E di almeno 0,03 bit per parola rispetto al verboso senza eco
TOLLERANZA_QUOTA_ECO = 0.01       # la quota di parole d'eco realizzata sta entro 0,01 da p
SD_CONTRO = 2.0                   # il campo delle lingue si allarga anche di 2 errori standard (sd fra le istanze / radice di n) della media del latino in chiaro

# coppie per la lettura del contributo degli ingredienti: (cella combinata, cella di riferimento, accoppiate per istanza?)
COPPIE = [('VE_0p02', 'V_3', True), ('VE_0p05', 'V_3', True), ('VE_0p1', 'V_3', True), ('VE_0p05_T6', 'V_6', True),
          ('VA_8', 'V_3', False), ('VA_12', 'V_3', False), ('VA_16', 'V_3', False),
          ('NV_30', 'N_30', False), ('NV_150', 'N_150', False), ('NV_600', 'N_600', False),
          ('VB_0p5', 'V_3', False), ('VB_0p8', 'V_3', False), ('VB_1p0', 'V_3', False),
          ('VT_2', 'VE_0p05', False), ('VT_3', 'VT_2', False), ('VT_4', 'VT_3', False)]

# ---------------------------------------------------------------- testi


def descrittori19():
    """I testi nuovi: nome -> descrizione (tipo 'cella19')."""
    T = OrderedDict()
    for cod in COMBINATI_SEL:
        p = CB.COMBINATI[cod]
        for v in p['valori']:
            for i in range(1, I14.ISTANZE + 1):
                T[CB.nome_istanza(cod, v, i)] = dict(tipo='cella19', cod=cod, valore=v, istanza=i, variante=None, cella=CB.nome_cella(cod, v))
        for c2, v, var in CB.VARIANTI:
            if c2 == cod:
                for i in range(1, I14.ISTANZE + 1):
                    T[CB.nome_istanza(cod, v, i, var)] = dict(tipo='cella19', cod=cod, valore=v, istanza=i, variante=var, cella=CB.nome_cella(cod, v, var))
    return T


def descrittori_tutti():
    """I testi nuovi piu' tutti quelli di ia14 (celle semplici, latino in chiaro, rimescolato, lingue, nativi), per l'analisi."""
    D = OrderedDict(I14.descrittori())
    D.update(descrittori19())
    return D


# i lavori di ia14 (lavoro_gru, lavoro_s9, lavoro_s10) cercano le pagine con `pagine_di` di ia14: qui lo si estende alle celle nuove
if not hasattr(I14, '_pagine_di_originale'):
    I14._pagine_di_originale = I14.pagine_di


def pagine_di19(nome, d):
    if d['tipo'] == 'cella19':
        return CB.genera_combinato(d['cod'], d['valore'], d['istanza'], I14.layout(), d['variante'])[0]
    return I14._pagine_di_originale(nome, d)


I14.pagine_di = pagine_di19


def lavoro19(job):
    return I14.lavoro(job)


def avvia_processo19():
    I14.avvia_processo()


def elenco_lavori19(descr19, descr_ctrl, nativi_lav):
    L = []
    for nome, d in descr19.items():
        for tp in ('R', 'K'):
            L.append(dict(tipo=tp, nome=nome, seme=d['istanza'], descr=d))
    for nome, d in descr19.items():
        L.append(dict(tipo='S10', nome=nome, descr=d))
    for nome, d in descr19.items():
        L.append(dict(tipo='S9', nome=nome, descr=d))
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(I14.chiave_di(j)) for x in filtro)]
    if descr_ctrl:
        L = I14.elenco_lavori(descr_ctrl, nativi_lav) + L
    return L


# ---------------------------------------------------------------- prova del codice


def layout_inventato():
    """Impaginazione INVENTATA (non e' del Voynich): 120 pagine, 10-24 righe da 4 a 11 parole. Solo per la prova del codice."""
    rnd = random.Random(7)
    return [('P%03d' % p, [(j % 8 == 0, rnd.randint(4, 11)) for j in range(rnd.randint(10, 24))]) for p in range(120)]


def prova_codice19():
    """Prove del modulo dei procedimenti combinati su un'impaginazione inventata e sul latino di Plinio (mai Voynich): (1) con p = 0 la
    cella VE e' IDENTICA al verboso di ia14 (T = 3 e T = 6); (2) ogni cella e' deterministica, istanze diverse sono testi diversi; (3) il
    testo di base si decifra (tolte le parole nulle d'eco) e tutte le parole d'eco sono nulle; (4) la quota di eco e' quella voluta;
    (5) il modulo non importa caricatori del Voynich."""
    res = OrderedDict()
    lay = layout_inventato()
    N = sum(CP.parole_per_pagina(lay))
    piatto = lambda P: [w for r in P.values() for _, ws in r for w in ws]  # noqa: E731
    ok = True
    for T, var in ((3, None), (6, 'T6')):
        a, _ = CP.genera('V', T, 1, lay)
        b, _ = CB.genera_combinato('VE', 0.0, 1, lay, var)
        ok = ok and piatto(a) == piatto(b)
    res['VE_senza_eco_identico_al_verboso_di_ia14'] = bool(ok)
    celle = [(c, v, None) for c, p in CB.COMBINATI.items() for v in p['valori']] + list(CB.VARIANTI)
    det = div = dec = eco = nulle = True
    pc = CP.parole_chiaro('latino')
    peggior = 0.0
    for cod, v, var in celle:
        pag, meta = CB.genera_combinato(cod, v, 1, lay, var)
        pag2, _ = CB.genera_combinato(cod, v, 1, lay, var)
        pag3, _ = CB.genera_combinato(cod, v, 2, lay, var)
        det = det and piatto(pag) == piatto(pag2)
        div = div and piatto(pag) != piatto(pag3)
        cfg, info, tipi = meta['config'], meta['_info'], meta['_tipi']
        tutte = piatto(pag)
        base = [w for w, t in zip(tutte, tipi) if t == 'b']
        d = CB.decifra_base(base, info)
        puro = cfg['A'] == 20 and cfg['b'] == 0 and cfg['n'] == 0
        r2 = random.Random(CP.seme_di('V', cfg['T'], 'latino', 1) if puro else CB.seme19(cod, v, var or '', 1))
        inizio = r2.randrange(0, max(1, len(pc) - 3 * N // 2))
        if cfg['n'] > 0:
            sub = pc[inizio:inizio + N]
            atteso = ''.join('[%s]' % w if w in info['libro_insieme'] else w for w in sub)
            dec = dec and atteso.startswith(d) and len(d) > 1000
        else:
            lettere, _ = CP.lettere_da(pc, inizio, int(1.62 * N) + 50)
            dec = dec and d == lettere[:info['lettere_usate']]
        # le parole d'eco sono nulle: non compaiono fra i gruppi decifrati (la base ha esattamente N - eco parole)
        nulle = nulle and len(base) == meta['parole_base'] and len(tutte) == N
        scarto = abs(meta['quota_eco'] - cfg['p'])
        peggior = max(peggior, scarto)
        eco = eco and scarto <= TOLLERANZA_QUOTA_ECO
    res['deterministico'] = bool(det)
    res['istanze_diverse'] = bool(div)
    res['decifrabile_tolte_le_nulle'] = bool(dec)
    res['parole_nulle_e_numero_giusto'] = bool(nulle)
    res['quota_eco_giusta'] = bool(eco)
    res['scarto_quota_eco_massimo'] = float(peggior)
    src = open(CB.__file__.replace('.pyc', '.py'), encoding='utf-8').read()
    res['modulo_senza_caricatori_del_voynich'] = not any(('import ' + m) in src for m in ('trascrizione', 'misure', 'pezzi', 'e134', 'e337', 'sintassi_testi'))
    res['superato'] = all(v for k, v in res.items() if k != 'scarto_quota_eco_massimo')
    return res


# ---------------------------------------------------------------- scala e raggio su un sottoinsieme di misure


def scale_e_raggi_sub(rif, lingue_sint, comps):
    """Come `I14.scale_e_raggi` (stessa scala, stesso raggio, stessa tolleranza) ma sulle sole misure `comps`. Con tutte e nove da' gli stessi
    numeri di ia14 (lo verifica `analizza19`)."""
    V, A, B, sdV = rif['V'], rif['A'], rif['B'], rif['sdV']
    disp = {k: statistics.stdev(v) for k, v in rif['lingue_gru'].items() if len(v) > 2}
    for k in COMPS_SINT:
        vs = [x[k] for x in lingue_sint if x.get(k) is not None]
        if len(vs) > 2:
            disp[k] = statistics.stdev(vs)
    scala = OrderedDict()
    for k in COMPS:
        cand = [x for x in (disp.get(k), sdV.get(k) or 0.0) if x]
        scala[k] = max(cand) if cand else None
    cs = [k for k in comps if scala[k]]
    cab = [k for k in cs if k in COMPS_AB]

    def dist(X, Y, c):
        return math.sqrt(statistics.mean(((X[k] - Y[k]) / scala[k]) ** 2 for k in c))
    dA, dB, dAB = dist(A, V, cab), dist(B, V, cab), dist(A, B, cab)
    d_seme = math.sqrt(statistics.mean((sdV[k] / scala[k]) ** 2 for k in cs if sdV.get(k)))
    eps = max(dA, dB, d_seme)
    tau = OrderedDict()
    for k in COMPS:
        t = 2 * (sdV.get(k) or 0.0)
        if k in COMPS_AB:
            t = max(t, abs(A[k] - V[k]), abs(B[k] - V[k]))
        tau[k] = t
    return scala, dict(d_A=dA, d_B=dB, d_AB=dAB, d_seme=d_seme, epsilon=eps), tau


# ---------------------------------------------------------------- controllo del latino in chiaro (corretto)


def controllo_latino(t0m, t0_sd, n_istanze, rif, lingue_sint):
    """CORREZIONE rispetto a ia14 (dichiarata, fatta dopo aver visto l'esito di ia14). In ia14 il profilo medio di T0 doveva stare nel campo
    delle lingue (min-max) allargato del 10% su tutte e nove le misure: ha mancato GL e Lambda. Il campo e' fatto di singoli campioni e T0 e'
    una media di tre campioni di un solo testo con rumore proprio (Lambda: deviazione standard fra istanze 0,075, piu' del campo stesso).
    Qui: il campo si allarga del maggiore fra il 10% del campo e SD_CONTRO errori standard della media di T0 (deviazione standard fra le istanze divisa per la radice del loro numero). Il controllo e' PER
    MISURA; le misure superate sono quelle "leggibili". Se sono meno di MIN_MISURE_LEGGIBILI le letture non si fanno; se sono meno di nove
    le letture si fanno solo sulle misure leggibili (scala, raggio e firme ricalcolati su quelle)."""
    det = OrderedDict()
    for k in COMPS:
        vs = rif['lingue_gru'][k] if k in COMPS_GRU else [x[k] for x in lingue_sint if x.get(k) is not None]
        if len(vs) < 3 or t0m is None or t0m.get(k) is None:
            det[k] = dict(superato=None)
            continue
        lo, hi = min(vs), max(vs)
        marg_dieci = I14.ALLARGA_RANGE * (hi - lo)
        marg_rumore = SD_CONTRO * (t0_sd.get(k) or 0.0) / math.sqrt(max(n_istanze, 1))
        marg = max(marg_dieci, marg_rumore)
        det[k] = dict(valore=t0m[k], minimo=lo, massimo=hi, margine=marg, margine_dieci=marg_dieci, margine_rumore=marg_rumore,
                      superato=bool(lo - marg <= t0m[k] <= hi + marg),
                      superato_vecchio=bool(lo - marg_dieci <= t0m[k] <= hi + marg_dieci))
    leggibili = [k for k in COMPS if det[k].get('superato')]
    return dict(dettaglio=det, eseguito=any(v['superato'] is not None for v in det.values()), misure_leggibili=leggibili,
                misure_non_leggibili=[k for k in COMPS if k not in leggibili],
                superato=len(leggibili) >= MIN_MISURE_LEGGIBILI, tutte_e_nove=len(leggibili) == len(COMPS))


# ---------------------------------------------------------------- analisi


def media_sd(profili):
    medio = OrderedDict((k, I14.media_non_nulla([p[k] for p in profili])) for k in COMPS)
    sd = OrderedDict((k, I14.sd_non_nulla([p[k] for p in profili])) for k in COMPS)
    return medio, sd


def valuta(celle_inst, V, scala, raggi, tau, comps):
    """Per ogni cella: profilo medio, distanza, classe, firme (sulle sole misure `comps`)."""
    eps = raggi['epsilon']
    out = OrderedDict()
    for cella, c in celle_inst.items():
        profili = [p for p in c['profili']]
        medio, sd = media_sd(profili)
        dm, zs, nz = I14.distanza(medio, V, scala, comps)
        d_i = [I14.distanza(p, V, scala, comps)[0] for p in profili]
        classi_i = [I14.classe(x, eps) for x in d_i]
        firme = OrderedDict((k, (abs(medio[k] - V[k]) <= tau[k]) if medio[k] is not None else None) for k in COMPS)
        larghe = OrderedDict((k, (abs(medio[k] - V[k]) <= 2 * tau[k]) if medio[k] is not None else None) for k in COMPS)
        fc = [k for k in comps if firme[k]]
        out[cella] = OrderedDict(
            descr=c['descr'], istanze=len(profili), medio=medio, sd_istanze=sd, z=zs, componenti_misurate=nz, distanza=dm, distanza_per_istanza=d_i,
            sd_distanza=I14.sd_non_nulla(d_i), classe=I14.classe(dm, eps), classi_per_istanza=classi_i, stabile=len(set(classi_i)) == 1,
            firme=firme, firme_larghe=larghe, firme_raggiunte=len(fc), firme_raggiunte_larghe=sum(1 for k in comps if larghe[k]),
            misure_in_lettura=len(comps), mancate=[k for k in comps if firme[k] is False], avvertenze=sorted(set(c['flag'])))
    return out


def analizza19(corse, versioni):
    descr = descrittori_tutti()
    rif = I14.riferimenti()
    R, K, S9, S10, errori = I14.raccogli(corse)
    V = rif['V']
    istanze = OrderedDict()
    for nome, d in descr.items():
        semi = [d['istanza']] if d['tipo'] in ('cella', 'cella19', 'chiaro') else list(range(1, I14.ISTANZE + 1)) if d['tipo'] == 'nativo' else [None]
        for s in semi:
            p, flag = I14.profilo_istanza(nome, R, K, S9, S10, s)
            istanze[(nome, s)] = dict(profilo=p, flag=flag, descr=d)
    lingue_sint = [istanze[(n, None)]['profilo'] for n, d in descr.items() if d['tipo'] == 'lingua' and (n, None) in istanze]
    scala, raggi, tau = I14.scale_e_raggi(rif, lingue_sint)
    # controllo di coerenza: la mia scala sul sottoinsieme "tutte e nove" e' quella di ia14
    scala2, raggi2, tau2 = scale_e_raggi_sub(rif, lingue_sint, COMPS)
    coerente = all(abs((scala[k] or 0) - (scala2[k] or 0)) < 1e-12 for k in COMPS) and abs(raggi['epsilon'] - raggi2['epsilon']) < 1e-12
    # celle (media sulle istanze): le nuove, le semplici di ia14 (riferimento), il latino in chiaro
    celle = OrderedDict()
    for nome, d in descr.items():
        if d['tipo'] not in ('cella', 'cella19', 'chiaro'):
            continue
        c = celle.setdefault(d['cella'], dict(descr=dict((k, v) for k, v in d.items() if k != 'istanza'), profili=[], flag=[], nomi=[]))
        p = istanze[(nome, d['istanza'])]
        c['profili'].append(p['profilo'])
        c['flag'].extend(p['flag'])
        c['nomi'].append(nome)
    # profilo medio e rumore del latino in chiaro
    t0 = celle.get('T0')
    t0m, t0sd = media_sd(t0['profili']) if t0 else (None, OrderedDict())
    d_t0 = I14.distanza(t0m, V, scala)[0] if t0m else None
    ctrl = I14.controlli(descr, rif, istanze, R, K, S9, S10, scala, tau, raggi, t0m, d_t0, lingue_sint)
    ctrl['latino_in_chiaro_ia14'] = ctrl.pop('latino_in_chiaro_tra_le_lingue')       # il controllo vecchio, solo per memoria
    lat = controllo_latino(t0m, t0sd, len(t0['profili']) if t0 else 0, rif, lingue_sint)
    ctrl['latino_in_chiaro_corretto'] = lat
    # controllo dell'eco (positivo): VE con p = 0,10 deve avere E almeno 0,03 sopra il verboso senza eco (V_3 di ia14)
    ve, v3 = celle.get('VE_0p1'), celle.get('V_3')
    if ve and v3 and I14.media_non_nulla([p['E'] for p in ve['profili']]) is not None and I14.media_non_nulla([p['E'] for p in v3['profili']]) is not None:
        dE = I14.media_non_nulla([p['E'] for p in ve['profili']]) - I14.media_non_nulla([p['E'] for p in v3['profili']])
        ctrl['eco_misurabile'] = dict(eseguito=True, aumento_E=dE, soglia=SOGLIA_ECO, superato=bool(dE >= SOGLIA_ECO))
    else:
        ctrl['eco_misurabile'] = dict(eseguito=False, superato=False)
    ctrl['codice19'] = prova_codice19()
    ctrl['scala_coerente_con_ia14'] = dict(superato=bool(coerente), eseguito=True)
    # leggibilita'
    comps_leg = list(lat['misure_leggibili'])
    scala_l, raggi_l, tau_l = scale_e_raggi_sub(rif, lingue_sint, comps_leg)
    # la separazione si rifa sulle misure in lettura (con tutte e nove e' quella di ia14)
    d_t0_l = I14.distanza(t0m, V, scala_l, comps_leg)[0] if t0m else None
    ctrl['separazione_in_lettura'] = dict(distanza_latino_in_chiaro=d_t0_l, epsilon=raggi_l['epsilon'],
                                          rapporto=(d_t0_l / raggi_l['epsilon']) if d_t0_l and raggi_l['epsilon'] else None, soglia=I14.SEPARAZIONE_MIN,
                                          eseguito=d_t0_l is not None, superato=bool(d_t0_l is not None and d_t0_l >= I14.SEPARAZIONE_MIN * raggi_l['epsilon']))
    valide = OrderedDict(
        riproduzione=bool(ctrl['riproduzione_rete']['superato'] and ctrl['riproduzione_sintassi']['superato']),
        latino_in_chiaro=bool(lat['superato']),
        separazione=bool(ctrl['separazione_in_lettura']['superato']),
        negativo=bool(ctrl['negativo_rimescolato']['superato']),
        codice=bool(ctrl['codice']['superato'] and ctrl['codice19']['superato']),
        scala=bool(coerente))
    generale = all(valide.values())
    completo = valuta(celle, V, scala, raggi, tau, COMPS)
    leggibile = valuta(celle, V, scala_l, raggi_l, tau_l, comps_leg) if comps_leg != COMPS else completo
    letture = leggi(leggibile, completo, celle, ctrl, valide, generale, comps_leg, raggi_l, rif)
    altri = OrderedDict()
    for nome, d in descr.items():
        if d['tipo'] in ('nativo', 'lingua', 'negativo'):
            semi = list(range(1, I14.ISTANZE + 1)) if d['tipo'] == 'nativo' else [None]
            profili = [istanze[(nome, s)]['profilo'] for s in semi]
            medio, sd = media_sd(profili)
            dm, zs, nz = I14.distanza(medio, V, scala_l, comps_leg)
            altri[nome] = OrderedDict(tipo=d['tipo'], medio=medio, sd_istanze=sd, distanza=dm, componenti_misurate=nz, classe=I14.classe(dm, raggi_l['epsilon']),
                                      firme_raggiunte=sum(1 for k in comps_leg if medio[k] is not None and abs(medio[k] - V[k]) <= tau_l[k]))
    out = OrderedDict(
        esperimento='ia19', versioni=versioni,
        parametri=OrderedDict(ISTANZE=I14.ISTANZE, COMBINATI19=COMBINATI_SEL, CONTROLLI19=CONTROLLI19, CORSE_IA14=os.path.basename(CORSE_IA14), BOOT=I14.BOOT,
                              SOLO_CONTROLLI=SOLO_CONTROLLI, NATIVI=I14.NATIVI, LINGUE14=I14.LINGUE14,
                              griglia=OrderedDict((c, OrderedDict(nome=p['nome'], parametro=p['par'], valori=list(p['valori']))) for c, p in CB.COMBINATI.items()),
                              varianti=[list(x) for x in CB.VARIANTI],
                              soglie=OrderedDict(MIN_MISURE_LEGGIBILI=MIN_MISURE_LEGGIBILI, SOGLIA_ECO=SOGLIA_ECO, TOLLERANZA_QUOTA_ECO=TOLLERANZA_QUOTA_ECO,
                                                 SD_CONTRO=SD_CONTRO, CLASSE_DENTRO=I14.CLASSE_DENTRO, CLASSE_VICINO=I14.CLASSE_VICINO,
                                                 SEPARAZIONE_MIN=I14.SEPARAZIONE_MIN, ALLARGA_RANGE=I14.ALLARGA_RANGE, K_TEMA=CB.K_TEMA, Q_TEMA=CB.Q_TEMA,
                                                 FATTORE_PREFISSI=CB.FATTORE_PREFISSI)),
        riferimenti=OrderedDict(Voynich=V, Voynich_A=rif['A'], Voynich_B=rif['B'], sd_voynich=rif['sdV'], scala=scala_l, scala_completa=scala, tolleranza_firma=tau_l,
                                raggi=raggi_l, raggi_completi=raggi, misure_in_lettura=comps_leg, impronte=rif['impronte'],
                                impronta_corse_ia14=(I14.impronta(os.path.relpath(CORSE_IA14, RISULTATI)) if CONTROLLI19 == 'ia14' and os.path.exists(CORSE_IA14) else None)),
        celle=leggibile, celle_complete=completo if comps_leg != COMPS else None, altri=altri,
        errori=[dict(nome=e['nome'], lavoro=e['lavoro'], errore=e['errore']) for e in errori], controlli=ctrl, letture=letture)
    out = I14.pulisci(out)
    os.makedirs(USCITA, exist_ok=True)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    righe = scrivi_md(out)
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(righe) + '\n')
    print('\n'.join(righe[:70]), flush=True)
    return out


def leggi(celle, completo, tutte, ctrl, valide, generale, comps_leg, raggi, rif):
    """Le letture preregistrate (L1-L6). `celle` e' la valutazione sulle misure leggibili. Una lettura e' 'non leggibile' se un controllo da cui
    dipende non e' superato; per le combinazioni con l'eco (VE, VT) serve anche il controllo dell'eco."""
    n = len(comps_leg)
    soglia_parziale = math.ceil(2 * n / 3)
    eco_ok = bool(ctrl['eco_misurabile']['superato'])
    L = OrderedDict(valide=valide, controllo_eco=eco_ok, leggibile=bool(generale), misure_in_lettura=comps_leg, misure_non_leggibili=[k for k in COMPS if k not in comps_leg])
    nuove = OrderedDict((c, v) for c, v in celle.items() if v['descr']['tipo'] == 'cella19')
    semplici = OrderedDict((c, v) for c, v in celle.items() if v['descr']['tipo'] == 'cella')

    def leggibile_cod(cod):
        return bool(generale and (eco_ok or cod not in ('VE', 'VT')))
    L['L1_distanza'] = OrderedDict((c, OrderedDict(distanza=v['distanza'], classe=v['classe'], stabile=v['stabile'], leggibile=leggibile_cod(v['descr']['cod'])))
                                   for c, v in nuove.items())
    L['L2_firme'] = OrderedDict((c, OrderedDict(raggiunte=v['firme_raggiunte'], su=n, larghe=v['firme_raggiunte_larghe'], mancate=v['mancate'],
                                                insieme='si' if v['firme_raggiunte'] == n else 'quasi' if v['firme_raggiunte'] >= n - 2 else 'no',
                                                leggibile=leggibile_cod(v['descr']['cod']))) for c, v in nuove.items())
    per_proc = OrderedDict()
    for cod, p in CB.COMBINATI.items():
        cs = [(c, v) for c, v in nuove.items() if v['descr']['cod'] == cod and not v['descr'].get('variante')]
        if not cs:
            continue
        mig = min(cs, key=lambda x: x[1]['distanza'] if x[1]['distanza'] is not None else 1e9)

        def classe_cod(v):
            if v['classe'] == 'dentro' and v['firme_raggiunte'] >= n - 1 and v['stabile']:
                return 'compatibile'
            if v['classe'] in ('dentro', 'vicino') and v['firme_raggiunte'] >= soglia_parziale:
                return 'parziale'
            return 'no'
        ordine = {'compatibile': 2, 'parziale': 1, 'no': 0}
        esiti = [classe_cod(v) for _, v in cs]
        per_proc[cod] = OrderedDict(nome=p['nome'], distanza_minima=mig[1]['distanza'], cella_piu_vicina=mig[0],
                                    distanza_massima=max((v['distanza'] for _, v in cs if v['distanza'] is not None), default=None),
                                    classi=[v['classe'] for _, v in cs], firme_massime=max(v['firme_raggiunte'] for _, v in cs),
                                    esito=max(esiti, key=lambda e: ordine[e]), leggibile=leggibile_cod(cod))
    L['L3_per_combinazione'] = per_proc
    per_firma = OrderedDict()
    for k in COMPS:
        comb = sorted({v['descr']['cod'] for v in nuove.values() if v['firme'].get(k)})
        simp = sorted({v['descr']['cod'] for v in semplici.values() if v['firme'].get(k)})
        per_firma[k] = OrderedDict(in_lettura=k in comps_leg, combinazioni_che_la_raggiungono=comb, celle_combinate=sum(1 for v in nuove.values() if v['firme'].get(k)),
                                   celle_combinate_totali=len(nuove), procedimenti_semplici_che_la_raggiungono=simp,
                                   celle_semplici=sum(1 for v in semplici.values() if v['firme'].get(k)), celle_semplici_totali=len(semplici),
                                   nuova=bool(comb) and not simp)
    L['L4_per_firma'] = per_firma
    coppie = OrderedDict()
    for a, b, app in COPPIE:
        x, y = celle.get(a), celle.get(b)
        if not (x and y):
            continue
        if app:
            sdp = {k: I14.sd_non_nulla([p[k] - q[k] for p, q in zip(tutte[a]['profili'], tutte[b]['profili']) if p[k] is not None and q[k] is not None]) for k in COMPS}
        else:
            sdp = {k: max(x['sd_istanze'][k], y['sd_istanze'][k]) for k in COMPS}
        diff = OrderedDict((k, (x['medio'][k] - y['medio'][k]) if x['medio'][k] is not None and y['medio'][k] is not None else None) for k in COMPS)
        coppie[a + ' contro ' + b] = OrderedDict(
            accoppiate=app, distanza_combinata=x['distanza'], distanza_riferimento=y['distanza'],
            differenza_distanza=(x['distanza'] - y['distanza']) if x['distanza'] is not None and y['distanza'] is not None else None,
            differenza_per_misura=diff, conta=[k for k in COMPS if diff[k] is not None and abs(diff[k]) > 2 * max(sdp[k], 1e-12)])
    L['L5_contributo_ingredienti'] = coppie
    dcomb = [(c, v['distanza']) for c, v in nuove.items() if v['distanza'] is not None]
    dsimp = [(c, v['distanza']) for c, v in semplici.items() if v['distanza'] is not None]
    if dcomb and dsimp:
        c1, d1 = min(dcomb, key=lambda x: x[1])
        c2, d2 = min(dsimp, key=lambda x: x[1])
        sd1 = nuove[c1]['sd_distanza']
        L['L6_contro_i_semplici'] = OrderedDict(combinata_piu_vicina=c1, distanza=d1, semplice_piu_vicina=c2, distanza_semplice=d2, differenza=d1 - d2,
                                                migliore=bool(d1 < d2 - 2 * sd1), firme_massime_combinate=max(v['firme_raggiunte'] for v in nuove.values()),
                                                firme_massime_semplici=max((v['firme_raggiunte'] for v in semplici.values()), default=None))
    return L


def f3(x):
    return I14.f3(x)


def f2(x):
    return I14.f2(x)


def scrivi_md(o):
    R = o['riferimenti']
    comps = R['misure_in_lettura']
    L = []
    L.append('# ia19 - procedimenti combinati e le firme del Voynich')
    L.append('')
    L.append('Non e\' una decifrazione: si confrontano procedimenti. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia19.md`.')
    L.append('')
    L.append('## Controlli')
    L.append('')
    c = o['controlli']
    for k in ('riproduzione_rete', 'riproduzione_sintassi', 'latino_in_chiaro_corretto', 'separazione_in_lettura', 'negativo_rimescolato', 'eco_misurabile', 'scala_coerente_con_ia14'):
        L.append('- %s: eseguito %s, superato %s' % (k, c[k].get('eseguito'), c[k].get('superato')))
    lat = c['latino_in_chiaro_corretto']
    L.append('- latino in chiaro, misure leggibili: %s; non leggibili: %s' % (', '.join(lat['misure_leggibili']) or '-', ', '.join(lat['misure_non_leggibili']) or '-'))
    L.append('- codice (ia14): %s' % ', '.join('%s %s' % (k, v) for k, v in c['codice'].items()))
    L.append('- codice (ia19): %s' % ', '.join('%s %s' % (k, v) for k, v in c['codice19'].items()))
    L.append('- letture leggibili: %s (%s); controllo dell\'eco %s' % (o['letture']['leggibile'], ', '.join('%s %s' % (k, v) for k, v in o['letture']['valide'].items()), o['letture']['controllo_eco']))
    L.append('')
    L.append('## Riferimenti e misure in lettura (%s)' % ', '.join(comps))
    L.append('')
    L.append('| misura | Voynich | A | B | sd Voynich | scala | tolleranza |')
    L.append('|---|---|---|---|---|---|---|')
    for k in I14.COMPS:
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (I14.NOMI_COMPS[k], f3(R['Voynich'].get(k)), f3(R['Voynich_A'].get(k)), f3(R['Voynich_B'].get(k)),
                                                       f3(R['sd_voynich'].get(k)), f3(R['scala'].get(k)), f3(R['tolleranza_firma'].get(k))))
    r = R['raggi']
    L.append('')
    L.append('Raggio epsilon %s (A dal Voynich %s, B %s, A contro B %s, rumore del Voynich da se\' %s).' % (f2(r['epsilon']), f2(r['d_A']), f2(r['d_B']), f2(r['d_AB']), f2(r['d_seme'])))
    L.append('')
    L.append('## Celle: distanza dal Voynich (unita\' di scala) e firme raggiunte (su %d misure in lettura)' % len(comps))
    L.append('')
    L.append('| cella | tipo | d | classe | stabile | firme | larghe | mancate |')
    L.append('|---|---|---|---|---|---|---|---|')
    for nome, v in o['celle'].items():
        d = v['descr']
        tp = ('combinazione ' + CB.COMBINATI[d['cod']]['nome']) if d['tipo'] == 'cella19' else (CP.PROCEDIMENTI[d['cod']]['nome'] + ' (ia14)') if d['tipo'] == 'cella' else 'latino in chiaro'
        L.append('| %s | %s | %s | %s | %s | %d/%d | %d/%d | %s |' % (nome, tp, f2(v['distanza']), v['classe'], v['stabile'], v['firme_raggiunte'], v['misure_in_lettura'],
                                                                  v['firme_raggiunte_larghe'], v['misure_in_lettura'], ','.join(v['mancate']) or '-'))
    L.append('')
    L.append('## Profilo medio delle celle (media sulle istanze; sd fra istanze fra parentesi)')
    L.append('')
    L.append('| cella | ' + ' | '.join(I14.COMPS) + ' |')
    L.append('|---|' + '---|' * len(I14.COMPS))
    for nome, v in o['celle'].items():
        L.append('| %s | ' % nome + ' | '.join('%s (%s)' % (f3(v['medio'][k]), f3(v['sd_istanze'][k])) for k in I14.COMPS) + ' |')
    L.append('')
    L.append('## Nativi, lingue e negativo')
    L.append('')
    L.append('| testo | ' + ' | '.join(I14.COMPS) + ' | d | classe |')
    L.append('|---|' + '---|' * (len(I14.COMPS) + 2))
    for nome, v in o['altri'].items():
        L.append('| %s | ' % nome + ' | '.join(f3(v['medio'][k]) for k in I14.COMPS) + ' | %s | %s |' % (f2(v['distanza']), v['classe']))
    L.append('')
    L.append('## Letture')
    L.append('')
    for cod, v in o['letture']['L3_per_combinazione'].items():
        L.append('- %s (%s): esito %s (leggibile %s); distanza minima %s (%s), massima %s, classi %s, firme al massimo %d' % (
            cod, v['nome'], v['esito'], v['leggibile'], f2(v['distanza_minima']), v['cella_piu_vicina'], f2(v['distanza_massima']), '/'.join(v['classi']), v['firme_massime']))
    L.append('')
    for k, v in o['letture']['L4_per_firma'].items():
        L.append('- firma %s%s: combinazioni %d/%d celle (%s); semplici %d/%d (%s)%s' % (
            k, '' if v['in_lettura'] else ' (fuori lettura)', v['celle_combinate'], v['celle_combinate_totali'], ','.join(v['combinazioni_che_la_raggiungono']) or '-',
            v['celle_semplici'], v['celle_semplici_totali'], ','.join(v['procedimenti_semplici_che_la_raggiungono']) or '-', ' NUOVA' if v['nuova'] else ''))
    L.append('')
    L6 = o['letture'].get('L6_contro_i_semplici')
    if L6:
        L.append('- contro i semplici: combinata piu\' vicina %s (%s), semplice piu\' vicino %s (%s), migliore %s' % (L6['combinata_piu_vicina'], f2(L6['distanza']),
                                                                                                                L6['semplice_piu_vicina'], f2(L6['distanza_semplice']), L6['migliore']))
    L.append('')
    L.append('## Contributo degli ingredienti (differenza di distanza e misure che cambiano oltre 2 deviazioni standard)')
    L.append('')
    for k, v in o['letture']['L5_contributo_ingredienti'].items():
        L.append('- %s: differenza di distanza %s; cambiano: %s' % (k, f2(v['differenza_distanza']), ','.join(v['conta']) or '-'))
    if o['errori']:
        L.append('')
        L.append('ERRORI: %d lavori falliti: %s' % (len(o['errori']), ', '.join('%s %s' % (e['lavoro'], e['nome']) for e in o['errori'])))
    return L


# ---------------------------------------------------------------- main


def main():
    import torch
    import sklearn
    import scipy
    if os.environ.get('PROCEDIMENTI'):
        raise SystemExit('FERMO: la variabile PROCEDIMENTI e\' di ia14 e cambierebbe le celle di riferimento: toglierla')
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=np.__version__, sklearn=sklearn.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'corse,analisi').split(',')
    descr19 = descrittori19()
    descr_ctrl = OrderedDict((n, d) for n, d in I14.descrittori().items() if d['tipo'] in ('chiaro', 'negativo', 'lingua', 'nativo')) if CONTROLLI19 == 'ricalcola' else OrderedDict()
    prova = [k for k in ('PASSI', 'OGNI', 'PAZIENZA', 'SEMI', 'NASCOSTO', 'CADUTA', 'PAGINE', 'RIGHE_PAGINA', 'FILTRO', 'SOLO_CONTROLLI', 'USCITA', 'BOOT',
                         'ISTANZE', 'NATIVI', 'LINGUE14', 'COMBINATI19', 'CONTROLLI19', 'USCITA_CACHE19', 'CORSE_IA14') if k in os.environ]
    print("variabili d'ambiente attive: %s" % (', '.join(prova) if prova else 'nessuna'), flush=True)
    print('testi nuovi: %d; testi di controllo da rifare: %d' % (len(descr19), len(descr_ctrl)), flush=True)
    cod = prova_codice19()
    print('prova del codice dei procedimenti combinati: %s' % dict(cod), flush=True)
    if not cod['superato']:
        raise SystemExit('FERMO: il codice dei procedimenti combinati non supera la sua prova')
    percorso = os.path.join(USCITA, 'ia19_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [x for x in I14.carica_corse(percorso) if x.get('tipo') != 'errore']
    elif 'corse' in fasi:
        open(percorso, 'w').close()
    if 'corse' in fasi:
        fatte = {json.dumps(x['chiave']) for x in corse}
        nativi_lav = I14.lavori_nativi_gru(descr_ctrl) if descr_ctrl else {}
        tutti = elenco_lavori19(descr19, descr_ctrl, nativi_lav)
        da_fare = [j for j in tutti if json.dumps(I14.chiave_di(j)) not in fatte]
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(tutti) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 1))
        with get_context('spawn').Pool(processi, initializer=avvia_processo19) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro19, da_fare), 1):
                corse.append(r)
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s)%s' % (i, len(da_fare), (time.time() - inizio) / 60, r['chiave'], r['tempo'],
                                                         (' ERRORE ' + r['errore']) if r['tipo'] == 'errore' else ''), flush=True)
    elif os.path.exists(percorso):
        corse = [x for x in I14.carica_corse(percorso) if x.get('tipo') != 'errore']
    if 'analisi' in fasi:
        if CONTROLLI19 == 'ia14':
            if not os.path.exists(CORSE_IA14):
                raise SystemExit('FERMO: manca %s (i controlli e le celle semplici si leggono da li)' % CORSE_IA14)
            corse = [x for x in I14.carica_corse(CORSE_IA14) if x.get('tipo') != 'errore'] + corse
        analizza19(corse, versioni)


if __name__ == '__main__':
    main()
