# -*- coding: utf-8 -*-
"""Esperimento 13: a quali lingue somiglia il Voynich, tutto considerato?

Mettiamo insieme le misure degli esperimenti precedenti, per le Bibbie in
alfabeto o abjad, e cerchiamo le lingue piu' vicine al Voynich: ogni misura e'
standardizzata sulle lingue (quante deviazioni standard dalla media), e la
distanza e' quella euclidea. Le misure:

- h1, h2: incertezza su una lettera e sulla successiva (esperimento 1);
- lunghezza delle parole, parole diverse su parole totali, hapax (esp. 2);
- ripetizioni immediate rispetto alla riga (esp. 9);
- somiglianza fra parole della stessa riga (esp. 9);
- legame attraverso lo spazio e prevedibilita' dello spazio (esp. 11).

La somiglianza nella riga e' l'unica misura in cui nessuna lingua si avvicina:
la distanza si calcola con e senza, per vedere chi e' vicino sul resto.

Legge i risultati degli esperimenti 1, 2, 9, 11; scrive e13_profilo.json e .md.
"""
import json, math, os, statistics, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue

RISULTATI = os.path.join(QUI, '..', 'risultati')
MISURE = [('h1', 'h1'), ('h2', 'h2'), ('lung_media', 'lunghezza parole'),
          ('tipi_su_parole', 'parole diverse'), ('hapax', 'hapax'),
          ('identiche_log', 'ripetizioni immediate (log)'), ('confine', 'legame attraverso lo spazio'),
          ('spazio_spiegato_1', 'spazio prevedibile'), ('somiglianza_riga', 'somiglianza nella riga')]


def carica(nome):
    with open(os.path.join(RISULTATI, nome), encoding='utf-8') as f:
        return json.load(f)


def main():
    e01, e02, e09, e11 = (carica('e01_prevedibilita.json'), carica('e02_impronta.json'),
                          carica('e09_sintesi.json'), carica('e11_spazi.json'))
    indice = lingue.indice()
    righe = {}
    for chiave, meta in indice.items():
        nome = 'Bibbia: ' + meta['lingua']
        if chiave not in e01['lingue'] or chiave not in e02['lingue_30000']:
            continue
        if nome not in e09['naturali'] or nome not in e11['naturali']:
            continue
        righe[meta['lingua']] = {
            'famiglia': meta['famiglia'],
            'h1': e01['lingue'][chiave]['h1'], 'h2': e01['lingue'][chiave]['h2'],
            'lung_media': e02['lingue_30000'][chiave]['lung_media'],
            'tipi_su_parole': e02['lingue_30000'][chiave]['tipi_su_parole'],
            'hapax': e02['lingue_30000'][chiave]['hapax'],
            'identiche_log': math.log(max(e09['naturali'][nome]['identiche_vs_riga'], 0.01)),
            'somiglianza_riga': e09['naturali'][nome]['somiglianza_riga'],
            'confine': e11['naturali'][nome]['confine'],
            'spazio_spiegato_1': e11['naturali'][nome]['spazio_spiegato_1'],
        }
    v = {
        'h1': e01['voynich']['ZL EVA, glifi fusi']['h1'], 'h2': e01['voynich']['ZL EVA, glifi fusi']['h2'],
        'lung_media': e02['voynich']['ZL']['lung_media'], 'tipi_su_parole': e02['voynich']['ZL']['tipi_su_parole'],
        'hapax': e02['voynich']['ZL']['hapax'],
        'identiche_log': math.log(e09['voynich']['Voynich (Zandbergen-Landini)']['identiche_vs_riga']),
        'somiglianza_riga': e09['voynich']['Voynich (Zandbergen-Landini)']['somiglianza_riga'],
        'confine': e11['voynich_e_cifrati']['Voynich (Zandbergen-Landini, glifi)']['confine'],
        'spazio_spiegato_1': e11['voynich_e_cifrati']['Voynich (Zandbergen-Landini, glifi)']['spazio_spiegato_1'],
    }
    media = {k: statistics.mean(r[k] for r in righe.values()) for k, _ in MISURE}
    dev = {k: statistics.stdev(r[k] for r in righe.values()) for k, _ in MISURE}
    z = lambda r, k: (r[k] - media[k]) / dev[k]
    ris = {'voynich_z': {k: z(v, k) for k, _ in MISURE}, 'lingue': len(righe)}
    for con in (True, False):
        chiavi = [k for k, _ in MISURE if con or k != 'somiglianza_riga']
        dist = sorted((math.sqrt(sum((z(r, k) - z(v, k)) ** 2 for k in chiavi)), n, r['famiglia'])
                      for n, r in righe.items())
        # quanto e' lontano il Voynich dalla nuvola: distanza dal vicino piu' vicino,
        # confrontata con la stessa distanza per ogni lingua
        vicini_lingue = []
        for n, r in righe.items():
            vicini_lingue.append(min(math.sqrt(sum((z(r, k) - z(s, k)) ** 2 for k in chiavi))
                                     for m, s in righe.items() if m != n))
        vicini_lingue.sort()
        ris['con_somiglianza' if con else 'senza_somiglianza'] = {
            'piu_vicine': [{'lingua': n, 'famiglia': f, 'distanza': d} for d, n, f in dist[:12]],
            'distanza_voynich_dal_piu_vicino': dist[0][0],
            'distanza_dal_piu_vicino_fra_lingue': {'mediana': statistics.median(vicini_lingue),
                                                    'massimo': vicini_lingue[-1]},
        }
        print('%s la somiglianza nella riga:' % ('con' if con else 'senza'))
        for d, n, f in dist[:10]:
            print('   %.2f  %-28s %s' % (d, n, f))
        print('   distanza del Voynich dal vicino piu\' vicino %.2f; fra le lingue: mediana %.2f, massimo %.2f' % (
            dist[0][0], statistics.median(vicini_lingue), vicini_lingue[-1]))
    print('Voynich in deviazioni standard dalla media delle lingue:',
          {k: round(x, 1) for k, x in ris['voynich_z'].items()})
    # due componenti principali delle lingue, per il grafico
    import numpy as np
    chiavi = [k for k, _ in MISURE]
    nomi = list(righe)
    Z = np.array([[z(righe[n], k) for k in chiavi] for n in nomi])
    zv = np.array([z(v, k) for k in chiavi])
    _, _, vt = np.linalg.svd(Z - Z.mean(axis=0), full_matrices=False)
    P = (Z - Z.mean(axis=0)) @ vt[:2].T
    pv = (zv - Z.mean(axis=0)) @ vt[:2].T
    ris['piano'] = {'lingue': {n: [float(P[i, 0]), float(P[i, 1])] for i, n in enumerate(nomi)},
                    'voynich': [float(pv[0]), float(pv[1])]}
    with open(os.path.join(RISULTATI, 'e13_profilo.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)
    disegna(ris)


def disegna(ris):
    import grafici
    lingue_xy = ris['piano']['lingue']
    vx, vy = ris['piano']['voynich']
    vicine = [x['lingua'] for x in ris['con_somiglianza']['piu_vicine'][:3]]
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.12)
        xs = [p[0] for p in lingue_xy.values()]
        ys = [p[1] for p in lingue_xy.values()]
        ax.scatter(xs, ys, s=30, color=t['contesto'], edgecolor=t['sfondo'], linewidth=1.0,
                   label='lingue (Bibbia, alfabeto o abjad)', zorder=2)
        ax.scatter([vx], [vy], s=70, color=t['accento'], edgecolor=t['sfondo'], linewidth=1.5,
                   label='Voynich', zorder=3)
        ax.annotate('Voynich', (vx, vy), xytext=(8, 6), textcoords='offset points', fontsize=9,
                    color=t['inchiostro'])
        for n in vicine:
            x, y = lingue_xy[n]
            ax.annotate(n.split(' (')[0], (x, y), xytext=(6, -10), textcoords='offset points',
                        fontsize=8, color=t['secondario'])
        ax.set_xlabel('prima componente (le nove misure riassunte)')
        ax.set_ylabel('seconda componente')
        ax.legend(loc='lower left', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Il Voynich non somiglia a nessuna lingua',
                       'Nove misure insieme, riassunte su due assi. Le lingue formano una nuvola;\n'
                       'il Voynich sta fuori, più lontano di quanto una lingua lo sia da qualsiasi altra.')
        grafici.salva(fig, RISULTATI, 'e13_profilo', tema)


def scrivi_tabella(ris):
    out = ['# Esperimento 13: a quali lingue somiglia il Voynich', '',
           'Nove misure, standardizzate sulle %d Bibbie in alfabeto o abjad; distanza euclidea.' % ris['lingue'], '',
           '## Il Voynich, misura per misura', '',
           '| misura | deviazioni standard dalla media delle lingue |', '|---|---|']
    for k, nome in MISURE:
        out.append('| %s | %+.1f |' % (nome, ris['voynich_z'][k]))
    for chiave, titolo in (('con_somiglianza', 'Con tutte le misure'),
                           ('senza_somiglianza', 'Senza la somiglianza nella riga')):
        r = ris[chiave]
        out += ['', '## %s' % titolo, '',
                'Distanza del Voynich dalla lingua più vicina: **%.2f**. Per confronto, la distanza di ogni '
                'lingua dalla sua vicina più prossima: mediana %.2f, massimo %.2f.' % (
                    r['distanza_voynich_dal_piu_vicino'], r['distanza_dal_piu_vicino_fra_lingue']['mediana'],
                    r['distanza_dal_piu_vicino_fra_lingue']['massimo']), '',
                '| lingua | famiglia | distanza |', '|---|---|---|']
        out += ['| %s | %s | %.2f |' % (x['lingua'], x['famiglia'], x['distanza']) for x in r['piu_vicine']]
    with open(os.path.join(RISULTATI, 'e13_profilo.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
