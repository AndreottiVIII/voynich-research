# -*- coding: utf-8 -*-
"""Esperimento 80: verso fisso o riga elastica? Seconda prova: righe corte per spazio disponibile (ereditato dal
Voynich nel controllo) e statistica di verosimiglianza sotto il modello delle giunture (validazione a meta').

Preregistrazione: preregistrazioni/e80.md. Scrive risultati/e80_verso_o_elastica_2.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e77_versi_sandhi as e77
import e79_verso_o_elastica as e79

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SOGLIA, PERMUTAZIONI, LISCIATURA = 80, 0.75, 500, 0.5
D = e71.D


def classifica(righe):
    """righe: (pagina, inizio, fine, parole); vero se la riga e' corta rispetto alla mediana della pagina."""
    per_pagina = defaultdict(list)
    for pag, _, fine, ps in righe:
        if not fine:
            per_pagina[pag].append(e79.larghezza(ps, D))
    med = {p: statistics.median(v) for p, v in per_pagina.items()}
    return [pag in med and e79.larghezza(ps, D) < SOGLIA * med[pag] for pag, _, _, ps in righe]


def coppie(righe, corte, dividi):
    pulita = trascrizione.pulita
    dentro = {0: [], 1: []}
    gruppi = {'corte': {0: [], 1: []}, 'piene': {0: [], 1: []}}
    for k, (pag, inizio, fine, ps) in enumerate(righe):
        meta = k % 2
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro[meta].append((dividi(a)[-1], dividi(b)[0]))
        if k + 1 < len(righe) and not fine:
            pag2, inizio2, _, ps2 = righe[k + 1]
            if pag2 == pag and not inizio2 and ps and ps2 and pulita(ps[-1]) and pulita(ps2[0]):
                gruppi['corte' if corte[k] else 'piene'][meta].append((dividi(ps[-1])[-1], dividi(ps2[0])[0]))
    return dentro, gruppi


class Giunture:
    def __init__(self, cc):
        self.c = defaultdict(Counter)
        self.segni = set()
        for a, b in cc:
            self.c[a][b] += 1
            self.segni.update((a, b))
        self.tot = {a: sum(x.values()) for a, x in self.c.items()}

    def p(self, b, a):
        k = len(self.segni) + 1
        return (self.c[a][b] + LISCIATURA) / (self.tot.get(a, 0) + LISCIATURA * k)


def statistica(cc, modello):
    pb = Counter(b for _, b in cc)
    n = len(cc)
    return sum(math.log2(modello.p(b, a) / (pb[b] / n)) for a, b in cc) / n


def eccesso(cc, modello, rnd):
    if len(cc) < 10:
        return None
    vera = statistica(cc, modello)
    primi, secondi = [a for a, _ in cc], [b for _, b in cc]
    nulli = []
    for _ in range(PERMUTAZIONI):
        rnd.shuffle(secondi)
        nulli.append(statistica(list(zip(primi, secondi)), modello))
    return vera - statistics.mean(nulli), statistics.pstdev(nulli)


def misura(nome, righe, corte, dividi):
    rnd = random.Random(SEME)
    dentro, gruppi = coppie(righe, corte, dividi)
    ris = OrderedDict()
    rif, gr = [], {'corte': [], 'piene': []}
    for meta in (0, 1):
        modello = Giunture(dentro[meta])
        altra = 1 - meta
        rif.append(eccesso(dentro[altra], modello, rnd))
        for g in gr:
            gr[g].append(eccesso(gruppi[g][altra], modello, rnd))
    e_rif = statistics.mean(x[0] for x in rif)
    ris['riferimento_dentro'] = e_rif
    for g, valori in gr.items():
        valori = [x for x in valori if x]
        if not valori:
            ris[g] = OrderedDict([('n', 0), ('eccesso', None), ('z', None), ('R', float('nan')), ('R_limite_sup', float('nan'))])
            continue
        e = statistics.mean(x[0] for x in valori)
        se = math.sqrt(sum(x[1] ** 2 for x in valori)) / len(valori)
        ris[g] = OrderedDict([('n', sum(len(gruppi[g][m]) for m in (0, 1))), ('eccesso', e), ('z', e / se if se else None),
                              ('R', e / e_rif), ('R_limite_sup', (e + 2 * se) / e_rif)])
    ris['delta'] = ris['corte']['R'] - ris['piene']['R']
    print('%-40s rif %.4f | corte n %4d R %.2f (sup %.2f, z %.1f) | piene n %4d R %.2f (sup %.2f, z %.1f) | delta %.2f' % (
        nome, e_rif, ris['corte']['n'], ris['corte']['R'], ris['corte']['R_limite_sup'], ris['corte']['z'] or 0,
        ris['piene']['n'], ris['piene']['R'], ris['piene']['R_limite_sup'], ris['piene']['z'] or 0, ris['delta']), flush=True)
    return ris


def main():
    tutte = e79.righe_voynich()
    voy = [w for _, _, _, ps in tutte for w in ps if trascrizione.pulita(w)]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    corte_v = classifica(tutte)
    ris = OrderedDict()
    ris['Voynich, tutto'] = misura('Voynich, tutto', tutte, corte_v, D)
    rh = e79.righe_voynich('H')
    ris['Voynich H'] = misura('Voynich H', rh, classifica(rh), D)
    f, sha = e77.TESTI['Manusmṛti']
    versi = e77.mezzi_versi(f, sha)
    vl = e79.verso_limitato(versi, tutte, media_voy)
    ris['controllo: verso con spazio limitato'] = misura('controllo: verso con spazio limitato', vl, corte_v[:len(vl)], e71.lettere)
    libero = [(i // e77.RIGHE_PAGINA, i % e77.RIGHE_PAGINA == 0, (i + 1) % e77.RIGHE_PAGINA == 0, ps) for i, ps in enumerate(versi)]
    ris['controllo: verso senza limiti'] = misura('controllo: verso senza limiti', libero, [False] * len(libero), e71.lettere)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    ts = [(i // 29, inizio, i + 1 < len(ts) and ts[i + 1][0], ps) for i, (inizio, ps) in enumerate(ts)]
    ris['Timm e Schinner, seme 19'] = misura('Timm e Schinner, seme 19', ts, classifica(ts), D)
    with open(os.path.join(RISULTATI, 'e80_verso_o_elastica_2.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e80 — Verso fisso o riga elastica? (seconda prova)', '',
           'Statistica di verosimiglianza sotto il modello delle giunture (stimato su metà delle righe, provato sull\'altra); '
           'R = eccesso del gruppo / eccesso dentro la riga. Righe corte: < %.2f della mediana di pagina (nel controllo, '
           'ereditate dal Voynich). Preregistrazione: `preregistrazioni/e80.md`.' % SOGLIA, '',
           '| testo | riferimento (bit) | corte n | R corte (lim. sup.) | piene n | R piene (lim. sup.) | Δ |',
           '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        c, p = r['corte'], r['piene']
        out.append('| %s | %.4f | %d | %.2f (%.2f) | %d | %.2f (%.2f) | %.2f |' % (
            nome, r['riferimento_dentro'], c['n'], c['R'], c['R_limite_sup'], p['n'], p['R'], p['R_limite_sup'], r['delta']))
    with open(os.path.join(RISULTATI, 'e80_verso_o_elastica_2.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
