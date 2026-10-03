# -*- coding: utf-8 -*-
"""Esperimenti 328, 329, 330. (e328) a quale livello (fascicolo, bifoglio, pagina, paragrafo, riga) sta la variazione
del testo; (e329) il primo e l'ultimo paragrafo della pagina differiscono per argomento (lessico normalizzato) o per
abitudine (le 5 scelte di grafia)?; (e330) l'ultimo paragrafo del recto somiglia al primo del verso piu' che il primo
del recto all'ultimo del verso?

Preregistrazione: preregistrazioni/e328.md. Scrive risultati/e328_livelli.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e327_stato_pagina as e327

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
LUNGHI_KT = {'t', 'f', 'cth', 'cfh'}


def carica():
    """Pagine nell'ordine del libro: lista di paragrafi, ognuno lista di (tipo, parole)."""
    pag = OrderedDict()
    cur = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if not ws:
            continue
        pars = pag.setdefault(r.pagina, [])
        if r.inizio_par or not pars or cur.get(r.pagina) is None:
            pars.append([])
            cur[r.pagina] = True
        tipo = 'prima' if r.inizio_par else ('ultima' if r.fine_par else 'interna')
        pars[-1].append((tipo, ws))
        if r.fine_par:
            cur[r.pagina] = None
    return pag


# ---------- e328 ----------

def variabili(ws):
    u = [D(w) for w in ws]
    n = len(u)
    tot = sum(len(x) for x in u)
    return [sum(x[-1] == 'y' for x in u) / n, sum(x[-1] == 'n' for x in u) / n, sum(g == 'e' for x in u for g in x) / tot,
            sum(x[:2] == ['q', 'o'] for x in u) / n, tot / n]


NOMI_VAR = ['finale -y', 'finale -n', 'segno e', 'iniziale qo-', 'lunghezza media']


def r2(v, w, g):
    """Quota della varianza pesata spiegata dalle medie dei gruppi g (interi)."""
    m = np.average(v, weights=w)
    sw = np.bincount(g, weights=w)
    sv = np.bincount(g, weights=w * v)
    mg = np.divide(sv, sw, out=np.zeros_like(sv), where=sw > 0)
    return float((sw * (mg - m) ** 2).sum() / (w * (v - m) ** 2).sum())


def e328(pag, testa, rnd):
    righe = []   # (variabili, peso, fascicolo, bifoglio, pagina, paragrafo)
    for p, pars in pag.items():
        h = testa.get(p)
        if not h or not h['Q']:
            continue
        for k, par in enumerate(pars):
            interne = [ws for t, ws in par if t == 'interna']
            if len(interne) >= 2:
                for ws in interne:
                    righe.append((variabili(ws), len(ws), h['Q'], (h['Q'], h['B']), p, (p, k)))
    w = np.array([r[1] for r in righe], dtype=float)
    livelli = []
    for j in (2, 3, 4, 5):
        lab = {}
        livelli.append(np.array([lab.setdefault(r[j], len(lab)) for r in righe]))
    nomi_liv = ['fascicolo', 'bifoglio', 'pagina', 'paragrafo']
    out = OrderedDict()
    for vi, nv in enumerate(NOMI_VAR):
        v = np.array([r[0][vi] for r in righe])
        prec = np.zeros(len(righe), dtype=int)
        r_prec = 0.0
        tab = OrderedDict()
        for k, g in enumerate(livelli):
            vero = r2(v, w, g) - r_prec
            nul = []
            for _ in range(200):
                gs = g.copy()
                for gp in np.unique(prec):
                    idx = np.where(prec == gp)[0]
                    gs[idx] = g[rnd.sample(list(idx), len(idx))]
                nul.append(r2(v, w, gs) - r_prec)
            tab[nomi_liv[k]] = OrderedDict([('delta_R2', vero), ('nullo', statistics.mean(nul)), ('eccesso', vero - statistics.mean(nul)),
                                            ('z', (vero - statistics.mean(nul)) / (statistics.pstdev(nul) or 1))])
            r_prec += vero
            prec = g
        tab['riga (resto)'] = OrderedDict([('delta_R2', 1 - r_prec)])
        migliore = max((x for x in tab if x != 'riga (resto)'), key=lambda x: tab[x]['eccesso'])
        out[nv] = OrderedDict([('livelli', tab), ('livello_con_eccesso_maggiore', migliore), ('livelli_z_oltre_3', [x for x in tab if x != 'riga (resto)' and tab[x]['z'] > 3])])
    return OrderedDict([('righe', len(righe)), ('variabili', out)])


# ---------- e329 ----------

def normalizza(w):
    u = list(D(w))
    m = {'sh': 'ch', 't': 'k', 'f': 'p', 'cth': 'ckh', 'cfh': 'cph'}
    u = [m.get(g, g) for g in u]
    if len(u) >= 2 and u[-1] == 'r' and u[-2] in ('o', 'a'):
        u[-1] = 'l'
    if len(u) >= 3 and u[0] == 'q' and u[1] == 'o':
        u = u[1:]
    if len(u) >= 2 and u[-2] == 'e' and u[-1] == 'y':
        u[-2] = 'd'
    return ''.join(u)


def scelte(ws):
    """Per le 5 scelte: (posti, forme lunghe)."""
    c = [[0, 0] for _ in range(5)]
    for w in ws:
        u = D(w)
        for g in u:
            if g in ('ch', 'sh'):
                c[0][0] += 1
                c[0][1] += g == 'sh'
            if g in GALL:
                c[1][0] += 1
                c[1][1] += g in LUNGHI_KT
        if len(u) >= 2 and u[-1] in ('l', 'r') and u[-2] in ('o', 'a'):
            c[2][0] += 1
            c[2][1] += u[-1] == 'r'
        if (len(u) >= 3 and u[0] == 'q' and u[1] == 'o' and u[2] in GALL) or (len(u) >= 2 and u[0] == 'o' and u[1] in GALL):
            c[3][0] += 1
            c[3][1] += u[0] == 'q'
        if len(u) >= 2 and u[-1] == 'y' and u[-2] in ('d', 'e'):
            c[4][0] += 1
            c[4][1] += u[-2] == 'e'
    return c


def jsd_counter(c1, c2):
    t1, t2 = sum(c1.values()), sum(c2.values())
    out = 0.0
    for k in set(c1) | set(c2):
        a, b = c1[k] / t1, c2[k] / t2
        m = (a + b) / 2
        out += (a * math.log2(a / m) if a else 0) + (b * math.log2(b / m) if b else 0)
    return out / 2


def e329(pag, rnd):
    coppie = []
    for p, pars in pag.items():
        if len(pars) >= 3:
            a = [ws for _, ws in pars[0]]
            b = [ws for _, ws in pars[-1]]
            if sum(map(len, a)) >= 15 and sum(map(len, b)) >= 15:
                coppie.append((a, b))

    def misura(ps):
        lex, gra = [], []
        for a, b in ps:
            wa = [w for r in a for w in r]
            wb = [w for r in b for w in r]
            lex.append(jsd_counter(Counter(map(normalizza, wa)), Counter(map(normalizza, wb))))
            ca, cb = scelte(wa), scelte(wb)
            g = 0.0
            for (n1, l1), (n2, l2) in zip(ca, cb):
                if n1 >= 5 and n2 >= 5:
                    pp = (l1 + l2) / (n1 + n2)
                    if 0 < pp < 1:
                        g += abs(l1 / n1 - l2 / n2) / math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
            gra.append(g)
        return statistics.mean(lex), statistics.mean(gra)
    vero = misura(coppie)
    nul = []
    for _ in range(1000):
        ps = []
        for a, b in coppie:
            r = a + b
            r = rnd.sample(r, len(r))
            ps.append((r[:len(a)], r[len(a):]))
        nul.append(misura(ps))
    z = [(vero[k] - statistics.mean(n[k] for n in nul)) / statistics.pstdev(n[k] for n in nul) for k in (0, 1)]
    esiti = [x for x, ok in (('argomento', z[0] > 3), ('abitudine', z[1] > 3)) if ok]
    return OrderedDict([('coppie', len(coppie)), ('lessico', vero[0]), ('nullo_lessico', statistics.mean(n[0] for n in nul)), ('z_lessico', z[0]),
                        ('grafia', vero[1]), ('nullo_grafia', statistics.mean(n[1] for n in nul)), ('z_grafia', z[1]), ('esito', ' e '.join(esiti) or 'nessuno dei due')])


# ---------- e330 ----------

def e330(pag, testa, rnd):
    pp = [p for p in pag if sum(len(ws) for par in pag[p] for _, ws in par) >= 60]
    stat_pag = [e327.somma([e327.riga_stat(ws) for par in pag[p] for _, ws in par])[0] for p in pp]
    mu = {k: statistics.mean(v[k] for v in stat_pag) for k in stat_pag[0]}
    sd = {k: statistics.pstdev(v[k] for v in stat_pag) for k in stat_pag[0]}
    punt = lambda v: (v['e'] - mu['e']) / sd['e'] + (v['fy'] - mu['fy']) / sd['fy'] - (v['a'] - mu['a']) / sd['a'] - (v['n'] - mu['n']) / sd['n'] - (v['fn'] - mu['fn']) / sd['fn']

    def dist(par1, par2):
        s1, c1 = e327.somma([e327.riga_stat(ws) for _, ws in par1])
        s2, c2 = e327.somma([e327.riga_stat(ws) for _, ws in par2])
        return abs(punt(s1) - punt(s2)), e327.jsd(c1, c2)
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seguente = dict(zip(ordine, ordine[1:]))
    fogli, aperture = [], []
    for p in pag:
        h = testa.get(p)
        if not h or h['lato'] != 'r':
            continue
        v = seguente.get(p)
        if v and testa[v]['lato'] == 'v' and testa[v]['F'] == h['F'] and v in pag and len(pag[p]) >= 2 and len(pag[v]) >= 2:
            fogli.append((p, v))
    for p in pag:
        h = testa.get(p)
        if not h or h['lato'] != 'v':
            continue
        r = seguente.get(p)
        if r and testa[r]['lato'] == 'r' and r in pag and len(pag[p]) >= 2 and len(pag[r]) >= 2:
            aperture.append((p, r))

    def prova(coppie):
        diffs = []
        for a, b in coppie:
            vic = dist(pag[a][-1], pag[b][0])
            lon = dist(pag[a][0], pag[b][-1])
            diffs.append((lon[0] - vic[0], lon[1] - vic[1]))
        if len(diffs) < 5:
            return OrderedDict([('coppie', len(diffs))])
        vero = [statistics.mean(d[k] for d in diffs) for k in (0, 1)]
        nul = []
        for _ in range(1000):
            seg = [rnd.choice((-1, 1)) for _ in diffs]
            nul.append([statistics.mean(s * d[k] for s, d in zip(seg, diffs)) for k in (0, 1)])
        z = [(vero[k] - statistics.mean(n[k] for n in nul)) / statistics.pstdev(n[k] for n in nul) for k in (0, 1)]
        esito = 'scritto di seguito' if max(z) > 3 else ('no' if max(z) < 2 else 'incerto')
        return OrderedDict([('coppie', len(diffs)), ('lontana_meno_vicina_asse', vero[0]), ('z_asse', z[0]), ('lontana_meno_vicina_segni', vero[1]), ('z_segni', z[1]), ('esito', esito)])
    return OrderedDict([('fogli (recto → verso)', prova(fogli)), ('aperture (verso → recto seguente)', prova(aperture))])


def main():
    pag = carica()
    testa = e308.intestazioni()
    r328 = e328(pag, testa, random.Random(328))
    print('e328', r328['righe'], {v: (x['livello_con_eccesso_maggiore'], x['livelli_z_oltre_3']) for v, x in r328['variabili'].items()}, flush=True)
    r329 = e329(pag, random.Random(329))
    print('e329', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r329.items()}, flush=True)
    r330 = e330(pag, testa, random.Random(330))
    print('e330', {k: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} for k, v in r330.items()}, flush=True)
    json.dump(OrderedDict([('e328', r328), ('e329', r329), ('e330', r330)]), open(os.path.join(RISULTATI, 'e328_livelli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e328, e329, e330 — Dove sta la variazione; stato o argomento; continuità fra recto e verso', '', 'Preregistrazione: `preregistrazioni/e328.md`.', '',
          '## e328 — %d righe interne' % r328['righe'], '', '| variabile | livello | ΔR² | nullo | eccesso | z |', '|---|---|---|---|---|---|']
    for nv, x in r328['variabili'].items():
        for lv, t in x['livelli'].items():
            if 'z' in t:
                md.append('| %s | %s | %.3f | %.3f | %+.3f | %.1f |' % (nv, lv, t['delta_R2'], t['nullo'], t['eccesso'], t['z']))
            else:
                md.append('| %s | %s | %.3f | | | |' % (nv, lv, t['delta_R2']))
    md += [''] + ['- %s: livello con l\'eccesso maggiore **%s**; livelli con z > 3: %s.' % (nv, x['livello_con_eccesso_maggiore'], ', '.join(x['livelli_z_oltre_3']) or 'nessuno')
                  for nv, x in r328['variabili'].items()]
    md += ['', '## e329 — %d coppie primo/ultimo paragrafo' % r329['coppie'], '',
           'Lessico normalizzato: JSD %.4f contro %.4f del nullo, z %.1f. Grafia (5 scelte): %.2f contro %.2f, z %.1f. Esito: **%s**.' % (
               r329['lessico'], r329['nullo_lessico'], r329['z_lessico'], r329['grafia'], r329['nullo_grafia'], r329['z_grafia'], r329['esito']), '',
           '## e330', '', '| coppie di pagine | numero | lontana − vicina (asse) | z | lontana − vicina (segni) | z | esito |', '|---|---|---|---|---|---|---|']
    for k, v in r330.items():
        if 'z_asse' in v:
            md.append('| %s | %d | %+.3f | %.1f | %+.4f | %.1f | %s |' % (k, v['coppie'], v['lontana_meno_vicina_asse'], v['z_asse'], v['lontana_meno_vicina_segni'], v['z_segni'], v['esito']))
        else:
            md.append('| %s | %d | – | – | – | – | troppo poche |' % (k, v['coppie']))
    open(os.path.join(RISULTATI, 'e328_livelli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
