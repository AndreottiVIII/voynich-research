# -*- coding: utf-8 -*-
"""La disposizione: dato il sacco delle parole di una pagina e la sua impaginazione (righe, parole per riga, inizi di
paragrafo), decide in quale posto va ogni parola. Nasce dall'e400: per i giudici contano i bordi della riga (G4, G7), le
prime righe dei paragrafi (G8) e, meno, le coppie di parole vicine (G6); l'ordine delle righe quasi niente.

Il modello ha due pezzi, imparati dal Voynich:
- affinita' parola -> tipo di posto (riga prima di paragrafo o no x prima, seconda, in mezzo, ultima): regressione
  logistica multinomiale sui tratti della parola (primo segno, primi due, ultimo, ultimi due, lunghezza, prefisso e finale
  dell'e285, presenza di p e di f), non sull'identita' della parola;
- legame fra vicine nella riga: bordi (modello.legami), unione attestata, coppia esatta vista in altre pagine.
La disposizione e' un campione (scambi di Metropolis, temperatura 1) dalla distribuzione sulle permutazioni del sacco.

Strati: 'D1' solo prima riga o no; 'D2' gli 8 tipi di posto; 'D3' D2 piu' i legami.
"""
import math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure

D = misure.divisore(misure.GLIFI_EVA)
POS = ('prima', 'seconda', 'mezzo', 'ultima')
PASSATE = 60
# unione attestata: 9,16% delle coppie vicine nel Voynich, 4,85% con le parole rimescolate nella pagina (e400, O4)
UNIONE_SI, UNIONE_NO = math.log(0.0916 / 0.0485), math.log((1 - 0.0916) / (1 - 0.0485))
PESI = OrderedDict([('posto', 1.0), ('bordi', 1.0), ('unione', 1.0), ('coppia', 1.0), ('identica', 0.0)])   # identica: e401b


def posizione(j, n):
    return 0 if j == 0 else (3 if j == n - 1 else (1 if j == 1 else 2))


def tratti(w, parti):
    u = D(w)
    p = parti(w)
    return ['i1=' + u[0], 'i2=' + ''.join(u[:2]), 'f1=' + u[-1], 'f2=' + ''.join(u[-2:]), 'n=%d' % min(len(u), 9),
            'pre=' + p[0], 'fin=' + p[2], 'p=%d' % ('p' in u or 'cph' in u), 'f=%d' % ('f' in u or 'cfh' in u)]


class Disposizione:
    """rr: righe (pagina, inizio paragrafo, parole) del testo da cui si impara (il Voynich)."""

    def __init__(self, rr):
        from sklearn.linear_model import LogisticRegression
        import modello
        self.parti, self.tab = modello.legami()
        parole = [w for _, _, ps in rr for w in ps]
        self.att = set(parole)
        cf = Counter(t for w in set(parole) for t in tratti(w, self.parti))
        self.indice = {t: i for i, t in enumerate(sorted(t for t, c in cf.items() if c >= 3))}
        tipi = sorted(set(parole))
        riga_di = {w: i for i, w in enumerate(tipi)}
        # matrice sparsa (nove tratti per parola): con quella densa l'addestramento, in dieci processi insieme, non finiva
        from scipy.sparse import csr_matrix
        ri, co = [], []
        for w, i in riga_di.items():
            for t in tratti(w, self.parti):
                if t in self.indice:
                    ri.append(i)
                    co.append(self.indice[t])
        M = csr_matrix((np.ones(len(ri)), (ri, co)), shape=(len(tipi), len(self.indice)))
        X = M[[riga_di[w] for _, _, ps in rr for w in ps]]
        y8 = np.array([4 * bool(ini) + posizione(j, len(ps)) for _, ini, ps in rr for j in range(len(ps))])
        self.aff = {}
        for nome, y in (('D1', y8 // 4), ('D2', y8)):
            m = LogisticRegression(C=1.0, max_iter=2000).fit(X, y)
            lp = m.predict_log_proba(M)
            self.aff[nome] = ({w: lp[i] for w, i in riga_di.items()}, list(m.classes_))
        self.sin, self.des, self.cop = Counter(), Counter(), Counter()
        self.sin_p, self.des_p, self.cop_p = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        self.n_p = Counter()
        for p, _, ps in rr:
            for a, b in zip(ps, ps[1:]):
                self.sin[a] += 1
                self.des[b] += 1
                self.cop[(a, b)] += 1
                self.sin_p[p][a] += 1
                self.des_p[p][b] += 1
                self.cop_p[p][(a, b)] += 1
                self.n_p[p] += 1
        self.n = sum(self.n_p.values())

    def legame(self, a, b, pag, pesi):
        x = 0.0
        if pesi['bordi']:
            pa, pb = self.parti(a), self.parti(b)
            for nome, (i, j) in (('fin_fin', (2, 2)), ('fin_pre', (2, 0)), ('pre_pre', (0, 0))):
                x += pesi['bordi'] * math.log(self.tab[nome].get((pa[i], pb[j]), 1.0))
        if pesi['unione']:
            x += pesi['unione'] * (UNIONE_SI if a + b in self.att else UNIONE_NO)
        if pesi['coppia']:
            n = self.n - self.n_p[pag]
            attese = (self.sin[a] - self.sin_p[pag][a]) * (self.des[b] - self.des_p[pag][b]) / n
            viste = self.cop[(a, b)] - self.cop_p[pag][(a, b)]
            x += pesi['coppia'] * min(2.5, max(-1.5, math.log((viste + 0.5) / (attese + 0.5))))
        if a == b and pesi.get('identica'):
            x += pesi['identica']       # termine additivo per la parola uguale alla precedente (negativo = evitata)
        return x

    def pagina(self, pag, righe, rnd, strato, pesi=None, passate=PASSATE):
        """righe: [(inizio paragrafo, parole)] della pagina; restituisce le stesse righe con le parole ridisposte."""
        pesi = dict(PESI, **(pesi or {}))
        aff, classi = self.aff['D1' if strato == 'D1' else 'D2']
        col = {c: i for i, c in enumerate(classi)}
        posti = []          # (classe, indice del posto a sinistra nella riga o -1, a destra o -1)
        for ini, ps in righe:
            base, n = len(posti), len(ps)
            for j in range(n):
                c = int(bool(ini)) if strato == 'D1' else 4 * bool(ini) + posizione(j, n)
                posti.append((col[c], base + j - 1 if j > 0 else -1, base + j + 1 if j < n - 1 else -1))
        arr = [w for _, ps in righe for w in ps]
        rnd.shuffle(arr)
        N = len(arr)
        legami = strato == 'D3'
        cache = {}

        def leg(a, b):
            k = (a, b)
            if k not in cache:
                cache[k] = self.legame(a, b, pag, pesi)
            return cache[k]

        def locale(i, j):
            x = pesi['posto'] * (aff[arr[i]][posti[i][0]] + aff[arr[j]][posti[j][0]])
            if legami:
                archi = set()
                for t in (i, j):
                    if posti[t][1] >= 0:
                        archi.add((posti[t][1], t))
                    if posti[t][2] >= 0:
                        archi.add((t, posti[t][2]))
                x += sum(leg(arr[a], arr[b]) for a, b in archi)
            return x
        if N >= 2:
            for _ in range(passate * N):
                i, j = rnd.randrange(N), rnd.randrange(N)
                if i == j or arr[i] == arr[j]:
                    continue
                prima = locale(i, j)
                arr[i], arr[j] = arr[j], arr[i]
                d = locale(i, j) - prima
                if d < 0 and rnd.random() >= math.exp(d):
                    arr[i], arr[j] = arr[j], arr[i]
        out, k = [], 0
        for ini, ps in righe:
            out.append((ini, arr[k:k + len(ps)]))
            k += len(ps)
        return out

    def disponi(self, rr, seme, strato, pesi=None, passate=PASSATE):
        """rr: righe (pagina, inizio paragrafo, parole) con i sacchi da disporre; stessa impaginazione in uscita."""
        rnd = random.Random(seme)
        per = OrderedDict()
        for p, ini, ps in rr:
            per.setdefault(p, []).append((ini, ps))
        out = []
        for p, righe in per.items():
            out.extend((p, ini, ps) for ini, ps in self.pagina(p, righe, rnd, strato, pesi, passate))
        return out
