# -*- coding: utf-8 -*-
"""Esperimento 296: le parole rare del Voynich sono varianti di una lettera di parole frequenti, sparse per il libro come
errori? Quote e R (e211) delle rare varianti e non varianti, nel Voynich e nel generatore dell'e288 (semi 7-9).

Preregistrazione: preregistrazioni/e296.md. Scrive risultati/e296_rare_errori.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure, trascrizione
import e211_parole_proprie as e211

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SOGLIA_FREQ, SEMI = 20, (7, 8, 9)


def dist1(a, b):
    """Vero se le due sequenze distano esattamente una modifica (sostituzione, inserzione o cancellazione)."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def analisi(righe):
    """righe: [(pagina, parole pulite)]."""
    freq = Counter(w for _, ps in righe for w in ps)
    frequenti = [tuple(D(w)) for w, c in freq.items() if c >= SOGLIA_FREQ]
    per_lung = defaultdict(list)
    for f in frequenti:
        per_lung[len(f)].append(f)

    def variante(w):
        u = tuple(D(w))
        return any(dist1(u, f) for L in (len(u) - 1, len(u), len(u) + 1) for f in per_lung.get(L, ()))
    rare = [w for w, c in freq.items() if 2 <= c <= 5]
    hapax = [w for w, c in freq.items() if c == 1]
    var = {w for w in rare if variante(w)}
    sez = {x.pagina: x.sezione for x in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    herb = defaultdict(list)
    for pag, ps in righe:
        herb[pag] += ps
    unita = [v for p, v in herb.items() if len(v) >= 60 and sez.get(p) == 'H']

    def R_di(gruppo):
        # e211.prova calcola R sulle parole con 2-5 occorrenze nelle unita': qui le parole rare (nelle unita') fuori dal gruppo diventano
        # segnaposto molto frequenti, cosi' contano solo le rare del gruppo
        cu = Counter(w for u in unita for w in u)
        sost = [[w if (w in gruppo or cu[w] > 5) else '·%d' % (i % 7) for i, w in enumerate(u)] for u in unita]
        return e211.prova(sost, random.Random(211))
    return OrderedDict([('tipi', len(freq)), ('frequenti', len(frequenti)), ('rare', len(rare)), ('rare_varianti', len(var)),
                        ('quota_rare_varianti', len(var) / len(rare)), ('quota_hapax_varianti', sum(variante(w) for w in hapax) / len(hapax)),
                        ('R_rare_varianti', R_di(var)), ('R_rare_non_varianti', R_di(set(rare) - var)), ('R_tutte_le_rare', R_di(set(rare)))])


def main():
    voy = [(r.pagina, [w for w in r.parole if trascrizione.pulita(w)]) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    ris = OrderedDict([('Voynich', analisi(voy))])
    import corpo2
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    c, c2, freq, _, _, _ = e251.contesto()
    for s in SEMI:
        e233.SIGMA_POST = 0.04
        rr = e236.dopo(corpo2.genera_v2(c2, dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), s), freq, 100 + s)
        ris['generatore e288, seme %d' % s] = analisi([(p, [w for w in ps if trascrizione.pulita(w)]) for p, _, ps in rr])
    for n, r in ris.items():
        print('%-26s rare %d, varianti %.3f (hapax %.3f) | R varianti %.2f, non varianti %.2f, tutte %.2f' % (
            n, r['rare'], r['quota_rare_varianti'], r['quota_hapax_varianti'], r['R_rare_varianti']['R'] or 0, r['R_rare_non_varianti']['R'] or 0,
            r['R_tutte_le_rare']['R'] or 0), flush=True)
    rv = ris['Voynich']['R_rare_varianti']['R']
    rg = statistics.mean(ris['generatore e288, seme %d' % s]['R_rare_varianti']['R'] for s in SEMI)
    esito = 'errori sparsi sostenuti' if rv <= 3 and rg >= 10 else ('non sostenuti' if rv > 5 else 'incerto')
    json.dump(OrderedDict([('risultati', ris), ('R_varianti_generatore_media', rg), ('esito', esito)]), open(os.path.join(RISULTATI, 'e296_rare_errori.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)
    md = ['# e296 — Le parole rare sono errori sparsi?', '', 'Rare = 2–5 occorrenze; varianti = a distanza 1 (sui segni) da una parola con almeno %d occorrenze. '
          'R dell\'e211 sulle pagine dell\'erbario. Preregistrazione: `preregistrazioni/e296.md`.' % SOGLIA_FREQ, '',
          '| testo | rare | quota varianti | quota hapax varianti | R varianti | R non varianti | R tutte |', '|---|---|---|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %d | %.3f | %.3f | %.2f | %.2f | %.2f |' % (n, r['rare'], r['quota_rare_varianti'], r['quota_hapax_varianti'], r['R_rare_varianti']['R'] or 0,
                                                              r['R_rare_non_varianti']['R'] or 0, r['R_tutte_le_rare']['R'] or 0))
    md += ['', 'Esito: **%s** (Voynich R varianti %.2f; generatore %.2f).' % (esito, rv, rg)]
    open(os.path.join(RISULTATI, 'e296_rare_errori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
