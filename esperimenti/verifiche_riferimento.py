# -*- coding: utf-8 -*-
"""IA25, parte 1 (modulo di supporto): la copia netta di ia09 con un riferimento "della stessa sezione" invece di "una pagina a caso".

Domanda: quanta parte della "copia" (copia netta, quota di copia rho, quota locale Λ) e' solo vocabolario di sezione, di lingua A/B, di mano
o di fascicolo? In ia09 la copia netta e' il guadagno dato dalle parole gia' scritte sulla pagina MENO quello dato dalle parole di un'altra
pagina scelta a caso. Nel Voynich una pagina a caso e' spesso di un'altra lingua o sezione. Qui il riferimento e' scelto in altri tre modi
(`verifiche_comune.RIF_NOMI`) e la misura si rifa (sempre con le funzioni di ia09, ia20: nessuna e' modificata).

Che cosa c'e' qui
- `rows_testo`: il libro da misurare (vero, v21, M1, M5, E2, testi di controllo costruiti qui);
- `testo_controllo`: due testi sintetici sul libro vero (stesse pagine, stesse righe, stesse lunghezze):
    'sez' = vocabolario di sezione e nessuna copia di pagina (ogni parola e' pescata dalle parole delle ALTRE pagine dello stesso gruppo
            sezione-lingua-mano), 'pag' = copia di pagina vera (il 10% delle parole da un piccolo lessico proprio della pagina, il resto dal
            vocabolario del gruppo);
- `lavoro_rif`: un testo, tutti i riferimenti: copia netta, Λ, rho, contatto e la "quota di sezione" = 1 - copia netta(rif) / copia netta(pagina a caso);
- `analisi`: tabelle, controlli e letture preregistrate.
Solo numeri e aggregati: nessuna parola ne' riga di testo.
"""
import random
import time
from collections import Counter, OrderedDict, defaultdict

import numpy as np

import verifiche_comune as C

I7, A9, MS = C.I7, C.A9, C.MS
I20_SOGLIA = C.I20.SOGLIA_ERRORI

SOGLIE = OrderedDict([
    ('ctrl_sez_min_N0', 0.03),            # testo 'sez': copia netta con la pagina a caso almeno questa (la copia finta si vede)
    ('ctrl_sez_min_quota', 0.30),         # testo 'sez': il riferimento di sezione ne toglie almeno questa quota
    ('ctrl_pag_min_N1', 0.03),            # testo 'pag': con il riferimento di sezione resta almeno questa copia netta
    ('ctrl_pag_max_quota', 0.25),         # testo 'pag': il riferimento di sezione ne toglie al massimo questa quota (con la pagina propria piu' lunga del riferimento un po' se ne perde sempre)
    ('separazione_min', 0.20),            # le due quote dei controlli devono distare almeno questo (altrimenti lo strumento non distingue)
    ('quota_molta', 0.60),                # quota di sezione CALIBRATA (0 = come il testo 'pag', 1 = come il testo 'sez') almeno questa: soprattutto vocabolario di sezione
    ('quota_poca', 0.25),                 # al massimo questa: soprattutto copia di pagina
    ('riproduzione_tol', 1e-4)])          # la copia netta con riferimento '0' deve ritrovare i valori di ia20/ia22 (solo sul Voynich)


P_PAGINA = 0.10                          # testo 'pag': quota di parole che vengono dal piccolo lessico della pagina (30 parole)


def rows_testo(nome):
    if nome.startswith('sint:'):
        return testo_controllo(nome.split(':')[1])
    return C.rows_libro(nome)


def testo_controllo(tipo):
    """Testo sintetico sul libro vero (vedi la descrizione del modulo). Semi fissi. Il vocabolario di un gruppo e' lo stesso per tutte le sue pagine (le parole del
    gruppo, con le loro frequenze); i gruppi con meno di 10 pagine usano il vocabolario di tutto il libro."""
    c = I7.contesto_A()
    vere = c['vere']
    meta = C.meta_pagine()
    gruppo = lambda p: (meta[p]['sez'], meta[p]['lingua'], meta[p]['mano'])        # noqa: E731
    per_gruppo = defaultdict(list)
    for p in vere:
        per_gruppo[gruppo(p)].append(p)
    tutte = [w for rows in vere.values() for _, ws in rows for w in ws]
    lex_g = {g: [w for q in ps for _, ws in vere[q] for w in ws] if len(ps) >= 10 else tutte for g, ps in per_gruppo.items()}
    rnd = random.Random(C.seme_str('ia25ctrl', tipo))
    out = OrderedDict()
    for p, rows in vere.items():
        lex = lex_g[gruppo(p)]
        if tipo == 'pag':
            propri = [rnd.choice(lex) for _ in range(30)]
        nr = []
        for ini, ws in rows:
            nw = []
            for _ in ws:
                if tipo == 'pag' and rnd.random() < P_PAGINA:
                    nw.append(rnd.choice(propri))
                else:
                    nw.append(rnd.choice(lex))
            nr.append((ini, nw))
        out[p] = nr
    return out


def lavoro_rif(nome, refs):
    inizio = time.time()
    rows = rows_testo(nome)
    ris = OrderedDict([('lavoro', 'rif|%s' % nome), ('nome', nome), ('riferimenti', OrderedDict())])
    stime = OrderedDict()
    for rif in refs:
        info = {}
        r = C.struttura_M(nome, rows, rif, info)
        s = C.stime_M(r)
        stime[rif] = s
        ris['riferimenti'][rif] = OrderedDict(
            copia_netta=s['netto'].p, copia_netta_ic=s['netto'].ic(), lam=s['lam'].p, lam_ic=s['lam'].ic(), rho=s['rho'].p, rho_ic=s['rho'].ic(),
            contatto=s['contatto'], pagine=s['pagine'], ripiego=info.get('ripiego', 0.0))
    if '0' in stime:
        for rif in refs:
            if rif == '0':
                continue
            q = A9.V(1.0, np.ones_like(stime[rif]['netto'].b)) - stime[rif]['netto'].dividi(stime['0']['netto'])
            ris['riferimenti'][rif]['quota_di_sezione'] = q.p
            ris['riferimenti'][rif]['quota_di_sezione_ic'] = q.ic()
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


# ---------------------------------------------------------------- analisi

def tipo_di(nome):
    return nome.split(':')[0]


def analisi(corse, refs, n_libri, riferimento_json=None):
    """corse: lavoro -> risultato. Tabella per tipo e riferimento, quota di sezione, letture L1.1-L1.3 e controlli."""
    R = {c['nome']: c for c in corse.values() if c['lavoro'].startswith('rif|')}
    tipi = OrderedDict()
    for n in R:
        if not n.startswith('sint:'):
            tipi.setdefault(tipo_di(n), []).append(n)
    tab = OrderedDict()
    for t, nomi in tipi.items():
        tab[t] = OrderedDict()
        for rif in refs:
            xs = [R[n]['riferimenti'][rif] for n in nomi if rif in R[n]['riferimenti']]
            if not xs:
                continue
            row = OrderedDict(libri=len(xs))
            for k in ('copia_netta', 'lam', 'rho', 'contatto', 'ripiego') + (('quota_di_sezione',) if rif != '0' else ()):
                row[k] = C.mes([x.get(k) for x in xs])
            row['pagine'] = xs[0]['pagine']
            if len(xs) == 1:
                row['copia_netta_ic'], row['lam_ic'] = xs[0]['copia_netta_ic'], xs[0]['lam_ic']
                if rif != '0':
                    row['quota_ic'] = xs[0]['quota_di_sezione_ic']
            tab[t][rif] = row
    out = OrderedDict(tabella=tab, soglie=SOGLIE)
    # ---- controlli
    ctr = OrderedDict()
    cs = {n: R[n] for n in R if n.startswith('sint:')}
    cal = OrderedDict()                                      # riferimento -> (quota del testo 'pag', quota del testo 'sez')
    for rif in refs:
        if rif == '0':
            continue
        sz = cs.get('sint:sez', {}).get('riferimenti', {}).get(rif)
        pg = cs.get('sint:pag', {}).get('riferimenti', {}).get(rif)
        if not sz or not pg:
            continue
        s0, p0 = cs['sint:sez']['riferimenti']['0'], cs['sint:pag']['riferimenti']['0']
        qs, qp = sz['quota_di_sezione'], pg['quota_di_sezione']
        cal[rif] = (qp, qs)
        ctr['positivo_vocabolario_di_sezione_rif%s' % rif] = OrderedDict(N0=s0['copia_netta'], N1=sz['copia_netta'], quota=qs,
                                                                          soglie=[SOGLIE['ctrl_sez_min_N0'], SOGLIE['ctrl_sez_min_quota']],
                                                                          riuscito=bool(s0['copia_netta'] >= SOGLIE['ctrl_sez_min_N0'] and qs >= SOGLIE['ctrl_sez_min_quota']))
        ctr['negativo_copia_di_pagina_vera_rif%s' % rif] = OrderedDict(N0=p0['copia_netta'], N1=pg['copia_netta'], quota=qp,
                                                                        soglie=[SOGLIE['ctrl_pag_min_N1'], SOGLIE['ctrl_pag_max_quota']],
                                                                        riuscito=bool(pg['copia_netta'] >= SOGLIE['ctrl_pag_min_N1'] and qp <= SOGLIE['ctrl_pag_max_quota']))
        ctr['separazione_rif%s' % rif] = OrderedDict(differenza_fra_le_quote=qs - qp, soglia=SOGLIE['separazione_min'], riuscito=bool(qs - qp >= SOGLIE['separazione_min']))
    if riferimento_json and not C.SOLO_CONTROLLI:
        rip = OrderedDict()
        for t, chiave in (('M1', 'M1'), ('M5', 'M5'), ('V21', 'V21')):
            if t in tab and '0' in tab[t] and chiave in riferimento_json['ia20']['struttura']:
                a = tab[t]['0']['copia_netta'][0]
                b = riferimento_json['ia20']['struttura'][chiave]['copia_netta'][0]
                rip[t] = OrderedDict(qui=a, ia20=b, uguale=bool(a is not None and abs(a - b) <= SOGLIE['riproduzione_tol']))
        if 'E2' in tab and '0' in tab['E2']:
            a = tab['E2']['0']['copia_netta'][0]
            b = riferimento_json['ia22']['struttura']['E2']['copia_netta'][0]
            rip['E2'] = OrderedDict(qui=a, ia22=b, uguale=bool(a is not None and abs(a - b) <= SOGLIE['riproduzione_tol']))
        if 'vere' in tab and '0' in tab['vere']:
            a = tab['vere']['0']['copia_netta'][0]
            b = riferimento_json['ia20']['vero']['copia_netta']
            rip['vere'] = OrderedDict(qui=a, ia20=b, uguale=bool(a is not None and abs(a - b) <= SOGLIE['riproduzione_tol']))
        ctr['riproduzione_ia20_ia22'] = OrderedDict(dettaglio=rip, riuscito=bool(rip) and all(v['uguale'] for v in rip.values()))
    out['controlli'] = ctr
    out['letture_valide'] = bool(ctr) and all(v['riuscito'] for v in ctr.values())
    out['calibrazione'] = OrderedDict((k, OrderedDict(quota_testo_pag=a, quota_testo_sez=b)) for k, (a, b) in cal.items())

    def calibrata(q, rif):
        if q is None or rif not in cal or cal[rif][1] == cal[rif][0]:
            return None
        return (q - cal[rif][0]) / (cal[rif][1] - cal[rif][0])
    # ---- letture
    L = OrderedDict()
    v = tab.get('vere', {})
    for rif in refs:
        if rif == '0' or rif not in v:
            continue
        q = v[rif].get('quota_di_sezione', (None, None))[0]
        ic = v[rif].get('quota_ic')
        qc = calibrata(q, rif)
        icc = [calibrata(x, rif) for x in ic] if ic else None
        esito = None if qc is None else ('soprattutto vocabolario di sezione' if qc >= SOGLIE['quota_molta'] else
                                         'soprattutto copia di pagina' if qc <= SOGLIE['quota_poca'] else 'in parte vocabolario di sezione')
        L['L1_%s' % rif] = OrderedDict(riferimento=C.RIF_NOMI[rif], quota_di_sezione=q, ic=ic, quota_calibrata=qc, ic_calibrata=icc,
                                       copia_netta=[v['0']['copia_netta'][0], v[rif]['copia_netta'][0]], lam=[v['0']['lam'][0], v[rif]['lam'][0]],
                                       rho=[v['0']['rho'][0], v[rif]['rho'][0]], esito=esito)
    # confronto del vero con gli altri testi: stessa lettura "al vero" con i due riferimenti
    cambi = OrderedDict()
    for t in tab:
        if t == 'vere':
            continue
        for rif in refs:
            if rif not in tab[t] or rif not in v:
                continue
            for k, vv in (('copia_netta', v[rif]['copia_netta'][0]), ('lam', v[rif]['lam'][0]), ('contatto', v[rif]['contatto'][0])):
                m, e = tab[t][rif][k]
                cambi.setdefault(t, OrderedDict()).setdefault(rif, OrderedDict())[k] = OrderedDict(
                    media=m, errore=e, vero=vv, al_vero=C.classe_vero(m, e, vv), distanza_relativa=(abs(m - vv) / abs(vv) if m is not None and vv else None))
    L['L2_al_vero_per_riferimento'] = cambi
    mutati = []
    for t, d in cambi.items():
        for k in ('copia_netta', 'lam', 'contatto'):
            if '0' in d and any(r in d for r in refs if r != '0'):
                a = d['0'][k]['al_vero']
                for r in refs:
                    if r != '0' and r in d and d[r][k]['al_vero'] != a:
                        mutati.append('%s %s: al vero con pagina a caso %s, con riferimento %s %s' % (t, k, nu_b(a), r, nu_b(d[r][k]['al_vero'])))
    L['L2_verdetti_cambiati'] = mutati
    qs = OrderedDict()
    for t in tab:
        if t == 'vere':
            continue
        for rif in refs:
            if rif != '0' and rif in tab[t] and rif in v and 'quota_di_sezione' in tab[t][rif]:
                m, e = tab[t][rif]['quota_di_sezione']
                qv = v[rif].get('quota_di_sezione', (None, None))[0]
                qs.setdefault(t, OrderedDict())[rif] = OrderedDict(quota=m, errore=e, calibrata=calibrata(m, rif), vero=qv, differenza=(m - qv) if m is not None and qv is not None else None,
                                                                    differisce_dal_vero=bool(m is not None and qv is not None and abs(m - qv) > I20_SOGLIA * (e or 0.0)))
    L['L3_quota_di_sezione_degli_altri_testi'] = qs
    out['letture'] = L
    return out


def nu_b(x):
    return 'sì' if x else 'no' if x is not None else '—'


def scrivi_md(o, refs):
    r = ['## Parte 1: copia netta con un riferimento di sezione', '',
         'Domanda: quanta parte della "copia" (copia netta di ia09, rho, Λ) e\' vocabolario di sezione, lingua e mano o fascicolo? Riferimenti: %s.' %
         '; '.join('%s = %s' % (k, C.RIF_NOMI[k]) for k in refs), '']
    for t, d in o['tabella'].items():
        r += ['### %s' % t, '']
        righe = []
        for rif, x in d.items():
            righe.append([rif, x['libri'], C.fmt_mes(x['copia_netta']), C.fmt_mes(x['lam']), C.fmt_mes(x['rho']), C.fmt_mes(x['contatto']),
                          C.fmt_mes(x.get('quota_di_sezione')) if rif != '0' else '—', C.fmt_mes(x['ripiego'], 2)])
        r += C.tabella_md(['rif', 'libri', 'copia netta', 'Λ', 'rho', 'contatto', 'quota di sezione', 'pagine con ripiego'], righe) + ['']
    r += ['### Controlli', '']
    for k, v in o['controlli'].items():
        r.append('- %s: %s' % (k, v))
    r += ['', 'Letture valide: %s' % nu_b(o['letture_valide']), '', '### Letture', '']
    for k, v in o['letture'].items():
        r.append('- %s: %s' % (k, v))
    return r
