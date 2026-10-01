# -*- coding: utf-8 -*-
"""Esperimento 112: risolutore a sillabe (trigrammi Witten-Bell, ricottura alla Gibbs) sul controllo: il Macer cifrato
in sillabe con varianti (e104), mu = 0 / 0,3 / 0,6. Prova di fattibilita'.

Preregistrazione: preregistrazioni/e112.md. Scrive risultati/e112_risolutore_sillabe.json e .md.
"""
import json, math, os, random, re, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MU = (0.0, 0.3, 0.6)
GIRI, T0, T1, RIPARTENZE, TOP, CASUALI = 40, 2.0, 0.05, 2, 150, 50
INIZIO, FINE, RARA = '<s>', '</s>', '<rara>'


# ------------------------------------------------------------ modello di sillabe

class Modello:
    def __init__(self, righe):
        c = Counter(s for r in righe for s in r)
        self.voc = {s for s, k in c.items() if k >= 2}
        righe = [[s if s in self.voc else RARA for s in r] for r in righe]
        self.c1, self.c2, self.c3 = Counter(), Counter(), Counter()
        self.ctx1, self.ctx2 = Counter(), Counter()
        self.seg1, self.seg2 = defaultdict(set), defaultdict(set)
        for r in righe:
            x = [INIZIO, INIZIO] + r + [FINE]
            for i in range(2, len(x)):
                a, b, s = x[i - 2], x[i - 1], x[i]
                self.c1[s] += 1
                self.c2[(b, s)] += 1
                self.ctx1[b] += 1
                self.seg1[b].add(s)
                self.c3[(a, b, s)] += 1
                self.ctx2[(a, b)] += 1
                self.seg2[(a, b)].add(s)
        self.n1 = sum(self.c1.values())
        self.V = len(self.c1) + 1
        self.t1 = {k: len(v) for k, v in self.seg1.items()}
        self.t2 = {k: len(v) for k, v in self.seg2.items()}
        self.sillabe = [s for s, _ in self.c1.most_common() if s not in (FINE, RARA)]

    def logp(self, a, b, s):
        k = (a, b, s)
        p1 = (self.c1[s] + 0.5) / (self.n1 + 0.5 * self.V)
        n, t = self.ctx1.get(b, 0), self.t1.get(b, 0)
        p2 = (self.c2[(b, s)] + t * p1) / (n + t) if n else p1
        n, t = self.ctx2.get((a, b), 0), self.t2.get((a, b), 0)
        p3 = (self.c3[k] + t * p2) / (n + t) if n else p2
        return math.log(p3)


# ------------------------------------------------------------ risolutore

class Cifrato:
    def __init__(self, righe):
        self.righe = righe
        self.simboli = sorted({x for r in righe for x in r})
        self.pos = defaultdict(list)
        for i, r in enumerate(righe):
            for j, x in enumerate(r):
                self.pos[x].append((i, j))
        self.freq = Counter(x for r in righe for x in r)


def termini(cif, chiave, mod, toccati):
    tot = 0.0
    for (i, j) in toccati:
        r = cif.righe[i]
        s = chiave[r[j]] if j < len(r) else FINE
        a = chiave[r[j - 2]] if j >= 2 else INIZIO
        b = chiave[r[j - 1]] if j >= 1 else INIZIO
        tot += mod.logp(a, b, s)
    return tot


def toccati_da(cif, x):
    out = set()
    for (i, j) in cif.pos[x]:
        L = len(cif.righe[i])
        for k in (j, j + 1, j + 2):
            if k <= L:
                out.add((i, k))
    return out


def punteggio_totale(cif, chiave, mod):
    tutti = {(i, k) for i, r in enumerate(cif.righe) for k in range(len(r) + 1)}
    return termini(cif, chiave, mod, tutti)


def partenza(cif, mod):
    """Quantili di frequenza: simbolo -> sillaba alla stessa frequenza cumulata."""
    simb = sorted(cif.simboli, key=lambda x: -cif.freq[x])
    ns = sum(cif.freq.values())
    syl = mod.sillabe
    cum_s, acc = [], 0
    tot_m = sum(mod.c1[s] for s in syl)
    for s in syl:
        acc += mod.c1[s] / tot_m
        cum_s.append(acc)
    chiave, acc, j = {}, 0.0, 0
    for x in simb:
        centro = acc + cif.freq[x] / ns / 2
        while j < len(syl) - 1 and cum_s[j] < centro:
            j += 1
        chiave[x] = syl[j]
        acc += cif.freq[x] / ns
    return chiave


def risolvi(cif, mod, seme):
    rnd = random.Random(seme)
    chiave = partenza(cif, mod)
    toccati = {x: toccati_da(cif, x) for x in cif.simboli}
    alte = mod.sillabe[:TOP]
    for giro in range(GIRI):
        T = T0 * (T1 / T0) ** (giro / max(1, GIRI - 1))
        ordine = cif.simboli[:]
        rnd.shuffle(ordine)
        for x in ordine:
            cand = set(alte)
            cand.update(rnd.sample(mod.sillabe, min(CASUALI, len(mod.sillabe))))
            cand.add(chiave[x])
            cand = list(cand)
            punti = []
            for s in cand:
                chiave[x] = s
                punti.append(termini(cif, chiave, mod, toccati[x]))
            m = max(punti)
            pesi = [math.exp((p - m) / T) for p in punti]
            chiave[x] = rnd.choices(cand, weights=pesi)[0]
    return chiave, punteggio_totale(cif, chiave, mod)


# ------------------------------------------------------------ misure

def copertura(righe_sillabe, lessico):
    import e17_ricottura as e17
    tot = c4 = c6 = 0
    for r in righe_sillabe:
        s = ''.join(x for x in r if x not in (RARA, FINE, INIZIO))
        if not s:
            continue
        tot += len(s)
        c4 += e17.copertura(s, lessico, 4)[0]
        c6 += e17.copertura(s, lessico, 6)[0]
    return c4 / tot, c6 / tot


def una(args):
    nome, righe_cif, vere, mod, lessico, seme = args
    cif = Cifrato(righe_cif)
    migliore = None
    for k in range(RIPARTENZE):
        chiave, p = risolvi(cif, mod, seme * 10 + k)
        if migliore is None or p > migliore[1]:
            migliore = (chiave, p)
    chiave, p = migliore
    dec = [[chiave[x] for x in r] for r in righe_cif]
    out = OrderedDict([('simboli', len(cif.simboli)), ('unita', sum(map(len, righe_cif))), ('punteggio', p / sum(len(r) + 1 for r in righe_cif))])
    if vere is not None:
        tot = giuste = 0
        for r, v in zip(dec, vere):
            for a, b in zip(r, v):
                tot += 1
                giuste += a == b
        out['accuratezza'] = giuste / tot
    out['copertura4'], out['copertura6'] = copertura(dec, lessico)
    out['esempio'] = [' '.join(r) for r in dec[:6]]
    return nome, out


def addestramento():
    import e98_versi_latini as e98
    from e36_posizione_pagina import plinio
    righe = []
    for nome in ('Ovidio, Metamorfosi', 'Lucrezio, De rerum natura', 'Virgilio, Eneide (esplorativo prima)'):
        righe.extend(e98.versi(e98.TESTI[nome]))
    lat = [w for _, ps in plinio() for w in ps]
    righe.extend(lat[i:i + 9] for i in range(0, len(lat), 9))
    lessico = {w for r in righe for w in r if len(w) >= 4}
    sill = [[s for w in r for s in generatori.sillabe(w)] for r in righe]
    return Modello(sill), lessico


def main():
    import e99_macer as e99
    import e104_sillabe_varianti as e104
    mod, lessico = addestramento()
    print('modello: %d sillabe nel vocabolario, %d unita\'; lessico %d parole' % (len(mod.voc), mod.n1, len(lessico)), flush=True)
    caps = e99.capitoli()
    sill = [[[s for w in ps for s in generatori.sillabe(w)] for ps in cap] for cap in caps]
    vere = [[s if s in mod.voc else RARA for s in r] for p in sill for r in p]
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    modif = generatori.Modifiche(voy, D)
    lavori = []
    cifrati = {}
    for mu in MU:
        pag = e104.costruisci(sill, voy, modif, mu, 1)
        cifrati[mu] = [r for p in pag for r in p]
        lavori.append(('cifrato, mu %.1f' % mu, cifrati[mu], vere, mod, lessico, 112))
    rnd = random.Random(112)
    tutte = [x for r in cifrati[0.6] for x in r]
    rnd.shuffle(tutte)
    it = iter(tutte)
    mescolato = [[next(it) for _ in r] for r in cifrati[0.6]]
    lavori.append(('negativo: mu 0.6 rimescolato', mescolato, None, mod, lessico, 112))
    ts = [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))]
    tot, ts30 = 0, []
    for r in ts:
        if tot >= 30000:
            break
        ts30.append(r)
        tot += len(r)
    lavori.append(('negativo: Timm e Schinner', ts30, None, mod, lessico, 112))
    ris = OrderedDict()
    ris['tetto: Macer in chiaro'] = OrderedDict(zip(('copertura4', 'copertura6'), copertura(vere, lessico)))
    print('tetto: copertura4 %.3f copertura6 %.3f' % tuple(ris['tetto: Macer in chiaro'].values()), flush=True)
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, lavori):
            ris[nome] = r
            print('%-30s simboli %5d | punteggio %.3f | accuratezza %s | copertura4 %.3f copertura6 %.3f' % (
                nome, r['simboli'], r['punteggio'], '%.3f' % r['accuratezza'] if 'accuratezza' in r else '-', r['copertura4'], r['copertura6']), flush=True)
            for e in r['esempio'][:3]:
                print('    ', e[:150], flush=True)
    neg = max(ris[k]['copertura6'] for k in ris if k.startswith('negativo'))
    valido = ris['cifrato, mu 0.0']['accuratezza'] >= 0.6
    fattibile = {mu: ris['cifrato, mu %.1f' % mu]['accuratezza'] >= 0.4 and ris['cifrato, mu %.1f' % mu]['copertura6'] >= neg + 0.10 for mu in MU}
    ris['valido'], ris['fattibile'] = valido, {str(k): v for k, v in fattibile.items()}
    print('risolutore valido:', valido, '| fattibile:', fattibile)
    with open(os.path.join(RISULTATI, 'e112_risolutore_sillabe.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e112 — Risolutore a sillabe: prova di fattibilità sul controllo', '',
           'Macer cifrato in sillabe con varianti (e104); trigrammi di sillabe da Ovidio, Lucrezio, Virgilio e Plinio. '
           'Preregistrazione: `preregistrazioni/e112.md`.', '', '| prova | simboli | accuratezza | copertura 4+ | copertura 6+ |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'copertura6' in r:
            out.append('| %s | %s | %s | %.1f%% | %.1f%% |' % (nome, r.get('simboli', '–'), '%.2f' % r['accuratezza'] if 'accuratezza' in r else '–',
                                                       100 * r['copertura4'], 100 * r['copertura6']))
    out += ['', 'Risolutore valido: **%s**. Fattibile: %s.' % ('sì' if valido else 'no', ', '.join('μ %s: %s' % (k, 'sì' if v else 'no') for k, v in fattibile.items())), '',
            'Esempi decifrati (μ 0,6):', '']
    out += ['    ' + e for e in ris['cifrato, mu 0.6']['esempio']]
    with open(os.path.join(RISULTATI, 'e112_risolutore_sillabe.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
