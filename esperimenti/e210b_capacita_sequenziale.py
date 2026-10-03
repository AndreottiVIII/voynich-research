# -*- coding: utf-8 -*-
"""Esperimento 210b: limite di capacita' del canale delle cinque scelte di grafia con un modello sequenziale combinato
(regressione logistica per scelta, solo contesto precedente nell'ordine di lettura), validazione pagine pari/dispari.

Preregistrazione: preregistrazioni/e210b.md. Scrive risultati/e210b_capacita_sequenziale.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e135_stato_riga as e135
import e154b_ordine_normalizzato as e154b
import e210_capacita_stretta as e210

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLA = 5


def occorrenze_estese():
    out = []
    righe = [r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    for k, r in enumerate(righe):
        ps = list(r.parole)
        for j, w in enumerate(ps):
            if not trascrizione.pulita(w):
                continue
            if w not in e210._CACHE:
                e210._CACHE[w] = [(f, v) for f, _, _, v in e135.occorrenze([('x', [w])]) if f in e210.SCELTE]
            n = e154b.normalizza(w)
            pos = 'prima' if j == 0 else 'seconda' if j == 1 else 'ultima' if j == len(ps) - 1 else 'interna'
            for f, v in e210._CACHE[w]:
                out.append(dict(pag=r.pagina, k=k, j=j, f=f, n=n, v=v, pos=pos, par=bool(r.inizio_par), lingua=r.lingua or '?', sez=r.sezione or '?'))
    return out, [r.pagina for r in righe]


def contesti(occ, pagina_di):
    """Per ogni occorrenza, le caratteristiche numeriche di contesto (solo cio' che precede). pagina_di: pagina di ogni
    riga (tutte le righe, anche senza occorrenze)."""
    per_riga = defaultdict(list)
    for i, o in enumerate(occ):
        per_riga[o['k']].append(i)
    righe_pagina = defaultdict(list)
    for k, pag in enumerate(pagina_di):
        righe_pagina[pag].append(k)
    prima_in_pagina = {}
    for pag, ks in righe_pagina.items():
        for t, k in enumerate(ks):
            prima_in_pagina[k] = ks[:t]
    valori_riga = {k: defaultdict(list) for k in range(len(pagina_di))}
    for k, idx in per_riga.items():
        for i in idx:
            valori_riga[k][occ[i]['f']].append(occ[i]['v'])
    out = []
    for i, o in enumerate(occ):
        x = {}
        k, f = o['k'], o['f']

        def metti(nome, vals):
            x[nome + ' presenza'] = 1.0 if vals else 0.0
            x[nome + ' quota'] = (sum(vals) / len(vals)) if vals else 0.0

        stessa = [occ[t]['v'] for t in per_riga[k] if occ[t]['j'] < o['j'] and occ[t]['f'] == f]
        metti('riga, prima', stessa)
        prec = prima_in_pagina[k]
        metti('riga precedente', valori_riga[prec[-1]][f] if prec else [])
        metti('pagina, prima', [v for kk in prec[:-1] for v in valori_riga[kk][f]])
        for g in e210.SCELTE:
            if g != f:
                metti('altra %d, riga, prima' % g, [occ[t]['v'] for t in per_riga[k] if occ[t]['j'] < o['j'] and occ[t]['f'] == g])
        x['posizione=' + o['pos']] = 1.0
        x['prima riga di paragrafo'] = 1.0 if o['par'] else 0.0
        x['lingua=' + o['lingua']] = 1.0
        x['sezione=' + o['sez']] = 1.0
        out.append(x)
    return out


def bit(p, v):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -math.log2(p if v else 1 - p)


def valuta(occ, ctx):
    pagine = []
    for o in occ:
        if o['pag'] not in pagine:
            pagine.append(o['pag'])
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    modelli = ('M0', 'solo parola', 'combinato')
    b = {m: [0.0] * len(occ) for m in modelli}
    for f in e210.SCELTE:
        idx = [i for i, o in enumerate(occ) if o['f'] == f]
        for verifica in (0, 1):
            tr = [i for i in idx if meta[occ[i]['pag']] != verifica]
            te = [i for i in idx if meta[occ[i]['pag']] == verifica]
            ytr = np.array([occ[i]['v'] for i in tr])
            q = (ytr.sum() + 1) / (len(ytr) + 2)
            conta = Counter(occ[i]['n'] for i in tr)
            parola = lambda i: {'parola=' + (occ[i]['n'] if conta[occ[i]['n']] >= MIN_PAROLA else '<rara>'): 1.0}
            for nome, feat in (('solo parola', lambda i: parola(i)), ('combinato', lambda i: dict(parola(i), **ctx[i]))):
                dv = DictVectorizer()
                Xtr = dv.fit_transform([feat(i) for i in tr])
                Xte = dv.transform([feat(i) for i in te])
                m = LogisticRegression(C=1.0, max_iter=5000).fit(Xtr, ytr)
                p = m.predict_proba(Xte)[:, 1]
                for i, pi in zip(te, p):
                    b[nome][i] = bit(pi, occ[i]['v'])
            for i in te:
                b['M0'][i] = bit(q, occ[i]['v'])
    return b


def main():
    occ, pagina_di = occorrenze_estese()
    ctx = contesti(occ, pagina_di)
    b = valuta(occ, ctx)
    totali = OrderedDict((m, sum(x)) for m, x in b.items())
    medie = OrderedDict((m, sum(x) / len(x)) for m, x in b.items())
    per_scelta = OrderedDict()
    for f in e210.SCELTE:
        idx = [i for i, o in enumerate(occ) if o['f'] == f]
        per_scelta[e135.SCELTE[f]] = OrderedDict((m, sum(b[m][i] for i in idx) / len(idx)) for m in b)
    e182 = json.load(open(os.path.join(RISULTATI, 'e182_capacita.json'), encoding='utf-8'))['Voynich']['bit_totali']
    e210r = json.load(open(os.path.join(RISULTATI, 'e210_capacita_stretta.json'), encoding='utf-8'))
    e189 = json.load(open(os.path.join(RISULTATI, 'e189_capacita_totale.json'), encoding='utf-8'))
    tot = totali['combinato']
    tre = tot + e189['b_segno_d_inizio']['bit_totali'] + e189['c_ordine_nella_riga']['bit_totali']
    esito = 'limite piu\' stretto' if tot <= 0.95 * e182 else 'il limite regge'
    ris = OrderedDict([('occorrenze', len(occ)), ('occorrenze_e210', e210r['occorrenze']), ('bit_per_occorrenza', medie), ('bit_totali', totali),
                       ('e182_bit_totali', e182), ('e210_MXL_bit_totali', e210r['bit_totali']), ('riduzione_su_e182', 1 - tot / e182),
                       ('per_scelta', per_scelta), ('tre_canali', tre), ('parole_latine', [tre / 4.1 / 6, tre / 2 / 6]), ('esito', esito)])
    print('occorrenze %d (e210 %d) | bit/occ %s | totali %s | e182 %.0f | tre canali %.0f | %s' % (
        len(occ), e210r['occorrenze'], {m: round(x, 4) for m, x in medie.items()}, {m: round(x) for m, x in totali.items()}, e182, tre, esito), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e210b_capacita_sequenziale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e210b — Capacità delle scelte di grafia con un modello sequenziale combinato', '',
          'Regressione logistica per scelta, solo con il contesto precedente nell\'ordine di lettura; validazione pagine pari/dispari. '
          'Preregistrazione: `preregistrazioni/e210b.md`.', '',
          '| scelta | M0 | solo parola | combinato |', '|---|---|---|---|']
    for s, x in per_scelta.items():
        md.append('| %s | %.3f | %.3f | %.3f |' % (s, x['M0'], x['solo parola'], x['combinato']))
    md.append('| **tutte (bit/occorrenza)** | %.3f | %.3f | %.3f |' % tuple(medie[m] for m in ('M0', 'solo parola', 'combinato')))
    md.append('| **bit totali** | %.0f | %.0f | %.0f |' % tuple(totali[m] for m in ('M0', 'solo parola', 'combinato')))
    md += ['', 'e182: %.0f bit; e210 (MXL, pseudo-verosimiglianza): %.0f bit. Combinato: %.0f bit (%+.1f%% su e182). Tre canali: %.0f bit, cioè %.0f–%.0f parole latine.' % (
        e182, e210r['bit_totali'], tot, -100 * ris['riduzione_su_e182'], tre, tre / 4.1 / 6, tre / 2 / 6), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e210b_capacita_sequenziale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
