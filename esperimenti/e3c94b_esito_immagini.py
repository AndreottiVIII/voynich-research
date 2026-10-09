# -*- coding: utf-8 -*-
"""Esperimento e3c94b: esito del controllo sulle immagini dalle letture (risultati/e3c94_letture.json) e dalla soglia
del campione (risultati/e3c94_campione.json), con i criteri di preregistrazioni/e3c94.md.

Scrive risultati/e3c94_controllo_immagini.json e .md.
"""
import json, os
from collections import Counter, OrderedDict

from scipy.stats import beta

QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = os.path.join(QUI, '..', 'risultati')


def cp(k, n):
    """Intervallo di Clopper-Pearson al 95%."""
    basso = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    alto = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return basso, alto


def main():
    c = json.load(open(os.path.join(RISULTATI, 'e3c94_campione.json'), encoding='utf-8'))
    l = json.load(open(os.path.join(RISULTATI, 'e3c94_letture.json'), encoding='utf-8'))
    s = c['soglia']
    a = Counter(x['classe'] for x in l['A'].values())
    n = len(l['A']) - a['illeggibile']
    k, i = a['q non trascritta'], a['incerta']
    b_ok = sum(1 for x in l['B'].values() if x['classe'] == 'q visibile')
    ic_k, ic_ki = cp(k, n), cp(k + i, n)
    if b_ok < 3:
        esito = 'non decidibile con queste immagini'
    elif ic_k[1] < s:
        esito = ('la caduta della q dopo il disegno non è (tutta) un effetto della trascrizione' +
                 (' (netto)' if ic_ki[1] < s else ' (probabile: con le incerte il limite alto supera la soglia)'))
    elif k / n >= s:
        esito = 'la caduta potrebbe essere tutta trascrizione'
    else:
        esito = 'incerto'
    if k >= 1:
        esito += '; una parte è trascrizione'
    cc = Counter(x['classe'] for x in l['C'].values())
    out = OrderedDict([('soglia', s), ('p_mezzo', c['p_mezzo']), ('p_salto', c['p_salto']), ('A', dict(a)), ('n', n), ('k', k), ('incerte', i),
                       ('IC95_k', ic_k), ('IC95_k_piu_incerte', ic_ki), ('B_q_visibile', b_ok), ('C', dict(cc)), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c94_controllo_immagini.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c94 — Controllo a campione sulle immagini', '',
          'Preregistrazione: `preregistrazioni/e3c94.md`. Campione: `risultati/e3c94_campione.md`; regioni: `risultati/e3c94_ritagli.json`; letture: `risultati/e3c94_letture.json`.', '',
          'Quota di *qo-* davanti a gallows: in mezzo alla riga %.3f, dopo il salto del disegno %.3f. Soglia s = %.3f.' % (c['p_mezzo'], c['p_salto'], s), '',
          '| gruppo | risultato |', '|---|---|',
          '| A, parole *o*- dopo il disegno (%d) | nessuna q %d, q non trascritta %d, incerte %d, illeggibili %d |' % (
              len(l['A']), a['nessuna q'], k, i, a['illeggibile']),
          '| k/n, IC 95%% | %d/%d, %.3f – %.3f |' % (k, n, ic_k[0], ic_k[1]),
          '| (k + incerte)/n, IC 95%% | %d/%d, %.3f – %.3f |' % (k + i, n, ic_ki[0], ic_ki[1]),
          '| B, controllo positivo | q visibile in %d su %d |' % (b_ok, len(l['B'])),
          '| C, *-m* di fine riga | %s |' % ', '.join('%s %d' % kv for kv in cc.items()), '',
          'Esito: **%s**.' % esito, '']
    for g in ('A', 'B', 'C'):
        for kk, x in l[g].items():
            md.append('- %s: %s — %s' % (kk, x['classe'], x['nota']))
    open(os.path.join(RISULTATI, 'e3c94_controllo_immagini.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
