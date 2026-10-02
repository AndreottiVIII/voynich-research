# -*- coding: utf-8 -*-
"""Esperimento 198: quota di multinsiemi di segni realizzati in piu' ordini (frequenti), Voynich contro lingue,
controllo "a ordinamento" e generatore.

Preregistrazione: preregistrazioni/e198.md. Scrive risultati/e198_ordinamento.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e186_nulli_acrostici as e186

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def quota(parole, dividi):
    freq = Counter(parole)
    classi = defaultdict(set)
    for w, c in freq.items():
        if c >= 2:
            classi[tuple(sorted(dividi(w)))].add(w)
    n = len(classi)
    multi = sum(1 for v in classi.values() if len(v) >= 2)
    esempi = [sorted(v) for v in classi.values() if len(v) >= 2][:12]
    return OrderedDict([('classi', n), ('con_piu_ordini', multi), ('quota', multi / n if n else None), ('esempi', esempi)])


def main():
    voy = [w for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))) if trascrizione.pulita(w)]
    n = len(voy)
    lat = lingue.parole('Latin')[:n]
    ita = lingue.parole('Italian')[:n]
    gen = [w for _, _, ps in e186.generatore(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))) for w in ps if trascrizione.pulita(w)]
    lettere = lambda w: list(w)
    ris = OrderedDict()
    ris['Voynich'] = quota(voy, D)
    ris['latino'] = quota(lat, lettere)
    ris['italiano'] = quota(ita, lettere)
    ris['controllo: latino ordinato'] = quota([''.join(sorted(w)) for w in lat], lettere)
    ris['generatore e180'] = quota(gen, D)
    for k, r in ris.items():
        print('%-28s classi %d, con più ordini %d, quota %.4f | esempi %s' % (k, r['classi'], r['con_piu_ordini'], r['quota'] or 0, r['esempi'][:5]), flush=True)
    v = ris['Voynich']['quota']
    esito = 'compatibile con un cifrario a ordinamento' if v <= 0.02 else 'non compatibile'
    ris['esito'] = esito
    print(esito)
    with open(os.path.join(RISULTATI, 'e198_ordinamento.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e198 — Un cifrario "a ordinamento"?', '', 'Quota di multinsiemi di segni con almeno due ordini frequenti. Preregistrazione: `preregistrazioni/e198.md`.', '',
           '| testo | classi | con più ordini | quota | esempi |', '|---|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %d | %.4f | %s |' % (k, r['classi'], r['con_piu_ordini'], r['quota'] or 0, '; '.join('/'.join(e) for e in r['esempi'][:4])))
    out += ['', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e198_ordinamento.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
