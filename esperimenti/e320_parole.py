# -*- coding: utf-8 -*-
"""Esperimenti 320, 321, 322. (e320) la prima parola del paragrafo, senza il gallows, ricompare nel suo paragrafo piu'
delle altre parole della prima riga? (e321) le parole tipiche della lingua B sono varianti di quelle di A? ci sono
pagine miste? (e322) le righe che si accorciano verso la fine del paragrafo: in quali sezioni?

Preregistrazione: preregistrazioni/e320.md. Scrive risultati/e320_parole.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e310_inizi_etichette as e310

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
PERM = 1000


def righe_voynich():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                out.append((r.pagina, bool(r.inizio_par), bool(r.fine_par), ws, r.sezione or '?', r.lingua or '?'))
    return out


def paragrafi(righe):
    out, cur = [], None
    for p, ini, fine, ws, s, l in righe:
        if ini:
            cur = {'pagina': p, 'sezione': s, 'lingua': l, 'righe': [ws]}
        elif cur is not None:
            cur['righe'].append(ws)
        if fine and cur is not None:
            out.append(cur)
            cur = None
    return out


def lev(a, b):
    prec = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prec[j] + 1, cur[j - 1] + 1, prec[j - 1] + (a[i - 1] != b[j - 1]))
        prec = cur
    return prec[-1]


# ---------- e320 ----------

def e320(par, rnd):
    par = [x for x in par if sum(len(r) for r in x['righe']) >= 15]
    parole = [[w for r in x['righe'] for w in r] for x in par]
    tipi = [Counter(ws) for ws in parole]
    per_len = [defaultdict(set) for _ in par]
    for k, ws in enumerate(parole):
        for w in set(ws):
            per_len[k][len(D(w))].add(tuple(D(w)))

    def nucleo(w):
        u = D(w)
        c = ''.join(u[1:]) if (u[0] in GALLOWS and len(u) > 1) else w
        return c if len(D(c)) >= 2 else None
    voci = []   # (paragrafo, parola da cercare, tipo 'nucleo'/'controllo')
    for k, x in enumerate(par):
        n = nucleo(x['righe'][0][0])
        if n:
            voci.append((k, n, 'nucleo', x['righe'][0][0]))
        for w in x['righe'][0][1:]:
            voci.append((k, w, 'controllo', w))

    def trova(w, k, togli):
        """(esatta, a una modifica) di w nel paragrafo k, togliendo un'occorrenza della parola 'togli' se e' di k."""
        c = tipi[k][w] - (1 if togli == w else 0)
        esatta = c > 0
        if esatta:
            return True, True
        u = tuple(D(w))
        vic = any(e310.dist1(u, y) for L in (len(u) - 1, len(u), len(u) + 1) for y in per_len[k].get(L, ()))
        return False, vic
    proprio = [trova(w, k, orig) for k, w, t, orig in voci]
    # blocchi per sezione e lunghezza
    per_sez = defaultdict(list)
    for k, x in enumerate(par):
        per_sez[x['sezione']].append(k)
    blocchi = []
    for s, ks in per_sez.items():
        ks = sorted(ks, key=lambda k: len(parole[k]))
        for i in range(0, len(ks), 5):
            blocchi.append(ks[i:i + 5])
    somma = [[0.0, 0.0] for _ in voci]
    nulli_n = []
    cache = {}
    for _ in range(PERM):
        a = {}
        for b in blocchi:
            x = list(b)
            rnd.shuffle(x)
            a.update(zip(b, x))
        es_n = []
        for i, (k, w, t, orig) in enumerate(voci):
            if a[k] == k:
                e_, v_ = proprio[i]
            else:
                ch = (w, a[k])
                if ch not in cache:
                    cache[ch] = trova(w, a[k], None)
                e_, v_ = cache[ch]
            somma[i][0] += e_
            somma[i][1] += v_
            if t == 'nucleo':
                es_n.append(e_)
        nulli_n.append(statistics.mean(es_n))
    altro = [(s0 / PERM, s1 / PERM) for s0, s1 in somma]
    gruppi = {'nucleo': [i for i, v in enumerate(voci) if v[2] == 'nucleo'], 'controllo': [i for i, v in enumerate(voci) if v[2] == 'controllo']}

    def R(ids, j):
        po = statistics.mean(proprio[i][j] for i in ids)
        pa = statistics.mean(altro[i][j] for i in ids)
        return po, pa, po / pa if pa else float('inf')
    out = OrderedDict()
    for g, ids in gruppi.items():
        out[g] = OrderedDict([('voci', len(ids)), ('esatta', R(ids, 0)), ('a_una_modifica', R(ids, 1))])
    # bootstrap sulla differenza dei R (esatta), ricampionando i paragrafi
    per_par = defaultdict(lambda: {'nucleo': [], 'controllo': []})
    for i, v in enumerate(voci):
        per_par[v[0]][v[2]].append(i)
    ks = list(per_par)
    diffs = []
    for _ in range(PERM):
        camp = [ks[rnd.randrange(len(ks))] for _ in ks]
        idn = [i for k in camp for i in per_par[k]['nucleo']]
        idc = [i for k in camp for i in per_par[k]['controllo']]
        rn, rc = R(idn, 0)[2], R(idc, 0)[2]
        if math.isfinite(rn) and math.isfinite(rc):
            diffs.append(rn - rc)
    d0 = out['nucleo']['esatta'][2] - out['controllo']['esatta'][2]
    z_diff = d0 / statistics.pstdev(diffs) if diffs and statistics.pstdev(diffs) else 0.0
    z_own = (out['nucleo']['esatta'][0] - statistics.mean(nulli_n)) / (statistics.pstdev(nulli_n) or 1)
    esito = 'parola-titolo' if (z_diff > 3 and z_own > 3) else ('no' if z_diff < 2 else 'incerto')
    esempi = [(par[k]['righe'][0][0], w) for (k, w, t, o), pr in zip(voci, proprio) if t == 'nucleo' and pr[0]][:20]
    return OrderedDict([('paragrafi', len(par)), ('misure', out), ('differenza_R', d0), ('z_differenza', z_diff), ('z_proprio_nuclei', z_own), ('esito', esito), ('esempi', esempi)])


# ---------- e321 ----------

def caratteristiche_AB(pag_A, pag_B):
    cA = Counter(w for p in pag_A for w in p['parole'])
    cB = Counter(w for p in pag_B for w in p['parole'])
    nA, nB = sum(cA.values()), sum(cB.values())
    cand = [w for w in set(cA) | set(cB) if cA[w] + cB[w] >= 10]
    lr = {w: math.log(((cB[w] + 0.5) / nB) / ((cA[w] + 0.5) / nA)) for w in cand}
    ordin = sorted(cand, key=lambda w: lr[w])
    return ordin[:40], ordin[-40:][::-1], cA


def operazione(a, b):
    """Descrive la modifica fra due tuple di segni a una modifica di distanza."""
    if len(a) == len(b):
        i = next(i for i in range(len(a)) if a[i] != b[i])
        return '%s→%s' % (a[i], b[i])
    if len(a) > len(b):
        i = next((i for i in range(len(b)) if a[i] != b[i]), len(b))
        return '−%s' % a[i]
    i = next((i for i in range(len(a)) if a[i] != b[i]), len(a))
    return '+%s' % b[i]


def e321(rnd):
    voy, X, nomi, P = e308.profili()
    testa = e308.intestazioni()
    herb = [p for p in voy.pagine if p['strato'][0] == 'H' and p['strato'][1] in ('A', 'B')]
    pA = [p for p in herb if p['strato'][1] == 'A']
    pB = [p for p in herb if p['strato'][1] == 'B']
    parA, parB, cA = caratteristiche_AB(pA, pB)
    dist = [min(lev(tuple(D(b)), tuple(D(a))) for a in parA) for b in parB]
    vero = statistics.mean(dist)
    pool = [w for w, n in cA.items() if n >= 10 and w not in parA and w not in parB]
    nulli = []
    for _ in range(PERM):
        cs = rnd.sample(pool, 40)
        nulli.append(statistics.mean(min(lev(tuple(D(b)), tuple(D(a))) for a in cs) for b in parB))
    z = (vero - statistics.mean(nulli)) / statistics.pstdev(nulli)
    esito_a = 'varianti' if z < -3 else ('vocabolari diversi' if abs(z) < 2 else 'incerto')
    coppie, ops = [], Counter()
    for b in parB:
        a = min(parA, key=lambda a: lev(tuple(D(b)), tuple(D(a))))
        d = lev(tuple(D(b)), tuple(D(a)))
        coppie.append((b, a, d))
        if d == 1:
            ops[operazione(tuple(D(a)), tuple(D(b)))] += 1
    # (b) pagine miste, con le parole scelte su meta' dei bifogli
    bif = lambda p: (testa.get(p['nome'], {}).get('Q'), testa.get(p['nome'], {}).get('B'))
    bifs = sorted({bif(p) for p in herb}, key=str)
    meta = {b: k % 2 for k, b in enumerate(bifs)}
    scelte = {}
    for f in (0, 1):
        a_, b_, _ = caratteristiche_AB([p for p in pA if meta[bif(p)] == f], [p for p in pB if meta[bif(p)] == f])
        scelte[f] = (set(a_), set(b_))
    tutte = (set(parA), set(parB))
    indici = []
    for p in voy.pagine:
        if p in herb:
            sA, sB = scelte[1 - meta[bif(p)]]
        else:
            sA, sB = tutte
        na = sum(w in sA for w in p['parole'])
        nb = sum(w in sB for w in p['parole'])
        if na + nb >= 10:
            indici.append((p['nome'], p['strato'][0], p['strato'][1], p['fascicolo'], na / (na + nb)))
    misti = [x for x in indici if 0.25 <= x[4] <= 0.75]
    q = len(misti) / len(indici)
    esito_b = 'passaggio graduale' if q >= 0.15 else ('netto' if q < 0.05 else 'intermedio')
    ist = Counter(min(int(x[4] * 10), 9) for x in indici)
    return OrderedDict([('parole_A', parA), ('parole_B', parB), ('distanza_media_B_da_A', vero), ('nullo', statistics.mean(nulli)), ('z', z), ('esito_a', esito_a),
                        ('coppie_B_A', coppie), ('modifiche_a_distanza_1', ops.most_common(10)), ('pagine', len(indici)), ('quota_miste', q), ('esito_b', esito_b),
                        ('istogramma_indice_A_decimi', [ist[k] for k in range(10)]), ('miste', misti)])


# ---------- e322 ----------

def e322(righe, par, rnd):
    def pendenza(pars, chiave):
        interne = [[chiave(ws) for ws in x['righe'][1:-1]] for x in pars if len(x['righe']) >= 5]
        if len(interne) < 10:
            return None

        def corr(ordini):
            ts, vs = [], []
            for vals, o in zip(interne, ordini):
                m = len(vals)
                for pos, v in zip(o, vals):
                    ts.append(pos / (m - 1))
                    vs.append(v)
            mt, mv = statistics.mean(ts), statistics.mean(vs)
            den = math.sqrt(sum((a - mt) ** 2 for a in ts) * sum((b - mv) ** 2 for b in vs))
            return sum((a - mt) * (b - mv) for a, b in zip(ts, vs)) / den if den else 0.0
        base = [list(range(len(v))) for v in interne]
        vero = corr(base)
        nul = []
        for _ in range(PERM):
            o = []
            for b in base:
                x = list(b)
                rnd.shuffle(x)
                o.append(x)
            nul.append(corr(o))
        return OrderedDict([('paragrafi', len(interne)), ('pendenza', vero), ('z', (vero - statistics.mean(nul)) / statistics.pstdev(nul))])
    nparole = lambda ws: float(len(ws))
    nsegni = lambda ws: float(sum(len(D(w)) for w in ws))
    per_sez = defaultdict(list)
    for x in par:
        per_sez[x['sezione']].append(x)
    sez = OrderedDict()
    for s, ps in sorted(per_sez.items(), key=str):
        a, b = pendenza(ps, nparole), pendenza(ps, nsegni)
        if a:
            sez[s] = OrderedDict([('parole', a), ('segni', b)])
    # posizione della riga nella pagina
    pag = defaultdict(list)
    for p, ini, fine, ws, s, l in righe:
        pag[(p, s)].append(len(ws))
    pagina = OrderedDict()
    for s in sorted({s for _, s in pag}, key=str):
        ps = [v for (p, s2), v in pag.items() if s2 == s and len(v) >= 6]
        if len(ps) < 5:
            continue

        def corr(ordini):
            ts, vs = [], []
            for vals, o in zip(ps, ordini):
                m = len(vals)
                for pos, v in zip(o, vals):
                    ts.append(pos / (m - 1))
                    vs.append(v)
            mt, mv = statistics.mean(ts), statistics.mean(vs)
            den = math.sqrt(sum((a - mt) ** 2 for a in ts) * sum((b - mv) ** 2 for b in vs))
            return sum((a - mt) * (b - mv) for a, b in zip(ts, vs)) / den if den else 0.0
        base = [list(range(len(v))) for v in ps]
        vero = corr(base)
        nul = []
        for _ in range(PERM):
            o = []
            for b in base:
                x = list(b)
                rnd.shuffle(x)
                o.append(x)
            nul.append(corr(o))
        pagina[s] = OrderedDict([('pagine', len(ps)), ('correlazione', vero), ('z', (vero - statistics.mean(nul)) / statistics.pstdev(nul))])
    zS = sez.get('S', {}).get('parole', {}).get('z')
    zH = sez.get('H', {}).get('parole', {}).get('z')
    if zS is not None and zS < -3:
        esito = 'abitudine dello scriba'
    elif zH is not None and zH < -3 and (zS is None or zS > -2):
        esito = 'effetto dell\'impaginazione'
    else:
        esito = 'incerto'
    return OrderedDict([('per_sezione', sez), ('posizione_nella_pagina', pagina), ('esito', esito)])


def main():
    righe = righe_voynich()
    par = paragrafi(righe)
    r320 = e320(par, random.Random(320))
    print('e320', r320['esito'], round(r320['differenza_R'], 3), round(r320['z_differenza'], 1), round(r320['z_proprio_nuclei'], 1), {g: {k: (tuple(round(x, 3) for x in v) if isinstance(v, tuple) else v) for k, v in m.items()} for g, m in r320['misure'].items()}, flush=True)
    r321 = e321(random.Random(321))
    print('e321', r321['esito_a'], round(r321['distanza_media_B_da_A'], 2), round(r321['nullo'], 2), round(r321['z'], 1), r321['esito_b'], round(r321['quota_miste'], 3), r321['istogramma_indice_A_decimi'], flush=True)
    r322 = e322(righe, par, random.Random(322))
    print('e322', r322['esito'], {s: (round(v['parole']['pendenza'], 3), round(v['parole']['z'], 1)) for s, v in r322['per_sezione'].items()}, flush=True)
    json.dump(OrderedDict([('e320', r320), ('e321', r321), ('e322', r322)]), open(os.path.join(RISULTATI, 'e320_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    m = r320['misure']
    md = ['# e320, e321, e322 — La prima parola del paragrafo; da A a B; le righe che si accorciano', '', 'Preregistrazione: `preregistrazioni/e320.md`.', '',
          '## e320 — %d paragrafi' % r320['paragrafi'], '', '| voci | numero | nel proprio paragrafo | in un altro | R | a una modifica: proprio | altro | R |', '|---|---|---|---|---|---|---|---|']
    for g in ('nucleo', 'controllo'):
        e_, v_ = m[g]['esatta'], m[g]['a_una_modifica']
        md.append('| %s | %d | %.3f | %.3f | %.2f | %.3f | %.3f | %.2f |' % ('nucleo della prima parola' if g == 'nucleo' else 'altre parole della prima riga', m[g]['voci'], e_[0], e_[1], e_[2], v_[0], v_[1], v_[2]))
    md += ['', 'Differenza dei R (esatta) %+.2f, z %.1f; nuclei, proprio contro altro, z %.1f. Esito e320: **%s**.' % (r320['differenza_R'], r320['z_differenza'], r320['z_proprio_nuclei'], r320['esito']),
           'Esempi (prima parola → nucleo ritrovato nel paragrafo): %s.' % ', '.join('%s → %s' % e for e in r320['esempi'][:12]), '', '## e321', '',
           'Parole tipiche di B (erbario): %s.' % ', '.join(r321['parole_B'][:20]), 'Parole tipiche di A: %s.' % ', '.join(r321['parole_A'][:20]), '',
           '(a) Distanza media di ogni parola-B dalla parola-A più vicina %.2f segni, contro %.2f del nullo, z %.1f: **%s**. Modifiche più comuni a distanza 1 (A → B): %s.' % (
               r321['distanza_media_B_da_A'], r321['nullo'], r321['z'], r321['esito_a'], ', '.join('%s (%d)' % o for o in r321['modifiche_a_distanza_1']) or 'nessuna'),
           'Coppie B–A più vicine: %s.' % ', '.join('%s~%s (%d)' % c for c in sorted(r321['coppie_B_A'], key=lambda c: c[2])[:15]), '',
           '(b) %d pagine; indice-A per decimi (da tutto B a tutto A): %s; pagine miste (0,25–0,75): %.0f%%: **%s**.' % (
               r321['pagine'], r321['istogramma_indice_A_decimi'], 100 * r321['quota_miste'], r321['esito_b']),
           'Pagine miste: %s.' % ', '.join('%s (%s-%s, fascicolo %s, %.2f)' % x for x in r321['miste']), '', '## e322', '', '| sezione | paragrafi | pendenza parole | z | pendenza segni | z |', '|---|---|---|---|---|---|']
    for s, v in r322['per_sezione'].items():
        md.append('| %s | %d | %+.3f | %.1f | %+.3f | %.1f |' % (s, v['parole']['paragrafi'], v['parole']['pendenza'], v['parole']['z'], v['segni']['pendenza'], v['segni']['z']))
    md += ['', 'Posizione della riga nella pagina contro numero di parole: %s.' % '; '.join('%s %.3f (z %.1f, %d pagine)' % (s, v['correlazione'], v['z'], v['pagine']) for s, v in r322['posizione_nella_pagina'].items()),
           '', 'Esito e322: **%s**.' % r322['esito']]
    open(os.path.join(RISULTATI, 'e320_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
