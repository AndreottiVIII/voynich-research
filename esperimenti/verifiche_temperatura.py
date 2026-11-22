# -*- coding: utf-8 -*-
"""IA25, parte 3 (modulo di supporto): scrivere gli imitatori "a temperatura giusta" (proposta C8 della revisione).

Domanda: lo scarto di forma delle parole nuove (vero 3,48 bit per glifo contro 3,7-3,8 degli imitatori, ia24) e' solo l'effetto del fatto che
tutti gli imitatori scrivono a temperatura 1 (pescano ogni segno con la probabilita' che il modello gli da')?

Che cosa c'e' qui
- `scrivi_libro_T`: la scrittura di ia20 (M1) e di ia22 (E2) con UN'unica differenza: i logit della GRU sono divisi per la temperatura T prima di pescare
  il segno (anche la scelta spazio / fine riga dopo una parola copiata). La scelta fra "parola libera" e "copia e ritocco" del puntatore di E2 (una
  decisione fra parole, non fra segni) NON cambia. Stessi modelli di ia20 e ia22 (letti dalla cache, mai riaddestrati), stesse pagine, stessi semi di ia20
  e ia22 per ogni libro: a T = 1,00 si riscrive esattamente il libro originale (controllo di identita'), a T diverso lo stesso flusso di numeri casuali
  e' usato con un'altra temperatura (i libri di temperature diverse sono "accoppiati").
- il controllo del processo noto: un M1 addestrato (5 pieghe, 1 replica) su un libro v21 messo nella disposizione del libro vero, scritto alle stesse
  temperature, e la forma misurata contro il libro v21 stesso;
- le misure di struttura e i giudici su qualunque libro (stesse funzioni di ia20), `forma_fold` (costo di forma delle parole nuove), l'analisi e le letture.
Solo numeri e aggregati.
"""
import itertools
import os
import pickle
import statistics
import time
from collections import Counter, OrderedDict

import numpy as np

import verifiche_comune as C

I7, I16, I20, I22, MS = C.I7, C.I16, C.I20, C.I22, C.MS
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import aprire_parole as AP  # noqa: E402

TIPI3 = ('M1', 'E2')
N_LIBRI25 = int(os.environ.get('N_LIBRI25', 10))
N_CTRL25 = int(os.environ.get('N_CTRL25', 3))                 # libri del controllo (processo noto) per temperatura
EPOCHE25 = int(os.environ.get('EPOCHE25', 150))
PAZIENZA25 = int(os.environ.get('PAZIENZA25', 10))
CHIAVE_C3 = 13                                                # libro v21 (senza messaggio) del controllo: fissato prima
TKEYS = [k for i, k in enumerate(C.TEMPERATURE) if str(i) in os.environ.get('TEMPI25', '0123')]
SOGLIE = OrderedDict([
    ('nuove_fascia', I20.NUOVE_FASCIA),             # quota di parole nuove fra 0,6 e 1,4 volte quella del vero (guardia di ia20)
    ('chiuso_quasi_tutto', 0.80),                   # frazione dello scarto di forma chiusa dalla temperatura migliore: "quasi tutto"
    ('chiuso_in_parte', 0.30),                      # sotto: "poco o niente"
    ('controllo_scarto_min', 0.10),                 # processo noto: scarto di forma a T=1 almeno questo (bit per glifo)
    ('controllo_chiude_min', 0.50),                 # e la temperatura migliore ne chiude almeno questa frazione
    ('scarto_voynich_min', 0.10)])                  # scarto di forma del Voynich a T=1 almeno questo perche' la domanda abbia senso (bit per glifo)
CTRL_IDENTITA_LIBRI = lambda n: (1, n // 2 + 1)    # noqa: E731  un libro per replica


def seme_libro(tipo, i):
    if tipo == 'M1':
        return 2000000 + 10000 * 1 + i                        # ia20: 2000000 + 10000 * passo + i
    if tipo == 'c3':
        return 2500000 + i
    return 2200000 + 10000 * I22.IDX[tipo] + i                # ia22: 2200000 + 10000 * indice del tipo + i


# ---------------------------------------------------------------- scrittura con temperatura

def scrivi_pagina_T(ctx, pen, regole, rp, voc, D, rng, conta, T, nt):
    """Come ia20.scrivi_pagina (M1, nt = 0) e ia22.scrivi_pagina22 (E2, nt = 4): ogni scelta di un segno usa exp((logit - massimo) / T)."""
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    pen.apri()
    lg = None
    for t in I7.testa_pagina(rp, voc):
        lg = pen.dai(t)
    if nt:
        psub, pins = pen.tabelle_ritocco()
    out = []
    for j, x in enumerate(rp):
        for t in I7.testa_riga(x, j, voc, D):
            lg = pen.dai(t)
        parole, lung, prima, fine = [], 0, 'inizio', False
        while not fine:
            w2 = None
            if nt:
                cand = pen.candidati()
                if cand:
                    pf, ppi = pen.puntatore(cand)
                    pr = np.concatenate([[pf], ppi[:len(cand)].reshape(-1)])
                    pr = pr / pr.sum()
                    for _ in range(8):
                        idx = int(rng.choice(len(pr), p=pr))
                        if idx == 0:
                            break
                        k, tipo_r = divmod(idx - 1, nt)
                        w2 = GM.campiona_ritocco(cand[k][0], tipo_r, psub, pins, rng)
                        if w2 is not None and len(w2):
                            stringhe = [unita[u] for u in w2]
                            if D(''.join(stringhe)) == stringhe:
                                conta[('uguale', 'cambia', 'aggiunge', 'toglie')[tipo_r]] += 1
                                break
                        w2 = None
                    conta['libero' if w2 is None else 'copia'] += 1
            if w2 is not None:
                for u in w2:
                    lg = pen.dai(u0 + u)
                lung += len(w2)
                ammessi = [SP, EOL] if lung < voc['lmax'] else [EOL]
                z = np.array([lg[a] for a in ammessi])
                z = np.exp((z - z.max()) / T)
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
                z = np.exp((z - z.max()) / T)
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


def modello_di(tipo, k, replica):
    """(modello, ctx, penna) del tipo e della piega: M1 e E2 dalla cache di ia20 e ia22; 'c3' dal controllo."""
    cap = _capacita()
    if tipo == 'M1':
        m, ctx = I20.carica(1, k, replica)
        return m, ctx, GM.Penna20(m, ctx, cap + 8)
    if tipo == 'c3':
        m, ctx = GM.carica_modello(percorso_modello_c3(k) + '.pt', I7.vocabolario())
        return m, ctx, GM.Penna20(m, ctx, cap + 8)
    m, ctx = I22.carica(tipo, k, replica)
    return m, ctx, EM.Penna22(m, ctx, cap + 8)


def _capacita():
    voc = I7.vocabolario()
    pp = I7.per_pagina(I7.libro_vero())
    return max(4 + sum(3 + voc['lmax'] + 2 for _ in rp) for rp in pp.values())


def scrivi_libro_T(tipo, replica, seme, T):
    righe, voc, D = I7.libro_vero(), I7.vocabolario(), I7.divisore()
    rng = np.random.default_rng(seme)
    pp = I7.per_pagina(righe)
    pg = I7.pieghe()
    regole = I20.RegoleScrittura(voc)
    nt = 0 if tipo in ('M1', 'c3') else EM.NT_PUNT[tipo]
    penne = {}
    conta = Counter()
    out = []
    for pag, rp in pp.items():
        k = pg[I7.foglio_di(pag)]
        if k not in penne:
            penne[k] = modello_di(tipo, k, replica)
        m, ctx, pen = penne[k]
        out += scrivi_pagina_T(ctx, pen, regole, rp, voc, D, rng, conta, T, nt)
    return out, conta


# ---------------------------------------------------------------- libri e loro misure

def lavoro_libro(tipo, tkey, i):
    """Scrive (se manca) il libro `tipo` a temperatura `tkey` e lo giudica con e231 ed e266 (i libri a T=1,00 sono gli originali di ia20 e ia22)."""
    inizio = time.time()
    C.crea_cartelle()
    nome = '%s@%s:%d' % (tipo, tkey, i)
    replica = I7.replica_del_libro(i, N_LIBRI25)
    conta = None
    if tkey == '100' and tipo in TIPI3:
        t = C.t_libro(nome)
    else:
        percorso = C.percorso_libro_T(tipo, tkey, i)
        if os.path.exists(percorso):
            t = I7.leggi_file(percorso)
        else:
            t, conta = scrivi_libro_T(tipo, replica, seme_libro(tipo, i), C.TEMPERATURE[tkey])
            I7.scrivi_file(t, percorso + '.tmp', 'ia25, libro %s T=%s %d' % (tipo, tkey, i), replica)
            os.replace(percorso + '.tmp', percorso)
            assert I7.leggi_file(percorso) == [(p, ini, ps) for p, ini, ps in t], 'il file non ridà il libro'
    ris = OrderedDict([('lavoro', 'libro3|%s|%s|%d' % (tipo, tkey, i)), ('tipo', tipo), ('tkey', tkey), ('i', i), ('replica', replica), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)),
                       ('segni_per_parola', statistics.mean(len(I7.divisore()(w)) for _, _, ps in t for w in ps))])
    if conta is not None:
        ris['modi_scrittura'] = OrderedDict(conta)
    if tipo in TIPI3:
        ris.update(I7.giudica(t))
        ris['copia'] = I7.copia_onesta(t)
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_identita(tipo, i):
    """Controllo: il libro `i` riscritto a T = 1,00 e' uguale, parola per parola, a quello di ia20 / ia22."""
    inizio = time.time()
    replica = I7.replica_del_libro(i, N_LIBRI25)
    t, _ = scrivi_libro_T(tipo, replica, seme_libro(tipo, i), 1.0)
    orig = C.t_libro('%s:%d' % (tipo, i))
    nuovo = [(p, bool(ini), ps) for p, ini, ps in t]
    vecchio = [(p, bool(ini), ps) for p, ini, ps in orig]
    diverse = sum(1 for a, b in itertools.zip_longest(nuovo, vecchio) if a != b)
    return OrderedDict([('lavoro', 'ident3|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('righe', len(nuovo)), ('righe_diverse', diverse), ('uguale', diverse == 0),
                        ('secondi', round(time.time() - inizio, 1))])


def nomi_libri3():
    n = ['%s@%s:%d' % (t, tk, i) for t in TIPI3 for tk in TKEYS for i in range(1, N_LIBRI25 + 1)]
    return n


def nomi_controllo():
    return ['c3@%s:%d' % (tk, i) for tk in TKEYS for i in range(1, N_CTRL25 + 1)]


def rows_di(nome):
    if nome.startswith('c3@'):
        return I7.libro_A_da_righe(I7.leggi_file(C.percorso_libro_T('c3', nome.split('@')[1].split(':')[0], int(nome.split(':')[1]))))
    return C.rows_libro(nome)


def lavoro_M(nome):
    """Copia netta, Λ, rho, contatto (ia09, ia08), G9 del giudice 2 e bordi (ia17) di un libro o di `vere` (come ia20.lavoro_M, ma con i nomi di IA25)."""
    import e266_discriminatore_forte as e266
    inizio = time.time()
    c = I7.contesto_A()
    k = I7.riferimenti()
    if nome == 'vere':
        rows = c['vere']
        g9 = I16.media_G9(k['vt266'])
    else:
        rows = rows_di(nome)
        g9 = I16.media_G9(e266.tabella(I7.righe_ini(C.t_libro(nome)), k['rif266']))
    r = C.struttura_M(nome, rows, '0')
    s = C.stime_M(r)
    pag = OrderedDict((p, rows[p]) for p in c['ids'] if p in rows)
    cp = {p: AP.conti_bordi({p: rr}) for p, rr in pag.items()}
    b = AP.firma_da_conti(I20.somma_conti(list(cp.values())))
    ris = OrderedDict([('lavoro', 'M3|%s' % nome), ('nome', nome), ('copia_netta', s['netto'].p), ('lam', s['lam'].p), ('rho', s['rho'].p), ('contatto', s['contatto']),
                       ('G9', g9), ('bordi_inizio', statistics.mean(b['inizio_%s' % f] for f in ('primo', 'ultimo', 'lung'))),
                       ('bordi_fine', statistics.mean(b['fine_%s' % f] for f in ('primo', 'ultimo', 'lung')))])
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def forma_fold(f, vere_rows, testi, c=None):
    """Per la piega f: costo di forma delle parole nuove [bit, glifi, parole nuove, parole] di ogni testo (nome -> pagine), con forma e parole note delle pagine
    di `vere_rows` delle altre pieghe (come ia20.lavoro_D)."""
    c = c or I7.contesto_A()
    pv = OrderedDict((p, vere_rows[p]) for p in c['ids'] if c['fold'][p] != f and p in vere_rows)
    cnt = Counter(w for rows in pv.values() for _, ws in rows for w in ws)
    forma, noti = R.Forma(cnt), set(cnt)
    out = OrderedDict()
    for nome, rows in testi.items():
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        out[nome] = R.costo_nuove(forma, pg, noti) if pg else [0.0, 0.0, 0, 0]
    return out


def lavoro_D(f, nomi):
    """D di ia10 per piega e forma delle parole nuove, per `vere` e per i libri `nomi`."""
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('vere', c['vere'])])
    for n in nomi:
        testi[n] = rows_di(n)
    out, info = MS.lavoro_D(f, c, testi)
    fm = forma_fold(f, c['vere'], testi, c)
    return OrderedDict([('lavoro', 'D3|%d' % f), ('piega', f), ('famiglie', info), ('D', out), ('forma', fm), ('secondi', round(time.time() - inizio, 1))])


def lavoro_K(f, nomi):
    inizio = time.time()
    c = I7.contesto_A()
    libri = OrderedDict()
    for n in nomi:
        libri[n] = rows_di(n)
    info, prof = MS.lavoro_K(f, c, libri)
    os.makedirs(C.MISURE25, exist_ok=True)
    with open(os.path.join(C.MISURE25, 'K3_f%d.pkl' % f), 'wb') as fh:
        pickle.dump(prof, fh)
    return OrderedDict([('lavoro', 'K3|%d' % f), ('scelte_K', info), ('libri', len(libri)), ('pagine_prova', len(prof['vere'])), ('secondi', round(time.time() - inizio, 1))])


def nomi_riferimento_K():
    """Libri per i controlli di K (v21 e controlli di ia20): come ia20.nomi_libri."""
    return ['V21:%d' % k for k in I20.CHIAVI_V21] + ['ctrl:' + n for n in I7.NOMI_CTRL_A if n != 'righe'] + ['ctrl:righe']


# ---------------------------------------------------------------- il controllo del processo noto (un libro v21 nella disposizione del vero)

def percorso_modello_c3(k):
    return os.path.join(C.MODELLI25, 'ia25_c3_%s_0' % k)


def righe_controllo():
    """Righe del libro vero (stessa disposizione: righe, lunghezze, sezioni, paragrafi) con le parole di un libro v21 (chiave CHIAVE_C3) versate in ordine.
    Le parole con glifi che non sono nell'inventario del libro vero si sostituiscono con la parola precedente (se ne conta il numero)."""
    if 'rc' in C._C:
        return C._C['rc']
    D, unita = I7.divisore(), set(I7.vocabolario()['unita'])
    v = I7.libro_riferimento_A('b', CHIAVE_C3)
    flusso = [''.join(w) for p in v for _, ws in v[p] for w in ws]
    it = itertools.cycle(flusso)
    out, sost, ultimo = [], 0, None
    for x in I7.libro_vero():
        y = dict(x)
        ps = []
        for _ in x['parole']:
            w = next(it)
            u = D(w)
            if not u or any(s not in unita for s in u) or D(''.join(u)) != u:
                w, sost = (ultimo or flusso[0]), sost + 1
            ps.append(w)
            ultimo = w
        y['parole'] = ps
        out.append(y)
    C._C['rc'] = (out, sost)
    return C._C['rc']


def rows_controllo():
    righe, _ = righe_controllo()
    return I7.libro_A_da_righe(I7.come_rr(righe))


def lavoro_addestra_c3(piega):
    inizio = time.time()
    C.crea_cartelle()
    voc = I7.vocabolario()
    righe, sost = righe_controllo()
    dp = I20.pagine_sintetiche(righe)
    ctx, add, val, fuori = I20.pagine_fold(piega, 1, dp, tag='c3')
    cfg = GM.cfg_completa(1, voc, ctx, I20.PICCOLO)

    def messaggio(s):
        try:
            print('[c3 p%s]%s' % (piega, s), flush=True)
        except OSError:
            pass
    m, cv, ca, scelta = GM.addestra_modello(cfg, ctx, add, val, 25000 + piega, EPOCHE25, PAZIENZA25, messaggi=messaggio)
    GM.salva_modello(m, percorso_modello_c3(piega) + '.pt', voc['segni'], ctx, dict(piega=piega, epoca_scelta=scelta, solo_prova=bool(C.SOLO_CONTROLLI)))
    return OrderedDict([('lavoro', 'addestra_c3|%s' % piega), ('piega', piega), ('epoche', len(ca)), ('epoca_scelta', scelta), ('parole_sostituite', sost),
                        ('bpc_validazione', round(GM.bpc_pagine(m, ctx, val), 5)), ('bpc_fuori', round(GM.bpc_pagine(m, ctx, fuori), 5)),
                        ('secondi', round(time.time() - inizio, 1))])


def lavoro_libro_c3(tkey, i):
    inizio = time.time()
    C.crea_cartelle()
    percorso = C.percorso_libro_T('c3', tkey, i)
    if not os.path.exists(percorso):
        t, _ = scrivi_libro_T('c3', 0, seme_libro('c3', i), C.TEMPERATURE[tkey])
        I7.scrivi_file(t, percorso + '.tmp', 'ia25, libro del controllo T=%s %d' % (tkey, i), 0)
        os.replace(percorso + '.tmp', percorso)
    return OrderedDict([('lavoro', 'libro_c3|%s|%d' % (tkey, i)), ('tkey', tkey), ('i', i), ('secondi', round(time.time() - inizio, 1))])


def lavoro_forma_c3(f):
    inizio = time.time()
    c = I7.contesto_A()
    testi = OrderedDict([('c3:testo', rows_controllo())])
    for n in nomi_controllo():
        testi[n] = rows_di(n)
    fm = forma_fold(f, testi['c3:testo'], testi, c)
    return OrderedDict([('lavoro', 'forma_c3|%d' % f), ('piega', f), ('forma', fm), ('secondi', round(time.time() - inizio, 1))])


# ---------------------------------------------------------------- analisi

def _forma_da_pieghe(fm_liste, nome):
    xs = [d[nome] for d in fm_liste if nome in d]
    if not xs or sum(y[1] for y in xs) == 0:
        return None, None
    return sum(y[0] for y in xs) / sum(y[1] for y in xs), sum(y[2] for y in xs) / max(sum(y[3] for y in xs), 1)


def analisi(corse):
    """corse: lavoro -> risultato. Una riga per (tipo, temperatura) con le nove misure e i tre giudici, controlli e letture preregistrate."""
    Cc = {k: v for k, v in corse.items() if not v.get('errore')}
    n_pag = len(I7.contesto_A()['ids'])
    out = OrderedDict(soglie=SOGLIE, temperature=C.TEMPERATURE)
    # ---- controlli dei giudici e identita'
    ctr = OrderedDict()
    pos = [Cc['O|O2|%d' % s]['AUC_e266'] for s in I7.SEMI_O if 'O|O2|%d' % s in Cc]
    caso = Cc.get('caso|0')
    ctr['paper_positivo'] = OrderedDict(AUC=C.mes(pos)[0], soglia=I20.POS_PAPER, riuscito=bool(pos) and statistics.mean(pos) >= I20.POS_PAPER)
    ctr['paper_negativo'] = OrderedDict(AUC_e231=caso and caso['AUC_e231'], AUC_e266=caso and caso['AUC_e266'], banda=I20.NEG_BANDA,
                                        riuscito=bool(caso) and all(I20.NEG_BANDA[0] <= caso[k] <= I20.NEG_BANDA[1] for k in ('AUC_e231', 'AUC_e266')))
    identita = [v for k, v in Cc.items() if k.startswith('ident3|')]
    ctr['identita_a_T1'] = OrderedDict(libri=len(identita), uguali=sum(1 for v in identita if v['uguale']), riuscito=bool(identita) and all(v['uguale'] for v in identita))
    profs = []
    for f in range(I7.PIEGHE):
        p = os.path.join(C.MISURE25, 'K3_f%d.pkl' % f)
        if os.path.exists(p):
            profs.append(pickle.load(open(p, 'rb')))
    prof = MS.unisci_profili(profs) if len(profs) == I7.PIEGHE else None
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
        ctr['K_negativo'] = OrderedDict(AUC=statistics.mean(neg), banda=I20.NEG_BANDA, riuscito=I20.NEG_BANDA[0] <= statistics.mean(neg) <= I20.NEG_BANDA[1])
        ctr['K_vede_v21'] = OrderedDict(AUC=C.mes(v21K)[0], soglia=I20.K_VEDE_V21, riuscito=bool(v21K) and statistics.mean(v21K) >= I20.K_VEDE_V21)
    ok_giudici = bool(ctr['paper_positivo']['riuscito'] and ctr['paper_negativo']['riuscito'] and prof and ctr['K_positivo']['riuscito'] and ctr['K_negativo']['riuscito']
                      and ctr['K_vede_v21']['riuscito'])
    # ---- misure per libro
    Mj = {v['nome']: v for k, v in Cc.items() if k.startswith('M3|')}
    Dj = [Cc['D3|%d' % f] for f in range(I7.PIEGHE) if 'D3|%d' % f in Cc]
    vero = OrderedDict()
    if 'vere' in Mj and len(Dj) == I7.PIEGHE:
        mv = Mj['vere']
        vero = OrderedDict((k, mv[k]) for k in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine'))
        vero['D'] = MS.D_da_pieghe([d['D']['vere'] for d in Dj])
        vero['costo_forma'], vero['parole_nuove'] = _forma_da_pieghe([d['forma'] for d in Dj], 'vere')
    celle = OrderedDict()
    per_replica = {}
    for tipo in TIPI3:
        for tk in TKEYS:
            nomi = ['%s@%s:%d' % (tipo, tk, i) for i in range(1, N_LIBRI25 + 1)]
            xs = []
            for n in nomi:
                if n not in Mj:
                    continue
                x = OrderedDict((k, Mj[n][k]) for k in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine'))
                x['D'] = MS.D_da_pieghe([d['D'][n] for d in Dj]) if Dj and all(n in d['D'] for d in Dj) else None
                x['costo_forma'], x['parole_nuove'] = _forma_da_pieghe([d['forma'] for d in Dj], n) if Dj else (None, None)
                x['_forma'] = x['costo_forma']
                lb = Cc.get('libro3|%s|%s|%s' % (tipo, tk, n.split(':')[1]))
                x['e231'], x['e266'] = (lb['AUC_e231'], lb['AUC_e266']) if lb else (None, None)
                x['replica'] = lb['replica'] if lb else None
                x['K'] = aucK.get(n)
                xs.append(x)
            if xs:
                celle[(tipo, tk)] = OrderedDict((k, C.mes([x[k] for x in xs])) for k in xs[0] if k not in ('replica', '_forma'))
                celle[(tipo, tk)]['libri'] = len(xs)
                per_replica[(tipo, tk)] = [[x['_forma'] for x in xs if x['replica'] == r_] for r_ in (0, 1)]
    # controllo negativo: a T = 1,00 le due repliche (semi di addestramento diversi) non danno forme diverse oltre 2 errori
    rep = OrderedDict()
    for tipo in TIPI3:
        if (tipo, '100') in per_replica and all(len([v for v in x if v is not None]) > 1 for x in per_replica[(tipo, '100')]):
            a_, b_ = [C.mes([v for v in x if v is not None]) for x in per_replica[(tipo, '100')]]
            e = (a_[1] ** 2 + b_[1] ** 2) ** 0.5
            rep[tipo] = OrderedDict(replica0=a_, replica1=b_, differenza=a_[0] - b_[0], errore=e, uguali=bool(abs(a_[0] - b_[0]) <= I20.SOGLIA_ERRORI * e))
    if rep:
        ctr['negativo_repliche_a_T1'] = OrderedDict(dettaglio=rep, riuscito=all(v['uguali'] for v in rep.values()),
                                                    nota='con meno di due libri per replica il controllo non si fa')
    out['controlli'] = ctr
    out['vero'] = vero
    out['celle'] = OrderedDict(('%s T=%s' % (t, C.TEMPERATURE[tk]), v) for (t, tk), v in celle.items())
    # ---- manipolazione: la forma cresce con la temperatura
    manip = OrderedDict()
    for tipo in TIPI3:
        f = [(C.TEMPERATURE[tk], celle[(tipo, tk)]['costo_forma']) for tk in TKEYS if (tipo, tk) in celle and celle[(tipo, tk)]['costo_forma'][0] is not None]
        ok = len(f) >= 2 and all(f[i + 1][1][0] - f[i][1][0] > I20.SOGLIA_ERRORI * ((f[i][1][1] or 0) ** 2 + (f[i + 1][1][1] or 0) ** 2) ** 0.5 for i in range(len(f) - 1))
        manip[tipo] = OrderedDict(forma=[[t, x[0], x[1]] for t, x in f], cresce_con_T=bool(ok))
    ctr['la_temperatura_agisce'] = OrderedDict(dettaglio=manip, riuscito=bool(manip) and all(v['cresce_con_T'] for v in manip.values()))
    # ---- controllo del processo noto
    Fc = [Cc['forma_c3|%d' % f] for f in range(I7.PIEGHE) if 'forma_c3|%d' % f in Cc]
    noto = OrderedDict()
    if len(Fc) == I7.PIEGHE:
        f0, n0 = _forma_da_pieghe([d['forma'] for d in Fc], 'c3:testo')
        for tk in TKEYS:
            vals = [_forma_da_pieghe([d['forma'] for d in Fc], 'c3@%s:%d' % (tk, i)) for i in range(1, N_CTRL25 + 1)]
            fv, nv = C.mes([v[0] for v in vals]), C.mes([v[1] for v in vals])
            noto[tk] = OrderedDict(T=C.TEMPERATURE[tk], forma=fv, scarto=(fv[0] - f0) if fv[0] is not None and f0 is not None else None, parole_nuove=nv)
        noto['_testo'] = OrderedDict(forma=f0, parole_nuove=n0)
    out['controllo_processo_noto'] = noto
    out['letture_valide'] = bool(ctr['identita_a_T1']['riuscito'] and ctr['la_temperatura_agisce']['riuscito'])
    out['giudici_validi'] = bool(ok_giudici)
    # ---- letture
    L = OrderedDict()
    vf = vero.get('costo_forma')
    vn = vero.get('parole_nuove')
    for tipo in TIPI3:
        if vf is None or (tipo, '100') not in celle:
            continue
        gap = OrderedDict()
        for tk in TKEYS:
            if (tipo, tk) not in celle:
                continue
            m, e = celle[(tipo, tk)]['costo_forma']
            pn = celle[(tipo, tk)]['parole_nuove'][0]
            guardia = bool(pn is not None and vn and SOGLIE['nuove_fascia'][0] * vn <= pn <= SOGLIE['nuove_fascia'][1] * vn)
            gap[tk] = OrderedDict(T=C.TEMPERATURE[tk], forma=m, scarto=(m - vf) if m is not None else None, al_vero=C.classe_vero(m, e, vf), guardia_parole_nuove=guardia,
                                  parole_nuove=pn)
        g1 = gap['100']['scarto'] if '100' in gap else None
        cand = [(abs(v['scarto']), tk) for tk, v in gap.items() if v['guardia_parole_nuove'] and v['scarto'] is not None]
        migliore = min(cand)[1] if cand else None
        chiuso = (g1 - gap[migliore]['scarto']) / g1 if migliore and g1 and g1 > 0 else None
        # compromessi: contatto e copia netta "al vero" a T=1 e non a T migliore
        comp = []
        if migliore and migliore != '100':
            for k in ('contatto', 'copia_netta'):
                a = C.classe_vero(*celle[(tipo, '100')][k], vero.get(k))
                b = C.classe_vero(*celle[(tipo, migliore)][k], vero.get(k))
                if a and not b:
                    comp.append(k)
        giud = OrderedDict()
        if migliore and migliore != '100' and ok_giudici:
            for j in ('e231', 'e266', 'K'):
                giud[j] = I20.classe_misura(celle[(tipo, '100')][j], celle[(tipo, migliore)][j], None)
        esito = None
        if g1 is None or g1 < SOGLIE['scarto_voynich_min']:
            esito = 'non c\'e\' uno scarto da spiegare a T=1 (sotto %.2f bit)' % SOGLIE['scarto_voynich_min']
        elif chiuso is None:
            esito = 'nessuna temperatura passa la guardia delle parole nuove'
        elif chiuso >= SOGLIE['chiuso_quasi_tutto']:
            esito = 'quasi tutto effetto della temperatura'
        elif chiuso >= SOGLIE['chiuso_in_parte']:
            esito = 'in parte effetto della temperatura'
        else:
            esito = 'poco o niente effetto della temperatura'
        L['L3_%s' % tipo] = OrderedDict(per_temperatura=gap, scarto_T1=g1, temperatura_migliore=migliore, frazione_chiusa=chiuso, esito=esito,
                                        compromessi_persi_contatto_copia=comp, giudici_da_T1_alla_migliore=giud, giudici_validi=ok_giudici)
    nc = out['controllo_processo_noto']
    if nc and '_testo' in nc and '100' in nc:
        g1 = nc['100']['scarto']
        cand = [(abs(nc[tk]['scarto']), tk) for tk in TKEYS if tk in nc and nc[tk]['scarto'] is not None]
        mig = min(cand)[1] if cand else None
        chiuso = (g1 - nc[mig]['scarto']) / g1 if mig and g1 and g1 > 0 else None
        vede = bool(g1 is not None and g1 >= SOGLIE['controllo_scarto_min'] and chiuso is not None and chiuso >= SOGLIE['controllo_chiude_min'])
        L['L3_controllo_processo_noto'] = OrderedDict(scarto_T1=g1, temperatura_migliore=mig, frazione_chiusa=chiuso, il_controllo_vede_l_effetto=vede)
        ctr['processo_noto_vede_la_temperatura'] = OrderedDict(riuscito=vede, nota='esito, non condizione di validita\': dice se lo scarto di forma a T=1 e\' un effetto generico')
    es = [L[k]['esito'] for k in L if k.startswith('L3_') and 'esito' in L[k]]
    chi = [L[k]['frazione_chiusa'] for k in L if k.startswith('L3_') and 'frazione_chiusa' in L[k] and L[k]['frazione_chiusa'] is not None]
    cv = L.get('L3_controllo_processo_noto', {}).get('il_controllo_vede_l_effetto')
    if chi:
        if max(chi) >= SOGLIE['chiuso_quasi_tutto'] and cv:
            sintesi = 'lo scarto di forma e\' in gran parte un effetto della scrittura a temperatura 1 (confermato dal processo noto)'
        elif max(chi) >= SOGLIE['chiuso_quasi_tutto'] and cv is False:
            sintesi = 'la temperatura chiude lo scarto ma il processo noto non vede lo stesso effetto: lettura con cautela'
        elif max(chi) < SOGLIE['chiuso_in_parte']:
            sintesi = 'lo scarto di forma non e\' (solo) l\'effetto della temperatura: resta anche a temperatura piu\' bassa'
        else:
            sintesi = 'lo scarto di forma e\' in parte un effetto della temperatura'
        L['L3_sintesi'] = sintesi
    out['letture'] = L
    return out


def scrivi_md(o):
    r = ['## Parte 3: la temperatura degli imitatori', '',
         'Domanda: lo scarto di forma delle parole nuove (vero contro imitatori, ia24) e\' solo l\'effetto della scrittura a temperatura 1? Temperature: %s.' %
         ', '.join(str(v) for v in o['temperature'].values()), '']
    v = o.get('vero', {})
    r.append('Vero (calcolato qui): ' + ', '.join('%s %s' % (k, C.fmt(x)) for k, x in v.items()))
    r += ['', '| cella | libri | forma | parole nuove | contatto | copia netta | e231 | e266 | K |', '|---|---|---|---|---|---|---|---|---|']
    for n, x in o['celle'].items():
        r.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n, x['libri'], C.fmt_mes(x['costo_forma']), C.fmt_mes(x['parole_nuove']), C.fmt_mes(x['contatto']),
                                                                 C.fmt_mes(x['copia_netta']), C.fmt_mes(x['e231']), C.fmt_mes(x['e266']), C.fmt_mes(x['K'])))
    r += ['', '### Controllo del processo noto (libro v21 nella disposizione del vero)', '']
    for k, x in o['controllo_processo_noto'].items():
        r.append('- %s: %s' % (k, x))
    r += ['', '### Controlli', ''] + ['- %s: %s' % (k, x) for k, x in o['controlli'].items()]
    r += ['', 'Letture valide: %s' % ('sì' if o['letture_valide'] else 'NO'), '', '### Letture', ''] + ['- %s: %s' % (k, x) for k, x in o['letture'].items()]
    return r
