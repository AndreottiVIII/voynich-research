# -*- coding: utf-8 -*-
"""Esperimento 72: al bordo della riga, scelta (S), aggiunta (A) o sostituzione (T) di un segno?

Miscela S + A + T + N (forma nuova, bigrammi di segni) stimata con EM; confronto dei modelli con la
verosimiglianza su dati esclusi (5 parti). Preregistrazione: preregistrazioni/e72.md.
Scrive risultati/e72_bordo_meccanismo.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PARTI, ITERAZIONI, LISCIATURA = 72, 5, 300, 0.5
MODELLI = OrderedDict([('S+N', 'SN'), ('S+N+A', 'SNA'), ('S+N+T', 'SNT'), ('S+N+A+T', 'SNAT')])


def bordi(righe, pulita):
    """Per ogni riga utile: (indice, parola iniziale o None, parola finale, parole interne)."""
    out = []
    for i, (inizio, ps) in enumerate(righe):
        if len(ps) < e71.MIN_PAROLE:
            continue
        ini = ps[0] if (not inizio and pulita(ps[0])) else None
        fin = ps[-1] if pulita(ps[-1]) else None
        out.append((i, ini, fin, [w for w in ps[1:-1] if pulita(w)]))
    return out


class Bigrammi:
    def __init__(self, parole):
        self.c = defaultdict(Counter)
        alfabeto = set()
        for s in parole:
            seq = ('^',) + s + ('$',)
            alfabeto.update(s)
            for a, b in zip(seq, seq[1:]):
                self.c[a][b] += 1
        self.k = len(alfabeto) + 1
        self.tot = {a: sum(x.values()) for a, x in self.c.items()}

    def p(self, s):
        seq = ('^',) + s + ('$',)
        lp = 0.0
        for a, b in zip(seq, seq[1:]):
            lp += math.log((self.c[a][b] + LISCIATURA) / (self.tot.get(a, 0) + LISCIATURA * self.k))
        return math.exp(lp)


def componenti(bordo, mezzo, lato):
    """Per ogni parola di bordo: segno di bordo, prob. S (senza s_g), A, T, N."""
    n = len(mezzo)
    pm = Counter(mezzo)
    pm = {w: c / n for w, c in pm.items()}
    massa = Counter()
    for w, p in pm.items():
        massa[w[lato]] += p
    # sostituzione: massa delle parole interne con lo stesso resto e un segno di bordo x qualsiasi
    resto = Counter()
    resto_segno = defaultdict(Counter)
    for w, p in pm.items():
        if len(w) >= 2:
            r = w[1:] if lato == 0 else w[:-1]
            resto[r] += p
            resto_segno[r][w[lato]] += p
    big = Bigrammi(mezzo)
    out = []
    for w in bordo:
        g = w[lato]
        s = pm.get(w, 0.0) / massa[g] if massa[g] else 0.0
        if len(w) >= 2:
            r = w[1:] if lato == 0 else w[:-1]
            a = pm.get(r, 0.0)
            t = resto.get(r, 0.0) - resto_segno[r][g]
        else:
            a = t = 0.0
        out.append((g, s, a, t, big.p(w)))
    return out


def em(dati, quali):
    segni = sorted({d[0] for d in dati})
    pi = {'S': 1.0 if 'S' in quali else 0.0, 'N': 1.0}
    sg = {g: 1.0 / len(segni) for g in segni}
    pa = {g: (1.0 if 'A' in quali else 0.0) / len(segni) for g in segni}
    pt = {g: (1.0 if 'T' in quali else 0.0) / len(segni) for g in segni}
    z = pi['S'] + pi['N'] + sum(pa.values()) + sum(pt.values())
    pi = {k: v / z for k, v in pi.items()}
    pa = {g: v / z for g, v in pa.items()}
    pt = {g: v / z for g, v in pt.items()}
    for _ in range(ITERAZIONI):
        rs, rn = Counter(), 0.0
        ra, rt = Counter(), Counter()
        for g, s, a, t, b in dati:
            v = (pi['S'] * sg[g] * s, pa[g] * a, pt[g] * t, pi['N'] * b)
            tot = sum(v)
            if tot <= 0:
                continue
            rs[g] += v[0] / tot
            ra[g] += v[1] / tot
            rt[g] += v[2] / tot
            rn += v[3] / tot
        n = len(dati)
        pi['S'] = sum(rs.values()) / n
        pi['N'] = rn / n
        tot_s = sum(rs.values())
        sg = {g: (rs[g] / tot_s if tot_s else 0.0) for g in segni}
        pa = {g: ra[g] / n for g in segni}
        pt = {g: rt[g] / n for g in segni}
    return pi, sg, pa, pt


def logv(dati, par):
    pi, sg, pa, pt = par
    lp = 0.0
    for g, s, a, t, b in dati:
        v = pi['S'] * sg.get(g, 0.0) * s + pa.get(g, 0.0) * a + pt.get(g, 0.0) * t + pi['N'] * b
        lp += math.log2(max(v, 1e-300))
    return lp


def analizza(righe, dividi):
    rb = bordi(righe, trascrizione.pulita)
    seg = lambda w: tuple(dividi(w))
    ris = OrderedDict()
    for nome_lato, lato, chi in (('inizio', 0, 1), ('fine', -1, 2)):
        guadagni = OrderedDict((m, 0.0) for m in MODELLI)
        n_tot = 0
        for k in range(PARTI):
            addestra = [r for r in rb if r[0] % PARTI != k]
            prova = [r for r in rb if r[0] % PARTI == k]
            # P_mid e bigrammi da tutte le parole interne (non dipendono dai bordi)
            mezzo = [seg(w) for r in rb for w in r[3]]
            d_add = componenti([seg(r[chi]) for r in addestra if r[chi]], mezzo, lato)
            d_pro = componenti([seg(r[chi]) for r in prova if r[chi]], mezzo, lato)
            base = None
            for m, quali in MODELLI.items():
                lp = logv(d_pro, em(d_add, quali))
                if m == 'S+N':
                    base = lp
                guadagni[m] += lp - base
            n_tot += len(d_pro)
        guadagni = OrderedDict((m, g / n_tot) for m, g in guadagni.items())
        tutti = componenti([seg(r[chi]) for r in rb if r[chi]], [seg(w) for r in rb for w in r[3]], lato)
        pi, sg, pa, pt = em(tutti, 'SNAT')
        ris[nome_lato] = OrderedDict([
            ('n', n_tot), ('guadagno_bit', guadagni),
            ('pesi', OrderedDict([('S', pi['S']), ('A', sum(pa.values())), ('T', sum(pt.values())), ('N', pi['N'])])),
            ('A_per_segno', sorted(((g, round(v, 3)) for g, v in pa.items() if v >= 0.01), key=lambda x: -x[1])),
            ('T_per_segno', sorted(((g, round(v, 3)) for g, v in pt.items() if v >= 0.01), key=lambda x: -x[1])),
        ])
    return ris


def una(args):
    nome, righe, quale = args
    return nome, analizza(righe, e71.lettere if quale == 'lettere' else e71.D)


def main():
    from e36_posizione_pagina import plinio
    D = e71.D
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    rv = e71.righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    latino = [w for _, ps in plinio() for w in ps]
    codificato = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(SEME))
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    rc = e71.a_capo(codificato, D, larghezze, media_voy)
    rnd = random.Random(SEME)
    aggiunta = [(i, ['s' + ps[0]] + ps[1:] if rnd.random() < 0.5 else ps) for i, ps in rc]
    rnd = random.Random(SEME + 1)
    sostituita = []
    for i, ps in rc:
        if rnd.random() < 0.5:
            u = D(ps[-1])
            if u[-1] != 'm':
                ps = ps[:-1] + [''.join(u[:-1]) + 'm']
        sostituita.append((i, ps))
    testi = OrderedDict()
    testi['Voynich'] = (rv, 'eva')
    testi['Voynich A'] = (e71.righe_voynich('A'), 'eva')
    testi['Voynich B'] = (e71.righe_voynich('B'), 'eva')
    testi['Plinio, a capo'] = (e71.a_capo(latino, e71.lettere, larghezze, media_voy), 'lettere')
    testi['Plinio codificato, a capo'] = (rc, 'eva')
    testi['Naibbe, a capo'] = (e71.a_capo(naibbe[:len(voy)], D, larghezze, media_voy), 'eva')
    testi['controllo: aggiunta "s" all\'inizio'] = (aggiunta, 'eva')
    testi['controllo: sostituzione con "m" alla fine'] = (sostituita, 'eva')
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = (e71.righe_file(os.path.join(e71.CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt')), 'eva')
    testi['modello e51, seme 19'] = (e71.righe_file(os.path.join(e71.CACHE, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt')), 'eva')
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in testi.items()]):
            ris[nome] = r
            for lato in ('inizio', 'fine'):
                x = r[lato]
                print('%-42s %-6s n %5d | guadagno A %+.3f T %+.3f AT %+.3f | pesi S %.2f A %.2f T %.2f N %.2f | A %s | T %s' % (
                    nome, lato, x['n'], x['guadagno_bit']['S+N+A'], x['guadagno_bit']['S+N+T'], x['guadagno_bit']['S+N+A+T'],
                    x['pesi']['S'], x['pesi']['A'], x['pesi']['T'], x['pesi']['N'], x['A_per_segno'][:4], x['T_per_segno'][:4]), flush=True)
    with open(os.path.join(RISULTATI, 'e72_bordo_meccanismo.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e72 — Al bordo della riga: scelta, aggiunta o sostituzione?', '',
           'Guadagno in bit per parola di bordo sul modello base S+N (scelta + forma nuova), su dati esclusi (5 parti); pesi '
           'della miscela S+N+A+T su tutti i dati. Preregistrazione: `preregistrazioni/e72.md`.', '',
           '| testo | bordo | parole | +A | +T | +A+T | S | A | T | N | segni aggiunti | segni sostituiti |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        for lato in ('inizio', 'fine'):
            x = r[lato]
            out.append('| %s | %s | %d | %+.3f | %+.3f | %+.3f | %.2f | %.2f | %.2f | %.2f | %s | %s |' % (
                nome, lato, x['n'], x['guadagno_bit']['S+N+A'], x['guadagno_bit']['S+N+T'], x['guadagno_bit']['S+N+A+T'],
                x['pesi']['S'], x['pesi']['A'], x['pesi']['T'], x['pesi']['N'],
                ', '.join('%s %.2f' % gv for gv in x['A_per_segno'][:4]), ', '.join('%s %.2f' % gv for gv in x['T_per_segno'][:4])))
    with open(os.path.join(RISULTATI, 'e72_bordo_meccanismo.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
