# -*- coding: utf-8 -*-
"""Estrazione di regole leggibili dai bit di ogni parola per ia13 (modulo di supporto, non e' un esperimento).

Che cosa c'e' qui, in parole semplici:
- `carica_parole`: legge i bit di ogni parola di prova (file in cache protetta, scritti dai lavori di rete) e li mette in tabella:
  per ogni parola dal secondo posto della riga in poi, quanto le costa in piu' (media di piu' rimescolamenti e semi) il contesto rimescolato.
- famiglie di "tabelle di pezzi": per ogni coppia o terna di pezzi (ultimo glifo della parola prima -> primo glifo di questa, ...)
  la media della perdita; una tabella con media "tirata verso il centro" (m = 10 parole finte) e provata su pagine mai viste.
- un albero di decisione piccolo (poche foglie) con domande del tipo "la parola prima finisce con questo glifo?".
- il "soffitto": quanta della variazione della perdita da parola a parola e' prevedibile in principio (il resto e' rumore del
  rimescolamento), stimato dall'accordo fra rimescolamenti diversi.
Qui non si scrive nessun risultato; i nomi dei glifi vengono dati solo come codici anonimi (rango di frequenza) a chi li stampa.
"""
import glob
import os
from collections import Counter, OrderedDict

import numpy as np

MIN_FOGLIA = 40
M_TIRA = 10.0                      # parole finte per tirare la media di una cella verso la media generale


def carica_parole(cartella, nome, semi, fold_di=None):
    """Tutte le parole di prova di un testo: per ogni (seme, piega) il file `parole_<nome>_s<seme>_f<piega>.npz`. Con piu' semi la
    differenza di bit e' la media dei semi (stesse parole, stesse pagine). Restituisce un dict con liste e array, parole in ordine di
    lettura dentro ogni pagina; None se mancano file."""
    per_seme = []
    for s in semi:
        files = sorted(glob.glob(os.path.join(cartella, 'parole', 'parole_%s_s%d_f*.npz' % (nome, s))))
        if not files:
            return None
        per_seme.append(files)
    if len({len(f) for f in per_seme}) != 1:
        return None
    righe = None
    for files in per_seme:
        cur = dict(pagina=[], riga=[], J=[], nl=[], parola=[], ctrue=[], delta=[], fold=[])
        for fi, fn in enumerate(files):
            d = np.load(fn, allow_pickle=False)
            glifi = [str(x) for x in d['glifi']]
            off, gl = d['off'], d['gl']
            nomi = [str(x) for x in d['pagine']]
            piega = int(fn.split('_f')[-1].split('.')[0])
            for i in range(len(d['pag'])):
                cur['pagina'].append(nomi[d['pag'][i]])
                cur['riga'].append(int(d['riga'][i]))
                cur['J'].append(int(d['J'][i]))
                cur['nl'].append(int(d['nl'][i]))
                cur['parola'].append(tuple(glifi[g] for g in gl[off[i]:off[i + 1]]))
                cur['fold'].append(piega)
            cur['ctrue'].append(d['ctrue'])
            cur['delta'].append(d['delta'])
        cur['ctrue'] = np.concatenate(cur['ctrue'])
        cur['delta'] = np.concatenate(cur['delta'], axis=0).astype(np.float64)
        if righe is None:
            righe = cur
            righe['n_semi'] = 1
        else:
            chiave_a = list(zip(righe['pagina'], righe['riga'], righe['J']))
            chiave_b = list(zip(cur['pagina'], cur['riga'], cur['J']))
            if sorted(chiave_a) != sorted(chiave_b):
                return None
            if chiave_a != chiave_b:                               # stesse parole in ordine diverso: si riallinea
                pos = {k: i for i, k in enumerate(chiave_b)}
                o = np.array([pos[k] for k in chiave_a])
                cur['delta'], cur['ctrue'] = cur['delta'][o], cur['ctrue'][o]
            righe['delta'] = righe['delta'] + cur['delta']
            righe['ctrue'] = righe['ctrue'] + cur['ctrue']
            righe['n_semi'] += 1
    k = righe['n_semi']
    righe['delta'] = righe['delta'] / k
    righe['ctrue'] = righe['ctrue'] / k
    for c in ('riga', 'J', 'nl', 'fold'):
        righe[c] = np.array(righe[c], dtype=np.int64)
    righe['pagine'] = sorted(set(righe['pagina']))
    pos = {p: i for i, p in enumerate(righe['pagine'])}
    righe['pag'] = np.array([pos[p] for p in righe['pagina']], dtype=np.int64)
    return righe


def soffitto(yr):
    """Tetto di prevedibilita': quota della varianza della MEDIA dei rimescolamenti che non e' rumore del rimescolamento.
    yr (parole, R). Con R = 1 non si puo' stimare."""
    R = yr.shape[1]
    if R < 2:
        return float('nan')
    a = yr - yr.mean(0)
    v = float((a ** 2).mean(0).mean())
    cov = float(np.mean([(a[:, r] * a[:, s]).mean() for r in range(R) for s in range(r + 1, R)]))
    cov = max(cov, 0.0)
    rum = max(v - cov, 0.0)
    return cov / (cov + rum / R) if cov + rum > 0 else float('nan')


def tabella_regole(D):
    """Le parole con una parola prima nella riga (J >= 1), con i pezzi della parola, della prima e della seconda prima."""
    ok = D['J'] >= 1
    idx = np.where(ok)[0]
    n = len(D['J'])
    parole = D['parola']
    prev, prev2 = {}, {}
    for i in idx:
        prev[i] = parole[i - 1]
        prev2[i] = parole[i - 2] if D['J'][i] >= 2 else None
    R = OrderedDict()
    R['idx'] = idx
    R['J'] = D['J'][idx]
    R['nl'] = D['nl'][idx]
    R['e'] = R['nl'] - 1 - R['J']
    R['y'] = D['delta'][idx].mean(1)
    R['yr'] = D['delta'][idx]
    R['fold'] = D['fold'][idx]
    R['pag'] = D['pag'][idx]
    R['w'] = [parole[i] for i in idx]
    R['p1'] = [prev[i] for i in idx]
    R['p2'] = [prev2[i] for i in idx]
    return R


NA = ('NA',)


def _f1(w):
    return w[0] if w else NA


def _l1(w):
    return w[-1] if w else NA


def chiavi_famiglie(R):
    """Per ogni famiglia di regole, la chiave (tupla di pezzi) di ogni riga. NA = la parola non c'e' (il secondo posto di riga)."""
    w, p1, p2 = R['w'], R['p1'], R['p2']
    f = OrderedDict()
    f['contatto: ultimo(prec) -> primo']             = [(_l1(a), _f1(c)) for a, c in zip(p1, w)]
    f['ultimi2(prec) -> primo']                      = [(a[-2:], _f1(c)) for a, c in zip(p1, w)]
    f['ultimo(prec) -> primi2']                      = [(_l1(a), c[:2]) for a, c in zip(p1, w)]
    f['estremi(prec) -> primo']                      = [(_f1(a), _l1(a), _f1(c)) for a, c in zip(p1, w)]
    f['ultimo(prec2) -> primo (distanza 2)']         = [((_l1(b) if b else NA), _f1(c)) for b, c in zip(p2, w)]
    f['terna: ultimo(prec2), ultimo(prec) -> primo'] = [((_l1(b) if b else NA), _l1(a), _f1(c)) for a, b, c in zip(p1, p2, w)]
    f['lunghezze: prec -> parola']                   = [(len(a), len(c)) for a, c in zip(p1, w)]
    f['posto nella riga + primo']                    = [(min(int(j), 6), min(int(e), 3), _f1(c)) for j, e, c in zip(R['J'], R['e'], w)]
    f['la parola da sola: primo, ultimo, lunghezza'] = [(_f1(c), _l1(c), len(c)) for c in w]
    f['la parola intera']                            = [c for c in w]
    return f


def codifica(chiavi):
    d = {}
    return np.array([d.setdefault(k, len(d)) for k in chiavi], dtype=np.int64), d


def valuta_tabella(codici, y, fold, pag, P, top=None, m=M_TIRA):
    """Tabella di medie per cella, con il restringimento verso la media, provata a pieghe (addestramento = altre pieghe). Restituisce
    gli errori quadratici e le somme dei quadrati rispetto alla media di addestramento, per pagina (per il bootstrap)."""
    pred = np.zeros(len(y))
    mu_f = np.zeros(len(y))
    K = int(codici.max()) + 1
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        mu = float(y[tr].mean())
        s = np.bincount(codici[tr], weights=y[tr], minlength=K)
        c = np.bincount(codici[tr], minlength=K).astype(float)
        tab = (s + m * mu) / (c + m)
        if top is not None:
            sel = np.argsort(-np.abs(s - c * mu), kind='stable')[:top]
            t2 = np.full(K, mu)
            t2[sel] = tab[sel]
            tab = t2
        pred[te] = tab[codici[te]]
        mu_f[te] = mu
    return np.bincount(pag, weights=(y - pred) ** 2, minlength=P), np.bincount(pag, weights=(y - mu_f) ** 2, minlength=P)


def celle_top(codici, dic, y, k=10):
    """Le k celle con il maggiore contributo |somma di (y - media)| su tutti i dati: (chiave, parole, media, contributo)."""
    mu = float(y.mean())
    K = len(dic)
    s = np.bincount(codici, weights=y, minlength=K)
    c = np.bincount(codici, minlength=K).astype(float)
    contr = s - c * mu
    inv = {v: kk for kk, v in dic.items()}
    ordine = np.argsort(-np.abs(contr), kind='stable')[:k]
    tot = float(np.abs(contr).sum())
    return [(inv[int(i)], int(c[i]), float(s[i] / max(c[i], 1)), float(contr[i]), float(abs(contr[i]) / tot) if tot > 0 else 0.0) for i in ordine], mu


def rango_cella(codici, dic, y, chiave):
    """Il posto (1 = il primo) di una cella nella classifica per |contributo|; None se la cella non c'e'."""
    if chiave not in dic:
        return None
    mu = float(y.mean())
    K = len(dic)
    s = np.bincount(codici, weights=y, minlength=K)
    c = np.bincount(codici, minlength=K).astype(float)
    contr = np.abs(s - c * mu)
    return int((contr > contr[dic[chiave]]).sum() + 1)


def matrice_albero(R, glifi, top2=25):
    """Colonne per l'albero: domande si'/no sui pezzi (glifo finale e iniziale della parola prima, della parola, glifo finale della
    seconda prima, ultimi due glifi frequenti) e quattro numeri (lunghezze, posto dalla riga, posto dalla fine). Restituisce (X, nomi)."""
    w, p1, p2 = R['w'], R['p1'], R['p2']
    c2 = Counter(x[-2:] for x in w if len(x) >= 2)
    freq2 = [k for k, _ in c2.most_common(top2)]
    col, nomi = [], []

    def aggiungi(nome, v):
        nomi.append(nome)
        col.append(np.asarray(v, dtype=np.float32))
    for g in glifi:
        aggiungi(('prec.ultimo', g), [a[-1] == g for a in p1])
        aggiungi(('prec.primo', g), [a[0] == g for a in p1])
        aggiungi(('parola.primo', g), [c[0] == g for c in w])
        aggiungi(('parola.ultimo', g), [c[-1] == g for c in w])
        aggiungi(('prec2.ultimo', g), [(b is not None and b[-1] == g) for b in p2])
    for k in freq2:
        aggiungi(('prec.ultimi2', k), [a[-2:] == k for a in p1])
        aggiungi(('parola.ultimi2', k), [c[-2:] == k for c in w])
    aggiungi(('lunghezza prec', 0), [len(a) for a in p1])
    aggiungi(('lunghezza parola', 0), [len(c) for c in w])
    aggiungi(('posto', 0), R['J'])
    aggiungi(('posto dalla fine', 0), R['e'])
    return np.stack(col, axis=1), nomi


def valuta_albero(X, y, fold, pag, P, foglie, seme=0):
    """Albero di regressione a `foglie` foglie, provato a pieghe: (errori, somme dei quadrati) per pagina."""
    from sklearn.tree import DecisionTreeRegressor
    pred = np.zeros(len(y))
    mu_f = np.zeros(len(y))
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        t = DecisionTreeRegressor(max_leaf_nodes=foglie, min_samples_leaf=MIN_FOGLIA, random_state=seme).fit(X[tr], y[tr])
        pred[te] = t.predict(X[te])
        mu_f[te] = float(y[tr].mean())
    return np.bincount(pag, weights=(y - pred) ** 2, minlength=P), np.bincount(pag, weights=(y - mu_f) ** 2, minlength=P)


def albero_intero(X, y, foglie, seme=0):
    from sklearn.tree import DecisionTreeRegressor
    return DecisionTreeRegressor(max_leaf_nodes=foglie, min_samples_leaf=MIN_FOGLIA, random_state=seme).fit(X, y)


def prime_domande(albero, nomi, k=3):
    """Le domande (colonne) usate dalle prime k divisioni per importanza (indici di colonna)."""
    imp = albero.feature_importances_
    return [int(i) for i in np.argsort(-imp, kind='stable')[:k] if imp[i] > 0]
