# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: il mondo `struttura2` (controllo positivo con vocabolario di sezione e aperture di paragrafo, SENZA parole di tema per pagina).

In parole semplici
- In IA34 il mondo `struttura` aveva 15 "parole di tema" estratte a caso a ogni pagina: sono la parte del processo che un oracolo non puo' stimare dai soli fogli d'addestramento (sono
  decise dal seme, non dalle frequenze), e il suo oracolo e il suo gemello sono risultati non validi (gemello b 0,39 fuori fascia; oracolo N 0,75). Qui la stessa regola con `tema` = 0:
    * ogni parola "fresca" viene dal vocabolario della sua sezione e lingua (frequenze del libro);
    * con probabilita' 0,30 e' una parola della riga sopra in posizione vicina, ritoccata con probabilita' 0,5;
    * l'ultima parola di ogni riga viene, con probabilita' 0,5, dalle chiusure di riga della sezione; la prima parola di un paragrafo, con probabilita' 0,5, dalle aperture della sezione.
  Tutto quel che il processo usa (vocabolario di sezione, chiusure, aperture) si stima dai conteggi, e l'oracolo e' la stessa regola con le frequenze contate sui fogli d'addestramento.
- `righello_testi` non si modifica: il modulo registra il mondo in `RT.MONDI` e avvolge ancora `RT.righe_sintetiche` (sopra `piano_mondo`, che aggiunge `struttura`).
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

NOME_MONDO = 'struttura2'
PAR_STRUTTURA2 = OrderedDict([('eco', 0.30), ('ritocco', 0.5), ('tema', 0.0), ('n_tema', 15), ('freq_min_tema', 3), ('fine', 0.5), ('ini', 0.5)])
seme_str = PM.seme_str
_precedente = RT.righe_sintetiche


def _righe_sintetiche(base, nome, gemello=False):
    if nome != NOME_MONDO:
        return _precedente(base, nome, gemello)
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    return PM.sintetico_struttura(base, base, seme_str('ia35', 'mondo', nome, 'gemello' if gemello else 'vero'), D, unita, PAR_STRUTTURA2)


def registra():
    PM.registra()
    if NOME_MONDO not in RT.MONDI:
        RT.MONDI[NOME_MONDO] = dict(gen='struttura2', par=dict(PAR_STRUTTURA2))
    RT.righe_sintetiche = _righe_sintetiche


registra()


def libro_oracolo(righe_mondo, base, f_add, mult, seme):
    """Un libro dell'oracolo stimato del mondo `struttura2`: la regola con le frequenze contate sui fogli d'addestramento del testo del mondo (+ (mult - 1) campioni della vera regola)."""
    D = I7.divisore()
    unita = sorted({u for x in righe_mondo for w in x['parole'] for u in D(w)})
    ins = set(f_add)
    conteggi = [x for x in righe_mondo if x['foglio'] in ins]
    if mult > 1:
        lay_add = [x for x in base if x['foglio'] in ins]
        for j in range(1, mult):
            conteggi += PM.sintetico_struttura(lay_add, base, seme_str('ia35extra', j), D, unita, PAR_STRUTTURA2)
    return PM.t_da_righe(PM.sintetico_struttura(righe_mondo, conteggi, seme, D, unita, PAR_STRUTTURA2))


def libro_gemello(base, seme):
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    return PM.t_da_righe(PM.sintetico_struttura(base, base, seme, D, unita, PAR_STRUTTURA2))


if __name__ == '__main__':
    pass
