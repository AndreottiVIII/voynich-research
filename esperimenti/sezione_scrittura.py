# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: lo scrittore di IA33 (14 manopole, `oracolo_scrittura.ScrittoreL`, importato senza modificarlo) sopra la rete condizionata o la sua ablazione.

In parole semplici
- Stesse 14 manopole di IA33 (temperature, `top_p`, correzioni a conteggi di segni, di parole e di pagina, `b_nuove`, `s`): **non si usano le manopole di IA34** (la sorgente di sezione era
  risultata spenta e la ripresa dalla riga sopra al limite: IA35 chiede alla rete di imparare da sola quel che le manopole non riuscivano a dare).
- Cambia solo la rete: `ScrittoreCond(cartella)` legge `pieno.pt` di `sezione_rete` (condizionata o ablazione: lo dice `cfg['cond']`) e scrive con `PennaCond`. Le teste di pagina e di riga
  (sezione, lingua, mano, inizio di paragrafo, posizione, fascia di lunghezza) sono quelle della disposizione del libro del mondo, come per tutti gli scrittori (`I7.testa_pagina`, `I7.testa_riga`).
Nessun risultato e' scritto qui.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import rifare_dati as RD  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402
import sezione_rete as SR  # noqa: E402


class ScrittoreCond(OS.ScrittoreL):
    def __init__(self, cartella):
        orig = RD.Pieno
        RD.Pieno = SR.PienoCond                # `RS.Scrittore.__init__` costruisce il suo modello con `RD.Pieno`
        try:
            super().__init__(cartella)
        finally:
            RD.Pieno = orig

    def penna(self, s):
        s = round(float(s), 3)
        if s not in self._pen:
            if len(self._pen) > 4:
                self._pen.clear()
            m = self.P.modello(s)
            self._pen[s] = (m, SR.PennaCond(m, self.ctx))
        return self._pen[s]


if __name__ == '__main__':
    pass
