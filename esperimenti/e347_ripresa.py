# -*- coding: utf-8 -*-
"""Esperimenti 347, 348, 349 sulla ripresa dalle righe sopra. (e347) eccesso di ripresa per distanza in righe 1-6, esatta
e modificata, Voynich e generatore di Timm e Schinner; (e348) le parole uniche hanno piu' spesso una fonte modificata
nelle righe sopra delle altre parole della stessa lunghezza?; (e349) la ripresa per strato sezione x lingua e per mano.

Preregistrazione: preregistrazioni/e347.md. Scrive risultati/e347_ripresa.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e337_posizione as e337
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
simile, u = e341.simile, e341.u


def paragrafi():
    """Lista di paragrafi: {'righe': [[parole]], 'strato': 'S-L', 'mano': h}."""
    out, cur = [], None
    pag_prec = None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if not ws:
            continue
        if r.inizio_par or cur is None or r.pagina != pag_prec:
            cur = {'righe': [], 'strato': '%s-%s' % (r.sezione or '?', r.lingua or '?'), 'mano': r.mano or '?'}
            out.append(cur)
        cur['righe'].append(ws)
        pag_prec = r.pagina
    return out


def esatta(w, riga):
    return w in riga


def modificata(w, riga):
    return any(x != w and simile(w, x) for x in riga)


def e347(pars, rnd):
    out = OrderedDict()
    for L in range(1, 7):
        voci = [(k, i) for k, p in enumerate(pars) if len(p) >= L + 2 for i in range(L, len(p))]
        if not voci:
            continue

        def conta(scelta):
            es = mo = tot = 0
            for k, i in voci:
                fonte = pars[k][scelta(k, i)]
                for w in pars[k][i]:
                    tot += 1
                    es += esatta(w, fonte)
                    mo += modificata(w, fonte)
            return es / tot, mo / tot
        vero = conta(lambda k, i: i - L)
        nul = [conta(lambda k, i: rnd.choice([j for j in range(len(pars[k])) if j != i])) for _ in range(200)]
        r = OrderedDict([('righe', len(voci))])
        for j, nome in enumerate(('esatta', 'modificata')):
            m, sd = statistics.mean(n[j] for n in nul), statistics.pstdev(n[j] for n in nul)
            r[nome] = OrderedDict([('quota', vero[j]), ('nullo', m), ('eccesso', vero[j] - m), ('z', (vero[j] - m) / (sd or 1))])
        out[L] = r
    return out


def e348(pars, rnd):
    freq = Counter(w for p in pars for r in p for w in r)
    # per paragrafo: lista di (lunghezza, unica, indicatore vero, media dell'indicatore nel nullo, frequenza della fonte)
    righe_tok = []
    for p in pars:
        voci = []
        if len(p) >= 3:
            def indic(ordine):
                """{(riga originale, posizione): fonte modificata nelle 2 righe sopra} con le righe nell'ordine dato."""
                out = {}
                for t, o in enumerate(ordine):
                    sopra = (p[ordine[t - 1]] if t >= 1 else []) + (p[ordine[t - 2]] if t >= 2 else [])
                    for j, w in enumerate(p[o]):
                        out[(o, j)] = modificata(w, sopra)
                return out
            vero = indic(list(range(len(p))))
            acc = Counter()
            for _ in range(200):
                for key, val in indic(rnd.sample(range(len(p)), len(p))).items():
                    acc[key] += val
            for i in range(1, len(p)):
                sopra = p[i - 1] + (p[i - 2] if i >= 2 else [])
                for j, w in enumerate(p[i]):
                    fonti = [x for x in sopra if x != w and simile(w, x)]
                    voci.append((len(u(w)), freq[w] == 1, vero[(i, j)], acc[(i, j)] / 200, freq[fonti[0]] if fonti else None))
        righe_tok.append(voci)

    def stima(campione):
        hap = [v for p in campione for v in p if v[1]]
        non = [v for p in campione for v in p if not v[1]]
        if not hap or not non:
            return None
        eh = statistics.mean(v[2] - v[3] for v in hap)
        per_L = defaultdict(list)
        for v in non:
            per_L[v[0]].append(v[2] - v[3])
        lh = Counter(v[0] for v in hap)
        pesi = [(c, statistics.mean(per_L[L])) for L, c in lh.items() if per_L.get(L)]
        en = sum(c * m for c, m in pesi) / sum(c for c, _ in pesi)
        return eh, en
    eh, en = stima(righe_tok)
    boot = [b for b in (stima([righe_tok[rnd.randrange(len(righe_tok))] for _ in righe_tok]) for _ in range(1000)) if b]
    sd = statistics.pstdev(b[0] - b[1] for b in boot)
    z = (eh - en) / sd if sd else 0.0
    fh = [v[4] for p in righe_tok for v in p if v[1] and v[4]]
    fn = [v[4] for p in righe_tok for v in p if not v[1] and v[4]]
    esito = 'le parole uniche nascono dalla ripresa' if z > 3 else ('no' if z < 2 else 'incerto')
    return OrderedDict([('unici', sum(1 for p in righe_tok for v in p if v[1])), ('eccesso_unici', eh), ('eccesso_altri_stessa_lunghezza', en), ('z', z), ('esito', esito),
                        ('frequenza_mediana_fonti_unici', statistics.median(fh) if fh else None), ('frequenza_mediana_fonti_altri', statistics.median(fn) if fn else None)])


def e349(pars, rnd):
    dati = []    # per paragrafo: (strato, mano, si, tot, nullo_medio*tot)
    for p in pars['lista']:
        rr = p['righe']
        if len(rr) < 4:
            continue

        def q(x):
            si = tot = 0
            for i in range(2, len(x)):
                sopra = x[i - 1] + x[i - 2]
                for w in x[i]:
                    tot += 1
                    si += any(simile(w, y) for y in sopra)
            return si, tot
        si, tot = q(rr)
        nul = statistics.mean(q(rnd.sample(rr, len(rr)))[0] for _ in range(200))
        dati.append((p['strato'], p['mano'], si, tot, nul))

    def E(ds):
        t = sum(d[3] for d in ds)
        return (sum(d[2] for d in ds) - sum(d[4] for d in ds)) / t if t else None
    tutto = E(dati)
    out = OrderedDict()
    for chiave, j in (('strato', 0), ('mano', 1)):
        gruppi = defaultdict(list)
        for d in dati:
            gruppi[d[j]].append(d)
        for g, ds in sorted(gruppi.items(), key=str):
            if sum(d[3] for d in ds) < 1500:
                continue
            boot = sorted(E([ds[rnd.randrange(len(ds))] for _ in ds]) for _ in range(500))
            ic = [boot[12], boot[487]]
            out['%s %s' % (chiave, g)] = OrderedDict([('paragrafi', len(ds)), ('parole', sum(d[3] for d in ds)), ('E', E(ds)), ('IC95', ic),
                                                      ('diverso_dalla_media', not (ic[0] <= tutto <= ic[1]))])
    diversi = [k for k, v in out.items() if v['diverso_dalla_media']]
    return OrderedDict([('E_complessivo', tutto), ('gruppi', out), ('esito', ('gruppi diversi dalla media: ' + ', '.join(diversi)) if diversi else 'ripresa uniforme')])


def main():
    rnd = random.Random(347)
    lista = paragrafi()
    pars = [p['righe'] for p in lista]
    r347v = e347(pars, rnd)
    print('e347 Voynich', {L: (round(v['esatta']['eccesso'], 4), round(v['esatta']['z'], 1), round(v['modificata']['eccesso'], 4), round(v['modificata']['z'], 1)) for L, v in r347v.items()}, flush=True)
    r347t = OrderedDict()
    for s in (1, 19):
        r347t[s] = e347(e337.pagine_ts(s), rnd)
        print('e347 TS', s, {L: (round(v['esatta']['eccesso'], 4), round(v['esatta']['z'], 1), round(v['modificata']['eccesso'], 4), round(v['modificata']['z'], 1)) for L, v in r347t[s].items()}, flush=True)
    r349 = e349({'lista': lista}, random.Random(349))
    print('e349', r349['esito'], round(r349['E_complessivo'], 4), flush=True)
    r348 = e348(pars, random.Random(348))
    print('e348', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r348.items()}, flush=True)

    def fin_dove(r, nome):
        ok = [L for L, v in r.items() if v[nome]['z'] > 3]
        return max(ok) if ok else 0
    sint = OrderedDict([('Voynich', {n: fin_dove(r347v, n) for n in ('esatta', 'modificata')})] + [('Timm e Schinner, seme %d' % s, {n: fin_dove(r347t[s], n) for n in ('esatta', 'modificata')}) for s in r347t])
    json.dump(OrderedDict([('e347', OrderedDict([('Voynich', r347v), ('Timm e Schinner', r347t), ('fin_dove', sint)])), ('e348', r348), ('e349', r349)]),
              open(os.path.join(RISULTATI, 'e347_ripresa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e347, e348, e349 — Fin dove guarda indietro lo scriba; parole uniche; ripresa per sezione e mano', '', 'Preregistrazione: `preregistrazioni/e347.md`.', '',
          '## e347 — eccesso di ripresa dalla riga a distanza L (z)', '', '| L | Voynich esatta | Voynich modificata | T&S 1 esatta | T&S 1 modificata | T&S 19 esatta | T&S 19 modificata |', '|---|---|---|---|---|---|---|']
    for L in r347v:
        cel = [r347v[L]] + [r347t[s].get(L) for s in r347t]
        md.append('| %d | %s |' % (L, ' | '.join('%+.4f (%.1f) | %+.4f (%.1f)' % (c['esatta']['eccesso'], c['esatta']['z'], c['modificata']['eccesso'], c['modificata']['z']) if c else '– | –' for c in cel)))
    md += ['', 'Fin dove (ultima distanza con z > 3): %s.' % '; '.join('%s: esatta %d, modificata %d' % (k, v['esatta'], v['modificata']) for k, v in sint.items()), '',
           '## e348', '', 'Parole uniche %d. Eccesso di fonte modificata nelle 2 righe sopra: uniche %+.4f, altre della stessa lunghezza %+.4f; differenza z %.1f: **%s**.' % (
               r348['unici'], r348['eccesso_unici'], r348['eccesso_altri_stessa_lunghezza'], r348['z'], r348['esito']),
           'Frequenza mediana delle fonti: delle uniche %s, delle altre %s.' % (r348['frequenza_mediana_fonti_unici'], r348['frequenza_mediana_fonti_altri']), '',
           '## e349 — E1p complessivo %+.4f' % r349['E_complessivo'], '', '| gruppo | paragrafi | parole | E1p | IC 95% | diverso dalla media |', '|---|---|---|---|---|---|']
    for k, v in r349['gruppi'].items():
        md.append('| %s | %d | %d | %+.4f | %+.4f – %+.4f | %s |' % (k, v['paragrafi'], v['parole'], v['E'], v['IC95'][0], v['IC95'][1], 'sì' if v['diverso_dalla_media'] else 'no'))
    md += ['', 'Esito e349: **%s**.' % r349['esito']]
    open(os.path.join(RISULTATI, 'e347_ripresa.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
