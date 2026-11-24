# -*- coding: utf-8 -*-
"""IA36, modulo di supporto: l'obiettivo del ciclo (12 grandezze di IA34 piu' `riuso_sez`) con le guardie, i libri dell'esame e i lavori del banco.

In parole semplici
- Una valutazione (`valuta36`) scrive un MEZZO libro con lo scrittore a 16 manopole (memoria di sezione) sopra la rete condizionata `C` (la variante scelta in IA35, gia' addestrata) e lo misura come in
  IA35 (12 grandezze di IA34, k90 su una meta' per candidato) piu': `riuso_sez` (z come le altre misure, ENTRA nell'obiettivo se `RIUSO_OBIETTIVO36=1`, predefinito) e le CINQUE GUARDIE (z in scale;
  NON entrano nell'obiettivo: pagano una penalita' se escono dal permesso, vedi `prudente_scelta`). Le dieci misure d'esame non si calcolano nel ciclo.
- `libro36`: un libro intero con spec ['L', cubo a 16, rete]; ['ORA', m], ['GEMS'] come in IA35. `GU`: le guardie e `riuso_sez` di un libro dell'esame (valori; i z si fanno all'analisi). `GI`: le guardie di un libro INTERO scritto per il controllo dei finalisti (come quelli dell'esame).
- Le funzioni lavorano dentro un processo che ha chiamato `rifare_misure.prepara(mondo, cartella)`; la rete e' in `<cartella>/rete_C` (copiata da IA35 o addestrata nelle prove).
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
import oracolo_misure as OM  # noqa: E402
import piano_lavori as PL  # noqa: E402
import sezione_mondo as SMO  # noqa: E402
import sezione_lavori as SL  # noqa: E402
import prudente_misure as PMG  # noqa: E402
import prudente_scrittura as PW  # noqa: E402

RIUSO_OBIETTIVO = os.environ.get('RIUSO_OBIETTIVO36', '1') == '1'
OBIETTIVO36 = PL.OBIETTIVO34 + (PMG.EXTRA_OBIETTIVO36 if RIUSO_OBIETTIVO else ())
GUARDIE36 = PMG.GUARDIE36
FUORI_MISURE36 = SL.FUORI_MISURE35
_W = RM._W


def scrittore36(rete='C'):
    k = 'SZ_' + rete
    if k not in _W:
        _W[k] = PW.ScrittoreSez(os.path.join(_W['cart'], 'rete_' + rete))
    return _W[k]


def carica_guardie():
    """Il riferimento delle guardie del mondo (`guardie.json` nella cartella del mondo), se c'e'."""
    p = os.path.join(_W['cart'], 'guardie.json')
    _W['gu'] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    return _W['gu']


def vero_guardie(fogli):
    """Le sei misure (guardie e riuso_sez) sulle pagine VERE dei fogli `fogli` (stesse pagine e stesso ordine di `rifare_misure.vero_su`)."""
    key = ('vero_g', tuple(fogli))
    if key not in _W:
        c = I7.contesto_A()
        ins = set(fogli)
        rows = OrderedDict((p, c['vere'][p]) for p in c['ids'] if I7.foglio_di(p) in ins)
        _W[key] = PMG.misure_testo(rows)
    return _W[key]


def z_guardie36(rows, fogli):
    """z (in scale) delle guardie e di riuso_sez di un mezzo libro `rows` rispetto al vero degli stessi fogli. -> (dict z, dict valori)."""
    if _W.get('gu') is None:
        return OrderedDict(), OrderedDict()
    v = PMG.misure_testo(rows)
    z = PMG.z_misure(v, vero_guardie(fogli), _W['gu']['scala'])
    return z, v


def valuta36(args):
    """args = (generazione, indice, u, seme, fogli, con_k90, rete). Scrive un mezzo libro e lo misura. -> dict (come `sezione_lavori.valuta35`, piu' `zg` (guardie), `riuso_sez`)."""
    gen, i, u, seme, fogli, con_k90, rete = args
    inizio = time.time()
    try:
        S = scrittore36(rete)
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
        zg, vg = z_guardie36(rows, fogli)
        if RIUSO_OBIETTIVO and 'riuso_sez' in zg:
            zs['riuso_sez'] = zg['riuso_sez']
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = RM.valuta_copia(conti)
        a = [min(abs(z), RM.ZCAP32) for z in zs.values()]
        zguardie = OrderedDict((k, zg[k]) for k in GUARDIE36 if k in zg)
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('rete', rete), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('somma', float(sum(a))), ('n', len(a)), ('obiettivo_puro', float(np.mean(a))), ('penalita', pen), ('obiettivo', float(np.mean(a)) + pen),
                            ('z', zs), ('zg', zguardie), ('valori', v), ('valori_g', vg), ('vero_meta', vh), ('copia', q), ('copia_violazioni', viol), ('pagine', len(rows)), ('pagine_K', npag),
                            ('parole', sum(len(p) for _, _, p in t)), ('secondi_scrittura', round(t_scrittura, 1)), ('secondi_k90', round(t_k90, 1)),
                            ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


def scrivi_libro36(tipo, i, spec, seme):
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    man = None
    if os.path.exists(p):
        t = I7.leggi_file(p)
    else:
        if spec[0] == 'L':
            t, man = scrittore36(spec[2]).libro33(np.asarray(spec[1], float), seme, None)
        elif spec[0] == 'ORA':
            t = SMO.libro_oracolo(I7.libro_vero(), OM._base_originale(), f_add, int(spec[1]), seme)
        elif spec[0] == 'GEMS':
            t = SMO.libro_gemello(OM._base_originale(), seme)
        else:
            raise ValueError(spec)
        I7.scrivi_file(t, p + '.tmp', 'ia36, libro %s %d, mondo %s' % (tipo, i, _W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('spec', spec[0]), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_GU(nome):
    """Le guardie e `riuso_sez` di un libro dell'esame (valori; i z si fanno con il riferimento del testo vero intero)."""
    inizio = time.time()
    c = I7.contesto_A()
    out = OrderedDict([('lavoro', 'GU|%s' % nome)])
    out.update(PMG.misure_testo(B.rows_testo(nome), c['ids']))
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_GI(nome, rep, u, seme, rete):
    """Il controllo di guardia su un LIBRO INTERO (come quelli dell'esame): scrive un libro con tutte le pagine (senza salvarlo) e ne calcola le guardie e `riuso_sez` sulle pagine dei giudici."""
    inizio = time.time()
    S = scrittore36(rete)
    t, man = S.libro33(np.asarray(u, float), seme, None)
    c = I7.contesto_A()
    out = OrderedDict([('lavoro', 'GI|%s|%d' % (nome, rep)), ('nome', nome), ('rep', rep), ('seme', seme), ('parole', sum(len(p) for _, _, p in t))])
    out['valori'] = PMG.misure_testo(I7.libro_A_da_righe(t), c['ids'])
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_riferimento_guardie():
    inizio = time.time()
    c = I7.contesto_A()
    r = PMG.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s))
    r['lavoro'] = 'RIF_GU'
    r['secondi'] = round(time.time() - inizio, 1)
    return r


def lavoro_banco36(args):
    inizio = time.time()
    try:
        if args[0] == 'libro36':
            return scrivi_libro36(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'valuta':
            return valuta36(args[1:])
        if args[0] == 'GU':
            return lavoro_GU(args[1])
        if args[0] == 'GI':
            return lavoro_GI(args[1], int(args[2]), args[3], int(args[4]), args[5])
        if args[0] == 'NM':
            return SL.lavoro_NM8(args[1])
        if args[0] == 'B35':
            return SL.lavoro_B35(args[1], args[2], int(args[3]))
        return OM.lavoro_banco33(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3] if not isinstance(a, list))), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])


if __name__ == '__main__':
    pass
