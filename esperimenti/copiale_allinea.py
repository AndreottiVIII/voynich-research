# -*- coding: utf-8 -*-
"""Allineamento simbolo per simbolo fra la trascrizione del cifrario Copiale e il testo decifrato (Knight, Megyesi,
Schaefer 2011; file dell'Università di Stoccolma in dati/cache/copiale, non committati). Le righe dei due file
corrispondono una a una. Le lettere romane semplici (a – z, A – Z) sono spazi o lettere senza valore (articolo, §5);
gli altri simboli valgono una lettera, due o tre (sch, ss, st, ch, en/em), oppure ripetono la consonante prima (:).
L'allineamento si impara a giri (EM "duro" con programmazione dinamica monotona riga per riga).

Uso: righe, pagine, chiave = copiale_allinea.carica()
"""
import math, os, re
from collections import Counter, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
CARTELLA = os.path.join(QUI, '..', 'dati', 'cache', 'copiale')
GIRI = 10
SALTO = 9.0  # costo di un'unità del chiaro lasciata senza simbolo


def spazio(s):
    return len(s) == 1 and s.isalpha() and s.isascii()


def leggi():
    """[(pagina, simboli, unità del chiaro)] riga per riga; le unità sono caratteri, spazi o logogrammi *xx*."""
    t = open(os.path.join(CARTELLA, 'copiale-transcription.txt'), encoding='utf-8').read().split('\n')
    d = open(os.path.join(CARTELLA, 'copiale-deciphered.txt'), encoding='latin-1').read().split('\n')
    tt, pt = [], []
    pag = None
    for l in t:
        l = l.strip()
        m = re.match(r'##\s*PAGE\s*(\S+)', l)
        if m:
            pag = m.group(1)
        elif l and not l.startswith('##'):
            tt.append((pag, l))
    dd = [l.strip() for l in d if l.strip() and not l.strip().startswith('##')]
    assert len(tt) == len(dd), (len(tt), len(dd))
    out = []
    for (pag, a), b in zip(tt, dd):
        simboli = a.split()
        unita = re.findall(r'\*[^*]+\*|.', b)
        unita = [' ' if u.isspace() else u for u in unita]
        # spazi multipli in uno
        uu = []
        for u in unita:
            if u == ' ' and uu and uu[-1] == ' ':
                continue
            uu.append(u)
        out.append((pag, simboli, tuple(uu)))
    return out


def costo(P, s, e):
    p = P[s].get(e)
    if p is not None:
        return -math.log(p)
    n = len(e)
    base = {0: 6.0, 1: 7.0, 2: 10.0, 3: 13.0}.get(n, 20.0)
    if spazio(s) and e != (' ',):
        base += 4.0
    return base


def allinea(simboli, unita, P):
    """Programmazione dinamica: ogni simbolo emette 0 – 3 unità (un logogramma vale da solo); unità saltate costano SALTO."""
    n, m = len(simboli), len(unita)
    INF = float('inf')
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            v = D[i][j]
            if v == INF:
                continue
            if j < m and v + SALTO < D[i][j + 1]:
                D[i][j + 1], B[i][j + 1] = v + SALTO, (i, j, None)
            if i < n:
                s = simboli[i]
                for k in range(0, 4):
                    if j + k > m:
                        break
                    e = tuple(unita[j:j + k])
                    if k > 1 and any(len(u) > 1 for u in e):
                        break
                    c = v + costo(P, s, e)
                    if c < D[i + 1][j + k]:
                        D[i + 1][j + k], B[i + 1][j + k] = c, (i, j, e)
    coppie = []
    i, j = n, m
    while (i, j) != (0, 0):
        pi, pj, e = B[i][j]
        if e is not None:
            coppie.append((pi, pj, e))
        i, j = pi, pj
    coppie.reverse()
    return coppie, D[n][m]


def stima(conti):
    P = {}
    for s, c in conti.items():
        tot = sum(c.values()) + 1.0
        P[s] = {e: x / tot for e, x in c.items()}
    return defaultdict(dict, P)


def impara(righe, giri=GIRI):
    P = defaultdict(dict)
    for _, simboli, _ in righe:
        for s in simboli:
            if spazio(s):
                P[s] = {(' ',): 0.9, (): 0.09}
    allineamenti = None
    for g in range(giri):
        conti = defaultdict(Counter)
        allineamenti = []
        tot = 0.0
        for _, simboli, unita in righe:
            cp, c = allinea(simboli, unita, P)
            tot += c
            allineamenti.append(cp)
            for i, _, e in cp:
                conti[simboli[i]][e] += 1
        P = stima(conti)
    return P, allineamenti


def chiave(P):
    """Valore principale di ogni simbolo e sua quota."""
    out = {}
    for s, d in P.items():
        if d:
            e, p = max(d.items(), key=lambda z: z[1])
            out[s] = (''.join(e), p / sum(d.values()))
    return out


def carica():
    righe = leggi()
    P, al = impara(righe)
    return righe, al, chiave(P)


if __name__ == '__main__':
    import sys
    righe, al, k = carica()
    per_lettera = defaultdict(list)
    for s, (e, q) in k.items():
        per_lettera[e].append((s, round(q, 2)))
    conta = Counter(s for _, ss, _ in righe for s in ss)
    for e in sorted(per_lettera, key=lambda z: -sum(conta[s] for s, _ in per_lettera[z])):
        print(repr(e), sorted(per_lettera[e], key=lambda z: -conta[z[0]]), [conta[s] for s, _ in sorted(per_lettera[e], key=lambda z: -conta[z[0]])])
