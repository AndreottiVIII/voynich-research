# -*- coding: utf-8 -*-
"""Prove di unita' di ia30 (modulo, non e' un esperimento): solo su testi NON Voynich (il libro latino nella disposizione del Voynich, SOLO_CONTROLLI=1).

    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO22=1 PICCOLO30=1 USCITA=<cartella con i modelli piccoli di prova> python esperimenti/interventi_prove.py [nomi delle prove]

Servono modelli piccoli gia' addestrati sul latino (M1, M5 di ia20 e E2 di ia22, piega 0, replica 0; in `USCITA`): si fanno con `ia20.addestra` e `ia22.addestra`.
Che cosa prova:
  foto        dopo ogni genere di intervento la penna ritorna esattamente com'era: le letture senza intervento prima e dopo coincidono (anche la memoria di M5);
  nullo       l'intervento nullo (rilegge la stessa cosa) da' differenze esattamente zero, sia sulla parola sia sulla riga;
  perdita     la somma delle log-probabilita' delle parole lette dal lettore coincide con i bit per segno del calcolo a tratti di ia20/ia22 (miscela del puntatore compresa);
  interventi  gli interventi cambiano solo cio' che devono (ultimo glifo, ultime due, penultimo, primo, parola intera; la riga sopra; la testa);
  scrittura   la scrittura con la condizione `base` coincide, segno per segno e con gli stessi numeri casuali, con la scrittura di ia20 e di ia22; con l'intervento nullo
              il libro e' identico; con un intervento vero cambia;
  patch       lo scambio di stati: tutto = effetto donatore (f0 = 1), solo secondo strato = 1 per il primo glifo, solo primo strato = 0;
  maschera    la maschera del puntatore rinormalizza;
  sintetico   il testo sintetico ha le regole piantate (contatto dal solo ultimo glifo; eco dalla riga sopra; bordi) e la taratura le porta al valore voluto.
Nessuna parola del latino esce da qui: solo numeri.
"""
import math
import os
import random
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
assert os.environ.get('SOLO_CONTROLLI') == '1', 'le prove girano solo sul latino (SOLO_CONTROLLI=1)'
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import ia20_imitatore_gradini as I20  # noqa: E402
import ia22_eco_e_legame as I22  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import interventi_motore as IM  # noqa: E402
import interventi_scrittura as IW  # noqa: E402
import interventi_sintetici as IS  # noqa: E402

TIPI = ('M1', 'E2', 'M5')


def modello(tipo, piega=0, replica=0):
    return I22.carica('E2', piega, replica) if tipo == 'E2' else I20.carica(1 if tipo == 'M1' else 5, piega, replica)


def preparati(tipo, piega=0):
    m, ctx = modello(tipo, piega)
    voc = I7.vocabolario()
    dp = I16.dati_pagine()
    f_add, f_val, f_fuori = I7.fogli_della_piega(piega)
    add = [d for d in dp.values() if d['foglio'] in set(f_add)]
    fuori = [d for d in dp.values() if d['foglio'] in set(f_fuori)]
    cap = max(len(d['tok']) for d in dp.values()) + 1700
    L = IM.Lettore(m, ctx, voc, tipo, cap)
    return L, add, fuori, dp


def leggi_tutta(L, tok):
    """Tutte le parole di una pagina vera lette dal lettore (senza interventi): lista di dict."""
    ctx = L.ctx
    righe = IM.struttura(tok, ctx)
    L.pen.apri()
    lg = L.alimenta(tok[:4])
    out = []
    for r, Ln in enumerate(righe):
        lg = L.alimenta(tok[Ln['h']:Ln['h'] + 3])
        out += L.continua(tok, righe, r, 0, lg, 10 ** 6)
    return out


def ok(nome, cond, dettaglio=''):
    print('%s %s %s' % ('PASS' if cond else 'FAIL', nome, dettaglio), flush=True)
    return bool(cond)


def prova_foto():
    esiti = []
    for tipo in TIPI:
        L, add, fuori, dp = preparati(tipo)
        d = fuori[0]
        a = leggi_tutta(L, d['tok'])
        rng = random.Random(1)
        don = IM.Donatori(add[:20], L.ctx)
        IM.lavoro_pagina(L, d, don, rng, 6, 8, 4, IM.NOMI_PAROLA, IM.NOMI_RIGA)
        b = leggi_tutta(L, d['tok'])
        dmax = max(abs(x['lpw'] - y['lpw']) + abs(x['lpm'] - y['lpm']) + float(np.abs(x['lp1'] - y['lp1']).max()) for x, y in zip(a, b))
        esiti.append(ok('foto %s: lettura prima e dopo gli interventi identica' % tipo, dmax == 0.0, 'differenza massima %.3g' % dmax))
    return all(esiti)


def prova_nullo():
    esiti = []
    for tipo in TIPI:
        L, add, fuori, dp = preparati(tipo)
        rng = random.Random(2)
        don = IM.Donatori(add[:20], L.ctx)
        tot = 0.0
        n = 0
        for d in fuori[:3]:
            acc, _ = IM.lavoro_pagina(L, d, don, rng, 6, 8, 4, ['nul'], ['lnul'])
            for a in acc.values():
                tot += float(np.abs(a['S']).sum() + np.abs(a['U'][1:]).sum())
                n += int(a['N'][:, 0].sum())
        esiti.append(ok('nullo %s: differenze esattamente zero' % tipo, tot == 0.0 and n > 0, '%d punti, somma |diff| = %.3g' % (n, tot)))
    return all(esiti)


def prova_perdita():
    esiti = []
    for tipo in TIPI:
        L, add, fuori, dp = preparati(tipo)
        m, ctx = L.m, L.ctx
        d = fuori[0]
        parole = leggi_tutta(L, d['tok'])
        bit_lettore = -sum(w['lpm'] for w in parole) / math.log(2)
        tk = np.asarray(d['tok'])
        ntok = int((tk[1:] >= ctx.primo).sum())
        if tipo == 'E2':
            (P,) = EM.prepara_insiemi([[d]], ctx, 'E2')[0]
            bpc = EM.bpc_pagine(m, ctx, [P])
        else:
            P = GM.prepara_pagina(d, ctx, tipo == 'M5')
            bpc = GM.bpc_pagine(m, ctx, [P])
        bit_cod = bpc * ntok
        esiti.append(ok('perdita %s: bit del lettore = bit di ia20/ia22' % tipo, abs(bit_lettore - bit_cod) < 2e-3 * max(bit_cod, 1), 'lettore %.4f, calcolo a tratti %.4f' % (bit_lettore, bit_cod)))
        if tipo != 'M1':
            bit_gru = -sum(w['lpw'] for w in parole) / math.log(2)
            esiti.append(ok('perdita %s: la miscela da' % tipo + ' un valore diverso dal solo GRU', abs(bit_gru - bit_lettore) > 1e-6, 'solo GRU %.4f' % bit_gru))
    return all(esiti)


def prova_interventi():
    esiti = []
    L, add, fuori, dp = preparati('M1')
    ctx, voc = L.ctx, L.voc
    rng = random.Random(3)
    don = IM.Donatori(add, ctx)
    trovato = None
    for d in fuori:
        tok = d['tok']
        righe = IM.struttura(tok, ctx)
        classi, parole = IM.classi_parole(tok, righe, ctx)
        for r in range(2, len(righe)):
            for i in range(3, len(righe[r]['parole'])):
                if len(parole[r][i - 1]) >= 5 and len(parole[r][i - 2]) >= 3 and all(
                        IM.regione(n, ctx, voc, tok, righe, parole, r, i, don, rng, d['nome']) is not None for n in IM.MINIME):
                    trovato = (d, tok, righe, classi, parole, r, i)
                    break
            if trovato:
                break
        if trovato:
            break
    if trovato is None:
        return ok('interventi: un punto con tutte le coppie minime esiste nelle pagine tenute fuori', False)
    d, tok, righe, classi, parole, r, i = trovato
    p = parole[r][i - 1]
    u0 = ctx.u0
    for nome, vari in (('u1', [len(p) - 1]), ('u2', [len(p) - 2, len(p) - 1]), ('p2', [len(p) - 2]), ('p3', [len(p) - 3]), ('pm', [len(p) // 2]), ('p1', [0]), ('pw', None)):
        reg = IM.regione(nome, ctx, voc, tok, righe, parole, r, i, don, rng, d['nome'])
        if reg is None:
            esiti.append(ok('interventi %s: applicabile' % nome, False))
            continue
        start, toks, s_cur = reg
        q = tuple(int(x) - u0 for x in toks[:-1])
        esiti.append(ok("interventi %s: la parola percepita e' una parola vera" % nome, q in set(don.parole), ""))
        diff = [k for k in range(len(p)) if p[k] != q[k]]
        giusto = (len(q) == len(p) and toks[-1] == int(tok[righe[r]['parole'][i - 1][1]]) and (set(diff) <= set(vari) and diff) if vari is not None else (len(q) == len(p) and q != p))
        esiti.append(ok('interventi %s: cambia solo i glifi giusti' % nome, giusto, 'posti cambiati %s' % diff))
    reg = IM.regione('rs_a', ctx, voc, tok, righe, parole, r, 0, don, rng, d['nome'])
    start, toks, s_cur = reg
    esiti.append(ok('interventi rs_a: parte dalla riga sopra e finisce all\'inizio della parola', start == righe[r - 1]['w0'] and s_cur == righe[r]['w0'] and ctx.EOL in toks, ''))
    reg = IM.regione('hN', ctx, voc, tok, righe, parole, r, 0, don, rng, d['nome'])
    start, toks, s_cur = reg
    esiti.append(ok('interventi hN: cambia solo il terzo segno della testa', len(toks) == 3 and toks[:2] == [int(x) for x in tok[righe[r]['h']:righe[r]['h'] + 2]] and toks[2] != int(tok[righe[r]['h'] + 2]), ''))
    reg = IM.regione('rl', ctx, voc, tok, righe, parole, 4 if len(righe) > 4 else r, 0, don, rng, d['nome'])
    esiti.append(ok('interventi rl: parte tre righe sopra', reg is None or reg[0] == righe[(4 if len(righe) > 4 else r) - 3]['w0'], ''))
    return all(esiti)


def prova_scrittura():
    esiti = []
    voc, D = I7.vocabolario(), I7.divisore()
    righe = I7.libro_vero()
    pp = I7.per_pagina(righe)
    pag = list(pp)[3]
    rp = pp[pag]
    regole = I20.RegoleScrittura(voc)
    for tipo in TIPI:
        L, add, fuori, dp = preparati(tipo)
        don = IM.Donatori(add, L.ctx)
        cap = max(4 + sum(3 + voc['lmax'] + 2 for _ in rp2) for rp2 in pp.values()) + 8
        # riferimento: la scrittura di ia20/ia22
        from collections import Counter
        rng = np.random.default_rng(11)
        if tipo == 'E2':
            pen = EM.Penna22(L.m, L.ctx, cap)
            rif = I22.scrivi_pagina22(L.m, L.ctx, pen, regole, rp, voc, D, rng, Counter())
        else:
            pen = GM.Penna20(L.m, L.ctx, cap)
            rif = I20.scrivi_pagina(L.m, L.ctx, pen, regole, rp, voc, D, rng, Counter())
        base = IW.scrivi_pagina30(L, 'base', regole, rp, voc, D, np.random.default_rng(11), Counter(), don, random.Random(5), pag)
        esiti.append(ok('scrittura %s: base = scrittura di ia20/ia22' % tipo, base == rif, '%d righe' % len(base)))
        nul = IW.scrivi_pagina30(L, 'nul', regole, rp, voc, D, np.random.default_rng(11), Counter(), don, random.Random(5), pag)
        esiti.append(ok('scrittura %s: intervento nullo = senza intervento' % tipo, nul == base, ''))
        for cond in ('u2', 'rs_a', 'hN', 'fill') + (('ptr_off', 'ptr_sopra') if tipo != 'M1' else ()):
            c = Counter()
            t = IW.scrivi_pagina30(L, cond, regole, rp, voc, D, np.random.default_rng(11), c, don, random.Random(5), pag)
            esiti.append(ok('scrittura %s: %s cambia il libro' % (tipo, cond), t != base and len(t) == len(base), 'interventi %d' % c['interventi']))
    return all(esiti)


def prova_patch():
    esiti = []
    for tipo in ('M1', 'E2'):
        L, add, fuori, dp = preparati(tipo)
        ctx = L.ctx
        rng = random.Random(4)
        don = IM.Donatori(add[:20], ctx)
        patch = {n: IM.classifica_dimensioni(L, add[:10], don, rng, n, 30) for n in IM.NOMI_PATCH}
        H = L.m.cfg['nasc']
        patch['__rnd__'] = {n: np.random.default_rng(1).permutation(H) for n in IM.NOMI_PATCH}
        tot = {}
        for d in fuori[:4]:
            acc, pc = IM.lavoro_pagina(L, d, don, rng, 6, 12, 6, ['u2', 'pw'], ['rs_a'], patch=patch, n_patch=6)
            for k, v in pc.items():
                t = tot.setdefault(k, [0.0] * 4)
                for x in range(4):
                    t[x] += v[x]
        f0 = lambda nome, var: tot[(nome, var)][0] / tot[(nome, var)][1]
        fw = lambda nome, var: tot[(nome, var)][2] / tot[(nome, var)][3]
        for nome in IM.NOMI_PATCH:
            if tipo == 'M1' or nome != 'rs_a':
                esiti.append(ok('patch %s %s: tutto = effetto donatore' % (tipo, nome), abs(f0(nome, 'tutto') - 1) < 1e-6 and abs(fw(nome, 'tutto') - 1) < 1e-6, 'f0 %.6f fw %.6f' % (f0(nome, 'tutto'), fw(nome, 'tutto'))))
            else:
                esiti.append(ok('patch %s %s: lo stato non porta i candidati (fw < 1)' % (tipo, nome), abs(f0(nome, 'tutto') - 1) < 1e-6 and fw(nome, 'tutto') < 1, 'f0 %.6f fw %.6f' % (f0(nome, 'tutto'), fw(nome, 'tutto'))))
            esiti.append(ok('patch %s %s: solo secondo strato porta tutto il primo glifo' % (tipo, nome), abs(f0(nome, 'y2') - 1) < 1e-6, 'f0 %.6f' % f0(nome, 'y2')))
            esiti.append(ok('patch %s %s: solo primo strato non cambia il primo glifo' % (tipo, nome), abs(f0(nome, 'y1')) < 1e-6, 'f0 %.6f' % f0(nome, 'y1')))
            esiti.append(ok('patch %s %s: tutte le dimensioni = tutto' % (tipo, nome), abs(f0(nome, 'top%d' % IM.KS_DIM[-1]) - f0(nome, 'y2') if IM.KS_DIM[-1] >= H else True) < 1e-6 or IM.KS_DIM[-1] < H,
                            'k massimo %d su %d' % (IM.KS_DIM[-1], H)))
            esiti.append(ok('patch %s %s: le dimensioni scelte portano piu\' di quelle a caso (k=%d)' % (tipo, nome, IM.KS_DIM[3]), f0(nome, 'top%d' % IM.KS_DIM[3]) >= f0(nome, 'rnd%d' % IM.KS_DIM[3]) - 0.05,
                            'top %.3f, a caso %.3f' % (f0(nome, 'top%d' % IM.KS_DIM[3]), f0(nome, 'rnd%d' % IM.KS_DIM[3]))))
    return all(esiti)


def prova_maschera():
    ppi = np.array([[0.1, 0.1, 0.0, 0.0], [0.2, 0.0, 0.0, 0.1], [0.05, 0.05, 0.0, 0.0]])
    pf = 0.3
    esiti = []
    for par, attesi in (('off', 0), ('d1', 1), ('d2', 1), ('sopra', 1), ('riga', 2)):
        a, b = IW.maschera(par, pf, ppi, 3, 2 if par == 'riga' else 2)
        z = a + float(b.sum())
        esiti.append(ok('maschera %s rinormalizza' % par, abs(z - 1) < 1e-12, 'somma %.12f' % z))
    a, b = IW.maschera('d1', pf, ppi, 3, 2)
    esiti.append(ok('maschera d1 tiene solo la prima riga', b[1:].sum() == 0 and b[0].sum() > 0, ''))
    a, b = IW.maschera('sopra', pf, ppi, 3, 2)
    esiti.append(ok('maschera sopra tiene solo i candidati dopo quelli della riga in corso', b[:2].sum() == 0 and b[2].sum() > 0, ''))
    return all(esiti)


def prova_sintetico():
    import rifarlo_ritocchi as R
    esiti = []
    righe, D, voc = I7.libro_vero(), I7.divisore(), I7.vocabolario()
    info = {}
    s = IS.sintetico_regole(righe, 5, D, voc['unita'], contatto=0.5, info=info)
    pref = info['pref']
    n = k = 0
    for x in s:
        ws = x['parole']
        for a, b in zip(ws, ws[1:]):
            n += 1
            k += D(b)[0] == pref[D(a)[-1]]
    s0 = IS.sintetico_regole(righe, 5, D, voc['unita'])
    n0 = k0 = 0
    for x in s0:
        ws = x['parole']
        for a, b in zip(ws, ws[1:]):
            n0 += 1
            k0 += D(b)[0] == pref[D(a)[-1]]
    esiti.append(ok('sintetico: contatto piantato dal solo ultimo glifo', k / n > k0 / n0 + 0.3, 'quota %.3f contro %.3f senza regola' % (k / n, k0 / n0)))
    se = IS.sintetico_regole(righe, 5, D, voc['unita'], eco=0.3, ritocco=0.0)
    uguali = tot = 0
    sopra = None
    for x in se:
        if sopra is not None and x['pagina'] == sopra[0]:
            tot += len(x['parole'])
            uguali += sum(w in set(sopra[1]) for w in x['parole'])
        sopra = (x['pagina'], x['parole'])
    se0 = IS.sintetico_regole(righe, 5, D, voc['unita'])
    u0 = t0 = 0
    sopra = None
    for x in se0:
        if sopra is not None and x['pagina'] == sopra[0]:
            t0 += len(x['parole'])
            u0 += sum(w in set(sopra[1]) for w in x['parole'])
        sopra = (x['pagina'], x['parole'])
    esiti.append(ok('sintetico: eco dalla riga sopra', uguali / tot > u0 / t0 + 0.2, 'quota %.3f contro %.3f' % (uguali / tot, u0 / t0)))
    p, v, cr = IS.proporzionale(lambda q: R.mi_contatto(IS.righe_a_rows(IS.sintetico_regole(righe, 7, D, voc['unita'], contatto=q), D)), 0.188, 0.1, 5)
    esiti.append(ok('sintetico: la taratura porta il contatto al valore voluto', abs(v - 0.188) < 0.02, 'p %.3f -> %.4f' % (p, v)))
    return all(esiti)


PROVE = [('maschera', prova_maschera), ('sintetico', prova_sintetico), ('foto', prova_foto), ('nullo', prova_nullo), ('perdita', prova_perdita), ('interventi', prova_interventi),
         ('scrittura', prova_scrittura), ('patch', prova_patch)]


def main():
    nomi = sys.argv[1:] or [n for n, _ in PROVE]
    risultati = {}
    for n, f in PROVE:
        if n in nomi:
            print('== prova %s' % n, flush=True)
            risultati[n] = f()
    print('RIEPILOGO: ' + ', '.join('%s %s' % (n, 'ok' if v else 'FALLITA') for n, v in risultati.items()), flush=True)
    sys.exit(0 if all(risultati.values()) else 1)


if __name__ == '__main__':
    main()
