# -*- coding: utf-8 -*-
"""Esperimento 300b: la somiglianza fra pagine consecutive dell'e300 con le permutazioni dentro sezione x lingua di Currier.

Preregistrazione: preregistrazioni/e300b.md. Scrive risultati/e300b_ordine_lingua.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e300_ordine_scribi as e300

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            x = per.setdefault(r.pagina, {'strato': '%s-%s' % (r.sezione, r.lingua or '?'), 'parole': []})
            x['parole'] += [w for w in r.parole if trascrizione.pulita(w)]
    pagine = [(p, x['strato'], x['parole']) for p, x in per.items() if len(x['parole']) >= e300.MIN_PAROLE]
    r = e300.ordine(pagine, random.Random(300))
    z = r['z'] or 0
    esito = 'traccia d\'ordine oltre la lingua' if z > 3 else ('spiegata dalla lingua' if z < 1 else 'incerto')
    print('A %.4f nullo %.4f z %.1f | Spearman %.3f -> %s' % (r['A'], r['nullo'], z, r['spearman_distanza_somiglianza'] or 0, esito), flush=True)
    json.dump(OrderedDict([('risultato', r), ('esito', esito)]), open(os.path.join(RISULTATI, 'e300b_ordine_lingua.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    open(os.path.join(RISULTATI, 'e300b_ordine_lingua.md'), 'w', encoding='utf-8').write(
        '# e300b — Ordine delle pagine dentro sezione e lingua\n\nPreregistrazione: `preregistrazioni/e300b.md`.\n\n'
        'Coppie consecutive nello stesso strato (sezione × lingua): A %.4f contro %.4f del nullo, z %.1f; Spearman distanza-somiglianza %.3f.\n\n'
        'Esito: **%s**.\n' % (r['A'], r['nullo'], z, r['spearman_distanza_somiglianza'] or 0, esito))


if __name__ == '__main__':
    main()
