# -*- coding: utf-8 -*-
"""Esperimento 126: parole rimescolate dentro la riga? Accordo fra terminazioni diverse nella composizione della riga
(coppie a distanza >= 2), contro lo scambio di parole fra righe della stessa pagina.

Preregistrazione: preregistrazioni/e126.md. Scrive risultati/e126_trasposizione_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_PAROLE, RIGHE_PAGINA = 126, 200, 4, 29
D = misure.divisore(misure.GLIFI_EVA)


def pagine_term(pagine, dividi):
    """pagine: liste di righe di parole -> pagine di righe di terminazioni (righe pulite con almeno MIN_PAROLE parole)."""
    out = []
    for p in pagine:
        rr = [[tuple(dividi(w)[-2:]) for w in ps] for ps in p if len(ps) >= MIN_PAROLE and all(trascrizione.pulita(w) for w in ps)]
        if len(rr) >= 2:
            out.append(rr)
    return out


def dissimili(a, b):
    return a[-1] != b[-1] and (len(a) < 2 or len(b) < 2 or a[-2] != b[-2])


def statistiche(pagine):
    cc, uguali, tot = [], 0, 0
    for p in pagine:
        for r in p:
            for i in range(len(r)):
                for j in range(i + 2, len(r)):
                    a, b = r[i], r[j]
                    tot += 1
                    uguali += a == b
                    if dissimili(a, b):
                        cc.append((a, b))
                        cc.append((b, a))
    return misure.informazione_mutua(cc), uguali / tot


def scambia(pagine, rnd):
    out = []
    for p in pagine:
        classi = {'prima': [], 'ultima': [], 'interna': []}
        for r in p:
            classi['prima'].append(r[0])
            classi['ultima'].append(r[-1])
            classi['interna'].extend(r[1:-1])
        for v in classi.values():
            rnd.shuffle(v)
        it = {k: iter(v) for k, v in classi.items()}
        nuova = []
        for r in p:
            nuova.append([next(it['prima'])] + [next(it['interna']) for _ in r[1:-1]] + [next(it['ultima'])])
        out.append(nuova)
    return out


def una(args):
    nome, pagine, quale = args
    pt = pagine_term(pagine, e71.lettere if quale == 'lettere' else D)
    rnd = random.Random(SEME)
    im, ug = statistiche(pt)
    nulli_im, nulli_ug = [], []
    for _ in range(RIMESCOLAMENTI):
        a, b = statistiche(scambia(pt, rnd))
        nulli_im.append(a)
        nulli_ug.append(b)
    m, s = statistics.mean(nulli_im), statistics.pstdev(nulli_im)
    mu = statistics.mean(nulli_ug)
    return nome, OrderedDict([('pagine', len(pt)), ('righe', sum(map(len, pt))),
                              ('accordo', OrderedDict([('im', im), ('nullo', m), ('eccesso', im - m), ('z', (im - m) / s if s else None)])),
                              ('identiche', OrderedDict([('quota', ug), ('nullo', mu), ('rapporto', ug / mu if mu else None)]))])


def a_pagine(righe, n=RIGHE_PAGINA):
    return [righe[i:i + n] for i in range(0, len(righe), n)]


def testi():
    import e98_versi_latini as e98
    t = OrderedDict()
    for q in ('ZL', 'IT'):
        per = OrderedDict()
        for r in trascrizione.testo_corrente(trascrizione.leggi(q)):
            if r.parole:
                per.setdefault(r.pagina, []).append(list(r.parole))
        t['Voynich ' + q] = (list(per.values()), 'eva')
    for s in (19, 1, 2):
        rr = [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt'))]
        t['Timm e Schinner, seme %d' % s] = (a_pagine(rr), 'eva')
    for chiave, nome in (('Latin', 'latina'), ('Italian', 'italiana'), ('Hungarian', 'ungherese'), ('Turkish', 'turca')):
        ps = lingue.parole(chiave)[:35000]
        t['Bibbia ' + nome] = (a_pagine([ps[i:i + 9] for i in range(0, len(ps), 9)]), 'lettere')
    t['Ovidio'] = (a_pagine(e98.versi(e98.TESTI['Ovidio, Metamorfosi'])[:5000]), 'lettere')
    return t


def main():
    t = testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, p, q) for n, (p, q) in t.items()]):
            ris[nome] = r
            a = r['accordo']
            print('%-26s pagine %4d righe %5d | accordo fra terminazioni diverse: eccesso %+.4f (z %.1f) | identiche x%.2f' % (
                nome, r['pagine'], r['righe'], a['eccesso'], a['z'] or 0, r['identiche']['rapporto']), flush=True)
    z = lambda n: ris[n]['accordo']['z'] or 0
    lingue_ = ['Bibbia latina', 'Bibbia italiana', 'Bibbia ungherese', 'Bibbia turca', 'Ovidio']
    valido = sum(z(n) > 4 for n in lingue_) >= 3
    voy = min(z('Voynich ZL'), z('Voynich IT'))
    ts = max(z('Timm e Schinner, seme %d' % s) for s in (19, 1, 2))
    if voy > 4 and ts < 2:
        esito = 'trasposizione non esclusa'
    elif voy > 4 and ts > 4:
        esito = 'non discriminante'
    elif max(z('Voynich ZL'), z('Voynich IT')) < 2:
        esito = 'esclusa alla sensibilita del controllo'
    else:
        esito = 'indeciso'
    frazione = ris['Voynich ZL']['accordo']['eccesso'] / ris['Bibbia latina']['accordo']['eccesso'] if ris['Bibbia latina']['accordo']['eccesso'] else None
    ris['valido'], ris['esito'], ris['frazione_del_latino'] = valido, esito, frazione
    print('valido', valido, '| esito:', esito, '| eccesso Voynich ZL / latino %.3f' % (frazione or 0))
    with open(os.path.join(RISULTATI, 'e126_trasposizione_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e126 — Parole rimescolate dentro la riga?', '',
           'Accordo fra terminazioni **diverse** (ultimi 2 segni, coppie a distanza ≥ 2 nella stessa riga), contro %d scambi di parole fra '
           'righe della stessa pagina (per classe di posizione). Preregistrazione: `preregistrazioni/e126.md`.' % RIMESCOLAMENTI, '',
           '| testo | pagine | righe | eccesso d\'IM (z) | terminazioni identiche × nullo |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %d | %+.4f (%.1f) | %.2f |' % (nome, r['pagine'], r['righe'], r['accordo']['eccesso'], r['accordo']['z'] or 0, r['identiche']['rapporto']))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**. Eccesso del Voynich (ZL) come frazione del latino: %.3f.' % ('sì' if valido else 'no', esito, frazione or 0)]
    with open(os.path.join(RISULTATI, 'e126_trasposizione_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
