# -*- coding: utf-8 -*-
"""Modello del Voynich (3/10/2026, sera): al posto del generatore "copia e modifica la pagina", una mescolanza di
componenti, ognuna legata a una proprieta' trovata negli esperimenti, con i pesi imparati dal testo per massima
verosimiglianza. Ogni parola si sceglie cosi': si estrae una componente con i pesi del suo gruppo (tipo di riga x
posizione nella riga), poi una parola da quella componente.

Componenti (P_k(parola | contesto)):
  pagina    il lessico della pagina vera (come il "pool" dei generatori precedenti; in apprendimento senza la parola stessa)
  coppia    le parole che seguono la parola precedente nella stessa riga, nel resto del libro (e285, e295: dentro la riga)
  bordo     le parole che seguono una parola con lo stesso segno finale, nel resto del libro (e294: bordi legati)
  memoria   le parole gia' scritte nella pagina (omogeneita', gradiente piatto)
  vicine    le parole delle due pagine precedenti (e300, e300b: pagine consecutive simili)
  sezione   il lessico della sezione per tipo di riga (prima di paragrafo o no) e posizione (prima, in mezzo, ultima)
  posizione lo stesso senza la sezione
  libro     il lessico di tutto il libro (senza la pagina)
  sopra     le parole della riga sopra nelle posizioni j-1, j, j+1 (verticale)
  nuova     una parola nuova: variante di una modifica di una parola presa dalla componente "posizione" (e296: errori
            sparsi su parole frequenti); in apprendimento vale EPS per le parole che non compaiono altrove.

In apprendimento ogni componente si calcola senza la pagina della parola (tranne "pagina", senza la sola parola, e
"memoria"/"sopra", che guardano solo indietro): il modello non impara a copiare la pagina che sta scrivendo. Lo stesso
vale nella generazione per coppia, bordo, sezione e posizione (occorrenze della stessa pagina escluse).

    python voynichizzatore/modello.py            # adatta i pesi e li stampa
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure, trascrizione

D = misure.divisore(misure.GLIFI_EVA)
COMP = ('pagina', 'coppia', 'bordo', 'memoria', 'vicine', 'sezione', 'posizione', 'libro', 'sopra', 'nuova')
EPS = 1e-5
PESI = os.path.join(QUI, 'modello_pesi.json')


def posclasse(j, n):
    return 'prima' if j == 0 else ('ultima' if j == n - 1 else 'mezzo')


class Voynich:
    """Il testo in righe (pagina, inizio paragrafo, parole pulite) con sezione e lingua, e i conteggi."""

    def __init__(self):
        righe = []
        for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
            ws = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
            if ws:
                righe.append((r.pagina, bool(r.inizio_par), ws, r.sezione, r.lingua or '?'))
        self.righe = righe
        self.pagine = list(OrderedDict((p, 1) for p, *_ in righe))
        self.sez = {p: s for p, _, _, s, _ in righe}
        self.per_pag = defaultdict(list)
        for i, (p, *_rest) in enumerate(righe):
            self.per_pag[p].append(i)
        # occorrenze (parola, pagina) per contesto
        self.occ_coppia = defaultdict(list)
        self.occ_bordo = defaultdict(list)
        self.occ_sez = defaultdict(list)
        self.occ_pos = defaultdict(list)
        self.occ_tutte = []
        self.cnt = Counter()
        for p, ini, ws, s, _ in righe:
            n = len(ws)
            for j, w in enumerate(ws):
                self.cnt[w] += 1
                self.occ_tutte.append((w, p))
                pc = posclasse(j, n)
                self.occ_sez[(s, ini, pc)].append((w, p))
                self.occ_pos[(ini, pc)].append((w, p))
                if j > 0:
                    self.occ_coppia[ws[j - 1]].append((w, p))
                    self.occ_bordo[D(ws[j - 1])[-1]].append((w, p))
        self.conta = {}
        for nome, occ in (('coppia', self.occ_coppia), ('bordo', self.occ_bordo), ('sez', self.occ_sez), ('pos', self.occ_pos)):
            tot, per_pag, tot_ctx, ctx_pag = {}, {}, {}, {}
            for k, lst in occ.items():
                c = Counter(w for w, _ in lst)
                cp = defaultdict(Counter)
                for w, p in lst:
                    cp[p][w] += 1
                tot[k], per_pag[k] = c, cp
                tot_ctx[k] = len(lst)
                ctx_pag[k] = Counter(p for _, p in lst)
            self.conta[nome] = (tot, per_pag, tot_ctx, ctx_pag)
        self.pag_cnt = {p: Counter(w for i in idx for w in self.righe[i][2]) for p, idx in self.per_pag.items()}

    def p_ctx(self, nome, k, w, p):
        """P(w | contesto k) nel resto del libro (senza la pagina p); None se il contesto e' vuoto fuori da p."""
        tot, per_pag, tot_ctx, ctx_pag = self.conta[nome]
        if k not in tot:
            return None
        den = tot_ctx[k] - ctx_pag[k][p]
        if den <= 0:
            return None
        return (tot[k][w] - per_pag[k][p][w]) / den


def tabella(v):
    """Per ogni parola del Voynich: gruppo (tipo di riga, posizione) e le probabilita' delle componenti (nan = assente)."""
    gruppi, X = [], []
    for ip, p in enumerate(v.pagine):
        idx = v.per_pag[p]
        prec = [w for q in v.pagine[max(0, ip - 2):ip] for i in v.per_pag[q] for w in v.righe[i][2]]
        cprec = Counter(prec)
        cpag = v.pag_cnt[p]
        npag = sum(cpag.values())
        gia = Counter()
        ngia = 0
        sopra = None
        for i in idx:
            _, ini, ws, s, _ = v.righe[i]
            n = len(ws)
            for j, w in enumerate(ws):
                pc = posclasse(j, n)
                riga = [np.nan] * len(COMP)
                riga[0] = (cpag[w] - 1) / (npag - 1) if npag > 1 else np.nan
                if j > 0:
                    x = v.p_ctx('coppia', ws[j - 1], w, p)
                    riga[1] = np.nan if x is None else x
                    x = v.p_ctx('bordo', D(ws[j - 1])[-1], w, p)
                    riga[2] = np.nan if x is None else x
                riga[3] = gia[w] / ngia if ngia else np.nan
                riga[4] = cprec[w] / len(prec) if prec else np.nan
                x = v.p_ctx('sez', (s, ini, pc), w, p)
                riga[5] = np.nan if x is None else x
                x = v.p_ctx('pos', (ini, pc), w, p)
                riga[6] = np.nan if x is None else x
                altrove = v.cnt[w] - cpag[w]
                riga[7] = altrove / (len(v.occ_tutte) - npag)
                if sopra:
                    vic = [sopra[t] for t in (j - 1, j, j + 1) if 0 <= t < len(sopra)]
                    riga[8] = sum(x == w for x in vic) / len(vic) if vic else np.nan
                riga[9] = EPS if (altrove == 0 and cpag[w] == 1) else 0.0
                gruppi.append((ini, pc))
                X.append(riga)
                gia[w] += 1
                ngia += 1
            sopra = ws
    return gruppi, np.array(X, dtype=float)


def adatta(v=None):
    """Pesi delle componenti per gruppo (tipo di riga, posizione), per massima verosimiglianza (componenti assenti escluse
    e pesi rinormalizzati parola per parola)."""
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
            num = (P0 * l).sum(1)
            den = (A * l).sum(1)
            return -np.log(np.maximum(num / den, 1e-300)).sum()
        r = minimize(nll, np.zeros(len(COMP)), method='L-BFGS-B')
        l = np.exp(r.x - r.x.max())
        out['%s|%s' % g] = OrderedDict([('pesi', OrderedDict(zip(COMP, (l / l.sum()).tolist()))), ('parole', int(sel.sum())),
                                        ('nll_per_parola', float(r.fun / sel.sum()))])
    json.dump(out, open(PESI, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out


_V = {}


def genera(seme, pesi=None, forza=None):
    """Un manoscritto con la stessa impaginazione del Voynich (pagine, righe, parole per riga, inizi di paragrafo).
    forza: {componente: moltiplicatore del peso} per le prove."""
    import e234_tema_variato as e234
    import e251_lessico_sezione as e251
    if 'v' not in _V:
        _V['v'] = Voynich()
    v = _V['v']
    pesi = pesi or json.load(open(PESI, encoding='utf-8'))
    c2 = e251._prepara()['c2']
    rnd = random.Random(seme)
    out = []
    generate = OrderedDict()

    def da_occ(lst, p):
        for _ in range(30):
            w, q = lst[rnd.randrange(len(lst))]
            if q != p:
                return w
        return None
    for ip, p in enumerate(v.pagine):
        idx = v.per_pag[p]
        vera = [w for i in idx for w in v.righe[i][2]]
        prec = [w for q in v.pagine[max(0, ip - 2):ip] for w in generate.get(q, [])]
        gia, sopra = [], None
        for i in idx:
            _, ini, ws, s, _ = v.righe[i]
            n = len(ws)
            riga = []
            for j in range(n):
                pc = posclasse(j, n)
                lam = pesi['%s|%s' % (ini, pc)]['pesi']
                disp = OrderedDict()
                disp['pagina'] = True
                disp['coppia'] = j > 0 and riga[-1] in v.occ_coppia
                disp['bordo'] = j > 0
                disp['memoria'] = bool(gia)
                disp['vicine'] = bool(prec)
                disp['sezione'] = (s, ini, pc) in v.occ_sez
                disp['posizione'] = True
                disp['libro'] = True
                disp['sopra'] = bool(sopra)
                disp['nuova'] = True
                nomi = [k for k in COMP if disp[k]]
                pp = [lam[k] * (forza or {}).get(k, 1.0) for k in nomi]
                w = None
                for _ in range(5):
                    k = rnd.choices(nomi, pp)[0]
                    if k == 'pagina':
                        w = rnd.choice(vera)
                    elif k == 'coppia':
                        w = da_occ(v.occ_coppia[riga[-1]], p)
                    elif k == 'bordo':
                        lst = v.occ_bordo.get(D(riga[-1])[-1])
                        w = da_occ(lst, p) if lst else None
                    elif k == 'memoria':
                        w = rnd.choice(gia)
                    elif k == 'vicine':
                        w = rnd.choice(prec)
                    elif k == 'sezione':
                        w = da_occ(v.occ_sez[(s, ini, pc)], p)
                    elif k == 'posizione':
                        w = da_occ(v.occ_pos[(ini, pc)], p)
                    elif k == 'libro':
                        w = da_occ(v.occ_tutte, p)
                    elif k == 'sopra':
                        vic = [sopra[t] for t in (j - 1, j, j + 1) if 0 <= t < len(sopra)]
                        w = rnd.choice(vic) if vic else None
                    else:
                        base = da_occ(v.occ_pos[(ini, pc)], p)
                        w = e234.forza_variante(base, c2['mod'], rnd, 0.4, c2['att'], c2['D']) if base else None
                    if w:
                        break
                riga.append(w or rnd.choice(vera))
            gia += riga
            sopra = riga
            out.append((p, ini, riga))
        generate[p] = gia
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for g, x in adatta().items():
        print('%-14s %5d parole, nll %.3f | %s' % (g, x['parole'], x['nll_per_parola'], {k: round(p, 3) for k, p in x['pesi'].items()}))
