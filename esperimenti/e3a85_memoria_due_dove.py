# -*- coding: utf-8 -*-
"""Esperimento e3a85: eccesso di informazione condizionata I(a;c|b) nelle terne di segni dentro le parole, rispetto a
testi simulati con una catena di ordine 1; Voynich, generatori, testi sensati; scomposizione per segno di mezzo e posto.

Preregistrazione: preregistrazioni/e3a85.md. Scrive risultati/e3a85_memoria_due_dove.json e .md.
"""
import bisect, json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SIM = 20


def terne(parole):
    out = []
    for w in parole:
        n = len(w)
        for i in range(n - 2):
            posto = ('tutte e due' if n == 3 else 'inizio') if i == 0 else ('fine' if i + 2 == n - 1 else 'mezzo')
            out.append((w[i], w[i + 1], w[i + 2], posto))
    return out


def cmi_per_b(tt):
    """{b: (peso P(b), I(a;c|b))} e CMI totale."""
    per = defaultdict(Counter)
    for a, b, c, _ in tt:
        per[b][a, c] += 1
    n = len(tt)
    out = {}
    tot = 0.0
    for b, cc in per.items():
        m = sum(cc.values())
        sa, sc = Counter(), Counter()
        for (a, c), k in cc.items():
            sa[a] += k
            sc[c] += k
        i = sum(k / m * math.log2(k * m / (sa[a] * sc[c])) for (a, c), k in cc.items())
        out[b] = (m / n, i)
        tot += m / n * i
    return out, tot


def catena1(parole):
    c = defaultdict(Counter)
    for w in parole:
        s = ['^'] + list(w) + ['$']
        for a, b in zip(s, s[1:]):
            c[a][b] += 1
    return {a: (list(cc), list(np.cumsum(list(cc.values())))) for a, cc in c.items()}


def simula(tab, n, rnd):
    out = []
    while len(out) < n:
        a, w = '^', []
        while len(w) < 30:
            simboli, cum = tab[a]
            x = simboli[bisect.bisect_right(cum, rnd.random() * cum[-1])]
            if x == '$':
                break
            w.append(x)
            a = x
        if w:
            out.append(tuple(w))
    return out


def eccesso(parole, rnd, dettaglio=False):
    parole = [tuple(w) for w in parole]
    tt = terne(parole)
    per_o, tot_o = cmi_per_b(tt)
    tab = catena1(parole)
    sims = [cmi_per_b(terne(simula(tab, len(parole), rnd))) for _ in range(SIM)]
    ecc = tot_o - statistics.mean(t for _, t in sims)
    if not dettaglio:
        return ecc
    per_b = {}
    for b, (p, i) in per_o.items():
        i_sim = statistics.mean(s[0].get(b, (0, 0))[1] for s in sims)
        per_b[b] = p * (i - i_sim)
    # per posto: CMI calcolata dentro ogni classe di posto, pesata
    per_posto = OrderedDict()
    sim_tt = [terne(simula(tab, len(parole), rnd)) for _ in range(5)]
    for posto in ('inizio', 'mezzo', 'fine', 'tutte e due'):
        sub = [t for t in tt if t[3] == posto]
        if not sub:
            continue
        o = cmi_per_b(sub)[1]
        s = statistics.mean(cmi_per_b([t for t in st if t[3] == posto])[1] for st in sim_tt)
        per_posto[posto] = OrderedDict([('terne', len(sub)), ('quota_terne', len(sub) / len(tt)), ('eccesso', o - s)])
    return ecc, per_b, per_posto


def main():
    rnd = random.Random(3185)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        sub.append(eccesso(prese, rnd))
    ris = OrderedDict([('Voynich', OrderedDict([('eccesso', statistics.median(sub)), ('sottoinsiemi', sub)]))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            ris[k] = OrderedDict([('eccesso', eccesso(e3a55.prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]), rnd))])
    ris['Timm e Schinner, seme 1'] = OrderedDict([('eccesso', eccesso(e3a55.prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]), rnd))])
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    sens = OrderedDict((k.replace('.txt', ''), eccesso(e3a55.prime(t), rnd)) for k, t in e381.testi().items())
    gen = [ris[k]['eccesso'] for k in ris if k != 'Voynich']
    v = ris['Voynich']['eccesso']
    esito = 'il Voynich ha più memoria di due segni dei generatori' if v > max(gen) else ('meno' if v < min(gen) else 'come i generatori')
    vals = sorted(sens.values())
    q = sum(1 for x in vals if x < v) / len(vals)
    tutto = [w for p in voy_pag for r in p for w in r]
    ecc_t, per_b, per_posto = eccesso(tutto, rnd, dettaglio=True)
    tot_b = sum(per_b.values())
    top = sorted(per_b.items(), key=lambda kv: -kv[1])[:6]
    out = OrderedDict([('testi', ris), ('lingue', OrderedDict([('minimo', vals[0]), ('mediana', float(np.median(vals))), ('massimo', vals[-1]), ('quota_sotto_il_voynich', q)])),
                       ('voynich_tutto', OrderedDict([('eccesso', ecc_t), ('segni_di_mezzo', [[b, c, c / tot_b] for b, c in top]), ('posti', per_posto)])),
                       ('testi_sensati', sens), ('esito', esito)])
    print(json.dumps(out['voynich_tutto'], ensure_ascii=False), esito, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a85_memoria_due_dove.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a85 — Dove sta la "memoria di due segni" delle parole del Voynich?', '', 'Preregistrazione: `preregistrazioni/e3a85.md`. Eccesso di I(a;c|b) (bit per terna) rispetto a 20 simulazioni di ordine 1.', '',
          '| testo | eccesso |', '|---|---|']
    md += ['| %s | %.4f%s |' % (k, x['eccesso'], ' (sottoinsiemi: %s)' % ', '.join('%.4f' % s for s in x['sottoinsiemi']) if 'sottoinsiemi' in x else '') for k, x in ris.items()]
    md += ['| testi sensati | mediana %.4f (da %.4f a %.4f); il Voynich supera il %.0f%% |' % (float(np.median(vals)), vals[0], vals[-1], 100 * q), '',
           'Esito: **%s**.' % esito, '', '## Voynich, testo intero (descrittivo)', '', 'Eccesso %.4f bit per terna.' % ecc_t, '',
           '| segno di mezzo | contributo | quota |', '|---|---|---|']
    md += ['| %s | %.4f | %.0f%% |' % (b, c, 100 * c / tot_b) for b, c in top]
    md += ['', '| posto della terna | terne | quota | eccesso dentro la classe |', '|---|---|---|---|']
    md += ['| %s | %d | %.2f | %.4f |' % (k, x['terne'], x['quota_terne'], x['eccesso']) for k, x in per_posto.items()]
    open(os.path.join(RISULTATI, 'e3a85_memoria_due_dove.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
