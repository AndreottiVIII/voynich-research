# -*- coding: utf-8 -*-
"""Esperimento 132: la prima parola della riga (tolto il segno aggiunto) si comporta da nome? Unicita', concentrazione
nella pagina, presenza fra le etichette; contro parole interne appaiate per sezione e lunghezza.

Preregistrazione: preregistrazioni/e132.md. Scrive risultati/e132_prima_parola_lemma.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, ESTRAZIONI, MIN_PAROLE = 132, 1000, 4
D = misure.divisore(misure.GLIFI_EVA)
AGGIUNTI, GAMBE = {'y', 'd', 's', 'o'}, {'p', 't', 'k', 'f'}


def taglia(w, insieme):
    u = D(w)
    return ''.join(u[1:]) if len(u) >= 3 and u[0] in insieme else w


def gettoni(righe):
    """righe: (pagina, sezione, inizio paragrafo, parole) -> gruppi di (pagina, sezione, forma, lunghezza, contata),
    dove contata = 1 se la forma coincide con la parola scritta (quindi e' gia' nei conteggi del testo)."""
    g = defaultdict(list)
    for pag, sez, ini, ps in righe:
        if len(ps) < MIN_PAROLE or not all(trascrizione.pulita(w) for w in ps):
            continue
        t = lambda w, scritta: (pag, sez, w, len(D(w)), 1 if w == scritta else 0)
        if ini:
            g['G3 prime dei paragrafi (gamba tolta)'].append(t(taglia(ps[0], GAMBE), ps[0]))
        else:
            g['G1 prime delle righe (segno tolto)'].append(t(taglia(ps[0], AGGIUNTI), ps[0]))
            g['G1 prime delle righe (non tolto)'].append(t(ps[0], ps[0]))
            g['G2 seconde (placebo)'].append(t(ps[1], ps[1]))
        for k, w in enumerate(ps[2:-1]):
            g['interne'].append(t(w, w) + (k,))
    return g


def contesto(righe):
    tot = Counter()
    per_pag = defaultdict(Counter)
    for pag, _, _, ps in righe:
        for w in ps:
            tot[w] += 1
            per_pag[pag][w] += 1
    return tot, per_pag


def valori(tok, tot, per_pag, etichette, et_farm):
    pag, sez, w, _, contata = tok[:5]
    n = tot[w] - contata          # altre occorrenze nel testo
    v = {'M1a': 1.0 if n == 0 else 0.0}
    v['M1b'] = (per_pag[pag][w] - contata) / n if n >= 1 else None
    if etichette is not None:
        v['M2'] = 1.0 if w in etichette else 0.0
        v['M3'] = (1.0 if w in et_farm else 0.0) if sez == 'H' else None
    return v


def confronta(gruppo, interne, tot, per_pag, etichette, et_farm, rnd, misure_):
    per_chiave = defaultdict(list)
    for t in interne:
        per_chiave[(t[1], t[3])].append(t)
    appaiati = [t for t in gruppo if per_chiave[(t[1], t[3])]]
    vi = {t: valori(t, tot, per_pag, etichette, et_farm) for t in set(interne)}
    out = OrderedDict([('n', len(appaiati))])
    for m in misure_:
        reale = [valori(t, tot, per_pag, etichette, et_farm)[m] for t in appaiati]
        idx = [i for i, x in enumerate(reale) if x is not None]
        if not idx:
            continue
        r = statistics.mean(reale[i] for i in idx)
        nulli = []
        for _ in range(ESTRAZIONI):
            xs = []
            for i in idx:
                t = appaiati[i]
                cand = per_chiave[(t[1], t[3])]
                for _ in range(20):
                    x = vi[rnd.choice(cand)][m]
                    if x is not None:
                        xs.append(x)
                        break
            nulli.append(statistics.mean(xs) if xs else 0.0)
        mm, s = statistics.mean(nulli), statistics.pstdev(nulli)
        out[m] = OrderedDict([('reale', r), ('nullo', mm), ('eccesso', r - mm), ('z', (r - mm) / s if s else None), ('n', len(idx))])
    return out


def ts_righe(con_nomi, rnd):
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    out = []
    usate = {w for _, ps in rr for w in ps}
    segni = [g for g, _ in Counter(g for _, ps in rr for w in ps for g in D(w)).most_common(15)]
    nomi = {}
    for i, (ini, ps) in enumerate(rr):
        pag = i // 29
        if con_nomi and pag not in nomi:
            nomi[pag] = []
            while len(nomi[pag]) < 4:
                w = ''.join(rnd.choice(segni) for _ in range(rnd.randint(5, 7)))
                if w not in usate:
                    usate.add(w)
                    nomi[pag].append(w)
        ps = list(ps)
        if con_nomi and not ini and rnd.random() < 0.5:
            ps = [rnd.choice(nomi[pag])] + ps
        out.append((pag, None, ini, ps))
    return out


def main():
    zl = trascrizione.leggi('ZL')
    righe = [(r.pagina, r.sezione, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(zl) if r.parole]
    etichette = {w for r in zl if r.tipo and r.tipo[0] == 'L' for w in r.parole if trascrizione.pulita(w)}
    et_farm = {w for r in zl if r.tipo and r.tipo[0] == 'L' and r.sezione == 'P' for w in r.parole if trascrizione.pulita(w)}
    rnd = random.Random(SEME)
    ris = OrderedDict()
    tot, per_pag = contesto(righe)
    g = gettoni(righe)
    ris['Voynich'] = OrderedDict()
    for nome in ('G1 prime delle righe (segno tolto)', 'G1 prime delle righe (non tolto)', 'G2 seconde (placebo)', 'G3 prime dei paragrafi (gamba tolta)'):
        ris['Voynich'][nome] = confronta(g[nome], g['interne'], tot, per_pag, etichette, et_farm, rnd, ('M1a', 'M1b', 'M2', 'M3'))
    for etich, con in (('controllo positivo: Timm e Schinner con nomi', True), ('controllo negativo: Timm e Schinner', False)):
        rr = ts_righe(con, random.Random(SEME))
        tt, pp = contesto(rr)
        gg = gettoni(rr)
        ris[etich] = OrderedDict()
        for nome in ('G1 prime delle righe (non tolto)', 'G2 seconde (placebo)'):
            ris[etich][nome] = confronta(gg[nome], gg['interne'], tt, pp, None, None, rnd, ('M1a', 'M1b'))
    for testo, gruppi in ris.items():
        for nome, r in gruppi.items():
            print('%-46s %-38s n %5d | %s' % (testo, nome, r['n'], ' | '.join('%s %.3f vs %.3f (z %.1f)' % (m, r[m]['reale'], r[m]['nullo'], r[m]['z'] or 0)
                                                                         for m in ('M1a', 'M1b', 'M2', 'M3') if m in r)), flush=True)
    z = lambda t, n, m: (ris[t][n].get(m) or {}).get('z') or 0
    pos, neg = 'controllo positivo: Timm e Schinner con nomi', 'controllo negativo: Timm e Schinner'
    G1p = 'G1 prime delle righe (non tolto)'
    valido = max(z(pos, G1p, 'M1a'), z(pos, G1p, 'M1b')) > 4 and max(z(neg, G1p, 'M1a'), z(neg, G1p, 'M1b')) < 2
    G1, G2, G3 = 'G1 prime delle righe (segno tolto)', 'G2 seconde (placebo)', 'G3 prime dei paragrafi (gamba tolta)'
    lemmi = any(z('Voynich', G1, m) > 4 and z('Voynich', G2, m) < 2 for m in ('M1a', 'M1b'))
    titoli = any(z('Voynich', G3, m) > 4 and z('Voynich', G2, m) < 2 for m in ('M1a', 'M1b'))
    ris['esiti'] = OrderedDict([('valido', valido), ('prime_come_lemmi', lemmi), ('titoli', titoli)])
    print('valido %s | prime parole come lemmi %s | titoli dei paragrafi %s' % (valido, lemmi, titoli))
    with open(os.path.join(RISULTATI, 'e132_prima_parola_lemma.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e132 — La prima parola della riga è un lemma?', '',
           'Gruppi contro parole interne appaiate per sezione e lunghezza (%d estrazioni). M1a: forma unica; M1b: altre occorrenze sulla stessa pagina; '
           'M2: fra le etichette; M3: titoli d\'erbario fra le etichette della farmaceutica. Preregistrazione: `preregistrazioni/e132.md`.' % ESTRAZIONI, '',
           '| testo | gruppo | n | M1a (z) | M1b (z) | M2 (z) | M3 (z) |', '|---|---|---|---|---|---|---|']
    for testo, gruppi in ris.items():
        if testo == 'esiti':
            continue
        for nome, r in gruppi.items():
            cella = lambda m: '%.3f vs %.3f (%.1f)' % (r[m]['reale'], r[m]['nullo'], r[m]['z'] or 0) if m in r else '–'
            out.append('| %s | %s | %d | %s | %s | %s | %s |' % (testo, nome, r['n'], cella('M1a'), cella('M1b'), cella('M2'), cella('M3')))
    out += ['', 'Controllo valido: **%s**. Prime parole come lemmi: **%s**. Titoli dei paragrafi: **%s**.' % (
        'sì' if valido else 'no', 'sì' if lemmi else 'no', 'sì' if titoli else 'no')]
    with open(os.path.join(RISULTATI, 'e132_prima_parola_lemma.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
