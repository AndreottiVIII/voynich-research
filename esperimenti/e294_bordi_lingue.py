# -*- coding: utf-8 -*-
"""Esperimento 294: profilo dei bordi (prefisso, centro, finale, finale -> prefisso: eccesso di informazione mutua fra parole
vicine) nel Voynich, nel generatore e in tutte le lingue della cache e nei testi tecnici latini. Indice dei bordi =
(prefisso + finale)/2 - centro.

Preregistrazione: preregistrazioni/e294.md. Scrive risultati/e294_bordi_lingue.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import lingue, misure, trascrizione
import e249_pezzi_simboli as e249
import e285_pezzi_contesto as e285

RISULTATI = os.path.join(QUI, '..', 'risultati')
PAROLE, PER_RIGA, RIMESCOLAMENTI, SEME = 20000, 9, 30, 294
G_EVA = misure.divisore(misure.GLIFI_EVA)


def segmentatore(parole, unita):
    """Il segmentatore dell'e249 con la funzione di unita' data (segni EVA o lettere)."""
    conta = Counter()
    for w in parole:
        u = unita(w)
        for n in range(1, e249.N_MAX + 1):
            for i in range(len(u) - n + 1):
                conta[tuple(u[i:i + n])] += 1
    lessico = {x for x, _ in conta.most_common(e249.LESSICO)} | {x for x in conta if len(x) == 1}
    tot = sum(conta[x] for x in lessico)
    lp = {x: math.log(conta[x] / tot) - e249.PENALITA for x in lessico}

    def taglia(w):
        u = tuple(unita(w))
        best = [(0.0, [])] + [(-1e18, None)] * len(u)
        for i in range(1, len(u) + 1):
            for n in range(1, min(e249.N_MAX, i) + 1):
                x = u[i - n:i]
                if x in lp and best[i - n][1] is not None and best[i - n][0] + lp[x] > best[i][0]:
                    best[i] = (best[i - n][0] + lp[x], best[i - n][1] + [''.join(x)])
        return best[len(u)][1]
    return taglia


def profilo(righe, unita, seme):
    """righe di parole -> eccessi per pezzo e indice dei bordi."""
    taglia = segmentatore([w for r in righe for w in r], unita)
    cache = {}
    tp = lambda w: cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w))
    pr = [[tp(w) for w in r] for r in righe if len(r) >= 2]
    e285.RIMESCOLAMENTI = RIMESCOLAMENTI
    ecc = e285.eccessi(pr, random.Random(seme))
    e = {k: v['eccesso'] for k, v in ecc.items()}
    return OrderedDict([('eccessi', e), ('indice_bordi', (e['prefisso'] + e['finale']) / 2 - e['centro'])])


def in_righe(parole):
    parole = parole[:PAROLE]
    return [parole[i:i + PER_RIGA] for i in range(0, len(parole), PER_RIGA)]


def lavoro(args):
    tipo, chiave = args
    try:
        if tipo == 'Voynich':
            righe = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
            return args, profilo(righe, G_EVA, SEME)
        if tipo == 'generatore':
            import corpo2
            import e233_frequenti_esatte as e233
            import e236_due_fonti as e236
            import e251_lessico_sezione as e251
            c, c2, freq, _, _, _ = e251.contesto()
            e233.SIGMA_POST = 0.04
            rr = e236.dopo(corpo2.genera_v2(c2, dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), 7), freq, 107)
            return args, profilo([[w for w in ps if trascrizione.pulita(w)] for _, _, ps in rr], G_EVA, SEME)
        parole = lingue.genere(chiave) if tipo == 'tecnico' else lingue.parole(chiave, max_caratteri=400000)
        parole = [w.lower() for w in parole if w.isalpha()]
        if len(parole) < 5000:
            return args, None
        return args, profilo(in_righe(parole), list, SEME)
    except Exception as ex:
        return args, {'errore': repr(ex)}


def main():
    lavori = [('Voynich', 'Voynich'), ('generatore', 'e288 seme 7')] + [('lingua', k) for k in lingue.indice()] + [('tecnico', k) for k in lingue.GENERI]
    ris = OrderedDict()
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for (t, k), r in pool.imap_unordered(lavoro, lavori):
            ris['%s: %s' % (t, k)] = r
            if r and 'errore' not in r:
                print('%-40s indice bordi %+.4f | %s' % ('%s: %s' % (t, k), r['indice_bordi'], {a: round(b, 4) for a, b in r['eccessi'].items()}), flush=True)
            else:
                print('%-40s %s' % ('%s: %s' % (t, k), r), flush=True)
    validi = {n: r for n, r in ris.items() if r and 'errore' not in r}
    iv = validi['Voynich: Voynich']['indice_bordi']
    naturali = {n: r['indice_bordi'] for n, r in validi.items() if n.startswith(('lingua', 'tecnico'))}
    sopra = [n for n, x in naturali.items() if x >= iv]
    meta = [n for n, x in naturali.items() if x >= iv / 2]
    esito = 'profilo da lingua' if len(sopra) >= 3 else ('profilo non da lingua' if not meta else 'incerto')
    grad = sorted(validi.items(), key=lambda kv: -kv[1]['indice_bordi'])
    json.dump(OrderedDict([('risultati', ris), ('indice_Voynich', iv), ('naturali_sopra', sopra), ('naturali_sopra_meta', meta), ('esito', esito)]),
              open(os.path.join(RISULTATI, 'e294_bordi_lingue.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e294 — Il profilo dei bordi nelle lingue', '', 'Indice dei bordi = (eccesso del prefisso + eccesso del finale)/2 − eccesso del centro (informazione mutua fra '
          'parole vicine oltre il rimescolamento nella riga). Preregistrazione: `preregistrazioni/e294.md`.', '',
          '| testo | indice dei bordi | prefisso | centro | finale | finale → prefisso |', '|---|---|---|---|---|---|']
    for n, r in grad[:25]:
        e = r['eccessi']
        md.append('| %s | %+.4f | %+.4f | %+.4f | %+.4f | %+.4f |' % (n, r['indice_bordi'], e['prefisso'], e['centro'], e['finale'], e['finale → prefisso']))
    md += ['', '(prime 25 su %d; tutte nel json)' % len(grad), '', 'Testi naturali con indice ≥ Voynich (%+.4f): %d (%s). Con indice ≥ metà: %d.' % (
        iv, len(sopra), ', '.join(sopra[:10]) or '—', len(meta)), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e294_bordi_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
