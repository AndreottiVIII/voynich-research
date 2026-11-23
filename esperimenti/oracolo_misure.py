# -*- coding: utf-8 -*-
"""IA33, modulo di supporto: l'obiettivo della parte L, la scrittura dei libri dell'esame (L, oracolo, gemello, baseline classico) e i lavori del banco.

In parole semplici
- L'obiettivo e' quello di IA32 (`rifare_misure`, importato senza modificarlo: stesso tetto z = 10, stessa penalita' di copia, stessi mezzi libri con il "vero degli stessi
  fogli") PIU' la quota di parole nuove fra le grandezze di allenamento: nove grandezze (copia netta, contatto, G9, bordi d'inizio, costo di forma, **parole nuove**; giudici e231, e266, K).
  Le misure tenute fuori dal ciclo, guardate solo all'esame, sono Λ, D, bordi di fine riga, k90 e R_rel; i giudici mai visti N, KN e b.
- Un lavoro "libro" scrive un libro intero con uno dei generatori dell'esame, scelto dalla `spec`:
    ['L', u]       lo scrittore piu' libero (`oracolo_scrittura.ScrittoreL`) con le manopole `u`;
    ['KN', m]      l'oracolo ufficiale: Kneser-Ney di ordine 3 stimato sui conteggi dei fogli d'addestramento del mondo (m = 1, 2, 4: volte il testo);
    ['MLE', m]     l'oracolo secondario: gli stessi conteggi grezzi della vera catena;
    ['GEM']        il gemello: la VERA catena (stimata sul libro intero) con un seme nuovo (solo nel mondo `markov2`);
    ['NGR']        il baseline classico: KN con l'ordine scelto sulla validazione (3-6), sui fogli d'addestramento.
  Il file e' scritto come quello degli altri libri del banco (`tar_<tipo>_<i>.txt`) e ha i conti di copia come in IA32.
Le funzioni lavorano dentro un processo che ha chiamato `rifare_misure.prepara(mondo, cartella33)`.
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
import righello_testi as RT  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import rifare_misure as RM  # noqa: E402
import rifare_scrittura as RS  # noqa: E402
import rifare_dati as RD  # noqa: E402
import oracolo_catene as OC  # noqa: E402
import oracolo_scrittura as OS  # noqa: E402

OBI_MISURE33 = ('copia_netta', 'contatto', 'G9', 'bordi_inizio', 'costo_forma', 'parole_nuove')
OBI_GIUDICI33 = ('e231', 'e266', 'K')
OBIETTIVO33 = OBI_MISURE33 + OBI_GIUDICI33
FUORI_MISURE33 = ('lam', 'D', 'bordi_fine', 'k90', 'R_rel')
FUORI_GIUDICI33 = ('N', 'KN', 'b')

_W = RM._W
_M = {}


def scrittore33():
    if 'SL' not in _W:
        _W['SL'] = OS.ScrittoreL(os.path.join(_W['cart'], 'modello'))
    return _W['SL']


def z_ciclo33(v, vh):
    """z delle nove grandezze dell'obiettivo (come `rifare_misure.z_ciclo`, con le parole nuove)."""
    rif = _W['rif']
    zs = OrderedDict()
    for m in OBI_MISURE33:
        if v.get(m) is not None and rif['scala'].get(m):
            zs[m] = (v[m] - vh[m]) / rif['scala'][m]
    for j in OBI_GIUDICI33:
        nu = rif['nullo'].get(j)
        if v.get(j) is not None and nu and nu['sd']:
            zs[j] = (v[j] - nu['media']) / nu['sd']
    return zs


def obiettivo33(v, vh):
    zs = z_ciclo33(v, vh)
    a = [min(abs(z), RM.ZCAP32) for z in zs.values()]
    return float(np.mean(a)), zs


def valuta33(args):
    """args = (generazione, indice, u, seme, fogli): scrive un mezzo libro con lo scrittore piu' libero e lo misura. -> dict come `rifare_misure.valuta`."""
    gen, i, u, seme, fogli = args
    inizio = time.time()
    try:
        S = scrittore33()
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
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = RM.valuta_copia(conti)
        vh = RM.vero_su(fogli)
        obj, zs = obiettivo33(v, vh)
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('obiettivo_puro', obj), ('penalita', pen), ('obiettivo', obj + pen), ('z', zs), ('valori', v), ('vero_meta', vh), ('copia', q),
                            ('copia_violazioni', viol), ('pagine', len(rows)), ('pagine_K', npag), ('parole', sum(len(p) for _, _, p in t)),
                            ('secondi_scrittura', round(t_scrittura, 1)), ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


# ---------------------------------------------------------------- generatori a conteggi: modelli stimati (una volta per processo)

def _righe_mondo():
    return I7.libro_vero()


def _fogli_mondo():
    f_add, f_val, f_fuori = RD.divisione_fogli()
    return f_add, f_val, f_fuori


def _base_originale():
    """Il libro "originale" da cui il mondo e' stato costruito (per il gemello e per i campioni in piu' della vera catena). Nel mondo `vero` e' il libro del mondo."""
    return RT._BASE.get('originale') or I7.libro_vero()


def _testo_addestramento(mult):
    """Pagine "vere" d'addestramento per l'oracolo: i fogli d'addestramento del mondo + (mult - 1) campioni della VERA catena sulla disposizione di quei fogli."""
    f_add, _, _ = _fogli_mondo()
    liste = [OC.vere_di_righe(_righe_mondo(), f_add)]
    if mult > 1:
        base = _base_originale()
        cont_vera = OC.conta([OC.vere_di_righe(base)], 2)
        lay = OC.layout_di_righe(base, f_add)
        for j in range(1, mult):
            liste.append(OC.genera_vere(cont_vera, lay, OC.seme_str('ia33extra', _W['mondo'], j), 2))
    return liste


def modello_generatore(spec):
    """Il generatore (oggetto con `genera(layout, seme) -> pagine "vere"`) per `spec`; si tiene in memoria per processo."""
    chiave = tuple(spec[:2]) if spec[0] in ('KN', 'MLE') else (spec[0],)
    if chiave in _M:
        return _M[chiave]
    righe = _righe_mondo()
    if spec[0] == 'KN':
        liste = _testo_addestramento(int(spec[1]))
        righe_add = [r for v in liste for r in OC.righe_di_vere(v)]
        m = OC.KNCatena(righe_add, 3, OC.glifi_del_libro(righe))
        g = lambda lay, seme: m.genera_vere(lay, seme)
    elif spec[0] == 'MLE':
        liste = _testo_addestramento(int(spec[1]))
        cont = OC.conta(liste, 2)
        g = lambda lay, seme: OC.genera_vere(cont, lay, seme, 2)
    elif spec[0] == 'GEM':
        base = _base_originale()
        cont = OC.conta([OC.vere_di_righe(base)], 2)
        g = lambda lay, seme: OC.genera_vere(cont, lay, seme, 2)
    elif spec[0] == 'NGR':
        f_add, f_val, _ = _fogli_mondo()
        m, ordine, bit, tutti = OC.scegli_ordine(OC.righe_di_vere(OC.vere_di_righe(righe, f_add)), OC.righe_di_vere(OC.vere_di_righe(righe, f_val)), OC.glifi_del_libro(righe))
        _M['ngr_info'] = OrderedDict([('ordine', ordine), ('bit_validazione', round(float(bit), 4)), ('tutti', tutti)])
        g = lambda lay, seme: m.genera_vere(lay, seme)
    else:
        raise ValueError(spec)
    _M[chiave] = g
    return g


def scrivi_libro33(tipo, i, spec, seme):
    """Un libro INTERO del tipo `spec` nel formato del banco (`B.percorso_libro_tar`). -> dict (come `rifare_misure.scrivi_libro_esame`)."""
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    f_add = RD.divisione_fogli()[0]
    if os.path.exists(p):
        t = I7.leggi_file(p)
        man = None
    elif spec[0] == 'L':
        S = scrittore33()
        t, man = S.libro33(np.asarray(spec[1], float), seme, None)
    else:
        g = modello_generatore(spec)
        t = OC.t_da_vere(g(OC.layout_di_righe(_righe_mondo()), seme))
        man = None
    if not os.path.exists(p):
        I7.scrivi_file(t, p + '.tmp', 'ia33, libro %s %d, mondo %s' % (tipo, i, _W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, f_add)
    q, sg, viol, pen = RM.valuta_copia(conti)
    ris = OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('spec', spec[0]), ('righe', len(t)),
                       ('parole', sum(len(ps) for _, _, ps in t)), ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol)])
    if man is not None:
        ris['manopole'] = man
    if spec[0] == 'NGR' and 'ngr_info' in _M:
        ris['ngr'] = _M['ngr_info']
    ris['secondi'] = round(time.time() - inizio, 1)
    return ris


def lavoro_banco33(args):
    """Un lavoro del banco di IA26 (o J32, o libro33, o valuta33) dentro il processo preparato."""
    inizio = time.time()
    try:
        if args[0] == 'libro33':
            return scrivi_libro33(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'valuta':
            return valuta33(args[1:])
        if args[0] == 'J32':
            return RM.lavoro_J32(args[1])
        return B.lavoro(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3])), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])


if __name__ == '__main__':
    pass
