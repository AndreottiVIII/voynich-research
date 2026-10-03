# -*- coding: utf-8 -*-
"""Esperimento 285: dipendenza fra pezzi omologhi (prefisso, centro, finale) di parole vicine, oltre il vocabolario
della riga (eccesso sull'informazione mutua con le parole rimescolate nella riga). Voynich contro il generatore e241
(semi 7-9) e contro un controllo positivo con un testo latino nascosto nei finali.

Preregistrazione: preregistrazioni/e285.md. Scrive risultati/e285_pezzi_contesto.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e249_pezzi_simboli as e249
import e251_lessico_sezione as e251

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, SEMI_GEN, INIZIO_LATINO = 285, 100, (7, 8, 9), 20000
PEZZI = OrderedDict([('prefisso', (0, 0)), ('centro', (1, 1)), ('finale', (2, 2)), ('finale → prefisso', (2, 0))])


def parti(taglia, w):
    p = taglia(w) or [w]
    if len(p) == 1:
        return ('', p[0], '')
    if len(p) == 2:
        return (p[0], '', p[1])
    return (p[0], ''.join(p[1:-1]), p[-1])


def mi(coppie):
    n = len(coppie)
    cxy, cx, cy = Counter(coppie), Counter(a for a, _ in coppie), Counter(b for _, b in coppie)
    return sum(c / n * math.log2(c * n / (cx[a] * cy[b])) for (a, b), c in cxy.items())


def eccessi(righe, rnd):
    """righe: liste di triple (prefisso, centro, finale). Eccesso di informazione mutua per ogni coppia di pezzi."""
    out = OrderedDict()
    for nome, (i, j) in PEZZI.items():
        vero = mi([(a[i], b[j]) for r in righe for a, b in zip(r, r[1:])])
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            cc = []
            for r in righe:
                x = list(r)
                rnd.shuffle(x)
                cc += [(a[i], b[j]) for a, b in zip(x, x[1:])]
            nulli.append(mi(cc))
        out[nome] = OrderedDict([('vero', vero), ('nullo', statistics.mean(nulli)), ('sd', statistics.pstdev(nulli)), ('eccesso', vero - statistics.mean(nulli))])
    return out


def latino():
    for w in lingue.parole('Latin')[INIZIO_LATINO:]:
        for ch in w.lower():
            if ch.isalpha():
                yield ch


def main():
    rnd = random.Random(SEME)
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    taglia = e249.segmentatore([w for r in voy for w in r])
    cache = {}
    tp = lambda w: cache[w] if w in cache else cache.setdefault(w, parti(taglia, w))
    testi = OrderedDict([('Voynich', [[tp(w) for w in r] for r in voy])])
    c, c2, freq, _, _, _ = e251.contesto()
    for s in SEMI_GEN:
        rr = e236.dopo(e233.genera(c2, dict(e251.CONF, gamma=0.0), s), freq, 100 + s)
        testi['generatore e241, seme %d' % s] = [[tp(w) for w in ps if trascrizione.pulita(w)] for _, _, ps in rr]
    g7 = testi['generatore e241, seme %d' % SEMI_GEN[0]]
    finali = [f for f, _ in Counter(t[2] for r in g7 for t in r if t[2]).most_common()]
    lettere = [l for l, _ in Counter(x for _, x in zip(range(200000), latino())).most_common()]
    mappa = {l: finali[i % len(finali)] for i, l in enumerate(lettere)}
    for nome, p in (('controllo positivo (finali = latino, puro)', 1.0), ('controllo positivo (al 50%)', 0.5)):
        it, rr_ = latino(), []
        for r in g7:
            rr_.append([(a, b, mappa[next(it)]) if f and rnd.random() < p else (a, b, f) for a, b, f in r])
        testi[nome] = rr_
    ris = OrderedDict()
    for nome, righe in testi.items():
        ris[nome] = eccessi([r for r in righe if len(r) >= 2], rnd)
        print('%-44s ' % nome + ' | '.join('%s %+.4f' % (k, v['eccesso']) for k, v in ris[nome].items()), flush=True)
    gen = [n for n in testi if n.startswith('generatore')]
    soglia = {k: max(ris[g][k]['eccesso'] for g in gen) for k in PEZZI}
    valido = ris['controllo positivo (finali = latino, puro)']['finale']['eccesso'] > soglia['finale'] + 3 * ris['controllo positivo (finali = latino, puro)']['finale']['sd']
    portatori = [k for k in ('prefisso', 'centro', 'finale') if ris['Voynich'][k]['eccesso'] > soglia[k] + 3 * ris['Voynich'][k]['sd']]
    esito = 'non valido' if not valido else ('pezzo portatore candidato: ' + ', '.join(portatori) if portatori else 'nessun pezzo portatore oltre il procedimento')
    json.dump(OrderedDict([('risultati', ris), ('soglia_generatori', soglia), ('valido', valido), ('portatori', portatori), ('esito', esito)]),
              open(os.path.join(RISULTATI, 'e285_pezzi_contesto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e285 — Tabelle e griglie: un pezzo della parola dipende dal contesto?', '',
          'Eccesso di informazione mutua (bit) fra pezzi omologhi di parole vicine, rispetto alle parole rimescolate nella riga (%d rimescolamenti). '
          'Pezzi dal segmentatore dell\'e249. Preregistrazione: `preregistrazioni/e285.md`.' % RIMESCOLAMENTI, '',
          '| testo | ' + ' | '.join(PEZZI) + ' |', '|---|' + '---|' * len(PEZZI)]
    for nome in testi:
        md.append('| %s | %s |' % (nome, ' | '.join('%+.4f (sd %.4f)' % (ris[nome][k]['eccesso'], ris[nome][k]['sd']) for k in PEZZI)))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e285_pezzi_contesto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
