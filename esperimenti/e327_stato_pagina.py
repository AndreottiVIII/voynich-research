# -*- coding: utf-8 -*-
"""Esperimento 327: controllo dell'e326 (meta' alta e meta' bassa della pagina diverse) senza l'effetto delle righe di
inizio e fine paragrafo. Tre versioni: solo righe interne; nullo a pari tipo di riga; primo contro ultimo paragrafo.

Preregistrazione: preregistrazioni/e327.md. Scrive risultati/e327_stato_pagina.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def riga_stat(ws):
    u = [D(w) for w in ws]
    return (Counter(g for x in u for g in x), len(u), sum(x[-1] == 'y' for x in u), sum(x[-1] == 'n' for x in u))


def somma(rs):
    segni, n, fy, fn = Counter(), 0, 0, 0
    for c, a, b, d in rs:
        segni.update(c)
        n += a
        fy += b
        fn += d
    tot = sum(segni.values())
    return {'e': segni['e'] / tot, 'a': segni['a'] / tot, 'n': segni['n'] / tot, 'fy': fy / n, 'fn': fn / n}, segni


def jsd(c1, c2):
    t1, t2 = sum(c1.values()), sum(c2.values())
    out = 0.0
    for k in set(c1) | set(c2):
        a, b = c1[k] / t1, c2[k] / t2
        m = (a + b) / 2
        out += (a * math.log2(a / m) if a else 0) + (b * math.log2(b / m) if b else 0)
    return out / 2


def main():
    rnd = random.Random(327)
    pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                tipo = 'prima' if r.inizio_par else ('ultima' if r.fine_par else 'interna')
                pag.setdefault(r.pagina, []).append((tipo, riga_stat(ws), bool(r.inizio_par), bool(r.fine_par)))
    pp = [p for p, rs in pag.items() if sum(x[1][1] for x in rs) >= 60]
    vals = [somma([x[1] for x in pag[p]])[0] for p in pp]
    mu = {k: statistics.mean(v[k] for v in vals) for k in vals[0]}
    sd = {k: statistics.pstdev(v[k] for v in vals) for k in vals[0]}
    punt = lambda v: (v['e'] - mu['e']) / sd['e'] + (v['fy'] - mu['fy']) / sd['fy'] - (v['a'] - mu['a']) / sd['a'] - (v['n'] - mu['n']) / sd['n'] - (v['fn'] - mu['fn']) / sd['fn']

    def misura(coppie):
        d1, d2 = [], []
        for a, b in coppie:
            sa, ca = somma(a)
            sb, cb = somma(b)
            d1.append(abs(punt(sa) - punt(sb)))
            d2.append(jsd(ca, cb))
        return statistics.mean(d1), statistics.mean(d2)

    def prova(vere, nullo):
        v = misura(vere)
        n = [misura(nullo()) for _ in range(PERM)]
        z = [(v[k] - statistics.mean(x[k] for x in n)) / statistics.pstdev(x[k] for x in n) for k in (0, 1)]
        return OrderedDict([('coppie', len(vere)), ('D1', v[0]), ('nullo_D1', statistics.mean(x[0] for x in n)), ('z_D1', z[0]),
                            ('D2', v[1]), ('nullo_D2', statistics.mean(x[1] for x in n)), ('z_D2', z[1])])
    # 1. solo righe interne
    interne = {p: [x[1] for x in pag[p] if x[0] == 'interna'] for p in pp}
    p1 = [p for p in pp if len(interne[p]) >= 12]
    vere1 = [(interne[p][:len(interne[p]) // 2], interne[p][len(interne[p]) // 2:]) for p in p1]

    def nullo1():
        out = []
        for p in p1:
            r = list(interne[p])
            rnd.shuffle(r)
            out.append((r[:len(r) // 2], r[len(r) // 2:]))
        return out
    v1 = prova(vere1, nullo1)
    print('1', dict(v1), flush=True)
    # 2. tutte le righe, nullo a pari tipo
    p2 = [p for p in pp if len(pag[p]) >= 16]
    vere2 = [([x[1] for x in pag[p][:len(pag[p]) // 2]], [x[1] for x in pag[p][len(pag[p]) // 2:]]) for p in p2]

    def nullo2():
        out = []
        for p in p2:
            rs = pag[p]
            nuove = [None] * len(rs)
            for t in ('prima', 'ultima', 'interna'):
                pos = [i for i, x in enumerate(rs) if x[0] == t]
                st = [rs[i][1] for i in pos]
                rnd.shuffle(st)
                for i, s in zip(pos, st):
                    nuove[i] = s
            h = len(rs) // 2
            out.append((nuove[:h], nuove[h:]))
        return out
    v2 = prova(vere2, nullo2)
    print('2', dict(v2), flush=True)
    # 3. primo contro ultimo paragrafo
    coppie3 = []
    for p in pp:
        par, cur = [], None
        for t, s, ini, fine in pag[p]:
            if ini:
                cur = []
            if cur is not None and not ini and not fine:
                cur.append(s)
            if fine and cur is not None:
                par.append(cur)
                cur = None
        if len(par) >= 3 and len(par[0]) >= 2 and len(par[-1]) >= 2:
            coppie3.append((par[0], par[-1]))

    def nullo3():
        out = []
        for a, b in coppie3:
            r = list(a) + list(b)
            rnd.shuffle(r)
            out.append((r[:len(a)], r[len(a):]))
        return out
    v3 = prova(coppie3, nullo3) if len(coppie3) >= 10 else OrderedDict([('coppie', len(coppie3))])
    print('3', dict(v3), flush=True)
    z12 = [v1['z_D1'], v1['z_D2'], v2['z_D1'], v2['z_D2']]
    esito = 'lo stato cambia davvero dentro la pagina' if max(z12) > 3 else ('l\'e326 era un effetto del tipo di riga' if max(z12) < 2 else 'incerto')
    esito3 = ('cambio fra paragrafi' if max(v3.get('z_D1', 0), v3.get('z_D2', 0)) > 3 else 'nessun cambio fra paragrafi') if 'z_D1' in v3 else 'troppo pochi paragrafi'
    out = OrderedDict([('1_solo_righe_interne', v1), ('2_nullo_a_pari_tipo', v2), ('3_primo_contro_ultimo_paragrafo', v3), ('esito', esito), ('esito_paragrafi', esito3)])
    json.dump(out, open(os.path.join(RISULTATI, 'e327_stato_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e327 — Lo stato dentro la pagina, senza le righe di inizio e fine paragrafo', '', 'Preregistrazione: `preregistrazioni/e327.md`.', '',
          '| versione | coppie | D1 (asse) | nullo | z | D2 (segni) | nullo | z |', '|---|---|---|---|---|---|---|---|']
    for k, v in list(out.items())[:3]:
        if 'z_D1' in v:
            md.append('| %s | %d | %.2f | %.2f | %.1f | %.4f | %.4f | %.1f |' % (k, v['coppie'], v['D1'], v['nullo_D1'], v['z_D1'], v['D2'], v['nullo_D2'], v['z_D2']))
        else:
            md.append('| %s | %d | – | – | – | – | – | – |' % (k, v['coppie']))
    md += ['', 'Esito: **%s**. Fra paragrafi: **%s**.' % (esito, esito3)]
    open(os.path.join(RISULTATI, 'e327_stato_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, '|', esito3)


if __name__ == '__main__':
    main()
