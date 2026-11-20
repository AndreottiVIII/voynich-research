# -*- coding: utf-8 -*-
"""Esperimento IA14 (ia14): quale procedimento produce le "firme" del Voynich. NON e' una decifrazione: si confrontano
procedimenti (famiglie di cifrari e di generatori), non si legge il manoscritto.

Idea. Le misure di ia02, ia03, ia09 e ia10 hanno dato al Voynich nove "firme" (contesto cortissimo, riga sopra inutile, pezzi
ripetuti a distanza che aiutano poco, parola mai vista che costa come una vista, parole inventate vere, quota di copia con
la sua parte locale, eco della pagina, ordine debole fra famiglie). Qui si applicano le STESSE misure a testi prodotti da sette
procedimenti (cifrari verbosi, sillabari, nomenclatori, auto-citazione, tabella a griglia, sostituzione con spazi riscritti,
polialfabetico), con testi in chiaro latino, italiano o tedesco dove il procedimento ne ha uno, nell'impaginazione del Voynich
(solo come lunghezze), e si vede dove cade ciascuno rispetto al Voynich e alle lingue. Nessuna taratura: ogni procedimento ha
un solo parametro con tre valori fissati in `cifrari_procedimenti.py`, e si misura dove cadono.

Misure (nove firme, tutte importate dai moduli gia' eseguiti, mai riscritte):
  k90, GL, GR (corte)   ia03, variante B (GRU piu' cache): k90 interpolato, guadagno lungo, guadagno dalla riga sopra
  R_rel, Q              ia02: rapporto fra costo delle parole mai viste e viste (rete diviso trigrammi); quota di parole
                        inventate dalla rete che compaiono davvero nel resto del testo
  rho, Lambda, E        ia09: quota di copia, quota locale della copia, eco netta (bit per parola)
  g                     ia10: ordine fra famiglie di parole oltre la composizione della riga (bit per coppia)
Le misure del Voynich NON si ricalcolano: si leggono da risultati/ia02..ia10 (stesse definizioni, stesse funzioni).

Testi per ogni cella (procedimento, valore del parametro): ISTANZE istanze (3 predefinito), ognuna con il suo seme di generazione
e il suo seme della rete (il numero dell'istanza). Controlli: Naibbe e Timm e Schinner (testi gia' misurati) e il latino
(Plinio) ricalcolati dallo stesso codice, che devono riprodurre ia02/ia03/ia09/ia10; il latino in chiaro nell'impaginazione del
Voynich, che deve cadere fra le lingue; il latino in chiaro con le parole mescolate, che non deve avere sintassi; 8 lingue
nell'impaginazione del Voynich, per la dispersione delle misure di ia09 e ia10.

Preregistrazione: preregistrazioni/ia14.md. Scrive risultati/ia14_quale_cifrario.json e .md (solo numeri) e, una riga per lavoro,
risultati/ia14_corse.jsonl (solo numeri: nessuna parola, nessuna riga di testo).
Variabili nuove: ISTANZE, PROCEDIMENTI, LINGUE14, NATIVI, USCITA_CACHE14. Le altre sono quelle di ia01/ia02/ia03/ia09/ia10: SOLO_CONTROLLI,
PAGINE, RIGHE_PAGINA, PASSI, OGNI, PAZIENZA, NASCOSTO, CADUTA, BOOT (qui predefinito 200), FASI (corse, analisi), FILTRO, RIPRENDI, PROCESSI.
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
import e3c95_imparabilita as e95  # noqa: E402
import ia01_giudice_neurale as G  # noqa: E402
import ia02_parole_mai_viste as I2  # noqa: E402
import ia03_contesto as I3  # noqa: E402
import ia09_dove_sta_sintassi as I9  # noqa: E402
import ia10_famiglie_parole as I10  # noqa: E402
import sintassi_testi as TT  # noqa: E402
import famiglie_testi as FT  # noqa: E402
import cifrari_procedimenti as CP  # noqa: E402

NOME = 'ia14_quale_cifrario'
USCITA = G.USCITA
SOLO_CONTROLLI = G.SOLO_CONTROLLI
RISULTATI = os.path.join(QUI, '..', 'risultati')
ISTANZE = int(os.environ.get('ISTANZE', 3))
PROCEDIMENTI_SEL = [x for x in os.environ.get('PROCEDIMENTI', ','.join(CP.PROCEDIMENTI)).split(',') if x]
NATIVI = os.environ.get('NATIVI', '1') == '1'
BOOT = int(os.environ.get('BOOT', 200))
CACHE14 = os.environ.get('USCITA_CACHE14', os.path.join(QUI, '..', 'dati', 'cache', 'ia14', 'uscite'))
# ia09 e ia10 leggono BOOT e CACHE come variabili di modulo: qui si fissano (anche nei processi figli, perche' sono a livello di modulo)
I9.BOOT = BOOT
I10.BOOT = BOOT
I10.CACHE = CACHE14

# le otto lingue per la dispersione delle misure di sintassi (testi di Gaskell e Bowern, scelti prima)
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
LINGUE14 = [x for x in os.environ.get('LINGUE14', ','.join(LINGUE_CHIAVI)).split(',') if x]

COMPS = ['k90', 'GL', 'GR', 'R_rel', 'Q', 'rho', 'lambda', 'E', 'g']
COMPS_GRU = COMPS[:5]
COMPS_SINT = COMPS[5:]
COMPS_AB = [c for c in COMPS if c != 'lambda']        # per A e B del Voynich non c'e' Lambda
NOMI_COMPS = OrderedDict([
    ('k90', 'k90 (segni di contesto, interpolato)'), ('GL', 'GL (guadagno lungo, bit per segno)'),
    ('GR', 'GR (riga sopra, parole corte, bit)'), ('R_rel', 'R_rel (mai viste / viste)'), ('Q', 'Q (inventate vere)'),
    ('rho', 'rho (quota di copia)'), ('lambda', 'Lambda (quota locale)'), ('E', 'E (eco netta, bit per parola)'),
    ('g', 'g (ordine fra famiglie, bit per coppia)')])

SOGLIA_SINTASSI = 0.03          # bit per parola: come ia09 (SOGLIA_W): sotto, la parte non e' misurabile
RHO_NEUTRO = 0.5                # valore di rho quando nessuna parte (grammatica, eco) e' misurabile (si segnala)
TOLLERANZA_RIPRODUZIONE = dict(frazione_scala=0.25, k90=0.5, rho=0.02, lambda_=0.03, E=0.02, g=0.01, D=0.02)
CLASSE_DENTRO, CLASSE_VICINO = 1.0, 3.0           # multipli di epsilon
SEPARAZIONE_MIN = 2.0           # il latino in chiaro deve stare ad almeno 2 epsilon dal Voynich
ALLARGA_RANGE = 0.10            # il latino in chiaro deve stare dentro il campo delle lingue allargato del 10%
SOGLIA_NEGATIVO_E, SOGLIA_NEGATIVO_G = 0.03, 0.02
K90_NON_DEFINITO = 255.0        # k90 di un testo dove il contesto non guadagna niente (ia03: guadagno totale sotto 0,25 bit)

NOME_IA09 = dict(nat_latino='latino', nat_naibbe='naibbe', nat_ts='ts1')      # nomi dei nativi in ia09 e in ia10
NOME_IA10 = dict(nat_latino='latino', nat_naibbe='naibbe', nat_ts='ts')
NATIVI_GRU = OrderedDict([('nat_naibbe', 'Naibbe'), ('nat_ts', 'Timm e Schinner (seme 1)'), ('nat_latino', 'Latin')])


# ---------------------------------------------------------------- testi

_CACHE = {}


def layout():
    """Impaginazione del Voynich (solo lunghezze): nel Voynich le pagine vere di ia01; con SOLO_CONTROLLI il latino di prova."""
    if 'layout' not in _CACHE:
        _CACHE['layout'] = CP.layout_da_pagine(TT.testo_vere()['pagine'])
    return _CACHE['layout']


def pagine_latino_nativo():
    """Il latino di ia09/ia10 (Plinio in pagine di RIGHE_PAGINA righe, un paragrafo ogni 8): le stesse pagine, costruite leggendo solo il
    file di Plinio."""
    chiave = CP.CHIAVI_CHIARO['latino']
    righe = []
    for l in CP._testo(chiave).splitlines():
        ws = [w for w in (CP.parola_lingua(p) for p in l.split()) if w]
        if ws:
            righe.append(ws)
    npg, rp = int(os.environ.get('PAGINE', 196)), int(os.environ.get('RIGHE_PAGINA', 23))
    pagine = OrderedDict()
    for i in range(npg):
        rows = righe[i * rp:(i + 1) * rp]
        if not rows:
            break
        pagine['L%03d' % i] = [(j % 8 == 0, [tuple(w) for w in r]) for j, r in enumerate(rows)]
    return OrderedDict((p, r) for p, r in sorted(pagine.items()) if sum(len(ws) for _, ws in r) >= G.MIN_PAROLE)


def descrittori():
    """Tutti i testi: nome -> descrizione. Il nome e' fatto di lettere, cifre e trattini bassi (serve anche come nome di file)."""
    T = OrderedDict()
    for cod in PROCEDIMENTI_SEL:
        p = CP.PROCEDIMENTI[cod]
        for v in p['valori']:
            for i in range(1, ISTANZE + 1):
                T[CP.nome_istanza(cod, v, i)] = dict(tipo='cella', cod=cod, valore=v, istanza=i, chiaro=None, cella='%s_%s' % (cod, str(v).replace('.', 'p')))
        for cod2, v, ch in CP.VARIANTI_CHIARO:
            if cod2 == cod:
                for i in range(1, ISTANZE + 1):
                    T[CP.nome_istanza(cod, v, i, ch)] = dict(tipo='cella', cod=cod, valore=v, istanza=i, chiaro=ch,
                                                             cella='%s_%s_%s' % (cod, str(v).replace('.', 'p'), ch))
    for i in range(1, ISTANZE + 1):
        T['T0_i%d' % i] = dict(tipo='chiaro', istanza=i, cella='T0')
    T['Tneg_i1'] = dict(tipo='negativo', istanza=1, cella='Tneg')
    for l in LINGUE14:
        T['LG_' + l] = dict(tipo='lingua', lingua=l, cella='LG_' + l)
    if NATIVI:
        for n in (NATIVI_GRU if not SOLO_CONTROLLI else {'nat_latino': 'Latin'}):
            T[n] = dict(tipo='nativo', cella=n)
    return T


def pagine_di(nome, d):
    """Le pagine (nome pagina -> righe (inizio, [parola])) di un testo non nativo."""
    t = d['tipo']
    if t == 'cella':
        return CP.genera(d['cod'], d['valore'], d['istanza'], layout(), d['chiaro'])[0]
    if t == 'chiaro':
        return CP.testo_lingua_in_layout(CP.CHIAVI_CHIARO['latino'], layout(), d['istanza'])
    if t == 'negativo':
        return CP.rimescola_tutto(CP.testo_lingua_in_layout(CP.CHIAVI_CHIARO['latino'], layout(), 1), CP.seme_di('neg', 1))
    if t == 'lingua':
        return CP.testo_lingua_in_layout(LINGUE_CHIAVI[d['lingua']], layout(), 0)
    raise ValueError(nome)


def blocchi_di(pagine):
    """Blocchi per la rete: una pagina = un blocco (come il Voynich in e3c95), righe = liste di parole."""
    return [[list(ws) for _, ws in rows] for rows in pagine.values()]


def pagine_nativo(nome):
    """Pagine dei testi nativi per ia09/ia10 (solo per i lavori di sintassi); None = lo costruisce ia09 (Timm e Schinner)."""
    if nome == 'nat_latino':
        return pagine_latino_nativo()
    if nome == 'nat_naibbe':
        return FT._da_blocchi(e95.naibbe(), 'N')
    if nome == 'nat_ts':
        return FT._da_blocchi(e95.timm_schinner(), 'T')
    raise ValueError(nome)


# ---------------------------------------------------------------- lavori

def lavoro_gru(job):
    """Un lavoro di rete: 'R' (ia02) o 'K' (ia03) su un testo di un seme. Il lavoro (testi gia' codificati) arriva dal chiamante per i
    nativi, e si prepara qui per gli altri."""
    tipo, nome, seme = job['tipo'], job['nome'], job['seme']
    mod = I2 if tipo == 'R' else I3
    lav = job.get('lavoro')
    if lav is None:
        d = job['descr']
        blocchi = blocchi_di(pagine_di(nome, d))
        t = OrderedDict([(nome, dict(blocchi=blocchi, ruolo='generatore', gruppo=nome, trasforma=None, speciali=None))])
        if tipo == 'R':
            e95.SEMI = (seme,)
            lavori, scarti = I2.prepara(t, t)
        else:
            I3.SEMI = (seme,)
            lavori, scarti = I3.prepara(t)
        if scarti or len(lavori) != 1:
            raise RuntimeError('lavoro di rete non preparato: %s' % (scarti,))
        lav = lavori[0]
    return dict(tipo=tipo, nome=nome, seme=seme, corsa=mod.corsa(lav))


def lavoro_s9(job):
    """ia09 su un testo (e sul testo con le parole mescolate dentro la pagina): rho, Lambda, E, G0 e il tipo. Solo numeri."""
    nome, d = job['nome'], job['descr']
    if d['tipo'] == 'nativo' and nome == 'nat_ts':
        base = 'ts1'                                    # nativo di ia09 (stesse pagine, stesse pieghe)
    else:
        # i nativi hanno il nome che avevano in ia09: rimescolamenti e divisioni dipendono dal nome, e per riprodurre ia09 devono essere gli stessi
        base = NOME_IA09.get(nome, nome)
        pag = pagine_nativo(nome) if d['tipo'] == 'nativo' else pagine_di(nome, d)
        I9._T.clear()
        I9._T[base] = dict(pagine=pag, fold=TT.pieghe(pag), tipo=None)
    r0 = I9.lavoro_C(base)
    if base != 'ts1':
        I9._T[base] = dict(pagine=pag, fold=TT.pieghe(pag), tipo=None)
    r1 = I9.lavoro_C(base + '~p')
    D0, D1 = I9.Dati(r0), I9.Dati(r1)
    W = I9.pesi_bootstrap(len(D0.pag))
    m0, m1 = I9.misure(D0, W), I9.misure(D1, W)
    out = dict(tipo='S9', nome=nome, pagine=len(D0.pag))
    for tg in ('w',):
        r = m0[tg]
        lt = I9.lettura_tipo(r, tg)
        ll = I9.lettura_locale(m0[tg], m1[tg], tg)
        ql = ll.get('quota_locale')
        out.update(rho=float(r['rho'].p), rho_ic=[float(x) for x in r['rho'].ic()], A_gram=float(r['A_gram'].p), A_cn=float(r['A_cn'].p),
                   E=float(r['netto'].p), E_ic=[float(x) for x in r['netto'].ic()], G0=float(r['G0'].p),
                   quota_simile=float(r['quota_simile']), esito_tipo=lt['esito'], esito_locale=ll['esito'],
                   Lambda=(float(ql['punto']) if ql else None), Lambda_ic=([float(x) for x in ql['ic']] if ql else None),
                   E_pagina_rimescolata=float(m1[tg]['netto'].p), costo_base=float(D0.costo_base(tg)))
    return out


def lavoro_s10(job):
    """ia10 su un testo: g (ordine fra famiglie oltre la composizione della riga), D, G, G_c, K. Le liste di parole per famiglia si
    scrivono solo nella cartella protetta (dati/cache/ia14/uscite), come in ia10."""
    nome, d = job['nome'], job['descr']
    if d['tipo'] == 'nativo':
        base, pag = NOME_IA10[nome], pagine_nativo(nome)       # nome di ia10: i semi dipendono dal nome
    else:
        base, pag = nome, pagine_di(nome, d)
    pag = I10._filtra(pag)
    I10._T[base] = FT.Testo(base, pag)
    corse = [I10.lavoro_piega(base, f) for f in range(I10.NF)]
    ris = I10.riassunto_testo(base, corse, {})
    return dict(tipo='S10', nome=nome, pagine=len(pag), g=float(ris['g']['punto']), g_ic=ris['g']['ic'], D=float(ris['D']['punto']),
                D_ic=ris['D']['ic'], G=float(ris['G']['punto']), G_c=float(ris['G_senza_ordine']['punto']), K=ris['K_scelti'],
                coppie=ris['coppie'], ari_semi=ris['ari_semi'], quota_rare_prova=ris['quota_rare_prova'])


def lavoro(job):
    """Un errore non ferma gli altri: si registra come 'errore' (RIPRENDI=1 lo rifa)."""
    inizio = time.time()
    try:
        f = dict(R=lavoro_gru, K=lavoro_gru, S9=lavoro_s9, S10=lavoro_s10)[job['tipo']]
        r = f(job)
    except Exception as e:  # noqa: BLE001
        r = dict(tipo='errore', nome=job['nome'], seme=job.get('seme'), lavoro=job['tipo'], errore='%s: %s' % (type(e).__name__, str(e)[:300]))
    r['chiave'] = chiave_di(job)
    r['tempo'] = round(time.time() - inizio, 1)
    return r


def chiave_di(job):
    return [job['tipo'], job['nome'], job.get('seme')]


def avvia_processo():
    e95.avvia_processo()


def lavori_nativi_gru(descr):
    """I lavori di rete dei nativi (Naibbe, Timm e Schinner, latino) con i testi esatti di ia02 e di ia03: si preparano nel processo
    principale col catalogo di quegli esperimenti (pesante: carica tutte le lingue) e arrivano ai figli gia' codificati."""
    nativi = [n for n, d in descr.items() if d['tipo'] == 'nativo']
    if not nativi:
        return {}
    out = {}
    e95.SEMI = tuple(range(1, ISTANZE + 1))
    t2, scelti2 = I2.catalogo()
    sel2 = OrderedDict((NATIVI_GRU[n], scelti2[NATIVI_GRU[n]]) for n in nativi)
    lav2, scarti = I2.prepara(t2, sel2)
    if scarti:
        raise SystemExit('FERMO: nativi esclusi da ia02: %s' % scarti)
    del t2, scelti2
    for l in lav2:
        out[('R', [n for n in nativi if NATIVI_GRU[n] == l['testo']][0], l['seme'])] = l
    I3.SEMI = tuple(range(1, ISTANZE + 1))
    t3 = I3.catalogo()
    sel3 = OrderedDict((NATIVI_GRU[n], t3[NATIVI_GRU[n]]) for n in nativi)
    lav3, scarti = I3.prepara(sel3)
    if scarti:
        raise SystemExit('FERMO: nativi esclusi da ia03: %s' % dict(scarti))
    del t3
    for l in lav3:
        out[('K', [n for n in nativi if NATIVI_GRU[n] == l['testo']][0], l['seme'])] = l
    return out


def elenco_lavori(descr, nativi_lav):
    L = []
    for nome, d in descr.items():
        if d['tipo'] in ('cella', 'chiaro'):
            for tp in ('R', 'K'):
                L.append(dict(tipo=tp, nome=nome, seme=d['istanza'], descr=d))
        elif d['tipo'] == 'nativo':
            for s in range(1, ISTANZE + 1):
                for tp in ('R', 'K'):
                    L.append(dict(tipo=tp, nome=nome, seme=s, descr=d, lavoro=nativi_lav[(tp, nome, s)]))
    for nome, d in descr.items():
        L.append(dict(tipo='S10', nome=nome, descr=d))
    for nome, d in descr.items():
        L.append(dict(tipo='S9', nome=nome, descr=d))
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    if filtro:
        L = [j for j in L if any(x in json.dumps(chiave_di(j)) for x in filtro)]
    return L


# ---------------------------------------------------------------- riferimenti (letti dai risultati gia' prodotti)

def leggi_json(nome):
    with open(os.path.join(RISULTATI, nome), encoding='utf-8') as f:
        return json.load(f)


def se_da_ic(ic):
    return (ic[1] - ic[0]) / 3.92 if ic and ic[1] == ic[1] and ic[0] == ic[0] else None


def impronta(nome):
    with open(os.path.join(RISULTATI, nome), 'rb') as f:
        return '%08x' % (zlib.crc32(f.read()) & 0xffffffff)


def riferimenti():
    """Voynich (tutto, A, B), valore, deviazione standard fra semi o dal bootstrap, lingue; tutto da risultati/ia02, ia03, ia09, ia10."""
    d2, d3 = leggi_json('ia02_parole_mai_viste.json'), leggi_json('ia03_contesto.json')
    d9, d10 = leggi_json('ia09_dove_sta_sintassi.json'), leggi_json('ia10_famiglie_parole.json')
    T2, T3 = d2['testi'], d3['varianti']['B']['testi']

    def gru(n):
        return dict(k90=T3[n]['k90_interpolato']['media'], GL=T3[n]['GL']['media'], GR=T3[n]['GR_corte']['media'],
                    R_rel=T2[n]['R_rel']['media'], Q=T2[n]['Q_rete']['media'])

    def gru_ds(n):
        return dict(k90=T3[n]['k90_interpolato']['ds'], GL=T3[n]['GL']['ds'], GR=T3[n]['GR_corte']['ds'],
                    R_rel=T2[n]['R_rel']['ds'], Q=T2[n]['Q_rete']['ds'])
    def sint(c9, c10, w=None):
        """rho, E, g, Lambda (valore e deviazione standard dal bootstrap) di un testo di ia09/ia10."""
        w = w or d9['testi'][c9]['w']
        val = dict(rho=w['tipo']['rho']['punto'], E=w['netto']['punto'], g=d10['testi'][c10]['g']['punto'])
        sd = dict(rho=se_da_ic(w['tipo']['rho']['ic']), E=se_da_ic(w['netto']['ic']), g=se_da_ic(d10['testi'][c10]['g']['ic']))
        lam = (w.get('locale') or {}).get('quota_locale')
        if lam:
            val['lambda'], sd['lambda'] = lam['punto'], se_da_ic(lam['ic'])
        return val, sd
    if SOLO_CONTROLLI:
        # SOLO PER LA PROVA DEL CODICE: i riferimenti sono due lingue (nessun numero del Voynich entra nella prova)
        V, A, B = gru('Latin'), gru('English'), gru('Latin')
        sdV = gru_ds('Latin')
        vv, sv = sint('latino', 'latino')
        va, _ = sint('inglese', 'inglese')
        V.update(vv)
        sdV.update(sv)
        A.update(va)
        B.update(vv)
    else:
        V, A, B = gru('Voynich'), gru('Voynich A'), gru('Voynich B')
        sdV = gru_ds('Voynich')
        vv, sv = sint('vere', 'vere')
        V.update(vv)
        sdV.update(sv)
        for X, l, lv in ((A, 'A', 'vereA'), (B, 'B', 'vereB')):
            w = d9['voynich_A_B'][l]['w']
            X.update(rho=w['tipo']['rho']['punto'], E=w['netto']['punto'], g=d10['testi'][lv]['g']['punto'])
    lingue = [n for n in T2 if T2[n]['ruolo'] == 'lingua']
    lin = {k: [] for k in COMPS_GRU}
    for n in lingue:
        x = gru(n)
        ok_q = T2[n].get('Q_ok', True)
        for k in COMPS_GRU:
            if x[k] is not None and (k != 'Q' or ok_q):
                lin[k].append(x[k])
    # riproduzione: i valori dei nativi e dei semi, dai file originali delle corse
    corse2 = [json.loads(l) for l in open(os.path.join(RISULTATI, 'ia02_corse.jsonl'), encoding='utf-8') if l.strip()]
    corse3 = [json.loads(l) for l in open(os.path.join(RISULTATI, 'ia03_corse.jsonl'), encoding='utf-8') if l.strip()]
    orig = {}
    for nome, nm in NATIVI_GRU.items():
        orig[nome] = OrderedDict()
        for c in corse2:
            if c['testo'] == nm:
                m = I2.misure_corsa(c)
                orig[nome].setdefault(c['seme'], {}).update(R_rel=m['R_rel'], Q=m['Q_rete'])
        for c in corse3:
            if c['testo'] == nm:
                m = I3.misure_corsa(c, 'B')
                orig[nome].setdefault(c['seme'], {}).update(k90=m['k90_interpolato'], GL=m['GL'], GR=m['GR_corte'])
    sint = dict(
        ts1=dict(rho=d9['testi']['ts1']['w']['tipo']['rho']['punto'], E=d9['testi']['ts1']['w']['netto']['punto'],
                 **{'lambda': (d9['testi']['ts1']['w'].get('locale', {}).get('quota_locale') or {}).get('punto')}),
        latino=dict(rho=d9['testi']['latino']['w']['tipo']['rho']['punto'], E=d9['testi']['latino']['w']['netto']['punto'],
                    **{'lambda': (d9['testi']['latino']['w'].get('locale', {}).get('quota_locale') or {}).get('punto')}),
        g=dict(nat_ts=d10['testi']['ts']['g']['punto'], nat_naibbe=d10['testi']['naibbe']['g']['punto'], nat_latino=d10['testi']['latino']['g']['punto']),
        D=dict(nat_ts=d10['testi']['ts']['D']['punto'], nat_naibbe=d10['testi']['naibbe']['D']['punto'], nat_latino=d10['testi']['latino']['D']['punto']))
    return dict(V=V, A=A, B=B, sdV=sdV, lingue_gru=lin, originali=orig, sintassi_originale=sint,
                impronte={f: impronta(f) for f in ('ia02_parole_mai_viste.json', 'ia03_contesto.json', 'ia09_dove_sta_sintassi.json',
                                                   'ia10_famiglie_parole.json', 'ia02_corse.jsonl', 'ia03_corse.jsonl')})


# ---------------------------------------------------------------- analisi

def carica_corse(percorso):
    if not os.path.exists(percorso):
        return []
    return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]


def misure_di_corse(c_R, c_K):
    """Per un seme: k90, GL, GR (da ia03 B), R_rel, Q (da ia02)."""
    m = OrderedDict((k, None) for k in COMPS_GRU)
    if c_K is not None:
        x = I3.misure_corsa(c_K, 'B')
        m.update(k90=x['k90_interpolato'], GL=x['GL'], GR=x['GR_corte'])
    if c_R is not None:
        x = I2.misure_corsa(c_R)
        m.update(R_rel=x['R_rel'], Q=x['Q_rete'])
    return m


def misure_sintassi(r9, r10):
    """rho, Lambda, E (ia09) e g (ia10) di un testo, con le regole di imputazione preregistrate (e il segno di quando scattano)."""
    out = OrderedDict((k, None) for k in COMPS_SINT)
    flag = []
    if r9:
        misurabile = max(r9['A_gram'], r9['A_cn']) >= SOGLIA_SINTASSI
        if misurabile:
            out['rho'] = r9['rho']
        else:
            out['rho'] = RHO_NEUTRO
            flag.append('rho_neutro')
        if r9['Lambda'] is not None:
            out['lambda'] = r9['Lambda']
        else:
            out['lambda'] = 0.0
            flag.append('lambda_zero')
        out['E'] = r9['E']
    if r10:
        out['g'] = r10['g']
    return out, flag


def media_non_nulla(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def sd_non_nulla(xs):
    xs = [x for x in xs if x is not None]
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def raccogli(corse):
    R, K, S9, S10, errori = {}, {}, {}, {}, []
    for c in corse:
        if c['tipo'] == 'errore':
            errori.append(c)
        elif c['tipo'] == 'R':
            R.setdefault(c['nome'], {})[c['seme']] = c['corsa']
        elif c['tipo'] == 'K':
            K.setdefault(c['nome'], {})[c['seme']] = c['corsa']
        elif c['tipo'] == 'S9':
            S9[c['nome']] = c
        elif c['tipo'] == 'S10':
            S10[c['nome']] = c
    return R, K, S9, S10, errori


def profilo_istanza(nome, R, K, S9, S10, seme):
    """Il profilo di una istanza (un testo, un seme di rete): dict(comp -> valore), e le avvertenze."""
    p = OrderedDict((k, None) for k in COMPS)
    p.update(misure_di_corse(R.get(nome, {}).get(seme), K.get(nome, {}).get(seme)))
    s, flag = misure_sintassi(S9.get(nome), S10.get(nome))
    p.update(s)
    if K.get(nome, {}).get(seme) is not None and p['k90'] is None:
        p['k90'] = K90_NON_DEFINITO                      # il contesto non guadagna niente (sotto 0,25 bit): "infinito" = massimo della griglia
        flag.append('k90_non_definito')
    return p, flag


def scale_e_raggi(rif, lingue_sint):
    """Scala di ogni misura (deviazione standard fra le lingue, almeno quella del Voynich da se' fra semi o dal bootstrap), raggio epsilon
    (il piu' lontano fra Voynich A e Voynich B dal Voynich intero, sulle 8 misure che hanno entrambi; almeno il rumore del Voynich da
    se') e tolleranza di ogni firma."""
    V, A, B, sdV = rif['V'], rif['A'], rif['B'], rif['sdV']
    disp = {k: statistics.stdev(v) for k, v in rif['lingue_gru'].items() if len(v) > 2}
    for k in COMPS_SINT:
        vs = [x[k] for x in lingue_sint if x.get(k) is not None]
        if len(vs) > 2:
            disp[k] = statistics.stdev(vs)
    scala = OrderedDict()
    for k in COMPS:
        s0 = disp.get(k)
        sv = sdV.get(k) or 0.0
        cand = [x for x in (s0, sv) if x]
        scala[k] = max(cand) if cand else None
    def dist(X, Y, comps):
        return math.sqrt(statistics.mean(((X[k] - Y[k]) / scala[k]) ** 2 for k in comps if scala[k]))
    dA, dB = dist(A, V, COMPS_AB), dist(B, V, COMPS_AB)
    d_ab = dist(A, B, COMPS_AB)
    d_seme = math.sqrt(statistics.mean((sdV[k] / scala[k]) ** 2 for k in COMPS if scala[k] and sdV.get(k)))
    eps = max(dA, dB, d_seme)
    tau = OrderedDict()
    for k in COMPS:
        t = 2 * (sdV.get(k) or 0.0)
        if k in COMPS_AB:
            t = max(t, abs(A[k] - V[k]), abs(B[k] - V[k]))
        tau[k] = t
    return scala, dict(d_A=dA, d_B=dB, d_AB=d_ab, d_seme=d_seme, epsilon=eps), tau


def distanza(p, V, scala, comps=None):
    comps = comps or COMPS
    zs = OrderedDict((k, ((p[k] - V[k]) / scala[k]) if (p.get(k) is not None and scala.get(k)) else None) for k in comps)
    vals = [z for z in zs.values() if z is not None]
    return (math.sqrt(statistics.mean(z * z for z in vals)) if vals else None), zs, len(vals)


def classe(d, eps):
    if d is None:
        return 'non misurabile'
    return 'dentro' if d <= CLASSE_DENTRO * eps else 'vicino' if d <= CLASSE_VICINO * eps else 'lontano'


def analizza(corse, versioni):
    descr = descrittori()
    rif = riferimenti()
    R, K, S9, S10, errori = raccogli(corse)
    V = rif['V']
    # ---- profili delle istanze
    istanze = OrderedDict()
    for nome, d in descr.items():
        semi = [d['istanza']] if d['tipo'] in ('cella', 'chiaro') else list(range(1, ISTANZE + 1)) if d['tipo'] == 'nativo' else [None]
        for s in semi:
            p, flag = profilo_istanza(nome, R, K, S9, S10, s)
            istanze[(nome, s)] = dict(profilo=p, flag=flag, descr=d)
    # ---- le 8 lingue (sintassi) per la scala
    lingue_sint = [istanze[(n, None)]['profilo'] for n, d in descr.items() if d['tipo'] == 'lingua' and (n, None) in istanze]
    scala, raggi, tau = scale_e_raggi(rif, lingue_sint)
    eps = raggi['epsilon']
    # ---- celle (media sulle istanze)
    celle = OrderedDict()
    for nome, d in descr.items():
        if d['tipo'] not in ('cella', 'chiaro'):
            continue
        c = celle.setdefault(d['cella'], dict(descr=dict((k, v) for k, v in d.items() if k not in ('istanza',)), istanze=[]))
        c['istanze'].append((nome, d['istanza']))
    risultati_celle = OrderedDict()
    for cella, c in celle.items():
        profili = [istanze[(n, s)]['profilo'] for n, s in c['istanze']]
        flags = [f for n, s in c['istanze'] for f in istanze[(n, s)]['flag']]
        medio, sd = OrderedDict(), OrderedDict()
        for k in COMPS:
            xs = [p[k] for p in profili]
            medio[k] = media_non_nulla(xs)
            sd[k] = sd_non_nulla(xs)
        dm, zs, nz = distanza(medio, V, scala)
        d_i = [distanza(p, V, scala)[0] for p in profili]
        classi_i = [classe(x, eps) for x in d_i]
        firme = OrderedDict((k, (abs(medio[k] - V[k]) <= tau[k]) if medio[k] is not None else None) for k in COMPS)
        firme2 = OrderedDict((k, (abs(medio[k] - V[k]) <= 2 * tau[k]) if medio[k] is not None else None) for k in COMPS)
        risultati_celle[cella] = OrderedDict(
            descr=c['descr'], istanze=len(profili), medio=medio, sd_istanze=sd, z=zs, componenti_misurate=nz, distanza=dm,
            distanza_per_istanza=d_i, sd_distanza=sd_non_nulla(d_i), classe=classe(dm, eps), classi_per_istanza=classi_i,
            stabile=len(set(classi_i)) == 1, firme_raggiunte=sum(1 for v in firme.values() if v), firme=firme,
            firme_raggiunte_larghe=sum(1 for v in firme2.values() if v), firme_larghe=firme2,
            mancate=[k for k, v in firme.items() if v is False], avvertenze=sorted(set(flags)), flag_conteggio=len(flags))
    # ---- nativi, lingue, negativo
    altri = OrderedDict()
    for nome, d in descr.items():
        if d['tipo'] in ('nativo', 'lingua', 'negativo'):
            semi = list(range(1, ISTANZE + 1)) if d['tipo'] == 'nativo' else [None]
            profili = [istanze[(nome, s)]['profilo'] for s in semi]
            medio = OrderedDict((k, media_non_nulla([p[k] for p in profili])) for k in COMPS)
            dm, zs, nz = distanza(medio, V, scala)
            altri[nome] = OrderedDict(tipo=d['tipo'], medio=medio, sd_istanze=OrderedDict((k, sd_non_nulla([p[k] for p in profili])) for k in COMPS),
                                      distanza=dm, componenti_misurate=nz, classe=classe(dm, eps),
                                      firme_raggiunte=sum(1 for k in COMPS if medio[k] is not None and abs(medio[k] - V[k]) <= tau[k]))
    # ---- il latino in chiaro nell'impaginazione del Voynich: profilo medio
    t0 = [istanze[(n, s)]['profilo'] for (n, s) in istanze if descr[n]['tipo'] == 'chiaro']
    t0m = OrderedDict((k, media_non_nulla([p[k] for p in t0])) for k in COMPS) if t0 else None
    d_t0 = distanza(t0m, V, scala)[0] if t0m else None
    # ---- controlli
    ctrl = controlli(descr, rif, istanze, R, K, S9, S10, scala, tau, raggi, t0m, d_t0, lingue_sint)
    # ---- letture
    letture = leggi(risultati_celle, ctrl, rif, scala, tau, raggi)
    out = OrderedDict(
        esperimento='ia14', versioni=versioni,
        parametri=OrderedDict(ISTANZE=ISTANZE, PROCEDIMENTI=PROCEDIMENTI_SEL, LINGUE14=LINGUE14, NATIVI=NATIVI, BOOT=BOOT, SOLO_CONTROLLI=SOLO_CONTROLLI,
                              griglia=OrderedDict((c, OrderedDict(nome=p['nome'], parametro=p['par'], valori=list(p['valori']), chiaro=p['chiaro']))
                                                  for c, p in CP.PROCEDIMENTI.items()),
                              varianti_chiaro=[list(x) for x in CP.VARIANTI_CHIARO],
                              soglie=OrderedDict(CLASSE_DENTRO=CLASSE_DENTRO, CLASSE_VICINO=CLASSE_VICINO, SEPARAZIONE_MIN=SEPARAZIONE_MIN,
                                                 ALLARGA_RANGE=ALLARGA_RANGE, SOGLIA_SINTASSI=SOGLIA_SINTASSI, RHO_NEUTRO=RHO_NEUTRO,
                                                 TOLLERANZA_RIPRODUZIONE=TOLLERANZA_RIPRODUZIONE, SOGLIA_NEGATIVO_E=SOGLIA_NEGATIVO_E,
                                                 SOGLIA_NEGATIVO_G=SOGLIA_NEGATIVO_G)),
        riferimenti=OrderedDict(Voynich=V, Voynich_A=rif['A'], Voynich_B=rif['B'], sd_voynich=rif['sdV'], scala=scala, tolleranza_firma=tau,
                                raggi=raggi, impronte=rif['impronte'],
                                lingue_gru=OrderedDict((k, dict(n=len(v), minimo=min(v), massimo=max(v), ds=statistics.stdev(v))) for k, v in rif['lingue_gru'].items())),
        celle=risultati_celle, altri=altri, errori=[dict(nome=e['nome'], lavoro=e['lavoro'], errore=e['errore']) for e in errori],
        controlli=ctrl, letture=letture)
    out = pulisci(out)
    os.makedirs(USCITA, exist_ok=True)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
        f.write('\n')
    righe = scrivi_md(out)
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(righe) + '\n')
    print('\n'.join(righe[:60]), flush=True)
    return out


def pulisci(x):
    if isinstance(x, dict):
        return OrderedDict((str(k), pulisci(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return [pulisci(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return x


def controlli(descr, rif, istanze, R, K, S9, S10, scala, tau, raggi, t0m, d_t0, lingue_sint):
    out = OrderedDict()
    # 1. riproduzione delle misure di rete sui nativi (stessi semi 1..ISTANZE)
    rip = OrderedDict()
    for nome in [n for n, d in descr.items() if d['tipo'] == 'nativo']:
        semi = list(range(1, ISTANZE + 1))
        orig = rif['originali'][nome]
        mio = [istanze[(nome, s)]['profilo'] for s in semi]
        r = OrderedDict()
        for k in COMPS_GRU:
            a = media_non_nulla([p[k] for p in mio])
            b = media_non_nulla([orig.get(s, {}).get(k) for s in semi])
            tol = TOLLERANZA_RIPRODUZIONE['k90'] if k == 'k90' else TOLLERANZA_RIPRODUZIONE['frazione_scala'] * scala[k]
            r[k] = dict(nuovo=a, originale=b, differenza=(a - b) if a is not None and b is not None else None, tolleranza=tol,
                        superato=(a is not None and b is not None and abs(a - b) <= tol))
        rip[nome] = r
    out['riproduzione_rete'] = dict(dettaglio=rip, superato=bool(rip) and all(v['superato'] for r in rip.values() for v in r.values()),
                                    eseguito=bool(rip))
    # 2. riproduzione delle misure di sintassi: ts1 (ia09), latino (ia09), g e D di ts, naibbe, latino (ia10)
    rs = OrderedDict()
    for nome, base in (('nat_ts', 'ts1'), ('nat_latino', 'latino')):
        if nome not in S9:
            continue
        o = rif['sintassi_originale'][base]
        a = S9[nome]
        rs['%s_rho' % nome] = dict(nuovo=a['rho'], originale=o['rho'], superato=abs(a['rho'] - o['rho']) <= TOLLERANZA_RIPRODUZIONE['rho'])
        rs['%s_E' % nome] = dict(nuovo=a['E'], originale=o['E'], superato=abs(a['E'] - o['E']) <= TOLLERANZA_RIPRODUZIONE['E'])
        ln, lo = a['Lambda'], o['lambda']
        rs['%s_Lambda' % nome] = dict(nuovo=ln, originale=lo, superato=(ln is None and lo is None) or
                                      (ln is not None and lo is not None and abs(ln - lo) <= TOLLERANZA_RIPRODUZIONE['lambda_']))
    for nome in ('nat_ts', 'nat_naibbe', 'nat_latino'):
        if nome in S10:
            a, o, od = S10[nome], rif['sintassi_originale']['g'][nome], rif['sintassi_originale']['D'][nome]
            rs['%s_g' % nome] = dict(nuovo=a['g'], originale=o, superato=abs(a['g'] - o) <= TOLLERANZA_RIPRODUZIONE['g'])
            rs['%s_D' % nome] = dict(nuovo=a['D'], originale=od, superato=abs(a['D'] - od) <= TOLLERANZA_RIPRODUZIONE['D'])
    out['riproduzione_sintassi'] = dict(dettaglio=rs, superato=bool(rs) and all(v['superato'] for v in rs.values()), eseguito=bool(rs))
    # 3. il latino in chiaro nell'impaginazione del Voynich cade fra le lingue (tutte e nove le misure)
    dentro = OrderedDict()
    if t0m:
        for k in COMPS:
            vs = rif['lingue_gru'][k] if k in COMPS_GRU else [x[k] for x in lingue_sint if x.get(k) is not None]
            if len(vs) < 3 or t0m[k] is None:
                dentro[k] = dict(superato=None)
                continue
            lo, hi = min(vs), max(vs)
            marg = ALLARGA_RANGE * (hi - lo)
            dentro[k] = dict(valore=t0m[k], minimo=lo, massimo=hi, superato=(lo - marg <= t0m[k] <= hi + marg))
    out['latino_in_chiaro_tra_le_lingue'] = dict(dettaglio=dentro, eseguito=bool(dentro),
                                                 superato=bool(dentro) and all(v['superato'] for v in dentro.values() if v['superato'] is not None) and
                                                 any(v['superato'] is not None for v in dentro.values()))
    # 4. il profilo separa il Voynich dal latino in chiaro
    out['separazione'] = dict(distanza_latino_in_chiaro=d_t0, epsilon=raggi['epsilon'], rapporto=(d_t0 / raggi['epsilon']) if d_t0 and raggi['epsilon'] else None,
                              soglia=SEPARAZIONE_MIN, eseguito=d_t0 is not None,
                              superato=bool(d_t0 is not None and d_t0 >= SEPARAZIONE_MIN * raggi['epsilon']))
    # 5. negativo: latino con le parole mescolate fra tutte le pagine, nessuna sintassi
    neg = S9.get('Tneg_i1'), S10.get('Tneg_i1')
    if neg[0] and neg[1]:
        out['negativo_rimescolato'] = dict(E=neg[0]['E'], A_gram=neg[0]['A_gram'], A_cn=neg[0]['A_cn'], g=neg[1]['g'], eseguito=True,
                                           superato=(neg[0]['E'] < SOGLIA_NEGATIVO_E and max(neg[0]['A_gram'], neg[0]['A_cn']) < SOGLIA_SINTASSI and
                                                     neg[1]['g'] <= SOGLIA_NEGATIVO_G))
    else:
        out['negativo_rimescolato'] = dict(eseguito=False, superato=False)
    # 6. il codice dei procedimenti
    out['codice'] = prova_codice()
    return out


def prova_codice():
    """Reversibilita' dei cifrari veri (verboso, sostituzione, polialfabetico) e assenza di caricatori del Voynich nel modulo."""
    res = OrderedDict()
    pc = CP.parole_chiaro('latino')
    lettere, _ = CP.lettere_da(pc, 1000, 20000)
    ok = True
    for T in (1, 3, 6):
        parole, usate, tav = CP.genera_verboso(random.Random(T), 2000, T, lettere)
        ok = ok and CP.decifra_verboso(parole, tav) == lettere[:usate]
    res['verboso_reversibile'] = ok
    parole, tab, flusso = CP.genera_sostituzione(random.Random(2), 1500, 5.0, lettere)
    dec = CP.decifra_sostituzione(flusso, tab)
    res['sostituzione_reversibile'] = bool(dec == lettere[:len(dec)] and len(dec) > 500)
    parole, info, flusso = CP.genera_polialfabetico(random.Random(3), 1500, 5, lettere)
    res['polialfabetico_reversibile'] = CP.decifra_polialfabetico(flusso, info) == lettere[:len(flusso)]
    src = open(CP.__file__.replace('.pyc', '.py'), encoding='utf-8').read()
    res['modulo_senza_caricatori_del_voynich'] = not any(('import ' + m) in src for m in ('trascrizione', 'misure', 'pezzi', 'e134', 'e337'))
    res['superato'] = all(v for v in res.values())
    return res


def leggi(celle, ctrl, rif, scala, tau, raggi):
    """Le letture preregistrate (L1-L5). Una lettura e' 'non leggibile' se un controllo da cui dipende non e' superato."""
    valide = OrderedDict(
        riproduzione=bool(ctrl['riproduzione_rete']['superato'] and ctrl['riproduzione_sintassi']['superato']),
        lingue=bool(ctrl['latino_in_chiaro_tra_le_lingue']['superato']),
        separazione=bool(ctrl['separazione']['superato']),
        negativo=bool(ctrl['negativo_rimescolato']['superato']),
        codice=bool(ctrl['codice']['superato']))
    leggibile = all(valide.values())
    L = OrderedDict(valide=valide, leggibile=leggibile)
    L['L1_distanza'] = OrderedDict((c, OrderedDict(distanza=v['distanza'], classe=v['classe'], stabile=v['stabile'])) for c, v in celle.items()
                                   if v['descr']['tipo'] == 'cella')
    L['L2_firme'] = OrderedDict((c, OrderedDict(raggiunte=v['firme_raggiunte'], larghe=v['firme_raggiunte_larghe'], mancate=v['mancate'],
                                                insieme='si' if v['firme_raggiunte'] == len(COMPS) else 'quasi' if v['firme_raggiunte'] >= len(COMPS) - 2 else 'no'))
                                for c, v in celle.items() if v['descr']['tipo'] == 'cella')
    per_proc = OrderedDict()
    for cod, p in CP.PROCEDIMENTI.items():
        cs = [(c, v) for c, v in celle.items() if v['descr']['tipo'] == 'cella' and v['descr']['cod'] == cod and not v['descr'].get('chiaro')]
        if not cs:
            continue
        mig = min(cs, key=lambda x: x[1]['distanza'] if x[1]['distanza'] is not None else 1e9)
        per_proc[cod] = OrderedDict(
            nome=p['nome'], distanza_minima=mig[1]['distanza'], cella_piu_vicina=mig[0], distanza_massima=max((v['distanza'] for _, v in cs if v['distanza'] is not None), default=None),
            classi=[v['classe'] for _, v in cs], firme_massime=max(v['firme_raggiunte'] for _, v in cs),
            qualche_cella_dentro=any(v['classe'] == 'dentro' for _, v in cs), qualche_cella_9_su_9=any(v['firme_raggiunte'] == len(COMPS) for _, v in cs))
    L['L3_per_procedimento'] = per_proc
    per_firma = OrderedDict()
    for k in COMPS:
        raggiungono = sorted({v['descr']['cod'] for c, v in celle.items() if v['descr']['tipo'] == 'cella' and v['firme'].get(k)})
        per_firma[k] = OrderedDict(procedimenti_che_la_raggiungono=raggiungono, celle_che_la_raggiungono=sum(1 for v in celle.values() if v['firme'].get(k)),
                                   celle_totali=sum(1 for v in celle.values() if v['descr']['tipo'] == 'cella'))
    L['L4_per_firma'] = per_firma
    sens = OrderedDict()
    base = celle.get('V_3')
    for ch in ('italiano', 'tedesco'):
        x = celle.get('V_3_' + ch)
        if base and x:
            sens[ch] = OrderedDict(
                distanza=x['distanza'], distanza_latino=base['distanza'],
                differenza_per_misura=OrderedDict((k, (x['medio'][k] - base['medio'][k]) if x['medio'][k] is not None and base['medio'][k] is not None else None) for k in COMPS),
                piu_di_2_sd=[k for k in COMPS if x['medio'][k] is not None and base['medio'][k] is not None and
                             abs(x['medio'][k] - base['medio'][k]) > 2 * max(x['sd_istanze'][k], base['sd_istanze'][k], 1e-12)])
    L['L5_testo_in_chiaro'] = sens
    return L


def f3(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%.3f' % x


def f2(x):
    return '-' if x is None or (isinstance(x, float) and math.isnan(x)) else '%.2f' % x


def scrivi_md(o):
    R = o['riferimenti']
    L = []
    L.append('# ia14 - quale procedimento produce le firme del Voynich')
    L.append('')
    L.append('Non e\' una decifrazione: si confrontano procedimenti. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia14.md`.')
    L.append('')
    L.append('## Controlli')
    L.append('')
    c = o['controlli']
    for k in ('riproduzione_rete', 'riproduzione_sintassi', 'latino_in_chiaro_tra_le_lingue', 'separazione', 'negativo_rimescolato'):
        L.append('- %s: eseguito %s, superato %s' % (k, c[k].get('eseguito'), c[k].get('superato')))
    L.append('- codice dei procedimenti: %s' % ', '.join('%s %s' % (k, v) for k, v in c['codice'].items()))
    L.append('- letture leggibili: %s (%s)' % (o['letture']['leggibile'], ', '.join('%s %s' % (k, v) for k, v in o['letture']['valide'].items())))
    L.append('')
    L.append('## Riferimenti (letti da risultati/ia02, ia03, ia09, ia10)')
    L.append('')
    L.append('| misura | Voynich | A | B | sd Voynich | scala | tolleranza |')
    L.append('|---|---|---|---|---|---|---|')
    for k in COMPS:
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (NOMI_COMPS[k], f3(R['Voynich'].get(k)), f3(R['Voynich_A'].get(k)), f3(R['Voynich_B'].get(k)),
                                                       f3(R['sd_voynich'].get(k)), f3(R['scala'].get(k)), f3(R['tolleranza_firma'].get(k))))
    r = R['raggi']
    L.append('')
    L.append('Raggio epsilon %s (A dal Voynich %s, B %s, A contro B %s, rumore del Voynich da se\' %s).' % (f2(r['epsilon']), f2(r['d_A']), f2(r['d_B']), f2(r['d_AB']), f2(r['d_seme'])))
    L.append('')
    L.append('## Celle: distanza dal Voynich (in unita\' di scala) e firme raggiunte')
    L.append('')
    L.append('| cella | procedimento | d | classe | stabile | firme | larghe | mancate |')
    L.append('|---|---|---|---|---|---|---|---|')
    for nome, v in o['celle'].items():
        L.append('| %s | %s | %s | %s | %s | %d/9 | %d/9 | %s |' % (nome, CP.PROCEDIMENTI[v['descr']['cod']]['nome'] if v['descr'].get('cod') else 'latino in chiaro',
                                                                  f2(v['distanza']), v['classe'], v['stabile'], v['firme_raggiunte'], v['firme_raggiunte_larghe'],
                                                                  ','.join(v['mancate']) or '-'))
    L.append('')
    L.append('## Profilo medio delle celle (media sulle istanze; sd fra istanze fra parentesi)')
    L.append('')
    L.append('| cella | ' + ' | '.join(COMPS) + ' |')
    L.append('|---|' + '---|' * len(COMPS))
    for nome, v in o['celle'].items():
        L.append('| %s | ' % nome + ' | '.join('%s (%s)' % (f3(v['medio'][k]), f3(v['sd_istanze'][k])) for k in COMPS) + ' |')
    L.append('')
    L.append('## Nativi, lingue e negativo')
    L.append('')
    L.append('| testo | ' + ' | '.join(COMPS) + ' | d | classe |')
    L.append('|---|' + '---|' * (len(COMPS) + 2))
    for nome, v in o['altri'].items():
        L.append('| %s | ' % nome + ' | '.join(f3(v['medio'][k]) for k in COMPS) + ' | %s | %s |' % (f2(v['distanza']), v['classe']))
    L.append('')
    L.append('## Letture')
    L.append('')
    for cod, v in o['letture']['L3_per_procedimento'].items():
        L.append('- %s (%s): distanza minima %s (%s), massima %s, classi %s, firme al massimo %d/9' % (
            cod, v['nome'], f2(v['distanza_minima']), v['cella_piu_vicina'], f2(v['distanza_massima']), '/'.join(v['classi']), v['firme_massime']))
    L.append('')
    for k, v in o['letture']['L4_per_firma'].items():
        L.append('- firma %s: raggiunta da %d celle su %d (%s)' % (k, v['celle_che_la_raggiungono'], v['celle_totali'], ','.join(v['procedimenti_che_la_raggiungono']) or 'nessun procedimento'))
    if o['errori']:
        L.append('')
        L.append('ERRORI: %d lavori falliti: %s' % (len(o['errori']), ', '.join('%s %s' % (e['lavoro'], e['nome']) for e in o['errori'])))
    return L


# ---------------------------------------------------------------- main

def main():
    import torch
    import sklearn
    import scipy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=np.__version__, sklearn=sklearn.__version__, scipy=scipy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    fasi = os.environ.get('FASI', 'corse,analisi').split(',')
    descr = descrittori()
    prova = [k for k in ('PASSI', 'OGNI', 'PAZIENZA', 'SEMI', 'NASCOSTO', 'CADUTA', 'PAGINE', 'RIGHE_PAGINA', 'FILTRO', 'SOLO_CONTROLLI', 'USCITA', 'BOOT',
                         'ISTANZE', 'PROCEDIMENTI', 'LINGUE14', 'NATIVI', 'USCITA_CACHE14') if k in os.environ]
    print("variabili d'ambiente attive: %s" % (', '.join(prova) if prova else 'nessuna'), flush=True)
    print('testi: %d (%s)' % (len(descr), ', '.join('%s %d' % (t, sum(1 for d in descr.values() if d['tipo'] == t)) for t in sorted({d['tipo'] for d in descr.values()}))), flush=True)
    cod = prova_codice()
    print('prova del codice dei procedimenti: %s' % dict(cod), flush=True)
    if not cod['superato']:
        raise SystemExit('FERMO: il codice dei procedimenti non supera la sua prova')
    percorso = os.path.join(USCITA, 'ia14_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    elif 'corse' in fasi:
        open(percorso, 'w').close()
    if 'corse' in fasi:
        fatte = {json.dumps(x['chiave']) for x in corse}
        nativi_lav = lavori_nativi_gru(descr) if NATIVI else {}
        tutti = elenco_lavori(descr, nativi_lav)
        da_fare = [j for j in tutti if json.dumps(chiave_di(j)) not in fatte]
        print('lavori: %d da fare, %d gia fatti' % (len(da_fare), len(tutti) - len(da_fare)), flush=True)
        inizio = time.time()
        processi = int(os.environ.get('PROCESSI', 10))
        with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
            for i, r in enumerate(pool.imap_unordered(lavoro, da_fare), 1):
                corse.append(r)
                with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print('[%d/%d %.0f min] %s (%.0f s)%s' % (i, len(da_fare), (time.time() - inizio) / 60, r['chiave'], r['tempo'],
                                                         (' ERRORE ' + r['errore']) if r['tipo'] == 'errore' else ''), flush=True)
    elif os.path.exists(percorso):
        corse = [x for x in carica_corse(percorso) if x.get('tipo') != 'errore']
    if 'analisi' in fasi:
        analizza(corse, versioni)


if __name__ == '__main__':
    main()
