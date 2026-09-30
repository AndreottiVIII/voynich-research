# -*- coding: utf-8 -*-
"""Prepara i testi di confronto: clona il corpus biblico e ne estrae i campioni.

Le trascrizioni del Voynich stanno gia' nel repository (dati/trascrizioni/);
i testi di confronto no, pesano troppo. Questo script scarica una volta sola
le cento Bibbie, la Latin Library (ricette, agricoltura, piante), il codice
del cifrario Naibbe, il generatore di Timm e Schinner e il breviario romano
(Divinum Officium), ciascuno a un commit fissato, dentro dati/cache/sorgenti/,
e scrive i testi normalizzati delle Bibbie in dati/cache/lingue/. Git ignora
tutta dati/cache/. I testi latini e il Naibbe si leggono dalla copia scaricata.

    python3 voynich/prepara.py
"""
import os, subprocess, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, 'analisi'))
import lingue

URL = 'https://github.com/christos-c/bible-corpus'
COMMIT_PIENO = '44e5fca1bfb369a5da2ee23ebc6f421c88489c5c'


def git(*argomenti, cwd=None):
    subprocess.check_call(['git'] + list(argomenti), cwd=cwd)


def fissa(url, cartella, commit):
    """Clona (se serve) e porta la copia locale esattamente al commit indicato."""
    os.makedirs(os.path.dirname(os.path.abspath(cartella)), exist_ok=True)
    if not os.path.isdir(os.path.join(cartella, '.git')):
        git('clone', '--depth', '1', url, cartella)
    attuale = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cartella).decode().strip()
    if attuale != commit:
        git('fetch', '--depth', '1', 'origin', commit, cwd=cartella)
        git('checkout', '--quiet', commit, cwd=cartella)


def fissa_in_parte(url, cartella, commit, percorsi):
    """Come fissa, ma scarica solo alcune cartelle: il repository intero e' grande."""
    os.makedirs(os.path.dirname(os.path.abspath(cartella)), exist_ok=True)
    if not os.path.isdir(os.path.join(cartella, '.git')):
        git('clone', '--depth', '1', '--filter=blob:none', '--no-checkout', url, cartella)
    git('-c', 'core.protectNTFS=false', 'sparse-checkout', 'set', *percorsi, cwd=cartella)
    git('fetch', '--depth', '1', '--filter=blob:none', 'origin', commit, cwd=cartella)
    # protectNTFS=false (anche per sparse-checkout, che altrimenti va in crash): su Windows git
    # rifiuta percorsi con "\" anche fuori dalle cartelle scelte (naibbe-cipher ne ha); fuori
    # dalle cartelle scelte non si scrive niente, quindi non c'e' rischio
    git('-c', 'core.protectNTFS=false', 'checkout', '--quiet', commit, cwd=cartella)


def main():
    fissa(URL, lingue.SORGENTE, COMMIT_PIENO)
    fissa('https://github.com/cltk/lat_text_latin_library', lingue.LATIN_LIBRARY, lingue.COMMIT_LL)
    # il cifrario Naibbe di Greshko (2025): tabelle e testo cifrato di esempio
    # solo le cartelle che servono: figure_utils/ contiene nomi di file con "\" che su Windows
    # non si possono creare (vedi QUADERNO.md, 30/09/2026)
    fissa_in_parte('https://github.com/greshko/naibbe-cipher', os.path.join(lingue.SORGENTI, 'naibbe-cipher'),
                   'f2675ec5dd275268bc64dd48ea64fc0e0e9827a2',
                   ['references', 'encrypted', 'decrypted', 'input', 'respaced_plaintext'])
    # il generatore ad autocitazione di Timm e Schinner (2020), in Java: serve all'esperimento 22
    fissa('https://github.com/TorstenTimm/SelfCitationTextgenerator',
          os.path.join(lingue.SORGENTI, 'SelfCitationTextgenerator'), 'a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7')
    # il breviario romano in latino (progetto Divinum Officium): preghiere e litanie per l'esperimento 25
    fissa_in_parte('https://github.com/DivinumOfficium/divinum-officium',
                   os.path.join(lingue.SORGENTI, 'divinum-officium'), '2dbc3c24ea7f96f014060aaa51caeec477f3c578',
                   ['web/www/horas/Latin'])
    # la decifrazione latina di Schechter (glossario e trascrizione): esperimento 26
    fissa('https://github.com/scott-schechter/voynich-decoded',
          os.path.join(lingue.SORGENTI, 'voynich-decoded'), '71f2f3c91e9113d285ab21e024f1dd70c1f43c44')
    # Rozanova e Temerev (2026, arXiv 2608.17096): coordinate per parola di voynichese.com sulle
    # immagini Beinecke e corpora di controllo; lo snapshot e' quello analizzato nell'articolo (MIT)
    fissa('https://github.com/lrozanova/voynich-units',
          os.path.join(lingue.SORGENTI, 'voynich-units'), '66f8adaadc120f93e8a4c906685ba66a9d3ab847')
    # il gibberish di Gaskell e Bowern (2022), redistribuito nel repository del Naibbe fuori dalle
    # cartelle scaricate: si estrae lo zip con git show, senza checkout (esperimento 41)
    gb = os.path.join(lingue.SORGENTI, 'gaskell_bowern')
    os.makedirs(gb, exist_ok=True)
    with open(os.path.join(gb, 'gibberish_transcriptions.zip'), 'wb') as f:
        f.write(subprocess.check_output(
            ['git', 'show', 'f2675ec5dd275268bc64dd48ea64fc0e0e9827a2:figure_utils/gaskell_bowern_2022/'
             'data/cleaned/gibberish_transcriptions.zip'], cwd=os.path.join(lingue.SORGENTI, 'naibbe-cipher')))
    indice = lingue.prepara()
    lingue.prepara_pinyin()
    indice = lingue.indice()
    corte = [k for k, v in indice.items() if v['caratteri'] < 250_000]
    print('%d lingue pronte in %s' % (len(indice), os.path.normpath(lingue.CACHE)))
    if corte:
        print('troppo corte per il confronto alla pari: %s' % ', '.join(corte))


if __name__ == '__main__':
    main()
