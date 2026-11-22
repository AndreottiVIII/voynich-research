# -*- coding: utf-8 -*-
"""Prove di unita' del banco di IA26 (modulo di supporto, non e' un esperimento).

Si lanciano solo sul libro latino nella disposizione del Voynich, MAI sul Voynich:

    SOLO_CONTROLLI=1 USCITA=<cartella fuori dal repo> python esperimenti/righello_prove.py [lente]

Prove veloci (qualche minuto): giudice KN (probabilita' che sommano a 1), giudice N (il segno dell'AUC, il rimescolamento delle parole si vede, quello delle righe no),
nullo dei giudici, divisione a meta' (fogli interi, bilanciata, ripetibile), distanza e riferimento su numeri finti, calibrazione su una funzione nota, classi di lettura,
catalogo e caricamento dei testi non Voynich, mondi sintetici (disposizione, gemello, attivazione). Con `lente`: la somma delle metà coincide con il libro intero sui numeri
per pagina (copia netta e Λ, contatto, D, forma), che costa qualche minuto in piu'. Non scrive niente nel repo.
"""
import os
import sys
import time
from collections import OrderedDict

import numpy as np

if os.environ.get('SOLO_CONTROLLI') != '1':
    raise SystemExit('SOLO_CONTROLLI=1 obbligatorio: queste prove non si fanno sul Voynich')

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import righello_banco as B  # noqa: E402
import righello_giudici as RG  # noqa: E402
import righello_testi as RT  # noqa: E402
import ia07_voynich_neurale as I7  # noqa: E402
import ia01_giudice_neurale as G  # noqa: E402
import imitatore_misure as MS  # noqa: E402

_N = dict(ok=0, ko=0)


def ok(nome, condizione, dettaglio=''):
    _N['ok' if condizione else 'ko'] += 1
    print('%s %s %s' % ('OK  ' if condizione else 'FALLITA', nome, dettaglio), flush=True)


def prova_kn():
    c = I7.contesto_A()
    test, val, add = MS.divisione_K(c, 0)
    for n in (3, 5):
        m = RG.KneserNey([c['ids'][p] for p in add], n, c['V'])
        h = (1,) * (n - 1)
        s = sum(m.prob(h, w) for w in range(c['V']))
        ok('KN: le probabilita\' sommano a 1 (ordine %d)' % n, abs(s - 1.0) < 1e-9, 'somma %.12f' % s)
        h2 = tuple(int(x) for x in c['ids'][add[0]][:n - 1])
        s2 = sum(m.prob(h2, w) for w in range(c['V']))
        ok('KN: idem dopo un contesto visto (ordine %d)' % n, abs(s2 - 1.0) < 1e-9, 'somma %.12f' % s2)
    m, info = RG.scegli_kn([c['ids'][p] for p in add], [c['ids'][p] for p in val], c['V'])
    b = m.bit_medi([c['ids'][p] for p in val])
    ok('KN: bit per glifo sulla validazione sotto quelli di un modello uniforme', b < np.log2(c['V']), 'ordine %d, %.3f bit contro %.3f' % (info['ordine'], b, np.log2(c['V'])))
    info2, prof = RG.lavoro_KN(0, c, {'parole': G.rimescola_parole(c['vere'], 11)})
    ok('KN: profili di 14 numeri per le pagine della piega', all(len(v) == 14 for v in prof['vere'].values()) and len(prof['vere']) > 20, '%d pagine' % len(prof['vere']))


def prova_N():
    c = I7.contesto_A()
    nomi = sorted(c['ids'])
    voc = RG.vocabolario_N(c['vere'])
    ok('N: vocabolario di 1.500 n-grammi diversi', len(voc) == len(set(voc)) == RG.VOC_N, '%d' % len(voc))
    Xv, pv = RG.matrice_righe_N(c['vere'], nomi, voc)
    ok('N: una riga di matrice per riga di testo', Xv.shape[0] == sum(len(c['vere'][p]) for p in nomi), '%s' % (Xv.shape,))
    sh, ri = G.rimescola_parole(c['vere'], 5), G.rimescola_righe(c['vere'], 5)
    a_sh = RG.auc_N(Xv, pv, *RG.matrice_righe_N(sh, nomi, voc), len(nomi))
    a_ri = RG.auc_N(Xv, pv, *RG.matrice_righe_N(ri, nomi, voc), len(nomi))
    ok('N: le parole rimescolate dentro la riga si vedono (AUC > 0,70)', a_sh > 0.70, 'AUC %.3f' % a_sh)
    ok('N: le righe rimescolate non si vedono (conteggi dentro la riga): AUC 0,5', abs(a_ri - 0.5) < 0.05, 'AUC %.3f' % a_ri)
    nul = RG.auc_nullo_N(Xv, pv, len(nomi), 5)
    ok('N: nullo con etichette a caso vicino a 0,5', 0.35 < float(np.mean(nul)) < 0.65, 'media %.3f su %d' % (np.mean(nul), len(nul)))
    prof = {p: np.array([len(c['vere'][p]), sum(len(ws) for _, ws in c['vere'][p])], dtype=float) for p in nomi}
    nul2 = RG.auc_nullo_profili(prof, 4)
    ok('nullo dei giudici a profili: AUC con etichette a caso', all(0.2 < x < 0.8 for x in nul2), ', '.join('%.2f' % x for x in nul2))


def prova_meta():
    c = I7.contesto_A()
    info = B.pagine_info()
    h1, h2 = B.dividi_meta(1)
    ok('metà: le due metà non si sovrappongono e coprono le pagine', set(h1).isdisjoint(h2) and set(h1) | set(h2) == set(c['ids']), '%d + %d' % (len(h1), len(h2)))
    f1, f2 = {info[p][0] for p in h1}, {info[p][0] for p in h2}
    ok('metà: i fogli sono interi (nessun foglio in tutte e due)', f1.isdisjoint(f2), '%d e %d fogli' % (len(f1), len(f2)))
    ok('metà: bilanciate (la più piccola almeno 40% delle pagine)', min(len(h1), len(h2)) >= 0.4 * len(c['ids']), '%d / %d' % (len(h1), len(h2)))
    ok('metà: ripetibili con lo stesso seme, diverse con un altro', B.dividi_meta(1) == (h1, h2) and B.dividi_meta(2) != (h1, h2))
    t1, t2 = B.dividi_meta(1, tutte=True)
    ok('metà: con `tutte` stesse metà di fogli, con le pagine corte', {info[p][0] for p in t1} == f1 and set(h1) <= set(t1))
    # bilanciamento per (sezione, lingua)
    st = {}
    for p in c['ids']:
        st.setdefault(info[p][1:], [0, 0])
    for k, h in ((0, h1), (1, h2)):
        for p in h:
            st[info[p][1:]][k] += 1
    sbil = max(abs(a - b) / max(a + b, 1) for a, b in st.values() if a + b >= 8)
    ok('metà: bilanciate dentro ogni (sezione, lingua) con almeno 8 pagine (scarto massimo 40%)', sbil <= 0.4, 'scarto massimo %.2f' % sbil)


def prova_distanza():
    rng = np.random.default_rng(1)
    C = {'metro': dict(lavoro='metro', vero={m: 1.0 for m in B.MISURE_CONTEGGIO}, diffs={m: list(rng.normal(0, 0.1, 200)) for m in B.MISURE_CONTEGGIO}, divisioni=200)}
    for tp, campo in (('K', 'k90'), ('R', 'R_rel')):
        for s in (1, 2, 3):
            C['G|%s|vero|%d' % (tp, s)] = {campo: 2.0 + 0.01 * s}
        for s in range(1, 7):
            C['gm|%s|%d|1' % (tp, s)] = {campo: 2.0 + rng.normal(0, 0.2)}
            C['gm|%s|%d|2' % (tp, s)] = {campo: 2.0 + rng.normal(0, 0.2)}
    for j in B.GIUDICI:
        C['nullo|%s' % j] = dict(auc=list(rng.normal(0.5, 0.04, 100)), n=100)
    rif = B.riferimento_da_corse(C)
    ok('riferimento: scale per le 11 misure e nulli per i 6 giudici', len(rif['scala']) == 11 and len(rif['nullo']) == 6)
    v = OrderedDict((m, rif['vero'][m]) for m in B.MISURE)
    v.update((j, rif['nullo'][j]['media']) for j in B.GIUDICI)
    d0 = B.distanza(v, rif)
    ok('distanza: un testo uguale al vero ha distanza 0', d0['distanza'] < 1e-9 and d0['fuori'] == 0.0 and d0['n'] == 17, 'n = %d' % d0['n'])
    v2 = OrderedDict(v)
    v2['D'] = rif['vero']['D'] + 3 * rif['scala']['D']
    d1 = B.distanza(v2, rif)
    ok('distanza: una misura sola a 3 scale: z = 3, un diciassettesimo della somma', abs(d1['z']['D'] - 3.0) < 1e-9 and abs(d1['distanza'] - 3.0 / 17) < 1e-9 and abs(d1['fuori'] - 1 / 17) < 1e-9)
    v3 = OrderedDict(v)
    v3['e231'] = rif['nullo']['e231']['media'] + 100 * rif['nullo']['e231']['sd']
    d2 = B.distanza(v3, rif)
    ok('distanza: il tetto a 6 impedisce che una sola misura domini', abs(d2['distanza'] - 6.0 / 17) < 1e-9)
    v4 = OrderedDict(v)
    v4['A'] = rif['nullo']['A']['media'] - 4 * rif['nullo']['A']['sd']
    ok('distanza: un AUC molto sotto il nullo conta come uno sopra (due code)', abs(B.distanza(v4, rif)['z']['A'] + 4.0) < 1e-9)
    v5 = OrderedDict((m, None) for m in B.DISTANZA_SU)
    v5['D'] = rif['vero']['D']
    ok('distanza: le misure mancanti si saltano', B.distanza(v5, rif)['n'] == 1)


def prova_calibrazione():
    import ia26_righello_taratura as T
    def mondo(e, t, c):                                       # funzione quadratica nota che sostituisce il testo sintetico
        return dict(copia_netta=0.5 * e + 0.3 * t + 0.2 * e * e, lam=0.2 + 0.5 * e - 0.6 * t, contatto=0.4 * c + 0.1 * e, G9=0.02 + 0.2 * t - 0.4 * t * t)
    bers = mondo(0.05, 0.10, 0.30)
    C = {}
    for e in T.GRIGLIA_ECO:
        for t in T.GRIGLIA_TEMA:
            for c_ in T.GRIGLIA_CONT:
                C['cal|g|%s|%s|%s' % (e, t, c_)] = dict(par=dict(eco=e, tema=t, contatto=c_), **mondo(e, t, c_))
    punto, prev = T.calibra(C, bers)
    reale = mondo(*punto)
    err = max(abs(reale[m] - bers[m]) / bers[m] for m in bers)
    ok('calibrazione: la regressione quadratica trova un punto vicino ai valori da raggiungere', err < 0.15, 'punto %s, errore relativo massimo %.3f' % (tuple(round(x, 3) for x in punto), err))
    punto2, _ = T.calibra(C, bers, centro=punto)
    reale2 = mondo(*punto2)
    err2 = max(abs(reale2[m] - bers[m]) / bers[m] for m in bers)
    ok('calibrazione: con i pesi locali (rifinitura) il punto resta buono', err2 < 0.15, 'errore relativo massimo %.3f' % err2)
    ok('calibrazione: il punto sta nella scatola', all(T.BOX_CAL[k][0] <= x <= T.BOX_CAL[k][1] for k, x in zip(('eco', 'tema', 'contatto'), punto)))


def prova_classi():
    import ia26_righello_taratura as T
    ok('classe: vicino al gemello e poco fuori fascia = al vero', T.classe_distanza(0.8, 0.1, 0.6) == 'al vero')
    ok('classe: quattro volte il gemello = lontano', T.classe_distanza(2.5, 0.3, 0.6) == 'lontano')
    ok('classe: meta\' fuori fascia = lontano anche con distanza piccola', T.classe_distanza(1.0, 0.5, 0.6) == 'lontano')
    ok('classe: nel mezzo = intermedio', T.classe_distanza(1.8, 0.3, 0.6) == 'intermedio')
    ok('classe: il pavimento del gemello (0,5)', T.classe_distanza(0.9, 0.1, 0.05) == 'al vero' and T.classe_distanza(2.0, 0.1, 0.05) == 'lontano')
    ok('fascia: gruppo tutto fuori', T.classe_fascia([3.0, 2.5, 4.0, 2.2, 5.0]) == 'fuori fascia')
    ok('fascia: gruppo tutto dentro', T.classe_fascia([0.1, -0.5, 1.0, 0.0, 1.5]) == 'dentro la fascia')
    ok('fascia: gruppo misto', T.classe_fascia([3.0, 0.1, 2.5, 0.0]) == 'misto')


def prova_catalogo():
    nomi = RT.catalogo()
    ok('catalogo: nomi unici, comincia dal vero', len(nomi) == len(set(nomi)) and nomi[0] == 'vero', '%d testi' % len(nomi))
    ok('catalogo: 24 cifrari, 8 lingue, 3 controlli', sum(n.startswith('CIF:') for n in nomi) == 24 and sum(n.startswith('LG:') for n in nomi) == 8 and sum(n.startswith('CTRL:') for n in nomi) == 3)
    lay = RT.layout_del_vero()
    pag = [p for p, _ in lay]
    for n in ('TS:1', 'NAIBBE:1', 'LG:inglese', 'CIF:V_3_i1', 'CIF:F_3p5_i1', 'CIF:V_3_italiano_i1', 'CIF:T0_i1', 'CTRL:tutto'):
        r = RT.rows_di(n)
        stesso = r is not None and list(r) == pag and all([(bool(i), len(ws)) for i, ws in r[p]] == dict(lay)[p] for p in pag)
        ok('catalogo: %s ha la disposizione del libro vero' % n, stesso)
        if stesso:
            ok('catalogo: %s ha parole non vuote' % n, all(len(w) > 0 for p in pag for _, ws in r[p] for w in ws))
    ok('catalogo: i nomi dei cifrari si leggono', RT._cifrario_args('CIF:F_3p5_i1') == ('F', 3.5, 1, None) and RT._cifrario_args('CIF:V_3_italiano_i1') == ('V', 3, 1, 'italiano'))
    ok('catalogo: famiglia', RT.famiglia('ia20_M1:3') == 'ia20_M1' and RT.famiglia('CIF:V_3_i1') == 'CIF:V_3' and RT.famiglia('LG:latino') == 'LG')
    t = RT.t_da_rows(RT.rows_di('TS:1'))
    ok('catalogo: t -> rows -> t coincide', RT.t_da_rows(RT.rows_da_t(t)) == t)


def prova_mondi():
    base = I7.libro_vero()
    D = I7.divisore()
    for mondo in RT.MONDI:
        r = RT.righe_sintetiche(base, mondo)
        g = RT.righe_sintetiche(base, mondo, gemello=True)
        stessa = len(r) == len(base) and all(a['pagina'] == b['pagina'] and a['ini'] == b['ini'] and len(a['parole']) == len(b['parole']) for a, b in zip(r, base))
        ok('mondo %s: stessa disposizione del libro vero' % mondo, stessa)
        ok('mondo %s: il gemello ha la stessa disposizione e parole diverse' % mondo, len(g) == len(r) and any(a['parole'] != b['parole'] for a, b in zip(r, g)))
        ok('mondo %s: ripetibile (stesso seme)' % mondo, [x['parole'] for x in RT.righe_sintetiche(base, mondo)] == [x['parole'] for x in r])
        ok('mondo %s: glifi del libro vero' % mondo, {u for x in r for w in x['parole'] for u in D(w)} <= {u for x in base for w in x['parole'] for u in D(w)})
    RT.attiva_mondo('tec')
    v = I7.libro_vero()
    ok('attiva_mondo: il libro vero di ia07 e\' il testo del mondo', [x['parole'] for x in v] == [x['parole'] for x in RT.righe_sintetiche(base, 'tec')])
    ok('attiva_mondo: i riferimenti dei giudici vengono dal mondo', len(I7.riferimenti()['vpag']) == len(I7.per_pagina(v)))
    gem = RT.rows_gemello('tec')
    ok('mondo: il gemello si ricostruisce sul libro originale (non sul mondo)', set(gem) == set(I7.per_pagina(v)))


def prova_lente():
    """La somma delle meta' (tutte le pagine) coincide con il libro intero: copia netta, Λ, contatto da `lavoro_M`; D e forma dai numeri per pagina."""
    dp = B.dati_per_pagina_vero()
    tutte = B.misure_su(dp, list(dp['pag']))
    r = B.lavoro_M('vero')
    for m in ('copia_netta', 'lam', 'contatto'):
        ok('metà (lenta): %s sommata su tutte le pagine = lavoro_M' % m, abs(tutte[m] - r[m]) < 1e-9, '%.6f contro %.6f' % (tutte[m], r[m]))
    ok('metà (lenta): bordi e G9 uguali a lavoro_M', abs(tutte['bordi_inizio'] - r['bordi_inizio']) < 1e-9 and abs(tutte['bordi_fine'] - r['bordi_fine']) < 1e-9 and abs(tutte['G9'] - r['G9']) < 1e-9)
    d = B.lavoro_D(0, 0)
    pg0 = [p for p in dp['pag'] if dp['c']['fold'][p] == 0]
    a0, b0, c0 = sum(dp['D'][p][0] for p in pg0), sum(dp['D'][p][1] for p in pg0), sum(dp['D'][p][2] for p in pg0)
    ok('metà (lenta): D del vero nella piega 0 = somma dei numeri per pagina', max(abs(a0 - d['D']['vero'][0]), abs(b0 - d['D']['vero'][1]), abs(c0 - d['D']['vero'][2])) < 1e-6,
       '%.3f %.3f %.3f' % (a0, b0, c0))
    fo = [dp['forma'][p] for p in pg0]
    ok('metà (lenta): forma del vero nella piega 0 = somma dei numeri per pagina', abs(sum(y[0] for y in fo) - d['forma']['vero'][0]) < 1e-6 and sum(y[3] for y in fo) == d['forma']['vero'][3])
    h1, h2 = B.dividi_meta(1)
    a, b = B.misure_su(dp, h1), B.misure_su(dp, h2)
    ok('metà (lenta): le due metà danno numeri finiti', all(np.isfinite(list(a.values()) + list(b.values()))), 'copia netta %.3f e %.3f' % (a['copia_netta'], b['copia_netta']))


def main(argv):
    inizio = time.time()
    B.imposta_mondo('vero', [])
    for f in (prova_kn, prova_N, prova_meta, prova_distanza, prova_calibrazione, prova_classi, prova_catalogo):
        t = time.time()
        f()
        print('   (%s: %.0f s)' % (f.__name__, time.time() - t), flush=True)
    if 'lente' in argv:
        prova_lente()
    prova_mondi()                                             # per ultima: attiva un mondo e non si torna indietro
    print('\nprove: %d riuscite, %d fallite (%.0f s)' % (_N['ok'], _N['ko'], time.time() - inizio))
    return 1 if _N['ko'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
