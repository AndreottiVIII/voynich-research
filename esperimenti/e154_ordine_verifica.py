# -*- coding: utf-8 -*-
"""Esperimento 154: l'ordine dei bifogli ricostruito dal vocabolario rende piu' graduali caratteristiche indipendenti
(preferenze di grafia per riga, impaginazione)?

Preregistrazione: preregistrazioni/e154.md. Scrive risultati/e154_ordine_verifica.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e135_stato_riga as e135
import e148_bifogli as e148
import e150_ordine_scrittura as e150

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, CASUALI, MINIMO = 154, 1000, 6
D = misure.divisore(misure.GLIFI_EVA)
SCELTE = (0, 1, 2, 4, 6)


def caratteristiche(U):
    """Per unita': grafia (5 residui) e impaginazione (4 valori), dalle righe di paragrafo dei fogli dell'unita'."""
    fogli_di = {n: [int(x[1:]) for x in n.split('-')] for n in U}
    righe_par = defaultdict(list)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        f = e148.foglio(r.pagina)
        if r.parole:
            righe_par[f].append((bool(r.inizio_par), list(r.parole)))
    graf, imp = {}, {}
    tutte, chi = [], []
    for n, ff in fogli_di.items():
        for f in ff:
            for _, ps in righe_par[f]:
                tutte.append(('x', ps))
                chi.append(n)
    occ = [o for o in e135.occorrenze(tutte) if o[0] in SCELTE]
    quota = defaultdict(lambda: [0, 0])
    for f, r, st, v in occ:
        quota[(f, st[1:])][0] += v
        quota[(f, st[1:])][1] += 1
    acc = defaultdict(list)
    for f, r, st, v in occ:
        a, m = quota[(f, st[1:])]
        acc[(chi[r], f)].append(v - a / m)
    for n, ff in fogli_di.items():
        graf[n] = [statistics.mean(acc[(n, f)]) if acc[(n, f)] else 0.0 for f in SCELTE]
        rr = [x for f in ff for x in righe_par[f]]
        if not rr:
            imp[n] = None
            continue
        npar = max(1, sum(ini for ini, _ in rr))
        iniziali = [ps[0] for ini, ps in rr if ini and ps]
        imp[n] = [statistics.mean(len(ps) for _, ps in rr), statistics.mean(sum(len(D(w)) for w in ps) for _, ps in rr),
                  len(rr) / npar, sum(1 for w in iniziali if D(w)[0] in ('p', 'f')) / max(1, len(iniziali))]
    return graf, imp


def standardizza(vv):
    k = len(next(iter(vv.values())))
    out = {n: list(v) for n, v in vv.items()}
    for j in range(k):
        col = [v[j] for v in vv.values()]
        m, s = statistics.mean(col), statistics.pstdev(col) or 1.0
        for n in out:
            out[n][j] = (vv[n][j] - m) / s
    return out


def distanza(ordine, X):
    return statistics.mean(math.dist(X[a], X[b]) for a, b in zip(ordine, ordine[1:]))


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    graf, imp = caratteristiche(U)
    gruppi = defaultdict(list)
    for n, u in U.items():
        if imp.get(n) is not None:
            gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = OrderedDict((k, v) for k, v in sorted(gruppi.items(), key=lambda kv: -len(kv[1])) if len(v) >= MINIMO)
    ris = OrderedDict([('gruppi', {('mano %s, lingua %s' % k): len(v) for k, v in gruppi.items()})])
    for nome_c, C in (('(I) grafia', graf), ('(II) impaginazione', imp)):
        tot = {'ricostruito': 0.0, 'rilegatura': 0.0}
        pesi = 0
        casuali = [0.0] * CASUALI
        dettaglio = OrderedDict()
        for k, nomi in gruppi.items():
            X = standardizza({n: C[n] for n in nomi})
            vett = {n: Counter(w for ps in U[n]['righe'] for w in ps) for n in nomi}
            S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
            ric = [nomi[i] for i in e150.ricostruisci(S)]
            ril = sorted(nomi, key=lambda n: U[n]['primo'])
            w = len(nomi) - 1
            dr, dl = distanza(ric, X), distanza(ril, X)
            tot['ricostruito'] += w * dr
            tot['rilegatura'] += w * dl
            pesi += w
            for i in range(CASUALI):
                o = nomi[:]
                rnd.shuffle(o)
                casuali[i] += w * distanza(o, X)
            dettaglio['mano %s, lingua %s' % k] = OrderedDict([('ricostruito', dr), ('rilegatura', dl)])
        r_ric, r_ril = tot['ricostruito'] / pesi, tot['rilegatura'] / pesi
        cas = [x / pesi for x in casuali]
        p = sum(x <= r_ric for x in cas) / CASUALI
        ris[nome_c] = OrderedDict([('ricostruito', r_ric), ('rilegatura', r_ril), ('casuali_media', statistics.mean(cas)), ('p', p), ('per_gruppo', dettaglio)])
        print('%-20s ricostruito %.3f | rilegatura %.3f | casuali %.3f | p %.3f | %s' % (nome_c, r_ric, r_ril, statistics.mean(cas), p,
                                                                                    ' '.join('%s %.2f/%.2f' % (g, x['ricostruito'], x['rilegatura']) for g, x in dettaglio.items())), flush=True)
    conferma = any(ris[c]['ricostruito'] < ris[c]['rilegatura'] and ris[c]['p'] < 0.05 for c in ('(I) grafia', '(II) impaginazione'))
    ris['ordine_confermato'] = conferma
    print('ordine confermato da dati indipendenti:', conferma)
    with open(os.path.join(RISULTATI, 'e154_ordine_verifica.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e154 — L\'ordine ricostruito rende più graduali dati indipendenti?', '', 'Gruppi (mano, lingua): %s. Distanza media fra unità consecutive (più bassa = più graduale). '
           'Preregistrazione: `preregistrazioni/e154.md`.' % ', '.join('%s (%d)' % kv for kv in ris['gruppi'].items()), '',
           '| caratteristiche | ricostruito | rilegatura | casuali (media) | p |', '|---|---|---|---|---|']
    for c in ('(I) grafia', '(II) impaginazione'):
        r = ris[c]
        out.append('| %s | %.3f | %.3f | %.3f | %.3f |' % (c, r['ricostruito'], r['rilegatura'], r['casuali_media'], r['p']))
    out += ['', 'Ordine confermato da dati indipendenti: **%s**.' % ('sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e154_ordine_verifica.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
