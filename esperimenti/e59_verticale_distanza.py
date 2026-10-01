# -*- coding: utf-8 -*-
"""Esperimento 59: la traccia verticale dell'e58 al variare della distanza d fra le righe.

Parole interne (senza la prima e l'ultima di ogni riga), posizione assoluta, 500 rimescolamenti;
la riga di confronto e' quella d righe sopra nella stessa pagina, d = 1, 2, 3, 5.
Preregistrazione: preregistrazioni/e59.md. Scrive risultati/e59_verticale_distanza.json e .md.
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e22_timm_schinner as e22
import e58_parola_sopra as e58
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
DISTANZE = (1, 2, 3, 5)
e58.RIMESCOLAMENTI = 500


def coppie_a_distanza(pagine, dividi, d):
    out = []
    for p in pagine:
        p = [[tuple(dividi(w)) if dividi else tuple(w) for w in r][1:-1] for r in p]
        for i in range(d, len(p)):
            if len(p[i]) >= 2 and len(p[i - d]) >= 2:
                out.append((p[i], p[i - d]))
    return out


def main():
    D = e58.D
    testi = OrderedDict()
    testi['Voynich'] = (pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL'))), D)
    testi['Voynich, Currier B'] = (pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')), D)
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = (e58.da_file(os.path.join(e22.LAVORO, 'seme_%d' % s, 'generate',
                                                                          'generated_text.txt')), D)
    testi['Bibbia latina (pagine finte)'] = (misure.pagine_finte(lingue.parole('Latin')[:35000]), None)
    ris = OrderedDict()
    for nome, (pagine, dividi) in testi.items():
        ris[nome] = OrderedDict()
        for d in DISTANZE:
            r = e58.prova(coppie_a_distanza(pagine, dividi, d), False)
            ris[nome][d] = r
        print('%-32s %s' % (nome, '  '.join('d%d %.3f (z %.1f)' % (d, ris[nome][d]['rapporto'], ris[nome][d]['z'])
                                           for d in DISTANZE)), flush=True)
    with open(os.path.join(RISULTATI, 'e59_verticale_distanza.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e59 — La traccia verticale con la distanza fra le righe', '',
           'Rapporto fra la somiglianza con la parola nella stessa posizione della riga d righe sopra e la '
           'somiglianza con le altre parole di quella riga (parole interne). Tra parentesi z rispetto a 500 '
           'rimescolamenti. Preregistrazione: `preregistrazioni/e59.md`.', '',
           '| testo | ' + ' | '.join('d = %d' % d for d in DISTANZE) + ' | eccesso d=2 / d=1 |',
           '|---|' + '---|' * (len(DISTANZE) + 1)]
    for nome, r in ris.items():
        e1, e2 = r[1]['rapporto'] - 1, r[2]['rapporto'] - 1
        out.append('| %s | %s | %s |' % (nome, ' | '.join('%.3f (%.1f)' % (r[d]['rapporto'], r[d]['z']) for d in DISTANZE),
                                         '%.2f' % (e2 / e1) if e1 > 0 else '—'))
    with open(os.path.join(RISULTATI, 'e59_verticale_distanza.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
