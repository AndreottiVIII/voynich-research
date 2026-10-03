# -*- coding: utf-8 -*-
"""Esperimento 355: (a) le varianti rare di parole frequenti tornano sulle pagine dello stesso bifoglio piu' del caso?
(b) la quota di parole uniche varia fra i bifogli piu' del caso, ed e' legata alla ripresa?

Preregistrazione: preregistrazioni/e355.md. Scrive risultati/e355_sessioni_errori.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e341_fonti as e341
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
CLASSI = ['stesso foglio', 'stesso bifoglio, fogli diversi', 'apertura', 'stesso fascicolo, altro', 'altro fascicolo']


def classe(x, y, testa, seg):
    hx, hy = testa[x], testa[y]
    if hx['Q'] == hy['Q'] and hx['F'] == hy['F']:
        return 'stesso foglio'
    if hx['Q'] == hy['Q'] and hx['B'] == hy['B']:
        return 'stesso bifoglio, fogli diversi'
    if (seg.get(x) == y and hx['lato'] == 'v' and hy['lato'] == 'r') or (seg.get(y) == x and hy['lato'] == 'v' and hx['lato'] == 'r'):
        return 'apertura'
    return 'stesso fascicolo, altro' if hx['Q'] == hy['Q'] else 'altro fascicolo'


def main():
    rnd = random.Random(355)
    testa = e308.intestazioni()
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seg = dict(zip(ordine, ordine[1:]))
    pag = e341.pagine()
    sez = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        sez.setdefault(r.pagina, r.sezione or '?')
    pagine = [p for p in pag if testa.get(p, {}).get('Q')]
    tok = [(p, w) for p in pagine for par in pag[p] for r in par for w in r]
    freq = Counter(w for _, w in tok)
    sim = e350.simili_globali(set(freq))
    varianti = {w for w, n in freq.items() if 2 <= n <= 5 and any(freq[v] >= 20 for v in sim[w] if v != w)}
    # (a)
    pos_sez = defaultdict(list)
    for p, w in tok:
        pos_sez[sez[p]].append(p)
    var_sez = defaultdict(list)    # sezione -> [tipo variante per ogni occorrenza]
    for p, w in tok:
        if w in varianti:
            var_sez[sez[p]].append(w)

    def conta(assegna):
        c = Counter()
        for s, occ in assegna.items():
            per_tipo = defaultdict(list)
            for w, p in occ:
                per_tipo[w].append(p)
            for w, ps in per_tipo.items():
                for i in range(len(ps)):
                    for j in range(i + 1, len(ps)):
                        if ps[i] != ps[j]:
                            c[classe(ps[i], ps[j], testa, seg)] += 1
        return c
    vero_ass = defaultdict(list)
    for p, w in tok:
        if w in varianti:
            vero_ass[sez[p]].append((w, p))
    vero = conta(vero_ass)
    nul = []
    for _ in range(1000):
        ass = {}
        for s, tipi in var_sez.items():
            posti = rnd.sample(pos_sez[s], len(tipi))
            ass[s] = list(zip(tipi, posti))
        nul.append(conta(ass))
    a = OrderedDict()
    for c in CLASSI:
        xs = [n[c] for n in nul]
        m, sd = statistics.mean(xs), statistics.pstdev(xs)
        a[c] = OrderedDict([('osservate', vero[c]), ('attese', m), ('rapporto', vero[c] / m if m else None), ('z', (vero[c] - m) / sd if sd else 0.0)])
    b_ = a['stesso bifoglio, fogli diversi']
    esito_a = 'varianti di sessione' if (b_['z'] > 3 and (b_['rapporto'] or 0) > (a['apertura']['rapporto'] or 0)) else ('no' if b_['z'] < 2 else 'incerto')
    # (b)
    bif_tok = defaultdict(list)
    for p, w in tok:
        bif_tok[(testa[p]['Q'], testa[p]['B'])].append(w)
    rip = {}
    for b in bif_tok:
        pars = [par for p in pagine if (testa[p]['Q'], testa[p]['B']) == b for par in pag[p]]
        si = tot = nulsum = 0.0
        for par in pars:
            if len(par) < 4:
                continue

            def q(x):
                s_ = t_ = 0
                for i in range(2, len(x)):
                    sopra = x[i - 1] + x[i - 2]
                    for w in x[i]:
                        t_ += 1
                        s_ += e341.ha_fonte(w, sopra)
                return s_, t_
            s1, t1 = q(par)
            si += s1
            tot += t1
            nulsum += statistics.mean(q(rnd.sample(par, len(par)))[0] for _ in range(50))
        rip[b] = (si - nulsum) / tot if tot else None
    sez_b = {b: Counter(sez[p] for p in pagine if (testa[p]['Q'], testa[p]['B']) == b).most_common(1)[0][0] for b in bif_tok}
    grandi = [b for b, ws in bif_tok.items() if len(ws) >= 150]
    quota = {b: sum(freq[w] == 1 for w in bif_tok[b]) / len(bif_tok[b]) for b in grandi}
    var_vero = statistics.pvariance(list(quota.values()))
    nul_v = []
    per_s = defaultdict(list)
    for b in grandi:
        per_s[sez_b[b]].append(b)
    for _ in range(1000):
        q2 = {}
        for s, bs in per_s.items():
            ind = [freq[w] == 1 for b in bs for w in bif_tok[b]]
            rnd.shuffle(ind)
            i = 0
            for b in bs:
                n = len(bif_tok[b])
                q2[b] = sum(ind[i:i + n]) / n
                i += n
        nul_v.append(statistics.pvariance(list(q2.values())))
    zv = (var_vero - statistics.mean(nul_v)) / statistics.pstdev(nul_v)
    from scipy.stats import spearmanr
    bs = [b for b in grandi if rip.get(b) is not None]
    xs, ys = [quota[b] for b in bs], [rip[b] for b in bs]
    rho = spearmanr(xs, ys).correlation
    nr = [spearmanr(xs, rnd.sample(ys, len(ys))).correlation for _ in range(1000)]
    zr = (rho - statistics.mean(nr)) / statistics.pstdev(nr)
    esito_b = ('sessioni più o meno inventive' if zv > 3 else ('no' if zv < 2 else 'incerto')) + ('; chi inventa di più copia di meno' if zr < -3 else '')
    out = OrderedDict([('varianti_tipi', len(varianti)), ('a', a), ('esito_a', esito_a),
                       ('b', OrderedDict([('bifogli', len(grandi)), ('varianza_quota_uniche', var_vero), ('nullo', statistics.mean(nul_v)), ('rapporto', var_vero / statistics.mean(nul_v)),
                                          ('z', zv), ('spearman_uniche_ripresa', rho), ('z_spearman', zr), ('bifogli_con_ripresa', len(bs))])), ('esito_b', esito_b)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:1500], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e355_sessioni_errori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e355 — Le sessioni di scrittura: errori ricorrenti e parole uniche', '', 'Preregistrazione: `preregistrazioni/e355.md`.', '',
          '## (a) %d varianti rare: coppie di occorrenze su pagine diverse della stessa sezione' % len(varianti), '', '| classe | osservate | attese | rapporto | z |', '|---|---|---|---|---|']
    for c, v in a.items():
        md.append('| %s | %d | %.1f | %.2f | %.1f |' % (c, v['osservate'], v['attese'], v['rapporto'] or 0, v['z']))
    bb = out['b']
    md += ['', 'Esito (a): **%s**.' % esito_a, '', '## (b) Parole uniche per bifoglio (%d bifogli con almeno 150 parole)' % bb['bifogli'], '',
           '- Varianza della quota di uniche fra i bifogli: %.6f contro %.6f del nullo (rapporto %.2f), z %.1f.' % (bb['varianza_quota_uniche'], bb['nullo'], bb['rapporto'], bb['z']),
           '- Spearman fra quota di uniche e ripresa (E1p) del bifoglio: %.3f su %d bifogli, z %.1f.' % (bb['spearman_uniche_ripresa'], bb['bifogli_con_ripresa'], bb['z_spearman']),
           '', 'Esito (b): **%s**.' % esito_b]
    open(os.path.join(RISULTATI, 'e355_sessioni_errori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
