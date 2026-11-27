# -*- coding: utf-8 -*-
"""Esperimento IA45 (ia45): le colonne di segni singoli a margine di f49v, f66r, f76r (e l'anello di f57v come confronto).

Strada 1 di PROPOSTE_NON_IA_FABLE.md. Due ipotesi che si smentiscono a vicenda, scritte prima (preregistrazioni/ia45.md):
  A  la colonna e' una sequenza convenzionale ("alfabeto" recitato, anche piu' volte): le colonne dividono l'ordine dei segni e
     ogni colonna e' periodica;
  B  i segni della colonna sono i segni che aprono le righe accanto, scritti staccati (come nelle e72/e73).
Niente reti ne' modelli: conti e permutazioni. Non e' una decifrazione: un esito dice solo quale ipotesi e' compatibile, o nessuna.

Fasi (un solo comando le fa tutte, in quest'ordine):
  C  controlli su testo latino (mondi A, B, Bs, N1, N2, N3 con la forma delle pagine), `dati/cache/ia45/controlli.jsonl`
     (ripresa con RIPRENDI=1);
  C2 falsi allarmi su righe vere di ALTRE pagine del manoscritto (mondi N4a, N4b: nessuna colonna vera), `controlli.jsonl`;
     rifiuta di partire con SENZA_VOYNICH45=1;
  G  il cancello: per ogni parte (A, B1, B2) dice se i controlli passano (positivi >= 90%, falsi allarmi <= 5%);
  V  il Voynich (ZL, Takahashi, Glen Claston), SOLO per le parti ammesse; non parte se il cancello non ammette niente;
  S  `risultati/ia45_colonne.md` e `.json`: solo numeri (mai i segni ne' il testo della trascrizione).

    nohup bash strumenti/coda.sh ia45 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=4:ia45" > /dev/null 2>&1 &

Variabili (valori senza virgole e senza due punti): CACHE45 (cartella dei lavori), USCITA45 (dove scrivere i risultati),
N_PROVE45 (prove per mondo, 200), K45 (rimescolamenti per test, 20000), FASE45 (C, G, V, S o tutto), SENZA_VOYNICH45 (1 = la
fase V sul manoscritto e la C2 rifiutano di partire: per le prove di codice), TESTO45 (vuoto = manoscritto; 'prova' = mondi di
controllo al posto delle trascrizioni nella fase V, solo per provare le fasi V e S).
"""
import json
import os
import sys
import time
from collections import OrderedDict
from multiprocessing import get_context

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, '..')
sys.path.insert(0, QUI)
import colonne_dati as CD         # noqa: E402
import colonne_test as T          # noqa: E402
import colonne_controlli as CC    # noqa: E402

NOME = 'ia45_colonne'
CACHE = os.environ.get('CACHE45', os.path.join(RADICE, 'dati', 'cache', 'ia45'))
USCITA = os.environ.get('USCITA45', os.path.join(RADICE, 'risultati'))
N_PROVE = int(os.environ.get('N_PROVE45', 200))
K = int(os.environ.get('K45', 20000))
FASE = os.environ.get('FASE45', 'tutto')
PROCESSI = min(int(os.environ.get('PROCESSI', 4)), 8)
RIPRENDI = os.environ.get('RIPRENDI') == '1'
TRASCRIZIONI = ('ZL', 'IT', 'GC')
SOGLIA_POSITIVO, SOGLIA_FALSI = 0.90, 0.05
PARTI = ('A', 'B1', 'B2')


def _scrivi(percorso, dati):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dati, f, ensure_ascii=False, indent=1)
        f.write('\n')


# ------------------------------------------------------------------------------------------------------ fase C: controlli
def lavoro_controllo(arg):
    mondo, seme, k = arg
    pagine, rif = CC.mondo(mondo, seme)
    ris = T.batteria(pagine, rif, k, 450000 + 1000 * CC.MONDI.index(mondo) + seme)
    A, B1, B2 = T.lettura(ris)
    return dict(mondo=mondo, seme=seme, A=A, B1=B1, B2=B2,
                p={n: (None if r['p'] is None else round(r['p'], 6)) for n, r in ris.items()})


def fase_C():
    percorso = os.path.join(CACHE, 'controlli.jsonl')
    fatti = set()
    if RIPRENDI and os.path.exists(percorso):
        with open(percorso, encoding='utf-8') as f:
            for riga in f:
                d = json.loads(riga)
                fatti.add((d['mondo'], d['seme']))
    elif os.path.exists(percorso):
        os.remove(percorso)
    lavori = [(m, s, K) for m in CC.MONDI for s in range(1, N_PROVE + 1) if (m, s) not in fatti]
    os.makedirs(CACHE, exist_ok=True)
    print('fase C: %d lavori (%d gia fatti), %d processi, K=%d' % (len(lavori), len(fatti), PROCESSI, K), flush=True)
    t0 = time.time()
    with open(percorso, 'a', encoding='utf-8', newline='\n') as f, get_context('spawn').Pool(PROCESSI) as pool:
        for i, d in enumerate(pool.imap_unordered(lavoro_controllo, lavori, chunksize=4)):
            f.write(json.dumps(d) + '\n')
            f.flush()
            if (i + 1) % 100 == 0:
                print('  %d/%d (%.0f s)' % (i + 1, len(lavori), time.time() - t0), flush=True)
    print('fase C finita in %.0f s' % (time.time() - t0), flush=True)


def _avvia_ms():
    global INDICE_MS, RIF_MS
    import trascrizione
    righe = trascrizione.leggi('ZL')
    INDICE_MS = CC.indice_pagine(righe, 'ZL')
    RIF_MS = CD.riferimento(righe, 'ZL')


def lavoro_controllo_ms(arg):
    mondo, seme, k = arg
    pagine, rif = CC.mondo_manoscritto(INDICE_MS, mondo, seme, RIF_MS)
    ris = T.batteria(pagine, rif, k, 451000 + 1000 * CC.MONDI_MS.index(mondo) + seme)
    A, B1, B2 = T.lettura(ris)
    return dict(mondo=mondo, seme=seme, A=A, B1=B1, B2=B2,
                p={n: (None if r['p'] is None else round(r['p'], 6)) for n, r in ris.items()})


def fase_C2():
    if os.environ.get('SENZA_VOYNICH45') == '1':
        print('fase C2 saltata (SENZA_VOYNICH45=1)', flush=True)
        return
    percorso = os.path.join(CACHE, 'controlli.jsonl')
    fatti = set()
    if os.path.exists(percorso):
        with open(percorso, encoding='utf-8') as f:
            for riga in f:
                d = json.loads(riga)
                fatti.add((d['mondo'], d['seme']))
    lavori = [(m, s, K) for m in CC.MONDI_MS for s in range(1, N_PROVE + 1) if (m, s) not in fatti]
    print('fase C2: %d lavori' % len(lavori), flush=True)
    t0 = time.time()
    with open(percorso, 'a', encoding='utf-8', newline='\n') as f, get_context('spawn').Pool(PROCESSI, initializer=_avvia_ms) as pool:
        for i, d in enumerate(pool.imap_unordered(lavoro_controllo_ms, lavori, chunksize=4)):
            f.write(json.dumps(d) + '\n')
            f.flush()
    print('fase C2 finita in %.0f s' % (time.time() - t0), flush=True)


# ------------------------------------------------------------------------------------------------------ fase G: cancello
def tassi():
    percorso = os.path.join(CACHE, 'controlli.jsonl')
    per = {m: [] for m in CC.MONDI + CC.MONDI_MS}
    with open(percorso, encoding='utf-8') as f:
        for riga in f:
            d = json.loads(riga)
            per[d['mondo']].append(d)
    return {m: dict(n=len(v), **{p: (sum(1 for d in v if d[p]) / len(v) if v else None) for p in PARTI}) for m, v in per.items() if v}


def fase_G():
    t = tassi()
    # regola scritta prima: la parte e' ammessa se il suo positivo >= 90% e i suoi falsi allarmi <= 5% in tutti i negativi
    # A: positivo = mondo A; B1: positivo = mondo B; B2 (composizione): positivo = mondo Bs.
    # negativi: A e B1 in N1, N2, N3 e nel mondo dell'altra ipotesi; B2 solo in N1 e nel mondo A (N2, N3 hanno la composizione
    # delle righe per costruzione).
    regole = OrderedDict([
        ('A', dict(positivo='A', negativi=('N1', 'N2', 'N3', 'B', 'N4a', 'N4b'))),
        ('B1', dict(positivo='B', negativi=('N1', 'N2', 'N3', 'A', 'N4a', 'N4b'))),
        ('B2', dict(positivo='Bs', negativi=('N1', 'A', 'N4a'))),
    ])
    prova_senza_ms = os.environ.get('SENZA_VOYNICH45') == '1'      # solo prove di codice: i mondi N4 non ci sono
    esito = OrderedDict()
    for parte, r in regole.items():
        pos = t[r['positivo']][parte]
        falsi = {m: t[m][parte] for m in r['negativi'] if not (prova_senza_ms and m in CC.MONDI_MS)}
        ok = pos is not None and pos >= SOGLIA_POSITIVO and all(v is not None and v <= SOGLIA_FALSI for v in falsi.values())
        esito[parte] = dict(positivo=r['positivo'], tasso_positivo=pos, falsi_allarmi=falsi, ammessa=bool(ok))
        print('parte %-3s positivo (%s) %.3f | falsi allarmi %s -> %s' % (
            parte, r['positivo'], pos, {m: round(v, 3) for m, v in falsi.items()}, 'AMMESSA' if ok else 'non ammessa'), flush=True)
    # descrittivo: il mondo staccato (Bs) visto da B1, e il mondo B visto da B2
    print('descrittivo: Bs visto da B1 %.3f | B visto da B2 %.3f' % (t['Bs']['B1'], t['B']['B2']), flush=True)
    for m in CC.MONDI_MS:
        if m in t:
            print('manoscritto, altre pagine, %s: A %.3f B1 %.3f B2 %.3f (%d prove)' % (m, t[m]['A'], t[m]['B1'], t[m]['B2'], t[m]['n']), flush=True)
    _scrivi(os.path.join(CACHE, 'cancello.json'), dict(tassi=t, parti=esito, K=K, n_prove=N_PROVE))
    return esito, t


# ------------------------------------------------------------------------------------------------------ fase V: Voynich
def conteggi(pagine):
    return OrderedDict((p.nome, dict(segni=len(p.colonna), distinti=len(set(p.colonna)), rari=sum(1 for x in p.colonna if x.startswith('Z')),
                                     illeggibili=sum(1 for x in p.colonna if x == '?'), righe=p.n_righe)) for p in pagine)


def fase_V(esito):
    prova = os.environ.get('TESTO45') == 'prova'
    if os.environ.get('SENZA_VOYNICH45') == '1' and not prova:
        sys.exit('SENZA_VOYNICH45=1: la fase V sul manoscritto non parte')
    ammesse = [p for p, e in esito.items() if e['ammessa']]
    if not ammesse:
        print('fase V: il cancello non ammette niente: il Voynich non si tocca', flush=True)
        return None
    out = OrderedDict()
    for i, quale in enumerate(TRASCRIZIONI):
        if prova:        # solo per provare il codice: mondi di controllo al posto delle trascrizioni (A, A, N1)
            pagine, rif = CC.mondo('N1' if quale == 'GC' else 'A', 900 + i)
        else:
            pagine, rif = CD.tutto(quale)
        ris = T.batteria(pagine, rif, K, 450900 + i)
        out[quale] = OrderedDict(conteggi=conteggi(pagine), test=OrderedDict(
            (n, dict(osservato=None if r['osservato'] is None else round(float(r['osservato']), 6), p=r['p'],
                     **{k: v for k, v in r.items() if k in ('comuni', 'ritardo', 'nota', 'segni')})) for n, r in ris.items()))
        print('V %s fatto' % quale, flush=True)
    _scrivi(os.path.join(CACHE, 'voynich.json'), dict(ammesse=ammesse, K=K, alfa=T.ALFA, trascrizioni=out))
    return out


# ------------------------------------------------------------------------------------------------------ fase S: risultati
def parte_di(nome):
    return 'A' if nome[0] == 'A' else nome.split()[0]


def confermati(v, ammesse):
    """Un test e' confermato se p <= alfa in ZL e in almeno una fra IT e GC. Ritorna dict nome -> (ZL, IT, GC, confermato)."""
    out = OrderedDict()
    for nome, r in v['ZL']['test'].items():
        ps = [v[q]['test'].get(nome, {}).get('p') for q in TRASCRIZIONI]
        sig = [p is not None and p <= T.ALFA for p in ps]
        out[nome] = (ps, bool(sig[0] and (sig[1] or sig[2])) and parte_di(nome) in ammesse)
    return out


def fase_S(esito, t, v):
    ammesse = [p for p, e in esito.items() if e['ammessa']]
    ris = OrderedDict(esperimento='ia45', alfa=T.ALFA, n_test=T.N_TEST, K=K, controlli=t, cancello=esito)
    righe = ['# ia45 — le colonne di segni singoli a margine', '',
             'Preregistrazione: `preregistrazioni/ia45.md`. Solo numeri: i segni e il testo della trascrizione non stanno qui. '
             'Soglia di ogni test: p <= %.5f (0,01 diviso %d test). **Non e\' una decifrazione**: un esito dice solo quale ipotesi e\' compatibile.'
             % (T.ALFA, T.N_TEST), '',
             '## Controlli (testo latino, %d prove per mondo, %d rimescolamenti)' % (N_PROVE, K), '',
             '| mondo | prove | A | B1 | B2 |', '|---|---|---|---|---|']
    for m, r in t.items():
        righe.append('| %s | %d | %.3f | %.3f | %.3f |' % (m, r['n'], r['A'], r['B1'], r['B2']))
    righe += ['', '| parte | positivo | tasso | falsi allarmi | cancello |', '|---|---|---|---|---|']
    for p, e in esito.items():
        righe.append('| %s | %s | %.3f | %s | %s |' % (p, e['positivo'], e['tasso_positivo'],
                     ', '.join('%s %.3f' % (m, x) for m, x in e['falsi_allarmi'].items()), 'ammessa' if e['ammessa'] else 'NON ammessa'))
    if v is None:
        righe += ['', 'Il cancello non ammette niente: il manoscritto non e\' stato toccato.']
        ris['voynich'] = None
    else:
        ris['voynich'] = v
        conf = confermati(v, ammesse)
        ris['confermati'] = OrderedDict((n, dict(p=ps, confermato=c)) for n, (ps, c) in conf.items())
        righe += ['', '## Conteggi (ZL)', '', '| pagina | segni | distinti | glifi rari | illeggibili | righe di testo |', '|---|---|---|---|---|---|']
        for n, c in v['ZL']['conteggi'].items():
            righe.append('| %s | %d | %d | %d | %d | %d |' % (n, c['segni'], c['distinti'], c['rari'], c['illeggibili'], c['righe']))
        for q in TRASCRIZIONI:
            righe += ['', '## Test, trascrizione %s' % q, '', '| test | osservato | p | nota |', '|---|---|---|---|']
            for n, r in v[q]['test'].items():
                righe.append('| %s | %s | %s | %s |' % (n, '–' if r['osservato'] is None else r['osservato'],
                             '–' if r['p'] is None else '%.5f' % r['p'], r.get('nota', '') or ('ritardo %s' % r['ritardo'] if 'ritardo' in r else '')))
        righe += ['', '## Confermati (p <= soglia in ZL e in IT o GC, parte ammessa)', '']
        for n, (ps, c) in conf.items():
            righe.append('- %s: %s' % (n, 'confermato' if c else 'no'))
        a = any(c for n, (ps, c) in conf.items() if parte_di(n) == 'A' and n != 'A2 f57v')
        b1 = any(c for n, (ps, c) in conf.items() if parte_di(n) == 'B1')
        b2 = any(c for n, (ps, c) in conf.items() if parte_di(n) == 'B2')
        lettura = 'compatibile con A (sequenza convenzionale)' if a and not b1 else 'compatibile con B (segni uguali a quelli d\'inizio riga)' if b1 and not a \
            else 'compatibile con entrambe' if a and b1 else 'nessuna delle due'
        righe += ['', '**Lettura:** %s%s.' % (lettura, '; composizione dei segni come quella dei segni che aprono le righe (B2)' if b2 else '')]
        ris['lettura'] = dict(A=a, B1=b1, B2=b2, testo=lettura)
    _scrivi(os.path.join(USCITA, NOME + '.json'), ris)
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(righe) + '\n')


def main():
    if FASE in ('C', 'tutto'):
        fase_C()
        fase_C2()
    if FASE == 'C2':
        fase_C2()
    esito = t = v = None
    if FASE in ('G', 'V', 'S', 'tutto'):
        esito, t = fase_G()
    if FASE in ('V', 'S', 'tutto'):
        if FASE == 'S' and os.path.exists(os.path.join(CACHE, 'voynich.json')):
            with open(os.path.join(CACHE, 'voynich.json'), encoding='utf-8') as f:
                v = json.load(f)['trascrizioni']
        else:
            v = fase_V(esito)
    if FASE in ('S', 'tutto'):
        fase_S(esito, t, v)


if __name__ == '__main__':
    main()
