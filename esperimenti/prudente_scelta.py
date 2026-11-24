# -*- coding: utf-8 -*-
"""IA36, modulo di supporto: la SCELTA PRUDENTE (funzioni pure, provabili su numeri finti).

In parole semplici
- Il problema (IA34, IA35): il ciclo a prove ed errori scende sull'obiettivo spingendo le manopole agli estremi e, nel mondo di regola nota, rovina la struttura che non vede
  (IA35, `struttura2`: obiettivo da 5,41 a 4,19 ma 2 misure tenute fuori su 10 al vero).
- La protezione usa strumenti DISTINTI dall'esame (le dieci misure d'esame non entrano mai qui): cinque **misure di guardia** (`prudente_misure`).
    * Per ogni guardia il "permesso" e' max(ZG_ABS, min(ZG_TETTO, |z del neutro| + DELTA_G)): la guardia puo' stare entro ZG_ABS dal vero, oppure non peggio del neutro (le manopole neutre della stessa
      rete, rivalutate all'inizio) piu' DELTA_G, ma mai oltre ZG_TETTO (il neutro puo' essere lontanissimo dal vero: il tetto evita che il permesso diventi vuoto). L'**eccesso** e' quanto |z| supera il permesso (tetto ZCAP_G); la **penalita' di guardia** e' la media degli eccessi sulle guardie.
    * Obiettivo prudente = obiettivo + W_G x penalita' di guardia. E' quello che CMA-ES minimizza e con cui si scelgono i finalisti.
    * **Scelta prudente fra i finalisti:** si considerano "prudenti" i finalisti con penalita' di guardia <= PEN_MAX; vince il minimo di obiettivo prudente fra loro; se nessuno e' prudente vince
      quello con la penalita' piu' bassa (e lo si scrive).
    * **Partenza prudente:** il ciclo parte dal punto scelto da IA35 se questo e' prudente; altrimenti dal migliore (obiettivo prudente) fra quel punto, il punto di IA33 e il neutro.
- Senza protezione (`W_G36=0`, `PRUDENTE36=0`): l'obiettivo prudente e' l'obiettivo e si sceglie il minimo, come in IA35. Serve alla prova sul mondo di sviluppo.
Variabili: ZG_ABS36 (2), DELTA_G36 (1), ZG_TETTO36 (4), W_G36 (2), PEN_MAX36 (0,25), ZCAP_G36 (10), PRUDENTE36 (1).
Nessun risultato e' scritto qui.
"""
import os
from collections import OrderedDict

import numpy as np

ZG_ABS = float(os.environ.get('ZG_ABS36', 2.0))
DELTA_G = float(os.environ.get('DELTA_G36', 1.0))
ZG_TETTO = float(os.environ.get('ZG_TETTO36', 4.0))
W_G = float(os.environ.get('W_G36', 2.0))
PEN_MAX = float(os.environ.get('PEN_MAX36', 0.25))
ZCAP_G = float(os.environ.get('ZCAP_G36', 10.0))
PRUDENTE = os.environ.get('PRUDENTE36', '1') == '1'


def permesso(zn):
    """Il permesso di una guardia dato il suo z (in scale) per le manopole neutre (None -> solo ZG_ABS)."""
    return max(ZG_ABS, min(ZG_TETTO, (abs(zn) + DELTA_G) if zn is not None else 0.0))


def eccessi(zg, zn):
    """Eccesso di ogni guardia di `zg` (dizionario nome -> z) sul suo permesso. `zn`: dizionario nome -> z del neutro (puo' essere vuoto)."""
    zn = zn or {}
    return OrderedDict((k, min(ZCAP_G, max(0.0, abs(z) - permesso(zn.get(k))))) for k, z in zg.items() if z is not None)


def penalita_guardie(zg, zn):
    """Media degli eccessi sulle guardie presenti (0 se non ce ne sono)."""
    e = eccessi(zg, zn)
    return float(np.mean(list(e.values()))) if e else 0.0


def media_z(lista):
    """Media, guardia per guardia, dei dizionari di z di piu' valutazioni (mezzi libri). -> dict nome -> z medio (solo le guardie presenti in almeno una)."""
    out = OrderedDict()
    nomi = []
    for d in lista:
        for k in d:
            if k not in nomi:
                nomi.append(k)
    for k in nomi:
        v = [d[k] for d in lista if d.get(k) is not None]
        if v:
            out[k] = float(np.mean(v))
    return out


def obiettivo_prudente(obiettivo, pen, peso=None):
    peso = W_G if peso is None else peso
    return float(obiettivo + peso * pen)


def valore_candidato(rs, zn, guardie, peso=None):
    """Il valore di un candidato del ciclo dalle sue valutazioni `rs` (le due meta'; ognuna con `somma`, `n`, `penalita` e `zg`): obiettivo (come `media_valutazioni` di IA35, che resta
    la media dei z con tetto piu' la penalita' di copia) piu' W_G x penalita' di guardia sulla media dei z di guardia delle valutazioni. -> (valore prudente, obiettivo, penalita' di guardia) o None."""
    ok = [r for r in rs if not r.get('errore')]
    if not ok:
        return None
    ob = float(sum(r['somma'] for r in ok) / sum(r['n'] for r in ok) + np.mean([r['penalita'] for r in ok]))
    zg = media_z([{k: r['zg'][k] for k in guardie if k in r.get('zg', {})} for r in ok])
    pen = penalita_guardie(zg, zn)
    return obiettivo_prudente(ob, pen, peso), ob, pen


def scegli_finalista(fin, solo_rete='C'):
    """Sceglie il vincitore fra i finalisti `fin` (nome -> dict con `rete`, `obiettivo`, `penalita_guardia`, `obiettivo_prudente`). -> (nome, motivo)."""
    cand = [n for n, x in fin.items() if x.get('obiettivo') is not None and x.get('rete') == solo_rete]
    if not cand:
        return None, 'nessun finalista valutato'
    if not PRUDENTE:
        return min(cand, key=lambda n: fin[n]['obiettivo']), 'senza protezione: minimo dell\'obiettivo'
    ok = [n for n in cand if fin[n]['penalita_guardia'] <= PEN_MAX]
    if ok:
        n = min(ok, key=lambda m: fin[m]['obiettivo_prudente'])
        return n, 'minimo dell\'obiettivo prudente fra i %d finalisti prudenti (penalita\' di guardia <= %.2f)' % (len(ok), PEN_MAX)
    n = min(cand, key=lambda m: (fin[m]['penalita_guardia'], fin[m]['obiettivo_prudente']))
    return n, 'NESSUN finalista prudente: scelto quello con la penalita\' di guardia piu\' bassa'


def scegli_partenza(cand):
    """La partenza prudente. `cand`: nome -> dict con `obiettivo_prudente`, `penalita_guardia` (in ordine di preferenza: il primo e' il punto di IA35). -> (nome, motivo)."""
    nomi = list(cand)
    if not PRUDENTE:
        return nomi[0], 'senza protezione: si parte dal punto di IA35'
    primo = nomi[0]
    if cand[primo]['penalita_guardia'] <= PEN_MAX:
        return primo, 'il punto di IA35 e\' prudente (penalita\' di guardia %.2f <= %.2f)' % (cand[primo]['penalita_guardia'], PEN_MAX)
    n = min(nomi, key=lambda m: cand[m]['obiettivo_prudente'])
    return n, 'il punto di IA35 non e\' prudente (penalita\' di guardia %.2f > %.2f): si parte dal migliore per obiettivo prudente' % (cand[primo]['penalita_guardia'], PEN_MAX)


if __name__ == '__main__':
    pass
