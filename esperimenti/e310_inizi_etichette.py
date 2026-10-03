# -*- coding: utf-8 -*-
"""Esperimenti 310 e 311. (e310) le parole d'inizio paragrafo: un gallows aggiunto a una parola normale, o parole nuove?
(e311) le etichette ricompaiono nel testo della propria pagina?

Preregistrazione: preregistrazioni/e310.md. Scrive risultati/e310_inizi_etichette.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
RICAMPIONI, PERM = 1000, 1000


def dist1(a, b):
    """Vero se le tuple di segni a e b sono a una modifica (sostituzione, inserimento, cancellazione) di distanza."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def e310(righe, rnd):
    freq = Counter(w for _, _, ws in righe for w in ws)
    nota = lambda s: freq.get(s, 0) >= 2
    gruppi = {'a': [], 'b': [], 'c': []}
    for _, ini, ws in righe:
        if not ws:
            continue
        gruppi['a' if ini else 'b'].append(ws[0])
        gruppi['c'] += ws[1:-1]

    def togli(w, pos):
        u = D(w)
        if len(u) < 2:
            return None
        i = {'primo': 0, 'secondo': 1, 'ultimo': len(u) - 1}[pos]
        return ''.join(u[:i] + u[i + 1:])

    def misure_gruppo(ws):
        uniche = [w for w in ws if freq[w] == 1]
        gall = lambda w: D(w)[0] in GALLOWS
        gn = lambda w: gall(w) and nota(togli(w, 'primo') or '')
        out = OrderedDict([('parole', len(ws)), ('quota_uniche', len(uniche) / len(ws)), ('quota_gallows_iniziale', sum(map(gall, ws)) / len(ws)),
                           ('quota_gallows_piu_parola_nota', sum(map(gn, ws)) / len(ws)), ('uniche', len(uniche)),
                           ('uniche_gallows_iniziale', sum(map(gall, uniche)) / len(uniche) if uniche else 0.0),
                           ('uniche_gallows_piu_parola_nota', sum(map(gn, uniche)) / len(uniche) if uniche else 0.0)])
        ug = [w for w in uniche if gall(w)]
        out['fra_uniche_con_gallows_resto_noto'] = sum(nota(togli(w, 'primo') or '') for w in ug) / len(ug) if ug else 0.0
        for pos in ('primo', 'secondo', 'ultimo'):
            out['uniche_togliendo_%s_parola_nota' % pos] = sum(nota(togli(w, pos) or '') for w in uniche) / len(uniche) if uniche else 0.0
        return out, uniche
    ris = OrderedDict()
    un = {}
    for g, ws in gruppi.items():
        ris[g], un[g] = misure_gruppo(ws)
    # (a) contro (c) fra le uniche, a pari lunghezza
    gn = lambda w: D(w)[0] in GALLOWS and nota(togli(w, 'primo') or '')
    per_L = defaultdict(list)
    for w in un['c']:
        per_L[len(D(w))].append(w)
    vero = ris['a']['uniche_gallows_piu_parola_nota']
    nulli = []
    for _ in range(RICAMPIONI):
        camp = []
        for w in un['a']:
            L = len(D(w))
            pool = per_L.get(L) or per_L.get(L - 1) or per_L.get(L + 1) or un['c']
            camp.append(rnd.choice(pool))
        nulli.append(sum(map(gn, camp)) / len(camp))
    sd = statistics.pstdev(nulli)
    z = (vero - statistics.mean(nulli)) / sd if sd else 0.0
    esito = 'prefisso meccanico' if (z > 3 and vero >= 0.30) else ('parole nuove' if z < 2 else 'incerto')
    resto_nuovo = 1 - ris['a']['uniche_togliendo_primo_parola_nota']
    esempi = [(w, togli(w, 'primo')) for w in un['a'] if gn(w)][:20]
    return OrderedDict([('gruppi', ris), ('a_contro_c', OrderedDict([('a', vero), ('c_a_pari_lunghezza', statistics.mean(nulli)), ('z', z)])),
                        ('esito', esito), ('uniche_di_a_che_restano_nuove', resto_nuovo), ('esempi', esempi)])


def e311(rnd):
    R = trascrizione.leggi('ZL')
    testo, etich, sez = defaultdict(list), defaultdict(list), {}
    for r in R:
        if not r.parole:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        sez.setdefault(r.pagina, r.sezione or '?')
        if r.tipo[0] == trascrizione.PARAGRAFO:
            testo[r.pagina] += ws
        elif r.tipo[0] == 'L':
            etich[r.pagina] += ws
    pagine = [p for p in etich if len(etich[p]) >= 3 and len(testo[p]) >= 30]
    tipi = {p: set(testo[p]) for p in pagine}
    per_len = {p: defaultdict(list) for p in pagine}
    for p in pagine:
        for w in tipi[p]:
            per_len[p][len(D(w))].append(tuple(D(w)))

    def quota(assegna, etichette):
        es = vi = tot = 0
        for p in pagine:
            q = assegna[p]
            for w in etichette[p]:
                tot += 1
                if w in tipi[q]:
                    es += 1
                    vi += 1
                else:
                    u = tuple(D(w))
                    if any(dist1(u, x) for L in (len(u) - 1, len(u), len(u) + 1) for x in per_len[q].get(L, ())):
                        vi += 1
        return es / tot, vi / tot
    ident = {p: p for p in pagine}
    vero = quota(ident, etich)
    blocchi = []
    per_sez = defaultdict(list)
    for p in pagine:
        per_sez[sez[p]].append(p)
    for s, ps in per_sez.items():
        ps = sorted(ps, key=lambda p: len(testo[p]))
        for i in range(0, len(ps), 5):
            blocchi.append(ps[i:i + 5])
    nulli = []
    for _ in range(PERM):
        a = {}
        for b in blocchi:
            x = list(b)
            rnd.shuffle(x)
            a.update(zip(b, x))
        nulli.append(quota(a, etich))
    z = [(vero[k] - statistics.mean(n[k] for n in nulli)) / (statistics.pstdev(n[k] for n in nulli) or 1) for k in (0, 1)]
    pos = {p: [rnd.choice(testo[p]) for _ in etich[p]] for p in pagine}
    vp = quota(ident, pos)
    nulli_p = []
    for _ in range(200):
        a = {}
        for b in blocchi:
            x = list(b)
            rnd.shuffle(x)
            a.update(zip(b, x))
        nulli_p.append(quota(a, pos)[0])
    zp = (vp[0] - statistics.mean(nulli_p)) / (statistics.pstdev(nulli_p) or 1)
    sezioni = OrderedDict()
    for s, ps in sorted(per_sez.items(), key=str):
        tot = sum(len(etich[p]) for p in ps)
        es = sum(w in tipi[p] for p in ps for w in etich[p])
        sezioni[s] = OrderedDict([('pagine', len(ps)), ('etichette', tot), ('nel_proprio_testo', es / tot if tot else 0.0)])
    ricorrenti = [(p, w) for p in pagine for w in etich[p] if w in tipi[p]][:40]
    esito = 'etichette legate al testo della pagina' if z[0] > 3 else ('nessun legame' if z[0] < 2 and z[1] < 2 else 'incerto')
    return OrderedDict([('pagine', len(pagine)), ('etichette', sum(len(etich[p]) for p in pagine)), ('esatte', vero[0]), ('a_una_modifica', vero[1]),
                        ('nullo_esatte', statistics.mean(n[0] for n in nulli)), ('nullo_a_una_modifica', statistics.mean(n[1] for n in nulli)),
                        ('z_esatte', z[0]), ('z_a_una_modifica', z[1]), ('controllo_positivo', OrderedDict([('quota', vp[0]), ('z', zp)])),
                        ('per_sezione', sezioni), ('esito', esito), ('ricorrenti', ricorrenti)])


def main():
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append((r.pagina, bool(r.inizio_par), ws))
    r310 = e310(righe, random.Random(310))
    print('e310', r310['esito'], r310['a_contro_c'], flush=True)
    for g, x in r310['gruppi'].items():
        print('  ', g, {k: round(v, 3) if isinstance(v, float) else v for k, v in x.items()}, flush=True)
    r311 = e311(random.Random(311))
    print('e311', r311['esito'], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r311.items() if k not in ('per_sezione', 'ricorrenti', 'controllo_positivo')},
          r311['controllo_positivo'], flush=True)
    json.dump(OrderedDict([('e310', r310), ('e311', r311)]), open(os.path.join(RISULTATI, 'e310_inizi_etichette.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    nomi = {'a': '(a) prime parole dei paragrafi', 'b': '(b) prime parole delle altre righe', 'c': '(c) parole in mezzo alla riga'}
    chiavi = list(r310['gruppi']['a'])
    md = ['# e310, e311 — Parole d\'inizio paragrafo; etichette e testo', '', 'Preregistrazione: `preregistrazioni/e310.md` (con la correzione del controllo).', '',
          '## e310', '', '| misura | ' + ' | '.join(nomi[g] for g in 'abc') + ' |', '|---|---|---|---|']
    for k in chiavi:
        md.append('| %s | %s |' % (k.replace('_', ' '), ' | '.join(('%.3f' % r310['gruppi'][g][k]) if isinstance(r310['gruppi'][g][k], float) else str(r310['gruppi'][g][k]) for g in 'abc')))
    x = r310['a_contro_c']
    md += ['', 'Fra le parole uniche: "gallows + parola nota" in (a) %.3f contro %.3f in (c) a pari lunghezza, z %.1f. Esito e310: **%s**.' % (x['a'], x['c_a_pari_lunghezza'], x['z'], r310['esito']),
           'Parole uniche di (a) che restano nuove togliendo il primo segno: %.0f%%.' % (100 * r310['uniche_di_a_che_restano_nuove']),
           'Esempi: %s.' % ', '.join('%s → %s' % e for e in r310['esempi'][:12]), '', '## e311', '',
           '%d pagine, %d parole d\'etichetta. Nel testo della propria pagina: esatte %.3f (nullo %.3f, z %.1f); a una modifica %.3f (nullo %.3f, z %.1f). Controllo positivo: %.3f, z %.1f.' % (
               r311['pagine'], r311['etichette'], r311['esatte'], r311['nullo_esatte'], r311['z_esatte'], r311['a_una_modifica'], r311['nullo_a_una_modifica'], r311['z_a_una_modifica'],
               r311['controllo_positivo']['quota'], r311['controllo_positivo']['z']), '', 'Per sezione: %s.' % '; '.join('%s: %d pagine, %d etichette, %.2f nel proprio testo' % (
                   s, v['pagine'], v['etichette'], v['nel_proprio_testo']) for s, v in r311['per_sezione'].items()), '', 'Esito e311: **%s**.' % r311['esito'], '',
           'Etichette presenti nel testo della propria pagina (prime 40): %s.' % ', '.join('%s %s' % pw for pw in r311['ricorrenti'])]
    open(os.path.join(RISULTATI, 'e310_inizi_etichette.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
