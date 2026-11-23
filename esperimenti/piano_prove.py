# -*- coding: utf-8 -*-
"""IA34, prove di unita' (modulo di supporto, non e' un esperimento). Solo su controlli: SOLO_CONTROLLI=1 (libro latino con la disposizione del Voynich).

    SOLO_CONTROLLI=1 PYTHONIOENCODING=utf-8 USCITA=<cartella> python esperimenti/piano_prove.py [parte ...]
Prove: (1) il mondo `struttura`: parole del vocabolario della sezione, legame con la riga sopra piu' forte che a caso, oracolo e gemello; (2) le sei misure nuove: separano i
controlli rimescolati (e il neutro della rete, se c'e' un libro di prova) dal vero; (3) il cubo di 17 manopole; (4) lo scrittore: con le manopole nuove a zero la scelta e' identica a
quella di IA33 (stessi numeri casuali); sorgente di sezione, ripresa dalla riga sopra e fine riga fanno quello che devono; (5) l'obiettivo di un candidato (k90 solo in una meta');
(6) le regole di lettura su numeri finti. La prova del mondo unico per processo e' in `oracolo_prove`.
"""
import os
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))


def prova_mondo():
    import ia07_voynich_neurale as I7
    import piano_mondo as PM
    base = I7.libro_vero()
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    righe = PM.sintetico_struttura(base, base, 12345, D, unita)
    righe2 = PM.sintetico_struttura(base, base, 12345, D, unita)
    assert [x['parole'] for x in righe] == [x['parole'] for x in righe2], 'non deterministico'
    assert all(len(a['parole']) == len(b['parole']) for a, b in zip(righe, base)), 'numero di parole per riga cambiato'
    # vocabolario di sezione: la gran parte delle parole sono del vocabolario della sua sezione (le altre sono eco ritoccate)
    voc = {}
    for x in base:
        voc.setdefault(PM.chiave_di(x), set()).update(x['parole'])
    dentro = tot = 0
    for x in righe:
        for w in x['parole']:
            tot += 1
            dentro += w in voc[PM.chiave_di(x)]
    assert dentro / tot > 0.85, 'parole fuori dal vocabolario di sezione: %.3f' % (1 - dentro / tot)
    # legame con la riga sopra: quota di parole che stanno nella riga sopra (posizione vicina) contro lo stesso testo con le righe rimescolate nella pagina
    import random

    def quota_eco(rr):
        n = k = 0
        sopra = None
        pag = None
        for x in rr:
            if x['pagina'] != pag:
                pag, sopra = x['pagina'], None
            if sopra:
                for j, w in enumerate(x['parole']):
                    n += 1
                    k += w in sopra[max(0, j - 1): j + 2]
            sopra = x['parole']
        return k / n
    mesc = []
    rnd = random.Random(1)
    perpag = OrderedDict()
    for x in righe:
        perpag.setdefault(x['pagina'], []).append(x)
    for rr in perpag.values():
        rr = list(rr)
        rnd.shuffle(rr)
        mesc += rr
    q, q0 = quota_eco(righe), quota_eco(mesc)
    assert q > q0 + 0.10, 'legame con la riga sopra %.3f contro %.3f a caso' % (q, q0)
    # fine riga: la parola che chiude le righe viene dalla distribuzione delle chiusure piu' spesso che a caso
    fin = {}
    for x in base:
        fin.setdefault(PM.chiave_di(x), Counter())[x['parole'][-1]] += 1
    a = np.mean([x['parole'][-1] in fin[PM.chiave_di(x)] for x in righe])
    b = np.mean([x['parole'][len(x['parole']) // 2] in fin[PM.chiave_di(x)] for x in righe])
    assert a > b + 0.10, 'chiusure di riga: %.3f contro %.3f' % (a, b)
    # oracolo e gemello
    f_add = sorted({x['foglio'] for x in base})[::2]
    t = PM.libro_oracolo(base, base, f_add, 1, 7)
    t2 = PM.libro_oracolo(base, base, f_add, 2, 7)
    g = PM.libro_gemello(base, 99)
    assert len(t) == len(base) == len(t2) == len(g)
    ins = set(f_add)
    voc_add = {w for x in base if x['foglio'] in ins for w in x['parole']}
    fuori = np.mean([w not in voc_add for _, _, ps in t for w in ps])
    fuori_g = np.mean([w not in voc_add for _, _, ps in g for w in ps])
    assert fuori < fuori_g, 'l\'oracolo (vocabolario dei soli fogli d\'addestramento) deve avere meno parole fuori di un gemello (%.3f contro %.3f)' % (fuori, fuori_g)
    return 'mondo struttura: parole di sezione %.3f, legame riga sopra %.3f (a caso %.3f), chiusure %.3f (%.3f); oracolo: parole fuori addestramento %.3f (gemello %.3f)' % (
        dentro / tot, q, q0, a, b, fuori, fuori_g)


def prova_misure():
    import righello_testi as RT
    import righello_banco as B
    import ia07_voynich_neurale as I7
    import piano_misure as PMS
    c = I7.contesto_A()
    ref = PMS.riferimento_mondo(c['vere'], lambda s: B.dividi_meta(s), 30)
    for n in PMS.NOMI_NM:
        assert ref['vero'][n] is not None and ref['sigma'][n], n
    tutto = PMS.misure_testo(RT.rows_di('CTRL:tutto'), c['ids'])
    z = {n: (tutto[n] - ref['vero'][n]) / ref['sigma'][n] for n in PMS.NOMI_NM}
    assert abs(z['burst']) > 5 and abs(z['sezione']) > 5 and abs(z['lag23']) > 5, 'i testi rimescolati devono essere separati da burst, sezione e lag23: %s' % {k: round(v, 1) for k, v in z.items()}
    righe = PMS.misure_testo(RT.rows_di('CTRL:righe'), c['ids'])
    zr = {n: (righe[n] - ref['vero'][n]) / ref['sigma'][n] for n in PMS.NOMI_NM}
    # il vero contro il vero non si separa: meta' contro tutto, a un sigma di scala
    h1, h2 = B.dividi_meta(7)
    m1 = PMS.misure_testo(c['vere'], h1)
    zh = {n: abs(m1[n] - ref['vero'][n]) / ref['scala'][n] for n in PMS.NOMI_NM}
    assert max(zh.values()) < 4, 'una meta\' del vero non deve stare lontana: %s' % {k: round(v, 1) for k, v in zh.items()}
    return 'misure nuove: i testi tutto rimescolati separati (z %s); righe rimescolate (z %s); una meta\' del vero entro %.1f scale' % (
        {k: round(v, 1) for k, v in z.items()}, {k: round(v, 1) for k, v in zr.items()}, max(zh.values()))


def prova_cubo():
    import oracolo_scrittura as OS
    import piano_scrittura as PS
    assert PS.DIM34 == 17 and len(PS.neutro_cubo34()) == 17
    k0 = PS.da_cubo34(PS.neutro_cubo34())
    assert all(abs(k0[n] - PS.NEUTRO34[n]) < 1e-9 for n in PS.NOMI34), k0
    k = PS.da_cubo34(np.ones(17))
    assert abs(k['w_tri'] - 15.0) < 1e-9 and abs(k['m_sez'] - 0.8) < 1e-9 and abs(k['w_riga'] - 0.8) < 1e-9 and abs(k['w_fine'] - 3.0) < 1e-9, k
    ia33 = OrderedDict([('T_primo', 1.1), ('T_int', 0.8), ('T_fine', 1.2), ('T_eol', 0.95), ('T_riga', 1.3), ('top_p', 0.98), ('w_cont', 3.2), ('w_tri', 6.27), ('w_quad', 7.46), ('s', 0.9),
                        ('w_uni', 0.92), ('w_bi', 0.4), ('b_nuove', 0.58), ('w_pag', 0.22)])
    k2 = PS.da_cubo34(PS.cubo_da_valori34(ia33))
    for n, v in ia33.items():
        assert abs(k2[n] - v) < 1e-6, (n, k2[n], v)
    for n in ('m_sez', 'w_riga', 'w_fine'):
        assert k2[n] == 0.0
    return 'cubo di 17 manopole: neutro, limiti (w a 15, m_sez e w_riga a 0,8, w_fine a 3), inversione dei valori di IA33'


def _scrittore_senza_rete():
    import ia07_voynich_neurale as I7
    import rifare_dati as RD
    import rifare_scrittura as RS
    import piano_scrittura as PS
    from types import SimpleNamespace
    voc = I7.vocabolario()
    f_add = RD.divisione_fogli()[0]
    s = PS.ScrittorePiano.__new__(PS.ScrittorePiano)
    s.ctx = SimpleNamespace(SP=voc['primo_contenuto'], EOL=voc['primo_contenuto'] + 1)
    c = RS.tabella_bigrammi(f_add)
    V = c.shape[1]
    lisc = c + 0.05 * (c.sum(1, keepdims=True) > 0)
    den = lisc.sum(1, keepdims=True)
    s.T = np.where(den > 0, lisc / np.maximum(den, 1e-12), 1.0 / V)
    s.logT = np.log(np.maximum(s.T, 1e-9))
    s.V = V
    s.T3 = RS.tabella_trigrammi(f_add)
    s.logT3 = {k: np.log(np.maximum(v, 1e-9)) for k, v in s.T3.items()}
    s._tabelle_l(f_add)
    s._piano(f_add)
    return s, voc, f_add


def _stato(V, chiave=None):
    import oracolo_scrittura as OS
    S = OS.StatoLibro(V)
    S.Ge = {}
    S.nuova_riga(V)
    S.riga_sopra, S.riga_cur, S.flag, S.chiave = [], [], False, chiave
    return S


def prova_scelta():
    import oracolo_scrittura as OS
    import piano_scrittura as PS
    s, voc, f_add = _scrittore_senza_rete()
    V, SP, EOL = s.V, s.ctx.SP, s.ctx.EOL
    u0 = voc['primo_contenuto'] + 2
    rng = np.random.default_rng(5)
    lg = list(rng.normal(0, 2.0, V))
    amm = [SP, EOL] + list(range(u0, u0 + 8))
    # (a) con le manopole nuove a zero: identica a IA33 (stessi numeri casuali, stesso stato), anche con le correzioni di parole e di pagina accese
    k1 = dict(PS.da_cubo34(PS.neutro_cubo34()))
    k1.update(T_int=0.8, T_fine=1.2, w_cont=1.5, w_tri=6.0, w_quad=3.0, top_p=0.95, T_eol=0.9, w_uni=1.0, w_bi=1.0, b_nuove=0.5, w_pag=0.3)
    ra, rb = np.random.default_rng(9), np.random.default_rng(9)
    Sa = OS.StatoLibro(V)
    Sa.nuova_riga(V)
    Sa.wid = []
    Sb = _stato(V)
    Sb.wid = []
    diff = 0
    w0 = s.lessico.parole.most_common(1)[0][0]
    for t in range(500):
        sa = s.scegli33(lg, amm, Sa, k1, ra, False, 3)
        Sa.prev3, Sa.prev2, Sa.prev = Sa.prev2, Sa.prev, sa
        sb = s.scegli34(lg, amm, Sb, k1, rb, False, 3)
        Sb.prev3, Sb.prev2, Sb.prev = Sb.prev2, Sb.prev, sb
        diff += int(sa != sb)
    assert diff == 0, 'scegli34 con le manopole nuove a zero differisce da IA33 (%d su 500)' % diff
    # (b) sorgente di sezione: ogni parola estratta e' una parola del vocabolario di quella sezione
    chiave = next(k for k in s.sez.chiavi if len(s.sez.uni[k]) > 200)
    lessico = set()
    for pi, c in s.sez.uni[chiave].items():
        if -1 in c:
            lessico.add(pi)
    k2 = dict(PS.da_cubo34(PS.neutro_cubo34()))
    k2['m_sez'] = 0.8
    tutti = [g for g in range(u0, V)]
    rng = np.random.default_rng(3)
    lg0 = [0.0] * V
    ok = n = 0
    for _ in range(300):
        S = _stato(V, chiave)
        S.flag = True
        while True:
            amm2 = ([SP, EOL] if S.wid else []) + tutti
            sc = s.scegli34(lg0, amm2, S, k2, rng, False, len(S.wid))
            if sc in (SP, EOL):
                break
            S.wid.append(sc)
            if len(S.wid) > 30:
                break
        n += 1
        ok += tuple(S.wid) in lessico
    assert ok == n, 'parole fuori dal vocabolario di sezione: %d su %d' % (n - ok, n)
    # (c) ripresa dalla riga sopra: la parola della riga sopra in posizione vicina guadagna
    k3 = dict(PS.da_cubo34(PS.neutro_cubo34()))
    k3['w_riga'] = 0.7
    cand = next(w for w, c in s.lessico.parole.most_common(50) if len(w) >= 3)
    amm3 = sorted({cand[0]} | set(range(u0, u0 + 8)))

    def conriga():
        S = _stato(V, None)
        S.riga_sopra = [cand, cand]
        S.riga_cur = [cand]
        S.wid = []
        return S
    def freq(k):
        r = np.random.default_rng(11)
        cont = np.zeros(len(amm3))
        for _ in range(3000):
            cont[amm3.index(s.scegli34(lg0, amm3, conriga(), k, r, False, 0))] += 1
        return cont / cont.sum()
    f0, f3 = freq(PS.da_cubo34(PS.neutro_cubo34())), freq(k3)
    i = amm3.index(cand[0])
    assert f3[i] > f0[i] + 0.15, 'w_riga non spinge verso la riga sopra: %.3f -> %.3f' % (f0[i], f3[i])
    # (d) fine riga: se il libro ha scritto una parola solo come chiusura di riga, la retroazione la riporta verso la tabella
    k4 = dict(PS.da_cubo34(PS.neutro_cubo34()))
    k4['w_fine'] = 3.0
    w = next(w for w, c in s.sez.occ.most_common(200) if c >= 30)
    T = s.sez.tab_fine[s.sez.chiave_fine(w)]
    amm4 = [SP, EOL, u0]

    def conparola():
        S = _stato(V, None)
        S.wid = list(w)
        S.Ge[s.sez.chiave_fine(w)] = np.array([0.0, 400.0])           # il libro l'ha scritta sempre come ultima della riga
        return S

    def pe(k):
        r = np.random.default_rng(13)
        n = 0
        for _ in range(3000):
            n += s.scegli34([0, 0] + [0] * (V - 2), amm4, conparola(), k, r, False, 3) == EOL
        return n / 3000
    p0, p4 = pe(PS.da_cubo34(PS.neutro_cubo34())), pe(k4)
    assert p4 < p0 - 0.10 or T[1] > 0.9, 'w_fine non frena la fine riga troppo scritta: %.3f -> %.3f (tabella %.3f)' % (p0, p4, T[1])
    return 'scrittore: manopole nuove a zero = IA33 (500 scelte); sorgente di sezione: %d parole tutte del vocabolario; w_riga %.2f -> %.2f; w_fine %.2f -> %.2f' % (n, f0[i], f3[i], p0, p4)


def prova_obiettivo():
    os.environ.setdefault('PICCOLO32', '1')
    import ia34_piano as X
    rs = [dict(somma=12.0, n=12, penalita=0.5), dict(somma=11.0, n=11, penalita=0.5)]
    v = X.media_valutazioni(rs)
    assert abs(v - (23.0 / 23 + 0.5)) < 1e-9, v
    assert X.media_valutazioni([]) is None
    import piano_lavori as PL
    assert len(PL.OBIETTIVO34) == 12 and 'k90' in PL.OBIETTIVO34 and 'lam' in PL.OBIETTIVO34 and 'bordi_fine' in PL.OBIETTIVO34
    assert set(PL.FUORI_MISURE34) == {'D', 'R_rel', 'heaps', 'burst', 'riga_cv', 'sezione', 'lag23', 'ini_par'}
    return 'obiettivo: 12 grandezze, k90 in una meta\' (peso 1/23), 8 misure tenute fuori'


def prova_criteri():
    os.environ.setdefault('PICCOLO32', '1')
    import ia34_piano as X

    def ins(media, err=0.01, n=8, ok=True, quota=1.0, fuori=None, mis=None):
        j = OrderedDict((k, OrderedDict([('media', media[k]), ('sd_libri', 0.01), ('n', n), ('errore', err)])) for k in X.GIUDICI3)
        return OrderedDict([('n', n), ('ruolo', ''), ('giudici_mai_visti', j), ('giudici_ok', all(0.4 <= v <= 0.6 for v in media.values())), ('giudici_di_allenamento', {}),
                            ('misure_tenute_fuori', mis or {}), ('misure_di_allenamento', {}), ('quota_entro_2sigma', quota), ('misure_fuori', fuori or []), ('copia_ok', ok),
                            ('copia_violazione_max', 0.0), ('copia_quote', {})])
    R = OrderedDict()
    R['orac'] = ins(dict(N=0.30, KN=0.62, b=0.66))
    R['orac2'] = ins(dict(N=0.40, KN=0.55, b=0.60))
    R['gem'] = ins(dict(N=0.50, KN=0.51, b=0.52))
    R['neu'] = ins(dict(N=0.98, KN=0.90, b=0.99), n=4)
    O = X.lettura_O(R)
    assert O['verdetto'] == 'irraggiungibile' and O['giudici_oltre_0_60'] == ['N', 'KN', 'b'], O
    R['ia33k'] = ins(dict(N=0.33, KN=0.75, b=0.56), mis={'k90': OrderedDict(z=3.0)})
    R['best'] = ins(dict(N=0.33, KN=0.62, b=0.58), quota=0.875, mis={'k90': OrderedDict(z=0.5)})
    e = X.esito_L('vero', R, None, O)
    assert e['esito'] == "al livello dell'oracolo" and e['confronto_con_ia33']['giudici']['KN']['differenza_distanza_da_0_5'] < 0, e
    R['best'] = ins(dict(N=0.33, KN=0.62, b=0.58), quota=0.4)
    assert X.esito_L('vero', R, None, O)['esito'] == 'non riuscito'
    R['best'] = ins(dict(N=0.52, KN=0.55, b=0.58), quota=0.9)
    assert X.esito_L('vero', R, None, O)['esito'] == 'riuscito assoluto'
    # nel mondo struttura la quota richiesta non supera quella del gemello
    R['gem'] = ins(dict(N=0.50, KN=0.51, b=0.52), quota=0.5)
    R['best'] = ins(dict(N=0.33, KN=0.62, b=0.58), quota=0.5)
    e = X.esito_L('struttura', R, None, O)
    assert e['esito'] == "al livello dell'oracolo" and abs(e['quota_richiesta'] - 0.5) < 1e-9, e
    assert X.esito_L('vero', R, None, O)['esito'] == 'non riuscito'
    R['gem'] = ins(dict(N=0.50, KN=0.51, b=0.52))
    R['neu'] = ins(dict(N=0.98, KN=0.90, b=0.60), n=4)
    assert X.esito_L('vero', R, None, O)['esito'] == 'non valido'
    return 'criteri: 8 casi su numeri finti ok'


def main():
    prove = [prova_mondo, prova_cubo, prova_scelta, prova_obiettivo, prova_criteri, prova_misure]
    filtro = sys.argv[1:]
    for f in prove:
        if filtro and not any(x in f.__name__ for x in filtro):
            continue
        print('OK', f(), flush=True)


if __name__ == '__main__':
    main()
