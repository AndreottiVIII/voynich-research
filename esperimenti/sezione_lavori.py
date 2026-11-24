# -*- coding: utf-8 -*-
"""IA35, modulo di supporto: l'obiettivo del ciclo (le 12 grandezze di IA34) sulla rete condizionata o sull'ablazione, i libri dell'esame, il giudice b mediato e i lavori del banco.

In parole semplici
- L'obiettivo e' quello di IA34 (`piano_lavori.z_ciclo34`: copia netta, contatto, G9, bordi d'inizio, costo di forma, parole nuove, Λ, bordi di fine, k90 su una sola meta' per candidato;
  giudici e231, e266, K; piu' la penalita' della guardia anti-copia). Cambia la rete: ogni candidato dice su quale rete si scrive (`C` condizionata, `A` ablazione).
- Libri dell'esame: `spec` = ['L', u, rete] (14 manopole di IA33 sulla rete `C` o `A`), ['ORA', m] (oracolo stimato del mondo `struttura2`), ['GEMS'] (gemello).
- Lavori nuovi: `NM8` (le otto misure di struttura di un libro), `B35` (il giudice b mediato su un insieme di libri: `sezione_giudice`).
Le funzioni lavorano dentro un processo che ha chiamato `rifare_misure.prepara(mondo, cartella)`; le reti sono in `<cartella>/rete_C` e `<cartella>/rete_A`.
"""
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
import righello_giudici as RG  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_dati as RD  # noqa: E402
import oracolo_misure as OM  # noqa: E402
import piano_lavori as PL  # noqa: E402
import sezione_mondo as SMO  # noqa: E402
import sezione_misure as SM  # noqa: E402
import sezione_giudice as SG  # noqa: E402
import sezione_scrittura as SS  # noqa: E402

OBI_MISURE35 = PL.OBI_MISURE34
OBI_GIUDICI35 = PL.OBI_GIUDICI34
OBIETTIVO35 = PL.OBIETTIVO34
FUORI_MISURE35 = ('D', 'R_rel') + SM.NOMI_NM8
_W = RM._W


def scrittore35(rete):
    k = 'SC_' + rete
    if k not in _W:
        _W[k] = SS.ScrittoreCond(os.path.join(_W['cart'], 'rete_' + rete))
    return _W[k]


def valuta35(args):
    """args = (generazione, indice, u, seme, fogli, con_k90, rete). Scrive un mezzo libro e lo misura. -> dict (come `piano_lavori.valuta34`, piu' `rete`)."""
    gen, i, u, seme, fogli, con_k90, rete = args
    inizio = time.time()
    try:
        S = scrittore35(rete)
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
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = RM.valuta_copia(conti)
        zs = PL.z_ciclo34(v, vh)
        a = [min(abs(z), RM.ZCAP32) for z in zs.values()]
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('rete', rete), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('somma', float(sum(a))), ('n', len(a)), ('obiettivo_puro', float(np.mean(a))), ('penalita', pen), ('obiettivo', float(np.mean(a)) + pen),
                            ('z', zs), ('valori', v), ('vero_meta', vh), ('copia', q), ('copia_violazioni', viol), ('pagine', len(rows)), ('pagine_K', npag),
                            ('parole', sum(len(p) for _, _, p in t)), ('secondi_scrittura', round(t_scrittura, 1)), ('secondi_k90', round(t_k90, 1)),
                            ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


def scrivi_libro35(tipo, i, spec, seme):
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    man = None
    if os.path.exists(p):
        t = I7.leggi_file(p)
    else:
        if spec[0] == 'L':
            t, man = scrittore35(spec[2]).libro33(np.asarray(spec[1], float), seme, None)
        elif spec[0] == 'ORA':
            t = SMO.libro_oracolo(I7.libro_vero(), OM._base_originale(), f_add, int(spec[1]), seme)
        elif spec[0] == 'GEMS':
            t = SMO.libro_gemello(OM._base_originale(), seme)
        else:
            raise ValueError(spec)
        I7.scrivi_file(t, p + '.tmp', 'ia35, libro %s %d, mondo %s' % (tipo, i, _W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('spec', spec[0]), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_NM8(nome):
    inizio = time.time()
    c = I7.contesto_A()
    out = OrderedDict([('lavoro', 'NM|%s' % nome)])
    out.update(SM.misure_testo(B.rows_testo(nome), c['ids']))
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_riferimento_NM8():
    inizio = time.time()
    c = I7.contesto_A()
    r = SM.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s))
    r['lavoro'] = 'RIF_NM'
    r['secondi'] = round(time.time() - inizio, 1)
    return r


def lavoro_B35(tipo, nomi, seme):
    """Il giudice b mediato (`sezione_giudice.esame_b_medio`) sull'insieme di libri `nomi` (nomi del banco)."""
    inizio = time.time()
    c = I7.contesto_A()
    fuori = set(RD.divisione_fogli()[2])
    pagine = [p for p in c['ids'] if I7.foglio_di(p) in fuori]
    voc = RG.vocabolario_N(c['vere'])
    r = SG.esame_b_medio(c['vere'], [B.rows_testo(n) for n in nomi], pagine, I7.foglio_di, voc, seme=seme)
    out = OrderedDict([('lavoro', 'B35|%s' % tipo)])
    out.update(r)
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_banco35(args):
    inizio = time.time()
    try:
        if args[0] == 'libro35':
            return scrivi_libro35(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'valuta':
            return valuta35(args[1:])
        if args[0] == 'NM':
            return lavoro_NM8(args[1])
        if args[0] == 'B35':
            return lavoro_B35(args[1], args[2], int(args[3]))
        return OM.lavoro_banco33(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3] if not isinstance(a, list))), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])


if __name__ == '__main__':
    pass
