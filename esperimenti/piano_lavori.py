# -*- coding: utf-8 -*-
"""IA34, modulo di supporto: l'obiettivo del ciclo (12 grandezze), i libri dell'esame (scrittore con il piano del libro, oracolo e gemello del mondo `struttura`) e i lavori del banco.

In parole semplici
- Obiettivo di una valutazione = media di min(|z|, 10) su **dodici grandezze di allenamento**: le nove di IA33 (copia netta, contatto, G9, bordi d'inizio, costo di forma, parole nuove;
  giudici e231, e266, K) piu' **Λ, bordi di fine riga e k90** (la struttura su scala di riga e di pagina che IA33 aveva perso). z come in IA33 (misure rispetto al vero degli stessi fogli,
  scala del banco; giudici rispetto al nullo), piu' la penalita' della guardia anti-copia. **k90 si calcola su una sola delle due meta' di ogni candidato** (la meta' 0: costa una rete
  piccola, circa 40 secondi): l'obiettivo di un candidato e' la somma dei z (con tetto) delle due meta' divisa per il loro numero (23: k90 pesa meta' degli altri).
- Un lavoro "libro34" scrive un libro intero con la `spec`: ['L', u] (scrittore con il piano del libro, cubo di 17 manopole), ['ORA', m] (oracolo stimato del mondo `struttura` con m volte
  il testo), ['GEMS'] (gemello: la vera regola con semi nuovi). Un lavoro "NM" calcola le sei misure nuove (`piano_misure`) di un libro.
Le funzioni lavorano dentro un processo che ha chiamato `rifare_misure.prepara(mondo, cartella)` (come per IA33).
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
import ia07_voynich_neurale as I7  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_dati as RD  # noqa: E402
import oracolo_misure as OM  # noqa: E402
import piano_mondo as PM  # noqa: E402
import piano_misure as PMS  # noqa: E402
import piano_scrittura as PS  # noqa: E402

OBI_MISURE34 = ('copia_netta', 'contatto', 'G9', 'bordi_inizio', 'costo_forma', 'parole_nuove', 'lam', 'bordi_fine', 'k90')
OBI_GIUDICI34 = ('e231', 'e266', 'K')
OBIETTIVO34 = OBI_MISURE34 + OBI_GIUDICI34
FUORI_MISURE34 = ('D', 'R_rel') + PMS.NOMI_NM
_W = RM._W


def scrittore34():
    if 'SP' not in _W:
        _W['SP'] = PS.ScrittorePiano(os.path.join(_W['cart'], 'modello'))
    return _W['SP']


def k90_vero_su(fogli):
    """k90 sulle pagine VERE dei fogli `fogli` (stessa rete piccola e stesso seme dei testi misurati)."""
    key = ('k90_vero', tuple(fogli))
    if key not in _W:
        c = I7.contesto_A()
        ins = set(fogli)
        rows = OrderedDict((p, c['vere'][p]) for p in c['ids'] if I7.foglio_di(p) in ins)
        _W[key] = B.corse_gru(B.blocchi_di(rows), 'veroH', 'K', B.SEME_GRU)['k90']
    return _W[key]


def z_ciclo34(v, vh):
    rif = _W['rif']
    zs = OrderedDict()
    for m in OBI_MISURE34:
        if v.get(m) is not None and vh.get(m) is not None and rif['scala'].get(m):
            zs[m] = (v[m] - vh[m]) / rif['scala'][m]
    for j in OBI_GIUDICI34:
        nu = rif['nullo'].get(j)
        if v.get(j) is not None and nu and nu['sd']:
            zs[j] = (v[j] - nu['media']) / nu['sd']
    return zs


def valuta34(args):
    """args = (generazione, indice, u, seme, fogli, con_k90). Scrive un mezzo libro e lo misura. -> dict (come `oracolo_misure.valuta33`, con `somma` e `n` dei z con tetto)."""
    gen, i, u, seme, fogli, con_k90 = args
    inizio = time.time()
    try:
        S = scrittore34()
        t, man = S.libro34(np.asarray(u, float), seme, fogli)
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
            vh['k90'] = k90_vero_su(fogli)
            t_k90 = time.time() - t1
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = RM.valuta_copia(conti)
        zs = z_ciclo34(v, vh)
        a = [min(abs(z), RM.ZCAP32) for z in zs.values()]
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('somma', float(sum(a))), ('n', len(a)), ('obiettivo_puro', float(np.mean(a))), ('penalita', pen), ('obiettivo', float(np.mean(a)) + pen),
                            ('z', zs), ('valori', v), ('vero_meta', vh), ('copia', q), ('copia_violazioni', viol), ('pagine', len(rows)), ('pagine_K', npag),
                            ('parole', sum(len(p) for _, _, p in t)), ('secondi_scrittura', round(t_scrittura, 1)), ('secondi_k90', round(t_k90, 1)),
                            ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


def scrivi_libro34(tipo, i, spec, seme):
    """Un libro INTERO nel formato del banco. -> dict (come `oracolo_misure.scrivi_libro33`)."""
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    man = None
    if os.path.exists(p):
        t = I7.leggi_file(p)
    else:
        if spec[0] == 'L':
            t, man = scrittore34().libro34(np.asarray(spec[1], float), seme, None)
        elif spec[0] == 'ORA':
            t = PM.libro_oracolo(I7.libro_vero(), OM._base_originale(), f_add, int(spec[1]), seme)
        elif spec[0] == 'GEMS':
            t = PM.libro_gemello(OM._base_originale(), seme)
        else:
            raise ValueError(spec)
        I7.scrivi_file(t, p + '.tmp', 'ia34, libro %s %d, mondo %s' % (tipo, i, _W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('spec', spec[0]), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_NM(nome):
    inizio = time.time()
    c = I7.contesto_A()
    out = OrderedDict([('lavoro', 'NM|%s' % nome)])
    out.update(PMS.misure_testo(B.rows_testo(nome), c['ids']))
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_riferimento_NM():
    """Le sei misure nuove sul testo vero del mondo e la loro scala (divisioni per fogli del banco)."""
    inizio = time.time()
    c = I7.contesto_A()
    r = PMS.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s))
    r['lavoro'] = 'RIF_NM'
    r['secondi'] = round(time.time() - inizio, 1)
    return r


def lavoro_banco34(args):
    inizio = time.time()
    try:
        if args[0] == 'libro34':
            return scrivi_libro34(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'valuta':
            return valuta34(args[1:])
        if args[0] == 'NM':
            return lavoro_NM(args[1])
        return OM.lavoro_banco33(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3])), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])


if __name__ == '__main__':
    pass
