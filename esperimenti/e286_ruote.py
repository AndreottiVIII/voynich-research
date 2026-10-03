# -*- coding: utf-8 -*-
"""Esperimento 286: negli anelli di testo circolare (Cc) le parole consecutive cambiano un solo pezzo (prefisso, centro,
finale) piu' del caso, come in una ruota combinatoria? Contro le parole rimescolate nell'anello, contro tratti di
paragrafo delle stesse lunghezze e con un controllo positivo di ruote sintetiche.

Preregistrazione: preregistrazioni/e286.md. Scrive risultati/e286_ruote.json e .md.
"""
import itertools, json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e249_pezzi_simboli as e249
import e285_pezzi_contesto as e285

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_PAROLE, RUMORE = 286, 1000, 6, 0.3


def M(segmenti):
    cc = [(a, b) for s in segmenti for a, b in zip(s, s[1:])]
    return sum(sum(x == y for x, y in zip(a, b)) == 2 for a, b in cc) / len(cc)


def prova(segmenti, rnd):
    vero = M(segmenti)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for s in segmenti:
            x = list(s)
            rnd.shuffle(x)
            mes.append(x)
        nulli.append(M(mes))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('segmenti', len(segmenti)), ('coppie', sum(len(s) - 1 for s in segmenti)), ('M', vero), ('nullo', m),
                        ('eccesso', vero - m), ('z', (vero - m) / sd if sd else None)])


def main():
    rnd = random.Random(SEME)
    zl = list(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    tutte = [r for r in trascrizione.leggi('ZL')]
    pul = lambda r: [w for w in r.parole if trascrizione.pulita(w)]
    voy = [w for r in zl if r.parole for w in pul(r)]
    taglia = e249.segmentatore(voy)
    cache = {}
    tp = lambda w: cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w))
    anelli = [[tp(w) for w in pul(r)] for r in tutte if r.tipo == 'Cc' and r.parole and len(pul(r)) >= MIN_PAROLE]
    lunghezze = [len(a) for a in anelli]
    flusso = [tp(w) for w in voy]
    ordinario, i = [], 0
    for L in lunghezze:
        ordinario.append(flusso[i:i + L])
        i += L
    pre = sorted({t[0] for t in flusso if t[0]})
    cen = sorted({t[1] for t in flusso if t[1]})
    fin = sorted({t[2] for t in flusso if t[2]})
    sintetici = []
    for L in lunghezze:
        ruota = list(itertools.product(rnd.sample(pre, 2), rnd.sample(cen, 3), rnd.sample(fin, 2)))
        a = [ruota[k % len(ruota)] for k in range(L)]
        sintetici.append([rnd.choice(flusso) if rnd.random() < RUMORE else t for t in a])
    testi = OrderedDict([('anelli (Cc)', anelli), ('riferimento: paragrafi in tratti uguali', ordinario), ('controllo positivo: ruote sintetiche', sintetici)])
    ris = OrderedDict((n, prova(s, rnd)) for n, s in testi.items())
    for n, r in ris.items():
        print('%-42s M %.4f nullo %.4f eccesso %+.4f z %.1f' % (n, r['M'], r['nullo'], r['eccesso'], r['z'] or 0), flush=True)
    a, o, p = (ris[n] for n in testi)
    valido = (p['z'] or 0) > 4
    ruote = (a['z'] or 0) > 3 and a['eccesso'] >= 2 * max(o['eccesso'], 0)
    esito = 'non valido' if not valido else ('ruote combinatorie' if ruote else 'nessuna struttura combinatoria oltre la copia')
    json.dump(OrderedDict([('risultati', ris), ('valido', valido), ('esito', esito)]), open(os.path.join(RISULTATI, 'e286_ruote.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    md = ['# e286 — Gli anelli di testo circolare sono ruote combinatorie?', '',
          'M = quota di coppie consecutive che cambiano un solo pezzo su tre (prefisso, centro, finale; segmentatore dell\'e249). z contro %d '
          'rimescolamenti dentro ogni segmento. Preregistrazione: `preregistrazioni/e286.md`.' % RIMESCOLAMENTI, '',
          '| testo | segmenti | coppie | M | nullo | eccesso | z |', '|---|---|---|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %d | %d | %.4f | %.4f | %+.4f | %.1f |' % (n, r['segmenti'], r['coppie'], r['M'], r['nullo'], r['eccesso'], r['z'] or 0))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e286_ruote.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
