# -*- coding: utf-8 -*-
"""Modello del Voynich, seconda forma (3/10/2026, sera). Al posto del generatore "copia e modifica la pagina": un modello
che dice da dove vengono le parole e quale viene scelta, con i pesi imparati dal testo.

1. DA DOVE (mescolanza di fonti, pesi per massima verosimiglianza sul Voynich, per gruppo tipo di riga x posizione):
   memoria   le parole gia' scritte nella pagina (la pagina si ripete: omogeneita', coppie identiche)
   vicine    le parole delle due pagine precedenti (e300, e300b, e304: il lessico e le varianti cambiano nel tempo)
   coppia    le parole che seguono la parola precedente nella stessa riga, nel resto del libro (e285; e295: dentro la riga)
   sezione   il lessico della sezione per tipo di riga (prima di paragrafo o no) e posizione (prima, in mezzo, ultima)
             (e273, e302: le prime righe sono un registro a parte)
   posizione lo stesso senza la sezione
   libro     il lessico di tutto il libro
   nuova     una parola che non c'e' nel Voynich: variante di una modifica di una parola della componente "posizione"
             (e296: le parole rare sono errori su parole frequenti)
   In apprendimento le componenti coppia, sezione, posizione e libro si contano senza la pagina della parola, memoria e
   vicine guardano solo indietro: il modello non vede la pagina che sta scrivendo (il primo prototipo, che usava il
   lessico della pagina vera, confondeva "lessico della pagina" e "memoria" e generava pagine troppo varie: 0,836 tipi su
   parole contro 0,756).
2. QUALE (scelta fra K candidate estratte dalla mescolanza, con peso prodotto dei legami ai bordi con la parola
   precedente della riga, imparati dal Voynich: finale->finale, finale->prefisso, prefisso->prefisso, parti dell'e285;
   e294: le parole vicine si legano per i bordi). Gli esponenti beta si regolano perche' i legami del testo generato
   siano quelli del Voynich.

    python voynichizzatore/modello.py            # stima i pesi e li scrive in modello_pesi.json
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure, trascrizione

D = misure.divisore(misure.GLIFI_EVA)
COMP = ('memoria', 'vicine', 'coppia', 'sezione', 'posizione', 'libro', 'nuova')
EPS = 1e-5
PESI = os.path.join(QUI, 'modello_pesi.json')
K = 16
MEMORIA_RIGHE_PRECEDENTI = True   # e303: nella riga le parole si evitano; la memoria e' quella delle righe sopra
BETA = OrderedDict([('fin_fin', 1.0), ('fin_pre', 1.0), ('pre_pre', 1.0)])


def posclasse(j, n):
    return 'prima' if j == 0 else ('ultima' if j == n - 1 else 'mezzo')


class Voynich:
    """Il testo in righe (pagina, inizio paragrafo, parole pulite, sezione, lingua) con le occorrenze per contesto."""

    def __init__(self):
        righe = []
        for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
            ws = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
            if ws:
                righe.append((r.pagina, bool(r.inizio_par), ws, r.sezione, r.lingua or '?'))
        self.righe = righe
        self.pagine = list(OrderedDict((p, 1) for p, *_ in righe))
        self.per_pag = defaultdict(list)
        for i, (p, *_r) in enumerate(righe):
            self.per_pag[p].append(i)
        self.occ = {'coppia': defaultdict(list), 'sezione': defaultdict(list), 'posizione': defaultdict(list), 'libro': defaultdict(list)}
        self.cnt = Counter()
        for p, ini, ws, s, _ in righe:
            n = len(ws)
            for j, w in enumerate(ws):
                self.cnt[w] += 1
                pc = posclasse(j, n)
                self.occ['sezione'][(s, ini, pc)].append((w, p))
                self.occ['posizione'][(ini, pc)].append((w, p))
                self.occ['libro'][0].append((w, p))
                if j > 0:
                    self.occ['coppia'][ws[j - 1]].append((w, p))
        self.conta = {}
        for nome, occ in self.occ.items():
            tot, per_pag, tot_ctx, ctx_pag = {}, {}, {}, {}
            for k, lst in occ.items():
                tot[k] = Counter(w for w, _ in lst)
                cp = defaultdict(Counter)
                for w, p in lst:
                    cp[p][w] += 1
                per_pag[k] = cp
                tot_ctx[k] = len(lst)
                ctx_pag[k] = Counter(p for _, p in lst)
            self.conta[nome] = (tot, per_pag, tot_ctx, ctx_pag)
        self.pag_cnt = {p: Counter(w for i in idx for w in self.righe[i][2]) for p, idx in self.per_pag.items()}

    def p_ctx(self, nome, k, w, p):
        tot, per_pag, tot_ctx, ctx_pag = self.conta[nome]
        if k not in tot:
            return None
        den = tot_ctx[k] - ctx_pag[k][p]
        if den <= 0:
            return None
        return (tot[k][w] - per_pag[k][p][w]) / den


def tabella(v):
    gruppi, X = [], []
    for ip, p in enumerate(v.pagine):
        prec = [w for q in v.pagine[max(0, ip - 2):ip] for i in v.per_pag[q] for w in v.righe[i][2]]
        cprec = Counter(prec)
        cpag = v.pag_cnt[p]
        gia, ngia = Counter(), 0
        for i in v.per_pag[p]:
            _, ini, ws, s, _ = v.righe[i]
            n = len(ws)
            if MEMORIA_RIGHE_PRECEDENTI:
                gia_r, ngia_r = Counter(gia), ngia
            for j, w in enumerate(ws):
                pc = posclasse(j, n)
                riga = [np.nan] * len(COMP)
                if MEMORIA_RIGHE_PRECEDENTI:
                    riga[0] = gia_r[w] / ngia_r if ngia_r else np.nan
                else:
                    riga[0] = gia[w] / ngia if ngia else np.nan
                riga[1] = cprec[w] / len(prec) if prec else np.nan
                if j > 0:
                    x = v.p_ctx('coppia', ws[j - 1], w, p)
                    riga[2] = np.nan if x is None else x
                x = v.p_ctx('sezione', (s, ini, pc), w, p)
                riga[3] = np.nan if x is None else x
                x = v.p_ctx('posizione', (ini, pc), w, p)
                riga[4] = np.nan if x is None else x
                riga[5] = v.p_ctx('libro', 0, w, p)
                riga[6] = EPS if v.cnt[w] - cpag[w] == 0 else 0.0
                gruppi.append((ini, pc))
                X.append(riga)
                gia[w] += 1
                ngia += 1
    return gruppi, np.array(X, dtype=float)


def adatta(v=None):
    from scipy.optimize import minimize
    v = v or Voynich()
    gruppi, X = tabella(v)
    out = OrderedDict()
    for g in sorted(set(gruppi), key=str):
        sel = np.array([x == g for x in gruppi])
        P = X[sel]
        A = ~np.isnan(P)
        P0 = np.nan_to_num(P)

        def nll(th):
            l = np.exp(th - th.max())
            return -np.log(np.maximum((P0 * l).sum(1) / (A * l).sum(1), 1e-300)).sum()
        r = minimize(nll, np.zeros(len(COMP)), method='L-BFGS-B')
        l = np.exp(r.x - r.x.max())
        out['%s|%s' % g] = OrderedDict([('pesi', OrderedDict(zip(COMP, (l / l.sum()).tolist()))), ('parole', int(sel.sum())),
                                        ('nll_per_parola', float(r.fun / sel.sum()))])
    json.dump(out, open(PESI, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out


_LEG = {}


def legami():
    """parti(w) dell'e285 e le tre tabelle dei legami fra parole vicine nella riga del Voynich: rapporto fra frequenza
    osservata e attesa con le parti indipendenti, fra 0,2 e 5 (coppie con meno di 5 attese -> 1)."""
    if not _LEG:
        import e249_pezzi_simboli as e249
        import e285_pezzi_contesto as e285
        voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
        taglia = e249.segmentatore([w for r in voy for w in r])
        cache = {}

        def parti(w):
            if w not in cache:
                cache[w] = e285.parti(taglia, w)
            return cache[w]
        tab = {}
        for nome, (i, j) in (('fin_fin', (2, 2)), ('fin_pre', (2, 0)), ('pre_pre', (0, 0))):
            coppie = [(parti(a)[i], parti(b)[j]) for r in voy for a, b in zip(r, r[1:])]
            n = len(coppie)
            cxy, cx, cy = Counter(coppie), Counter(a for a, _ in coppie), Counter(b for _, b in coppie)
            t = {}
            for a in cx:
                for b in cy:
                    e = cx[a] * cy[b] / n
                    if e >= 5:
                        t[(a, b)] = min(5.0, max(0.2, cxy[(a, b)] / e))
            tab[nome] = t
        _LEG.update(parti=parti, tab=tab)
    return _LEG['parti'], _LEG['tab']


_V = {}


def genera(seme, pesi=None, forza=None, beta=None, k=K):
    """Un manoscritto con l'impaginazione del Voynich (pagine, righe, parole per riga, inizi di paragrafo).
    forza: {componente: moltiplicatore del peso}; beta: esponenti dei legami (BETA se None)."""
    import e234_tema_variato as e234
    import e251_lessico_sezione as e251
    if 'v' not in _V:
        _V['v'] = Voynich()
    v = _V['v']
    pesi = pesi or json.load(open(PESI, encoding='utf-8'))
    beta = BETA if beta is None else beta
    parti, tab = legami()
    c2 = e251._prepara()['c2']
    rnd = random.Random(seme)
    out, generate = [], OrderedDict()

    def da_occ(lst, p):
        for _ in range(30):
            w, q = lst[rnd.randrange(len(lst))]
            if q != p:
                return w
        return None

    def nuova(ini, pc, p):
        for _ in range(10):
            base = da_occ(v.occ['posizione'][(ini, pc)], p)
            w = e234.forza_variante(base, c2['mod'], rnd, 0.4, c2['att'], c2['D']) if base else None
            if w and w not in v.cnt:
                return w
        return None

    def legame(a, b):
        pa, pb = parti(a), parti(b)
        x = 1.0
        for nome, (i, j) in (('fin_fin', (2, 2)), ('fin_pre', (2, 0)), ('pre_pre', (0, 0))):
            if beta.get(nome):
                x *= tab[nome].get((pa[i], pb[j]), 1.0) ** beta[nome]
        return x
    for ip, p in enumerate(v.pagine):
        prec = [w for q in v.pagine[max(0, ip - 2):ip] for w in generate.get(q, [])]
        gia = []
        for i in v.per_pag[p]:
            _, ini, ws, s, _ = v.righe[i]
            n = len(ws)
            riga = []
            for j in range(n):
                pc = posclasse(j, n)
                lam = pesi['%s|%s' % (ini, pc)]['pesi']
                mem = gia[:len(gia) - j] if MEMORIA_RIGHE_PRECEDENTI else gia
                disp = {'memoria': bool(mem), 'vicine': bool(prec), 'coppia': j > 0 and riga[-1] in v.occ['coppia'],
                        'sezione': (s, ini, pc) in v.occ['sezione'], 'posizione': True, 'libro': True, 'nuova': True}
                nomi = [c for c in COMP if disp[c]]
                pp = [lam[c] * (forza or {}).get(c, 1.0) for c in nomi]
                cand = []
                for _ in range(k if j > 0 else 1):
                    w = None
                    for _t in range(5):
                        c = rnd.choices(nomi, pp)[0]
                        if c == 'memoria':
                            w = rnd.choice(mem)
                        elif c == 'vicine':
                            w = rnd.choice(prec)
                        elif c == 'coppia':
                            w = da_occ(v.occ['coppia'][riga[-1]], p)
                        elif c == 'sezione':
                            w = da_occ(v.occ['sezione'][(s, ini, pc)], p)
                        elif c == 'posizione':
                            w = da_occ(v.occ['posizione'][(ini, pc)], p)
                        elif c == 'libro':
                            w = da_occ(v.occ['libro'][0], p)
                        else:
                            w = nuova(ini, pc, p)
                        if w:
                            break
                    cand.append(w or da_occ(v.occ['libro'][0], p))
                if len(cand) > 1:
                    w = rnd.choices(cand, [legame(riga[-1], x) for x in cand])[0]
                else:
                    w = cand[0]
                riga.append(w)
                gia.append(w)
            out.append((p, ini, riga))
        generate[p] = gia
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for g, x in adatta().items():
        print('%-14s %5d parole, nll %.3f | %s' % (g, x['parole'], x['nll_per_parola'], {k: round(p, 3) for k, p in x['pesi'].items()}))
