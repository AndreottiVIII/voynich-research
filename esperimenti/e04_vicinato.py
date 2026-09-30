# -*- coding: utf-8 -*-
"""Esperimento 4: le parole vicine si copiano?

Nel Voynich la stessa parola si ripete subito piu' spesso del caso, e due parole
vicine si somigliano piu' di due parole qualsiasi. Ma il vocabolario del Voynich
cambia da pagina a pagina, e questo da solo rende simili le parole della stessa
pagina. Qui il paragone e' interno: le coppie adiacenti contro coppie prese a
caso nella stessa riga, nella stessa pagina, o in un tratto di testo lungo come
una riga (8 parole) o come una pagina (150 parole). Per le lingue, che non hanno
righe del manoscritto, si usano i tratti di lunghezza fissa.

Scrive risultati/e04_vicinato.json e risultati/e04_vicinato.md.
"""
import json, os, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
N_LINGUE = 30000
BLOCCHI = (8, 150)


def per_pagina(righe):
    pagine = OrderedDict()
    for r in righe:
        pagine.setdefault(r.pagina, []).extend(p for p in r.parole if trascrizione.pulita(p))
    return list(pagine.values())


def misura_voynich(quale):
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi(quale))
    parole = trascrizione.parole(corrente)
    out = {'parole': len(parole)}
    out['riga'] = misure.vicinato(trascrizione.righe_di_parole(corrente), glifi)
    out['pagina'] = misure.vicinato(per_pagina(corrente), glifi)
    for b in BLOCCHI:
        out['blocco_%d' % b] = misure.vicinato(misure.a_blocchi(parole, b), glifi)
    return out


def misura_parole(parole):
    out = {'parole': len(parole)}
    for b in BLOCCHI:
        out['blocco_%d' % b] = misure.vicinato(misure.a_blocchi(parole, b))
    return out


def main():
    ris = {'voynich': {}, 'latino_tecnico': {}, 'lingue': {}}
    for q in ('ZL', 'IT'):
        ris['voynich'][q] = r = misura_voynich(q)
        for k in ('riga', 'pagina', 'blocco_8', 'blocco_150'):
            print('Voynich %s %-10s identiche x%.2f  distanza %.3f  | grappolo: identiche x%.2f  distanza %.3f' % (
                q, k, r[k]['identiche_rapporto'], r[k]['distanza_rapporto'],
                r[k]['grappolo_identiche'], r[k]['grappolo_distanza']))
    for nome in lingue.GENERI:
        ris['latino_tecnico'][nome] = r = misura_parole(lingue.genere(nome))
        print('%-36s identiche x%.2f / x%.2f  distanza %.3f / %.3f | grappolo 8: x%.2f %.3f' % (
            nome, r['blocco_8']['identiche_rapporto'], r['blocco_150']['identiche_rapporto'],
            r['blocco_8']['distanza_rapporto'], r['blocco_150']['distanza_rapporto'],
            r['blocco_8']['grappolo_identiche'], r['blocco_8']['grappolo_distanza']))
    for chiave, meta in sorted(lingue.indice().items()):
        if meta['tipo_scrittura'] not in ('alfabeto', 'abjad') or chiave.endswith('-tok'):
            continue
        parole = lingue.parole(chiave)[:N_LINGUE]
        if len(parole) < N_LINGUE:
            continue
        r = misura_parole(parole)
        r.update({k: meta[k] for k in ('lingua', 'tipo_scrittura')})
        ris['lingue'][chiave] = r
    with open(os.path.join(RISULTATI, 'e04_vicinato.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def riassunto(valori):
    valori = sorted(valori)
    return '%.3f – %.3f (mediana %.3f)' % (valori[0], valori[-1], statistics.median(valori))


def scrivi_tabella(ris):
    L = ris['lingue'].values()
    out = ['# Esperimento 4: le parole vicine si copiano?', '',
           'Coppie di parole adiacenti contro coppie prese a caso **nello stesso blocco**.',
           '"Identiche ×": quante volte più spesso le vicine sono la stessa parola.',
           '"Distanza": distanza di edit fra vicine diverse, diviso quella fra coppie a caso '
           'del blocco; sotto 1 le vicine si somigliano di più.',
           'Le ultime due colonne ("grappolo") confrontano invece le coppie a caso nel blocco con '
           'le coppie a caso in tutto il testo: dicono quanto il vocabolario di una riga o di una '
           'pagina è omogeneo rispetto al resto.', '',
           '| testo | blocco | vicine: identiche × | vicine: distanza | grappolo: identiche × | grappolo: distanza |',
           '|---|---|---|---|---|---|']
    for q, r in ris['voynich'].items():
        for k, nome in [('riga', 'riga vera'), ('pagina', 'pagina vera'),
                        ('blocco_8', '8 parole'), ('blocco_150', '150 parole')]:
            out.append('| **Voynich %s** | %s | %.2f | %.3f | %.2f | %.3f |' % (
                q, nome, r[k]['identiche_rapporto'], r[k]['distanza_rapporto'],
                r[k]['grappolo_identiche'], r[k]['grappolo_distanza']))
    for nome, r in ris['latino_tecnico'].items():
        for b in BLOCCHI:
            k = 'blocco_%d' % b
            out.append('| %s | %d parole | %.2f | %.3f | %.2f | %.3f |' % (
                nome, b, r[k]['identiche_rapporto'], r[k]['distanza_rapporto'],
                r[k]['grappolo_identiche'], r[k]['grappolo_distanza']))
    for b in BLOCCHI:
        k = 'blocco_%d' % b
        out.append('| %d Bibbie (alfabeto e abjad), intervallo | %d parole | %s | %s | %s | %s |' % (
            len(ris['lingue']), b,
            riassunto([r[k]['identiche_rapporto'] for r in L]),
            riassunto([r[k]['distanza_rapporto'] for r in L]),
            riassunto([r[k]['grappolo_identiche'] for r in L]),
            riassunto([r[k]['grappolo_distanza'] for r in L])))
    with open(os.path.join(RISULTATI, 'e04_vicinato.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
