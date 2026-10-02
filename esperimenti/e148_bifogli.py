# -*- coding: utf-8 -*-
"""Esperimento 148: i due fogli di un bifoglio si somigliano piu' di fogli alla stessa distanza (stessa mano e lingua)?

Preregistrazione: preregistrazioni/e148.md. Scrive risultati/e148_bifogli.json e .md.
"""
import json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e135_stato_riga as e135

RISULTATI = os.path.join(QUI, '..', 'risultati')
ZL = os.path.join(QUI, '..', 'dati', 'trascrizioni', 'ZL3b-n.txt')
SEME, ESTRAZIONI = 148, 10000
D = misure.divisore(misure.GLIFI_EVA)
SCELTE = (0, 1, 2, 4, 6)


def variabili_pagine():
    out = {}
    for l in open(ZL, encoding='latin-1'):
        m = trascrizione._PAGINA.match(l.rstrip('\n'))
        if m and not trascrizione._LOCUS.match(l):
            out[m.group(1)] = dict(trascrizione._VAR.findall(m.group(2) or ''))
    return out


def foglio(pag):
    m = re.match(r'f(\d+)', pag)
    return int(m.group(1)) if m else None


def fogli():
    var = variabili_pagine()
    zl = trascrizione.leggi('ZL')
    parole, righe, mani, lingue = defaultdict(list), defaultdict(list), defaultdict(Counter), defaultdict(Counter)
    for r in zl:
        f = foglio(r.pagina)
        if f is None or not r.parole:
            continue
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        parole[f].extend(ps)
        if r.tipo and r.tipo[0] == 'P':
            righe[f].append(list(r.parole))
        mani[f][r.mano] += len(ps)
        lingue[f][r.lingua] += len(ps)
    info = {}
    for pag, v in var.items():
        f = foglio(pag)
        if f is not None and 'Q' in v and 'B' in v:
            info.setdefault(f, (v['Q'], v['B']))
    out = {}
    for f, ws in parole.items():
        if len(ws) >= 50 and f in info:
            out[f] = {'parole': ws, 'righe': righe[f], 'fascicolo': info[f][0], 'bifoglio': info[f][1],
                      'mano': mani[f].most_common(1)[0][0], 'lingua': lingue[f].most_common(1)[0][0]}
    return out


def coseno(a, b):
    num = sum(a[k] * b[k] for k in a if k in b)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def bigrammi(ws):
    c = Counter()
    for w in ws:
        u = ['^'] + D(w) + ['$']
        c.update(zip(u, u[1:]))
    return c


def profili(F):
    righe, chi = [], []
    for f, d in F.items():
        for ps in d['righe']:
            righe.append(('x', ps))
            chi.append(f)
    occ = [o for o in e135.occorrenze(righe) if o[0] in SCELTE]
    quota = defaultdict(lambda: [0, 0])
    for fz, r, st, v in occ:
        quota[(fz, st[1:])][0] += v
        quota[(fz, st[1:])][1] += 1
    acc = defaultdict(list)
    for fz, r, st, v in occ:
        a, n = quota[(fz, st[1:])]
        acc[(chi[r], fz)].append(v - a / n)
    return {f: [statistics.mean(acc[(f, fz)]) if acc[(f, fz)] else 0.0 for fz in SCELTE] for f in F}


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else 0.0


def main():
    rnd = random.Random(SEME)
    F = fogli()
    tipi = {f: Counter(d['parole']) for f, d in F.items()}
    bg = {f: bigrammi(d['parole']) for f, d in F.items()}
    pr = profili(F)
    misure_ = OrderedDict([('(1) coseno dei tipi di parola', lambda a, b: coseno(tipi[a], tipi[b])),
                           ('(2) coseno dei bigrammi di segni', lambda a, b: coseno(bg[a], bg[b])),
                           ('(3) correlazione dei profili di grafia', lambda a, b: pearson(pr[a], pr[b]))])
    per_fasc = defaultdict(list)
    for f, d in F.items():
        per_fasc[d['fascicolo']].append(f)
    coniugate = []
    for q, ff in per_fasc.items():
        per_b = defaultdict(list)
        for f in ff:
            per_b[F[f]['bifoglio']].append(f)
        for b, fs in per_b.items():
            if len(fs) == 2:
                coniugate.append(tuple(sorted(fs)))
    ris = OrderedDict([('fogli', len(F)), ('coppie_coniugate', len(coniugate))])
    for nome, sim in misure_.items():
        quantili, dettaglio = [], []
        for a, b in coniugate:
            ff = sorted(per_fasc[F[a]['fascicolo']])
            dist = abs(ff.index(b) - ff.index(a))
            conf = [(x, y) for i, x in enumerate(ff) for y in ff[i + 1:]
                    if abs(ff.index(y) - ff.index(x)) == dist and (x, y) != (a, b) and F[x]['bifoglio'] != F[y]['bifoglio']
                    and F[x]['mano'] == F[a]['mano'] == F[y]['mano'] == F[b]['mano'] and F[x]['lingua'] == F[a]['lingua'] == F[y]['lingua'] == F[b]['lingua']]
            if not conf or F[a]['mano'] != F[b]['mano'] or F[a]['lingua'] != F[b]['lingua']:
                continue
            s = sim(a, b)
            cs = [sim(x, y) for x, y in conf]
            q = (sum(c < s for c in cs) + 0.5 * sum(c == s for c in cs)) / len(cs)
            quantili.append(q)
            dettaglio.append(('f%d-f%d' % (a, b), round(s, 3), len(cs), round(q, 2)))
        if not quantili:
            ris[nome] = OrderedDict([('coppie', 0)])
            continue
        m = statistics.mean(quantili)
        nulli = [statistics.mean(rnd.random() for _ in quantili) for _ in range(ESTRAZIONI)]
        p = sum(x >= m for x in nulli) / ESTRAZIONI
        ris[nome] = OrderedDict([('coppie', len(quantili)), ('media_quantili', m), ('p', p), ('dettaglio', dettaglio)])
        print('%-40s coppie %2d | media dei quantili %.3f | p %.4f' % (nome, len(quantili), m, p), flush=True)
    ok = lambda n: ris[n].get('coppie', 0) and ris[n]['p'] < 0.01 and ris[n]['media_quantili'] >= 0.6
    unita = ok('(1) coseno dei tipi di parola') or ok('(2) coseno dei bigrammi di segni')
    ris['bifogli_come_unita'] = bool(unita)
    print('bifogli scritti come unita\':', bool(unita))
    with open(os.path.join(RISULTATI, 'e148_bifogli.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e148 — I due fogli dello stesso bifoglio si somigliano più dei vicini?', '', 'Coppie coniugate contro coppie non coniugate dello stesso fascicolo, alla stessa distanza, '
           'con stessa mano e lingua. Preregistrazione: `preregistrazioni/e148.md`.', '', '| misura | coppie | media dei quantili | p |', '|---|---|---|---|']
    for nome in misure_:
        r = ris[nome]
        out.append('| %s | %d | %s | %s |' % (nome, r.get('coppie', 0), '%.3f' % r['media_quantili'] if 'media_quantili' in r else '–', '%.4f' % r['p'] if 'p' in r else '–'))
    out += ['', 'Bifogli scritti come unità: **%s**.' % ('sì' if unita else 'no')]
    with open(os.path.join(RISULTATI, 'e148_bifogli.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
