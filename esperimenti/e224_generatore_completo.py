# -*- coding: utf-8 -*-
"""Esperimento 224: generatore senza messaggio con regola di fine riga, giunture piu' forti, parole spezzate, copia
verticale, formule da lontano, concentrazione delle frequenze e varianti nuove; salita per coordinate sulla pagella
(seme 1), verifica su semi nuovi.

Preregistrazione: preregistrazioni/e224.md. Scrive risultati/e224_generatore_completo.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e131_procedimento_riga as e131
import e135_stato_riga as e135
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e211_parole_proprie as e211
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
BASE = OrderedDict([('eta', 0.0), ('sigma', 0.0), ('lam_k', (1.0, 8)), ('phi', 0.0), ('psi', 0.0), ('alfa', 1.0), ('nu', 0.4)])
GRIGLIA = OrderedDict([('eta', [0.0, 1.0, 2.0]), ('sigma', [0.0, 0.03, 0.06]), ('lam_k', [(1.0, 8), (1.5, 16), (2.0, 16)]),
                       ('phi', [0.0, 0.1, 0.2]), ('psi', [0.0, 0.03, 0.06]), ('alfa', [1.0, 1.3]), ('nu', [0.4, 0.5, 0.6])])
PASSATE, SEME_RICERCA, SEMI_VERIFICA = 2, 1, (2, 3, 4)
_CTX = {}


def contesto():
    if _CTX:
        return _CTX
    import misure
    Dv = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), Dv, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    # rapporto di fine riga per l'ultimo segno
    fine, dentro = Counter(), Counter()
    for _, ps in e71.righe_voynich():
        pp = [w for w in ps if trascrizione.pulita(w)]
        if len(pp) >= 3:
            fine[Dv(pp[-1])[-1]] += 1
            for w in pp[1:-1]:
                dentro[Dv(w)[-1]] += 1
        nf, nd = sum(fine.values()), sum(dentro.values())
    rapporto = {g: ((fine[g] + 1) / (nf + len(fine))) / ((dentro.get(g, 0) + 1) / (nd + len(fine))) for g in set(fine) | set(dentro)}
    att = set(voy)
    _CTX.update(dict(D=Dv, voy=voy, soglia_ab=soglia_ab, v=v, vb=vb, rapporto=rapporto, att=att, mod=generatori.Modifiche(voy, Dv),
                     P=e145.pagine(), starts=e131.inizi(), q=e145.quote(), L=e152.lift()))
    return _CTX


def variante(w, mu, mod, rnd, nu, att, Dv):
    u = tuple(Dv(w))
    for _ in range(generatori.poisson(rnd, mu)):
        x = mod.modifica(u, rnd)
        if ''.join(x) in att or (mod.valida(x) and rnd.random() < nu):
            u = x
    return ''.join(u)


def spezza(w, att, Dv, rnd):
    u = Dv(w)
    tagli = [i for i in range(1, len(u)) if ''.join(u[:i]) in att and ''.join(u[i:]) in att]
    if not tagli:
        return None
    i = rnd.choice(tagli)
    return [''.join(u[:i]), ''.join(u[i:])]


def genera(c, prm, seme):
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    h = {f: 0.0 for f in e145.SCELTE}
    righe, storia = [], []
    for pag, d in c['P'].items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        cnt = Counter(pool)
        tipi = list(cnt)
        pesi_pool = [cnt[t] ** prm['alfa'] for t in tipi]
        estrai = lambda: rnd.choices(tipi, pesi_pool)[0]
        tema = [estrai() for _ in range(e153.K)]
        prima_sopra, sopra = None, None
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            n = len(ps)
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or Dv(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            while len(riga) < n:
                pos = len(riga)
                # formule: copia di 2-3 parole da una riga gia' generata
                if prm['psi'] and storia and 1 <= pos <= n - 3 and rnd.random() < prm['psi']:
                    src = rnd.choice(storia)
                    if len(src) >= 4:
                        a = rnd.randrange(1, len(src) - 2)
                        m = min(rnd.choice((2, 3)), n - pos, len(src) - a)
                        riga += [variante(x, e153.MU / 2, mod, rnd, prm['nu'], att, Dv) for x in src[a:a + m]]
                        continue
                cand = []
                for j in range(k):
                    if prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra):
                        base = sopra[pos]
                    else:
                        base = rnd.choice(tema) if rnd.random() < 0.3 else estrai()
                    cand.append(variante(base, e153.MU, mod, rnd, prm['nu'], att, Dv))
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    pesi.append(p)
                x = rnd.choices(cand, pesi)[0]
                if prm['sigma'] and pos < n - 1 and len(Dv(x)) >= 4 and rnd.random() < prm['sigma']:
                    s = spezza(x, att, Dv, rnd)
                    if s:
                        riga += s
                        continue
                riga.append(x)
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
    return righe


def misura(args):
    prm, seme, completa = args
    c = contesto()
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    rr = genera(c, prm, seme)
    righe = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(righe, c['voy'], c['soglia_ab'], c['v'], c['vb'])
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in e145.SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, kk = [], 0
    for pag, ini, ps in rr:
        kk += ini
        par.append((pag, kk, ps))
    r['r_righe_consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    if completa:
        per = OrderedDict()
        for pag, ini, ps in rr:
            per.setdefault(pag, []).append((ini, ps))
        _, t = e160.una(('x', list(per.values())))
        for kx, x in t.items():
            r['T ' + kx] = x['z']
        herb = defaultdict(list)
        sez = {x.pagina: x.sezione for x in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
        for pag, _, ps in rr:
            herb[pag] += [w for w in ps if trascrizione.pulita(w)]
        unita_h = [v for p, v in herb.items() if len(v) >= 60 and sez.get(p) == 'H']
        r['R_parole_proprie'] = e211.prova(unita_h, random.Random(seme))['R'] if unita_h else None
    return json.dumps(prm, default=list), seme, r


def valuta(r, c):
    esiti = OrderedDict()
    for prop, f in e61.BANDE.items():
        try:
            esiti[prop] = bool(f(r, c['v']))
        except (KeyError, TypeError, ZeroDivisionError):
            esiti[prop] = False
    vb = c['vb']
    esiti['bordo di riga'] = 0.5 * vb[0] <= r['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= r['bordo_fine'] <= 2 * vb[1]
    R = r['R_riga'] if r.get('R_riga') is not None else 1
    riga = r['S1'] <= 0.7 and R < 0.1 and r['A'] >= 1.0 and r['scelte_per_riga'] >= 3 and abs(r['r_righe_consecutive'] - e145.VOY_R1) <= 0.07
    return esiti, riga


def punteggio(r, c):
    esiti, riga = valuta(r, c)
    return (sum(esiti.values()) if riga else -1), esiti, riga


def main():
    c = contesto()
    corrente = dict(BASE)
    storia = []
    with Pool(int(os.environ.get('PROCESSI', '2'))) as pool:
        _, _, r0 = misura((corrente, SEME_RICERCA, False))
        s0, es0, rg0 = punteggio(r0, c)
        storia.append((dict(corrente), s0))
        print('partenza %s -> %d/18 (riga %s) mancano %s' % (corrente, s0, rg0, [k for k, x in es0.items() if not x]), flush=True)
        for passata in range(PASSATE):
            for par, valori in GRIGLIA.items():
                prove = [dict(corrente, **{par: x}) for x in valori if x != corrente[par]]
                risultati = list(pool.imap(misura, [(p, SEME_RICERCA, False) for p in prove]))
                for p, (_, _, r) in zip(prove, risultati):
                    s, es, rg = punteggio(r, c)
                    storia.append((dict(p), s))
                    print('  %s=%s -> %d/18 (riga %s) mancano %s' % (par, p[par], s, rg, [k for k, x in es.items() if not x]), flush=True)
                    if s > s0:
                        corrente, s0 = p, s
                print('passata %d, %s: tengo %s (%d/18)' % (passata + 1, par, corrente[par], s0), flush=True)
        finali = list(pool.imap(misura, [(corrente, s, True) for s in SEMI_VERIFICA]))
    rr = [r for _, _, r in finali]
    chiavi = [kx for kx, x in rr[0].items() if isinstance(x, (int, float)) and all(isinstance(y.get(kx), (int, float)) for y in rr)]
    mm = {kx: sum(y[kx] for y in rr) / len(rr) for kx in chiavi}
    esiti, riga = valuta(mm, c)
    completo = riga and all(esiti.values())
    ris = OrderedDict([('configurazione', {kx: (list(v) if isinstance(v, tuple) else v) for kx, v in corrente.items()}), ('punteggio_ricerca', s0),
                       ('verifica_pagella', sum(esiti.values())), ('verifica_esiti', esiti), ('riga_riprodotta', riga), ('completo', completo),
                       ('medie_verifica', mm), ('ricerca', [(dict((kx, list(v) if isinstance(v, tuple) else v) for kx, v in p.items()), s) for p, s in storia])])
    json.dump(ris, open(os.path.join(RISULTATI, 'e224_generatore_completo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    print('finale %s | verifica %d/18 riga %s completo %s | mancano %s | R parole proprie %s | T %s' % (
        corrente, sum(esiti.values()), riga, completo, [kx for kx, x in esiti.items() if not x], mm.get('R_parole_proprie'),
        {kx: round(v, 1) for kx, v in mm.items() if kx.startswith('T ')}), flush=True)
    md = ['# e224 — Verso un generatore senza messaggio 18/18', '', 'Preregistrazione: `preregistrazioni/e224.md`.', '',
          'Configurazione finale: %s.' % ', '.join('%s %s' % kv for kv in corrente.items()), '',
          'Ricerca (seme 1): %d/18. Verifica (semi 2–4, medie): **%d/18**, riga riprodotta: %s, completo: **%s**.' % (s0, sum(esiti.values()), 'sì' if riga else 'no', 'sì' if completo else 'no'), '',
          'Proprietà mancanti in verifica: %s.' % (', '.join(kx for kx, x in esiti.items() if not x) or 'nessuna'), '',
          'Fuori pagella: raggruppamento delle parole rare per pagina R = %s (Voynich 1,96); T3/T4 %s.' % (
              '%.2f' % mm['R_parole_proprie'] if mm.get('R_parole_proprie') is not None else '–', {kx: round(v, 1) for kx, v in mm.items() if kx.startswith('T ')})]
    open(os.path.join(RISULTATI, 'e224_generatore_completo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
