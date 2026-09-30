# -*- coding: utf-8 -*-
"""Esperimento 2: l'impronta a livello di parola.

Se il Voynich fosse una lingua cifrata parola per parola in modo fisso (una
sostituzione semplice, un cifrario "verboso" dove ogni lettera diventa due o
tre glifi, un codice dove ogni parola ha il suo codice), le lettere
cambierebbero ma le parole no: quante parole diverse ci sono, quante compaiono
una volta sola, quanto una parola dipende da quella prima, quanto spesso una
parola si ripete subito. Queste misure si possono confrontare con le lingue
senza sapere niente del cifrario.

Campioni di 30.000 parole (10.000 per le lingue A e B di Currier, che sono piu'
corte), tre finestre per testo.

Scrive risultati/e02_impronta.json e risultati/e02_impronta.md.
"""
import json, os, statistics, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
FINESTRE = 3
CHIAVI = ['h2', 'lung_media', 'lung_dev', 'tipi_su_parole', 'hapax', 'h_parola',
          'im_vicine_eccesso', 'ripetute', 'ripetute_rapporto', 'dist_rapporto',
          'dist_rapporto_diverse']


def finestre(parole, n, k=FINESTRE):
    if len(parole) < n:
        return []
    ultimo = len(parole) - n
    return [parole[ultimo * i // (k - 1):ultimo * i // (k - 1) + n] for i in range(k)]


def misura(parole, n, dividi=None):
    righe = []
    for tratto in finestre(parole, n):
        r = misure.parole_misure(tratto, dividi)
        r['h2'] = misure.condizionate(misure.sequenza(tratto, dividi), k_max=2)['h2']
        righe.append(r)
    if not righe:
        return None
    out = {'parole': n}
    for c in CHIAVI:
        valori = [r[c] for r in righe]
        out[c] = statistics.mean(valori)
        out[c + '_dev'] = statistics.stdev(valori) if len(valori) > 1 else 0.0
    out['lunghezze'] = righe[0]['lunghezze']
    return out


def voynich():
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl = trascrizione.leggi('ZL')
    corrente = trascrizione.testo_corrente(zl)
    yield 'ZL', trascrizione.parole(corrente), glifi, 30000
    yield 'IT', trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('IT'))), glifi, 30000
    yield 'GC v101', trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('GC'))), None, 30000
    unite = trascrizione.testo_corrente(trascrizione.leggi('ZL', virgola_spazio=False))
    yield 'ZL virgole unite', trascrizione.parole(unite), glifi, 30000
    for lingua in 'AB':
        yield 'ZL lingua %s' % lingua, trascrizione.parole(
            trascrizione.testo_corrente(zl, lingua=lingua)), glifi, 10000
    yield 'ZL (10.000 parole)', trascrizione.parole(corrente), glifi, 10000


def main():
    ris = {'voynich': {}, 'lingue_30000': {}, 'lingue_10000': {}}
    for nome, parole, dividi, n in voynich():
        r = misura(parole, n, dividi)
        r['disponibili'] = len(parole)
        ris['voynich'][nome] = r
        print('%-20s parole %5d  h2 %.2f  lung %.2f  tipi/parole %.3f  hapax %.2f  IM+ %.3f  rip x%.2f  dist %.3f/%.3f' % (
            nome, len(parole), r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'],
            r['im_vicine_eccesso'], r['ripetute_rapporto'], r['dist_rapporto'], r['dist_rapporto_diverse']))
    for chiave, meta in sorted(lingue.indice().items()):
        parole = lingue.parole(chiave)
        for n in (30000, 10000):
            r = misura(parole, n)
            if r is None:
                continue
            r.update({k: meta[k] for k in ('lingua', 'famiglia', 'scrittura', 'tipo_scrittura')})
            ris['lingue_%d' % n][chiave] = r
    with open(os.path.join(RISULTATI, 'e02_impronta.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    out = ['# Esperimento 2: impronta a livello di parola', '',
           'Campioni di 30.000 parole, media di %d finestre. Le misure dopo h2 non cambiano '
           'se ogni parola è cifrata sempre nello stesso modo.' % FINESTRE, '',
           '- **h2**: incertezza sulla lettera successiva (bit); per il Voynich in glifi.',
           '- **lung.**: lunghezza media delle parole, in lettere o glifi.',
           '- **tipi/parole**: parole diverse diviso parole totali.',
           '- **hapax**: quota delle parole diverse che compaiono una volta sola.',
           '- **IM in più**: quanto una parola dice sulla successiva, oltre il caso (bit).',
           '- **ripetute ×**: quante volte una parola si ripete subito, rispetto al caso.',
           '- **somiglianza vicine**: distanza fra parole vicine diviso distanza fra parole a caso, '
           'escluse le ripetizioni identiche; sotto 1 le vicine si somigliano più del caso.', '',
           '> **Attenzione.** "IM in più" dipende molto dal genere del testo: i testi tecnici latini '
           '(esperimento 3) scendono quanto il Voynich. La "poca sintassi" che sembra emergere qui è '
           'un effetto del confronto con la Bibbia. Anche "somiglianza vicine" va letta insieme agli '
           'esperimenti 4 e 5: quasi tutta viene dalla pagina, non dall\'essere adiacenti.', '',
           '| testo | scrittura | h2 | lung. | tipi/parole | hapax | IM in più | ripetute × | somiglianza vicine |',
           '|---|---|---|---|---|---|---|---|---|']
    righe = [('**Voynich %s**' % k, v, '') for k, v in ris['voynich'].items() if v['parole'] == 30000]
    righe += [(k, v, v['tipo_scrittura']) for k, v in ris['lingue_30000'].items()]
    righe.sort(key=lambda r: r[1]['im_vicine_eccesso'])
    for nome, v, scr in righe:
        out.append('| %s | %s | %.2f | %.2f | %.3f | %.2f | %.3f | %.2f | %.3f |' % (
            nome, scr, v['h2'], v['lung_media'], v['tipi_su_parole'], v['hapax'],
            v['im_vicine_eccesso'], v['ripetute_rapporto'], v['dist_rapporto_diverse']))
    with open(os.path.join(RISULTATI, 'e02_impronta.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e02_impronta.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f))
    else:
        main()
