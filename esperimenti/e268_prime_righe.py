# -*- coding: utf-8 -*-
"""Esperimento 268 (passo 3b del piano 18/18): il registro delle prime righe. Nelle righe di inizio paragrafo, con
probabilita' rho, la base di una candidata viene dalle prime righe vere delle altre pagine della stessa sezione (copia di
e233.genera: genera_pr). Base e241 (gamma 0). Scelta di rho sul seme 1 con l'AUC del gruppo G8 dell'e266; verifica sui
semi 7, 8, 9; misura dell'e273 sull'uscita del seme 7.

Preregistrazione: preregistrazioni/e268.md. Scrive risultati/e268_prime_righe.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
RHO, SEME_SCELTA, SEMI_VERIFICA = (0.2, 0.4, 0.6, 0.8), 1, (7, 8, 9)
SEME_E273, ALTRI, RICAMPIONI = 273, 5, 1000
D = e237.D
_PRIME = {}


def prime_per_pagina(c):
    """Per ogni pagina: le parole pulite (esclusa la prima) delle prime righe vere delle ALTRE pagine della stessa sezione."""
    if not _PRIME:
        sez = e230.sezioni()
        per_sez = defaultdict(list)
        for p, d in c['P'].items():
            for ini, ps in d['righe']:
                if ini:
                    per_sez[sez.get(p)].extend((p, w) for w in ps[1:] if trascrizione.pulita(w))
        for p in c['P']:
            _PRIME[p] = [w for q, w in per_sez[sez.get(p)] if q != p]
    return _PRIME


def misura_e273(rr):
    """La misura dell'e273 (D1 - D2 e z con 1.000 ricampionamenti) su un testo generato (pagina, inizio, parole)."""
    sez = e230.sezioni()
    P, cur, pag = [], None, None
    for p, ini, ps in rr:
        u = [tuple(D(w)) for w in ps if trascrizione.pulita(w)]
        if not u:
            continue
        if ini or cur is None or p != pag:
            if cur and len(cur['righe']) >= 3:
                P.append(cur)
            cur, pag = {'pagina': p, 'sezione': sez.get(p), 'righe': []}, p
        cur['righe'].append(u)
    if cur and len(cur['righe']) >= 3:
        P.append(cur)
    rnd = random.Random(SEME_E273)
    inventario = sorted({x for p in P for r in p['righe'] for u in r for x in u})
    vic = {}

    def V(u):
        if u not in vic:
            vic[u] = e237.vicini(u, inventario) | {u}
        return vic[u]

    def S(A, B):
        return sum(1 for u in A if V(u) & B) / len(A) if A else 0.0
    per_sez = defaultdict(list)
    for i, p in enumerate(P):
        per_sez[p['sezione']].append(i)
    diffs = []
    for i, p in enumerate(P):
        altri = [j for j in per_sez[p['sezione']] if P[j]['pagina'] != p['pagina']]
        if len(altri) < ALTRI:
            continue
        prime_altre = {u for j in rnd.sample(altri, ALTRI) for u in P[j]['righe'][0]}
        r1, r2 = p['righe'][0], p['righe'][1]
        resto1 = {u for r in p['righe'][1:] for u in r}
        resto2 = {u for k, r in enumerate(p['righe']) if k != 1 for u in r}
        diffs.append(S(r1, prime_altre) - S(r1, resto1) - (S(r2, prime_altre) - S(r2, resto2)))
    media = statistics.mean(diffs)
    se = statistics.pstdev([statistics.mean(rnd.choice(diffs) for _ in diffs) for _ in range(RICAMPIONI)])
    return OrderedDict([('paragrafi', len(diffs)), ('D1_meno_D2', media), ('z', media / se if se else None)])


def genera_pr(c, prm, seme, rho=0.0, prime_per_pag=None):
    """Come e232.genera ('gamma', 'fisica', 'delta'), con in piu' 'kappa' (modifiche medie MU * (2 r)^kappa, r = rango
    percentile della parola di base) e 'chi' (con questa probabilita' la seconda candidata e' una variante della parola
    precedente della riga)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rango = e233.ranghi(c)
    fattore = (lambda w: (2 * rango.get(w, 1.0)) ** kappa) if kappa else (lambda w: 1.0)
    sez = e230.sezioni()
    lessico = defaultdict(list)
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    h = {f: 0.0 for f in e145.SCELTE}
    righe, storia = [], []
    for pag, d in c['P'].items():
        s_pag = sez.get(pag)
        nuove_pag = []
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        cnt = Counter(pool)
        tipi = list(cnt)
        pesi_pool = [cnt[t] ** prm['alfa'] for t in tipi]
        lex = lessico[s_pag]
        pr_pag = prime_per_pag.get(pag, []) if rho else []
        gt, gp = e232.globali(c, lingua, prm['alfa'])

        def estrai():
            if gamma and lex and rnd.random() < gamma:
                return rnd.choice(lex)
            if delta and rnd.random() < delta:
                return rnd.choices(gt, gp)[0]
            return rnd.choices(tipi, pesi_pool)[0]

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
                if prm['psi'] and storia and 1 <= pos <= n - 3 and rnd.random() < prm['psi']:
                    src = rnd.choice(storia)
                    if len(src) >= 4:
                        a = rnd.randrange(1, len(src) - 2)
                        m = min(rnd.choice((2, 3)), n - pos, len(src) - a)
                        riga += [e224.variante(x, e153.MU / 2, mod, rnd, prm['nu'], att, Dv) for x in src[a:a + m]]
                        continue
                cand = []
                for j in range(k):
                    if fisica:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi']
                    else:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra)
                    if copia and fisica:
                        x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                        centri, acc = [], 0
                        for w in sopra:
                            centri.append(acc + len(Dv(w)) / 2)
                            acc += len(Dv(w)) + 1
                        base = sopra[min(range(len(sopra)), key=lambda t: abs(centri[t] - x0))]
                    elif copia:
                        base = sopra[pos]
                    elif chi and j == 1 and rnd.random() < chi:
                        base = riga[-1]
                    else:
                        if rho and ini and pr_pag and rnd.random() < rho:
                            base = rnd.choice(pr_pag)
                        else:
                            base = rnd.choice(tema) if rnd.random() < 0.3 else estrai()
                    cand.append(e224.variante(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv))
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
                    s = e224.spezza(x, att, Dv, rnd)
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
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe


def lavoro(args):
    tipo, rho, seme = args
    k = e251._prepara()
    c = k['c']
    rr = e236.dopo(genera_pr(k['c2'], dict(e251.CONF, gamma=0.0), seme, rho, prime_per_pagina(c)), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(c, rr)
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    out = OrderedDict([('rho', rho), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('AUC_e266', d266['AUC']), ('AUC_G8', d266['AUC_per_gruppo']['G8'])])
    if tipo == 'verifica':
        out['AUC_e231'] = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']
        out['AUC_per_gruppo_e266'] = d266['AUC_per_gruppo']
        if seme == SEMI_VERIFICA[0]:
            out['e273'] = misura_e273(rr)
    return args, out


def tutti(lavori):
    n = int(os.environ.get('PROCESSI', '1'))
    if n <= 1:
        return dict(lavoro(a) for a in lavori)
    with Pool(n) as pool:
        return dict(pool.imap_unordered(lavoro, lavori))


def main():
    k = e251._prepara()
    identico = genera_pr(k['c2'], dict(e251.CONF, gamma=0.0), SEME_SCELTA, 0.0, prime_per_pagina(k['c'])) == e233.genera(
        k['c2'], dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), SEME_SCELTA)
    print("rho 0 identico all'e241: %s" % identico, flush=True)
    sc = tutti([('scelta', r, SEME_SCELTA) for r in (0.0,) + RHO])
    b1 = sc[('scelta', 0.0, SEME_SCELTA)]
    for r in (0.0,) + RHO:
        x = sc[('scelta', r, SEME_SCELTA)]
        print('seme 1, rho %.1f: pagella %d riga %s | AUC e266 %.3f G8 %.3f' % (r, x['pagella'], x['riga'], x['AUC_e266'], x['AUC_G8']), flush=True)
    ammessi = [r for r in RHO if sc[('scelta', r, SEME_SCELTA)]['pagella'] >= b1['pagella'] - 1 and (sc[('scelta', r, SEME_SCELTA)]['riga'] or not b1['riga'])]
    rs = min(ammessi, key=lambda r: (sc[('scelta', r, SEME_SCELTA)]['AUC_G8'], r)) if ammessi else RHO[0]
    print('ammessi %s -> rho* %.1f' % (ammessi, rs), flush=True)
    vv = tutti([('verifica', r, s) for s in SEMI_VERIFICA for r in (0.0, rs)])
    for s in SEMI_VERIFICA:
        for r in (0.0, rs):
            x = vv[('verifica', r, s)]
            print('seme %d rho %.1f: pagella %d riga %s mancano %s | AUC e231 %.3f e266 %.3f G8 %.3f' % (
                s, r, x['pagella'], x['riga'], x['mancano'], x['AUC_e231'], x['AUC_e266'], x['AUC_G8']), flush=True)
    br = {'base': [vv[('verifica', 0.0, s)] for s in SEMI_VERIFICA], 'rho': [vv[('verifica', rs, s)] for s in SEMI_VERIFICA]}
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in xs)), ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in xs)),
                             ('AUC_G8_media', statistics.mean(x['AUC_G8'] for x in xs))]) for n, xs in br.items()}
    z273 = br['rho'][0]['e273']['z']
    motivi = []
    if not (z273 or 0) > 3:
        motivi.append('e273')
    if medie['rho']['AUC_G8_media'] > medie['base']['AUC_G8_media'] - 0.05:
        motivi.append('G8')
    if medie['rho']['pagella_somma'] < medie['base']['pagella_somma'] or medie['rho']['semi_con_riga'] < medie['base']['semi_con_riga']:
        motivi.append('pagella o riga')
    esito = 'non valido' if not identico else ('passo superato' if not motivi else 'non superato: ' + ' + '.join(motivi))
    out = OrderedDict([('validita_identico_e241', identico), ('scelta_seme_1', [sc[('scelta', r, SEME_SCELTA)] for r in (0.0,) + RHO]), ('ammessi', ammessi),
                       ('rho', rs), ('verifica', br), ('medie', medie), ('e273_base', br['base'][0]['e273']), ('e273_rho', br['rho'][0]['e273']),
                       ('esito', esito), ('motivo', motivi)])
    json.dump(out, open(os.path.join(RISULTATI, 'e268_prime_righe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    mb, mr = medie['base'], medie['rho']
    md = ['# e268 — Passo 3b del piano 18/18: il registro delle prime righe', '',
          "Base e241 (γ 0). Nelle prime righe dei paragrafi, con probabilità ρ, la base viene dalle prime righe vere delle altre pagine della stessa sezione. "
          'ρ scelto sul seme 1 (AUC del gruppo G8 dell\'e266): **%.1f**. Validità (ρ 0 = e241): %s. Preregistrazione: `preregistrazioni/e268.md`.' % (rs, 'sì' if identico else 'NO'), '',
          '| ρ (seme 1) | pagella | riga | AUC e266 | G8 |', '|---|---|---|---|---|']
    for x in out['scelta_seme_1']:
        md.append('| %.1f | %d | %s | %.3f | %.3f |' % (x['rho'], x['pagella'], 'sì' if x['riga'] else 'no', x['AUC_e266'], x['AUC_G8']))
    md += ['', '| seme | braccio | pagella | riga | mancano | AUC e231 | AUC e266 | G8 |', '|---|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('base', 'rho'):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f | %.3f |' % (s, 'e241' if n == 'base' else 'ρ %.1f' % rs, x['pagella'], 'sì' if x['riga'] else 'no',
                                                                       ', '.join(x['mancano']) or '—', x['AUC_e231'], x['AUC_e266'], x['AUC_G8']))
    md += ['', "Misura dell'e273 sul seme 7 (Voynich: +0,047, z 4,7): e241 %+.3f (z %.1f); ρ %+.3f (z %.1f)." % (
        out['e273_base']['D1_meno_D2'], out['e273_base']['z'] or 0, out['e273_rho']['D1_meno_D2'], z273 or 0), '',
           'Medie: e241 pagella %d (somma), riga in %d semi, AUC %.3f / %.3f, G8 %.3f; ρ pagella %d, riga in %d semi, AUC %.3f / %.3f, G8 %.3f.' % (
               mb['pagella_somma'], mb['semi_con_riga'], mb['AUC_e231_media'], mb['AUC_e266_media'], mb['AUC_G8_media'],
               mr['pagella_somma'], mr['semi_con_riga'], mr['AUC_e231_media'], mr['AUC_e266_media'], mr['AUC_G8_media']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e268_prime_righe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
