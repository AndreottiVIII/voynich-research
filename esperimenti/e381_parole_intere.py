# -*- coding: utf-8 -*-
"""Esperimento 381: le misure dei testi sensati di e374, e375, e377 rifatte con le parole intere (spazi come
separatori; lettere, segni combinanti e apostrofi tenuti; segno = lettera + segni combinanti).

Preregistrazione: preregistrazioni/e381.md. Scrive risultati/e381_parole_intere.json e .md.
"""
import json, os, random, statistics, sys, unicodedata, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e374_bordi_gibberish as e374
import e375_coppie as e375
import e377_giuntura_gibberish as e377

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
APOSTROFI = ("'", '’')
CATEGORIE = ('Historical', 'Modern', 'Conlangs')


def parola(pezzo):
    """Segni di una parola intera: lettera + segni combinanti; apostrofi dopo la prima lettera."""
    segni = []
    for c in pezzo.lower():
        cat = unicodedata.category(c)
        if cat[0] == 'L':
            segni.append(c)
        elif cat[0] == 'M' and segni:
            segni[-1] += c
        elif c in APOSTROFI and segni:
            segni.append(c)
    return tuple(segni)


def testi():
    out = OrderedDict()
    with zipfile.ZipFile(os.path.join(GB, 'meaningful.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt') and ('/texts/' in n or n.startswith('texts/')):
                righe = []
                for l in z.read(n).decode('utf-8', errors='ignore').splitlines():
                    ws = [w for w in (parola(p) for p in l.split()) if w]
                    if ws:
                        righe.append(ws)
                out[os.path.basename(n)] = righe
    return out


def main():
    rnd = random.Random(381)
    sens = testi()
    voy_pag = e375.voynich()
    n_voy = sum(len(r) for p in voy_pag for r in p)
    ris = OrderedDict()
    # e374
    a = OrderedDict()
    prime60 = {k: t[:60] for k, t in sens.items()}
    gruppi374 = OrderedDict([('testi sensati', [r for t in prime60.values() for r in t])])
    for cat in CATEGORIE:
        gruppi374['testi sensati: %s' % cat] = [r for k, t in prime60.items() if k.startswith(cat) for r in t]
    for nome, righe in gruppi374.items():
        vero, zs, cont = e374.z_testo(righe, rnd, 1000)
        a[nome] = OrderedDict([('righe', sum(len(r) >= 3 for r in righe)), ('F1', vero[0]), ('F2', vero[1]), ('L1', vero[2]), ('L2', vero[3]), ('z', zs)])
        print('e374', nome, json.dumps(a[nome], default=float), flush=True)
    ris['e374'] = a
    # e375 ed e377 sui gruppi pareggiati
    b, c = OrderedDict(), OrderedDict()
    for cat in CATEGORIE:
        tt = [t for k, t in sens.items() if k.startswith(cat)]
        pag = e375.a_pagine(tt, quota=n_voy / len(tt))
        b['testi sensati: %s' % cat] = e375.Corpo(pag).prova(rnd)
        print('e375', cat, json.dumps(b['testi sensati: %s' % cat], default=float), flush=True)
        x = e377.prova([r for p in pag for r in p], rnd, 1000)
        x.pop('coppie_in_eccesso')
        c['testi sensati: %s' % cat] = x
        print('e377', cat, json.dumps(x, default=float), flush=True)
    ris['e375'] = b
    ris['e377'] = c
    # e377, controllo per testo
    per_testo = []
    for k, t in sens.items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        x = e377.prova(righe, rnd, 50)
        per_testo.append(OrderedDict([('testo', k), ('parole', x['parole']), ('E', x['E']), ('z', x['z'])]))
    per_testo.sort(key=lambda x: -x['E'])
    voy = [r for p in voy_pag for r in p]
    sub = []
    for _ in range(5):
        o = rnd.sample(voy, len(voy))
        pr, n = [], 0
        for r in o:
            if n >= 10000:
                break
            pr.append(r)
            n += len(r)
        sub.append(e377.prova(pr, rnd, 50)['E'])
    Ev = statistics.median(sub)
    sopra = [x for x in per_testo if x['E'] > Ev]
    ris['e377_per_testo'] = per_testo
    ris['e377_voynich_10000'] = sub
    controllo375 = all(x['z'] > 3 for x in b.values())
    esiti = OrderedDict([('e374', 'invariato (dipendeva solo dal gibberish)'),
                         ('e375', 'controllo positivo confermato' if controllo375 else 'controllo positivo NON confermato: esito da rileggere'),
                         ('e377', 'invariato (dipendeva solo da gibberish e Voynich)'),
                         ('giuntura_del_voynich', 'E %.3f; %d testi su %d hanno E maggiore' % (Ev, len(sopra), len(per_testo)))])
    ris['esiti'] = esiti
    json.dump(ris, open(os.path.join(RISULTATI, 'e381_parole_intere.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e381 — Testi sensati con le parole intere: e374, e375, e377 rifatti', '', 'Preregistrazione: `preregistrazioni/e381.md`.', '',
          '## e374 (bordi della riga)', '', '| testi | righe | F1 | z | F2 | z | L1 | z | L2 | z |', '|---|---|---|---|---|---|---|---|---|---|']
    for k, x in a.items():
        md.append('| %s | %d | %.4f | %.1f | %.4f | %.1f | %+.2f | %.1f | %+.2f | %.1f |' % (k, x['righe'], x['F1'], x['z'][0], x['F2'], x['z'][1], x['L1'], x['z'][2], x['L2'], x['z'][3]))
    md += ['', '## e375 (coppie oltre la giuntura) ed e377 (giuntura)', '', '| gruppo | parole | S | nullo | R | z | E giuntura | z |', '|---|---|---|---|---|---|---|---|']
    for k in b:
        md.append('| %s | %d | %d | %.1f | %.2f | %.1f | %.4f | %.1f |' % (k, b[k]['parole'], b[k]['S'], b[k]['nullo'], b[k]['R'], b[k]['z'], c[k]['E'], c[k]['z']))
    md += ['', '## e377, giuntura per testo (prime 10.000 parole, 50 rimescolamenti)', '', 'Voynich su 10.000 parole: %s (mediana %.3f).' % (', '.join('%.3f' % x for x in sub), Ev), '',
           '| testo | parole | E | z |', '|---|---|---|---|']
    for x in per_testo:
        md.append('| %s | %d | %.4f | %.1f |' % (x['testo'], x['parole'], x['E'], x['z']))
    md += ['', 'Esiti: ' + '; '.join('%s: %s' % kv for kv in esiti.items()) + '.']
    open(os.path.join(RISULTATI, 'e381_parole_intere.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
