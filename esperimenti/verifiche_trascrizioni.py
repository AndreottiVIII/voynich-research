# -*- coding: utf-8 -*-
"""IA25, parte 4 (modulo di supporto): le letture centrali con un'altra trascrizione e un altro alfabeto dei glifi (la parte di C7 che serve subito).

Domanda: "si impara con 2-3 segni (k90 di ia03)", "una parola mai vista costa come una vista (R_rel di ia02)", "il contatto ultimo->primo glifo (ia08)" e
"la copia netta (ia09)" reggono se si cambia la trascrizione (Zandbergen-Landini contro Takahashi contro Claston) o l'alfabeto (glifi EVA fusi contro
lettere, un'altra fusione, l'alfabeto v101 di Claston)?

Trascrizioni in `dati/trascrizioni` (la stessa funzione di lettura di ia07, `trascrizione.leggi`):
  ZL  Zandbergen-Landini, EVA          IT  Takahashi, EVA di base          GC  Glen Claston, alfabeto v101 (un segno per glifo)
Varianti (nomi fissati prima; tutte sul testo corrente in paragrafi, parole senza ? e *):
  ZL    ZL, glifi EVA fusi (ch, sh, cth, ckh, cph, cfh): e' la lettura di ia02, ia03, ia08, ia09 (riferimento)
  ZLn   ZL, EVA non fuso (una lettera = un segno)
  IT    Takahashi, glifi EVA fusi
  GC    Claston, un carattere v101 = un segno
  ZLx   ZL fuso piu' i 6 digrammi di glifi piu' frequenti fusi (la stessa regola che si applica alle lingue)
  ZLc   ZL con la virgola (spazio incerto) NON come spazio: le due meta' restano unite
  RIN   ZL fuso con i glifi RINOMINATI (cambia solo il nome dei segni): controllo negativo, non deve cambiare niente
  SPO   ZL fuso con il 15% dei confini fra parole spostati di un segno: controllo positivo, le misure devono accorgersene
Con SOLO_CONTROLLI=1 il "libro vero" e' latino nella disposizione del Voynich e le varianti IT, GC, ZLc sono SIMULATE sul latino (IT: 3% dei confini spostati;
GC: lettere rinominate; ZLc: 4% di parole unite): non si legge nessuna trascrizione del Voynich.
Lingue: le lettere (ia02, ia03: si leggono dai loro file di risultati) e le stesse con i 6 digrammi piu' frequenti fusi (nuove).
"""
import math
import os
import random
import statistics
import time
from collections import Counter, OrderedDict

import verifiche_comune as C

import ia02_parole_mai_viste as I2  # noqa: E402
import ia03_contesto as I3  # noqa: E402
import ia14_quale_cifrario as I14  # noqa: E402
import e3c95_imparabilita as e95  # noqa: E402

I7, MS = C.I7, C.MS
SEMI25 = int(os.environ.get('SEMI25', 3))
LINGUE25 = [x for x in os.environ.get('LINGUE25', '').split('|') if x]
VAR_ALL = OrderedDict([('ZL', 'ZL, glifi EVA fusi (riferimento)'), ('ZLn', 'ZL, EVA non fuso'), ('IT', 'Takahashi, EVA fuso'), ('GC', 'Claston, alfabeto v101'),
                       ('ZLx', 'ZL fuso + 6 digrammi fusi'), ('ZLc', 'ZL, virgola non spazio'), ('RIN', 'ZL, glifi rinominati (controllo negativo)'),
                       ('SPO', 'ZL, 15% dei confini spostati (controllo positivo)')])
VAR_GRU_SOLO_SEME1 = ('SPO',)                         # il controllo positivo basta con un seme (RIN usa tutti i semi: cambia l'ordine dei segni, quindi anche i pesi iniziali della rete)
TOL = OrderedDict([('k90', 0.317), ('R_rel', 0.061), ('copia_netta', 0.015), ('lam', 0.079), ('rho', 0.173), ('contatto', 0.03)])    # tolleranze di ia14 (tau); il contatto: 0,03
SOGLIE = OrderedDict([('tolleranze', TOL), ('n_digrammi', 6), ('quota_confini_spostati', 0.15), ('rinomina_tol_copia', 1e-6), ('positivo_misure_mosse', 2),
                      ('riproduzione_k90', 1e-6), ('riproduzione_conteggi', 5e-4)])
MIN_PAROLE = 40                                      # pagine con almeno 40 parole (come ia01)
_C = {}


# ---------------------------------------------------------------- lettura delle trascrizioni

def _sposta_confini(pagine, quota, seme):
    """Sposta di un segno il confine fra due parole vicine (a caso, con probabilita' `quota` per confine)."""
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            ws = list(ws)
            for j in range(len(ws) - 1):
                if rnd.random() < quota:
                    a, b = ws[j], ws[j + 1]
                    pool = a + b
                    d = rnd.choice((-1, 1))
                    k = len(a) + d
                    if 1 <= k <= len(pool) - 1:
                        ws[j], ws[j + 1] = pool[:k], pool[k:]
            nr.append((ini, ws))
        out[p] = nr
    return out


def _unisci(pagine, quota, seme):
    rnd = random.Random(seme)
    out = OrderedDict()
    for p, rows in pagine.items():
        nr = []
        for ini, ws in rows:
            nuove, j = [], 0
            while j < len(ws):
                if j + 1 < len(ws) and rnd.random() < quota:
                    nuove.append(ws[j] + ws[j + 1])
                    j += 2
                else:
                    nuove.append(ws[j])
                    j += 1
            nr.append((ini, nuove))
        out[p] = nr
    return out


def _rinomina_lettere(pagine):
    t = str.maketrans('abcdefghijklmnopqrstuvwxyz', '123456789ABCDEFGHIJKLMNOPQ')
    return OrderedDict((p, [(ini, [w.translate(t) for w in ws]) for ini, ws in rows]) for p, rows in pagine.items())


def righe_trascrizione(quale):
    """pagina -> [(inizio paragrafo, [parola come stringa])] di tutte le pagine, per 'ZL', 'IT', 'GC', 'ZLc' (virgola come parte della parola)."""
    k = ('righe', quale)
    if k in _C:
        return _C[k]
    if C.SOLO_CONTROLLI:
        base = OrderedDict()
        for x in I7.libro_vero():
            base.setdefault(x['pagina'], []).append((bool(x['ini']), list(x['parole'])))
        out = {'ZL': base, 'IT': _sposta_confini(base, 0.03, 2501), 'GC': _rinomina_lettere(base), 'ZLc': _unisci(base, 0.04, 2502)}[quale]
    else:
        import trascrizione
        q, vs = ('ZL', True) if quale == 'ZL' else ('ZL', False) if quale == 'ZLc' else (quale, True)
        out = OrderedDict()
        for r in trascrizione.testo_corrente(trascrizione.leggi(q, virgola_spazio=vs)):
            ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
            if ps:
                out.setdefault(r.pagina, []).append((bool(r.inizio_par), ps))
    _C[k] = out
    return out


def bigrammi_fusi(parole, n):
    """I `n` digrammi di segni vicini piu' frequenti (dentro la parola) di un elenco di parole (tuple di segni); a parita' l'ordine alfabetico."""
    c = Counter()
    for w in parole:
        for a, b in zip(w, w[1:]):
            c[(a, b)] += 1
    return [kk for kk, _ in sorted(c.items(), key=lambda x: (-x[1], str(x[0])))[:n]]


def applica_fusione(w, coppie):
    """Da sinistra a destra: dove due segni vicini sono una delle `coppie` (nell'ordine di frequenza) diventano un segno solo (senza sovrapporsi)."""
    out, i, ins = [], 0, set(coppie)
    while i < len(w):
        if i + 1 < len(w) and (w[i], w[i + 1]) in ins:
            out.append(w[i] + w[i + 1])
            i += 2
        else:
            out.append(w[i])
            i += 1
    return tuple(out)


def pagine_variante(var):
    """Variante `var` -> pagina -> [(inizio, [parola come tupla di segni])] (tutte le pagine)."""
    k = ('var', var)
    if k in _C:
        return _C[k]
    D = I7.divisore()
    base = {'ZL': 'ZL', 'ZLn': 'ZL', 'ZLx': 'ZL', 'RIN': 'ZL', 'SPO': 'ZL', 'IT': 'IT', 'GC': 'GC', 'ZLc': 'ZLc'}[var]
    righe = righe_trascrizione(base)
    if var == 'SPO':
        righe = _sposta_confini(righe, SOGLIE['quota_confini_spostati'], 2503)
    if var == 'ZLn':
        div = lambda w: tuple(w)                                              # noqa: E731
    elif var == 'GC':
        div = lambda w: tuple(w)                                              # noqa: E731
    else:
        div = lambda w: tuple(D(w))                                           # noqa: E731
    pag = OrderedDict((p, [(ini, [div(w) for w in ws]) for ini, ws in rr]) for p, rr in righe.items())
    if var == 'ZLx':
        tutte = [w for rr in pag.values() for _, ws in rr for w in ws]
        coppie = bigrammi_fusi(tutte, SOGLIE['n_digrammi'])
        pag = OrderedDict((p, [(ini, [applica_fusione(w, coppie) for w in ws]) for ini, ws in rr]) for p, rr in pag.items())
    if var == 'RIN':
        glifi = sorted({g for rr in pag.values() for _, ws in rr for w in ws for g in w})
        ren = {g: 'Z%d' % i for i, g in enumerate(glifi)}
        pag = OrderedDict((p, [(ini, [tuple(ren[g] for g in w) for w in ws]) for ini, ws in rr]) for p, rr in pag.items())
    _C[k] = pag
    return pag


def blocchi_variante(var):
    """Per le reti (ia02, ia03): lista di pagine, ogni pagina lista di righe, ogni riga lista di parole (tuple di segni)."""
    return [[list(ws) for _, ws in rr] for rr in pagine_variante(var).values()]


def pagine_per_conteggi(var):
    """(pagine, pieghe) per le misure di conteggio: pagine con almeno 40 parole e il cui foglio ha una piega nel libro vero."""
    pg = I7.pieghe()
    pag = OrderedDict()
    for p, rr in sorted(pagine_variante(var).items()):
        if sum(len(ws) for _, ws in rr) >= MIN_PAROLE and I7.foglio_di(p) in pg:
            pag[p] = rr
    return pag, {p: pg[I7.foglio_di(p)] for p in pag}


# ---------------------------------------------------------------- misure di conteggio (ia09, ia08)

def lavoro_conteggi(var):
    inizio = time.time()
    pag, fold = pagine_per_conteggi(var)
    r = MS.lavoro_M('vere', pag, fold)                 # il nome del libro vero in ia20, per tutte le varianti: stessi semi (ZL ritrova i numeri di ia20)
    s = C.stime_M(r)
    ris = OrderedDict([('lavoro', 'trasc|%s' % var), ('var', var), ('pagine', len(pag)), ('copia_netta', s['netto'].p), ('copia_netta_ic', s['netto'].ic()), ('lam', s['lam'].p),
                       ('rho', s['rho'].p), ('contatto', s['contatto']), ('parole', sum(len(ws) for rr in pag.values() for _, ws in rr)),
                       ('tipi', len({w for rr in pag.values() for _, ws in rr for w in ws}))])
    if var == 'ZL':
        c = I7.contesto_A()
        ris['identico_al_contesto_di_ia07'] = bool(list(pag) == list(c['ids']) and all(pag[p] == c['vere'][p] for p in pag))
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- reti (ia02, ia03): preparazione nel processo principale

def testi_lingue():
    """(lettere, fuse): nome della lingua -> blocchi, per le lingue di ia02 e ia03 (stesso catalogo di ia03), e le stesse con i 6 digrammi piu' frequenti fusi."""
    cat = I3.catalogo()
    lett = OrderedDict((n, v['blocchi']) for n, v in cat.items() if v['ruolo'] == 'lingua' and (not LINGUE25 or any(x in n for x in LINGUE25)))
    fuse = OrderedDict()
    for n, bl in lett.items():
        parole = [w for b in bl for r in b for w in r]
        coppie = bigrammi_fusi(parole, SOGLIE['n_digrammi'])
        fuse[n] = [[[applica_fusione(w, coppie) for w in r] for r in b] for b in bl]
    return lett, fuse


def prepara_lavori_gru(testi, semi):
    """testi: nome -> blocchi. -> lista di job (R e K) con i flussi gia' codificati, uno per testo e seme (come i nativi di ia14)."""
    out = []
    for nome, bl in testi.items():
        t = OrderedDict([(nome, dict(blocchi=bl, ruolo='voynich', gruppo=nome, trasforma=None, speciali=None))])
        e95.SEMI = tuple(semi[nome])
        lav2, sc2 = I2.prepara(t, t)
        I3.SEMI = tuple(semi[nome])
        lav3, sc3 = I3.prepara(t)
        if sc2 or sc3:
            out.append(dict(tipo='scarto', nome=nome, scarti=[str(sc2), str(sc3)]))
            continue
        for l in lav2:
            out.append(dict(tipo='R', nome=nome, seme=l['seme'], descr=dict(tipo='trasc'), lavoro=l))
        for l in lav3:
            out.append(dict(tipo='K', nome=nome, seme=l['seme'], descr=dict(tipo='trasc'), lavoro=l))
    return out


def lavoro_gru(job):
    r = I14.lavoro(job)
    r['lavoro'] = 'gru|%s|%s|%s' % (job['tipo'], job['nome'], job['seme'])
    return r


def semi_di(nome):
    if nome in VAR_GRU_SOLO_SEME1:
        return [1]
    return list(range(1, SEMI25 + 1))


# ---------------------------------------------------------------- analisi

def media_sd(xs):
    xs = [x for x in xs if x is not None]
    return (statistics.mean(xs), statistics.stdev(xs) if len(xs) > 1 else 0.0, len(xs)) if xs else (None, None, 0)


def misure_gru(corse, nome, seme_max=None):
    """k90 (variante B di ia03) e R_rel (ia02) di un testo dai risultati dei lavori `gru|...`."""
    k90, rrel, nuove = [], [], []
    for k, c in corse.items():
        if c.get('errore') or c.get('nome') != nome:
            continue
        if c['tipo'] == 'K':
            m = I3.misure_corsa(c['corsa'], 'B')
            k90.append((c['seme'], m['k90_interpolato'] if m['k90_interpolato'] is not None else I14.K90_NON_DEFINITO))
        elif c['tipo'] == 'R':
            m = I2.misure_corsa(c['corsa'])
            rrel.append((c['seme'], m['R_rel']))
            nuove.append((c['seme'], m.get('quota_nuove')))
    return dict(k90=sorted(k90), R_rel=sorted(rrel), quota_nuove=sorted(nuove))


def lingue_da_file(ia03_corse, ia02_corse, nomi, seme_max):
    """k90 e R_rel (alfabeto delle lettere) delle lingue `nomi` dai file di risultati di ia03 e ia02 (stessi semi 1..seme_max)."""
    out = OrderedDict()
    for n in nomi:
        k90 = [(c['seme'], I3.misure_corsa(c, 'B')['k90_interpolato']) for c in ia03_corse if c.get('testo') == n and c['seme'] <= seme_max]
        rr = [(c['seme'], I2.misure_corsa(c)['R_rel']) for c in ia02_corse if c.get('testo') == n and c['seme'] <= seme_max]
        k90 = [(s, v if v is not None else I14.K90_NON_DEFINITO) for s, v in k90]
        out[n] = dict(k90=sorted(k90), R_rel=sorted(rr))
    return out


def analisi(conteggi, corse_gru, lingue_lettere, lingue_fuse_nomi, rif_ia03=None, rif_ia20=None):
    """conteggi: var -> risultato di lavoro_conteggi; corse_gru: lavoro -> risultato (variabili di Voynich e lingue fuse); lingue_lettere: lingua -> misure da file (ia02/ia03)."""
    out = OrderedDict(soglie=SOGLIE, varianti=VAR_ALL)
    base = conteggi.get('ZL')
    tab = OrderedDict()
    for var in VAR_ALL:
        if var not in conteggi:
            continue
        x = conteggi[var]
        g = misure_gru(corse_gru, 'V:' + var)
        k90, rr = media_sd([v for _, v in g['k90']]), media_sd([v for _, v in g['R_rel']])
        tab[var] = OrderedDict(parole=x['parole'], tipi=x['tipi'], pagine=x['pagine'], copia_netta=x['copia_netta'], copia_netta_ic=x['copia_netta_ic'], lam=x['lam'], rho=x['rho'],
                               contatto=x['contatto'], k90=k90[0], k90_sd=k90[1], k90_n=k90[2], R_rel=rr[0], R_rel_sd=rr[1], R_rel_n=rr[2], k90_per_seme=g['k90'], R_rel_per_seme=g['R_rel'])
    out['tabella'] = tab
    # ---- le lingue: lettere (da file) e con i digrammi fusi (nuove)
    kl = OrderedDict((n, media_sd([v for _, v in d['k90']])[0]) for n, d in lingue_lettere.items())
    rl = OrderedDict((n, media_sd([v for _, v in d['R_rel']])[0]) for n, d in lingue_lettere.items())
    kf, rf = OrderedDict(), OrderedDict()
    for n in lingue_fuse_nomi:
        g = misure_gru(corse_gru, 'L:' + n + '+f')
        kf[n] = media_sd([v for _, v in g['k90']])[0]
        rf[n] = media_sd([v for _, v in g['R_rel']])[0]
    vl = [v for v in kl.values() if v is not None]
    vf = [v for v in kf.values() if v is not None]
    out['lingue'] = OrderedDict(lettere=OrderedDict(k90=kl, R_rel=rl), fuse=OrderedDict(k90=kf, R_rel=rf),
                                minimo_k90_lettere=min(vl) if vl else None, minimo_k90_fuse=min(vf) if vf else None, n_lettere=len(vl), n_fuse=len(vf))
    # ---- controlli
    ctr = OrderedDict()
    if base:
        ctr['ZL_uguale_al_contesto_di_ia07'] = OrderedDict(riuscito=bool(base.get('identico_al_contesto_di_ia07')))
    if 'RIN' in tab and 'ZL' in tab:
        d = OrderedDict((k, abs(tab['RIN'][k] - tab['ZL'][k])) for k in ('copia_netta', 'lam', 'contatto') if tab['RIN'][k] is not None and tab['ZL'][k] is not None)
        dk = abs(tab['RIN']['k90'] - tab['ZL']['k90']) if tab['RIN']['k90'] is not None and tab['ZL']['k90'] is not None else None
        ctr['negativo_rinomina'] = OrderedDict(differenze=d, differenza_k90=dk, soglia_conteggi=SOGLIE['rinomina_tol_copia'], soglia_k90=TOL['k90'],
                                               riuscito=bool(d) and all(v <= SOGLIE['rinomina_tol_copia'] for v in d.values()) and (dk is None or dk <= TOL['k90']))
    if 'SPO' in tab and 'ZL' in tab:
        mosse = [k for k in ('copia_netta', 'contatto', 'R_rel') if tab['SPO'][k] is not None and tab['ZL'][k] is not None and abs(tab['SPO'][k] - tab['ZL'][k]) > TOL[k]]
        ctr['positivo_confini_spostati'] = OrderedDict(misure_mosse=mosse, soglia=SOGLIE['positivo_misure_mosse'], riuscito=len(mosse) >= SOGLIE['positivo_misure_mosse'])
    if 'ZL' in tab and rif_ia20:
        d = OrderedDict((k, abs(tab['ZL'][k] - rif_ia20[k])) for k in ('copia_netta', 'lam', 'contatto') if tab['ZL'][k] is not None and rif_ia20.get(k) is not None)
        ctr['riproduzione_ia20_conteggi'] = OrderedDict(differenze=d, soglia=SOGLIE['riproduzione_conteggi'], riuscito=bool(d) and all(v <= SOGLIE['riproduzione_conteggi'] for v in d.values()))
    if 'ZL' in tab and rif_ia03 is not None and rif_ia03.get('Voynich'):
        mio = dict(tab['ZL']['k90_per_seme'])
        ok = [abs(mio[s] - v) <= SOGLIE['riproduzione_k90'] for s, v in rif_ia03['Voynich'] if s in mio]
        ctr['riproduzione_k90_di_ia03'] = OrderedDict(semi_confrontati=len(ok), riuscito=bool(ok) and all(ok))
    out['controlli'] = ctr
    out['letture_valide'] = bool(ctr) and all(v['riuscito'] for v in ctr.values())
    # ---- letture
    L = OrderedDict()
    if base:
        for var in ('ZLn', 'IT', 'GC', 'ZLx', 'ZLc'):
            if var not in tab:
                continue
            t, b = tab[var], tab['ZL']
            comp_fuso = var in ('ZLx',)
            minimo = out['lingue']['minimo_k90_fuse'] if comp_fuso else out['lingue']['minimo_k90_lettere']
            sotto = (t['k90'] < minimo) if t['k90'] is not None and minimo is not None else None
            diff = OrderedDict()
            for k in ('k90', 'R_rel', 'copia_netta', 'lam', 'rho', 'contatto'):
                a, bb = t[k], b[k]
                diff[k] = OrderedDict(variante=a, riferimento=bb, differenza=(a - bb) if a is not None and bb is not None else None,
                                      regge=(abs(a - bb) <= TOL[k]) if a is not None and bb is not None else None)
            ba = (b['k90'] < out['lingue']['minimo_k90_lettere']) if b['k90'] is not None and out['lingue']['minimo_k90_lettere'] is not None else None
            L['L4_%s' % var] = OrderedDict(
                descrizione=VAR_ALL[var], k90_sotto_tutte_le_lingue=sotto, k90_di_riferimento_sotto_tutte_le_lingue=ba, confronto_lingue='fuse' if comp_fuso else 'lettere',
                misure=diff, regge_tutto=bool(all(x['regge'] for x in diff.values() if x['regge'] is not None) and (sotto == ba if sotto is not None and ba is not None else True)))
        L['L4_sintesi'] = OrderedDict((v, x['regge_tutto']) for v, x in L.items() if v.startswith('L4_'))
    out['letture'] = L
    return out


def scrivi_md(o):
    r = ['## Parte 4: seconda trascrizione e altro alfabeto', '',
         'Domanda: k90 (ia03), R_rel (ia02), contatto (ia08) e copia netta (ia09) reggono al cambio di trascrizione e di alfabeto? Tolleranze: %s.' % dict(o['soglie']['tolleranze']), '',
         '| variante | parole | tipi | k90 (sd, n) | R_rel | copia netta | Λ | rho | contatto |', '|---|---|---|---|---|---|---|---|---|']
    for v, x in o['tabella'].items():
        r.append('| %s | %s | %s | %s (%s, %s) | %s | %s | %s | %s | %s |' % (v, x['parole'], x['tipi'], C.fmt(x['k90'], 2), C.fmt(x['k90_sd'], 2), x['k90_n'], C.fmt(x['R_rel'], 3),
                                                                           C.fmt(x['copia_netta'], 3), C.fmt(x['lam'], 3), C.fmt(x['rho'], 3), C.fmt(x['contatto'], 3)))
    L = o['lingue']
    r += ['', 'Lingue: minimo k90 con le lettere %s (%d lingue), con i 6 digrammi fusi %s (%d lingue).' % (C.fmt(L['minimo_k90_lettere'], 2), L['n_lettere'], C.fmt(L['minimo_k90_fuse'], 2), L['n_fuse']),
          '', '### Controlli', ''] + ['- %s: %s' % (k, v) for k, v in o['controlli'].items()]
    r += ['', 'Letture valide: %s' % ('sì' if o['letture_valide'] else 'NO'), '', '### Letture', ''] + ['- %s: %s' % (k, v) for k, v in o['letture'].items()]
    return r
