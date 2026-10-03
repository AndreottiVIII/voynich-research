# -*- coding: utf-8 -*-
"""Esperimento 251b (passo 2 del piano 18/18, secondo tentativo): l'e241 con riuso di pagina senza tema concentrato
(theta, K) e senza reimmissione (mazzo). Copia di e233.genera: genera_ab, identica all'e241 con theta 0,3, K 3, senza mazzo.
Scelta sul seme 1 con la regola dell'e251; verifica sui semi 7, 8, 9 contro l'e241.

Preregistrazione: preregistrazioni/e251b.md. Scrive risultati/e251b_riuso_mazzo.json e .md.
"""
import json, math, os, random, statistics, sys
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
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME_SCELTA, SEMI_VERIFICA = 1, (7, 8, 9)
CONFIGURAZIONI = OrderedDict([('e241', (0.3, 3, False)), ('θ 0,3 K 12', (0.3, 12, False)), ('θ 0,15 K 3', (0.15, 3, False)), ('θ 0', (0.0, 0, False)),
                              ('mazzo, θ 0,3 K 3', (0.3, 3, True)), ('mazzo, θ 0,15 K 3', (0.15, 3, True)), ('mazzo, θ 0', (0.0, 0, True)),
                              ('mazzo, θ 0,3 K 12', (0.3, 12, True))])
RIPIEGO = 'mazzo, θ 0,15 K 3'


def genera_ab(c, prm, seme):
    """Come e232.genera ('gamma', 'fisica', 'delta'), con in piu' 'kappa' (modifiche medie MU * (2 r)^kappa, r = rango
    percentile della parola di base) e 'chi' (con questa probabilita' la seconda candidata e' una variante della parola
    precedente della riga)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    theta, k_tema, mazzo = prm.get('theta', 0.3), prm.get('k_tema', e153.K), prm.get('mazzo', False)
    frequenti = {w for w, _ in Counter(c['voy']).most_common(200)} if mazzo else set()
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
        gt, gp = e232.globali(c, lingua, prm['alfa'])

        mazzo_pag = list(pool) if mazzo else None

        def estrai():
            if gamma and lex and rnd.random() < gamma:
                return rnd.choice(lex)
            if delta and rnd.random() < delta:
                return rnd.choices(gt, gp)[0]
            if mazzo:
                if not mazzo_pag:
                    mazzo_pag.extend(pool)
                i = rnd.randrange(len(mazzo_pag))
                w = mazzo_pag[i]
                if w not in frequenti:
                    mazzo_pag[i] = mazzo_pag[-1]
                    mazzo_pag.pop()
                return w
            return rnd.choices(tipi, pesi_pool)[0]

        tema = [estrai() for _ in range(k_tema)] if k_tema else []
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
                        base = rnd.choice(tema) if rnd.random() < theta and tema else estrai()
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


def prm_di(nome):
    theta, k, mazzo = CONFIGURAZIONI[nome]
    return dict(e251.CONF, gamma=0.0, theta=theta, k_tema=k, mazzo=mazzo)


def lavoro(args):
    tipo, nome, seme = args
    k = e251._prepara()
    c = k['c']
    rr = e236.dopo(genera_ab(k['c2'], prm_di(nome), seme), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(c, rr)
    out = OrderedDict([('configurazione', nome), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('R_parole_rare', e251.R_completo(rr, controllo=False)['R'])])
    if tipo == 'verifica':
        gp = e232.pagine_di(rr)
        d231 = e231.confronto(k['vpag'], gp, k['rif'])
        out.update([('AUC_e231', d231['AUC']), ('AUC_e231_gruppi', d231['AUC_per_gruppo']), ('piu_pesanti_e231', d231['piu_pesanti']),
                    ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC']),
                    ('descrittive', e234.descrittive(gp)), ('profilo', e237.profilo(gp)), ('valori', pg['valori'])])
    return args, out


def tutti(lavori):
    n = int(os.environ.get('PROCESSI', '1'))
    if n <= 1:
        return dict(lavoro(a) for a in lavori)
    with Pool(n) as pool:
        return dict(pool.imap_unordered(lavoro, lavori))


def main():
    k = e251._prepara()
    identico = genera_ab(k['c2'], prm_di('e241'), SEME_SCELTA) == e233.genera(k['c2'], dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), SEME_SCELTA)
    print("valori di controllo identici all'e241: %s" % identico, flush=True)
    sc = tutti([('scelta', n, SEME_SCELTA) for n in CONFIGURAZIONI])
    for n in CONFIGURAZIONI:
        x = sc[('scelta', n, SEME_SCELTA)]
        print('seme 1, %-18s: pagella %d riga %s | R rare %.1f' % (n, x['pagella'], x['riga'], x['R_parole_rare'] or float('nan')), flush=True)
    b1 = sc[('scelta', 'e241', SEME_SCELTA)]
    P = max(x['pagella'] for x in sc.values())
    ammesse = [n for n in CONFIGURAZIONI if n != 'e241' and sc[('scelta', n, SEME_SCELTA)]['pagella'] >= P - 1
               and (sc[('scelta', n, SEME_SCELTA)]['riga'] or not b1['riga']) and (sc[('scelta', n, SEME_SCELTA)]['R_parole_rare'] or 0) > 0]
    ordine = list(CONFIGURAZIONI)
    scelta = min(ammesse, key=lambda n: (abs(math.log(sc[('scelta', n, SEME_SCELTA)]['R_parole_rare'] / 1.96)), ordine.index(n))) if ammesse else RIPIEGO
    print('P* %d, ammesse %s -> scelta %s' % (P, ammesse, scelta), flush=True)
    vv = tutti([('verifica', n, s) for s in SEMI_VERIFICA for n in ('e241', scelta)])
    br = {n: [vv[('verifica', n, s)] for s in SEMI_VERIFICA] for n in ('e241', scelta)}
    for s in SEMI_VERIFICA:
        for n in ('e241', scelta):
            x = vv[('verifica', n, s)]
            print('seme %d %-18s: pagella %d riga %s mancano %s | R rare %.1f | AUC e231 %.3f (G3 %.3f) e266 %.3f' % (
                s, n, x['pagella'], x['riga'], x['mancano'], x['R_parole_rare'] or float('nan'), x['AUC_e231'], x['AUC_e231_gruppi']['G3'], x['AUC_e266']), flush=True)
    m = lambda xs, f: statistics.mean(f(x) for x in xs)
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('R_parole_rare_media', m(xs, lambda x: x['R_parole_rare'] or float('nan'))), ('AUC_e231_media', m(xs, lambda x: x['AUC_e231'])),
                             ('AUC_G3_media', m(xs, lambda x: x['AUC_e231_gruppi']['G3'])), ('AUC_e266_media', m(xs, lambda x: x['AUC_e266'])),
                             ('tipi_su_parole_pagina', m(xs, lambda x: x['descrittive']['tipi_su_parole_pagina'])),
                             ('uniche_nella_pagina', m(xs, lambda x: x['descrittive'].get('uniche_nella_pagina', float('nan'))))]) for n, xs in br.items()}
    mb, ms = medie['e241'], medie[scelta]
    motivi = []
    if not ms['R_parole_rare_media'] <= 5:
        motivi.append('R')
    if ms['pagella_somma'] < mb['pagella_somma']:
        motivi.append('pagella')
    if ms['semi_con_riga'] < mb['semi_con_riga']:
        motivi.append('riga')
    esito = 'non valido' if not identico else ('passo superato' if not motivi else 'non superato: ' + ' + '.join(motivi))
    utile = ms['AUC_e266_media'] <= mb['AUC_e266_media'] - 0.03 and ms['pagella_somma'] >= mb['pagella_somma']
    prosegue = scelta if (esito == 'passo superato' or (ms['pagella_somma'] >= mb['pagella_somma'] and ms['AUC_e266_media'] < mb['AUC_e266_media'])) else 'e241'
    out = OrderedDict([('validita_identico_e241', identico), ('scelta_seme_1', [sc[('scelta', n, SEME_SCELTA)] for n in CONFIGURAZIONI]), ('P_star', P),
                       ('ammesse', ammesse), ('scelta', scelta), ('parametri_scelti', prm_di(scelta)), ('verifica', br), ('medie', medie), ('esito', esito),
                       ('motivo', motivi), ('utile_per_il_generatore', utile), ('generatore_che_prosegue', prosegue)])
    json.dump(out, open(os.path.join(RISULTATI, 'e251b_riuso_mazzo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e251b — Passo 2, secondo tentativo: riuso di pagina senza tema concentrato e senza reimmissione', '',
          "Copia di e233.genera con θ (quota del tema), K (parole del tema) e mazzo (estrazione senza reimmissione dalla pagina, frequenti escluse). "
          'Validità (valori di controllo = e241): %s. Preregistrazione: `preregistrazioni/e251b.md`.' % ('sì' if identico else 'NO'), '',
          '| configurazione (seme 1) | pagella | riga | R parole rare |', '|---|---|---|---|']
    for x in out['scelta_seme_1']:
        md.append('| %s | %d | %s | %.1f |' % (x['configurazione'], x['pagella'], 'sì' if x['riga'] else 'no', x['R_parole_rare'] or float('nan')))
    md += ['', 'P* %d; ammesse: %s; scelta: **%s**.' % (P, ', '.join(ammesse) or 'nessuna', scelta), '',
           '| seme | configurazione | pagella | riga | mancano | R rare | AUC e231 | G3 | AUC e266 | tipi/parole pagina |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('e241', scelta):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.1f | %.3f | %.3f | %.3f | %.3f |' % (s, n, x['pagella'], 'sì' if x['riga'] else 'no', ', '.join(x['mancano']) or '—',
                                                                                x['R_parole_rare'] or float('nan'), x['AUC_e231'], x['AUC_e231_gruppi']['G3'], x['AUC_e266'],
                                                                                x['descrittive']['tipi_su_parole_pagina']))
    md += ['', 'Medie: ' + '; '.join('%s: pagella %d (somma), riga in %d semi, R rare %.1f, AUC e231 %.3f (G3 %.3f), e266 %.3f, tipi/parole %.3f' % (
        n, v['pagella_somma'], v['semi_con_riga'], v['R_parole_rare_media'], v['AUC_e231_media'], v['AUC_G3_media'], v['AUC_e266_media'], v['tipi_su_parole_pagina'])
        for n, v in medie.items()) + '. Voynich: tipi su parole nella pagina 0,756.', '',
           'Esito: **%s**. Utile per il generatore (AUC e266 almeno 0,03 sotto a pagella non inferiore): **%s**. Prosegue: **%s**.' % (esito, 'sì' if utile else 'no', prosegue)]
    open(os.path.join(RISULTATI, 'e251b_riuso_mazzo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
