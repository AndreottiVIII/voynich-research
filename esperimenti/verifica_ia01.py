"""Verifica dopo la corsa (non preregistrata, dichiarata come tale nel QUADERNO) del giudice A di ia01.

Domanda di Davide del 20/11: lo 0,751 del giudice A regge? Due dubbi:
  1. A mette insieme previsioni su pagine i cui profili vengono da 5 modelli del testo diversi (uno per piega):
     se la scala cambia fra i modelli l'AUC messa insieme potrebbe essere distorta. Qui si calcola anche l'AUC
     dentro ogni piega dei modelli del testo (media delle 5) e quella con i profili standardizzati dentro ogni piega.
  2. Con le etichette a caso le 5 AUC del controllo negativo variano da 0,386 a 0,613: piu' del previsto. Qui si
     rifa' il controllo negativo con 200 etichette a caso (stessa procedura di ia01) per vedere la distribuzione del
     caso e dove cade lo 0,751.

Nessun nuovo addestramento: usa solo i profili salvati in risultati/ia01_corse.jsonl e le funzioni di ia01.
Uscite: risultati/ia01_verifica.json e .md (solo numeri).
Uso, dalla radice del repo:
  PYTHONHASHSEED=0 dati/cache/.venv_lm/Scripts/python esperimenti/verifica_ia01.py
"""
import json
import os
import random
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import ia01_giudice_neurale as G  # noqa: E402

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NULLI = int(os.environ.get('NULLI', '200'))


def carica():
    corse = [json.loads(l) for l in open(os.path.join(RADICE, 'risultati', 'ia01_corse.jsonl'), encoding='utf-8')]
    return G.Dati(corse)


def auc_dentro(y, p, fo):
    v = []
    for f in sorted(set(fo)):
        I = [i for i, x in enumerate(fo) if x == f]
        a = G.auc(np.asarray(y)[I], np.asarray(p)[I])
        if a is not None:
            v.append(a)
    return float(np.mean(v)), v


def standardizza_per_piega(X, fo):
    X = np.array(X, dtype=float)
    fo = np.asarray(fo)
    for f in set(fo.tolist()):
        I = fo == f
        X[I] = (X[I] - X[I].mean(0)) / (X[I].std(0) + 1e-9)
    return X


def libro(dati, nome, fold):
    pag = [p for p in dati.prof['vere'] if p in dati.prof[nome]]
    X = np.array([dati.X('vere', p) for p in pag] + [dati.X(nome, p) for p in pag])
    y = np.array([0] * len(pag) + [1] * len(pag))
    fo = [fold[p] for p in pag] * 2
    a, p = G.auc_logistico(X, y, pag + pag)
    d, per = auc_dentro(y, p, fo)
    a_std, p_std = G.auc_logistico(standardizza_per_piega(X, fo), y, pag + pag)
    d_std, _ = auc_dentro(y, p_std, fo)
    return OrderedDict(AUC_messa_insieme=a, AUC_dentro_piega=d, AUC_per_piega=per, AUC_std_per_piega=a_std,
                       AUC_std_dentro_piega=d_std, pagine=len(pag))


def nullo(dati, s, fold):
    pag = list(dati.prof['vere'])
    random.Random(3970 + s).shuffle(pag)
    y = np.array([int(i >= len(pag) // 2) for i in range(len(pag))])
    X = np.array([dati.X('vere', p) for p in pag])
    a, p = G.auc_logistico(X, y, pag)
    d, _ = auc_dentro(y, p, [fold[q] for q in pag])
    return a, d


def main():
    dati = carica()
    fold = G.contesto()['fold']
    ris = OrderedDict(nota='verifica dopo la corsa, non preregistrata', nulli=NULLI)
    libri = OrderedDict()
    for k in G.CHIAVI:
        libri['a%d' % k] = libro(dati, 'a%d' % k, fold)
        print('a%d' % k, {x: round(v, 3) for x, v in libri['a%d' % k].items() if isinstance(v, float)}, flush=True)
    ris['libri'] = libri
    for n in ('ctrl:righe', 'ctrl:parole', 'ctrl:e192'):
        if n in dati.prof:
            ris[n] = libro(dati, n, fold)
    m = lambda k: float(np.mean([libri[l][k] for l in libri]))
    ris['medie'] = OrderedDict((k, m(k)) for k in ('AUC_messa_insieme', 'AUC_dentro_piega', 'AUC_std_per_piega',
                                                   'AUC_std_dentro_piega'))
    na, nd = [], []
    for s in range(1, NULLI + 1):       # s=1..5 sono le 5 etichette della corsa
        a, d = nullo(dati, s, fold)
        na.append(a)
        nd.append(d)
    q = lambda v: OrderedDict(media=float(np.mean(v)), sd=float(np.std(v, ddof=1)), p2_5=float(np.percentile(v, 2.5)),
                              p97_5=float(np.percentile(v, 97.5)), p99_9=float(np.percentile(v, 99.9)), massimo=float(max(v)))
    ris['nullo_messa_insieme'] = q(na)
    ris['nullo_dentro_piega'] = q(nd)
    ris['nullo_prime_5'] = na[:5]
    json.dump(ris, open(os.path.join(RADICE, 'risultati', 'ia01_verifica.json'), 'w', encoding='utf-8'), indent=1)
    f3 = lambda x: '%.3f' % x
    r = ['# ia01 — verifica dopo la corsa (non preregistrata)', '',
         'Profili salvati di ia01, nessun nuovo addestramento. Etichette a caso: %d.' % NULLI, '',
         '| misura | media sui 10 libri |', '|---|---|']
    for k, v in ris['medie'].items():
        r.append('| %s | %s |' % (k, f3(v)))
    r += ['', '| libro | messa insieme | dentro piega | per piega (5) |', '|---|---|---|---|']
    for l, d in libri.items():
        r.append('| %s | %s | %s | %s |' % (l, f3(d['AUC_messa_insieme']), f3(d['AUC_dentro_piega']),
                                            ', '.join(f3(x) for x in d['AUC_per_piega'])))
    for n in ('ctrl:righe', 'ctrl:parole', 'ctrl:e192'):
        if n in ris:
            r.append('| %s | %s | %s | %s |' % (n, f3(ris[n]['AUC_messa_insieme']), f3(ris[n]['AUC_dentro_piega']),
                                                ', '.join(f3(x) for x in ris[n]['AUC_per_piega'])))
    r += ['', 'Caso (vere contro vere, etichette a caso):', '']
    for k in ('nullo_messa_insieme', 'nullo_dentro_piega'):
        v = ris[k]
        r.append('- %s: media %s, sd %s, 95%% fra %s e %s, 99,9%% sotto %s, massimo %s' % (
            k, f3(v['media']), f3(v['sd']), f3(v['p2_5']), f3(v['p97_5']), f3(v['p99_9']), f3(v['massimo'])))
    r.append('- prime 5 etichette (quelle della corsa): ' + ', '.join(f3(x) for x in ris['nullo_prime_5']))
    open(os.path.join(RADICE, 'risultati', 'ia01_verifica.md'), 'w', encoding='utf-8').write('\n'.join(r) + '\n')
    print('\n'.join(r))


if __name__ == '__main__':
    main()
