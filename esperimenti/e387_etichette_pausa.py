# -*- coding: utf-8 -*-
"""Esperimento 387: nelle etichette (parole isolate) qo- davanti a gallows e' piu' raro e -l piu' frequente che in mezzo
alle righe, a parita' di strato? (previsione della "forma di pausa").

Preregistrazione: preregistrazioni/e387.md. Scrive risultati/e387_etichette_pausa.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 10000


def main():
    rng = np.random.RandomState(387)
    ev = {'qo': defaultdict(lambda: ([], [])), 'l': defaultdict(lambda: ([], []))}   # strato -> (etichette, righe)
    sezioni = defaultdict(Counter)
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.ETICHETTA:
            continue
        st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
        for p in r.parole:
            if not trascrizione.pulita(p):
                continue
            w = tuple(D(p))
            x = e380.ini_qo(w)
            if x:
                ev['qo'][st][0].append(x[1] == 'qo')
                sezioni[r.sezione or '?']['qo/o etichette'] += 1
            y = e380.fin_lr(w)
            if y:
                ev['l'][st][0].append(y[1] == 'l')
                sezioni[r.sezione or '?']['l/r etichette'] += 1
    for st, pag, par, ws, seps in e386.righe():
        n = len(ws)
        for j in range(1, n - 1):
            w = ws[j]
            if not w or seps[j - 1] != '.' or seps[j] != '.':
                continue
            x = e380.ini_qo(w)
            if x:
                ev['qo'][st][1].append(x[1] == 'qo')
            y = e380.fin_lr(w)
            if y:
                ev['l'][st][1].append(y[1] == 'l')
    ris = OrderedDict()
    for tipo, segno in (('qo', -1), ('l', +1)):
        strati = OrderedDict((st, (np.array(e, float), np.array(r, float))) for st, (e, r) in sorted(ev[tipo].items()) if len(e) >= 5 and len(r) >= 5)

        def diff(dati):
            num = den = 0.0
            for e, r in dati.values():
                num += len(e) * (e.mean() - r.mean())
                den += len(e)
            return num / den
        vero = diff(strati)
        nul = np.empty(PERM)
        for i in range(PERM):
            perm = OrderedDict()
            for st, (e, r) in strati.items():
                tutto = rng.permutation(np.concatenate([e, r]))
                perm[st] = (tutto[:len(e)], tutto[len(e):])
            nul[i] = diff(perm)
        p_prev = float(np.mean(segno * nul >= segno * vero))
        p_contro = float(np.mean(segno * nul <= segno * vero))
        if p_prev < 0.01:
            esito = 'previsione confermata'
        elif p_contro < 0.01:
            esito = 'smentita'
        else:
            esito = 'non decisa'
        ris[tipo] = OrderedDict([('strati', OrderedDict((st, OrderedDict([('etichette', len(e)), ('quota_etichette', float(e.mean())), ('righe', len(r)), ('quota_righe', float(r.mean()))])) for st, (e, r) in strati.items())),
                                 ('differenza', vero), ('p_nella_direzione_prevista', p_prev), ('p_contraria', p_contro), ('esito', esito)])
        print(tipo, json.dumps(ris[tipo], default=float), flush=True)
    out = OrderedDict([('risultati', ris), ('etichette_per_sezione', {k: dict(v) for k, v in sezioni.items()})])
    json.dump(out, open(os.path.join(RISULTATI, 'e387_etichette_pausa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e387 — Le etichette usano la "forma di pausa"?', '', 'Preregistrazione: `preregistrazioni/e387.md`.', '']
    for tipo, nome in (('qo', '*qo*- fra *qo*-/*o*- davanti a gallows (previsto: meno nelle etichette)'), ('l', '-*l* fra -*l*/-*r* (previsto: più nelle etichette)')):
        x = ris[tipo]
        md += ['## %s' % nome, '', '| strato | etichette | quota | righe (in mezzo) | quota |', '|---|---|---|---|---|']
        for st, s in x['strati'].items():
            md.append('| %s | %d | %.2f | %d | %.2f |' % (st, s['etichette'], s['quota_etichette'], s['righe'], s['quota_righe']))
        md += ['', 'Differenza pesata etichette − righe: %+.3f; p nella direzione prevista %.4f, p contraria %.4f. Esito: **%s**.' % (x['differenza'], x['p_nella_direzione_prevista'], x['p_contraria'], x['esito']), '']
    open(os.path.join(RISULTATI, 'e387_etichette_pausa.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
