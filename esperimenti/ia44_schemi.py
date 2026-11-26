# -*- coding: utf-8 -*-
"""Esperimento IA44 (ia44): schemi noti in anticipo, "una e una sola per pagina" (strada 2 di PROPOSTE_DECIFRARE_FABLE.md).

Tre ricerche, scritte nella preregistrazione prima di guardare il manoscritto:
  (a) erbario A e B: gruppi di 2-4 parole che, in quasi ogni pagina, compaiono "esattamente una" (le qualita' e i gradi degli erbari);
  (b) zodiaco, per segno: parole ricorrenti in 2-6 segni contro le divisioni note dei segni (elemento, modalita', pianeta);
  (c) zodiaco, per grado: le etichette dei segni contro le tavole note dei gradi (maschili/femminili, chiari/scuri, ...), su tutte
      le rotazioni e nei due versi.
Non e' una decifrazione: se qualcosa risulta, e' una regolarita' statistica (parole candidate), mai una lettura.

Fasi (un solo comando le fa tutte, in quest'ordine):
  C  controlli (SOLO testi non Voynich: v21, Naibbe, Timm e Schinner, latino cifrato, dati finti per lo zodiaco), in parallelo;
     scrivono `dati/cache/ia44/controlli.jsonl` (ripresa con RIPRENDI=1);
  G  il cancello: per ogni unita'/divisione/tavola dice se i controlli passano (positivi >= 90%, falsi allarmi <= 5%);
  V  il Voynich, SOLO per cio' che il cancello ammette, con due trascrizioni (ZL e Takahashi). Non parte se il cancello non ammette niente;
  S  `risultati/ia44_schemi.md` e `.json` (solo numeri e aggregati: mai testo della trascrizione; le parole candidate, se ci sono,
     stanno solo in `dati/cache/ia44/candidati_<trascrizione>.json`).

    nohup bash strumenti/coda.sh ia44 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia44" > /dev/null 2>&1 &

Variabili (valori senza virgole e senza due punti): CACHE44 (cartella dei lavori), LIBRI44 (libri v21 fatti qui), USCITA44 (dove scrivere
i risultati), K44 (campioni del nullo nei controlli dell'erbario, 299), KZ44 (idem per lo zodiaco, 999), KV44 (nullo dell'erbario sul
Voynich, 2999), KVZ44 (nullo dello zodiaco sul Voynich, 9999), N_PROVE44 (fattore sul numero di prove, 1; solo per le prove di codice),
FASE44 (C, G, V, S o tutto), TESTO44 (vuoto = manoscritto; 'prova' = testi di prova al posto del manoscritto, solo per provare la
fase V), SENZA_VOYNICH44 (1 = la fase V con il manoscritto rifiuta di partire: per le prove).
"""
import json
import os
import sys
import time
from collections import OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')          # un solo filo per processo: i processi in parallelo non si pestano i piedi
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, '..')
sys.path.insert(0, QUI)
import schemi_dati as D          # noqa: E402
import schemi_libri as L         # noqa: E402
import schemi_erbario as E       # noqa: E402
import schemi_controlli as C     # noqa: E402
import schemi_tavole as TV       # noqa: E402
import schemi_zodiaco as Z       # noqa: E402

NOME = 'ia44_schemi'
CACHE = os.environ.get('CACHE44', os.path.join(RADICE, 'dati', 'cache', 'ia44'))
USCITA = os.environ.get('USCITA44', os.path.join(RADICE, 'risultati'))
K = int(os.environ.get('K44', 299))
KZ = int(os.environ.get('KZ44', 999))
KV = int(os.environ.get('KV44', 2999))
KVZ = int(os.environ.get('KVZ44', 9999))
SCALA = float(os.environ.get('N_PROVE44', 1))
FASE = os.environ.get('FASE44', 'tutto')
TESTO = os.environ.get('TESTO44', '')
PROCESSI = int(os.environ.get('PROCESSI', 8))
RIPRENDI = os.environ.get('RIPRENDI') == '1'

# ---- soglie scritte nella preregistrazione prima di ogni numero
ALFA = 1 / 300                  # 0,01 diviso le tre ricerche; con 299 campioni del nullo il p piu' piccolo e' proprio 1/300
ALFA_T = ALFA * (1 + 1e-9)       # tolleranza di arrotondamento nel confronto p <= ALFA
POSITIVI_MIN = 0.90             # quota di prove positive viste perche' una unita'/divisione/tavola entri
FALSI_ALLARMI_MAX = 0.05
NPC_CANCELLO = 20               # (b): parole piantate per classe nel positivo del cancello
QUOTA_B_CANCELLO = 0.9
F_CANCELLO = 0.5                # (c): quota di righe con una parola di classe nel positivo del cancello

# ---- le prove dei controlli (numeri scritti prima; N_PROVE44 li riduce solo per provare il codice)
NEG_ERB = (('v21', tuple(range(1, 25))), ('naibbe', L.NAIBBE), ('timm', L.SEMI_TIMM), ('latino', tuple(range(1, 21))),
           ('latino_rif', tuple(range(1, 21))), ('rimesc', tuple(range(1, 25))))
POS_ERB = (('Q4', 20), ('QG', 20), ('CS', 10), ('QGd', 10), ('QGq100', 10), ('QGq60', 10), ('QGq40', 10), ('QGq25', 10))
NEG_ZOD = (('iid', 40), ('tema', 40))
POS_B = tuple((dv, NPC_CANCELLO, QUOTA_B_CANCELLO, 20) for dv in TV.divisioni()) + tuple(('elemento', n, 0.8, 10) for n in (5, 10, 40))
POS_C = tuple((t, F_CANCELLO, 20, False) for t in TV.tavole()) + tuple(
    (t, f, 10, False) for t in list(TV.tavole())[:3:2] for f in (0.2, 0.3, 0.7)) + ((list(TV.tavole())[0], F_CANCELLO, 10, True),)


def n_(n):
    return max(1, int(round(n * SCALA)))


# ---------------------------------------------------------------- lavori dei controlli

def lavori_controlli():
    jobs = []
    for u in ('A', 'B'):
        for fam, indici in NEG_ERB:
            for i in indici[:n_(len(indici))]:
                jobs.append(dict(ric='erb', tipo='neg', famiglia=fam, indice=int(i), unita=u, K=K))
        for schema, n in POS_ERB:
            for i in range(1, n_(n) + 1):
                jobs.append(dict(ric='erb', tipo='pos', schema=schema, indice=i, unita=u, K=K))
    for fam, n in NEG_ZOD:
        for i in range(1, n_(n) + 1):
            jobs.append(dict(ric='zod', tipo='neg', famiglia=fam, indice=i))
    for dv, npc, quota, n in POS_B:
        for i in range(1, n_(n) + 1):
            jobs.append(dict(ric='zodb', tipo='pos', divisione=dv, npc=npc, quota=quota, indice=i))
    for tav, f, n, per_segno in POS_C:
        for i in range(1, n_(n) + 1):
            jobs.append(dict(ric='zodc', tipo='pos', tavola=tav, f=f, per_segno=per_segno, indice=i))
    for j in jobs:
        j['id'] = '|'.join('%s=%s' % (k, j[k]) for k in sorted(j) if k not in ('K',))
    return jobs


def _dati_zod(famiglia, seme):
    lay = D.layout_zodiaco('ZL')
    return Z.sintetico(lay, seme, famiglia)


def _lati(et, al):
    return [[w for r in e for w in r] for e in et], [[w for r in e for w in r] + a for e, a in zip(et, al)]


def lavoro(job):
    t0 = time.time()
    if job['ric'] == 'erb':
        r = C.lavoro(dict(job))
    elif job['ric'] == 'zod':
        et, al = _dati_zod(job['famiglia'], 5000 + job['indice'] + (0 if job['famiglia'] == 'iid' else 1000))
        a, b = _lati(et, al)
        rb = Z.ricerca_b(a, b, k=KZ, seme=job['indice'])
        rc = Z.ricerca_c(et, k=KZ, seme=job['indice'])
        r = dict(p_b=rb['p'], stat_b=rb['stat'], nome_b=rb['nome'], p_c=rc['p'], stat_c=rc['stat'], nome_c=rc['nome'])
    elif job['ric'] == 'zodb':
        et, al = _dati_zod('iid', 6000 + job['indice'])
        et, al = Z.pianta_segni(et, al, job['indice'], job['divisione'], parole_per_classe=job['npc'], quota=job['quota'])
        a, b = _lati(et, al)
        rb = Z.ricerca_b(a, b, k=KZ, seme=job['indice'])
        r = dict(p=rb['p'], stat=rb['stat'], nome=rb['nome'])
    else:
        et, al = _dati_zod('iid', 7000 + job['indice'])
        et, _ = Z.pianta_gradi(et, job['indice'], job['tavola'], job['f'], rotazioni_per_segno=job['per_segno'])
        rc = Z.ricerca_c(et, k=KZ, seme=job['indice'])
        r = dict(p=rc['p'], stat=rc['stat'], nome=rc['nome'])
    out = dict(job)
    out.update(r)
    out['secondi'] = round(time.time() - t0, 1)
    return out


def fase_C():
    os.makedirs(CACHE, exist_ok=True)
    percorso = os.path.join(CACHE, 'controlli.jsonl')
    fatti = set()
    if RIPRENDI and os.path.exists(percorso):
        with open(percorso, encoding='utf-8') as f:
            for riga in f:
                if riga.strip():
                    fatti.add(json.loads(riga)['id'])
    jobs = [j for j in lavori_controlli() if j['id'] not in fatti]
    print('C: %d lavori da fare (%d gia fatti)' % (len(jobs), len(fatti)), flush=True)
    for k in L.CHIAVI_V21_NUOVE:
        if not os.path.exists(L.percorso_v21(k)):
            raise SystemExit('manca il libro v21 con chiave %d: va fatto con `python esperimenti/schemi_libri.py`' % k)
    t0 = time.time()
    with open(percorso, 'a', encoding='utf-8') as f, get_context('spawn').Pool(max(1, min(PROCESSI, 8))) as pool:
        for i, r in enumerate(pool.imap_unordered(lavoro, jobs, chunksize=1)):
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            if (i + 1) % 25 == 0:
                print('  %d/%d (%.0f s)' % (i + 1, len(jobs), time.time() - t0), flush=True)
    print('C: finita in %.0f s' % (time.time() - t0), flush=True)


def leggi_controlli():
    with open(os.path.join(CACHE, 'controlli.jsonl'), encoding='utf-8') as f:
        return [json.loads(r) for r in f if r.strip()]


# ---------------------------------------------------------------- il cancello

def _quota(xs):
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def cancello(rows):
    """Che cosa i controlli ammettono. Regole (preregistrate): una unita' dell'erbario entra se Q4 e QG sono visti (p <= ALFA_T e schema
    ritrovato) in almeno il 90% delle prove e i falsi allarmi sui negativi (p <= ALFA_T) sono al piu' il 5%; (b): una divisione entra se il
    suo positivo e' visto in almeno il 90% e i falsi allarmi sono al piu' il 5%; (c): idem per le tavole."""
    out = OrderedDict()
    erb = OrderedDict()
    for u in ('A', 'B'):
        neg = [r for r in rows if r['ric'] == 'erb' and r['tipo'] == 'neg' and r['unita'] == u]
        fa = _quota(r['p'] <= ALFA_T for r in neg)
        fa05 = _quota(r['p'] <= 0.05 for r in neg)
        per_fam = OrderedDict()
        for fam, _ in NEG_ERB:
            x = [r for r in neg if r['famiglia'] == fam]
            per_fam[fam] = dict(n=len(x), allarmi=sum(r['p'] <= ALFA_T for r in x), p_minore_005=sum(r['p'] <= 0.05 for r in x))
        det = OrderedDict()
        for schema, _ in POS_ERB:
            x = [r for r in rows if r['ric'] == 'erb' and r['tipo'] == 'pos' and r['unita'] == u and r['schema'] == schema]
            det[schema] = dict(n=len(x), visti=sum(r['p'] <= ALFA_T and r.get('recupero', False) for r in x), quota=_quota(r['p'] <= ALFA_T and r.get('recupero', False) for r in x))
        ok = (fa is not None and fa <= FALSI_ALLARMI_MAX and det['Q4']['quota'] is not None and det['Q4']['quota'] >= POSITIVI_MIN
              and det['QG']['quota'] is not None and det['QG']['quota'] >= POSITIVI_MIN)
        erb[u] = dict(ammessa=bool(ok), falsi_allarmi=fa, falsi_allarmi_005=fa05, n_negativi=len(neg), per_famiglia=per_fam, positivi=det)
    out['erbario'] = erb
    # zodiaco
    negz = [r for r in rows if r['ric'] == 'zod']
    fa_b = _quota(r['p_b'] <= ALFA_T for r in negz)
    fa_c = _quota(r['p_c'] <= ALFA_T for r in negz)
    b = OrderedDict()
    for dv, npc, quota, _ in POS_B:
        x = [r for r in rows if r['ric'] == 'zodb' and r['divisione'] == dv and r['npc'] == npc and r['quota'] == quota]
        b[(dv, npc, quota)] = dict(n=len(x), visti=sum(r['p'] <= ALFA_T for r in x), quota=_quota(r['p'] <= ALFA_T for r in x))
    ammesse_b = [dv for (dv, npc, quota), v in b.items() if npc == NPC_CANCELLO and quota == QUOTA_B_CANCELLO and v['quota'] is not None
                 and v['quota'] >= POSITIVI_MIN] if (fa_b is not None and fa_b <= FALSI_ALLARMI_MAX) else []
    out['b'] = dict(ammesse=ammesse_b, falsi_allarmi=fa_b, n_negativi=len(negz), positivi=OrderedDict(('%s|%d parole|quota %.1f' % k, v) for k, v in b.items()))
    c = OrderedDict()
    for tav, f, _, per_segno in POS_C:
        x = [r for r in rows if r['ric'] == 'zodc' and r['tavola'] == tav and r['f'] == f and r['per_segno'] == per_segno]
        c[(tav, f, per_segno)] = dict(n=len(x), visti=sum(r['p'] <= ALFA_T for r in x), quota=_quota(r['p'] <= ALFA_T for r in x))
    ammesse_c = [tav for (tav, f, ps), v in c.items() if f == F_CANCELLO and not ps and v['quota'] is not None and v['quota'] >= POSITIVI_MIN] \
        if (fa_c is not None and fa_c <= FALSI_ALLARMI_MAX) else []
    out['c'] = dict(ammesse=ammesse_c, falsi_allarmi=fa_c, n_negativi=len(negz),
                    positivi=OrderedDict(('%s|f %.1f%s' % (k[0], k[1], '|rotazione per segno' if k[2] else ''), v) for k, v in c.items()))
    return out


def fase_G():
    rows = leggi_controlli()
    g = cancello(rows)
    with open(os.path.join(CACHE, 'cancello.json'), 'w', encoding='utf-8') as f:
        json.dump(g, f, ensure_ascii=False, indent=1)
    for u, v in g['erbario'].items():
        print('G erbario %s: %s (falsi allarmi %s su %d; Q4 %s, QG %s)' % (u, 'AMMESSA' if v['ammessa'] else 'non ammessa', v['falsi_allarmi'],
                                                                        v['n_negativi'], v['positivi']['Q4']['quota'], v['positivi']['QG']['quota']), flush=True)
    print('G (b) ammesse:', g['b']['ammesse'], ' (c) ammesse:', g['c']['ammesse'], flush=True)
    return g


# ---------------------------------------------------------------- il Voynich (fase V)

def nulli_chunk(args):
    unita, tipo, semi = args
    return E.lavoro_nullo((unita, tipo, semi))


def testi_di(trascrizione):
    """(erbario: unita' -> (pagine, strati, parole), zodiaco: (etichette per segno, altro per segno)). Con TESTO44=prova NON si
    tocca il manoscritto: testi di prova (latino cifrato e dati finti; 'prova1' con gli schemi piantati, 'prova2' senza)."""
    if TESTO == 'prova':
        lay = D.layout_erbario('ZL')
        piantato = trascrizione == 'prova1'
        out = OrderedDict()
        for u in ('A', 'B'):
            pag = C.latino_cifrato(lay[u], 31 + (0 if piantato else 1), schema='QG' if piantato else None)
            out[u] = (pag, D.strati(lay[u]))
        et, al = Z.sintetico(D.layout_zodiaco('ZL'), 77 + (0 if piantato else 1), 'iid')
        if piantato:
            et, al = Z.pianta_segni(et, al, 3, 'elemento', parole_per_classe=NPC_CANCELLO, quota=QUOTA_B_CANCELLO)
            et, _ = Z.pianta_gradi(et, 4, list(TV.tavole())[0], F_CANCELLO)
        return out, (et, al)
    if os.environ.get('SENZA_VOYNICH44') == '1':
        raise SystemExit('SENZA_VOYNICH44=1: la fase V con il manoscritto non parte (solo prove)')
    tx = D.testo_erbario(trascrizione)
    out = OrderedDict((u, ([p['parole'] for p in tx[u]], D.strati(tx[u]))) for u in ('A', 'B'))
    zz = D.testo_zodiaco(trascrizione)
    return out, ([zz[s]['etichette'] for s in D.ORDINE_SEGNI], [zz[s]['altro'] for s in D.ORDINE_SEGNI])


def v_erbario(testo, gate, tr, pool):
    unita_ammesse = [u for u in ('A', 'B') if gate['erbario'][u]['ammessa']]
    if not unita_ammesse:
        return dict(eseguita=False, motivo='nessuna unita ammessa dal cancello')
    evs, dett, cand = [], OrderedDict(), OrderedDict()
    for u in unita_ammesse:
        pag, strati = testo[u]
        U = E.Unita(pag, strati)
        oss, gruppi = U.osservato()
        nulli = {}
        for tipo in E.NULLI:
            semi = [(900000 if tipo == 'tok' else 950000) + i for i in range(KV)]
            pezzi = [semi[i:i + 100] for i in range(0, KV, 100)]
            res = pool.map(nulli_chunk, [(U, tipo, p) for p in pezzi])
            nulli[tipo] = np.array([v for r in res for v in r])
        evs.append(E.valuta(oss, nulli))
        dett[u] = dict(N=U.N, V=U.V, oss=[round(float(x), 4) for x in oss])
        cand[u] = {'%d|%s|%s|%s' % (v + (mo,)): [U.voc[i] for i in g] for (v, mo), g in zip([(v, mo) for v in E.VARIANTI for mo in E.MODI], gruppi)}
    pf = E.p_finale(evs)
    pf = dict(p=pf['p'], per_tipo={t: dict(p=v['p'], stat=v['stat'], variante=list(v['variante']), unita=unita_ammesse[v['unita']],
                                           nullo_p95=v['nullo_p95']) for t, v in pf['per_tipo'].items()})
    with open(os.path.join(CACHE, 'candidati_%s.json' % tr), 'w', encoding='utf-8') as f:
        json.dump(dict(erbario=cand), f, ensure_ascii=False)
    return dict(eseguita=True, unita=unita_ammesse, dettaglio=dett, **pf, trovato=bool(pf['p'] <= ALFA_T))


def v_zodiaco(zod, gate):
    et, al = zod
    a, b = _lati(et, al)
    out = OrderedDict()
    if gate['b']['ammesse']:
        r = Z.ricerca_b(a, b, k=KVZ, seme=4401, solo=gate['b']['ammesse'])
        out['b'] = dict(eseguita=True, divisioni=gate['b']['ammesse'], trovato=bool(r['p'] <= ALFA_T), **r)
    else:
        out['b'] = dict(eseguita=False, motivo='nessuna divisione ammessa dal cancello')
    if gate['c']['ammesse']:
        r = Z.ricerca_c(et, k=KVZ, seme=4501, solo=gate['c']['ammesse'])
        out['c'] = dict(eseguita=True, tavole=gate['c']['ammesse'], trovato=bool(r['p'] <= ALFA_T), **r)
    else:
        out['c'] = dict(eseguita=False, motivo='nessuna tavola ammessa dal cancello')
    return out


def fase_V(gate):
    if not any(v['ammessa'] for v in gate['erbario'].values()) and not gate['b']['ammesse'] and not gate['c']['ammesse']:
        print('V: il cancello non ammette niente: il Voynich non si esegue', flush=True)
        return None
    trascrizioni = ('prova1', 'prova2') if TESTO == 'prova' else ('ZL', 'IT')
    out = OrderedDict()
    with get_context('spawn').Pool(max(1, min(PROCESSI, 8))) as pool:
        for tr in trascrizioni:
            print('V: trascrizione %s' % tr, flush=True)
            testo, zod = testi_di(tr)
            out[tr] = OrderedDict([('erbario', v_erbario(testo, gate, tr, pool)), ('zodiaco', v_zodiaco(zod, gate))])
    with open(os.path.join(CACHE, 'voynich.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
    return out


# ---------------------------------------------------------------- relazione

def pct(x):
    return '–' if x is None else '%.0f%%' % (100 * x)


def scrivi(gate, vo, rows):
    os.makedirs(USCITA, exist_ok=True)
    md = ['# IA44: schemi noti in anticipo, "una e una sola per pagina"', '',
          'Solo numeri e aggregati. Nessuna lettura: ogni "trovato" e\' una regolarita\' statistica (preregistrazione: preregistrazioni/ia44.md).', '',
          '## Controlli (testi non Voynich)', '']
    for u, v in gate['erbario'].items():
        md += ['### Erbario %s (%s)' % (u, 'AMMESSA' if v['ammessa'] else 'non ammessa'), '',
               'Falsi allarmi (p <= 1/300) su %d negativi: %s (con p <= 0,05: %s).' % (v['n_negativi'], pct(v['falsi_allarmi']), pct(v['falsi_allarmi_005'])), '',
               '| famiglia negativa | prove | allarmi | p <= 0,05 |', '|---|---|---|---|']
        for fam, x in v['per_famiglia'].items():
            md.append('| %s | %d | %d | %d |' % (fam, x['n'], x['allarmi'], x['p_minore_005']))
        md += ['', '| schema piantato | prove | visti e ritrovati | quota |', '|---|---|---|---|']
        for s, x in v['positivi'].items():
            md.append('| %s | %d | %d | %s |' % (s, x['n'], x['visti'], pct(x['quota'])))
        md.append('')
    md += ['### Zodiaco (b), per segno: divisioni ammesse: %s' % (', '.join(gate['b']['ammesse']) or 'nessuna'), '',
           'Falsi allarmi su %d zodiaci finti: %s.' % (gate['b']['n_negativi'], pct(gate['b']['falsi_allarmi'])), '', '| positivo | prove | visti | quota |', '|---|---|---|---|']
    for k, x in gate['b']['positivi'].items():
        md.append('| %s | %d | %d | %s |' % (k, x['n'], x['visti'], pct(x['quota'])))
    md += ['', '### Zodiaco (c), per grado: tavole ammesse: %s' % (', '.join(gate['c']['ammesse']) or 'nessuna'), '',
           'Falsi allarmi su %d zodiaci finti: %s.' % (gate['c']['n_negativi'], pct(gate['c']['falsi_allarmi'])), '', '| positivo | prove | visti | quota |', '|---|---|---|---|']
    for k, x in gate['c']['positivi'].items():
        md.append('| %s | %d | %d | %s |' % (k, x['n'], x['visti'], pct(x['quota'])))
    md += ['', '## Voynich', '']
    if vo is None:
        md.append('Non eseguito: il cancello non ammette niente (o la fase V non e\' stata chiesta).')
    else:
        for tr, v in vo.items():
            md += ['### Trascrizione %s' % tr, '', '| ricerca | eseguita | p | trovato |', '|---|---|---|---|']
            e = v['erbario']
            md.append('| (a) erbario | %s | %s | %s |' % ('si' if e['eseguita'] else 'no', '%.4f' % e['p'] if e['eseguita'] else '–',
                                                       ('SI' if e['trovato'] else 'no') if e['eseguita'] else '–'))
            for nome, ch in (('(b) segni', 'b'), ('(c) gradi', 'c')):
                z = v['zodiaco'][ch]
                md.append('| %s | %s | %s | %s |' % (nome, 'si' if z['eseguita'] else 'no', '%.4f' % z['p'] if z['eseguita'] else '–',
                                                    ('SI' if z['trovato'] else 'no') if z['eseguita'] else '–'))
            md.append('')
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(cancello=gate, voynich=vo, soglie=dict(alfa=ALFA, positivi_min=POSITIVI_MIN, falsi_allarmi_max=FALSI_ALLARMI_MAX),
                       k=dict(erbario=K, zodiaco=KZ, voynich_erbario=KV, voynich_zodiaco=KVZ)), f, ensure_ascii=False, indent=1, default=float)


def main():
    fasi = ('C', 'G', 'V', 'S') if FASE == 'tutto' else tuple(FASE)
    gate = vo = None
    if 'C' in fasi:
        fase_C()
    if 'G' in fasi:
        gate = fase_G()
    if 'V' in fasi:
        gate = gate or json.load(open(os.path.join(CACHE, 'cancello.json'), encoding='utf-8'))
        vo = fase_V(gate)
    if 'S' in fasi:
        gate = gate or json.load(open(os.path.join(CACHE, 'cancello.json'), encoding='utf-8'))
        if vo is None and os.path.exists(os.path.join(CACHE, 'voynich.json')) and 'V' not in fasi:
            vo = json.load(open(os.path.join(CACHE, 'voynich.json'), encoding='utf-8'))
        scrivi(gate, vo, leggi_controlli())
        print('scritto %s' % os.path.join(USCITA, NOME + '.md'), flush=True)


if __name__ == '__main__':
    main()
