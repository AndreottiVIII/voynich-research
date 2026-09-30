# -*- coding: utf-8 -*-
"""Esperimento 5: quanto dura la somiglianza fra parole vicine?

Nell'esperimento 4 le parole di una stessa riga del Voynich si somigliano molto
piu' che in qualsiasi testo naturale. Qui misuriamo come la somiglianza cala
con la distanza: fra parole della stessa riga, della riga sotto, di due righe
sotto, e cosi' via fino a sei, sempre nella stessa pagina. Il termine di
paragone sono coppie prese a caso in tutto il testo.

Due controlli:
- alfabeto grossolano: fondiamo i segni che i trascrittori confondono piu'
  spesso (a/o/y, r/s, ch/ee, k/t, m/g, i gallows con panchina). Se l'effetto
  nascesse da letture incerte che cambiano da pagina a pagina, qui calerebbe;
- testi naturali tagliati in righe finte da 8 parole e pagine da 20 righe.

Scrive risultati/e05_righe.json, risultati/e05_righe.md e il grafico.
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import grafici, lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
DISTANZE = misure.DISTANZE
PAROLE_RIGA, RIGHE_PAGINA = misure.PAROLE_RIGA, misure.RIGHE_PAGINA

GROSSOLANO = [('ee', 'ch'), ('cth', 'ckh'), ('cfh', 'cph'), ('a', 'o'), ('y', 'o'),
              ('r', 's'), ('t', 'k'), ('g', 'm')]


def grossolano(parola):
    for vecchio, nuovo in GROSSOLANO:
        parola = parola.replace(vecchio, nuovo)
    return parola


def pagine_voynich(quale='ZL', trasforma=None, lingua=None):
    corrente = trascrizione.testo_corrente(trascrizione.leggi(quale), lingua=lingua)
    pagine = OrderedDict()
    for r in corrente:
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        if trasforma:
            ps = [trasforma(p) for p in ps]
        if ps:
            pagine.setdefault(r.pagina, []).append(ps)
    return list(pagine.values())


def serie():
    glifi = misure.divisore(misure.GLIFI_EVA)
    yield 'Voynich (ZL)', 'voynich', pagine_voynich('ZL'), glifi
    yield 'Voynich, segni confondibili fusi', 'voynich', pagine_voynich('ZL', grossolano), glifi
    yield 'Voynich, lingua A', 'voynich', pagine_voynich('ZL', lingua='A'), glifi
    yield 'Voynich, lingua B', 'voynich', pagine_voynich('ZL', lingua='B'), glifi
    yield 'Voynich (Takahashi)', 'voynich', pagine_voynich('IT'), glifi
    for chiave, nome in [('Latin', 'Bibbia latina'), ('Italian', 'Bibbia italiana'),
                         ('German', 'Bibbia tedesca'), ('Hebrew', 'Bibbia ebraica')]:
        yield nome, 'naturale', misure.pagine_finte(lingue.parole(chiave)[:35000]), None
    for nome in ['Catone, agricoltura e ricette', 'Varrone, agricoltura', 'Isidoro XVII, piante',
                 'Apicio, ricette di cucina']:
        yield nome, 'naturale', misure.pagine_finte(lingue.genere(nome)), None


def main():
    ris = {}
    for nome, gruppo, pagine, dividi in serie():
        r = misure.decadimento(pagine, dividi)
        ris[nome] = {'gruppo': gruppo, 'decadimento': r}
        print('%-34s ' % nome + '  '.join('d%d %.3f/x%.2f' % (d, v['distanza'], v['identiche'] or 0)
                                         for d, v in r.items()))
    with open(os.path.join(RISULTATI, 'e05_righe.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)
    disegna(ris)


def scrivi_tabella(ris):
    intest = ' | '.join('d=%d' % d for d in DISTANZE)
    out = ['# Esperimento 5: quanto dura la somiglianza', '',
           'Distanza di edit media fra due parole diverse, la prima in una riga e la seconda '
           'd righe più sotto nella stessa pagina (d=0: stessa riga), divisa per la distanza '
           'fra due parole a caso del testo. Sotto 1 = si somigliano più del caso. '
           'Per i testi naturali: righe finte da %d parole, pagine da %d righe.' % (PAROLE_RIGA, RIGHE_PAGINA),
           '', '| testo | ' + intest + ' |', '|---|' + '---|' * len(DISTANZE)]
    for nome, r in ris.items():
        out.append('| %s | ' % nome + ' | '.join('%.3f' % r['decadimento'][d]['distanza'] for d in DISTANZE) + ' |')
    with open(os.path.join(RISULTATI, 'e05_righe.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    mostrati = ['Voynich (ZL)', 'Voynich, segni confondibili fusi']
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.10, right=0.76, top=0.80, bottom=0.12)
        naturali = [n for n, r in ris.items() if r['gruppo'] == 'naturale']
        for i, nome in enumerate(naturali):
            ys = [100 * (1 - ris[nome]['decadimento'][d]['distanza']) for d in DISTANZE]
            ax.plot(list(DISTANZE), ys, color=t['contesto'], linewidth=1.2, alpha=0.8,
                    label='testi naturali (Bibbie, ricette, agricoltura, piante)' if i == 0 else None,
                    zorder=2)
        colori = [t['accento'], t['secondo']]
        brevi = {'Voynich (ZL)': 'Voynich', 'Voynich, segni confondibili fusi': 'Voynich, segni\nconfondibili fusi'}
        for nome, colore in zip(mostrati, colori):
            ys = [100 * (1 - ris[nome]['decadimento'][d]['distanza']) for d in DISTANZE]
            ax.plot(list(DISTANZE), ys, color=colore, linewidth=2, marker='o', markersize=5,
                    markeredgecolor=t['sfondo'], markeredgewidth=1.5, label=nome, zorder=3)
            ax.annotate(brevi[nome], (DISTANZE[-1], ys[-1]), xytext=(8, 0), textcoords='offset points',
                        fontsize=8.5, color=t['inchiostro'], va='center')
        ax.axhline(0, color=t['asse'], linewidth=1)
        ax.set_xticks(list(DISTANZE))
        ax.set_xticklabels(['stessa\nriga'] + ['+%d' % d for d in DISTANZE[1:]])
        ax.set_xlabel('distanza fra le righe, nella stessa pagina')
        ax.set_ylabel('somiglianza in più rispetto al caso (%)')
        ax.legend(loc='center right', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t,
                       'Nel Voynich le parole della stessa pagina si somigliano',
                       'Quanto due parole diverse si somigliano più di due parole qualsiasi del testo,\n'
                       'a seconda di quante righe le separano. I testi naturali restano vicino a zero.')
        grafici.salva(fig, RISULTATI, 'e05_righe', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv:
        with open(os.path.join(RISULTATI, 'e05_righe.json'), encoding='utf-8') as f:
            dati = json.load(f)
        for r in dati.values():   # json trasforma le chiavi intere in stringhe
            r['decadimento'] = {int(k): v for k, v in r['decadimento'].items()}
        disegna(dati)
    else:
        main()
