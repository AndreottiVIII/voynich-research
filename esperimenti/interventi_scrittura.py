# -*- coding: utf-8 -*-
"""Supporto di ia30 (modulo, non e' un esperimento): scrivere un libro con un intervento sul contesto, e le misure leggere dei tratti.

Che cosa c'e' qui, in parole semplici
- `scrivi_pagina30`: come la scrittura di ia20/ia22 (segno per segno; per i modelli col puntatore, a inizio parola si pesca la scelta fra "libero" e
  "copia e ritocca"), ma con un INTERVENTO sulla "percezione" della rete: quello che la rete ha davanti e' diverso da quello che viene scritto.
    parola      quando una parola e' finita, la rete la rilegge con qualche glifo cambiato (ultimo, ultime due, primo, tutta) e solo dopo "vede" lo spazio;
                il testo scritto resta la parola vera; i candidati del puntatore restano le parole vere (l'intervento tocca solo la GRU e l'attenzione);
    riga        quando la riga e' finita, la rete la rilegge rimescolata, oppure sostituita con una riga di un'altra pagina: la riga sopra "percepita"
                diventa anche la fonte dei candidati del puntatore;
    testa       la fascia di lunghezza della riga (segno N della testa) e' una fascia a caso diversa dalla vera;
    riempimento un segno mai visto (il segno vuoto) dopo ogni spazio e dopo ogni testa di riga;
    puntatore   (solo E2 e M5) si tolgono dai candidati tutti tranne quelli ammessi: nessuno, solo la parola prima (posto 1), solo il posto 2, solo la riga
                sopra, solo la riga in corso; le probabilita' si rinormalizzano.
  Le scelte casuali dell'intervento usano un generatore a parte: con l'intervento "nullo" (rilegge la stessa cosa) il libro e' IDENTICO a quello senza
  intervento con lo stesso seme (prova di integrita').
- `misure_leggere`: le misure veloci sul libro scritto: contatto (g di ia08), eco per classe (copia o variante di una parola della riga in corso o della riga
  sopra, con il controllo "lontani"), firma dei bordi (ia17), aderenza della lunghezza di riga alla fascia della testa.
Nessuna parola del manoscritto compare qui.
"""
import math
import os
import random
import sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import gradini_modelli as GM  # noqa: E402
import echi_fase0 as F0  # noqa: E402
import interventi_motore as IM  # noqa: E402

# nome -> (tipo, parametro)
CONDIZIONI = OrderedDict([
    ('base', ('base', None)), ('nul', ('parola', 'nul')),
    ('u1', ('parola', 'u1')), ('u2', ('parola', 'u2')), ('p2', ('parola', 'p2')), ('p1', ('parola', 'p1')), ('pw', ('parola', 'pw')),
    ('rs_m', ('riga', 'rs_m')), ('rs_p', ('riga', 'rs_p')), ('rs_a', ('riga', 'rs_a')),
    ('hN', ('testa', 'hN')), ('fill', ('fill', None)),
    ('ptr_off', ('ptr', 'off')), ('ptr_sopra', ('ptr', 'sopra')), ('ptr_riga', ('ptr', 'riga')), ('ptr_d1', ('ptr', 'd1')), ('ptr_d2', ('ptr', 'd2'))])
SOLO_PUNTATORE = ('ptr_off', 'ptr_sopra', 'ptr_riga', 'ptr_d1', 'ptr_d2')


def maschera(par, pf, ppi, ncand, n_cur):
    """Tiene fra i candidati solo quelli ammessi e rinormalizza (libero + candidati ammessi = 1). ncand = candidati veri; n_cur = quanti sono della riga in corso."""
    keep = np.zeros(ppi.shape[0], bool)
    if par == 'sopra':
        keep[n_cur:ncand] = True
    elif par == 'riga':
        keep[:min(n_cur, ncand)] = True
    elif par == 'd1':
        keep[:min(1, ncand)] = True
    elif par == 'd2':
        keep[1:min(2, ncand)] = True
    p = ppi.copy()
    p[~keep] = 0.0
    z = pf + float(p.sum())
    return pf / z, p / z


def _units(parola_idx):
    return tuple(parola_idx)


def scrivi_pagina30(L, cond, regole, rp, voc, D, rng, conta, don, rng_h, nome_pagina):
    """Una pagina con la disposizione `rp` e l'intervento `cond` (nome di CONDIZIONI). `rng` (numpy) per la scelta delle parole; `rng_h` (random.Random) per le
    scelte dell'intervento. -> lista (pagina, inizio, parole)."""
    pen, ctx = L.pen, L.ctx
    SP, EOL, u0 = ctx.SP, ctx.EOL, ctx.u0
    unita = voc['unita']
    tipo_c, par = CONDIZIONI[cond]
    nt = 4 if L.punt else 0
    if tipo_c == 'ptr' and not nt:
        raise ValueError('intervento sul puntatore su un modello senza puntatore')
    campiona = _campiona
    pen.apri()
    lg = None
    for t in I7_testa_pagina(rp, voc):
        lg = pen.dai(t)
    if nt:
        psub, pins = L.tab
    out = []
    righe_scritte = []                                              # righe gia' scritte nella pagina (liste di tuple di glifi), per rs_p
    for j, x in enumerate(rp):
        testa = list(I7_testa_riga(x, j, voc, D))
        if tipo_c == 'testa':
            idx = voc['idx']
            alt = [idx['N:%d' % b] for b in range(8) if idx['N:%d' % b] != testa[2]]
            testa[2] = rng_h.choice(alt)
        for t in testa:
            lg = pen.dai(t)
        if tipo_c == 'fill':
            lg = pen.dai(0)
        f_riga = foto(pen) if tipo_c == 'riga' else None
        parole, lung, prima, fine = [], 0, 'inizio', False
        parole_riga = []                                            # parole vere della riga (tuple di indici di glifo)
        while not fine:
            f_par = foto(pen) if tipo_c == 'parola' else None
            w2 = None
            if nt:
                cand = pen.candidati()
                if cand:
                    pf, ppi = pen.puntatore(cand)
                    ppi = ppi[:len(cand)]
                    if tipo_c == 'ptr':
                        n_cur = min(len(pen.righe_parole.get(pen.linea, [])), ctx.S)
                        pf, ppi = maschera(par, pf, ppi, len(cand), n_cur)
                    pr = np.concatenate([[pf], ppi.reshape(-1)])
                    pr = pr / pr.sum()
                    for _ in range(8):
                        idx_ = int(rng.choice(len(pr), p=pr))
                        if idx_ == 0:
                            break
                        k, tipo_r = divmod(idx_ - 1, nt)
                        w2 = GM.campiona_ritocco(cand[k][0], tipo_r, psub, pins, rng)
                        if w2 is not None:
                            stringhe = [unita[u] for u in w2]
                            if D(''.join(stringhe)) == stringhe:
                                conta[('uguale', 'cambia', 'aggiunge', 'toglie')[tipo_r]] += 1
                                break
                        w2 = None
                    conta['libero' if w2 is None else 'copia'] += 1
            if w2 is not None:
                for u in w2:
                    lg = pen.dai(u0 + u)
                lung += len(w2)
                ammessi = [SP, EOL] if lung < voc['lmax'] else [EOL]
                z = np.array([lg[a] for a in ammessi])
                z = np.exp(z - z.max())
                s = ammessi[campiona(z / z.sum(), rng)]
                parola_idx = tuple(w2)
                parole.append(''.join(unita[u] for u in w2))
                prima = 'spazio'
                if s == EOL:
                    fine = True
                else:
                    lung += 1
            else:
                parola = []
                parola_idx = []
                while True:
                    amm = regole.ammessi(parola, lung, prima)
                    z = np.array([lg[a] for a in amm])
                    z = np.exp(z - z.max())
                    s = amm[campiona(z / z.sum(), rng)]
                    if s == EOL or s == SP:
                        break
                    lg = pen.dai(s)
                    lung += 1
                    parola.append(regole.unita[s])
                    parola_idx.append(s - u0)
                    prima = 'segno'
                parola_idx = tuple(parola_idx)
                parole.append(''.join(parola))
                prima = 'spazio' if s == SP else prima
                if s == EOL:
                    fine = True
                else:
                    lung += 1
            parole_riga.append(parola_idx)
            # ---- il terminatore s (spazio o fine riga) non e' ancora stato dato alla rete: qui agiscono gli interventi
            percepita = False
            if tipo_c == 'parola' and parola_idx:
                q = IM.modifica_parola(par, parola_idx, don, rng_h)
                if q is not None:
                    ripristina_(pen, f_par)
                    for u in q:
                        lg = pen.dai(u0 + u)
                    percepita = True
                    conta['interventi'] += 1
            if tipo_c == 'riga' and s == EOL:
                nuova = _riga_percepita(par, parole_riga, righe_scritte, don, rng_h, nome_pagina)
                if nuova is not None:
                    ripristina_(pen, f_riga)
                    for t in IM._tok_parole(nuova, ctx, EOL)[:-1]:
                        lg = pen.dai(t)
                    conta['interventi'] += 1
            lg = pen.dai(s)
            if percepita:                                         # i candidati del puntatore restano le parole vere
                pen.righe_parole[pen.linea][-1] = (parola_idx, GM.feat_parola(parola_idx, ctx))
            if tipo_c == 'fill' and s == SP:
                lg = pen.dai(0)
        righe_scritte.append(list(parole_riga))
        out.append((x['pagina'], x['ini'], parole))
    return out


def I7_testa_pagina(rp, voc):
    import ia07_voynich_neurale as I7
    return I7.testa_pagina(rp, voc)


def I7_testa_riga(x, j, voc, D):
    import ia07_voynich_neurale as I7
    return I7.testa_riga(x, j, voc, D)


def _campiona(pr, rng):
    import ia16_imitatore as I16
    return I16.campiona(pr, rng)


def ripristina_(pen, f):
    IM.ripristina(pen, f)


def foto(pen):
    return IM.foto(pen)


def _riga_percepita(par, parole_riga, righe_scritte, don, rng_h, nome_pagina):
    """La riga appena scritta come la rileggera' la rete (parole = tuple di glifi), o None."""
    if not parole_riga:
        return None
    if par == 'rs_m':
        if len(set(parole_riga)) < 2:
            return None
        v = list(parole_riga)
        for _ in range(12):
            rng_h.shuffle(v)
            if tuple(v) != tuple(parole_riga):
                return v
        return None
    if par == 'rs_p':
        lont = [q for q in range(len(righe_scritte)) if len(righe_scritte) - q >= 3 and righe_scritte[q]]
        return list(righe_scritte[rng_h.choice(lont)]) if lont else None
    if par == 'rs_a':
        return list(don.riga_altrove(nome_pagina, len(parole_riga), rng_h))
    raise ValueError(par)


# ---------------------------------------------------------------- misure leggere sul libro scritto

def riga_a_fascia(lu, voc):
    return int(sum(lu >= b for b in voc['bordi']))


def misure_leggere(rows, righe_layout, voc, D, t_scritto):
    """`rows`: pagina -> [(ini, [parola come tupla di glifi])] del libro scritto. `righe_layout`: le righe del libro vero (per la fascia di lunghezza).
    `t_scritto`: lista (pagina, ini, parole stringhe). -> dizionario di numeri."""
    import rifarlo_ritocchi as R
    import aprire_parole as AP
    out = OrderedDict()
    out['contatto'] = float(R.mi_contatto(rows))
    f = AP.firma_bordi(rows)
    out['bordi'] = OrderedDict((k, (None if v is None else float(v))) for k, v in f.items())
    c = Counter()
    for modo in ('vicini', 'lontani'):
        rng = random.Random(1)
        for p, rr in rows.items():
            for (r, i, cat, det) in F0.varianti_pagina(rr, modo=modo, rng=rng):
                c[(modo, cat)] += 1
    out['eco_conti'] = OrderedDict(('%s_%s' % k, v) for k, v in sorted(c.items()))
    n_v = sum(v for (m_, ca), v in c.items() if m_ == 'vicini')
    n_l = sum(v for (m_, ca), v in c.items() if m_ == 'lontani')
    out['tasso_eco_vicini'] = (c[('vicini', 'copia')] + c[('vicini', 'variante')]) / max(n_v, 1)
    out['tasso_eco_lontani'] = (c[('lontani', 'copia')] + c[('lontani', 'variante')]) / max(n_l, 1)
    # distanza della parola d'origine: riga in corso / riga sopra
    cur = sopra = 0
    for p, rr in rows.items():
        righe = [list(ws) for _, ws in rr]
        for r, ws in enumerate(righe):
            sp = righe[r - 1][::-1] if r > 0 else []
            for i, w in enumerate(ws):
                cu = ws[:i][::-1]
                cand = (cu + sp)[:F0.S_CAND]
                for rango, cnd in enumerate(cand):
                    if cnd == w or F0.una_modifica(cnd, w) is not None:
                        if rango < len(cu[:F0.S_CAND]):
                            cur += 1
                        else:
                            sopra += 1
                        break
    tot = sum(len(ws) for rr in rows.values() for _, ws in rr)
    out['eco_riga'] = cur / max(tot, 1)
    out['eco_sopra'] = sopra / max(tot, 1)
    # aderenza della lunghezza di riga alla fascia della testa
    ok = n = 0
    lungh = []
    k = 0
    for (pag, ini, ps) in t_scritto:
        if k >= len(righe_layout):
            break
        lu = sum(len(D(w)) for w in ps) + len(ps) - 1
        lungh.append(lu)
        ok += riga_a_fascia(lu, voc) == _fascia_layout(righe_layout[k], voc, D)
        n += 1
        k += 1
    out['aderenza_N'] = ok / max(n, 1)
    out['lunghezza_media_riga'] = float(np.mean(lungh)) if lungh else None
    return out


def _fascia_layout(x, voc, D):
    import ia07_voynich_neurale as I7
    return riga_a_fascia(I7.lunghezza(x, D), voc)
