# -*- coding: utf-8 -*-
"""Esperimento 154b: come e154, ma l'ordine si ricostruisce su un vocabolario con le cinque scelte di grafia
unificate, cosi' che la verifica sulla grafia sia indipendente.

Preregistrazione: preregistrazioni/e154b.md. Scrive risultati/e154b_ordine_normalizzato.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e148_bifogli as e148
import e150_ordine_scrittura as e150
import e154_ordine_verifica as e154

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, CASUALI = 1542, 1000
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'k', 't', 'p', 'f'}


def normalizza(w):
    u = ['ch' if g == 'sh' else 'k' if g == 't' else g for g in D(w)]
    if len(u) >= 2 and u[-1] == 'r' and u[-2] in ('o', 'a'):
        u[-1] = 'l'
    if len(u) >= 3 and u[0] == 'q' and u[1] == 'o' and u[2] in GALLOWS:
        u = u[1:]
    if len(u) >= 2 and u[-1] == 'y' and u[-2] == 'd':
        u[-2] = 'e'
    return ''.join(u)


def main():
    rnd = random.Random(SEME)
    U = e150.unita()
    graf, imp = e154.caratteristiche(U)
    gruppi = defaultdict(list)
    for n, u in U.items():
        if imp.get(n) is not None:
            gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = OrderedDict((k, v) for k, v in sorted(gruppi.items(), key=lambda kv: -len(kv[1])) if len(v) >= e154.MINIMO)
    tot_r = tot_l = 0.0
    pesi = 0
    casuali = [0.0] * CASUALI
    dettaglio = OrderedDict()
    for k, nomi in gruppi.items():
        X = e154.standardizza({n: graf[n] for n in nomi})
        vett = {n: Counter(normalizza(w) for ps in U[n]['righe'] for w in ps) for n in nomi}
        S = [[e148.coseno(vett[a], vett[b]) for b in nomi] for a in nomi]
        ric = [nomi[i] for i in e150.ricostruisci(S)]
        ril = sorted(nomi, key=lambda n: U[n]['primo'])
        w = len(nomi) - 1
        dr, dl = e154.distanza(ric, X), e154.distanza(ril, X)
        tot_r += w * dr
        tot_l += w * dl
        pesi += w
        for i in range(CASUALI):
            o = nomi[:]
            rnd.shuffle(o)
            casuali[i] += w * e154.distanza(o, X)
        dettaglio['mano %s, lingua %s' % k] = OrderedDict([('ricostruito', dr), ('rilegatura', dl)])
    r_ric, r_ril = tot_r / pesi, tot_l / pesi
    cas = [x / pesi for x in casuali]
    p = sum(x <= r_ric for x in cas) / CASUALI
    conferma = r_ric < r_ril and p < 0.05
    ris = OrderedDict([('ricostruito', r_ric), ('rilegatura', r_ril), ('casuali_media', statistics.mean(cas)), ('p', p), ('per_gruppo', dettaglio), ('ordine_confermato_dalla_grafia', conferma)])
    print('grafia: ricostruito (vocabolario normalizzato) %.3f | rilegatura %.3f | casuali %.3f | p %.3f | %s | confermato %s' % (
        r_ric, r_ril, statistics.mean(cas), p, ' '.join('%s %.2f/%.2f' % (g, x['ricostruito'], x['rilegatura']) for g, x in dettaglio.items()), conferma))
    with open(os.path.join(RISULTATI, 'e154b_ordine_normalizzato.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e154b — Verifica sulla grafia con vocabolario normalizzato', '', 'Ordine ricostruito su vocabolario con ch=sh, k=t, -l=-r, qo-=o-, -dy=-ey. Preregistrazione: '
           '`preregistrazioni/e154b.md`.', '', '| | ricostruito | rilegatura | casuali (media) | p |', '|---|---|---|---|---|',
           '| distanza di grafia | %.3f | %.3f | %.3f | %.3f |' % (r_ric, r_ril, statistics.mean(cas), p), '',
           'Per gruppo (ricostruito / rilegatura): ' + '; '.join('%s %.2f / %.2f' % (g, x['ricostruito'], x['rilegatura']) for g, x in dettaglio.items()) + '.',
           '', 'Ordine confermato dalla grafia: **%s**.' % ('sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e154b_ordine_normalizzato.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
