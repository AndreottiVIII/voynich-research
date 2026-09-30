# -*- coding: utf-8 -*-
"""Esperimento 9: la sintesi in un grafico.

Due numeri per ogni testo, le due anomalie strutturali del Voynich:
- quanto spesso una parola ripete subito la precedente, rispetto a due parole
  prese a caso nella stessa riga (le lingue lo evitano: la grammatica non vuole
  "il il"; il Voynich no);
- quanto due parole diverse della stessa riga si somigliano nella grafia piu'
  di due parole qualsiasi del testo.
Testi naturali (Bibbie in alfabeto o abjad, testi tecnici latini), le codifiche
dell'esperimento 7, e il Voynich in due trascrizioni.

Scrive risultati/e09_sintesi.json, risultati/e09_sintesi.md e il grafico.
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import grafici, lingue, misure, trascrizione
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 35000


def due_numeri(pagine, dividi=None):
    righe = [riga for pag in pagine for riga in pag]
    vic = misure.vicinato(righe, dividi)
    dec = misure.decadimento(pagine, dividi, coppie_caso=100000, distanze=[0])
    return {'identiche_vs_riga': vic['identiche_rapporto'], 'somiglianza_riga': 1 - dec[0]['distanza']}


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    ris = {'voynich': OrderedDict(), 'naturali': OrderedDict(), 'codifiche': OrderedDict()}
    for q, nome in [('ZL', 'Voynich (Zandbergen-Landini)'), ('IT', 'Voynich (Takahashi)')]:
        ris['voynich'][nome] = due_numeri(pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi(q))), glifi)
        print(nome, ris['voynich'][nome])
    for chiave, meta in sorted(lingue.indice().items()):
        if meta['tipo_scrittura'] not in ('alfabeto', 'abjad') or chiave.endswith('-tok'):
            continue
        parole = lingue.parole(chiave)[:N]
        if len(parole) < N:
            continue
        ris['naturali']['Bibbia: ' + meta['lingua']] = due_numeri(misure.pagine_finte(parole))
    for nome in lingue.GENERI:
        ris['naturali'][nome] = due_numeri(misure.pagine_finte(lingue.genere(nome)))
    with open(os.path.join(RISULTATI, 'e07_codifiche.json'), encoding='utf-8') as f:
        e07 = json.load(f)['impronte']
    for nome, r in e07.items():
        if nome.startswith('Voynich') or 'in chiaro' in nome:
            continue
        ris['codifiche'][nome] = {'identiche_vs_riga': r['identiche_vs_riga'],
                                  'somiglianza_riga': r['somiglianza_riga']}
    with open(os.path.join(RISULTATI, 'e09_sintesi.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)
    disegna(ris)


def scrivi_tabella(ris):
    nat = list(ris['naturali'].values())
    fuori = [n for n, r in ris['naturali'].items() if r['identiche_vs_riga'] >= 0.8]
    out = ['# Esperimento 9: le due anomalie in sintesi', '',
           'Testi naturali: %d (Bibbie in alfabeto o abjad, 35.000 parole, e testi tecnici latini).' % len(nat),
           '', '| testo | identiche subito, rispetto alla riga | somiglianza nella riga |', '|---|---|---|']
    for gruppo in ('voynich', 'codifiche'):
        for nome, r in ris[gruppo].items():
            out.append('| %s | ×%.2f | %.1f%% |' % (nome, r['identiche_vs_riga'], 100 * r['somiglianza_riga']))
    ident = sorted(r['identiche_vs_riga'] for r in nat)
    somi = sorted(r['somiglianza_riga'] for r in nat)
    out += ['', 'Testi naturali: identiche subito da ×%.2f a ×%.2f (mediana ×%.2f); somiglianza '
            'nella riga da %.1f%% a %.1f%% (mediana %.1f%%).' % (
                ident[0], ident[-1], ident[len(ident) // 2], 100 * somi[0], 100 * somi[-1],
                100 * somi[len(somi) // 2]),
            'Testi naturali con ripetizioni immediate non evitate (×0,8 o più): %s.' % (', '.join(fuori) or 'nessuno')]
    with open(os.path.join(RISULTATI, 'e09_sintesi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=5.0)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.12)
        nat = list(ris['naturali'].values())
        ax.scatter([r['identiche_vs_riga'] for r in nat], [100 * r['somiglianza_riga'] for r in nat],
                   s=30, color=t['contesto'], edgecolor=t['sfondo'], linewidth=1.0,
                   label='testi naturali (Bibbie in ~90 lingue, testi tecnici latini)', zorder=2)
        cod = list(ris['codifiche'].values())
        ax.scatter([r['identiche_vs_riga'] for r in cod], [100 * r['somiglianza_riga'] for r in cod],
                   s=38, marker='s', color=t['secondo'], edgecolor=t['sfondo'], linewidth=1.0,
                   label='testi veri "tokenizzati" (codici, varianti, sillabe, stile di pagina)', zorder=3)
        voy = list(ris['voynich'].items())
        ax.scatter([r['identiche_vs_riga'] for _, r in voy], [100 * r['somiglianza_riga'] for _, r in voy],
                   s=70, color=t['accento'], edgecolor=t['sfondo'], linewidth=1.5, label='Voynich', zorder=4)
        ax.annotate('Voynich', (voy[0][1]['identiche_vs_riga'], 100 * voy[0][1]['somiglianza_riga']),
                    xytext=(10, 6), textcoords='offset points', fontsize=9, color=t['inchiostro'])
        ind = ris['naturali'].get('Bibbia: Indonesian')
        if ind:
            ax.annotate('indonesiano\n(plurali raddoppiati)', (ind['identiche_vs_riga'], 100 * ind['somiglianza_riga']),
                        xytext=(0, 12), textcoords='offset points', fontsize=8, color=t['secondario'], ha='center')
        stile = [r for n, r in ris['codifiche'].items() if 'stile' in n]
        if stile:
            alto = max(stile, key=lambda r: r['somiglianza_riga'])
            ax.annotate('codici con "stile di pagina"', (alto['identiche_vs_riga'], 100 * alto['somiglianza_riga']),
                        xytext=(-10, 0), textcoords='offset points', fontsize=8, color=t['secondario'],
                        ha='right', va='center')
        ax.axvline(1, color=t['asse'], linewidth=1, zorder=1)
        ax.annotate('come il caso', (1, ax.get_ylim()[1]), xytext=(4, -12), textcoords='offset points',
                    fontsize=8, color=t['muto'])
        ax.set_xscale('log')
        ax.set_xticks([0.01, 0.03, 0.1, 0.3, 1, 3])
        ax.set_xticklabels(['×0,01', '×0,03', '×0,1', '×0,3', '×1', '×3'])
        ax.set_xlabel('parola identica alla precedente, rispetto a due parole a caso della stessa riga')
        ax.set_ylabel('somiglianza fra parole della stessa riga (%)')
        ax.legend(loc='center left', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Nessuna delle codifiche provate somiglia al Voynich',
                       'A destra: le ripetizioni immediate non sono evitate. In alto: le parole vicine si somigliano.\n'
                       'Il Voynich ha le due cose insieme; le lingue e le loro codifiche no.')
        grafici.salva(fig, RISULTATI, 'e09_sintesi', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv:
        with open(os.path.join(RISULTATI, 'e09_sintesi.json'), encoding='utf-8') as f:
            disegna(json.load(f))
    else:
        main()
