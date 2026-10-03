# -*- coding: utf-8 -*-
"""Esperimento 295: la dipendenza fra i finali di parole vicine continua attraverso l'a capo (ultima parola di una riga,
prima della seguente)? Rapporto con quella dentro la riga, nel Voynich, nel generatore e nella Bibbia latina in righe.

Preregistrazione: preregistrazioni/e295.md. Scrive risultati/e295_a_capo.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import lingue, trascrizione
import e285_pezzi_contesto as e285
import e294_bordi_lingue as e294

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 295, 200


def misura(righe, unita, rnd):
    """righe: [(pagina, inizio paragrafo, parole)]."""
    taglia = e294.segmentatore([w for _, _, r in righe for w in r], unita)
    cache = {}
    fin = lambda w: (cache[w] if w in cache else cache.setdefault(w, e285.parti(taglia, w)))[2]
    e285.RIMESCOLAMENTI = 100
    dentro = e285.eccessi([[e285.parti(taglia, w) for w in r] for _, _, r in righe if len(r) >= 2], rnd)['finale']['eccesso']
    coppie = defaultdict(list)
    for (p1, _, r1), (p2, ini2, r2) in zip(righe, righe[1:]):
        if p1 == p2 and not ini2 and r1 and r2:
            coppie[p1].append((fin(r1[-1]), fin(r2[0])))
    tutte = [c for v in coppie.values() for c in v]
    vero = e285.mi(tutte)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for v in coppie.values():
            seconde = [b for _, b in v]
            rnd.shuffle(seconde)
            mes += [(a, b) for (a, _), b in zip(v, seconde)]
        nulli.append(e285.mi(mes))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    attraverso = vero - m
    return OrderedDict([('coppie_a_capo', len(tutte)), ('eccesso_dentro', dentro), ('eccesso_a_capo', attraverso), ('z_a_capo', attraverso / sd if sd else None),
                        ('r', attraverso / dentro if dentro else None)])


def main():
    rnd = random.Random(SEME)
    voy = [(r.pagina, bool(r.inizio_par), [w for w in r.parole if trascrizione.pulita(w)]) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    import corpo2
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    c, c2, freq, _, _, _ = e251.contesto()
    e233.SIGMA_POST = 0.04
    gen = [(p, ini, [w for w in ps if trascrizione.pulita(w)]) for p, ini, ps in e236.dopo(corpo2.genera_v2(c2, dict(e251.CONF, gamma=0.0, rip=0.5, phi=0.10), 7), freq, 107)]
    lat = [w.lower() for w in lingue.parole('Latin', max_caratteri=400000) if w.isalpha()][:30000]
    latino = [('p%d' % (i // 270), (i // 9) % 10 == 0, lat[i:i + 9]) for i in range(0, len(lat), 9)]
    ris = OrderedDict([('Voynich', misura(voy, e294.G_EVA, rnd)), ('generatore e288, seme 7', misura(gen, e294.G_EVA, rnd)),
                       ('controllo positivo: Bibbia latina in righe', misura(latino, list, rnd))])
    for n, r in ris.items():
        print('%-44s dentro %+.4f | a capo %+.4f (z %.1f) | r %.2f' % (n, r['eccesso_dentro'], r['eccesso_a_capo'], r['z_a_capo'] or 0, r['r'] or 0), flush=True)
    rv, rp = ris['Voynich'], ris['controllo positivo: Bibbia latina in righe']
    valido = (rp['r'] or 0) >= 0.5
    esito = ('non valido' if not valido else 'attraversa l\'a capo (come una lingua)' if (rv['r'] or 0) >= 0.5 and (rv['z_a_capo'] or 0) > 3
             else 'si ferma all\'a capo (abitudine di riga)' if (rv['r'] or 0) < 0.25 else 'incerto')
    json.dump(OrderedDict([('risultati', ris), ('valido', valido), ('esito', esito)]), open(os.path.join(RISULTATI, 'e295_a_capo.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)
    md = ['# e295 — La concordanza delle desinenze attraversa l\'a capo?', '', 'Eccesso di informazione mutua fra i finali di parole vicine dentro la riga (e285) e fra l\'ultima '
          'parola di una riga e la prima della seguente (stesso paragrafo e pagina). Preregistrazione: `preregistrazioni/e295.md`.', '',
          '| testo | coppie a capo | dentro la riga | attraverso l\'a capo | z | r |', '|---|---|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %.1f | %.2f |' % (n, r['coppie_a_capo'], r['eccesso_dentro'], r['eccesso_a_capo'], r['z_a_capo'] or 0, r['r'] or 0))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e295_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
