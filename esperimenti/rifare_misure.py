# -*- coding: utf-8 -*-
"""IA32, modulo di supporto: il valore di un insieme di manopole (l'obiettivo del ciclo) e le misure dell'esame.

In parole semplici
- Il banco e' quello di IA26 (`righello_banco`, importato senza modificarlo). Qui si usa solo una parte, scelta PRIMA (preregistrazione ia32):
    misure e giudici "di allenamento" (entrano nell'obiettivo):  copia netta, contatto, G9, bordi (inizio riga), costo di forma delle parole nuove;
                                                                  giudici e231, e266, K.
    misure "tenute fuori" (si guardano solo all'esame):          Λ, D, bordi (fine riga), quota di parole nuove, k90 e R_rel (se il riferimento le ha);
                                                                  giudici N e KN (IA26, ricalcolati sui libri nuovi) e il giudice nuovo "b".
- Obiettivo di una valutazione = media di min(|z|, ZCAP32) su queste 8 grandezze (z come nel banco: (valore - vero) / scala; per i giudici (AUC - media del nullo) /
  deviazione standard del nullo). ZCAP32 = 10 (nel banco il tetto e' 6; con 6 il cammino resterebbe piatto finche' un giudice sta a 0,8: dichiarato).
  Piu' una penalita' se la guardia anti-copia e' superata (vedi `penalita_copia`).
- Una valutazione scrive un MEZZO libro (meta' dei fogli, uguali per tutti i candidati della stessa generazione) e lo misura; K usa solo le pagine presenti.
Le funzioni lavorano dentro un processo che ha chiamato `prepara(mondo, cartella32)`.
"""
import json
import math
import os
import sys
import time
import zlib
from collections import Counter, OrderedDict

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
import ia01_giudice_neurale as G  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402
import rifare_scrittura as RS  # noqa: E402

ZCAP32 = float(os.environ.get('ZCAP32', 10))
OBI_MISURE = ('copia_netta', 'contatto', 'G9', 'bordi_inizio', 'costo_forma')
OBI_GIUDICI = ('e231', 'e266', 'K')
OBIETTIVO = OBI_MISURE + OBI_GIUDICI
FUORI_MISURE = ('lam', 'D', 'bordi_fine', 'parole_nuove', 'k90', 'R_rel')
FUORI_GIUDICI = ('N', 'KN', 'b')
SOGLIE_COPIA = OrderedDict([('5-grammi', 0.003), ('righe intere', 0.002), ('righe vere', 0.002)])   # ia20 (severe): sopra "copia"; si alzano al naturale x NAT_VOLTE
NAT_VOLTE = 1.25
PENALITA_COPIA = 5.0

_W = {}


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def prepara(mondo, cartella32, nomi=()):
    """Da chiamare per prima in ogni processo: attiva il mondo (il libro che fa da vero), le cartelle del banco e il modello pieno."""
    import torch
    torch.set_num_threads(1)
    B.imposta_mondo(mondo, list(nomi))
    _W['mondo'] = mondo
    _W['cart'] = cartella32
    _W['rif'] = json.load(open(B.dir_mondo('riferimento.json'), encoding='utf-8'))
    p = os.path.join(cartella32, 'naturale.json')
    _W['nat'] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    return _W


def scrittore():
    if 'S' not in _W:
        _W['S'] = RS.Scrittore(os.path.join(_W['cart'], 'modello'))
    return _W['S']


# ---------------------------------------------------------------- K sui mezzi libri, forma delle parole nuove

def _K_vere_e_modello(f):
    k = ('K', f)
    if k not in _W:
        c = I7.contesto_A()
        test, val, add = B.MS.divisione_K(c, f)
        g, _ = B.pickle_cache('K_f%d' % f, lambda: B.J.scegli_giudice_k([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V']))
        vere = {p: G.profilo(c['ids'][p], g.sorpresa(c['ids'][p])) for p in test}
        _W[k] = (g, vere, test)
    return _W[k]


def auc_K(rows):
    """AUC del giudice K sulle pagine presenti in `rows` (quelle di prova di ogni piega), con la stessa regressione di ia01. -> (AUC, pagine)."""
    c = I7.contesto_A()
    Xv, Xg, pag = [], [], []
    for f in range(B.PIEGHE):
        g, vere, test = _K_vere_e_modello(f)
        for p in test:
            if p in rows:
                a = G.codifica(rows[p], c['idx'])
                Xg.append(G.profilo(a, g.sorpresa(a)))
                Xv.append(vere[p])
                pag.append(p)
    if len(pag) < 12:
        return None, len(pag)
    X = np.array(Xv + Xg)
    y = np.array([0] * len(pag) + [1] * len(pag))
    return float(G.auc_logistico(X, y, pag + pag)[0]), len(pag)


def _forma_fold(f):
    k = ('forma', f)
    if k not in _W:
        c = I7.contesto_A()
        pv = OrderedDict((p, c['vere'][p]) for p in c['ids'] if c['fold'][p] != f)
        cnt = Counter(w for rr in pv.values() for _, ws in rr for w in ws)
        _W[k] = (R.Forma(cnt), set(cnt))
    return _W[k]


def forma_testo(rows):
    """(costo di forma delle parole nuove, quota di parole nuove) sulle pagine presenti, con i modelli per piega del banco (come `lavoro_D`)."""
    c = I7.contesto_A()
    bit = gl = nn = tot = 0.0
    for f in range(B.PIEGHE):
        forma, noti = _forma_fold(f)
        pg = OrderedDict((p, rows[p]) for p in c['ids'] if c['fold'][p] == f and p in rows)
        if pg:
            y = R.costo_nuove(forma, pg, noti)
            bit += y[0]
            gl += y[1]
            nn += y[2]
            tot += y[3]
    return (bit / max(gl, 1.0), nn / max(tot, 1.0))


# ---------------------------------------------------------------- guardia anti-copia

def soglie_copia():
    nat = _W.get('nat')
    out = OrderedDict()
    for k, s in SOGLIE_COPIA.items():
        n = None
        if nat:
            kk = 'righe intere' if k == 'righe vere' else k
            a, b = nat['conti'][kk]
            n = a / b if b else None
        out[k] = max(s, NAT_VOLTE * n) if n is not None else s
    return out


def valuta_copia(conti):
    """-> (quote, soglie, violazioni (quanto sopra soglia, in unita' di soglia), penalita')."""
    sg = soglie_copia()
    q = OrderedDict((k, (a / b if b else 0.0)) for k, (a, b) in conti.items())
    viol = OrderedDict((k, max(0.0, q[k] / sg[k] - 1.0)) for k in sg if k in q)
    return q, sg, viol, float(min(20.0, PENALITA_COPIA * sum(viol.values())))


# ---------------------------------------------------------------- una valutazione del ciclo

def vero_su(fogli):
    """Il valore VERO delle misure di conteggio sulle pagine dei fogli `fogli` (con la stessa procedura che si usa sul mezzo libro): un mezzo libro ha modelli di
    misura addestrati su meta' dei dati e dunque valori diversi da quelli di un libro intero anche per un imitatore perfetto; il confronto e' a coppie (stessi fogli)."""
    key = ('vero_su', tuple(fogli))
    if key not in _W:
        c = I7.contesto_A()
        ins = set(fogli)
        rows = OrderedDict((p, c['vere'][p]) for p in c['ids'] if I7.foglio_di(p) in ins)
        m = B.lavoro_M('veroH', rows=rows)
        out = OrderedDict((k, m[k]) for k in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine'))
        out['costo_forma'], out['parole_nuove'] = forma_testo(rows)
        _W[key] = out
    return _W[key]


def z_ciclo(v, vh):
    """z di ogni grandezza dell'obiettivo: misure rispetto al vero degli stessi fogli, scala del banco; giudici rispetto al nullo del banco."""
    rif = _W['rif']
    zs = OrderedDict()
    for m in OBI_MISURE:
        if v.get(m) is not None and rif['scala'].get(m):
            zs[m] = (v[m] - vh[m]) / rif['scala'][m]
    for j in OBI_GIUDICI:
        nu = rif['nullo'].get(j)
        if v.get(j) is not None and nu and nu['sd']:
            zs[j] = (v[j] - nu['media']) / nu['sd']
    return zs


def obiettivo_da_v(v, vh):
    zs = z_ciclo(v, vh)
    a = [min(abs(z), ZCAP32) for z in zs.values()]
    return float(np.mean(a)), zs


def valuta(args):
    """args = (generazione, indice, u, seme, fogli). Scrive il mezzo libro e lo misura. -> dict con obiettivo, z, valori, copia, tempi."""
    gen, i, u, seme, fogli = args
    inizio = time.time()
    try:
        S = scrittore()
        t, man = S.libro(np.asarray(u, float), seme, fogli)
        t_scrittura = time.time() - inizio
        rows = I7.libro_A_da_righe(t)
        v = OrderedDict((m, None) for m in list(B.MISURE) + list(B.GIUDICI))
        m = B.lavoro_M('cand', rows=rows)
        for k in ('copia_netta', 'lam', 'contatto', 'G9', 'bordi_inizio', 'bordi_fine'):
            v[k] = m[k]
        v['costo_forma'], v['parole_nuove'] = forma_testo(rows)
        j = I7.giudica(t)
        v['e231'], v['e266'] = j['AUC_e231'], j['AUC_e266']
        v['K'], npag = auc_K(rows)
        conti = RS.copia_libro(t, S.P.f_add)
        q, sg, viol, pen = valuta_copia(conti)
        vh = vero_su(fogli)
        obj, zs = obiettivo_da_v(v, vh)
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('gen', gen), ('i', i), ('u', list(map(float, u))), ('manopole', man), ('seme', seme),
                            ('obiettivo_puro', obj), ('penalita', pen), ('obiettivo', obj + pen), ('z', zs), ('valori', v), ('vero_meta', vh), ('copia', q),
                            ('copia_violazioni', viol), ('pagine', len(rows)), ('pagine_K', npag), ('parole', sum(len(p) for _, _, p in t)),
                            ('secondi_scrittura', round(t_scrittura, 1)), ('secondi', round(time.time() - inizio, 1))])
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', 'ciclo|%d|%d' % (gen, i)), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:])])


# ---------------------------------------------------------------- libri interi dell'esame e lavori del banco

def scrivi_libro_esame(tipo, i, u, seme):
    """Un libro INTERO con le manopole `u`, scritto nel formato del banco: dati/cache/ia32/<mondo>/banco/<mondo>/libri/tar_<tipo>_<i>.txt. -> dict."""
    inizio = time.time()
    p = B.percorso_libro_tar(tipo, i)
    S = scrittore()
    if os.path.exists(p):
        t = I7.leggi_file(p)
        man = RS.da_cubo(np.asarray(u, float))
    else:
        t, man = S.libro(np.asarray(u, float), seme, None)
        I7.scrivi_file(t, p + '.tmp', 'ia32, libro %s %d, mondo %s' % (tipo, i, _W['mondo']), 0)
        os.replace(p + '.tmp', p)
    conti = RS.copia_libro(t, S.P.f_add)
    q, sg, viol, pen = valuta_copia(conti)
    return OrderedDict([('lavoro', 'libro|%s|%d' % (tipo, i)), ('tipo', tipo), ('i', i), ('seme', seme), ('manopole', man), ('righe', len(t)),
                        ('parole', sum(len(ps) for _, _, ps in t)), ('copia', q), ('copia_soglie', sg), ('copia_violazioni', viol),
                        ('secondi', round(time.time() - inizio, 1))])


def lavoro_J32(nome):
    """e231, e266 e N sul libro `nome` (senza il giudice A: richiederebbe 10 modelli per mondo e non e' un giudice dell'esame)."""
    import righello_giudici as RG
    inizio = time.time()
    rows = B.rows_testo(nome)
    out = OrderedDict([('lavoro', 'J32|%s' % nome)])
    j = I7.giudica(RT.t_da_rows(rows))
    out['AUC_e231'], out['AUC_e266'] = j['AUC_e231'], j['AUC_e266']
    v = B.N_vero()
    Xt, pt = RG.matrice_righe_N(OrderedDict((p, rows.get(p, [])) for p in v['nomi']), v['nomi'], v['voc'])
    out['AUC_N'] = RG.auc_N(v['Xv'], v['pv'], Xt, pt, len(v['nomi']))
    out['secondi'] = round(time.time() - inizio, 1)
    return out


def lavoro_banco(args):
    """Un lavoro del banco di IA26 (o J32) dentro il processo preparato."""
    inizio = time.time()
    try:
        if args[0] == 'J32':
            return lavoro_J32(args[1])
        if args[0] == 'libro':
            return scrivi_libro_esame(args[1], int(args[2]), args[3], int(args[4]))
        if args[0] == 'valuta':
            return valuta(args[1:])
        return B.lavoro(args)
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', '|'.join(str(a) for a in args[:3])), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])),
                            ('traccia', traceback.format_exc()[-1500:]), ('secondi', round(time.time() - inizio, 1))])


def valori_libro(nome, C, pK, pKN, n_pag):
    """Il profilo di un libro dell'esame dai risultati `C` (lavoro -> risultato): come `B.valori_testo`, ma e231/e266/N dal lavoro J32."""
    v = B.valori_testo(nome, C, pK, pKN, n_pag)
    j = C.get('J32|%s' % nome)
    if j:
        v['e231'], v['e266'], v['N'] = j.get('AUC_e231'), j.get('AUC_e266'), j.get('AUC_N')
    return v
