# -*- coding: utf-8 -*-
"""IA25, parte 2 (modulo di supporto): il v21 e il "Naibbe vero + eco leggera" nella metrica di distanza di ia14/ia19, e la scomposizione della distanza.

Perche': la revisione dice che (1) il Naibbe VERO ha k90 1,72 in ia14 (il contesto corto si raggiunge), (2) il Naibbe vero senza eco sta gia' a distanza
2,05-2,12, come la migliore combinazione di ia19 (che aveva messo l'eco su un verboso SEMPLIFICATO scritto in casa), (3) la distanza e' dominata da una sola
misura (Λ pesa il 78% della distanza al quadrato per il Naibbe), (4) il v21 non e' mai stato messo in questa metrica.

Che cosa c'e' qui
- due tipi di testo nuovi per il codice di ia14 (`pagine_di25`, agganciato a `ia14.pagine_di` come fa ia19): 'v21' (un libro v21 senza messaggio di ia01,
  nelle sue pagine) e 'naibbe_eco' (le parole del Naibbe VERO, `e3c95.naibbe()`, nell'impaginazione del Voynich, con la quota p di parole nulle d'eco fatte
  con la STESSA funzione di ia19 (`combinati_procedimenti.tessi_eco`: meta' riprese dal tema della pagina, meta' varianti locali). p = 0 (controllo: nessuna
  eco), 0,02, 0,05, 0,10: gli stessi tre valori di VE di ia19, fissati prima);
- `descrittori25`, `lavori25`: i lavori di rete (R: ia02, K: ia03) e di sintassi (S9: ia09, S10: ia10) di ia14, uno per testo e istanza;
- `analisi`: per ogni cella di ia14, ia19 e di questa parte: profilo medio, distanza (stessa scala e stesso raggio di ia14), scomposizione della distanza al
  quadrato per misura, distanza senza Λ (scala e raggio ricalcolati sulle altre otto misure), classe, firme raggiunte; letture e controlli.
Le misure delle celle di ia14 e ia19 non si ricalcolano: si leggono da `risultati/ia14_corse.jsonl` e `ia19_corse.jsonl`.
"""
import json
import math
import os
import random
import statistics
from collections import OrderedDict

import verifiche_comune as C

import ia14_quale_cifrario as I14  # noqa: E402
import ia19_procedimenti_combinati as I19  # noqa: E402

I7 = C.I7
CP, CB, e95, TT = I14.CP, I19.CB, I14.e95, I14.TT
I14.I10.CACHE = os.path.join(C.CACHE25, 'uscite')          # le liste di parole per famiglia di ia10 vanno solo nella cartella protetta di IA25
ISTANZE25 = int(os.environ.get('ISTANZE25', 3))
P_ECO = (0.0, 0.02, 0.05, 0.10)               # 0,0 = controllo senza eco; gli altri tre sono quelli di VE di ia19
SOGLIE = OrderedDict([
    ('eco_misurabile_E', 0.03),               # E di NE(0,10) sopra NE(0): almeno 0,03 bit per parola (come ia19)
    ('controllo_costruzione_firme', 7),       # NE(0) in impaginazione deve avere almeno 7 firme su 9 entro la tolleranza di ia14 dal Naibbe nativo
    ('peso_lambda_dominante', 0.5),           # Λ "domina" una cella se pesa almeno la meta' della distanza al quadrato
    ('riproduzione_ia14', 1e-6)])             # la distanza ricalcolata deve coincidere con quella di risultati/ia14 (solo sul Voynich)
_C = {}


def chiavi_v21():
    return list(I7.CHIAVI_V21[:ISTANZE25])


def nome_ne(p, i):
    return 'NE_%s_i%d' % (str(p).replace('.', 'p'), i)


def descrittori25():
    T = OrderedDict()
    for i, k in enumerate(chiavi_v21(), 1):
        T['V21_i%d' % i] = dict(tipo='v21', istanza=i, chiave=k, cella='V21')
    for p in P_ECO:
        for i in range(1, ISTANZE25 + 1):
            T[nome_ne(p, i)] = dict(tipo='naibbe_eco', p=p, istanza=i, cella='NE_%s' % str(p).replace('.', 'p'))
    return T


def parole_naibbe():
    if 'nb' not in _C:
        _C['nb'] = [w for b in e95.naibbe() for r in b for w in r]
    return _C['nb']


def genera_naibbe_eco(p, istanza):
    """Le parole del Naibbe vero (un tratto di flusso, con partenza scelta con un seme fisso) nell'impaginazione del Voynich, con la quota p di parole nulle d'eco
    di ia19. Solo parole del Naibbe e parole d'eco costruite dal testo stesso (glifi con le frequenze del Naibbe)."""
    lay = I14.layout()
    N = sum(CP.parole_per_pagina(lay))
    rnd_eco = random.Random(CB.seme19('eco', 'NE', p, '', istanza))
    flag = [rnd_eco.random() < p for _ in range(N)] if p > 0 else [False] * N
    nbase = N - sum(flag)
    nb = parole_naibbe()
    inizio = random.Random(CP.seme_di('NE', 'inizio', istanza)).randrange(0, max(1, len(nb) - nbase))
    base = list(nb[inizio:inizio + nbase])
    while len(base) < nbase:
        base += nb[:nbase - len(base)]
    pagine, _ = CB.tessi_eco(rnd_eco, base, lay, flag)
    return pagine


if not hasattr(I14, '_pagine_di_prima_di_ia25'):
    I14._pagine_di_prima_di_ia25 = I14.pagine_di


def pagine_di25(nome, d):
    if d['tipo'] == 'v21':
        return I7.libro_riferimento_A('b', d['chiave'])
    if d['tipo'] == 'naibbe_eco':
        return genera_naibbe_eco(d['p'], d['istanza'])
    return I14._pagine_di_prima_di_ia25(nome, d)


I14.pagine_di = pagine_di25


def lavori25(descr25):
    L = []
    for nome, d in descr25.items():
        for tp in ('R', 'K'):
            L.append(dict(tipo=tp, nome=nome, seme=d['istanza'], descr=d))
        L.append(dict(tipo='S10', nome=nome, descr=d))
        L.append(dict(tipo='S9', nome=nome, descr=d))
    return L


def chiave_job(job):
    return 'cifr|%s|%s|%s' % (job['tipo'], job['nome'], job.get('seme'))


def lavoro(job):
    r = I14.lavoro(job)
    r['lavoro'] = chiave_job(job)
    return r


# ---------------------------------------------------------------- analisi

def media_profili(profili):
    return OrderedDict((k, I14.media_non_nulla([p[k] for p in profili])) for k in I14.COMPS)


def scomposizione(medio, V, scala, comps):
    zs = OrderedDict((k, ((medio[k] - V[k]) / scala[k]) if (medio.get(k) is not None and scala.get(k)) else None) for k in comps)
    q = OrderedDict((k, z * z) for k, z in zs.items() if z is not None)
    tot = sum(q.values())
    return OrderedDict((k, (v / tot if tot else None)) for k, v in q.items()), zs


def spearman(a, b):
    def rango(x):
        o = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        for k, i in enumerate(o):
            r[i] = k
        return r
    ra, rb = rango(a), rango(b)
    if len(a) < 3:
        return None
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def analisi(corse25, corse_ia14, corse_ia19, json_ia14=None):
    """corse*: liste di risultati di lavoro (formato di ia14). Restituisce un dizionario di soli numeri."""
    descr = OrderedDict(I19.descrittori_tutti())
    descr25 = descrittori25()
    descr.update(descr25)
    rif = I14.riferimenti()
    R, K, S9, S10, errori = I14.raccogli(list(corse_ia14) + list(corse_ia19) + list(corse25))
    V = rif['V']
    istanze = OrderedDict()
    for nome, d in descr.items():
        semi = [d['istanza']] if d['tipo'] in ('cella', 'cella19', 'chiaro', 'v21', 'naibbe_eco') else list(range(1, I14.ISTANZE + 1)) if d['tipo'] == 'nativo' else [None]
        for s in semi:
            p, flag = I14.profilo_istanza(nome, R, K, S9, S10, s)
            istanze[(nome, s)] = dict(profilo=p, flag=flag, descr=d)
    lingue_sint = [istanze[(n, None)]['profilo'] for n, d in descr.items() if d['tipo'] == 'lingua' and (n, None) in istanze]
    scala, raggi, tau = I14.scale_e_raggi(rif, lingue_sint)
    comps8 = [k for k in I14.COMPS if k != 'lambda']
    scala8, raggi8, tau8 = I19.scale_e_raggi_sub(rif, lingue_sint, comps8)
    eps, eps8 = raggi['epsilon'], raggi8['epsilon']
    # ---- celle (media sulle istanze) e nativi
    gruppi = OrderedDict()
    for nome, d in descr.items():
        if d['tipo'] in ('cella', 'cella19', 'chiaro', 'v21', 'naibbe_eco'):
            semi = [d['istanza']]
            etichetta = d['cella']
        elif d['tipo'] in ('nativo',):
            semi, etichetta = list(range(1, I14.ISTANZE + 1)), nome
        elif d['tipo'] in ('negativo',):
            semi, etichetta = [None], nome
        else:
            continue
        for s in semi:
            if (nome, s) in istanze and any(v is not None for v in istanze[(nome, s)]['profilo'].values()):
                gruppi.setdefault(etichetta, []).append(istanze[(nome, s)]['profilo'])
    celle = OrderedDict()
    for et, profili in gruppi.items():
        medio = media_profili(profili)
        d9, zs, nz = I14.distanza(medio, V, scala)
        d8, _, nz8 = I14.distanza(medio, V, scala8, comps8)
        quote, _ = scomposizione(medio, V, scala, I14.COMPS)
        firme = OrderedDict((k, (abs(medio[k] - V[k]) <= tau[k]) if medio[k] is not None else None) for k in I14.COMPS)
        celle[et] = OrderedDict(istanze=len(profili), medio=medio, distanza=d9, classe=I14.classe(d9, eps), distanza_senza_lambda=d8, classe_senza_lambda=I14.classe(d8, eps8),
                                z=zs, quota_della_distanza_al_quadrato=quote, peso_lambda=quote.get('lambda'), componenti=nz,
                                firme_raggiunte=sum(1 for v in firme.values() if v), firme=firme, mancate=[k for k, v in firme.items() if v is False])
    out = OrderedDict(riferimenti=OrderedDict(Voynich=V, scala=scala, scala_senza_lambda=scala8, raggio=eps, raggio_senza_lambda=eps8, tolleranza_firma=tau), soglie=SOGLIE)
    out['celle'] = celle
    # ---- controlli
    ctr = OrderedDict()
    ne0, ne10 = celle.get('NE_0p0'), celle.get('NE_0p1')
    nat = celle.get('nat_naibbe')
    if ne0 and nat:
        entro = [k for k in I14.COMPS if ne0['medio'][k] is not None and nat['medio'][k] is not None and abs(ne0['medio'][k] - nat['medio'][k]) <= tau[k]]
        ctr['costruzione_in_impaginazione'] = OrderedDict(firme_entro_la_tolleranza=len(entro), misure=entro, soglia=SOGLIE['controllo_costruzione_firme'],
                                                          riuscito=len(entro) >= SOGLIE['controllo_costruzione_firme'])
    if ne0 and ne10 and ne0['medio']['E'] is not None and ne10['medio']['E'] is not None:
        dE = ne10['medio']['E'] - ne0['medio']['E']
        ctr['eco_misurabile'] = OrderedDict(aumento_E=dE, soglia=SOGLIE['eco_misurabile_E'], riuscito=bool(dE >= SOGLIE['eco_misurabile_E']))
    if json_ia14 and not C.SOLO_CONTROLLI:
        rip = OrderedDict()
        for k, x in json_ia14['celle'].items():
            if k in celle and x.get('distanza') is not None and celle[k]['distanza'] is not None:
                rip[k] = abs(celle[k]['distanza'] - x['distanza'])
        for k, x in json_ia14['altri'].items():
            if k in celle and x.get('distanza') is not None and celle[k]['distanza'] is not None:
                rip[k] = abs(celle[k]['distanza'] - x['distanza'])
        ctr['riproduzione_distanze_ia14'] = OrderedDict(celle_confrontate=len(rip), scarto_massimo=max(rip.values()) if rip else None,
                                                        riuscito=bool(rip) and max(rip.values()) <= SOGLIE['riproduzione_ia14'])
    tn, t0 = celle.get('Tneg_i1'), celle.get('T0')
    if tn and tn['distanza'] is not None:
        ctr['negativo_testo_rimescolato'] = OrderedDict(distanza=tn['distanza'], epsilon=eps, distanza_senza_lambda=tn['distanza_senza_lambda'], epsilon_senza_lambda=eps8,
                                                        latino_in_chiaro=(t0 or {}).get('distanza'), riuscito=bool(tn['distanza'] > eps and tn['distanza_senza_lambda'] > eps8))
    out['controlli'] = ctr
    out['letture_valide'] = bool(ctr) and all(v['riuscito'] for v in ctr.values())
    # ---- letture
    L = OrderedDict()
    for et in ('V21', 'NE_0p0', 'NE_0p02', 'NE_0p05', 'NE_0p1', 'nat_naibbe'):
        if et in celle:
            c = celle[et]
            L['L2_%s' % et] = OrderedDict(distanza=c['distanza'], classe=c['classe'], distanza_senza_lambda=c['distanza_senza_lambda'], classe_senza_lambda=c['classe_senza_lambda'],
                                          peso_lambda=c['peso_lambda'], firme_raggiunte=c['firme_raggiunte'], mancate=c['mancate'],
                                          k90_raggiunto=c['firme'].get('k90'), k90=c['medio'].get('k90'))
    # le celle "semplificate" di ia14 e ia19 (esclusi nativi, lingue, controlli e le nuove)
    semplici = [et for et, c in celle.items() if et not in ('V21', 'T0', 'Tneg', 'nat_naibbe', 'nat_ts', 'nat_latino') and not et.startswith('NE_') and c['distanza'] is not None]
    if semplici:
        migliore = min(semplici, key=lambda e: celle[e]['distanza'])
        migliore8 = min(semplici, key=lambda e: celle[e]['distanza_senza_lambda'])
        pesi = [celle[e]['peso_lambda'] for e in semplici if celle[e]['peso_lambda'] is not None]
        cambi = [e for e in semplici if celle[e]['classe'] != celle[e]['classe_senza_lambda']]
        rho_s = spearman([celle[e]['distanza'] for e in semplici], [celle[e]['distanza_senza_lambda'] for e in semplici])
        L['L2_peso_di_lambda'] = OrderedDict(celle=len(semplici), mediana=statistics.median(pesi) if pesi else None,
                                             dominanti=sum(1 for x in pesi if x >= SOGLIE['peso_lambda_dominante']), naibbe_nativo=celle.get('nat_naibbe', {}).get('peso_lambda'),
                                             classe_cambia_senza_lambda=cambi, spearman_distanza_con_e_senza_lambda=rho_s, migliore_con=migliore,
                                             migliore_senza=migliore8, distanza_migliore_con=celle[migliore]['distanza'], distanza_migliore_senza=celle[migliore8]['distanza_senza_lambda'])
        nuove = [e for e in celle if e.startswith('NE_') and e != 'NE_0p0']
        L['L2_naibbe_eco_contro_le_celle_semplificate'] = OrderedDict(
            migliore_semplificata=migliore, distanza_migliore_semplificata=celle[migliore]['distanza'],
            naibbe_eco_piu_vicino_del_migliore=[e for e in nuove + ['NE_0p0'] if e in celle and celle[e]['distanza'] is not None and celle[e]['distanza'] < celle[migliore]['distanza']],
            naibbe_nativo=celle.get('nat_naibbe', {}).get('distanza'))
    raggiungono_k90 = [et for et, c in celle.items() if c['firme'].get('k90')]
    L['L2_k90_raggiunto_da'] = raggiungono_k90
    out['letture'] = L
    return out


def scrivi_md(o):
    r = ['## Parte 2: il v21 e il Naibbe vero con l\'eco nella metrica di ia14', '',
         'Domanda: nella metrica di ia14/ia19 (stessa scala e stesso raggio) dove stanno il v21 e il Naibbe vero con un\'eco leggera di pagina? Quanto pesa ogni misura '
         'nella distanza, e che cosa cambia senza Λ? Raggio epsilon: %s (senza Λ: %s).' % (C.fmt(o['riferimenti']['raggio'], 3), C.fmt(o['riferimenti']['raggio_senza_lambda'], 3)), '',
         '| cella | d (9 misure) | classe | peso di Λ | d senza Λ | classe senza Λ | firme | k90 |', '|---|---|---|---|---|---|---|---|']
    for et, c in o['celle'].items():
        r.append('| %s | %s | %s | %s | %s | %s | %s/9 | %s |' % (et, C.fmt(c['distanza'], 2), c['classe'], C.fmt(c['peso_lambda'], 2), C.fmt(c['distanza_senza_lambda'], 2), c['classe_senza_lambda'],
                                                                 c['firme_raggiunte'], C.fmt(c['medio'].get('k90'), 2)))
    r += ['', '### Controlli', ''] + ['- %s: %s' % (k, v) for k, v in o['controlli'].items()]
    r += ['', 'Letture valide: %s' % ('sì' if o['letture_valide'] else 'NO'), '', '### Letture', ''] + ['- %s: %s' % (k, v) for k, v in o['letture'].items()]
    return r
