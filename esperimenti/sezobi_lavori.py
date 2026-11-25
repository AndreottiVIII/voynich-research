# -*- coding: utf-8 -*-
"""IA38, modulo di supporto: la valutazione del ciclo di IA37 (`prudente_lavori.valuta36` con lo scrittore a frequenze per sezione) con DUE grandezze nuove nell'obiettivo: `div_bigr` e `div_par`.

In parole semplici
- `valuta38` e' `valuta36` (copiata qui perche' deve avere in mano le righe del mezzo libro): scrive un mezzo libro con lo scrittore a 15 manopole (`freqsez_scrittura.ScrittoreFreq`), lo misura come in IA37 (12 grandezze di
  IA34, `riuso_sez`, cinque guardie) e in piu' calcola la differenza fra sezioni (`sezobi_misure`) sulle sole pagine d'addestramento del mezzo libro, rispetto al vero delle stesse pagine.
- Le due grandezze entrano nell'obiettivo come le altre (z, min(|z|, 10)) con peso `PESO_SEZ38` ciascuna (predefinito 1; **con peso 0 non entrano e il risultato e' ESATTAMENTE quello di `valuta36`**: provato).
  Se non entrano si registrano lo stesso in `zdiv`.
Nessun risultato e' scritto qui.
"""
import json
import os
import sys
import time
from collections import OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import righello_banco as B  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_dati as RD  # noqa: E402
import piano_lavori as PL  # noqa: E402
import piano_misure as PMS  # noqa: E402
import prudente_lavori as PLV  # noqa: E402
import freqsez_lavori as FL  # noqa: E402
import sezobi_misure as SO  # noqa: E402

PESO_SEZ = float(os.environ.get('PESO_SEZ38', 1.0))
OBIETTIVO38 = PLV.OBIETTIVO36 + (SO.NOMI_OBI if PESO_SEZ > 0 else ())
_W = RM._W


def carica_div():
    """Il riferimento della differenza fra sezioni (`div_ref38.json` nella cartella del mondo), se c'e'."""
    p = os.path.join(_W['cart'], 'div_ref38.json')
    _W['div38'] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    return _W['div38']


def _sp():
    if 'sp38' not in _W:
        _W['sp38'] = {p: k[0] for p, k in PMS.chiavi_pagina().items()}
    return _W['sp38']


def vero_div(fogli):
    """(valore del vero, Spec) sulle pagine d'addestramento dei fogli `fogli` (le stesse pagine e lo stesso ordine di `rifare_misure.vero_su`)."""
    key = ('vero_div38', tuple(fogli))
    if key not in _W:
        c = I7.contesto_A()
        ins = set(fogli)
        f_add = RD.divisione_fogli()[0]
        pagine = SO.pagine_addestramento([p for p in c['ids'] if I7.foglio_di(p) in ins], f_add)
        spec = SO.Spec(c['vere'], pagine, _sp())
        _W[key] = (SO.div_con(c['vere'], pagine, spec, _sp()), spec, pagine)
    return _W[key]


def z_div(rows, fogli):
    """z (in scale) di `div_bigr` e `div_par` di un mezzo libro `rows`, e i valori. -> (dict z, dict valori)."""
    rif = _W.get('div38')
    if rif is None:
        return OrderedDict(), OrderedDict()
    (vb, vp), spec, pagine = vero_div(fogli)
    cb, cp = SO.div_con(rows, [p for p in pagine if p in rows], spec, _sp())
    val = OrderedDict([('div_bigr', cb), ('div_par', cp)])
    ver = {'div_bigr': vb, 'div_par': vp}
    z = OrderedDict()
    for n in SO.NOMI_OBI:
        if val[n] is not None and ver[n] is not None and rif['scala'].get(n):
            z[n] = (val[n] - ver[n]) / rif['scala'][n]
    return z, val


def valuta38(args):
    """args = (generazione, indice, u, seme, fogli, con_k90, rete). Come `prudente_lavori.valuta36`, piu' `div_bigr` e `div_par` (nell'obiettivo se `PESO_SEZ38` > 0)."""
    gen, i, u, seme, fogli, con_k90, rete = args
    inizio = time.time()
    try:
        S = FL.scrittore37(rete)
        t, man = S.libro33(np.asarray(u, float), seme, fogli)
        t_scrittura = time.time() - inizio
        rows = I7.libro_A_da_righe(t)
        v = OrderedDict((m, None) for m in list(B.MISURE) + list(B.GIUDICI))
        m = B.lavoro_M('cand', rows=rows)
        for k in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine'):
            v[k] = m[k]
        v['costo_forma'], v['parole_nuove'] = RM.forma_testo(rows)
        j = I7.giudica(t)
        v['e231'], v['e266'] = j['AUC_e231'], j['AUC_e266']
        v['K'], npag = RM.auc_K(rows)
        t_k90 = 0.0
        vh = dict(RM.vero_su(fogli))
        if con_k90:
            t1 = time.time()
            v['k90'] = B.corse_gru(B.blocchi_di(rows), 'cand', 'K', B.SEME_GRU)['k90']
            vh['k90'] = PL.k90_vero_su(fogli)
            t_k90 = time.time() - t1
        zs = PL.z_ciclo34(v, vh)
        zg, vg = PLV.z_guardie36(rows, fogli)
        if PLV.RIUSO_OBIETTIVO and 'riuso_sez' in zg:
            zs['riuso_sez'] = zg['riuso_sez']
        zd, vd = z_div(rows, fogli)
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = RM.valuta_copia(conti)
        a = [min(abs(z), RM.ZCAP32) for z in zs.values()]
        somma, n = float(sum(a)), len(a)
        if PESO_SEZ > 0:
            for nome, z in zd.items():
                zs[nome] = z
                somma += PESO_SEZ * min(abs(z), RM.ZCAP32)
                n += PESO_SEZ
        zguardie = OrderedDict((k, zg[k]) for k in PLV.GUARDIE36 if k in zg)
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('rete', rete), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('somma', somma), ('n', n), ('obiettivo_puro', somma / n), ('penalita', pen), ('obiettivo', somma / n + pen),
                            ('z', zs), ('zdiv', zd), ('valori_div', vd), ('zg', zguardie), ('valori', v), ('valori_g', vg), ('vero_meta', vh), ('copia', q), ('copia_violazioni', viol),
                            ('pagine', len(rows)), ('pagine_K', npag), ('parole', sum(len(p) for _, _, p in t)), ('secondi_scrittura', round(t_scrittura, 1)), ('secondi_k90', round(t_k90, 1)),
                            ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


def lavoro_riferimento_div38():
    """Il riferimento della differenza fra sezioni: vero e scala sui soli fogli d'addestramento (`sezobi_misure.riferimento`)."""
    inizio = time.time()
    c = I7.contesto_A()
    f_add = RD.divisione_fogli()[0]
    r = SO.riferimento(c['vere'], c['ids'], lambda s: B.dividi_meta(s), f_add)
    r['lavoro'] = 'RIF_DIV38'
    r['secondi'] = round(time.time() - inizio, 1)
    return r


def lavoro_banco38(args):
    if args[0] == 'valuta':
        return valuta38(args[1:])
    return FL.lavoro_banco37(args)


if __name__ == '__main__':
    pass
