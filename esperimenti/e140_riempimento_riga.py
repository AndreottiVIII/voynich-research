# -*- coding: utf-8 -*-
"""Esperimento 140: le varianti lunghe (ee, aiin, qo-) servono a riempire le righe corte? Correlazione fra surplus di
varianti lunghe e base della riga, entro pagina, contro rimescolamenti delle scelte dentro gli strati.

Preregistrazione: preregistrazioni/e140.md. Scrive risultati/e140_riempimento_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e135_stato_riga as e135

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERM = 140, 1000
D = misure.divisore(misure.GLIFI_EVA)
SCELTE = {3: 'e/ee', 5: 'ain/aiin', 4: 'o-/qo-'}


def base(ps):
    n = len(ps) - 1
    for w in ps:
        u = D(w)
        s = []
        for j, g in enumerate(u):
            if g == 'e' and j > 0 and u[j - 1] == 'e':
                continue  # ee -> e
            if g == 'i' and j + 2 < len(u) + 1 and u[j:j + 3] == ['i', 'i', 'n']:
                continue  # aiin -> ain (toglie una i)
            if g == 'q' and j == 0 and len(u) > 2 and u[1] == 'o':
                continue  # qo -> o
            s.append(g)
        n += len(s)
    return n


def righe_testo(par_righe):
    """par_righe: liste di paragrafi (pagina, parole) -> (pagina, parole, interna?) senza la prima riga di paragrafo."""
    out = []
    for p in par_righe:
        for j, (pag, ps) in enumerate(p):
            if j == 0 or len(ps) < 4 or not all(trascrizione.pulita(w) for w in ps):
                continue
            out.append((pag, ps, j < len(p) - 1))
    return out


def paragrafi_voynich():
    out, cur, pag = [], [], None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        if r.inizio_par or r.pagina != pag:
            if cur:
                out.append(cur)
            cur, pag = [], r.pagina
        cur.append((r.pagina, list(r.parole)))
    if cur:
        out.append(cur)
    return out


def paragrafi_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    out, cur = [], []
    for i, (ini, ps) in enumerate(rr):
        if ini or i % 29 == 0:
            if cur:
                out.append(cur)
            cur = []
        cur.append((i // 29, ps))
    if cur:
        out.append(cur)
    return out


def prepara(righe):
    occ = [o for o in e135.occorrenze([(pag, ps) for pag, ps, _ in righe]) if o[0] in SCELTE]
    basi = [base(ps) for _, ps, _ in righe]
    return occ, basi


def ranghi(x):
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranghi(a), ranghi(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def correlazione(righe, occ, valori, basi, quali):
    quota = defaultdict(lambda: [0, 0])
    for (f, _, st, _), v in zip(occ, valori):
        quota[(f, st)][0] += v
        quota[(f, st)][1] += 1
    surplus = defaultdict(float)
    for (f, r, st, _), v in zip(occ, valori):
        a, n = quota[(f, st)]
        surplus[r] += v - a / n
    idx = [i for i in range(len(righe)) if quali(righe[i])]
    per_pag = defaultdict(list)
    for i in idx:
        per_pag[righe[i][0]].append(i)
    s, b = [], []
    for pag, ii in per_pag.items():
        if len(ii) < 2:
            continue
        ms = statistics.mean(surplus[i] for i in ii)
        mb = statistics.mean(basi[i] for i in ii)
        for i in ii:
            s.append(surplus[i] - ms)
            b.append(basi[i] - mb)
    return spearman(s, b), len(s)


def valuta(righe, occ, valori, basi, rnd):
    gg = e135.gruppi(occ)
    out = OrderedDict()
    for nome, quali in (('righe interne', lambda r: r[2]), ('ultime righe di paragrafo', lambda r: not r[2])):
        rho, n = correlazione(righe, occ, valori, basi, quali)
        nulli = [correlazione(righe, occ, e135.permuta(valori, gg, rnd), basi, quali)[0] for _ in range(PERM)]
        m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        out[nome] = OrderedDict([('righe', n), ('rho', rho), ('nullo', m), ('z', (rho - m) / sd if sd else None)])
    return out


def imposto(righe, occ, basi, rnd):
    mediana = {}
    per = defaultdict(list)
    for (pag, _, _), b in zip(righe, basi):
        per[pag].append(b)
    for pag, l in per.items():
        mediana[pag] = statistics.median(l)
    out = []
    for (f, r, st, v) in occ:
        pag = righe[r][0]
        if rnd.random() < 0.5:
            v = 1 if basi[r] < mediana[pag] else 0
        out.append(v)
    return out


def main():
    rnd = random.Random(SEME)
    ris = OrderedDict()
    rv = righe_testo(paragrafi_voynich())
    occ, basi = prepara(rv)
    valori = [v for *_, v in occ]
    ris['Voynich ZL'] = valuta(rv, occ, valori, basi, rnd)
    ris['controllo positivo: varianti per riempire'] = valuta(rv, occ, imposto(rv, occ, basi, random.Random(SEME + 1)), basi, rnd)
    rt = righe_testo(paragrafi_ts())
    occ_t, basi_t = prepara(rt)
    ris['Timm e Schinner, seme 19'] = valuta(rt, occ_t, [v for *_, v in occ_t], basi_t, rnd)
    for nome, r in ris.items():
        print('%-44s | %s' % (nome, ' | '.join('%s: n %d rho %+.3f (nullo %+.3f, z %.1f)' % (k, x['righe'], x['rho'], x['nullo'], x['z'] or 0) for k, x in r.items())), flush=True)
    z = lambda n, k: ris[n][k]['z'] or 0
    valido = z('controllo positivo: varianti per riempire', 'righe interne') < -10
    ri, ru = ris['Voynich ZL']['righe interne'], ris['Voynich ZL']['ultime righe di paragrafo']
    allinea = ((ri['z'] or 0) < -4 and (abs(ru['z'] or 0) < 2 or abs(ru['rho']) < abs(ri['rho']) / 2)
               and abs(z('Timm e Schinner, seme 19', 'righe interne')) < 2)
    ris['valido'], ris['allineamento'] = valido, allinea
    print('controllo valido:', valido, '| allineamento con le varianti:', allinea)
    with open(os.path.join(RISULTATI, 'e140_riempimento_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e140 — Le varianti lunghe servono a riempire la riga?', '', 'Spearman fra surplus di varianti lunghe (ee, aiin, qo-) e base della riga, entro pagina; nullo: %d '
           'rimescolamenti delle scelte negli strati. Preregistrazione: `preregistrazioni/e140.md`.' % PERM, '',
           '| testo | righe interne: n, rho (z) | ultime righe di paragrafo: n, rho (z) |', '|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %s |' % (nome, ' | '.join('%d, %+.3f (%.1f)' % (x['righe'], x['rho'], x['z'] or 0) for x in r.values())))
    out += ['', 'Controllo valido: **%s**. Allineamento con le varianti: **%s**.' % ('sì' if valido else 'no', 'sì' if allinea else 'no')]
    with open(os.path.join(RISULTATI, 'e140_riempimento_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
