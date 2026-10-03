# -*- coding: utf-8 -*-
"""Esperimento 285c: la dipendenza fra finali di parole vicine (e285b) divisa in ripetizione dello stesso finale e
passaggi fra finali diversi; profilo per distanza; passaggi piu' frequenti del caso.

Preregistrazione: preregistrazioni/e285c.md. Scrive risultati/e285c_ripetizione_passaggi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e249_pezzi_simboli as e249
import e251_lessico_sezione as e251
import e285_pezzi_contesto as e285
import e285b_finale_non_varianti as e285b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, SEMI_GEN, MIN_OCC = 2853, 100, (7, 8, 9), 30


def coppie(righe, d=1):
    return [(a[1][2], b[1][2]) for r in righe for a, b in zip(r, r[d:]) if e285b.distanza(a[0], b[0]) >= e285b.DIST_MIN]


def ripetizione(cc):
    return sum(a == b for a, b in cc) / len(cc) if cc else 0.0


def passaggi(cc):
    return e285.mi([(a, b) for a, b in cc if a != b])


def misure(righe, rnd):
    rim = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in righe:
            x = list(r)
            rnd.shuffle(x)
            mes.append(x)
        rim.append(mes)
    out = OrderedDict()
    for nome, f in (('ripetizione', ripetizione), ('passaggi', passaggi)):
        vero = f(coppie(righe))
        nulli = [f(coppie(m)) for m in rim]
        m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        out[nome] = OrderedDict([('vero', vero), ('nullo', m), ('sd', sd), ('eccesso', vero - m), ('z', (vero - m) / sd if sd else None)])
    out['ripetizione_per_distanza'] = OrderedDict()
    for d in (1, 2, 3):
        vero = ripetizione(coppie(righe, d))
        nulli = [ripetizione(coppie(m, d)) for m in rim[:30]]
        out['ripetizione_per_distanza']['%d' % d] = vero - statistics.mean(nulli)
    cc = [(a, b) for a, b in coppie(righe) if a != b]
    ca, cb, n = Counter(a for a, _ in cc), Counter(b for _, b in cc), len(cc)
    oss = Counter(cc)
    rap = [((a, b), c, c / (ca[a] * cb[b] / n)) for (a, b), c in oss.items() if c >= MIN_OCC]
    out['passaggi_frequenti'] = [('%s → %s' % ab, c, round(r, 2)) for ab, c, r in sorted(rap, key=lambda x: -x[2])[:10]]
    return out


def main():
    rnd = random.Random(SEME)
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    taglia = e249.segmentatore([w for r in voy for w in r])
    cache = {}
    tp = lambda w: (w, cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w)))
    testi = OrderedDict([('Voynich', [[tp(w) for w in r] for r in voy])])
    c, c2, freq, _, _, _ = e251.contesto()
    for s in SEMI_GEN:
        rr = e236.dopo(e233.genera(c2, dict(e251.CONF, gamma=0.0), s), freq, 100 + s)
        testi['generatore e241, seme %d' % s] = [[tp(w) for w in ps if trascrizione.pulita(w)] for _, _, ps in rr]
    g7 = testi['generatore e241, seme %d' % SEMI_GEN[0]]
    finali = [f for f, _ in Counter(t[1][2] for r in g7 for t in r if t[1][2]).most_common()]
    lettere = [l for l, _ in Counter(x for _, x in zip(range(200000), e285.latino())).most_common()]
    mappa = {l: finali[i % len(finali)] for i, l in enumerate(lettere)}
    it, pos = e285.latino(), []
    for r in g7:
        nuova = []
        for w, (a, b, f) in r:
            if f:
                f2 = mappa[next(it)]
                nuova.append((w[:len(w) - len(f)] + f2, (a, b, f2)))
            else:
                nuova.append((w, (a, b, f)))
        pos.append(nuova)
    testi['controllo positivo (finali = latino)'] = pos
    ris = OrderedDict()
    for n, righe in testi.items():
        ris[n] = misure([r for r in righe if len(r) >= 2], rnd)
        print('%-40s ripetizione %+.4f (z %.1f) | passaggi %+.4f (z %.1f) | distanze %s' % (
            n, ris[n]['ripetizione']['eccesso'], ris[n]['ripetizione']['z'] or 0, ris[n]['passaggi']['eccesso'], ris[n]['passaggi']['z'] or 0,
            {k: round(v, 4) for k, v in ris[n]['ripetizione_per_distanza'].items()}), flush=True)
    gen = [n for n in testi if n.startswith('generatore')]
    soglia = {k: max(ris[g][k]['eccesso'] for g in gen) for k in ('ripetizione', 'passaggi')}
    p = ris['controllo positivo (finali = latino)']['passaggi']
    valido = p['eccesso'] > soglia['passaggi'] + 3 * p['sd']
    v = ris['Voynich']
    sist = v['passaggi']['eccesso'] > soglia['passaggi'] + 3 * v['passaggi']['sd']
    rip = v['ripetizione']['eccesso'] > soglia['ripetizione'] + 3 * v['ripetizione']['sd']
    if not valido:
        esito = 'non valido'
    elif sist and rip:
        esito = 'passaggi sistematici e ripetizione'
    elif sist:
        esito = 'passaggi sistematici (compatibile con un messaggio, da verificare oltre)'
    elif rip:
        esito = 'ripetizione (inerzia o concordanza)'
    else:
        esito = 'nessuna delle due oltre il generatore'
    json.dump(OrderedDict([('risultati', ris), ('soglie_generatori', soglia), ('valido', valido), ('esito', esito)]),
              open(os.path.join(RISULTATI, 'e285c_ripetizione_passaggi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e285c — Finali vicini: ripetizione o passaggi sistematici?', '',
          'Coppie di parole vicine non varianti; eccessi sul rimescolamento nella riga (%d rimescolamenti). Preregistrazione: `preregistrazioni/e285c.md`.' % RIMESCOLAMENTI, '',
          '| testo | ripetizione (eccesso, z) | passaggi fra finali diversi (eccesso, z) | ripetizione a distanza 1 / 2 / 3 |', '|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %+.4f (z %.1f) | %+.4f (z %.1f) | %s |' % (n, r['ripetizione']['eccesso'], r['ripetizione']['z'] or 0, r['passaggi']['eccesso'],
                                                                 r['passaggi']['z'] or 0, ' / '.join('%+.4f' % x for x in r['ripetizione_per_distanza'].values())))
    md += ['', 'Passaggi fra finali diversi più frequenti del caso nel Voynich (osservate, rapporto osservato / atteso): ' +
           '; '.join('%s %d (%.2f)' % x for x in ris['Voynich']['passaggi_frequenti']) + '.', '',
           'Lo stesso nel generatore (seme 7): ' + '; '.join('%s %d (%.2f)' % x for x in ris['generatore e241, seme 7']['passaggi_frequenti']) + '.', '',
           'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e285c_ripetizione_passaggi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
