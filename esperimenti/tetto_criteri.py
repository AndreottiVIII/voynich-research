# -*- coding: utf-8 -*-
"""IA43, modulo di supporto: i criteri scritti nella preregistrazione, come funzioni pure sui numeri (nessuna lettura di testi, nessun accesso al Voynich).

In parole semplici
- **Direzione e validita'** (da 6 libri di calibrazione piantati al 100% con la forma, ognuno col suo libro di partenza): per ogni misura la differenza (piantato - partenza); la misura e' VALIDA per
  quella forma se almeno 5 differenze su 6 hanno lo stesso segno e la media e' lontana dallo zero almeno 2 deviazioni standard dei libri senza messaggio. Il segno e' la direzione "messaggio".
- **Soglia** di una misura: il valore piu' estremo, nella direzione del messaggio, fra i 24 libri senza messaggio (un libro piantato e' "visto" da una misura se la supera).
- **k**: quante misure valide devono superare la loro soglia perche' la batteria "veda" un libro; il piu' piccolo k >= 2 per cui i falsi allarmi dei libri senza messaggio (ognuno giudicato con le
  soglie degli altri 23: "uno fuori") sono al piu' il 5%. Si calcola due volte: su tutte le misure (`k_B`) e sulle sole misure M (`k_M`, per il Voynich, che non ha giudici contro se stesso).
- **Tetto** di una cella (forma, alternative): la dose piu' bassa da cui in su (tutte le dosi della griglia, quella e le piu' alte) almeno 11 libri piantati su 12 sono visti.
Nessun risultato e' scritto qui.
"""
import math
from collections import OrderedDict

MIN_CONCORDI = 5          # su 6 libri di calibrazione
SOGLIA_SD = 2.0           # media delle differenze di calibrazione almeno cosi' lontana da zero, in deviazioni standard dei libri senza messaggio
FA_MAX = 0.05
K_MIN = 2                 # "un indizio vale solo con due misure concordi"
MIN_VISTI = 11            # libri piantati visti su 12
DOSI_PRESCRITTE = (0.05, 0.10, 0.20, 0.40, 0.70, 1.00)


def _validi(v):
    return [x for x in v if x is not None and x == x]


def media(v):
    v = _validi(v)
    return sum(v) / len(v) if v else None


def sd(v):
    v = _validi(v)
    if len(v) < 2:
        return None
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def direzioni(neg, cal):
    """neg: nome -> lista dei valori dei libri senza messaggio; cal: nome -> lista delle differenze (piantato - partenza) dei libri di calibrazione di UNA forma.
    -> nome -> dict(segno, valida, media_diff, sd_neg, concordi, n)."""
    out = OrderedDict()
    for nome, diffs in cal.items():
        d = _validi(diffs)
        s = sd(neg.get(nome, []))
        if len(d) < 3 or not s:
            out[nome] = OrderedDict([('segno', 0), ('valida', False), ('media_diff', media(d)), ('sd_neg', s), ('concordi', 0), ('n', len(d))])
            continue
        pos = sum(x > 0 for x in d)
        neg_n = sum(x < 0 for x in d)
        segno = 1 if pos >= neg_n else -1
        conc = max(pos, neg_n)
        m = sum(d) / len(d)
        minimo = MIN_CONCORDI if len(d) >= 6 else math.ceil(5 * len(d) / 6.0)
        out[nome] = OrderedDict([('segno', segno), ('valida', bool(conc >= minimo and abs(m) >= SOGLIA_SD * s)), ('media_diff', m), ('sd_neg', s), ('concordi', conc), ('n', len(d))])
    return out


def soglie(neg, dirz, escludi=None):
    """nome -> soglia: il valore piu' estremo dei libri senza messaggio nella direzione del messaggio (`escludi`: indice di un libro da lasciare fuori, per i falsi allarmi)."""
    out = OrderedDict()
    for nome, d in dirz.items():
        if not d['valida']:
            continue
        v = [x for i, x in enumerate(neg.get(nome, [])) if i != escludi and x is not None and x == x]
        if v:
            out[nome] = max(v) if d['segno'] > 0 else min(v)
    return out


def supera(v, soglia, segno):
    return v is not None and v == v and segno * (v - soglia) > 0


def visti_da(valori, sog, dirz, solo=None):
    """Le misure valide che un libro (nome -> valore) porta oltre la soglia."""
    return [n for n, t in sog.items() if (solo is None or n in solo) and supera(valori.get(n), t, dirz[n]['segno'])]


def scegli_k(neg_libri, dirz, solo=None, fa_max=FA_MAX, k_min=K_MIN):
    """neg_libri: lista di dict nome->valore (libri senza messaggio). -> (k, tabella falsi allarmi per k). Ogni libro e' giudicato con le soglie costruite sugli ALTRI."""
    neg = {n: [b.get(n) for b in neg_libri] for n in dirz}
    conti = []
    for i, b in enumerate(neg_libri):
        sog = soglie(neg, dirz, escludi=i)
        conti.append(len(visti_da(b, sog, dirz, solo)))
    n = len(neg_libri)
    fa = OrderedDict()
    validi = [m for m in dirz if dirz[m]['valida'] and (solo is None or m in solo)]
    for k in range(k_min, len(validi) + 1):
        fa[k] = sum(c >= k for c in conti) / n
    for k, f in fa.items():
        if f <= fa_max:
            return k, fa
    return None, fa


def libri_visti(libri, sog, dirz, k, solo=None):
    """Per ogni libro (dict nome->valore): True se almeno k misure valide superano la soglia."""
    return [len(visti_da(b, sog, dirz, solo)) >= k for b in libri]


def tetto(visti_per_dose, min_visti=MIN_VISTI):
    """visti_per_dose: dose -> numero di libri visti. -> la dose piu' bassa da cui in su (nella griglia) tutte le dosi hanno almeno `min_visti` libri visti; None se non c'e'."""
    dosi = sorted(visti_per_dose)
    ris = None
    for d in reversed(dosi):
        if visti_per_dose[d] is not None and visti_per_dose[d] >= min_visti:
            ris = d
        else:
            break
    return ris


def tetto_misura(valori_per_dose, sog, segno, min_visti=MIN_VISTI):
    """Il tetto di una sola misura: valori_per_dose: dose -> lista dei valori dei libri."""
    return tetto(OrderedDict((d, sum(supera(v, sog, segno) for v in vs)) for d, vs in valori_per_dose.items()), min_visti)


def lettura_tetto(t):
    """Parole per la tabella: tetto basso (sotto il 20%), medio, alto, nessuno."""
    if t is None:
        return 'nessun tetto: la batteria non vede il messaggio nemmeno alla dose piena in questa forma'
    if t < 0.20:
        return 'tetto basso (%d%%)' % round(100 * t)
    if t <= 0.40:
        return 'tetto medio (%d%%)' % round(100 * t)
    return 'tetto alto (%d%%)' % round(100 * t)


def controllo_positivo(visti_a100, n=12):
    """Forma a, alternative 1, dose 100%: la batteria deve vedere il messaggio in 12 libri su 12."""
    return visti_a100 == n


def controllo_negativo(fa_loo, fa_max=FA_MAX):
    return fa_loo is not None and fa_loo <= fa_max


if __name__ == '__main__':
    pass
