# -*- coding: utf-8 -*-
"""Esperimenti 316 e 317. (e316) il gallows d'inizio paragrafo: dipende dalla parola, dalla pagina, dal bifoglio? p/f
marcano il primo paragrafo della pagina? (e317) fra la prima e l'ultima riga del paragrafo c'e' un andamento graduale?

Preregistrazione: preregistrazioni/e316.md. Scrive risultati/e316_paragrafo.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = ('k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh')
PF = {'p', 'f', 'cph', 'cfh'}
PERM = 1000


def mi(coppie):
    n = len(coppie)
    cxy, cx, cy = Counter(coppie), Counter(a for a, _ in coppie), Counter(b for _, b in coppie)
    return sum(c / n * math.log2(c * n / (cx[a] * cy[b])) for (a, b), c in cxy.items())


def righe_voynich():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                out.append((r.pagina, bool(r.inizio_par), bool(r.fine_par), ws, r.sezione or '?', r.lingua or '?'))
    return out


def e316(righe, testa, rnd):
    inizi = []      # (pagina, sezione, lingua, gallows, segno seguente, primo paragrafo della pagina)
    viste = set()
    for p, ini, fine, ws, s, l in righe:
        if ini:
            u = D(ws[0])
            primo = p not in viste
            viste.add(p)
            if u[0] in GALLOWS:
                inizi.append((p, s, l, u[0], u[1] if len(u) > 1 else 'fine', primo))
    mezzo = []
    for p, ini, fine, ws, s, l in righe:
        for w in ws[1:-1]:
            u = D(w)
            if u[0] in GALLOWS:
                mezzo.append((u[0], u[1] if len(u) > 1 else 'fine'))

    def z_mi(cp):
        vero = mi(cp)
        g = [a for a, _ in cp]
        nul = []
        for _ in range(PERM):
            rnd.shuffle(g)
            nul.append(mi(list(zip(g, [b for _, b in cp]))))
        return OrderedDict([('parole', len(cp)), ('MI', vero), ('nullo', statistics.mean(nul)), ('z', (vero - statistics.mean(nul)) / statistics.pstdev(nul))])
    a = OrderedDict([('prime parole dei paragrafi', z_mi([(x[3], x[4]) for x in inizi])), ('parole in mezzo alla riga', z_mi(mezzo))])
    za = a['prime parole dei paragrafi']['z']
    esito_a = 'il gallows segue la parola' if za > 3 else ('indipendente dalla parola' if za < 2 else 'incerto')
    bif = {p: (v['Q'], v['B']) for p, v in testa.items()}
    per_sez = defaultdict(list)
    for i, x in enumerate(inizi):
        per_sez[x[1]].append(i)

    cp_pag, cp_bif = [], []
    for i in range(len(inizi)):
        for j in range(i + 1, len(inizi)):
            pi, pj = inizi[i][0], inizi[j][0]
            if pi == pj:
                cp_pag.append((i, j))
            elif bif.get(pi) and bif.get(pi) == bif.get(pj):
                cp_bif.append((i, j))

    def stat(gal):
        tot_p, tot_b = len(cp_pag), len(cp_bif)
        sp = sum(gal[i] == gal[j] for i, j in cp_pag)
        sb = sum(gal[i] == gal[j] for i, j in cp_bif)
        primi = [gal[i] in PF for i, x in enumerate(inizi) if x[5]]
        altri = [gal[i] in PF for i, x in enumerate(inizi) if not x[5]]
        return sp / max(1, tot_p), sb / max(1, tot_b), (statistics.mean(primi) - statistics.mean(altri)) if primi and altri else 0.0, tot_p, tot_b
    g0 = [x[3] for x in inizi]
    vero = stat(g0)
    nul = []
    for _ in range(PERM):
        g = list(g0)
        for idx in per_sez.values():
            x = [g0[i] for i in idx]
            rnd.shuffle(x)
            for i, v in zip(idx, x):
                g[i] = v
        nul.append(stat(g))
    zz = [(vero[k] - statistics.mean(n[k] for n in nul)) / (statistics.pstdev(n[k] for n in nul) or 1) for k in range(3)]
    b = OrderedDict([('stessa pagina', OrderedDict([('coppie', vero[3]), ('quota stesso gallows', vero[0]), ('nullo', statistics.mean(n[0] for n in nul)), ('z', zz[0])])),
                     ('stesso bifoglio', OrderedDict([('coppie', vero[4]), ('quota stesso gallows', vero[1]), ('nullo', statistics.mean(n[1] for n in nul)), ('z', zz[1])]))])
    scelto = [k for k, v in b.items() if v['z'] > 3]
    c = OrderedDict([('differenza p/f primo paragrafo meno altri', vero[2]), ('z', zz[2]),
                     ('esito', 'sì' if zz[2] > 3 else ('no' if abs(zz[2]) < 2 else 'incerto'))])
    tab = OrderedDict()
    for chiave, f in (('sezione', lambda x: x[1]), ('lingua', lambda x: x[2])):
        t = defaultdict(Counter)
        for x in inizi:
            t[f(x)][x[3]] += 1
        tab[chiave] = OrderedDict((k, dict(v)) for k, v in sorted(t.items(), key=str))
    return OrderedDict([('a', a), ('esito_a', esito_a), ('b', b), ('scelto_per', scelto), ('c', c), ('gallows_per', tab), ('totale', dict(Counter(g0)))])


def caratteristiche(ws):
    u = [D(w) for w in ws]
    n = len(u)
    tot = sum(len(x) for x in u)
    return OrderedDict([('lunghezza media', tot / n), ('quota segni gallows', sum(g in GALLOWS for x in u for g in x) / tot),
                        ('inizia con qo', sum(x[:2] == ['q', 'o'] for x in u) / n), ('inizia con ch', sum(x[0] == 'ch' for x in u) / n),
                        ('inizia con sh', sum(x[0] == 'sh' for x in u) / n), ('finale y', sum(x[-1] == 'y' for x in u) / n),
                        ('finale n', sum(x[-1] == 'n' for x in u) / n), ('numero di parole', float(n))])


def e317(righe, rnd):
    par, cur = [], []
    for p, ini, fine, ws, s, l in righe:
        if ini:
            cur = [ws]
        elif cur:
            cur.append(ws)
        if fine and cur:
            par.append(cur)
            cur = []
    par = [x for x in par if len(x) >= 5]
    interne = []    # per paragrafo: lista di caratteristiche delle righe interne in ordine
    for x in par:
        interne.append([caratteristiche(ws) for ws in x[1:-1]])
    nomi = list(interne[0][0])

    def misure_(ordini):
        out = {}
        for k in nomi:
            ts, vs, sec, alt2, pen, altp = [], [], [], [], [], []
            for righe_p, o in zip(interne, ordini):
                m = len(righe_p)
                for pos, r in zip(o, righe_p):
                    t = pos / (m - 1) if m > 1 else 0.0
                    ts.append(t)
                    vs.append(r[k])
                    (sec if pos == 0 else alt2).append(r[k])
                    (pen if pos == m - 1 else altp).append(r[k])
            mt, mv = statistics.mean(ts), statistics.mean(vs)
            cov = sum((a - mt) * (b - mv) for a, b in zip(ts, vs))
            den = math.sqrt(sum((a - mt) ** 2 for a in ts) * sum((b - mv) ** 2 for b in vs))
            out[k] = (cov / den if den else 0.0, statistics.mean(sec) - statistics.mean(alt2), statistics.mean(pen) - statistics.mean(altp))
        return out
    base = [list(range(len(r))) for r in interne]
    vero = misure_(base)
    nul = defaultdict(list)
    for _ in range(PERM):
        o = []
        for b in base:
            x = list(b)
            rnd.shuffle(x)
            o.append(x)
        for k, v in misure_(o).items():
            nul[k].append(v)
    out = OrderedDict()
    for k in nomi:
        zs = [(vero[k][j] - statistics.mean(n[j] for n in nul[k])) / (statistics.pstdev(n[j] for n in nul[k]) or 1) for j in range(3)]
        out[k] = OrderedDict([('pendenza', vero[k][0]), ('z_pendenza', zs[0]), ('seconda_meno_altre', vero[k][1]), ('z_seconda', zs[1]),
                              ('penultima_meno_altre', vero[k][2]), ('z_penultima', zs[2])])
    forti = [k for k, v in out.items() if abs(v['z_pendenza']) > 3]
    esito = 'arco graduale' if len(forti) >= 3 else ('solo gli estremi' if not forti else 'debole')
    return OrderedDict([('paragrafi', len(par)), ('righe_interne', sum(len(r) for r in interne)), ('caratteristiche', out), ('pendenze_forti', forti), ('esito', esito),
                        ('seconda_riga_forte', [k for k, v in out.items() if abs(v['z_seconda']) > 3]), ('penultima_forte', [k for k, v in out.items() if abs(v['z_penultima']) > 3])])


def main():
    righe = righe_voynich()
    testa = e308.intestazioni()
    r316 = e316(righe, testa, random.Random(316))
    print('e316', r316['esito_a'], {k: (round(v['MI'], 4), round(v['z'], 1)) for k, v in r316['a'].items()}, {k: (round(v['quota stesso gallows'], 3), round(v['z'], 1)) for k, v in r316['b'].items()}, r316['c'], flush=True)
    r317 = e317(righe, random.Random(317))
    print('e317', r317['esito'], r317['paragrafi'], {k: (round(v['pendenza'], 3), round(v['z_pendenza'], 1)) for k, v in r317['caratteristiche'].items()}, flush=True)
    json.dump(OrderedDict([('e316', r316), ('e317', r317)]), open(os.path.join(RISULTATI, 'e316_paragrafo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e316, e317 — Il gallows d\'inizio paragrafo; l\'arco del paragrafo', '', 'Preregistrazione: `preregistrazioni/e316.md`.', '', '## e316', '',
          '| gruppo | parole | MI gallows–segno seguente | nullo | z |', '|---|---|---|---|---|']
    for k, v in r316['a'].items():
        md.append('| %s | %d | %.4f | %.4f | %.1f |' % (k, v['parole'], v['MI'], v['nullo'], v['z']))
    md += ['', 'Esito (a): **%s**.' % r316['esito_a'], '', '| coppie di paragrafi | coppie | stesso gallows | nullo | z |', '|---|---|---|---|---|']
    for k, v in r316['b'].items():
        md.append('| %s | %d | %.3f | %.3f | %.1f |' % (k, v['coppie'], v['quota stesso gallows'], v['nullo'], v['z']))
    md += ['', 'Scelto per: **%s**.' % (', '.join(r316['scelto_per']) or 'né pagina né bifoglio'), '',
           '(c) *p*/*f* nel primo paragrafo della pagina meno negli altri: %+.3f, z %.1f: **%s**.' % (r316['c']['differenza p/f primo paragrafo meno altri'], r316['c']['z'], r316['c']['esito']), '',
           'Gallows d\'inizio in tutto: %s. Per sezione: %s. Per lingua: %s.' % (r316['totale'], r316['gallows_per']['sezione'], r316['gallows_per']['lingua']), '',
           '## e317 — %d paragrafi con almeno 5 righe, %d righe interne' % (r317['paragrafi'], r317['righe_interne']), '',
           '| caratteristica | pendenza (seconda → penultima) | z | seconda − altre | z | penultima − altre | z |', '|---|---|---|---|---|---|---|']
    for k, v in r317['caratteristiche'].items():
        md.append('| %s | %+.3f | %.1f | %+.4f | %.1f | %+.4f | %.1f |' % (k, v['pendenza'], v['z_pendenza'], v['seconda_meno_altre'], v['z_seconda'], v['penultima_meno_altre'], v['z_penultima']))
    md += ['', 'Esito e317: **%s** (pendenze con |z| > 3: %s). Seconda riga diversa in: %s. Penultima diversa in: %s.' % (
        r317['esito'], ', '.join(r317['pendenze_forti']) or 'nessuna', ', '.join(r317['seconda_riga_forte']) or 'nessuna', ', '.join(r317['penultima_forte']) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e316_paragrafo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
