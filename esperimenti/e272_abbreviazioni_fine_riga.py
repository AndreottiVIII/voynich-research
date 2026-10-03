# -*- coding: utf-8 -*-
"""Esperimento 272: il tronco (parola senza l'ultima unita') delle parole in -m a fine riga e' piu' spesso l'inizio di una
parola frequente piu' lunga che per le parole in -m interne? Controllo: -y.

Preregistrazione: preregistrazioni/e272.md. Scrive risultati/e272_abbreviazioni_fine_riga.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

from scipy.stats import fisher_exact

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_FREQ, PIU_LUNGA = 5, 2


def main():
    righe = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))]
    righe = [r for r in righe if len(r) >= 2]
    voc = Counter(w for r in righe for w in r)
    lunghe = [tuple(D(w)) for w, c in voc.items() if c >= MIN_FREQ]
    _comp = {}

    def completabile(tronco, fine):
        k = (tronco, fine)
        if k not in _comp:
            n = len(tronco)
            _comp[k] = any(len(u) >= n + PIU_LUNGA and u[:n] == tronco and u[-1] != fine for u in lunghe)
        return _comp[k]

    ris = OrderedDict()
    for fine in ('m', 'y'):
        conta = {'F': [0, 0], 'I': [0, 0]}
        for r in righe:
            for j, w in enumerate(r):
                u = tuple(D(w))
                if len(u) < 2 or u[-1] != fine:
                    continue
                g = 'F' if j == len(r) - 1 else ('I' if j > 0 else None)
                if g:
                    conta[g][0] += completabile(u[:-1], fine)
                    conta[g][1] += 1
        qF, qI = conta['F'][0] / conta['F'][1], conta['I'][0] / conta['I'][1]
        p = float(fisher_exact([[conta['F'][0], conta['F'][1] - conta['F'][0]], [conta['I'][0], conta['I'][1] - conta['I'][0]]], alternative='greater')[1])
        ris['-' + fine] = OrderedDict([('fine_riga', conta['F'][1]), ('interne', conta['I'][1]), ('completabili_fine', qF), ('completabili_interne', qI),
                                       ('rapporto', qF / qI if qI else None), ('p', p)])
        print('-' + fine, dict(ris['-' + fine]), flush=True)
    m, y = ris['-m'], ris['-y']
    esito = ('abbreviazione a fine riga' if (m['rapporto'] or 0) >= 1.3 and m['p'] < 0.01 and m['rapporto'] > (y['rapporto'] or 0)
             else 'nessun indizio' if (m['rapporto'] or 0) <= 1.1 or m['p'] > 0.05 else 'incerto')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e272_abbreviazioni_fine_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e272 — Le parole in -m a fine riga sono abbreviazioni?', '',
          'Tronco completabile = inizio di una parola attestata almeno %d volte, più lunga di almeno %d unità, che non finisce con la stessa unità. '
          'Preregistrazione: `preregistrazioni/e272.md`.' % (MIN_FREQ, PIU_LUNGA), '',
          '| terminazione | a fine riga | interne | completabili (fine) | completabili (interne) | rapporto | p |', '|---|---|---|---|---|---|---|']
    for k, r in list(ris.items())[:2]:
        md.append('| %s | %d | %d | %.3f | %.3f | %.2f | %.2g |' % (k, r['fine_riga'], r['interne'], r['completabili_fine'], r['completabili_interne'], r['rapporto'] or 0, r['p']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e272_abbreviazioni_fine_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
