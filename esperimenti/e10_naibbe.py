# -*- coding: utf-8 -*-
"""Esperimento 10: il cifrario Naibbe alla prova delle anomalie del Voynich.

Il cifrario Naibbe (Greshko 2025, Cryptologia, doi:10.1080/01611194.2025.2566408)
e' la proposta piu' seria di un cifrario quattrocentesco capace di trasformare
latino o italiano in qualcosa che somiglia al Voynich: il testo in chiaro si
taglia in pezzi di una o due lettere e ogni pezzo diventa una "parola", scelta
da una di sei tabelle con un mazzo di carte. Ogni parola vale quindi una o due
lettere, e la stessa lettera si scrive in molti modi.

Lo misuriamo con le stesse misure del Voynich, piu' una nuova: la dipendenza
attraverso lo spazio (fine di una parola contro inizio della successiva).
Poi una variante con "deriva": le preferenze fra le tabelle cambiano da una
pagina all'altra, come per uno scriba che cambia abitudini a ogni seduta.

Scrive risultati/e10_naibbe.json e risultati/e10_naibbe.md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
from e07_codifiche import impronta, pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
NAIBBE = os.environ.get('NAIBBE', os.path.join(lingue.SORGENTI, 'naibbe-cipher'))
N = 35000
PAROLE_PAGINA = misure.PAROLE_RIGA * misure.RIGHE_PAGINA


def completa(pagine, dividi):
    r = impronta(pagine, dividi)
    r.update(misure.confine([riga for pag in pagine for riga in pag], dividi))
    return r


def main():
    glifi_div = misure.divisore(misure.GLIFI_EVA)
    glifi = generatori.naibbe_tabelle(os.path.join(NAIBBE, 'references', 'naibbe_tables.csv'))
    ris = OrderedDict()
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    ris['Voynich (pagine e righe vere)'] = completa(pagine_voynich(corrente), glifi_div)
    ris['Voynich (righe finte da 8 parole)'] = completa(
        misure.pagine_finte(trascrizione.parole(corrente)), glifi_div)
    stampa('Voynich', ris['Voynich (pagine e righe vere)'])

    ufficiale = open(os.path.join(NAIBBE, 'encrypted', 'nathist_output_ciphertext.txt'),
                     encoding='utf-8').read().split()
    ris['Naibbe, cifrato ufficiale di Greshko (Plinio XVI)'] = completa(misure.pagine_finte(ufficiale), glifi_div)
    stampa('Naibbe ufficiale', ris['Naibbe, cifrato ufficiale di Greshko (Plinio XVI)'])

    testi = [('Vitruvio', lingue.genere('Vitruvio, architettura')),
             ('Bibbia latina', lingue.parole('Latin')),
             ('Bibbia italiana', lingue.parole('Italian'))]
    for nome, parole in testi:
        chiaro = parole[:N]
        ris[nome + ': testo in chiaro'] = completa(misure.pagine_finte(chiaro), None)
        stampa(nome + ' in chiaro', ris[nome + ': testo in chiaro'])
        lettere = ''.join(generatori.naibbe_pulisci(p) for p in parole[:14000])
        rnd = random.Random(21)
        cifrato, _ = generatori.naibbe(lettere, glifi, rnd)
        cifrato = cifrato[:N]
        chiave = nome + ': Naibbe'
        ris[chiave] = completa(misure.pagine_finte(cifrato), glifi_div)
        stampa(chiave, ris[chiave])
        for k in (3.0, 1.0, 0.3):
            rnd = random.Random(21)
            cifrato, _ = generatori.naibbe(lettere, glifi, rnd, PAROLE_PAGINA, k)
            chiave = nome + ': Naibbe con deriva di pagina (concentrazione %.1f)' % k
            ris[chiave] = completa(misure.pagine_finte(cifrato[:N]), glifi_div)
            stampa(chiave, ris[chiave])
    with open(os.path.join(RISULTATI, 'e10_naibbe.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, r):
    print('%-62s h2 %.2f lung %.2f tipi %.3f hapax %.2f ident x%.2f somigl. %.1f%%/%.1f%%/%.1f%% confine %.3f' % (
        nome, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_vs_riga'],
        100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe'],
        r['im_confine_eccesso']))


def scrivi_tabella(ris):
    out = ['# Esperimento 10: il cifrario Naibbe', '',
           'Greshko, M. A. (2025). *The Naibbe cipher: a substitution cipher that encrypts Latin and '
           'Italian as Voynich Manuscript-like ciphertext.* Cryptologia. '
           'doi:10.1080/01611194.2025.2566408. Codice: github.com/greshko/naibbe-cipher.', '',
           'Stesse misure dell\'esperimento 7, più **confine**: quanto l\'ultimo segno di una parola dice '
           'sul primo della successiva, oltre il caso (bit). "Deriva di pagina": a ogni pagina le '
           'preferenze fra le sei tabelle si ripescano; concentrazione più bassa = pagine più "di parte".', '',
           '| testo | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza: riga | riga sotto | 6 righe | confine |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        g = '**%s**' % nome if nome.startswith('Voynich') else nome
        out.append('| %s | %.2f | %.2f | %.3f | %.2f | ×%.2f | %.1f%% | %.1f%% | %.1f%% | %.3f |' % (
            g, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_vs_riga'],
            100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe'],
            r['im_confine_eccesso']))
    with open(os.path.join(RISULTATI, 'e10_naibbe.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
