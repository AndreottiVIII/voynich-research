# -*- coding: utf-8 -*-
"""Un attacco da manuale: sostituzione omofonica contro una lingua candidata.

L'ipotesi messa alla prova: ogni segno (glifo) del Voynich sta per una lettera
di una lingua nota; piu' segni possono stare per la stessa lettera (come nei
cifrari omofonici, o come le forme iniziali e finali di certe scritture); gli
spazi sono gli spazi fra le parole.

La chiave si cerca rendendo le parole del Voynich il piu' possibile simili a
parole di quella lingua, secondo un modello a trigrammi di lettere addestrato
sulla Bibbia della lingua. Ricerca per coordinate: si prova ogni lettera per
ogni segno e si tiene la migliore, finche' non migliora piu'; si riparte da
chiavi diverse e si tiene la migliore. Con lo stesso codice si decifrano i
controlli: testi veri cifrati con chiavi omofoniche casuali.

Il punteggio della ricerca non guarda se le parole esistono: dopo, si conta
quante parole decifrate sono parole vere della lingua, e quante coppie di
parole vicine sono coppie che la lingua usa davvero. Sono queste due cifre a
dire se una chiave ha senso.
"""
from collections import Counter

import numpy as np

BORDO = '#'


class Lingua:
    """Modello a trigrammi di lettere, vocabolario e coppie di parole di una lingua."""

    def __init__(self, parole, k=0.1):
        self.lettere = sorted(set(''.join(parole)))
        self.simboli = [BORDO] + self.lettere
        self.indice = {s: i for i, s in enumerate(self.simboli)}
        V = len(self.simboli)
        conti = np.zeros((V, V, V))
        for p, c in Counter(parole).items():
            s = [0, 0] + [self.indice[x] for x in p] + [0]
            for a, b, d in zip(s, s[1:], s[2:]):
                conti[a, b, d] += c
        contesto = conti.sum(axis=2, keepdims=True)
        lp = np.log((conti + k) / (contesto + k * V))
        # un simbolo in piu' per le posizioni vuote, che non contano
        self.lp = np.zeros((V + 1, V + 1, V + 1))
        self.lp[:V, :V, :V] = lp
        self.vuoto = V
        self.vocabolario = set(parole)
        self.coppie = set(zip(parole, parole[1:]))
        self.frequenza_lettere = Counter(''.join(parole))


class Cifrato:
    """Le parole di un testo cifrato, come sequenze di unita' (glifi)."""

    def __init__(self, parole, dividi, minimo=2):
        self.parole = parole
        self.dividi = dividi
        conti = Counter(parole)
        self.tipi = [w for w, c in conti.most_common() if c >= minimo]
        self.pesi = np.array([conti[w] for w in self.tipi], dtype=float)
        unita = [dividi(w) for w in self.tipi]
        self.unita = sorted({u for us in unita for u in us})
        self.indice = {u: i for i, u in enumerate(self.unita)}
        lmax = max(len(us) for us in unita)
        X = np.full((len(unita), lmax), -1, dtype=int)
        for i, us in enumerate(unita):
            X[i, :len(us)] = [self.indice[u] for u in us]
        self.X = X
        self.lunghezze = np.array([len(us) for us in unita])
        self.frequenza_unita = Counter(u for w in parole for u in dividi(w))


def punteggio(chiave, cif, lingua):
    """Log-verosimiglianza media per lettera delle parole decifrate."""
    T, L = cif.X.shape
    S = np.full((T, L + 3), lingua.vuoto, dtype=int)
    S[:, 0] = S[:, 1] = 0
    lettere = np.where(cif.X >= 0, chiave[np.maximum(cif.X, 0)], lingua.vuoto)
    S[:, 2:L + 2] = lettere
    S[np.arange(T), cif.lunghezze + 2] = 0
    lp = lingua.lp[S[:, :-2], S[:, 1:-1], S[:, 2:]]
    per_tipo = lp.sum(axis=1)
    return float((per_tipo * cif.pesi).sum() / (cif.pesi * (cif.lunghezze + 1)).sum())


def cerca(cif, lingua, rnd, ripartenze=8, giri=12):
    """Ricerca per coordinate con ripartenze. La prima chiave accoppia le unita'
    alle lettere per frequenza; le altre partono da quella, rimescolata."""
    lettere_freq = [lingua.indice[l] for l, _ in lingua.frequenza_lettere.most_common()]
    unita_freq = [cif.indice[u] for u, _ in cif.frequenza_unita.most_common() if u in cif.indice]
    base = np.zeros(len(cif.unita), dtype=int)
    for j, u in enumerate(unita_freq):
        base[u] = lettere_freq[min(j, len(lettere_freq) - 1)]
    tutte = np.arange(1, len(lingua.simboli))
    migliore = (-1e9, None)
    for r in range(ripartenze):
        chiave = base.copy()
        if r:
            for u in range(len(chiave)):
                if rnd.random() < 0.5:
                    chiave[u] = rnd.choice(list(tutte))
        attuale = punteggio(chiave, cif, lingua)
        for _ in range(giri):
            migliorata = False
            ordine = list(range(len(chiave)))
            rnd.shuffle(ordine)
            for u in ordine:
                vecchia = chiave[u]
                for l in tutte:
                    if l == vecchia:
                        continue
                    chiave[u] = l
                    p = punteggio(chiave, cif, lingua)
                    if p > attuale + 1e-9:
                        attuale, vecchia, migliorata = p, l, True
                chiave[u] = vecchia
            if not migliorata:
                break
        if attuale > migliore[0]:
            migliore = (attuale, chiave.copy())
    return migliore


def decifra_parola(parola, chiave, cif, lingua):
    return ''.join(lingua.simboli[chiave[cif.indice[u]]] if u in cif.indice else '?'
                   for u in cif.dividi(parola))


def valuta(righe, chiave, cif, lingua, rnd, minimo_lettere=4):
    """Quante parole decifrate sono parole vere; quante coppie di parole vicine
    sono coppie che la lingua usa, contro le stesse parole rimescolate nella riga."""
    tot = vere = lunghe = lunghe_vere = 0
    coppie = coppie_vere = mesc = mesc_vere = 0
    trovate = Counter()
    for riga in righe:
        dec = [decifra_parola(p, chiave, cif, lingua) for p in riga]
        for d in dec:
            tot += 1
            vere += d in lingua.vocabolario
            if d in lingua.vocabolario:
                trovate[d] += 1
            if len(d) >= minimo_lettere:
                lunghe += 1
                lunghe_vere += d in lingua.vocabolario
        for a, b in zip(dec, dec[1:]):
            if a in lingua.vocabolario and b in lingua.vocabolario:
                coppie += 1
                coppie_vere += (a, b) in lingua.coppie
        m = rnd.sample(dec, len(dec))
        for a, b in zip(m, m[1:]):
            if a in lingua.vocabolario and b in lingua.vocabolario:
                mesc += 1
                mesc_vere += (a, b) in lingua.coppie
    # Una chiave degenere schiaccia tutto su poche parole vere ripetute: una
    # decifrazione vera ne trova tante e diverse.
    prime3 = sum(c for _, c in trovate.most_common(3))
    return {'parole': tot, 'parole_vere': vere / tot,
            'parole_vere_diverse': len(trovate),
            'quota_tre_piu_frequenti': prime3 / vere if vere else 0.0,
            'parole_lunghe_vere': lunghe_vere / lunghe if lunghe else 0.0,
            'coppie_attestate': coppie_vere / coppie if coppie else 0.0,
            'coppie_attestate_mescolate': mesc_vere / mesc if mesc else 0.0}


def cifra_omofonico(parole, rnd, unita_per_lettera=(1, 2)):
    """Cifra un testo vero con una chiave omofonica casuale: ogni lettera riceve
    una o due unita' (u0, u1, ...) e a ogni occorrenza se ne sceglie una."""
    lettere = sorted(set(''.join(parole)))
    chiave, n = {}, 0
    for l in lettere:
        k = rnd.choice(unita_per_lettera)
        chiave[l] = ['u%d.' % (n + i) for i in range(k)]
        n += k
    return [''.join(rnd.choice(chiave[c]) for c in p) for p in parole], chiave


def dividi_unita(parola):
    """Per i testi cifrati di controllo: le unita' sono scritte 'u12.'."""
    return [x + '.' for x in parola.split('.') if x]
