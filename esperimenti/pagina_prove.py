# -*- coding: utf-8 -*-
"""Prove di unita' di ia23 (modulo, non e' un esperimento): solo su testi NON Voynich (il libro latino nella disposizione del Voynich, SOLO_CONTROLLI=1).

    SOLO_CONTROLLI=1 PICCOLO20=1 python esperimenti/pagina_prove.py [nomi delle prove]

Che cosa prova (con pesi casuali grandi, perche' le differenze si vedano):
  coppie     le coppie (parola, candidato, strada) trovate con gli indici sono le stesse di quelle trovate provando tutti i candidati;
  entrate    le corrispondenze di P1 raggruppate per classe coincidono con quelle calcolate candidato per candidato;
  stato      le classi (distanza, occorrenze) dello stato della pagina coincidono con un calcolo ingenuo;
  penna      scrivere segno per segno da' gli stessi logit del calcolo a tratti (P1) e gli stessi pesi del puntatore (P2, P3);
  somme      le miscele sommano a 1; ogni strada somma a 1 sulle sue parole (la normalizzazione di P1 e' esatta per costruzione, softmax: si prova con `ingenuo`);
  ingenuo    la perdita vettoriale coincide con un calcolo parola per parola scritto a parte (formule a mano delle strade);
  scrittura  una pagina scritta da ogni imitatore con la scrittura vera e' ben formata.
Nessuna parola del latino esce da qui: solo numeri.
"""
import os
import sys
import math
from collections import Counter

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
import gradini_modelli as GM  # noqa: E402
import echi_modelli as EM  # noqa: E402
import pagina_modelli as PM  # noqa: E402


def prepara(tipo, n_pagine=4, seme=7, scala=1.5, piccolo=True):
    """(m, ctx, fc, pagine preparate, pagine grezze): un modello con pesi casuali grandi e alcune pagine."""
    import torch
    voc = I7.vocabolario()
    dp = I16.dati_pagine()
    ordinate = sorted(dp.values(), key=lambda d: len(d['tok']))
    a = int(0.55 * len(ordinate))
    pagine = ordinate[a:a + n_pagine]                  # pagine di lunghezza medio-alta (con piu' righe e piu' ripetizioni)
    K, S = (40, 12) if piccolo else (GM.K_TIPI, GM.S_CAND)
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(pagine, GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    fc = PM.tabella_freq(PM.conta_tipi(pagine, ctx))
    ins = PM.prepara_insiemi([pagine], ctx, tipo, fc)[0]
    cfg = PM.cfg_completa(tipo, voc, ctx, piccolo)
    torch.manual_seed(seme)
    m = PM.costruisci(cfg)
    with torch.no_grad():
        for n, p in m.named_parameters():
            if n.startswith(('emb', 'gru', 'out')):
                p.mul_(scala * 2.0)
            elif n in ('rd', 'rc', 'rf'):
                p.add_(torch.randn_like(p) * 0.8)
            elif n == 'bet':
                p.copy_(torch.randn_like(p) * 1.0)
            elif n == 'beta':
                p.add_(torch.randn_like(p) * 1.0 + 3.0)
            elif n in ('Tsub', 'Tins'):
                p.copy_(torch.randn_like(p) * 1.0)
            elif n == 'gam':
                p.fill_(0.7)
            elif n in ('pq.weight', 'Wc'):
                p.mul_(6.0)
    m.eval()
    return m, ctx, fc, ins, pagine


def ok(nome, condizione, dettaglio=''):
    print('%-10s %s %s' % (nome, 'OK  ' if condizione else 'ERRORE', dettaglio), flush=True)
    return bool(condizione)


# ---------------------------------------------------------------- coppie, entrate, stato

def prova_coppie():
    tutto = True
    for tipo in ('P2', 'P3'):
        m, ctx, fc, ins, pagine = prepara(tipo, 6)
        n = nbr = 0
        for P in ins:
            a = PM.coppie_pagina(P['units'], P['tl'], P['nj'], ctx, tipo)
            b = PM.coppie_brute(P['units'], P['tl'], P['nj'], ctx, tipo)
            sa = sorted(zip(*[a[k].tolist() for k in ('pj', 'pk', 'pt', 'pc', 'px', 'pn')]))
            sb = sorted(zip(*[b[k].tolist() for k in ('pj', 'pk', 'pt', 'pc', 'px', 'pn')]))
            tutto &= (sa == sb)
            n += len(sa)
            nbr += len(sb)
        tutto &= ok('coppie', tutto, '%s: %d coppie con gli indici, %d provando tutto' % (tipo, n, nbr))
    return tutto


def prova_entrate():
    m, ctx, fc, ins, pagine = prepara('P1', 4)
    tutto = True
    for P in ins:
        brute = Counter()
        units, tl, nj, Tin = P['units'], P['tl'], P['nj'], P['Tin']
        for j, (s, e) in enumerate(P['words']):
            w = units[j]
            n = int(nj[j])
            for k in range(n):
                cl = int(P['DC'][j, k]) * (PM.NCC * PM.NFC) + int(P['CC'][j, k]) * PM.NFC + int(P['fcp'][k])
                per = EM.spinte_parola(w, tl[k])
                for l in range(len(w) + 1):
                    t = s - 1 + l
                    if t >= Tin:
                        continue
                    for (tau, sg) in per[l]:
                        brute[(t, cl, tau, sg)] += 1
        got = Counter()
        for t, cl, tau, sg, mu in zip(P['ft'].tolist(), P['fcl'].tolist(), P['ftau'].tolist(), P['fs'].tolist(), P['fm'].tolist()):
            got[(t, cl, tau, sg)] += mu
        tutto &= (got == brute)
        EM._MEMO.clear()
    return ok('entrate', tutto, 'P1: corrispondenze raggruppate = candidato per candidato (%d pagine)' % len(ins))


def prova_stato():
    m, ctx, fc, ins, pagine = prepara('P2', 5)
    tutto = True
    for P in ins:
        units = P['units']
        linee = [int(P['linea'][s]) for s, e in P['words']]
        for j in range(len(units)):
            vistiti = []
            for q in range(j):
                if units[q] not in vistiti:
                    vistiti.append(units[q])
            n = len(vistiti)
            tutto &= (n == int(P['nj'][j])) and vistiti == P['tl'][:n]
            for k, c in enumerate(vistiti):
                idx = [q for q in range(j) if units[q] == c]
                ult = idx[-1]
                dl = linee[j] - linee[ult]
                dc = 0 if ult == j - 1 else 1 if dl <= 0 else 2 if dl == 1 else 3 if dl == 2 else 4 if dl <= 5 else 5
                cc = 0 if len(idx) <= 1 else 1 if len(idx) == 2 else 2 if len(idx) <= 4 else 3
                tutto &= (int(P['DC'][j, k]) == dc and int(P['CC'][j, k]) == cc)
    return ok('stato', tutto, 'classi di distanza e di occorrenze = calcolo ingenuo (%d pagine)' % len(ins))


# ---------------------------------------------------------------- penna e calcolo a tratti

def logits_a_tratti(m, ctx, P):
    """(Tin, V): i logit di una pagina col calcolo a tratti (stato che passa da un tratto al successivo)."""
    import torch
    stato = GM.StatoRiga()
    res = []
    dettagli = []
    for (a, c) in P['chunks']:
        bt = PM.lotto_tratto([(P, (a, c))], ctx, m.tipo)
        X, Y, Mk, t, pw = PM.a_torch(bt, m.tipo)
        H = m.H
        h1 = (stato.h1 if stato.h1 is not None else torch.zeros(H))[None, None]
        h2 = (stato.h2 if stato.h2 is not None else torch.zeros(H))[None, None]
        with torch.no_grad():
            out = m(X, t, h1, h2)
            nll, ntok = m.nll(out, Y, Mk, pw)
        n = c - a
        res.append(out['logits'][0, :n].numpy())
        dettagli.append((out, pw, m.ultimo, a, c, Y, Mk))
        stato.h1 = out['y1'][0, n - 1].clone()
        stato.h2 = out['y2'][0, n - 1].clone()
    return np.concatenate(res), dettagli


def prova_penna():
    tutto = True
    for tipo in ('P1', 'P2', 'P3'):
        m, ctx, fc, ins, pagine = prepara(tipo, 3)
        voc = I7.vocabolario()
        pen = PM.Penna23(m, ctx, fc, 6000)
        dmax = pmax = 0.0
        npar = 0
        for P in ins:
            lg_t, det = logits_a_tratti(m, ctx, P)
            pen.apri()
            lg_p = []
            tok = P['tok']
            for t in range(P['Tin']):
                lg_p.append(np.array(pen.dai(int(tok[t])), dtype=np.float64))
            lg_p = np.array(lg_p)
            dmax = max(dmax, float(np.abs(lg_p - lg_t).max()))
            if tipo != 'P1':
                # pesi del puntatore ai primi simboli di ogni parola: pen.puntatore_pagina a inizio parola contro il calcolo a tratti
                pen.apri()
                ws0 = {int(s): j for j, s in enumerate(P['ws0'])}
                lpp_t = {}
                lpf_t = {}
                for (out, pw, ult, a, c, Y, Mk) in det:
                    if pw is None or pw['J'] == 0:
                        continue
                    rows, s0 = pw['rows'].numpy(), pw['s0'].numpy()
                    for q in range(len(rows)):
                        j = int(np.searchsorted(P['ws0'], a + s0[q]))
                        lpf_t[j] = float(np.exp(ult['lpf'][q].item()))
                        lpp_t[j] = np.exp(ult['lpp'][q].numpy())
                for t in range(P['Tin']):
                    pen.dai(int(tok[t]))
                    if t in ws0:
                        j = ws0[t]
                        K = int(P['nj'][j])
                        if K == 0:
                            continue
                        pf, pi = pen.puntatore_pagina()
                        npar += 1
                        pmax = max(pmax, abs(pf - lpf_t[j]), float(np.abs(pi - lpp_t[j][:K]).max()))
        if tipo == 'P1':
            tutto &= ok('penna', dmax < 5e-4, 'P1: differenza massima fra scrittura e tratti sui logit %.2e (logit fino a %.1f)' % (dmax, float(np.abs(lg_t).max())))
        else:
            tutto &= ok('penna', dmax < 5e-4 and pmax < 5e-4, '%s: logit %.2e, pesi del puntatore %.2e su %d inizi di parola' % (tipo, dmax, pmax, npar))
    return tutto


# ---------------------------------------------------------------- somme

def prova_somme():
    import torch
    tutto = True
    for tipo in ('P2', 'P3'):
        m, ctx, fc, ins, pagine = prepara(tipo, 3)
        scarto = 0.0
        for P in ins:
            lg_t, det = logits_a_tratti(m, ctx, P)
            for (out, pw, ult, a, c, Y, Mk) in det:
                if pw is None or pw['J'] == 0:
                    continue
                lpp, lpf = ult['lpp'], ult['lpf']
                v = pw['valid']
                tot = torch.exp(lpf) + (torch.exp(lpp) * v[:, :, None]).sum((1, 2))
                scarto = max(scarto, float((tot - 1).abs().max()))
        tutto &= ok('somme', scarto < 5e-6, '%s: pi libero + pi candidati = 1, scarto massimo %.2e' % (tipo, scarto))
        # ogni strada somma a 1 sulle sue parole
        lsub, lins = m.tabelle()
        psub, pins = lsub.exp().detach().numpy(), lins.exp().detach().numpy()
        U = ctx.U
        c = (3, 5, 3, 7)
        parole = {1: Counter(), 2: Counter(), 3: Counter()}
        n = len(c)
        for i in range(n):
            for x in range(U):
                if x != c[i]:
                    w = c[:i] + (x,) + c[i + 1:]
                    parole[1][w] = 1
        for i in range(n + 1):
            for x in range(U):
                parole[2][c[:i] + (x,) + c[i:]] = 1
        for i in range(n):
            parole[3][c[:i] + c[i + 1:]] = 1
        for st in (1, 2, 3):
            s = 0.0
            for w in parole[st]:
                for (t_, cx, x_, n_) in GM.scripts(c, w, U):
                    if t_ != st:
                        continue
                    if st == 1:
                        s += psub[cx, x_] / n_
                    elif st == 2:
                        s += pins[cx, x_] / n_
                    else:
                        s += 1.0 / n_
            tutto &= ok('strada', abs(s - 1.0) < 1e-5, '%s: la strada %d somma a %.7f' % (tipo, st, s))
    return tutto


# ---------------------------------------------------------------- calcolo ingenuo parola per parola

def prova_ingenuo():
    import torch
    tutto = True
    for tipo in ('P1', 'P2', 'P3'):
        m, ctx, fc, ins, pagine = prepara(tipo, 3)
        lsub, lins = m.tabelle() if tipo != 'P1' else (None, None)
        if tipo == 'P1':
            # la perdita a tratti coincide col -log delle probabilita' passo passo della penna
            pen = PM.Penna23(m, ctx, fc, 6000)
            diff = 0.0
            for P in ins:
                lg_t, det = logits_a_tratti(m, ctx, P)
                pen.apri()
                tot = 0.0
                tok = P['tok']
                for t in range(P['Tin']):
                    lg = np.array(pen.dai(int(tok[t])), dtype=np.float64)
                    if int(tok[t + 1]) >= ctx.primo:
                        lp = lg - (lg.max() + math.log(np.exp(lg - lg.max()).sum()))
                        tot -= lp[int(tok[t + 1])]
                stato = GM.StatoRiga()
                nll_c = 0.0
                for (a, c) in P['chunks']:
                    nl, nt = PM.passa_tratto(m, ctx, [(P, (a, c))], [stato])
                    nll_c += nl
                diff = max(diff, abs(tot - nll_c))
            tutto &= ok('ingenuo', diff < 2e-3, 'P1: perdita a tratti = -log delle probabilita' + ' passo passo, differenza massima %.2e nat' % diff)
            continue
        psub, pins = lsub.exp().detach().numpy(), lins.exp().detach().numpy()
        U = ctx.U
        u0, SP, EOL = ctx.u0, ctx.SP, ctx.EOL
        pen = PM.Penna23(m, ctx, fc, 6000)
        diff = 0.0
        npar = 0
        for P in ins:
            tok = [int(x) for x in P['tok']]
            pen.apri()
            lgs = []
            pis = {}
            for t in range(P['Tin']):
                lg = np.array(pen.dai(tok[t]), dtype=np.float64)
                lgs.append(lg)
            lgs = np.array(lgs)
            lps = lgs - (lgs.max(1, keepdims=True) + np.log(np.exp(lgs - lgs.max(1, keepdims=True)).sum(1, keepdims=True)))
            # pesi del puntatore con la penna
            pen.apri()
            ws0 = {int(s): j for j, s in enumerate(P['ws0'])}
            pp = {}
            for t in range(P['Tin']):
                pen.dai(tok[t])
                if t in ws0 and int(P['nj'][ws0[t]]) > 0:
                    pp[ws0[t]] = pen.puntatore_pagina()
            nt = PM.NT_PUNT[tipo]
            tot_naive = {}
            for j, (s, e) in enumerate(P['words']):
                w = P['units'][j]
                s0, e0 = s - 1, e - 1
                libero = float(sum(lps[t, tok[t + 1]] for t in range(s0, e0 + 1)))
                term = 0 if tok[e] == SP else 1
                lt = lgs[e0, [SP, EOL]]
                logr = lt[term] - (lt.max() + math.log(np.exp(lt - lt.max()).sum()))
                if j not in pp:
                    tot_naive[j] = libero
                    continue
                pf, pi = pp[j]
                n = int(P['nj'][j])
                acc = 0.0
                for k in range(n):
                    c = P['tl'][k]
                    lw, lc = len(w), len(c)
                    pr = [0.0] * nt
                    if w == c:
                        pr[0] = 1.0
                    if lw == lc:
                        d = [i for i in range(lc) if w[i] != c[i]]
                        if len(d) == 1:
                            pr[1] = psub[c[d[0]], w[d[0]]] / lc
                    if lw == lc + 1:
                        for i in range(lw):
                            if w[:i] + w[i + 1:] == c:
                                pr[2] += pins[c[i - 1] if i > 0 else U, w[i]] / lw
                    if lw == lc - 1 and lw >= 1:
                        for i in range(lc):
                            if c[:i] + c[i + 1:] == w:
                                pr[3] += 1.0 / lc
                    if tipo == 'P3':
                        p0 = math.exp(lps[s0, u0 + w[0]])
                        p1 = math.exp(lps[s0 + 1, u0 + w[1]]) if lw >= 2 else 0.0
                        if lw == lc and lc >= 1 and w[1:] == c[1:]:
                            pr[4] = p0
                        if lw == lc + 1 and w[1:] == c:
                            pr[5] = p0
                        if lw == lc and lc >= 2 and w[2:] == c[2:]:
                            pr[6] = p0 * p1
                    for q in range(nt):
                        acc += pi[k, q] * pr[q]
                cop = acc * math.exp(logr)
                tot_naive[j] = math.log(pf * math.exp(libero) + cop) if (pf * math.exp(libero) + cop) > 0 else float('-inf')
            # confronto col calcolo vettoriale a tratti
            stato = GM.StatoRiga()
            tot_v = {}
            for (a, c) in P['chunks']:
                bt = PM.lotto_tratto([(P, (a, c))], ctx, tipo)
                X, Y, Mk, t_, pw = PM.a_torch(bt, tipo)
                H = m.H
                h1 = (stato.h1 if stato.h1 is not None else torch.zeros(H))[None, None]
                h2 = (stato.h2 if stato.h2 is not None else torch.zeros(H))[None, None]
                with torch.no_grad():
                    out = m(X, t_, h1, h2)
                    m.nll(out, Y, Mk, pw)
                n_ = c - a
                stato.h1 = out['y1'][0, n_ - 1].clone()
                stato.h2 = out['y2'][0, n_ - 1].clone()
                if pw is not None and pw['J'] > 0:
                    for q, s0q in enumerate(pw['s0'].tolist()):
                        j = int(np.searchsorted(P['ws0'], a + s0q))
                        tot_v[j] = float(m.ultimo['tot'][q])
            for j in tot_v:
                diff = max(diff, abs(tot_v[j] - tot_naive[j]))
                npar += 1
        tutto &= ok('ingenuo', diff < 5e-4, '%s: perdita vettoriale = calcolo ingenuo parola per parola, differenza massima %.2e nat su %d parole' % (tipo, diff, npar))
    return tutto


# ---------------------------------------------------------------- scrittura

def prova_scrittura():
    import numpy as np_
    import ia20_imitatore_gradini as I20
    import ia23_pagina_intera as I23
    tutto = True
    voc, D = I7.vocabolario(), I7.divisore()
    righe = I7.libro_vero()
    pp = I7.per_pagina(righe)
    nome = list(pp)[3]
    rp = pp[nome]
    regole = I20.RegoleScrittura(voc)
    for tipo in ('P1', 'P2', 'P3'):
        m, ctx, fc, ins, pagine = prepara(tipo, 3, scala=0.5)
        pen = PM.Penna23(m, ctx, fc, 6000)
        rng = np_.random.default_rng(5)
        conta = Counter()
        out = I23.scrivi_pagina23(m, ctx, pen, regole, rp, voc, D, rng, conta)
        ok_ = len(out) == len(rp) and all(len(ps) >= 1 for _, _, ps in out)
        ok_ &= all(D(w) and ''.join(D(w)) == w for _, _, ps in out for w in ps)
        tutto &= ok('scrittura', ok_, '%s: pagina di %d righe scritta, %d parole, modi %s' % (tipo, len(out), sum(len(ps) for _, _, ps in out), dict(conta)))
    return tutto


PROVE = dict(coppie=prova_coppie, entrate=prova_entrate, stato=prova_stato, penna=prova_penna, somme=prova_somme, ingenuo=prova_ingenuo, scrittura=prova_scrittura)


def main():
    nomi = sys.argv[1:] or list(PROVE)
    esito = {}
    for n in nomi:
        esito[n] = PROVE[n]()
    print('RIEPILOGO', {k: ('ok' if v else 'ERRORE') for k, v in esito.items()}, flush=True)
    return all(esito.values())


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
