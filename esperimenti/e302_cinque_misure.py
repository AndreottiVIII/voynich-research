# -*- coding: utf-8 -*-
"""Esperimenti 302-306: cinque misure sul Voynich e sul corpo della v5 del voynichizzatore (semi 1, 2, 3).
e302 registro delle prime righe; e303 somiglianza fra righe e distanza; e304 errori ricorrenti; e305 coppie identiche;
e306 lunghezze delle parole per posizione nella riga.

Preregistrazione: preregistrazioni/e302.md. Scrive risultati/e302_cinque_misure.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEMI = (1, 2, 3)
PERM = 1000
DISTANZE = [0, 1, 2, 3, 4, 6, 8, 12, 16]
INIZIALI = ('q', 'o', 'ch', 'sh', 'd', 's', 'y', 'a', 'l', 'k', 't', 'p', 'f', 'c-gallows')
FINALI = ('y', 'n', 'l', 'r', 'm', 's', 'o', 'e')
GALLI = {'p': ('p', 'cph'), 'f': ('f', 'cfh'), 'k': ('k', 'ckh'), 't': ('t', 'cth')}


def pulito(rr):
    out = []
    for p, ini, ps in rr:
        ws = [w for w in ps if trascrizione.pulita(w)]
        if ws:
            out.append((p, bool(ini), ws))
    return out


def testo(nome):
    if nome == 'Voynich':
        import e293_banco as e293
        return pulito(e293.voynich_rr())
    import versioni
    return pulito(versioni.corpo(versioni.V5, int(nome.split()[-1])))


# ---------- e302 ----------

def caratteristiche_riga(ws):
    u = [D(w) for w in ws]
    n = len(u)
    f = OrderedDict()
    f['lunghezza media'] = statistics.mean(len(x) for x in u)
    for g in INIZIALI:
        if g == 'c-gallows':
            f['inizia con %s' % g] = sum(x[0] in ('ckh', 'cth', 'cph', 'cfh') for x in u) / n
        else:
            f['inizia con %s' % g] = sum(x[0] == g for x in u) / n
    for g in FINALI:
        f['finisce in %s' % g] = sum(x[-1] == g for x in u) / n
    tot = sum(len(x) for x in u)
    for g, gg in GALLI.items():
        f['segno %s' % g] = sum(s in gg for x in u for s in x) / tot
    return f, n, tot


def e302(rr, rnd):
    per_pag = defaultdict(list)
    for p, ini, ws in rr:
        f, n, tot = caratteristiche_riga(ws)
        per_pag[p].append((ini, f, n, tot))
    righe = [x for v in per_pag.values() for x in v]
    nomi = list(righe[0][1])

    def diff(etich):
        out = {}
        for k in nomi:
            peso = (lambda r: r[3]) if k.startswith('segno') else (lambda r: r[2])
            a = [(r[1][k], peso(r)) for r, e in zip(righe, etich) if e]
            b = [(r[1][k], peso(r)) for r, e in zip(righe, etich) if not e]
            ma = sum(v * w for v, w in a) / sum(w for _, w in a) if a else 0.0
            mb = sum(v * w for v, w in b) / sum(w for _, w in b) if b else 0.0
            out[k] = ma - mb
        return out
    vero = diff([r[0] for r in righe])
    nulli = defaultdict(list)
    for _ in range(PERM):
        et = []
        for v in per_pag.values():
            x = [r[0] for r in v]
            rnd.shuffle(x)
            et += x
        for k, d in diff(et).items():
            nulli[k].append(d)
    out = OrderedDict()
    for k in nomi:
        sd = statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('differenza', vero[k]), ('z', (vero[k] - statistics.mean(nulli[k])) / sd if sd else 0.0)])
    return out


# ---------- e303 ----------

def e303(rr):
    pagine = OrderedDict()
    for p, _, ws in rr:
        pagine.setdefault(p, []).append(ws)
    dec = misure.decadimento(list(pagine.values()), D, coppie_caso=100000, distanze=DISTANZE)
    return OrderedDict((d, OrderedDict([('somiglianza', 1 - dec[d]['distanza']), ('identiche', dec[d]['identiche'])])) for d in DISTANZE)


# ---------- e304 ----------

def dist1(a, b):
    import e296_rare_errori as e296
    return e296.dist1(a, b)


def e304(rr, rnd):
    import e230_generatore_meccanismi as e230
    sez = e230.sezioni()
    ordine = {}
    for p, _, _ in rr:
        ordine.setdefault(p, len(ordine))
    cnt = Counter(w for _, _, ws in rr for w in ws)
    frequenti = [w for w, n in cnt.items() if n >= 20]
    per_l = defaultdict(list)
    for w in frequenti:
        per_l[len(D(w))].append(w)
    pagine_di = defaultdict(list)
    for p, _, ws in rr:
        for w in ws:
            if 2 <= cnt[w] <= 5:
                pagine_di[w].append(p)
    varianti, madre = [], {}
    for w in pagine_di:
        u = tuple(D(w))
        for L in (len(u) - 1, len(u), len(u) + 1):
            m = next((f for f in per_l.get(L, ()) if dist1(u, tuple(D(f)))), None)
            if m:
                varianti.append(w)
                madre[w] = m
                break
    pag_sez = defaultdict(list)
    for p in ordine:
        pag_sez[sez.get(p)].append(p)

    def media_dist(gruppi):
        ds, vicine = [], 0
        for ps in gruppi:
            pp = sorted(set(ordine[p] for p in ps))
            if len(pp) >= 2:
                dd = [b - a for i, a in enumerate(pp) for b in pp[i + 1:]]
                ds.append(statistics.mean(dd))
                vicine += min(b - a for a, b in zip(pp, pp[1:])) <= 3
        return (statistics.mean(ds) if ds else 0.0), len(ds), vicine
    vero, n_multi, vicine = media_dist([pagine_di[w] for w in varianti])
    nulli = []
    for _ in range(200):
        gr = []
        for w in varianti:
            gr.append([rnd.choice(pag_sez[sez.get(p)]) for p in pagine_di[w]])
        nulli.append(media_dist(gr)[0])
    sd = statistics.pstdev(nulli)
    per_madre = defaultdict(list)
    for w in varianti:
        per_madre[madre[w]].append(cnt[w])
    conc = statistics.mean(sum(v) / len(v) for v in per_madre.values()) if per_madre else 0.0
    return OrderedDict([('varianti_rare', len(varianti)), ('in_piu_pagine', n_multi), ('quota_con_occorrenze_entro_3_pagine', vicine / n_multi if n_multi else 0.0),
                        ('distanza_media', vero), ('nullo', statistics.mean(nulli)), ('z', (vero - statistics.mean(nulli)) / sd if sd else 0.0),
                        ('occorrenze_per_variante', conc)])


# ---------- e305 ----------

def e305(rr):
    import e230_generatore_meccanismi as e230
    sez = e230.sezioni()
    cnt = Counter(w for _, _, ws in rr for w in ws)
    coppie, ident, pos, per_sez, tot_sez, frequenti = 0, Counter(), Counter(), Counter(), Counter(), 0
    for p, _, ws in rr:
        n = len(ws)
        for i, (a, b) in enumerate(zip(ws, ws[1:])):
            coppie += 1
            tot_sez[sez.get(p)] += 1
            if a == b:
                ident[a] += 1
                pos['inizio' if i == 0 else ('fine' if i == n - 2 else 'centro')] += 1
                per_sez[sez.get(p)] += 1
                frequenti += cnt[a] >= 50
    k = sum(ident.values())
    return OrderedDict([('quota', k / coppie), ('piu_ripetute', ident.most_common(10)),
                        ('posizione', OrderedDict((x, pos[x] / k if k else 0.0) for x in ('inizio', 'centro', 'fine'))),
                        ('per_sezione', OrderedDict((s, per_sez[s] / tot_sez[s]) for s in sorted(tot_sez, key=str) if tot_sez[s] >= 500)),
                        ('quota_di_parole_frequenti', frequenti / k if k else 0.0)])


# ---------- e306 ----------

def e306(rr):
    pos = defaultdict(list)
    for _, ini, ws in rr:
        L = [len(D(w)) for w in ws]
        n = len(L)
        tipo = 'prime' if ini else 'altre'
        if n >= 1:
            pos[(tipo, 'prima')].append(L[0])
            pos[(tipo, 'ultima')].append(L[-1])
        if n >= 3:
            pos[(tipo, 'seconda')].append(L[1])
            pos[(tipo, 'mediana')].append(L[n // 2])
            pos[(tipo, 'penultima')].append(L[-2])
    out = OrderedDict()
    for (tipo, p), v in sorted(pos.items()):
        out['%s riga, %s parola' % (tipo, p)] = OrderedDict([('media', statistics.mean(v)), ('dev', statistics.pstdev(v))])
    tutte = Counter(min(len(D(w)), 10) for _, _, ws in rr for w in ws)
    n = sum(tutte.values())
    out['distribuzione'] = OrderedDict((L, tutte[L] / n) for L in range(1, 11))
    return out


def lavoro(nome):
    rr = testo(nome)
    rnd = random.Random(302)
    return nome, OrderedDict([('e302', e302(rr, rnd)), ('e303', e303(rr)), ('e304', e304(rr, random.Random(304))), ('e305', e305(rr)), ('e306', e306(rr))])


def piatti(d, pref=''):
    """{'chiave/sottochiave': numero} per i valori numerici di un dizionario annidato."""
    out = OrderedDict()
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(piatti(v, '%s%s / ' % (pref, k)))
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            out['%s%s' % (pref, k)] = v
    return out


def manca(voy, gen, lunghezza=False):
    lo, hi, m = min(gen), max(gen), statistics.mean(gen)
    soglia = 0.1 if lunghezza else 0.10 * abs(voy)
    return not (lo <= voy <= hi) and abs(voy - m) > soglia


def main():
    nomi = ['Voynich'] + ['v5 seme %d' % s for s in SEMI]
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        ris = OrderedDict(pool.map(lavoro, nomi))
    gen = nomi[1:]
    V = ris['Voynich']
    esiti = OrderedDict()
    # e302
    el = []
    for k, x in V['e302'].items():
        if abs(x['z']) > 3:
            g = [ris[n]['e302'][k]['differenza'] for n in gen]
            m = statistics.mean(g)
            el.append(OrderedDict([('caratteristica', k), ('Voynich', x['differenza']), ('z', x['z']), ('generatore', m),
                                   ('manca', (m * x['differenza'] < 0) or abs(m) < abs(x['differenza']) / 2)]))
    esiti['e302'] = el
    # e303
    rel = lambda r, d: r['e303'][d]['somiglianza'] / r['e303'][1]['somiglianza'] if r['e303'][1]['somiglianza'] else 0.0
    curva = OrderedDict()
    for d in DISTANZE:
        g = [rel(ris[n], d) for n in gen]
        curva[d] = OrderedDict([('Voynich', rel(V, d)), ('generatore', statistics.mean(g)), ('manca', d >= 2 and manca(rel(V, d), g))])
    meta = next((d for d in DISTANZE if d >= 2 and rel(V, d) < 0.5), 'mai entro 16')
    esiti['e303'] = OrderedDict([('curva_relativa', curva), ('meta_Voynich', meta)])
    # e304
    zv = V['e304']['z']
    esiti['e304'] = OrderedDict([('esito', 'errori ricorrenti vicini' if zv < -3 else ('sparsi' if abs(zv) < 2 else 'incerto')),
                                 ('z', zv), ('occorrenze_per_variante_Voynich', V['e304']['occorrenze_per_variante']),
                                 ('occorrenze_per_variante_generatore', statistics.mean(ris[n]['e304']['occorrenze_per_variante'] for n in gen))])
    # e305, e306: confronto di tutti i valori numerici
    for e in ('e305', 'e306'):
        pv = piatti(V[e])
        pg = [piatti(ris[n][e]) for n in gen]
        esiti[e] = OrderedDict((k, OrderedDict([('Voynich', v), ('generatore', statistics.mean(p.get(k, 0.0) for p in pg))]))
                               for k, v in pv.items() if manca(v, [p.get(k, 0.0) for p in pg], lunghezza=(e == 'e306' and 'media' in k)))
    json.dump(OrderedDict([('risultati', ris), ('esiti', esiti)]), open(os.path.join(RISULTATI, 'e302_cinque_misure.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=str)
    md = ['# e302–e306 — Cinque misure sul Voynich e sul corpo della v5 (semi 1–3)', '', 'Preregistrazione: `preregistrazioni/e302.md`.', '',
          '## e302 — Registro delle prime righe (prime − altre, |z| > 3 nel Voynich)', '', '| caratteristica | Voynich | z | generatore | manca |', '|---|---|---|---|---|']
    for x in esiti['e302']:
        md.append('| %s | %+.4f | %.1f | %+.4f | %s |' % (x['caratteristica'], x['Voynich'], x['z'], x['generatore'], 'sì' if x['manca'] else 'no'))
    md += ['', '## e303 — Somiglianza fra righe rispetto alla distanza 1', '', '| distanza | Voynich | generatore | manca |', '|---|---|---|---|']
    for d, x in esiti['e303']['curva_relativa'].items():
        md.append('| %d | %.3f | %.3f | %s |' % (d, x['Voynich'], x['generatore'], 'sì' if x['manca'] else 'no'))
    md += ['', 'Distanza alla quale il Voynich scende sotto metà: %s.' % esiti['e303']['meta_Voynich'], '',
           '## e304 — Errori ricorrenti', '']
    for n in nomi:
        x = ris[n]['e304']
        md.append('- %s: %d varianti rare, %d in più pagine, distanza media %.1f pagine (nullo %.1f, z %.1f), entro 3 pagine %.2f, occorrenze per variante %.2f.' % (
            n, x['varianti_rare'], x['in_piu_pagine'], x['distanza_media'], x['nullo'], x['z'], x['quota_con_occorrenze_entro_3_pagine'], x['occorrenze_per_variante']))
    md += ['', 'Esito e304: **%s**.' % esiti['e304']['esito'], '', '## e305 — Coppie identiche', '']
    for n in nomi:
        x = ris[n]['e305']
        md.append('- %s: quota %.4f; posizione %s; di parole frequenti %.2f; più ripetute %s.' % (
            n, x['quota'], {k: round(v, 2) for k, v in x['posizione'].items()}, x['quota_di_parole_frequenti'], ', '.join('%s %d' % kv for kv in x['piu_ripetute'][:6])))
    md += ['', 'Mancano al generatore: %s.' % ('; '.join('%s (Voynich %.4f, generatore %.4f)' % (k, v['Voynich'], v['generatore']) for k, v in esiti['e305'].items()) or 'nessuna'),
           '', '## e306 — Lunghezze per posizione', '', '| posizione | Voynich | generatore (media semi) |', '|---|---|---|']
    for k, x in V['e306'].items():
        if k != 'distribuzione':
            g = statistics.mean(ris[n]['e306'][k]['media'] for n in gen)
            md.append('| %s | %.2f ± %.2f | %.2f |' % (k, x['media'], x['dev'], g))
    md += ['', 'Mancano al generatore: %s.' % ('; '.join('%s (Voynich %.3f, generatore %.3f)' % (k, v['Voynich'], v['generatore']) for k, v in esiti['e306'].items()) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e302_cinque_misure.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
