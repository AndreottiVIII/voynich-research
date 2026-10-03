# -*- coding: utf-8 -*-
"""Il corpo del voynichizzatore, giro 5 (v5): due ritocchi dopo la generazione, presi dalle scoperte del 3/10.

- circola(rr, kappa, seme): le parole rare del Voynich stanno in pagine diverse (e211, e296: R 0,57-1,96), quelle del
  generatore restano nella pagina dove nascono (R 40-56). Con probabilita' kappa un'occorrenza di una parola rara (2-5
  occorrenze nel testo generato) si scambia con un'occorrenza di un'altra parola rara di un'altra pagina della stessa
  sezione, con gli stessi segni iniziale e finale e la stessa lunghezza in segni (+-1). Conteggi globali, lunghezze delle
  righe e passaggi fra parole vicine (segno finale -> segno iniziale) restano quelli di prima.
- classi_riga(rr, f, seme): nel Voynich le 12 classi di segni facoltativi dell'e206b sono concordi dentro la riga (12 su
  12 con z > 3), nel generatore 2-3. Per ogni riga e ogni classe si estrae una forma bersaglio (lunga con la probabilita'
  della classe nel Voynich, cosi' le quote restano quelle); ogni parola della classe in disaccordo, con probabilita' f,
  passa alla compagna della coppia minima (togliendo o aggiungendo solo il segno della classe; le compagne lunghe pesate
  per frequenza nel Voynich). Diversamente dall'e252 cambia un solo segno e non sceglie la forma piu' frequente.

Con kappa 0 e f 0 il testo resta identico.
"""
import os, random, sys
from collections import Counter, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import trascrizione

MAX_RARA = 5
CHIAVE = 'stretta'   # 'larga': stessi segni iniziale e finale, lunghezza qualsiasi; 'larga+': come 'larga' e, se manca
                     # una compagna, stesso segno finale, poi qualsiasi parola rara della sezione
POSIZIONE = False    # True: si scambiano solo parole nella stessa posizione della riga (prima, in mezzo, ultima)
VICINE = 0           # > 0: la compagna sta al piu' a VICINE pagine di distanza nell'ordine del libro (e300)
_CL = {}


def circola(rr, kappa, seme):
    if not kappa:
        return rr
    import e230_generatore_meccanismi as e230
    import e206_segni_facoltativi as e206
    D = e206.D
    sez = e230.sezioni()
    rnd = random.Random(seme * 104729 + 5)
    out = [(p, ini, list(ps)) for p, ini, ps in rr]
    cnt = Counter(w for _, _, ps in out for w in ps if trascrizione.pulita(w))
    gruppi, riserva = defaultdict(list), defaultdict(list)
    ordine = {}
    for p, _, _ in out:
        ordine.setdefault(p, len(ordine))
    for i, (p, _, ps) in enumerate(out):
        for j, w in enumerate(ps):
            if trascrizione.pulita(w) and 2 <= cnt[w] <= MAX_RARA:
                u = D(w)
                s0 = (sez.get(p), (0 if j == 0 else (2 if j == len(ps) - 1 else 1))) if POSIZIONE else sez.get(p)
                gruppi[(s0, u[0], u[-1], len(u) if CHIAVE == 'stretta' else 0)].append((i, j))
                if CHIAVE == 'larga+':
                    riserva[(s0, u[-1])].append((i, j))
                    riserva[(s0,)].append((i, j))
    lontana = (lambda a, b: abs(ordine[a] - ordine[b]) > VICINE) if VICINE else (lambda a, b: False)
    usati = set()
    chiavi = list(gruppi)
    rnd.shuffle(chiavi)
    for (s, a, b, L) in chiavi:
        posti = gruppi[(s, a, b, L)]
        rnd.shuffle(posti)
        for (i, j) in posti:
            if (i, j) in usati or rnd.random() >= kappa:
                continue
            w, p = out[i][2][j], out[i][0]
            cand = []
            for LL in ((L, L - 1, L + 1) if L else (0,)):
                cand += [x for x in gruppi.get((s, a, b, LL), ()) if x not in usati and out[x[0]][0] != p and out[x[0]][2][x[1]] != w and not lontana(p, out[x[0]][0])]
                if len(cand) >= 3:
                    break
            if not cand and CHIAVE == 'larga+':
                for kk in ((s, b), (s,)):
                    cand = [x for x in riserva.get(kk, ()) if x not in usati and out[x[0]][0] != p and out[x[0]][2][x[1]] != w and not lontana(p, out[x[0]][0])]
                    if cand:
                        break
            if not cand:
                continue
            i2, j2 = rnd.choice(cand)
            out[i][2][j], out[i2][2][j2] = out[i2][2][j2], w
            usati.update(((i, j), (i2, j2)))
    return out


def _classi():
    if not _CL:
        import e206_segni_facoltativi as e206
        D = e206.D
        nomi = __import__('json').load(open(os.path.join(QUI, '..', 'risultati', 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
        voy = [w for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole for w in r.parole if trascrizione.pulita(w)]
        freq = Counter(voy)
        cl = e206.classi_di(freq)
        attestate = {w for w, n in freq.items() if n >= e206.MIN_TIPO}
        corta = defaultdict(dict)                 # parola lunga -> {classe: corta}
        lunghe = defaultdict(lambda: defaultdict(list))   # corta -> classe -> [(lunga, frequenza)]
        for w in attestate:
            u = D(w)
            for i, g in enumerate(u):
                s = ''.join(u[:i] + u[i + 1:])
                if s and s in attestate:
                    pos = 'iniziale' if i == 0 else ('finale' if i == len(u) - 1 else 'interna')
                    nome = '%s %s' % (g, pos)
                    if nome in nomi:
                        corta[w][nome] = s
                        lunghe[s][nome].append((w, freq[w]))
        quota = {}
        for nome in nomi:
            n1 = n0 = 0
            for w, d in cl.items():
                for c, v in d.items():
                    if '%s %s' % c == nome:
                        n1 += v * freq[w]
                        n0 += (1 - v) * freq[w]
            quota[nome] = n1 / (n1 + n0) if n1 + n0 else 0.5
        _CL.update(nomi=nomi, corta=corta, lunghe=lunghe, quota=quota)
    return _CL


def classi_riga(rr, f, seme):
    if not f:
        return rr
    k = _classi()
    rnd = random.Random(seme * 15485863 + 11)
    out = []
    for p, ini, ps in rr:
        bers = {nome: rnd.random() < k['quota'][nome] for nome in k['nomi']}
        nuova = []
        for w in ps:
            if trascrizione.pulita(w):
                opz = [('c', nome, s) for nome, s in k['corta'].get(w, {}).items() if not bers[nome]]
                opz += [('l', nome, ll) for nome, ll in k['lunghe'].get(w, {}).items() if bers[nome]]
                if opz and rnd.random() < f:
                    tipo, nome, x = rnd.choice(opz)
                    if tipo == 'c':
                        w = x
                    else:
                        w = rnd.choices([a for a, _ in x], [b for _, b in x])[0]
            nuova.append(w)
        out.append((p, ini, nuova))
    return out
