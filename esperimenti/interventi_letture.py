# -*- coding: utf-8 -*-
"""Supporto di ia30 (modulo, non e' un esperimento): analisi, controlli e letture preregistrate.

Che cosa c'e' qui, in parole semplici
- Dalle somme per pagina della fase A si ricavano, per ogni modello e ogni intervento, cinque "effetti" (in bit; piu' alto = l'intervento fa perdere piu' previsione):
    kl_primo   quanto cambia la previsione del primo glifo della prima parola dopo il punto (il "contatto" per gli interventi sulla parola prima; l'"inizio riga"
               per quelli sulla riga o sulla testa);
    eco_sopra  quanto peggiora la previsione delle parole che sono copie o varianti di una parola della RIGA SOPRA, rispetto alle altre parole;
    eco_riga   lo stesso per le parole che somigliano a una parola della riga in corso;
    term       quanto peggiora la previsione del terminatore (spazio o fine riga) sull'ultima parola della riga: i "bordi";
    pc         quanto cala la massa di copia del puntatore (solo E2 e M5).
  Gli errori si ricavano ricampionando le pagine (200 estrazioni).
- Ogni coppia intervento -> tratto riceve un'etichetta ("causale", "non causale", "zona grigia", "non leggibile") dal RAPPORTO con l'effetto di riferimento del tratto
  (l'ancora). Le soglie sono scritte nella preregistrazione. Un'etichetta vale per il Voynich solo se il controllo positivo (modelli addestrati su testo sintetico a regole
  note, 5 semi) restituisce l'etichetta giusta in almeno 4 semi su 5 per quella coppia ("validata").
- Per i libri: ogni tratto del libro scritto sotto un intervento diviso quello del libro senza intervento: "sparisce", "cala in parte", "resta", "cresce".
Nessuna parola del manoscritto compare qui.
"""
import glob
import json
import math
import os
from collections import Counter, OrderedDict

import numpy as np

B_BOOT = 200
SOGLIE = OrderedDict([('causale_rapporto_min', 0.50), ('non_causale_rapporto_max', 0.40)])      # fissate dopo la prova a taglia vera sul latino (vedi preregistrazione)
TAU = OrderedDict([('kl_primo', 0.01), ('eco_sopra', 0.02), ('eco_riga', 0.02), ('term', 0.05), ('pc', 0.01)])      # effetto minimo leggibile dell'ancora (bit)
TRATTI = ('kl_primo', 'eco_sopra', 'eco_riga', 'term', 'pc')
FAM_PAROLA = ('u1', 'u2', 'p2', 'p3', 'pm', 'p1', 'pw', 'w2', 'rc', 'nul', 'fill')
POSIZIONI = ('u1', 'p2', 'p3', 'pm', 'p1')                                  # interventi su un solo posto della parola prima: il loro rapporto mediano e' il "pavimento" della sensibilita' diffusa
SOGLIE_ECCESSO = OrderedDict([('causale_min', 0.25), ('non_causale_max', 0.15)])      # eccesso del rapporto sul pavimento (contatto)
MINIME = ('u1', 'u2', 'p2', 'p3', 'pm', 'p1')                                          # interventi con coppia minima: l'ancora e' `pw` sugli stessi punti (`pw@nome`)
FAM_RIGA = ('rs_m', 'rs_p', 'rs_a', 'rl', 'hN', 'hT', 'hR')
NEGATIVI = ('nul', 'lnul', 'rl', 'fill', 'lfill')
ANCORE = OrderedDict([('kl_primo', {'parola': 'pw', 'riga': 'hN'}), ('eco_sopra', {'parola': 'rs_a', 'riga': 'rs_a'}), ('eco_riga', {'parola': 'pw', 'riga': 'rs_a'}),
                      ('term', {'parola': 'hN', 'riga': 'hN'}), ('pc', {'parola': 'rs_a', 'riga': 'rs_a'})])
# verita' note del testo sintetico `ec` (fonti d'informazione piantate)
VERITA = OrderedDict([
    (('u1', 'kl_primo'), 'causale'), (('u2', 'kl_primo'), 'causale'), (('pw', 'kl_primo'), 'causale'),
    (('p2', 'kl_primo'), 'non causale'), (('p3', 'kl_primo'), 'non causale'), (('pm', 'kl_primo'), 'non causale'), (('p1', 'kl_primo'), 'non causale'), (('w2', 'kl_primo'), 'non causale'), (('rc', 'kl_primo'), 'non causale'),
    (('rs_a', 'eco_sopra'), 'causale'), (('rs_p', 'eco_sopra'), 'causale'), (('rs_m', 'eco_sopra'), 'non causale'), (('rl', 'eco_sopra'), 'non causale'),
    (('hN', 'term'), 'causale')])


def famiglia(nome):
    return 'parola' if nome in FAM_PAROLA else 'riga'


# ---------------------------------------------------------------- effetti da somme (S, N, U)

def _div(a, b, min_n=5):
    return float(a / b) if b >= min_n else float('nan')


def effetti(S, N, U):
    """Dai totali (S: classe x k x campo, N: classe x k, U: 3) i cinque effetti."""
    out = OrderedDict()
    out['kl_primo'] = _div(S[:, 0, 0].sum(), N[:, 0].sum())
    for nome, c in (('eco_sopra', 2), ('eco_riga', 1)):
        n_c, n_0 = N[c].sum(), N[0].sum()
        out[nome] = (-(_div(S[c, :, 2].sum(), n_c) - _div(S[0, :, 2].sum(), n_0)) if (n_c >= 5 and n_0 >= 5) else float('nan'))
    out['term'] = -_div(U[1], U[0])
    out['pc'] = -_div(S[:, :, 3].sum(), N.sum())
    return out


def unita_da_jobs(jobs, chiave='per_pagina'):
    """pagina -> {intervento: (S, N, U)} sommando i job che hanno la stessa pagina (repliche)."""
    out = OrderedDict()
    for d in jobs:
        for pagina, ints in d.get(chiave, {}).items():
            u = out.setdefault(pagina, {})
            for nome, a in ints.items():
                S, N, U = np.array(a['S']), np.array(a['N']), np.array(a['U'])
                if nome in u:
                    u[nome] = (u[nome][0] + S, u[nome][1] + N, u[nome][2] + U)
                else:
                    u[nome] = (S, N, U)
    return out


def stima_unita(unita, seme=1, B=B_BOOT):
    """Per ogni intervento: dizionario tratto -> dict(punto, campioni (B)). Ricampiona le unita' (pagine)."""
    nomi = sorted({n for u in unita.values() for n in u})
    pag = list(unita)
    rng = np.random.default_rng(seme)
    pesi = np.stack([np.bincount(rng.integers(0, len(pag), len(pag)), minlength=len(pag)) for _ in range(B)]) if pag else np.zeros((B, 0))
    out = OrderedDict()
    for nome in nomi:
        forme = next(u[nome] for u in unita.values() if nome in u)
        S = np.stack([unita[p][nome][0] if nome in unita[p] else np.zeros_like(forme[0]) for p in pag])
        N = np.stack([unita[p][nome][1] if nome in unita[p] else np.zeros_like(forme[1]) for p in pag])
        U = np.stack([unita[p][nome][2] if nome in unita[p] else np.zeros_like(forme[2]) for p in pag])
        tot = effetti(S.sum(0), N.sum(0), U.sum(0))
        camp = {t: [] for t in TRATTI}
        for b in range(B):
            e = effetti(np.tensordot(pesi[b], S, 1), np.tensordot(pesi[b], N, 1), np.tensordot(pesi[b], U, 1))
            for t in TRATTI:
                camp[t].append(e[t])
        out[nome] = OrderedDict((t, dict(punto=tot[t], campioni=np.array(camp[t]))) for t in TRATTI)
        out[nome]['_n'] = int(N.sum(0)[:, 0].sum())
    return out


def ic(x, q=(2.5, 97.5)):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 10:
        return [float('nan'), float('nan')]
    return [float(np.percentile(x, q[0])), float(np.percentile(x, q[1]))]


def pavimento(stima):
    """Campioni (ricampionamento delle pagine) del rapporto mediano, fra gli interventi su un solo posto della parola prima (`POSIZIONI`), dell'effetto sul primo glifo con
    quello della parola intera sugli stessi punti: la sensibilita' DIFFUSA della rete a un glifo cambiato in una parola vera, qualunque sia il posto. None se i posti
    leggibili sono meno di tre."""
    rs = []
    for j in POSIZIONI:
        a = stima.get('pw@' + j, {}).get('kl_primo')
        e = stima.get(j, {}).get('kl_primo')
        if a is None or e is None:
            continue
        with np.errstate(divide='ignore', invalid='ignore'):
            rs.append(np.where(a['campioni'] > 0, e['campioni'] / a['campioni'], np.nan))
    if len(rs) < 3:
        return None
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return np.nanmedian(np.stack(rs), 0)


def etichetta(stima, nome, tratto, pav=None):
    """Etichetta di (nome, tratto) rispetto all'ancora del tratto (della stessa famiglia). Restituisce dict(punto, ic, ancora, rapporto, ic_rapporto, etichetta).
    Per il contatto (`kl_primo`) degli interventi sulla parola prima con coppia minima la lettura e' sull'ECCESSO del rapporto sul pavimento diffuso (`pav`): causale se il
    rapporto ha il limite basso >= 0,50 e l'eccesso >= 0,25; non causale se l'eccesso ha il limite alto <= 0,15; altrimenti zona grigia."""
    fam = famiglia(nome)
    anc = ANCORE[tratto][fam]
    if tratto == 'kl_primo' and nome in MINIME and ('pw@' + nome) in stima:
        anc = 'pw@' + nome
    s = stima.get(nome, {}).get(tratto)
    a = stima.get(anc, {}).get(tratto)
    if s is None:
        return None
    out = OrderedDict([('punto', s['punto']), ('ic', ic(s['campioni'])), ('ancora', anc)])
    if a is None or not (a['punto'] == a['punto']):
        out.update(rapporto=None, ic_rapporto=None, etichetta='non leggibile')
        return out
    a_lo = ic(a['campioni'])[0]
    out['ancora_punto'] = a['punto']
    out['ancora_ic'] = ic(a['campioni'])
    if not (a_lo >= TAU[tratto]):
        out.update(rapporto=None, ic_rapporto=None, etichetta='non leggibile')
        return out
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(a['campioni'] > 0, s['campioni'] / a['campioni'], np.nan)
    rl, rh = ic(r)
    out['rapporto'] = float(s['punto'] / a['punto']) if a['punto'] else None
    out['ic_rapporto'] = [rl, rh]
    if tratto == 'kl_primo' and nome in MINIME and pav is not None:
        ecc = r - pav
        el, eh = ic(ecc)
        out['pavimento'] = float(np.nanmedian(pav))
        out['eccesso'] = float(np.nanmedian(ecc))
        out['ic_eccesso'] = [el, eh]
        if rl >= SOGLIE['causale_rapporto_min'] and el >= SOGLIE_ECCESSO['causale_min']:
            out['etichetta'] = 'causale'
        elif eh <= SOGLIE_ECCESSO['non_causale_max']:
            out['etichetta'] = 'non causale'
        else:
            out['etichetta'] = 'zona grigia'
        return out
    if nome == anc:
        out['etichetta'] = 'causale'
    elif rl >= SOGLIE['causale_rapporto_min']:
        out['etichetta'] = 'causale'
    elif rh <= SOGLIE['non_causale_rapporto_max']:
        out['etichetta'] = 'non causale'
    else:
        out['etichetta'] = 'zona grigia'
    return out


def mappa(stima):
    """nome -> tratto -> etichetta, per tutti gli interventi presenti."""
    out = OrderedDict()
    pav = pavimento(stima)
    for nome in stima:
        if '@' in nome:
            continue
        out[nome] = OrderedDict()
        for t in TRATTI:
            e = etichetta(stima, nome, t, pav)
            if e is not None and not (e['punto'] != e['punto']):
                out[nome][t] = e
        out[nome]['_n'] = stima[nome]['_n']
    return out


# ---------------------------------------------------------------- lettura dei file di fase A

def carica_A(cartella):
    out = {}
    for fn in sorted(glob.glob(os.path.join(cartella, 'A_*.json'))):
        d = json.load(open(fn, encoding='utf-8'))
        out.setdefault((d['fonte'], d['tipo']), []).append(d)
    return out


def valida_controllo(mappe_semi, verita=VERITA):
    """mappe_semi: lista di mappe (una per seme) del testo `ec`. -> dict (nome, tratto) -> dict(verita, etichette, validata). Validata se l'etichetta giusta esce in almeno
    il 80% dei semi (4 su 5)."""
    n = len(mappe_semi)
    need = int(math.ceil(0.8 * n))
    out = OrderedDict()
    for (nome, tratto), v in verita.items():
        ets = [m.get(nome, {}).get(tratto, {}).get('etichetta', 'assente') for m in mappe_semi]
        out['%s|%s' % (nome, tratto)] = OrderedDict([('verita', v), ('etichette', ets), ('giuste', sum(e == v for e in ets)), ('semi', n), ('validata', sum(e == v for e in ets) >= need)])
    return out


def controllo_senza(mappe_senza, mappe_ec=None):
    """Su modelli addestrati senza la regola (`senza`): le coppie che nel testo `ec` sono causali per costruzione (`u1` e `u2` per il contatto, `rs_p` per l'eco) NON devono
    risultare "causali" (l'effetto non e' zero neppure senza regola, perche' la rete e' sensibile anche a cio' che nessuna regola richiede: conta che l'ultimo glifo non sia
    speciale). `mappe_ec` serve solo a riportare, per confronto, l'etichetta degli stessi interventi nei modelli con la regola."""
    out = OrderedDict()
    for nome, tratto in (('u1', 'kl_primo'), ('u2', 'kl_primo'), ('rs_p', 'eco_sopra')):
        e_sen = [m.get(nome, {}).get(tratto, {}).get('etichetta', 'assente') for m in mappe_senza]
        r_sen = [m.get(nome, {}).get(tratto, {}).get('rapporto') for m in mappe_senza]
        e_ec = [m.get(nome, {}).get(tratto, {}).get('etichetta', 'assente') for m in (mappe_ec or [])]
        out['%s|%s' % (nome, tratto)] = OrderedDict([('etichette_senza', e_sen), ('rapporti_senza', r_sen), ('etichette_ec', e_ec), ('riuscito', all(e != 'causale' for e in e_sen))])
    return out


# ---------------------------------------------------------------- scambio di stati (dove)

def analisi_patch(jobs):
    """Per ogni (intervento, variante): media e errore (fra i modelli) di f0 (quanto del cambio del primo glifo passa) e fw (quanto del cambio delle parole). k70: il
    numero minimo di dimensioni del secondo strato che porta almeno il 70% (f0)."""
    per = {}
    for d in jobs:
        for chiave, v in d.get('patch', {}).items():
            nome, var = chiave.split('|')
            if v[4] == 0:
                continue
            f0 = v[0] / v[1] if v[1] > 0 else float('nan')
            fw = v[2] / v[3] if v[3] > 0 else float('nan')
            per.setdefault((nome, var), []).append((f0, fw, v[4]))
    out = OrderedDict()
    for (nome, var), lst in sorted(per.items()):
        a = np.array([[x[0], x[1]] for x in lst], dtype=float)
        m = np.nanmean(a, 0)
        e = np.nanstd(a, 0, ddof=1) / math.sqrt(len(a)) if len(a) > 1 else np.array([float('nan')] * 2)
        out.setdefault(nome, OrderedDict())[var] = OrderedDict([('f0', float(m[0])), ('f0_es', float(e[0])), ('fw', float(m[1])), ('fw_es', float(e[1])), ('modelli', len(lst)),
                                                                ('punti', int(sum(x[2] for x in lst)))])
    for nome, d in out.items():
        for pref in ('top', 'rnd'):
            ks = sorted(int(v[3:]) for v in d if v.startswith(pref))
            k70 = None
            for k in ks:
                if d['%s%d' % (pref, k)]['f0'] >= 0.7:
                    k70 = k
                    break
            d['_k70_' + pref] = k70
    return out


# ---------------------------------------------------------------- libri

def tabella_libri(corse, M):
    """Misure dei libri per (fonte, tipo, condizione): liste per libro."""
    leggere = {}
    pesanti, dd = {}, {}
    for c in corse:
        if c.get('errore'):
            continue
        l = c['lavoro']
        if l.startswith('libro|'):
            leggere.setdefault((c['fonte'], c['tipo'], c['cond']), {})[c['i']] = c
        elif l.startswith('M|') and l != 'M|vere':
            pesanti[l[2:]] = c
        elif l == 'M|vere':
            pesanti['vere'] = c
        elif l.startswith('D|'):
            dd[c['piega']] = c
        elif l.startswith('Dc|'):
            dd[('c', c['seme'])] = c
    return leggere, pesanti, dd


def valori_libro(c, pes, D_libro):
    """Tratti di un libro: dict nome -> valore."""
    m = c['misure']
    v = OrderedDict()
    v['contatto'] = m['contatto']
    v['eco_riga'] = m['eco_riga']
    v['eco_sopra'] = m['eco_sopra']
    v['tasso_eco'] = m['tasso_eco_vicini']
    v['eco_netto'] = m['tasso_eco_vicini'] - m['tasso_eco_lontani']                # eco meno le somiglianze per caso (candidati lontani)
    v['aderenza_N'] = m['aderenza_N']
    b = m['bordi']
    v['bordi_inizio'] = b.get('inizio_primo')
    v['bordi_fine'] = b.get('fine_ultimo')
    if pes is not None and pes.get('sintesi'):
        v['copia_netta'] = pes['sintesi'].get('copia_netta')
        v['lam'] = pes['sintesi'].get('lam')
        v['contatto_pesante'] = pes['sintesi'].get('contatto')
    if D_libro is not None:
        v['D'] = D_libro
    return v


def rapporto_boot(x, y, B=B_BOOT, seme=1):
    """Rapporto fra la media di x (condizione) e quella di y (base) con intervallo (ricampionando i libri)."""
    x = np.array([a for a in x if a is not None and a == a], dtype=float)
    y = np.array([a for a in y if a is not None and a == a], dtype=float)
    if len(x) == 0 or len(y) == 0 or y.mean() == 0:
        return None
    rng = np.random.default_rng(seme)
    r = []
    for _ in range(B):
        yy = y[rng.integers(0, len(y), len(y))].mean()
        xx = x[rng.integers(0, len(x), len(x))].mean()
        r.append(xx / yy if yy != 0 else float('nan'))
    lo, hi = ic(r)
    return OrderedDict([('rapporto', float(x.mean() / y.mean())), ('ic', [lo, hi])])


def etichetta_libro(rb, base_media, base_es):
    """sparisce / cala in parte / resta / cresce; 'non leggibile' se il tratto del libro senza intervento non e' sopra due errori."""
    if rb is None or base_media is None or base_es is None or abs(base_media) < 2 * base_es:
        return 'non leggibile'
    lo, hi = rb['ic']
    if hi <= 0.5:
        return 'sparisce'
    if lo >= 1.25:
        return 'cresce'
    if lo >= 0.8 and hi <= 1.25:
        return 'resta'
    return 'cala in parte'


# ---------------------------------------------------------------- analisi completa

def analisi(M, corse, versioni):
    import ia07_voynich_neurale as I7
    import imitatore_misure as MS
    o = OrderedDict([('esperimento', 'ia30'), ('solo_controlli', M.SOLO_CONTROLLI), ('versioni', versioni)])
    if os.path.exists(M.CALIB30):
        o['calibrazione'] = json.load(open(M.CALIB30, encoding='utf-8'))
    gruppi = carica_A(M.MISURE30)
    errori = [c for c in corse if c.get('errore')]
    o['errori'] = [OrderedDict([('lavoro', c['lavoro']), ('errore', c['errore'])]) for c in errori]
    # ---- modelli veri
    reale = OrderedDict()
    for tipo in M.TIPI30:
        jobs = gruppi.get(('reale', tipo), [])
        if not jobs:
            continue
        unita = unita_da_jobs(jobs)
        st = stima_unita(unita, seme=3000 + len(jobs))
        mp = mappa(st)
        ut = unita_da_jobs(jobs, 'testa')
        testa = OrderedDict()
        if ut:
            stt = _stima_testa(ut)
            testa = stt
        reale[tipo] = OrderedDict([('modelli', len(jobs)), ('pagine', len(unita)), ('mappa', _senza_campioni(mp)), ('testa_pagina', testa), ('patch', analisi_patch(jobs)),
                                   ('punti', _somma_punti(jobs))])
    o['modelli_veri'] = reale
    # ---- controlli
    controlli = OrderedDict()
    for tipo in M.TIPI30:
        semi = sorted((d['k'], d) for d in gruppi.get(('ec', tipo), []) for _ in [0])
        mappe = []
        for k, d in semi:
            st = stima_unita(unita_da_jobs([d]), seme=4000 + k)
            mappe.append(mappa(st))
        if mappe:
            valid = valida_controllo(mappe)
            sen = []
            for k, d in sorted((d['k'], d) for d in gruppi.get(('senza', tipo), [])):
                sen.append(mappa(stima_unita(unita_da_jobs([d]), seme=5000 + k)))
            controlli[tipo] = OrderedDict([('semi', len(mappe)), ('validazione', valid), ('senza', controllo_senza(sen, mappe) if sen else None),
                                           ('patch', analisi_patch([d for _, d in semi])), ('mappe_semi', [_senza_campioni(m) for m in mappe])])
    o['controlli'] = controlli
    for tipo, c in controlli.items():
        if tipo in reale:
            for nome in reale[tipo]['mappa']:
                for t, e in reale[tipo]['mappa'][nome].items():
                    if t.startswith('_'):
                        continue
                    chiave = '%s|%s' % (nome, t)
                    v = c['validazione'].get(chiave)
                    e['validata'] = None if v is None else bool(v['validata'])
    # ---- libri
    leggere, pesanti, dd = tabella_libri(corse, M)
    D_libri = {}
    dd_reali = {f: r for f, r in dd.items() if not isinstance(f, tuple)}
    if dd_reali and len(dd_reali) == M.PIEGHE:
        nomi = set()
        for f, r in dd_reali.items():
            nomi |= set(r['D'].keys())
        for n in nomi:
            if n == 'vere':
                continue
            D_libri[n] = MS.D_da_pieghe([dd_reali[f]['D'][n] for f in sorted(dd_reali)])
        if 'vere' in nomi:
            o['D_vero'] = MS.D_da_pieghe([dd_reali[f]['D']['vere'] for f in sorted(dd_reali)])
    D_ctrl = OrderedDict()
    for key, r in dd.items():
        if isinstance(key, tuple):
            for n, v in r['D'].items():
                val = MS.D_da_pieghe([v])
                if n == 'vere':
                    D_ctrl.setdefault('piantato', []).append(val)
                else:
                    D_libri[n] = val
    if D_ctrl:
        o['D_testo_piantato'] = D_ctrl
    libri = OrderedDict()
    for (fonte, tipo, cond), lib in sorted(leggere.items()):
        for i, c in sorted(lib.items()):
            nome = M.nome_libro(fonte, tipo, cond, i)
            v = valori_libro(c, pesanti.get(nome), D_libri.get(nome))
            libri.setdefault(fonte, OrderedDict()).setdefault(tipo, OrderedDict()).setdefault(cond, OrderedDict())[i] = v
    sintesi_libri = OrderedDict()
    for fonte, per_tipo in libri.items():
        for tipo, per_cond in per_tipo.items():
            base = per_cond.get('base')
            if not base:
                continue
            tratti = sorted({t for v in base.values() for t in v})
            tabella = OrderedDict()
            for cond, lib in per_cond.items():
                riga = OrderedDict()
                for t in tratti:
                    x = [v.get(t) for v in lib.values()]
                    y = [v.get(t) for v in base.values()]
                    xs = [a for a in x if a is not None and a == a]
                    ys = [a for a in y if a is not None and a == a]
                    if not xs or not ys:
                        continue
                    rb = rapporto_boot(xs, ys) if cond != 'base' else None
                    bm = float(np.mean(ys))
                    be = float(np.std(ys, ddof=1) / math.sqrt(len(ys))) if len(ys) > 1 else None
                    riga[t] = OrderedDict([('media', float(np.mean(xs))), ('es', float(np.std(xs, ddof=1) / math.sqrt(len(xs))) if len(xs) > 1 else None), ('libri', len(xs)),
                                           ('rapporto', rb), ('etichetta', None if cond == 'base' else etichetta_libro(rb, bm, be))])
                tabella[cond] = riga
            sintesi_libri.setdefault(fonte, OrderedDict())[tipo] = tabella
    o['libri'] = sintesi_libri
    o['integrita_nul'] = _integrita_nul(M)
    o['letture'] = letture(o, M)
    os.makedirs(M.USCITA, exist_ok=True)
    percorso = os.path.join(M.USCITA, 'ia30_interventi_causali.json')
    json.dump(o, open(percorso, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, default=float)
    with open(os.path.join(M.USCITA, 'ia30_interventi_causali.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(scrivi_md(o))
    o['percorso'] = percorso
    return o


def _somma_punti(jobs):
    c = Counter()
    for d in jobs:
        for k, v in d.get('punti', {}).items():
            c[k] += v
    return dict(c)


def _senza_campioni(mp):
    return OrderedDict((n, OrderedDict((t, (OrderedDict((k, v) for k, v in e.items() if k != 'campioni') if isinstance(e, dict) else e)) for t, e in d.items())) for n, d in mp.items())


def _stima_testa(ut):
    """Interventi sulla testa di pagina: per intervento e fascia di distanza dall'inizio (parole 0-9, 10-39, 40-99, 100+): perdita media (bit) e KL."""
    nomi = sorted({n for u in ut.values() for n in u})
    out = OrderedDict()
    for nome in nomi:
        tot = None
        for u in ut.values():
            if nome in u:
                S, N, U = u[nome]
                tot = (S.copy(), N.copy()) if tot is None else (tot[0] + S, tot[1] + N)
        S, N = tot
        out[nome] = OrderedDict([('perdita_per_fascia', [(-_div(S[:, b, 2].sum(), N[:, b].sum())) for b in range(S.shape[1])]),
                                 ('kl_per_fascia', [_div(S[:, b, 0].sum(), N[:, b].sum()) for b in range(S.shape[1])]), ('parole_per_fascia', [float(N[:, b].sum()) for b in range(S.shape[1])])])
    return out


def _integrita_nul(M):
    """Prova di integrita': il libro con l'intervento nullo e' identico al libro senza intervento (stesso seme)."""
    out = OrderedDict()
    for tipo in M.TIPI30:
        for fonte in ('reale', 'ec'):
            a, b = M.percorso_libro(fonte, tipo, 'base', 1), M.percorso_libro(fonte, tipo, 'nul', 1)
            if os.path.exists(a) and os.path.exists(b):
                ta, tb = open(a, encoding='utf-8').read().split('\n'), open(b, encoding='utf-8').read().split('\n')
                # la prima riga e' un titolo che nomina la condizione: si confronta il resto
                out['%s|%s' % (fonte, tipo)] = ta[1:] == tb[1:]
    return out


# ---------------------------------------------------------------- letture preregistrate

def letture(o, M):
    """L1-L6 (vedi la preregistrazione). Ogni lettura: per coppia, etichetta del vero e se e' validata dal controllo."""
    out = OrderedDict()
    mv = o.get('modelli_veri', {})
    ctl = o.get('controlli', {})

    def get(tipo, nome, tratto):
        e = mv.get(tipo, {}).get('mappa', {}).get(nome, {}).get(tratto)
        if e is None:
            return None
        v = e.get('validata')
        return OrderedDict([('etichetta', e['etichetta'] if v else 'lettura non valida' if v is False else e['etichetta'] + ' (nessun controllo)'),
                            ('etichetta_grezza', e['etichetta']), ('rapporto', e.get('rapporto')), ('ic_rapporto', e.get('ic_rapporto')), ('punto', e['punto']), ('validata', v)])
    coppie = OrderedDict([
        ('L1_contatto', [(n, 'kl_primo') for n in ('u1', 'u2', 'p2', 'p1', 'pw', 'w2', 'rc')]),
        ('L2_eco', [(n, 'eco_sopra') for n in ('rs_m', 'rs_p', 'rs_a', 'rl')] + [(n, 'pc') for n in ('rs_m', 'rs_p', 'rs_a')]),
        ('L3_bordi', [(n, 'term') for n in ('hN', 'hT', 'hR')] + [(n, 'kl_primo') for n in ('hN', 'hT', 'hR', 'rs_a')])])
    for nome, cp in coppie.items():
        out[nome] = OrderedDict((tipo, OrderedDict(('%s|%s' % c, get(tipo, c[0], c[1])) for c in cp)) for tipo in mv)
    # L1b: il contatto sta nelle ultime due lettere? (u2 rispetto a pw, e p1/p2 rispetto a u2)
    suff = OrderedDict()
    for tipo in mv:
        m = mv[tipo]['mappa']
        u2, pw, p1 = (m.get(n, {}).get('kl_primo') for n in ('u2', 'pw', 'p1'))
        if u2 and pw and u2.get('rapporto') is not None:
            suff[tipo] = OrderedDict([('u2_su_pw', u2['rapporto']), ('ic', u2['ic_rapporto']), ('p1_su_pw', None if not p1 else p1.get('rapporto')),
                                      ('lettura', 'sufficienti le ultime due lettere' if u2['ic_rapporto'][0] >= 0.8 else 'non sufficienti' if u2['ic_rapporto'][1] < 0.8 else 'zona grigia')])
    out['L1b_sufficienza_ultime_due'] = suff
    # L4: ordine delle famiglie (D): libri sotto interventi sulla parola prima, e il controllo `ord`
    L4 = OrderedDict()
    for fonte, nome in (('reale', 'reale'), ('ord', 'controllo ord')):
        for tipo, tab in o.get('libri', {}).get(fonte, {}).items():
            L4['%s|%s' % (nome, tipo)] = OrderedDict((cond, (riga['D']['etichetta'] if 'D' in riga else None)) for cond, riga in tab.items() if cond != 'base')
    out['L4_ordine_famiglie'] = L4
    # L5: dove (relativo al controllo)
    dove = OrderedDict()
    for tipo, d in mv.items():
        p = d.get('patch', {})
        pc = ctl.get(tipo, {}).get('patch', {})
        for nome in p:
            k, kc = p[nome].get('_k70_top'), pc.get(nome, {}).get('_k70_top')
            if k is None and kc is None:
                lett = 'mai 70% (come il controllo)' if nome in pc else 'mai 70% (nessun controllo)'
            elif kc is None:
                lett = 'nessun controllo' if nome not in pc else "più concentrata del controllo (che non arriva al 70%)"
            elif k is None:
                lett = 'più sparsa del controllo'
            else:
                lett = 'più concentrata del controllo' if k <= kc / 2 else 'più sparsa del controllo' if k >= kc * 2 else 'come il controllo'
            dove['%s|%s' % (tipo, nome)] = OrderedDict([('y2_f0', p[nome].get('y2', {}).get('f0')), ('y1_f0', p[nome].get('y1', {}).get('f0')), ('y2_fw', p[nome].get('y2', {}).get('fw')),
                                                       ('y1_fw', p[nome].get('y1', {}).get('fw')), ('k70_dimensioni', k), ('k70_controllo', kc),
                                                       ('k70_dimensioni_a_caso', p[nome].get('_k70_rnd')), ('lettura', lett)])
    out['L5_dove'] = dove
    out['L6_libri'] = 'vedi la tabella dei libri'
    return out


# ---------------------------------------------------------------- relazione

def mf(x, d=3):
    return '—' if x is None or (isinstance(x, float) and x != x) else ('%.*f' % (d, x))


def scrivi_md(o):
    L = []
    L.append('# ia30 — gli interventi causali dentro un imitatore\n')
    L.append('Solo numeri e aggregati. Effetti in bit (piu\' alto = l\'intervento fa perdere piu\' previsione). Vale per l\'IMITATORE; per il Voynich e\' un indizio indiretto.\n')
    if o.get('solo_controlli'):
        L.append('**PROVA DEL CODICE su testi non Voynich: i numeri non si leggono.**\n')
    if o.get('errori'):
        L.append('## Lavori falliti\n')
        for e in o['errori']:
            L.append('- %s: %s' % (e['lavoro'], e['errore']))
        L.append('')
    cal = o.get('calibrazione')
    if cal:
        L.append('## Taratura delle regole piantate\n')
        L.append('| regola | probabilita\' | misura ottenuta | bersaglio (vero) |\n|---|---|---|---|')
        mo, bs = cal['misura_ottenuta'], cal['bersagli']
        for r, p, m_ in (('contatto', 'contatto', 'contatto'), ('eco', 'eco', 'copia_netta'), ('bordi inizio', 'bordi_in', 'bordi_inizio_primo'), ('bordi fine', 'bordi_fi', 'bordi_fine_ultimo')):
            L.append('| %s | %s | %s | %s |' % (r, mf(cal[p], 4), mf(mo[m_], 4), mf(bs[m_], 4)))
        L.append('')
    for tipo, d in o.get('modelli_veri', {}).items():
        L.append('## Modello %s: mappa "intervento -> tratto"\n' % tipo)
        L.append('%d modelli, %d pagine. Per ogni cella: effetto (intervallo al 95%%), rapporto con l\'ancora, etichetta; "V" = coppia validata dal controllo positivo.\n' % (d['modelli'], d['pagine']))
        L.append('| intervento | punti | ' + ' | '.join(TRATTI) + ' |\n|---|---|' + '---|' * len(TRATTI))
        for nome, riga in d['mappa'].items():
            celle = []
            for t in TRATTI:
                e = riga.get(t)
                if e is None:
                    celle.append('—')
                else:
                    v = '' if e.get('validata') is None else (' V' if e['validata'] else ' x')
                    celle.append('%s [%s, %s] r=%s **%s**%s' % (mf(e['punto'], 4), mf(e['ic'][0], 4), mf(e['ic'][1], 4), mf(e.get('rapporto'), 2), e['etichetta'], v))
            L.append('| %s | %s | ' % (nome, riga.get('_n')) + ' | '.join(celle) + ' |')
        L.append('')
        if d.get('testa_pagina'):
            L.append('Testa di pagina (sezione hS, mano hM, lingua hL): perdita media per fascia di distanza dall\'inizio (parole 0-9, 10-39, 40-99, 100+)\n')
            for nome, e in d['testa_pagina'].items():
                L.append('- %s: perdita %s; KL del primo glifo %s' % (nome, ', '.join(mf(x, 4) for x in e['perdita_per_fascia']), ', '.join(mf(x, 4) for x in e['kl_per_fascia'])))
            L.append('')
        if d.get('patch'):
            L.append('Scambio parziale di stati (f0 = quota del cambio del primo glifo che passa; fw = quota del cambio delle parole): media sui modelli\n')
            for nome, pv in d['patch'].items():
                L.append('- **%s**: tutto f0 %s fw %s; solo secondo strato f0 %s fw %s; solo primo strato f0 %s fw %s; k70 dimensioni %s (a caso %s)' % (
                    nome, mf(pv.get('tutto', {}).get('f0')), mf(pv.get('tutto', {}).get('fw')), mf(pv.get('y2', {}).get('f0')), mf(pv.get('y2', {}).get('fw')),
                    mf(pv.get('y1', {}).get('f0')), mf(pv.get('y1', {}).get('fw')), pv.get('_k70_top'), pv.get('_k70_rnd')))
                L.append('  - k dimensioni (f0): ' + '; '.join('%d: %s (a caso %s)' % (k, mf(pv.get('top%d' % k, {}).get('f0'), 2), mf(pv.get('rnd%d' % k, {}).get('f0'), 2)) for k in (1, 2, 4, 8, 16, 32, 64, 128)))
            L.append('')
    if o.get('controlli'):
        L.append('## Controlli positivi (testo sintetico a regole note, alla forza del vero) e negativi\n')
        for tipo, c in o['controlli'].items():
            L.append('### %s (%d semi)\n' % (tipo, c['semi']))
            L.append('| coppia | verita\' piantata | etichette nei semi | giuste | validata |\n|---|---|---|---|---|')
            for k, v in c['validazione'].items():
                L.append('| %s | %s | %s | %d/%d | %s |' % (k, v['verita'], ', '.join(v['etichette']), v['giuste'], v['semi'], 'si' if v['validata'] else 'NO'))
            if c.get('senza'):
                L.append('\nModelli senza regola piantata (le coppie causali per costruzione in `ec` non devono risultare causali): ' + '; '.join(
                    '%s: senza regola %s (rapporti %s), con regola %s: %s' % (k_, ', '.join(e['etichette_senza']), [mf(x, 2) for x in e['rapporti_senza']], ', '.join(e['etichette_ec']),
                                                                           'riuscito' if e['riuscito'] else 'NON riuscito')
                    for k_, e in c['senza'].items()))
            L.append('')
    if o.get('integrita_nul'):
        L.append('## Integrita\': libro con intervento nullo = libro senza intervento\n')
        for k, v in o['integrita_nul'].items():
            L.append('- %s: %s' % (k, 'identico' if v else 'DIVERSO'))
        L.append('')
    for fonte, per_tipo in o.get('libri', {}).items():
        for tipo, tab in per_tipo.items():
            L.append('## Libri scritti sotto intervento (%s, %s): quali tratti spariscono e quali restano\n' % (fonte, tipo))
            tratti = list(next(iter(tab.values())).keys())
            L.append('| condizione | ' + ' | '.join(tratti) + ' |\n|---|' + '---|' * len(tratti))
            for cond, riga in tab.items():
                cel = []
                for t in tratti:
                    e = riga.get(t)
                    if e is None:
                        cel.append('—')
                    elif cond == 'base':
                        cel.append(mf(e['media'], 4))
                    else:
                        cel.append('%s (r=%s) %s' % (mf(e['media'], 4), mf(e['rapporto']['rapporto'], 2) if e.get('rapporto') else '—', e['etichetta']))
                L.append('| %s | ' % cond + ' | '.join(cel) + ' |')
            L.append('')
    L.append('## Letture preregistrate\n')
    for k, v in o.get('letture', {}).items():
        L.append('### %s\n' % k)
        if isinstance(v, dict):
            for tipo, d in v.items():
                if isinstance(d, dict):
                    L.append('- %s: %s' % (tipo, '; '.join('%s = %s' % (c, (e['etichetta'] if isinstance(e, dict) and 'etichetta' in e else e)) for c, e in d.items())))
                else:
                    L.append('- %s: %s' % (tipo, d))
        else:
            L.append(str(v))
        L.append('')
    return '\n'.join(L) + '\n'
