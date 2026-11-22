# -*- coding: utf-8 -*-
"""Prove di unita' di ia24 (modulo, non e' un esperimento): solo su testi NON Voynich (il libro latino nella disposizione del Voynich, SOLO_CONTROLLI=1).

    SOLO_CONTROLLI=1 PICCOLO20=1 python esperimenti/nuove_prove.py [nomi delle prove]

Che cosa prova (con pesi casuali grandi, perche' le differenze si vedano):
  vicini     le parole a una e a due modifiche trovate con gli indici sono le stesse di quelle trovate provando tutto il lessico;
  conteggi   il conteggio del lessico senza il foglio e' quello vero meno quello del foglio (e il foglio tolto non si vede);
  caselle    il modello a caselle: previsione che somma a 1, EM che non scende, parola campionata che segue la previsione;
  penna      scrivere segno per segno da' gli stessi logit del calcolo a tratti (W3, con la mistura delle caselle) e la stessa tabella dei primi due glifi (W1, W2);
  ingenuo    la perdita vettoriale di W1 e W2 coincide con un calcolo parola per parola scritto a parte (formule a mano delle strade e del lessico);
  somme      la miscela somma a 1; le sorgenti del lessico sommano a 1; una modifica somma alla probabilita' del suo tipo;
  modifiche  il campionatore delle modifiche segue la probabilita' teorica;
  scrittura  una pagina scritta da ogni imitatore con la scrittura vera e' ben formata;
  fase0      il costo di forma scomposto per posto somma a quello di ia20 (`rifarlo_ritocchi.costo_nuove`).
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
import ia20_imitatore_gradini as I20  # noqa: E402
import gradini_modelli as GM  # noqa: E402
import nuove_modelli as NM  # noqa: E402
import nuove_fase0 as NF  # noqa: E402
import rifarlo_ritocchi as R  # noqa: E402


def prepara(tipo, n_pagine=3, seme=7, scala=1.5, eco=False):
    """(m, ctx, lex, hmm, pagine preparate, grezze): un modello con pesi casuali grandi, un lessico che contiene le pagine di prova e altre 60."""
    import torch
    voc = I7.vocabolario()
    dp = I16.dati_pagine()
    if eco:                                                  # testo con eco locale piantata: le strade di pagina di W2 hanno qualcosa da fare
        import echi_modelli as EM
        D = I7.divisore()
        dp = I20.pagine_sintetiche(EM.sintetico_eco_contatto(I7.libro_vero(), 99, D, voc["unita"], eco=0.6, ritocco=0.6, inizio=0.0, contatto=0.0))
    ordinate = sorted(dp.values(), key=lambda d: len(d['tok']))
    a = int(0.55 * len(ordinate))
    pagine = ordinate[a:a + n_pagine]
    altre = [d for d in ordinate[:60]]
    K, S = 40, 12
    ctx = GM.Ctx(voc, GM.tipi_da_pagine(pagine + altre, GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    lex = NM.costruisci_lessico(pagine + altre, ctx)
    hmm = NM.adatta_caselle(lex, ctx, 4) if tipo == 'W3' else None
    ins = NM.prepara_insiemi([pagine], ctx, tipo, lex, hmm)[0]
    if tipo != 'W3':
        lex.riempi(NM.tipi_parole([ins]))
    cfg = NM.cfg_completa(tipo, voc, ctx, True)
    torch.manual_seed(seme)
    m = NM.costruisci(cfg)
    m.lessico = lex
    rng = torch.Generator().manual_seed(seme + 1)
    with torch.no_grad():
        for n, p in m.named_parameters():
            if n.startswith(('emb', 'gru', 'out')):
                p.mul_(scala * 2.0)
            elif n in ('Tsub', 'Tins'):
                p.copy_(torch.randn(p.shape, generator=rng))
            elif n == 'tau':
                p.copy_(torch.randn(p.shape, generator=rng) * 0.7)
            elif n in ('kap', 'gm'):
                p.copy_(torch.tensor([0.8, 1.3]))
            elif n == 'gb':
                p.copy_(torch.tensor([0.8, -0.3, 0.5]))
            elif n == 'gate.weight':
                p.mul_(40.0)
            elif n == 'gate.bias':
                p.fill_(0.2)
            elif n == 'mix.weight':
                p.mul_(4.0)
            elif n == 'mix.bias':
                p.copy_(torch.tensor([0.5, 0.0, -0.3, -0.8]))
            elif n in ('pq.weight', 'Wc'):
                p.mul_(6.0)
            elif n == 'rec':
                p.add_(torch.randn(p.shape, generator=rng) * 0.8)
            elif n == 'beta':
                p.add_(torch.randn(p.shape, generator=rng) * 0.8 + 3.0)
            elif n == 'gam':
                p.fill_(0.7)
    m.eval()
    return m, ctx, lex, hmm, ins, pagine


def ok(nome, condizione, dettaglio=''):
    print('%-10s %s %s' % (nome, 'OK  ' if condizione else 'ERRORE', dettaglio), flush=True)
    return bool(condizione)


# ---------------------------------------------------------------- vicini e conteggi

def prova_vicini():
    import random
    rnd = random.Random(5)
    U = 5
    parole = {tuple(rnd.randrange(U) for _ in range(rnd.randrange(1, 6))): rnd.randrange(1, 9) for _ in range(120)}
    lex = NM.Lessico(parole, U, 12)
    tutto = True
    n1 = n2 = 0
    for w in list(parole)[:25] + [tuple(rnd.randrange(U) for _ in range(rnd.randrange(2, 6))) for _ in range(25)]:
        r0, r1, r2 = lex.vicini(w)
        got1 = sorted((int(c), int(t), int(cx), int(x), float(n)) for c, t, cx, x, n in zip(*r1))
        brute1 = []
        for i, c in enumerate(lex.parole):
            if NM.distanza(c, w) == 1:
                for (t, cx, x, n) in GM.scripts(c, w, U):
                    brute1.append((i, t, cx, x, float(n)))
        tutto &= (got1 == sorted(brute1)) and (list(r0) == ([lex.idx[w]] if w in lex.idx else []))
        got2 = sorted(tuple(float(v) for v in row) for row in zip(*r2))
        brute2 = []
        for i in range(lex.K2):
            c = lex.parole[i]
            if NM.distanza(c, w) != 2:
                continue
            for cp in NM.n1_stringhe(c, U):
                if NM.distanza(cp, w) == 1:
                    for a in GM.scripts(c, cp, U):
                        for b in GM.scripts(cp, w, U):
                            brute2.append(tuple(float(v) for v in (i,) + a + b))
        tutto &= (got2 == sorted(brute2))
        n1 += len(got1)
        n2 += len(got2)
    return ok('vicini', tutto, '%d scritture a una modifica e %d percorsi a due modifiche: indici = tutto il lessico' % (n1, n2))


def prova_conteggi():
    m, ctx, lex, hmm, ins, pagine = prepara('W1', 3)
    f = pagine[0]['foglio']
    NN = lex.conteggi([f, 'nessun_foglio'])
    i, c = lex.foglio[f]
    tutto = bool(np.allclose(NN[0, i] + c, lex.n[i])) and bool(np.allclose(NN[1], lex.n))
    resto = np.ones(len(lex.parole), bool)
    resto[i] = False
    tutto &= bool(np.allclose(NN[0, resto], lex.n[resto]))
    return ok('conteggi', tutto, 'senza il foglio: %d parole toccate, %d senza di lui' % (len(i), int((NN[0] == 0).sum())))


# ---------------------------------------------------------------- caselle

def prova_caselle():
    from collections import Counter as C
    import random
    m, ctx, lex, hmm, ins, pagine = prepara('W1', 2)
    tipi = lex.parole
    h3 = NM.Caselle.adatta(tipi, ctx.U, NM.NSLOT, 3)
    h15 = NM.Caselle.adatta(tipi, ctx.U, NM.NSLOT, 15)
    tutto = h15.verosimiglianza >= h3.verosimiglianza - 1e-9
    for w in tipi[:50]:
        for l in range(len(w) + 1):
            p = np.exp(h15.predittivo(tuple(w[:l])))
            tutto &= abs(p.sum() - 1.0) < 1e-6 or l == 0
    # la parola campionata ha la distribuzione del primo glifo prevista
    rng = random.Random(1)
    cnt = C(h15.campiona(rng)[0] for _ in range(20000))
    pr = np.exp(h15.predittivo(()))[:ctx.U]
    dmax = max(abs(cnt[g] / 20000 - pr[g]) for g in range(ctx.U))
    tutto &= dmax < 0.02
    # le righe di A sommano a 1 con la fine
    tutto &= bool(np.allclose(h15.A.sum(1) + h15.fine, 1.0)) and bool(np.allclose(h15.E.sum(1), 1.0))
    bit = np.mean([sum(h15.bit_parola(w)) / len(w) for w in tipi[:300]])
    return ok('caselle', tutto, 'verosimiglianza %.3f (3 giri) -> %.3f (15 giri); primo glifo campionato: scarto massimo %.4f; %.2f bit per glifo sui tipi' % (
        h3.verosimiglianza, h15.verosimiglianza, dmax, bit))


# ---------------------------------------------------------------- penna e calcolo a tratti

def forward_chunks(m, ctx, P):
    """Per una pagina: (logits a tratti (Tin, V), lista per tratto di (out, pw, ultimo, a, c))."""
    import torch
    stato = GM.StatoRiga()
    res, det = [], []
    for (a, c) in P['chunks']:
        bt = NM.lotto_tratto([(P, (a, c))], ctx, m.tipo, m.lessico)
        X, Y, Mk, t, pw = NM.a_torch(bt, m.tipo)
        H = m.H
        h1 = (stato.h1 if stato.h1 is not None else torch.zeros(H))[None, None]
        h2 = (stato.h2 if stato.h2 is not None else torch.zeros(H))[None, None]
        with torch.no_grad():
            out = m(X, t, h1, h2)
            nll, ntok = m.nll(out, Y, Mk, pw)
        n = c - a
        res.append(out['logits'][0, :n].numpy())
        det.append((out, pw, m.ultimo, a, c))
        stato.h1 = out['y1'][0, n - 1].clone()
        stato.h2 = out['y2'][0, n - 1].clone()
    return np.concatenate(res), det


def prova_penna():
    import torch
    tutto = True
    msg = []
    for tipo in ('W3', 'W1', 'W2'):
        m, ctx, lex, hmm, ins, pagine = prepara(tipo, 3)
        voc = I7.vocabolario()
        pen = NM.Penna24(m, ctx, lex, hmm, 6000)
        dmax = cmax = 0.0
        for P in ins:
            lg_t, det = forward_chunks(m, ctx, P)
            pen.apri()
            lg_p = []
            tok = P['tok']
            tabelle = {}
            ws0 = {int(s): j for j, s in enumerate(P['ws0'])}
            for t in range(P['Tin']):
                lg_p.append(np.array(pen.dai(int(tok[t])), dtype=np.float64))
                if tipo != 'W3' and t in ws0:
                    tabelle[t] = pen.tabella_coppie()
            dmax = max(dmax, float(np.abs(np.array(lg_p) - lg_t).max()))
            if tipo == 'W3':
                pa = np.concatenate([x[0]['porta'][0].numpy().ravel() for x in det])
                dentro = pa > 0
                aa = pa[dentro]
                somma = np.concatenate([np.exp(x[0]['logits'][0].numpy()).sum(-1)[x[0]['porta'][0].numpy() > 0] for x in det])
                msg.append('porta %.2f-%.2f (media %.2f), somma delle probabilita %.1e dall\'uno' % (aa.min(), aa.max(), aa.mean(), float(np.abs(somma - 1).max())))
                tutto &= 0.02 < aa.mean() < 0.98 and float(np.abs(somma - 1).max()) < 1e-5
            if tipo != 'W3':
                for (out, pw, ult, a, c) in det:
                    if pw is None or pw['J'] == 0:
                        continue
                    rows, s0 = pw['rows'], pw['s0']
                    lp0 = torch.log_softmax(out['logits'][rows, s0], -1)
                    lgf = m.coppie(lp0, out['y1'][rows, s0], out['y2'][rows, s0]).numpy()
                    for q in range(len(rows)):
                        T = tabelle[a + int(s0[q])]
                        cmax = max(cmax, float(np.abs(T.reshape(-1) - lgf[q]).max()))
        tutto &= dmax < 1e-3 and cmax < 1e-3
        msg.append('%s logit %.1e%s' % (tipo, dmax, '' if tipo == 'W3' else ', tabella dei primi due glifi %.1e' % cmax))
    return ok('penna', tutto, '; '.join(msg))


# ---------------------------------------------------------------- calcolo ingenuo, parola per parola

def dist_tipo(u, t, psub, pins, U):
    """{parola: probabilita'} di un ritocco di tipo t (1 cambia, 2 aggiunge, 3 toglie) di `u`, in un posto uniforme, con le tabelle."""
    out = Counter()
    n = len(u)
    if t == 1:
        for i in range(n):
            for x in range(U):
                if x != u[i]:
                    out[u[:i] + (x,) + u[i + 1:]] += psub[u[i]][x] / n
    elif t == 2:
        for i in range(n + 1):
            cg = u[i - 1] if i > 0 else U
            for x in range(U):
                out[u[:i] + (x,) + u[i:]] += pins[cg][x] / (n + 1)
    elif t == 3 and n >= 2:
        for i in range(n):
            out[u[:i] + u[i + 1:]] += 1.0 / n
    return out


def dist1(u, tau, psub, pins, U):
    out = Counter()
    for t in (1, 2, 3):
        for w, p in dist_tipo(u, t, psub, pins, U).items():
            out[w] += tau[t - 1] * p
    return out


def ingenuo_pagina(m, ctx, lex, P, max_parole=None, stat=None):
    """Probabilita' (log, nat) di ogni parola della pagina `P` (con il terminatore) per W1 e W2, calcolata segno per segno con la penna e formule a mano."""
    import torch
    U, u0 = ctx.U, ctx.u0
    pen = NM.Penna24(m, ctx, lex, None, 6000)
    pen.apri()
    tok = P['tok']
    ws0, we0 = list(P['ws0']), list(P['we0'])
    inizi = {int(s): j for j, s in enumerate(ws0)}
    NNrow = lex.conteggi([P['foglio']])[0]
    kap, gm = [float(x) for x in m.kap.detach()], [float(x) for x in m.gm.detach()]
    tau = torch.softmax(m.tau, 0).detach().numpy()
    psub, pins = pen.tabelle_ritocco()
    nt = m.cfg['nt']
    lps = []
    lg_all = []
    for t in range(P['Tin']):
        lg = np.array(pen.dai(int(tok[t])), dtype=np.float64)
        lg_all.append(lg)
        if t in inizi:
            j = inizi[t]
            if max_parole is not None and j >= max_parole:
                lps.append(None)
                continue
            w = P['units'][j]
            T = pen.tabella_coppie()
            cand = pen.candidati() if m.tipo == 'W2' else []
            pf, pk, pc = pen.miscela(cand, T)
            # libero: somma dei log-probabilita' dei segni della parola e del terminatore (calcolati con i logit della penna, avanzando senza toccare lo stato)
            lfree = 0.0
            e0 = int(we0[j])
            lgs = []
            # i logit dei segni successivi li abbiamo solo dopo averli dati alla penna: li prendiamo dopo, nel secondo passaggio
            lps.append(dict(j=j, w=w, pf=pf, pk=pk, pc=pc, T=T, cand=cand, t0=t, e0=e0, term=int(P['wterm'][j])))
            # lessico
            wA = np.where(NNrow > 0, np.maximum(NNrow, 1e-6) ** kap[0], 0.0) * np.exp(gm[0] * T.reshape(-1)[lex.pair])
            qA = wA / wA.sum()
            K2 = lex.K2
            wB = np.where(NNrow[:K2] > 0, np.maximum(NNrow[:K2], 1e-6) ** kap[1], 0.0) * np.exp(gm[1] * T.reshape(-1)[lex.pair[:K2]])
            qB = wB / wB.sum()
            A0 = float(qA[lex.idx[w]]) if w in lex.idx else 0.0
            A1 = 0.0
            for i, c in enumerate(lex.parole):
                if abs(len(c) - len(w)) <= 1 and NM.distanza(c, w) == 1:
                    A1 += float(qA[i]) * dist1(c, tau, psub, pins, U).get(w, 0.0)
            A2 = 0.0
            for i in range(K2):
                c = lex.parole[i]
                if abs(len(c) - len(w)) > 2 or NM.distanza(c, w) != 2:
                    continue
                s = 0.0
                for cp, p1 in dist1(c, tau, psub, pins, U).items():
                    if NM.distanza(cp, w) == 1:
                        s += p1 * dist1(cp, tau, psub, pins, U).get(w, 0.0)
                A2 += float(qB[i]) * s
            lps[-1]['A'] = (A0, A1, A2)
            # strade di pagina (W2)
            cp_tot = 0.0
            if cand:
                for k, (c, f) in enumerate(cand):
                    for t_ in range(nt):
                        pw_ = (1.0 if c == w else 0.0) if t_ == 0 else dist_tipo(c, t_, psub, pins, U).get(w, 0.0)
                        cp_tot += float(pc[k][t_]) * pw_
            lps[-1]['cand_tot'] = cp_tot
    # secondo passaggio: i log-probabilita' dei segni liberi dai logit registrati
    out = []
    quote, presenti = [0.0] * 5, [0] * 5
    for d in lps:
        if d is None:
            continue
        t0, e0 = d['t0'], d['e0']
        lfree = 0.0
        for t in range(t0, e0 + 1):
            z = lg_all[t]
            lfree += float(z[int(tok[t + 1])] - (z.max() + math.log(np.exp(z - z.max()).sum())))
        z = lg_all[e0][[ctx.SP, ctx.EOL]]
        lr = float(z[d['term']] - (z.max() + math.log(np.exp(z - z.max()).sum())))
        A0, A1, A2 = d['A']
        r = math.exp(lr)
        parti = (d['pf'] * math.exp(lfree), r * d['pk'][0] * A0, r * d['pk'][1] * A1, r * d['pk'][2] * A2, r * d['cand_tot'])
        tot = sum(parti)
        for q in range(5):
            quote[q] += parti[q] / tot
            presenti[q] += parti[q] > 1e-12 * tot
        out.append(math.log(tot))
    if stat is not None:
        stat.update(quote=[x / max(len(out), 1) for x in quote], presenti=presenti)
    return out


def prova_ingenuo():
    tutto = True
    msg = []
    for tipo in ('W1', 'W2'):
        m, ctx, lex, hmm, ins, pagine = prepara(tipo, 1, eco=(tipo == 'W2'))
        P = ins[0]
        nmax = 40
        st = {}
        naive = ingenuo_pagina(m, ctx, lex, P, nmax, st)
        lg_t, det = forward_chunks(m, ctx, P)
        tot = []
        for (out, pw, ult, a, c) in det:
            if ult is not None and ult['tot'].numel():
                tot += ult['tot'].tolist()
        tot = tot[:len(naive)]
        dif = np.abs(np.array(naive) - np.array(tot))
        tutto &= float(dif.max()) < 5e-3
        msg.append('%s: %d parole, differenza massima %.1e nat (totale %.0f nat); quota media (libero, 0, 1, 2 modifiche, pagina) %s, parole con la strada non nulla %s' % (
            tipo, len(naive), float(dif.max()), float(-np.sum(tot)), ' '.join('%.2f' % x for x in st['quote']), st['presenti']))
        tutto &= st['presenti'][1] > 0 and st['presenti'][2] > 0 and st['presenti'][3] > 0
    return ok('ingenuo', tutto, '; '.join(msg))


# ---------------------------------------------------------------- somme e campionatore

def prova_somme():
    import torch
    m, ctx, lex, hmm, ins, pagine = prepara('W2', 1)
    P = ins[0]
    lg_t, det = forward_chunks(m, ctx, P)
    s_mix = max(float(x[2]['mix'].sum(1).max()) for x in det if x[2] is not None)          # libero + lessico: al massimo 1 (il resto va alle strade di pagina)
    # la miscela di W2 (libero + lessico + pagina) somma a 1 con le strade di pagina: dalla penna
    pen = NM.Penna24(m, ctx, lex, None, 6000)
    pen.apri()
    tok = P['tok']
    ws0 = {int(s) for s in P['ws0']}
    mass = []
    sorg = []
    for t in range(P['Tin']):
        pen.dai(int(tok[t]))
        if t in ws0 and len(mass) < 25:
            T = pen.tabella_coppie()
            cand = pen.candidati()
            pf, pk, pc = pen.miscela(cand, T)
            mass.append(pf + pk.sum() + (pc[:len(cand)].sum() if pc is not None and cand else 0.0))
            sorg.append((pen.pesi_sorgenti(T, 0).sum(), pen.pesi_sorgenti(T, 1).sum()))
    # una modifica: la probabilita' delle uscite somma a tau_sub + tau_ins + tau_del (la cancellazione manca per le parole di un glifo)
    psub, pins = pen.tabelle_ritocco()
    tau = torch.softmax(m.tau, 0).detach().numpy()
    ec = 0.0
    for u in [(1, 2, 3), (4, 0), (2, 2, 2, 5)]:
        d = dist1(u, tau, psub, pins, ctx.U)
        ec = max(ec, abs(sum(d.values()) - float(tau.sum())))
    u = (3,)
    ec = max(ec, abs(sum(dist1(u, tau, psub, pins, ctx.U).values()) - float(tau[0] + tau[1])))
    t_ok = max(abs(x[0] - 1) for x in sorg) < 1e-9 and max(abs(x[1] - 1) for x in sorg) < 1e-9
    tutto = s_mix <= 1.0 + 1e-6 and max(abs(x - 1.0) for x in mass) < 1e-5 and ec < 1e-5 and t_ok
    return ok('somme', tutto, 'miscela: penna %.1e dall\'uno, tratti al massimo %.6f; modifiche %.1e' % (max(abs(x - 1.0) for x in mass), s_mix, ec))


def prova_modifiche():
    import torch
    m, ctx, lex, hmm, ins, pagine = prepara('W1', 1)
    pen = NM.Penna24(m, ctx, lex, None, 6000)
    pen.apri()
    psub, pins = pen.tabelle_ritocco()
    tau = torch.softmax(m.tau, 0).detach().numpy()
    rng = np.random.default_rng(3)
    tutto = True
    msg = []
    for u in [(1, 2, 3, 4), (6, 6)]:
        teo = dist1(u, tau, psub, pins, ctx.U)
        N = 80000
        emp = Counter()
        for _ in range(N):
            w = GM.campiona_ritocco(u, 1 + int(rng.choice(3, p=tau)), psub, pins, rng)
            if w is not None:
                emp[w] += 1
        chiavi = set(teo) | set(emp)
        d = max(abs(emp[k] / N - teo.get(k, 0.0)) for k in chiavi)
        tutto &= d < 0.004
        msg.append('%.4f' % d)
    return ok('modifiche', tutto, 'scarto massimo fra frequenza e probabilita (80000 pescate): ' + ', '.join(msg))


# ---------------------------------------------------------------- scrittura e fase 0

def prova_scrittura():
    import ia24_parole_nuove as I24
    voc, D = I7.vocabolario(), I7.divisore()
    righe = I7.libro_vero()
    pp = I7.per_pagina(righe)
    nomi = list(pp)
    tutto = True
    msg = []
    regole = I20.RegoleScrittura(voc)
    for tipo in ('W1', 'W2', 'W3'):
        m, ctx, lex, hmm, ins, pagine = prepara(tipo, 2)
        pen = NM.Penna24(m, ctx, lex, hmm, 6000)
        rng = np.random.default_rng(11)
        conta = Counter()
        p = pagine[0]['nome']
        out = I24.scrivi_pagina24(m, ctx, lex, pen, regole, pp[p], voc, D, rng, conta)
        parole = [w for _, _, ps in out for w in ps]
        bene = len(parole) > 0 and all(len(w) > 0 and D(w) is not None for w in parole) and len(out) == len(pp[p])
        tutto &= bene
        msg.append('%s %d righe %d parole%s' % (tipo, len(out), len(parole), '' if tipo == 'W3' else ' (' + ', '.join('%s %d' % kv for kv in sorted(conta.items()) if not kv[0].endswith('nota') and not kv[0].endswith('nuova')) + ')'))
    return ok('scrittura', tutto, '; '.join(msg))


def prova_fase0():
    c = I7.contesto_A()
    glifi = I7.vocabolario()['unita']
    ogg = {f: NF.Piega(c['vere'], c['fold'], f, glifi, 40) for f in range(5)}
    pag = c['vere']
    M = NF.conta_pagine(pag, c['fold'], ogg, glifi)
    d, e, S = NF.riassunto(M, len(glifi), boot=20)
    bit = gl = nn = tot = 0
    for f in range(5):
        pg = {p: rows for p, rows in c['vere'].items() if c['fold'][p] == f}
        pv = {p: rows for p, rows in c['vere'].items() if c['fold'][p] != f}
        cnt = Counter(w for rows in pv.values() for _, ws in rows for w in ws)
        x = R.costo_nuove(R.Forma(cnt), pg, set(cnt))
        bit, gl, nn, tot = bit + x[0], gl + x[1], nn + x[2], tot + x[3]
    s = d['forma_primo'] + d['forma_secondo'] + d['forma_terzo'] + d['forma_dopo'] + d['forma_fine']
    tutto = abs(d['costo_forma'] - bit / gl) < 1e-9 and abs(s - d['costo_forma']) < 1e-9 and abs(d['quota_nuove'] - nn / tot) < 1e-12
    # le parole piantate sono tutte nuove e il controllo di "ritocco" porta s_top alto
    r = {}
    for modo in ('ritocco', 'libero', 'caselle'):
        rows = NF.pianta(c['vere'], c['fold'], ogg, glifi, modo, 1)
        Mp = NF.conta_pagine(rows, c['fold'], ogg, glifi)
        dp, _, _ = NF.riassunto(Mp, len(glifi), boot=0)
        r[modo] = (dp['quota_nuove'], dp['top_2'], dp['costo_caselle'], dp['costo_forma'])
    tutto &= abs(r['ritocco'][0] - d['quota_nuove']) < 0.01 and abs(r['libero'][0] - d['quota_nuove']) < 0.01
    return ok('fase0', tutto, 'costo di forma %.4f = %.4f (ia20), parti %.4f; quota nuove %.4f; piantate (top_2, caselle, forma): %s' % (
        d['costo_forma'], bit / gl, s, d['quota_nuove'], '; '.join('%s %.2f %.2f %.2f' % (k, v[1], v[2], v[3]) for k, v in r.items())))


def prova_bitparole():
    tutto = True
    msg = []
    for tipo in ('W1', 'W2', 'W3'):
        m, ctx, lex, hmm, ins, pagine = prepara(tipo, 2)
        lex_p = NM.Lessico({w: float(c) for w, c in list(zip(lex.parole, lex.n))[::2]}, ctx.U, ctx.K) if tipo == 'W3' else lex      # W3: meta' delle parole, cosi' ce ne sono di nuove
        r = NM.nat_per_parola(m, ctx, ins, lex_p, piantate={P['nome']: [True] * P['nw'] for P in ins})
        n = r['segni_nuove'] + r['segni_note']
        a = (r['nat_nuove'] + r['nat_note']) / n / math.log(2)
        b = NM.bpc_pagine(m, ctx, ins)
        tutto &= r['segni_piantate'] == n and abs(r['nat_piantate'] - r['nat_nuove'] - r['nat_note']) < 1e-2 and abs(a - b) < 1e-4 and (r['segni_nuove'] > 0 or tipo != 'W3') and r['segni_note'] > 0
        msg.append('%s: %.5f contro %.5f (segni nuovi %d, noti %d)' % (tipo, a, b, r['segni_nuove'], r['segni_note']))
    return ok('bitparole', tutto, 'bit per segno delle parole nuove e note sommano al totale: ' + '; '.join(msg))


PROVE = dict(bitparole=prova_bitparole, vicini=prova_vicini, conteggi=prova_conteggi, caselle=prova_caselle, penna=prova_penna, ingenuo=prova_ingenuo, somme=prova_somme, modifiche=prova_modifiche,
             scrittura=prova_scrittura, fase0=prova_fase0)

if __name__ == '__main__':
    scelte = sys.argv[1:] or list(PROVE)
    tutto = True
    for n in scelte:
        tutto &= PROVE[n]()
    print('TUTTO OK' if tutto else 'CI SONO ERRORI')
