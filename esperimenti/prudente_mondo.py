# -*- coding: utf-8 -*-
"""IA36, modulo di supporto: il mondo di SVILUPPO `struttura3` (solo prove: mai nella corsa vera).

In parole semplici
- Serve a fissare le soglie e i pesi della scelta prudente su un mondo DIVERSO da `struttura2` (il controllo positivo, che non si tara) e dal Voynich: stessa famiglia di regole di
  `struttura2` (vocabolario di sezione, riga sopra ritoccata, chiusure e aperture di paragrafo, nessuna parola di tema), con altri parametri e un altro seme:
  riga sopra con probabilita' 0,20 (in `struttura2` 0,30), ritocco 0,35 (0,5), chiusure di riga 0,6 (0,5), aperture di paragrafo 0,4 (0,5); semi `ia36dev`.
- Si usa con `SOLO_CONTROLLI=1` e `MONDI36=3` (la disposizione del libro e' quella del Voynich, il testo e' latino): il testo del mondo e' sintetico, costruito sul libro latino di prova.
Nessun risultato e' scritto qui.
"""
import os
import sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import righello_testi as RT  # noqa: E402
import piano_mondo as PM  # noqa: E402
import sezione_mondo as SMO  # noqa: E402,F401  (registra `struttura2`: questo si appoggia sopra)

NOME_MONDO = 'struttura3'
PAR_STRUTTURA3 = OrderedDict([('eco', 0.20), ('ritocco', 0.35), ('tema', 0.0), ('n_tema', 15), ('freq_min_tema', 3), ('fine', 0.6), ('ini', 0.4)])
seme_str = PM.seme_str
_precedente = RT.righe_sintetiche


def _righe_sintetiche(base, nome, gemello=False):
    if nome != NOME_MONDO:
        return _precedente(base, nome, gemello)
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    return PM.sintetico_struttura(base, base, seme_str('ia36dev', 'mondo', nome, 'gemello' if gemello else 'vero'), D, unita, PAR_STRUTTURA3)


def registra():
    if NOME_MONDO not in RT.MONDI:
        RT.MONDI[NOME_MONDO] = dict(gen='struttura3', par=dict(PAR_STRUTTURA3))
    RT.righe_sintetiche = _righe_sintetiche


registra()

if __name__ == '__main__':
    pass
