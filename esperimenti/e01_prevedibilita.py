# -*- coding: utf-8 -*-
"""Esperimento 1: la lettera successiva del Voynich e' troppo prevedibile?

Misura h1, h2, h3 sul testo corrente del Voynich (tre trascrizioni, due
alfabeti) e sulla Bibbia in 107 lingue. Tutti i campioni hanno lo stesso numero
di simboli, spazi compresi, e per ogni testo se ne prendono cinque finestre in
punti diversi: la dispersione fra le finestre dice quanto ballano i numeri.

Scrive risultati/e01_prevedibilita.json e risultati/e01_prevedibilita.md.
"""
import json, os, statistics, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import grafici, lingue, misure, trascrizione

N = 175_000         # simboli per campione: ci stanno tutte le varianti del Voynich
FINESTRE = 5
RISULTATI = os.path.join(QUI, '..', 'risultati')


def finestre(parole, dividi=None, n=N, k=FINESTRE):
    """k tratti contigui di parole, ciascuno lungo n simboli spazi compresi.
    Si taglia per parole, cosi' con e senza spazi si misura lo stesso testo."""
    lung = [(len(dividi(p)) if dividi else len(p)) + 1 for p in parole]
    if sum(lung) < n:
        return []
    ultimo, tot = len(parole), 0
    while tot < n:                       # l'inizio piu' tardo possibile
        ultimo -= 1
        tot += lung[ultimo]
    out = []
    for i in range(k):
        inizio = ultimo * i // (k - 1) if k > 1 else 0
        fine, tot = inizio, 0
        while fine < len(parole) and tot + lung[fine] <= n:
            tot += lung[fine]
            fine += 1
        out.append(parole[inizio:fine])
    return out


def misura(parole, dividi=None):
    righe = []
    for tratto in finestre(parole, dividi):
        a = misure.sequenza(tratto, dividi)
        b = misure.sequenza(tratto, dividi, spazio=False)
        r = misure.condizionate(a)
        mm = misure.condizionate(a, corretta=True)
        s = misure.condizionate(b, k_max=2)
        righe.append({'h0': r['h0'], 'h1': r['h1'], 'h2': r['h2'], 'h3': r['h3'],
                      'h2_mm': mm['h2'], 'h3_mm': mm['h3'], 'simboli': r['simboli'],
                      'h1_senza_spazi': s['h1'], 'h2_senza_spazi': s['h2']})
    if not righe:
        return None
    out = {}
    for chiave in righe[0]:
        valori = [r[chiave] for r in righe]
        out[chiave] = statistics.mean(valori)
        if len(valori) > 1 and chiave.startswith('h'):
            out[chiave + '_dev'] = statistics.stdev(valori)
    return out


def varianti_voynich():
    for q, alfabeto in [('ZL', 'EVA'), ('IT', 'EVA'), ('GC', 'v101')]:
        parole = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi(q)))
        yield '%s %s' % (q, alfabeto), parole, None
        if alfabeto == 'EVA':
            yield '%s EVA, glifi fusi' % q, parole, misure.divisore(misure.GLIFI_EVA)
    # Robustezza: lo spazio incerto (virgola) trattato come assenza di spazio
    parole = trascrizione.parole(trascrizione.testo_corrente(
        trascrizione.leggi('ZL', virgola_spazio=False)))
    yield 'ZL EVA, glifi fusi, virgole unite', parole, misure.divisore(misure.GLIFI_EVA)


def main():
    risultati = {'N': N, 'finestre': FINESTRE, 'voynich': {}, 'lingue': {}}
    for nome, parole, dividi in varianti_voynich():
        r = misura(parole, dividi)
        risultati['voynich'][nome] = r
        print('%-36s h1 %.3f  h2 %.3f  h3 %.3f  simboli %d' % (nome, r['h1'], r['h2'], r['h3'], r['simboli']))
    for chiave, meta in sorted(lingue.indice().items()):
        parole = lingue.parole(chiave)
        r = misura(parole)
        if r is None:
            continue
        r.update({k: meta[k] for k in ('lingua', 'famiglia', 'scrittura', 'tipo_scrittura')})
        risultati['lingue'][chiave] = r
    os.makedirs(RISULTATI, exist_ok=True)
    with open(os.path.join(RISULTATI, 'e01_prevedibilita.json'), 'w', encoding='utf-8') as f:
        json.dump(risultati, f, ensure_ascii=False, indent=1)
    scrivi_tabella(risultati)
    disegna(risultati)


def scrivi_tabella(ris):
    righe = [(k, v) for k, v in ris['lingue'].items()]
    righe += [('**Voynich ' + k + '**', dict(v, lingua='', tipo_scrittura='?'))
              for k, v in ris['voynich'].items()]
    righe.sort(key=lambda kv: kv[1]['h2'])
    out = ['# Esperimento 1: prevedibilità della lettera successiva', '',
           'Campioni di %d simboli (spazi compresi), media di %d finestre.' % (ris['N'], ris['finestre']),
           'h2 è l\'incertezza sulla lettera successiva sapendo quella prima: più è bassa, più il testo è prevedibile.',
           '', '| # | testo | scrittura | simboli | h1 | h2 | h3 | h1 - h2 |', '|---|---|---|---|---|---|---|---|']
    for i, (k, v) in enumerate(righe, 1):
        out.append('| %d | %s | %s | %d | %.2f | %.2f | %.2f | %.2f |' % (
            i, k, v.get('tipo_scrittura', ''), v['simboli'], v['h1'], v['h2'], v['h3'], v['h1'] - v['h2']))
    with open(os.path.join(RISULTATI, 'e01_prevedibilita.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


ITALIANO = {'Latin': 'latino', 'Italian': 'italiano', 'Maori': 'maori',
            'Vietnamese': 'vietnamita', 'Chinantec-NT': 'chinanteco', 'Hebrew': 'ebraico'}
SPOSTA = {'Chinantec-NT': (-6, -11, 'right'), 'Italian': (-6, -2, 'right'),
          'Latin': (-6, 4, 'right'), 'Hebrew': (6, 4, 'left')}
VOYNICH_DISEGNATI = {'ZL EVA': 'Voynich, EVA',
                     'ZL EVA, glifi fusi': 'Voynich, EVA con glifi fusi',
                     'GC v101': 'Voynich, alfabeto v101'}


def disegna(ris):
    """h1 contro h2: ogni punto e' un testo. Le scritture logografiche (cinese,
    giapponese, coreano) hanno migliaia di segni e finiscono fuori scala: sono
    nella tabella, non nel grafico. Le versioni '-tok' sono doppioni."""
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.09, right=0.97, top=0.80, bottom=0.12)
        altre = [(v['h1'], v['h2']) for k, v in ris['lingue'].items()
                 if v['tipo_scrittura'] not in ('alfabeto', 'logografica') and not k.endswith('-tok')]
        alfa = [(v['h1'], v['h2']) for k, v in ris['lingue'].items()
                if v['tipo_scrittura'] == 'alfabeto' and not k.endswith('-tok')]
        ax.scatter(*zip(*alfa), s=34, color=t['contesto'], edgecolor=t['sfondo'],
                   linewidth=1.2, label='lingue scritte in alfabeto', zorder=2)
        ax.scatter(*zip(*altre), s=34, facecolor='none', edgecolor=t['contesto'],
                   linewidth=1.1, label='altre scritture (abjad, abugida, sillabari)', zorder=2)
        voy = [(ris['voynich'][k]['h1'], ris['voynich'][k]['h2'], nome)
               for k, nome in VOYNICH_DISEGNATI.items()]
        ax.scatter([v[0] for v in voy], [v[1] for v in voy], s=58, color=t['accento'],
                   edgecolor=t['sfondo'], linewidth=1.5, label='Voynich', zorder=3)
        spost = {'Voynich, EVA': (8, -12), 'Voynich, EVA con glifi fusi': (8, 5),
                 'Voynich, alfabeto v101': (8, -4)}
        for x, y, nome in voy:
            ax.annotate(nome, (x, y), xytext=spost[nome], textcoords='offset points',
                        fontsize=8.5, color=t['inchiostro'], va='center')
        for k, nome in ITALIANO.items():
            v = ris['lingue'][k]
            dx, dy, lato = SPOSTA.get(k, (6, 4, 'left'))
            ax.annotate(nome, (v['h1'], v['h2']), xytext=(dx, dy), textcoords='offset points',
                        fontsize=8, color=t['secondario'], ha=lato)
        ax.set_xlabel('h1: incertezza su una lettera presa da sola (bit)')
        ax.set_ylabel('h2: incertezza sulla lettera successiva (bit)')
        leg = ax.legend(loc='lower right', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t,
                       'A parità di alfabeto, il Voynich è più prevedibile di ogni lingua',
                       'Bibbia in circa 100 lingue e testo del Voynich, campioni di %d simboli.\n'
                       'Più in basso = la lettera che segue è più facile da indovinare.' % ris['N'])
        grafici.salva(fig, RISULTATI, 'e01_prevedibilita', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv:
        with open(os.path.join(RISULTATI, 'e01_prevedibilita.json'), encoding='utf-8') as f:
            disegna(json.load(f))
    else:
        main()
