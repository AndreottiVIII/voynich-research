# -*- coding: utf-8 -*-
"""Esperimenti 342 e 343. (e342) quali modifiche separano una parola dalla sua fonte nelle righe sopra, rispetto alle
coppie a una modifica lontane nella pagina; confronto con il generatore di Timm e Schinner. (e343) lunghezza delle
catene di ripresa; il paragrafo come confine per la ripresa.

Preregistrazione: preregistrazioni/e342.md. Scrive risultati/e342_copie.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e337_posizione as e337
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
u, simile = e341.u, e341.simile


def operazione(a, b):
    """Tipo di modifica dalla fonte a (tuple di segni) alla parola b, a una modifica di distanza."""
    if len(a) == len(b):
        i = next(i for i in range(len(a)) if a[i] != b[i])
        return '%s→%s' % (a[i], b[i])
    if len(b) > len(a):
        i = next((i for i in range(len(a)) if a[i] != b[i]), len(a))
        posto = 'inizio' if i == 0 else ('fine' if i == len(b) - 1 else 'interno')
        return '+%s (%s)' % (b[i], posto)
    i = next((i for i in range(len(b)) if a[i] != b[i]), len(b))
    posto = 'inizio' if i == 0 else ('fine' if i == len(a) - 1 else 'interno')
    return '−%s (%s)' % (a[i], posto)


def fonte_vicina(par, i, j, solo_modifica, fuori_paragrafo=None):
    """(riga, posizione) della fonte piu' vicina della parola par[i][j] nelle 2 righe sopra dello stesso paragrafo."""
    w = par[i][j]
    for d in (1, 2):
        if i - d < 0:
            break
        cand = [(abs(k - j), k) for k, x in enumerate(par[i - d]) if simile(w, x) and (not solo_modifica or x != w)]
        if cand:
            return i - d, min(cand)[1]
    return None


def e342_testo(paragrafi_per_pagina):
    vicine, lontane = Counter(), Counter()
    for pars in paragrafi_per_pagina:
        righe = [r for par in pars for r in par]
        for par in pars:
            for i in range(1, len(par)):
                for j, w in enumerate(par[i]):
                    f = fonte_vicina(par, i, j, True)
                    if f:
                        vicine[operazione(u(par[f[0]][f[1]]), u(w))] += 1
        for i, r in enumerate(righe):
            for w in r:
                for k in list(range(i + 6, len(righe))) + list(range(i - 6, -1, -1)):
                    x = next((x for x in righe[k] if x != w and simile(w, x)), None)
                    if x:
                        lontane[operazione(u(x), u(w))] += 1
                        break
    return vicine, lontane


def confronta(vicine, lontane):
    nv, nl = sum(vicine.values()), sum(lontane.values())
    out = OrderedDict()
    for op, c in vicine.most_common(25):
        pv, pl = c / nv, (lontane[op] + 0.5) / (nl + 0.5)
        out[op] = OrderedDict([('vicine', c), ('quota_vicine', pv), ('quota_lontane', pl), ('rapporto', pv / pl), ('z', (pv - pl) / math.sqrt(pl * (1 - pl) / nv))])
    return out, nv, nl


def e342():
    pag = e341.pagine()
    v, l = e342_testo(list(pag.values()))
    voy, nv, nl = confronta(v, l)
    ts = {}
    for s in (1, 19):
        pp = [[p] for p in e337.pagine_ts(s)]
        tv, tl = e342_testo(pp)
        ts[s] = confronta(tv, tl)[0]
    pref = [op for op, x in voy.items() if x['rapporto'] > 1.5 and x['z'] > 3]
    evit = [op for op, x in voy.items() if x['rapporto'] < 0.67 and x['z'] < -3]
    pref_ts = set(op for s in ts for op, x in ts[s].items() if x['rapporto'] > 1.5 and x['z'] > 3)
    return OrderedDict([('coppie_vicine', nv), ('coppie_lontane', nl), ('modifiche', voy), ('preferite', pref), ('evitate', evit),
                        ('preferite_anche_dal_generatore', [op for op in pref if op in pref_ts]), ('preferite_dal_generatore', sorted(pref_ts))])


def e343(rnd):
    pag = e341.pagine()
    pars = [par for pars_ in pag.values() for par in pars_]

    def lunghezze(paragrafi):
        tot = []
        for par in paragrafi:
            link = {}
            for i in range(1, len(par)):
                for j in range(len(par[i])):
                    f = fonte_vicina(par, i, j, False)
                    if f:
                        link[(i, j)] = f
            memo = {}

            def lung(n):
                if n not in memo:
                    memo[n] = 1 + lung(link[n]) if n in link else 0
                return memo[n]
            tot += [lung((i, j)) for i in range(len(par)) for j in range(len(par[i]))]
        return statistics.mean(tot), Counter(min(x, 6) for x in tot)
    vero, dist = lunghezze(pars)
    nul = []
    for _ in range(200):
        nul.append(lunghezze([rnd.sample(par, len(par)) for par in pars])[0])
    za = (vero - statistics.mean(nul)) / statistics.pstdev(nul)
    # (b) confine del paragrafo
    per_par = []     # per paragrafo: (A_si, A_n, B_quota_media, A1_si, A1_n, B1_quota_media)
    for pp in pag.values():
        for k, par in enumerate(pp):
            a = b = a1 = b1 = None
            if k > 0 and len(pp[k - 1]) >= 2:
                prec = pp[k - 1]
                ws = par[0]
                a = (sum(e341.ha_fonte(w, prec[-1]) for w in ws), len(ws))
                b = statistics.mean(statistics.mean(e341.ha_fonte(w, r) for w in ws) for r in prec[:-1])
            inter = [(i, par[i]) for i in range(2, len(par) - 1)]
            if inter:
                s1 = n1 = 0
                qs = []
                for i, ws in inter:
                    s1 += sum(e341.ha_fonte(w, par[i - 1]) for w in ws)
                    n1 += len(ws)
                    lont = [par[x] for x in range(len(par)) if abs(x - i) >= 2]
                    if lont:
                        qs.append(statistics.mean(statistics.mean(e341.ha_fonte(w, r) for w in ws) for r in lont))
                a1 = (s1, n1)
                b1 = statistics.mean(qs) if qs else None
            per_par.append((a, b, a1, b1))

    def stima(campione):
        A = [x for x in campione if x[0] is not None]
        I = [x for x in campione if x[2] is not None and x[3] is not None]
        ab = sum(x[0][0] for x in A) / sum(x[0][1] for x in A) - statistics.mean(x[1] for x in A)
        ab1 = sum(x[2][0] for x in I) / sum(x[2][1] for x in I) - statistics.mean(x[3] for x in I)
        return ab, ab1
    v_ab, v_ab1 = stima(per_par)
    boot = [stima([per_par[rnd.randrange(len(per_par))] for _ in per_par]) for _ in range(1000)]
    sd_diff = statistics.pstdev((b[0] - b[1]) for b in boot)
    sd_ab = statistics.pstdev(b[0] for b in boot)
    z_diff = ((v_ab - v_ab1) / sd_diff) if sd_diff else 0.0
    z_ab = (v_ab / sd_ab) if sd_ab else 0.0
    if z_diff < -3 and z_ab < 2:
        esito_b = 'il paragrafo è un confine per la ripresa'
    elif z_ab > 3:
        esito_b = 'la ripresa attraversa il paragrafo'
    else:
        esito_b = 'incerto'
    return OrderedDict([('lunghezza_media', vero), ('nullo', statistics.mean(nul)), ('z_lunghezza', za), ('distribuzione', {str(k): v for k, v in sorted(dist.items())}),
                        ('esito_a', 'catene più lunghe del caso' if za > 3 else ('no' if za < 2 else 'incerto')),
                        ('A_meno_B_confine', v_ab), ('z_A_meno_B', z_ab), ('A1_meno_B1_interne', v_ab1), ('z_differenza', z_diff), ('esito_b', esito_b)])


def main():
    r343 = e343(random.Random(343))
    print('e343', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r343.items()}, flush=True)
    r342 = e342()
    print('e342', r342['coppie_vicine'], r342['coppie_lontane'], 'preferite', r342['preferite'], 'evitate', r342['evitate'], 'anche TS', r342['preferite_anche_dal_generatore'], flush=True)
    json.dump(OrderedDict([('e342', r342), ('e343', r343)]), open(os.path.join(RISULTATI, 'e342_copie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e342, e343 — Le regole delle modifiche; le catene di copia', '', 'Preregistrazione: `preregistrazioni/e342.md`.', '',
          '## e342 — %d coppie parola/fonte vicina, %d coppie lontane di riferimento' % (r342['coppie_vicine'], r342['coppie_lontane']), '',
          '| modifica (fonte → parola) | coppie vicine | quota vicine | quota lontane | rapporto | z |', '|---|---|---|---|---|---|']
    for op, x in r342['modifiche'].items():
        md.append('| %s | %d | %.3f | %.3f | %.2f | %.1f |' % (op, x['vicine'], x['quota_vicine'], x['quota_lontane'], x['rapporto'], x['z']))
    md += ['', 'Preferite nella ripresa: %s.' % (', '.join(r342['preferite']) or 'nessuna'), 'Evitate: %s.' % (', '.join(r342['evitate']) or 'nessuna'),
           'Preferite anche dal generatore di Timm e Schinner: %s (il generatore preferisce: %s).' % (', '.join(r342['preferite_anche_dal_generatore']) or 'nessuna', ', '.join(r342['preferite_dal_generatore']) or 'nessuna'),
           '', '## e343', '', '(a) Lunghezza media delle catene %.3f contro %.3f con le righe rimescolate nel paragrafo, z %.1f: **%s**. Distribuzione (0–6+): %s.' % (
               r343['lunghezza_media'], r343['nullo'], r343['z_lunghezza'], r343['esito_a'], r343['distribuzione']), '',
           '(b) Prima riga del paragrafo: ultima riga del paragrafo precedente meno una sua riga qualsiasi %+.4f (z %.1f); righe interne: riga sopra meno una riga lontana dello stesso paragrafo %+.4f; differenza z %.1f: **%s**.' % (
               r343['A_meno_B_confine'], r343['z_A_meno_B'], r343['A1_meno_B1_interne'], r343['z_differenza'], r343['esito_b'])]
    open(os.path.join(RISULTATI, 'e342_copie.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
