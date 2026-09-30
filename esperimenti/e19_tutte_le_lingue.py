# -*- coding: utf-8 -*-
"""Esperimento 19: il risolutore dell'esperimento 17 su tutte le lingue.

L'esperimento 17 prova quattordici lingue scelte (quelle plausibili per un
codice europeo del Quattrocento, piu' tre lontane che per profilo gli
somigliano). Qui la stessa prova su tutte le Bibbie del corpus scritte in un
alfabeto o in un abjad, con al massimo 32 lettere (oltre, la tabella del
modello a 5-grammi diventa troppo grande): se il Voynich fosse una
sostituzione di una lingua "inattesa", qui si vedrebbe.

Per ogni lingua, con il Voynich letto a segni EVA (una riga su due, circa
78.000 segni, per stare nei tempi):
- il testo in chiaro (tetto) e il controllo positivo (lo stesso testo cifrato
  con 26 simboli, come il Voynich, e risolto: si ritenta una ripartenza alla
  volta finche' la chiave torna, al massimo quattro volte, e tutto il resto ha
  poi almeno altrettante ripartenze);
- il controllo negativo (un'altra lingua cifrata allo stesso modo: il
  finlandese, o il latino per le lingue uraliche);
- il Voynich, e il Voynich letto da destra a sinistra (ogni riga al
  contrario: se la scrittura andasse all'indietro, il modello della lingua
  non la riconoscerebbe nell'altro verso);
- il Plinio cifrato col Naibbe, letto a segni EVA: ha la "grana" del Voynich
  (segni prevedibili, parole brevi e regolari) ma non e' una sostituzione di
  nessuna lingua. Dice quanto sale il punteggio per la sola grana: un testo
  cosi' regolare si piega al modello di qualsiasi lingua un po' meglio di un
  testo in un'altra lingua.

Scrive risultati/e19_tutte_le_lingue.json e .md; con --grafico il grafico.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e17_ricottura as e17

RISULTATI = os.path.join(QUI, '..', 'risultati')
MASSIMO_LETTERE = 32
MINIMO_PAROLE = 150000
RIPARTENZE = int(os.environ.get('RIPARTENZE', '2'))
MASSIMO_RIPARTENZE = 4


def candidate():
    """Le lingue del corpus in alfabeto o abjad, con testo abbastanza lungo."""
    out = OrderedDict()
    for chiave, meta in lingue.indice().items():
        if meta['tipo_scrittura'] not in ('alfabeto', 'abjad') or chiave.endswith('-tok'):
            continue
        ps = lingue.parole(chiave)
        if len(ps) < MINIMO_PAROLE or len(e17.alfabeto(ps)) > MASSIMO_LETTERE:
            continue
        out[chiave] = meta
    return out


def una_lingua(argomenti):
    chiave_l, meta, voynich, naibbe = argomenti
    rnd = random.Random('e19-' + chiave_l)
    testo, add, lettere, modello, lessico = e17.prepara_lingua(chiave_l)
    altra = 'Latin' if meta['famiglia'] == 'Uralic' else e17.STRANIERO
    altro = lingue.parole(altra)
    altro = e17.pulisci(altro, e17.alfabeto(altro))
    simboli = len({u for x in voynich for u in x})
    L = sum(map(len, voynich))
    chiaro = e17.in_righe(e17.prendi(testo[add:], L))
    r = OrderedDict([('lingua', meta['lingua']), ('famiglia', meta['famiglia']), ('lettere', len(modello.lettere)),
                     ('lingua del controllo negativo', altra)])
    r['tetto (testo in chiaro)'] = e17.giudica([''.join(x) for x in chiaro], modello, lessico)
    cif, vera = e17.cifra_abbinata(chiaro, simboli, rnd)
    # il controllo positivo si ritenta, una ripartenza alla volta, finche' la chiave torna (al massimo
    # quattro volte); tutto il resto ha poi almeno altrettante ripartenze, cosi' il Voynich non e'
    # svantaggiato rispetto al controllo
    migliore = None
    for k in range(1, MASSIMO_RIPARTENZE + 1):
        v = e17.attacca(cif, modello, lessico, rnd, vera=vera, ripartenze=1)
        if migliore is None or v['obiettivo'] > migliore['obiettivo']:
            migliore = v
        if migliore['chiave_giusta'] >= 0.9:
            break
    migliore['ripartenze_usate'] = k
    r['controllo positivo'] = migliore
    ripartenze = max(RIPARTENZE, k)
    cif, _ = e17.cifra_abbinata(e17.in_righe(e17.prendi(altro, L)), simboli, rnd)
    r['controllo negativo'] = e17.attacca(cif, modello, lessico, rnd, ripartenze=ripartenze)
    r['Voynich'] = e17.attacca(voynich, modello, lessico, rnd, ripartenze=ripartenze)
    r['Voynich al contrario'] = e17.attacca([x[::-1] for x in voynich], modello, lessico, rnd,
                                            ripartenze=ripartenze)
    r['Naibbe'] = e17.attacca(naibbe, modello, lessico, rnd, ripartenze=ripartenze)
    for k in ('controllo positivo', 'controllo negativo', 'Voynich', 'Voynich al contrario', 'Naibbe'):
        e17.stampa(meta['lingua'][:10], k, r[k])
    return chiave_l, r


def posizione(r, chiave='Voynich'):
    pos, neg = r['controllo positivo']['punteggio'], r['controllo negativo']['punteggio']
    return (r[chiave]['punteggio'] - neg) / (pos - neg)


def riuscito(r):
    """Il controllo positivo e' riuscito: solo allora la posizione vuol dire qualcosa."""
    return r['controllo positivo'].get('chiave_giusta', 0) >= 0.9


def main():
    # una riga su due, per stare nei tempi (settanta lingue): circa 78.000 segni, sempre molti
    # di piu' di quanti ne servono al risolutore per rompere i controlli
    voynich = e17.modi_voynich()['segni EVA'][::2]
    naibbe = e17.in_unita(e17.naibbe_righe(), e17.misure.divisore(e17.misure.GLIFI_EVA))[::2]
    lingue_c = candidate()
    print('%d lingue' % len(lingue_c), flush=True)
    percorso = os.path.join(RISULTATI, 'e19_tutte_le_lingue.json')
    ris = OrderedDict()
    if os.environ.get('RIPRENDI') and os.path.exists(percorso):
        # riprende un giro interrotto: le lingue gia' fatte restano come sono
        with open(percorso, encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
    # si rifanno le lingue mancanti e quelle in cui il controllo positivo non era riuscito
    ris = OrderedDict((k, r) for k, r in ris.items() if riuscito(r))
    lavori = [(k, m, voynich, naibbe) for k, m in lingue_c.items() if k not in ris]
    with Pool(int(os.environ.get('PROCESSI', '4'))) as pool:
        for chiave, r in pool.imap_unordered(una_lingua, lavori):
            ris[chiave] = r
            with open(percorso, 'w', encoding='utf-8') as f:
                json.dump(ris, f, ensure_ascii=False, indent=1)
    ris = OrderedDict((k, ris[k]) for k in lingue_c if k in ris)
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    righe = sorted(ris.items(), key=lambda x: (not riuscito(x[1]),
                                              -max(posizione(x[1]), posizione(x[1], 'Voynich al contrario'))))
    ok = sum(1 for _, r in righe if riuscito(r))
    out = ['# Esperimento 19: il risolutore su tutte le lingue', '',
           'Il Voynich letto a segni EVA (26 simboli, una riga su due), senza spazi, contro %d lingue. Per ogni lingua: controllo '
           'positivo (la lingua stessa cifrata con 26 simboli e risolta, ritentando una ripartenza alla volta '
           'finché la chiave torna, al massimo %d volte), controllo negativo (un\'altra lingua), il Voynich, il '
           'Voynich letto da destra a sinistra e il Plinio cifrato col Naibbe, con almeno %d ripartenze e almeno '
           'quante ne sono servite al controllo positivo.' % (len(ris), MASSIMO_RIPARTENZE, RIPARTENZE), '',
           'Il risolutore ritrova almeno il 90%% della chiave nel controllo positivo in %d lingue su %d. Dove non ci '
           'riesce la posizione non vuol dire niente: quelle lingue sono in fondo alla tabella e fuori dal '
           'grafico.' % (ok, len(ris)), '',
           '- **posizione**: dove cade il punteggio fra il controllo negativo (0) e il positivo (1), per il Voynich, '
           'il Voynich letto al contrario e il Plinio cifrato col Naibbe (che ha la grana del Voynich ma non è una '
           'sostituzione di nessuna lingua).', '',
           '| lingua | famiglia | lettere | chiave (positivo) | punteggio positivo | negativo | Voynich | '
           'posizione: Voynich | al contrario | Naibbe | copertura 6+: positivo / Voynich |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for k, r in righe:
        out.append('| %s | %s | %d | %.0f%% | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.0f%% / %.1f%% |' % (
            r['lingua'], r['famiglia'], r['lettere'], 100 * r['controllo positivo'].get('chiave_giusta', 0),
            r['controllo positivo']['punteggio'], r['controllo negativo']['punteggio'], r['Voynich']['punteggio'],
            posizione(r), posizione(r, 'Voynich al contrario'), posizione(r, 'Naibbe'),
            100 * r['controllo positivo']['copertura_6'], 100 * r['Voynich']['copertura_6']))
    schiacciate = [r['lingua'] for _, r in righe
                   if r['controllo positivo']['punteggio'] - r['controllo negativo']['punteggio'] < 0.3]
    if schiacciate:
        out += ['', 'In %s il controllo negativo arriva quasi al punteggio del positivo, con una chiave degenere che '
                'ripete poche lettere: la scala si schiaccia e le posizioni escono enormi. Non vogliono dire '
                'niente.' % ', '.join(schiacciate)]
    out += ['', '## Come "legge" il Voynich la chiave migliore, nelle lingue dove arriva più in alto', '']
    for k, r in [x for x in righe if riuscito(x[1])][:3]:
        chiave = 'Voynich' if posizione(r) >= posizione(r, 'Voynich al contrario') else 'Voynich al contrario'
        out += ['**%s** (%s):' % (r['lingua'], chiave.lower()), '', '```'] + r[chiave]['esempio'][:4] + ['```', '']
    with open(os.path.join(RISULTATI, 'e19_tutte_le_lingue.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    import grafici
    righe = sorted((r for r in ris.values() if riuscito(r)), key=lambda r: posizione(r))
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=4.8)
        fig.subplots_adjust(left=0.09, right=0.97, top=0.80, bottom=0.14)
        xs = range(len(righe))
        ax.axhline(1, color=t['muto'], linewidth=1.2, zorder=1)
        ax.axhline(0, color=t['muto'], linewidth=1.2, zorder=1)
        ax.text(0, 1.03, 'la lingua stessa, cifrata', ha='left', va='bottom', fontsize=8, color=t['secondario'])
        ax.text(0, 0.03, 'un\'altra lingua, cifrata', ha='left', va='bottom', fontsize=8, color=t['secondario'])
        basso = -1.0

        def punti(chiave, **stile):
            ys = [posizione(r, chiave) for r in righe]
            dentro = [(x, y) for x, y in zip(xs, ys) if y >= basso]
            fuori = [x for x, y in zip(xs, ys) if y < basso]
            ax.scatter([x for x, _ in dentro], [y for _, y in dentro], **stile)
            if fuori:        # fuori scala (controllo negativo degenere): sul bordo, con un triangolo
                stile = dict(stile, marker='v', label=None)
                ax.scatter(fuori, [basso + 0.04] * len(fuori), **stile)

        punti('Voynich al contrario', s=16, color=t['contesto'], edgecolor=t['sfondo'], linewidth=0.6,
              label='Voynich letto da destra a sinistra', zorder=2)
        punti('Naibbe', s=16, color=t['secondo'], edgecolor=t['sfondo'], linewidth=0.6,
              label='Naibbe (grana del Voynich, nessuna sostituzione)', zorder=2)
        punti('Voynich', s=22, color=t['accento'], edgecolor=t['sfondo'], linewidth=0.6, label='Voynich', zorder=3)
        ax.set_xticks([])
        ax.set_xlabel('%d lingue, in ordine' % len(righe))
        ax.set_ylabel('posizione del Voynich')
        ax.set_ylim(basso, 1.25)
        ax.legend(loc='center left', bbox_to_anchor=(0.0, 0.66), frameon=False, fontsize=8, labelcolor=t['secondario'])
        massimo = max(max(posizione(r), posizione(r, 'Voynich al contrario')) for r in righe)
        grafici.titoli(fig, ax, t, 'In nessuna delle %d lingue il Voynich si legge' % len(righe),
                       'La chiave migliore, fra un testo in un\'altra lingua (0) e uno nella lingua stessa (1). Il Voynich\n'
                       'non supera %s, neanche al contrario; il Naibbe, che non è una sostituzione, sta poco sotto.'
                       % ('%.1f' % massimo).replace('.', ','))
        grafici.salva(fig, RISULTATI, 'e19_tutte_le_lingue', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e19_tutte_le_lingue.json'), encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
