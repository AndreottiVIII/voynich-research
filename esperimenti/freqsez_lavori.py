# -*- coding: utf-8 -*-
"""IA37, modulo di supporto: i lavori di IA36 (`prudente_lavori`) con lo scrittore a frequenze per sezione, piu' i lavori nuovi della diagnosi.

In parole semplici
- `prudente_lavori.valuta36`, `scrivi_libro36`, `lavoro_GI` ecc. chiamano `scrittore36(rete)`: qui quella funzione e' sostituita (una sola volta, all'importazione) da `scrittore37`, che
  costruisce `freqsez_scrittura.ScrittoreFreq` sulla stessa rete condizionata `C` (copiata da IA35). Il resto (obiettivo a 13 grandezze con `riuso_sez`, guardie, libri, giudici) e' IA36 senza modifiche.
- Lavori nuovi: `DV` (divergenza fra sezioni di un libro, `freqsez_tabelle.divergenza_sezioni`; descrittiva) e `RIF_DV` (la stessa sul testo vero del mondo).
Nessun risultato e' scritto qui.
"""
import os
import sys
import time
from collections import OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import righello_banco as B  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import prudente_lavori as PLV  # noqa: E402
import freqsez_scrittura as FW  # noqa: E402
import freqsez_tabelle as FT  # noqa: E402

_W = PLV._W


def scrittore37(rete='C'):
    k = 'SF_' + rete
    if k not in _W:
        _W[k] = FW.ScrittoreFreq(os.path.join(_W['cart'], 'rete_' + rete))
    return _W[k]


PLV.scrittore36 = scrittore37                           # una sola volta, all'importazione: valuta36, scrivi_libro36 e lavoro_GI usano lo scrittore a frequenze per sezione


def lavoro_DV(nome):
    inizio = time.time()
    c = I7.contesto_A()
    out = OrderedDict([('lavoro', 'DV|%s' % nome)])
    out.update(FT.divergenza_sezioni(B.rows_testo(nome), c['ids']))
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_riferimento_DV():
    """La divergenza fra sezioni del testo vero del mondo (libro intero, pagine dei giudici)."""
    inizio = time.time()
    c = I7.contesto_A()
    out = FT.divergenza_sezioni(c['vere'], c['ids'])
    out['lavoro'] = 'RIF_DV'
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_banco37(args):
    if args[0] == 'DV':
        try:
            return lavoro_DV(args[1])
        except Exception as e:                                            # noqa: BLE001
            import traceback
            return OrderedDict([('lavoro', 'DV|%s' % args[1]), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])
    return PLV.lavoro_banco36(args)


if __name__ == '__main__':
    pass
