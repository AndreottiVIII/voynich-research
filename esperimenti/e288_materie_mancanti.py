# -*- coding: utf-8 -*-
"""Esperimento 288: le materie che il generatore manca (ripetizione, verticale, spazio). Copia di e233.genera con la
penalita' rip per le candidate uguali alla parola precedente (genera_m); in piu' phi con copia per indice dalla riga sopra
e sigma di dopo. Griglia di 27 configurazioni sul seme 1, verifica sui semi 7-9. Stampa ogni risultato appena arriva.

Preregistrazione: preregistrazioni/e288.md. Scrive risultati/e288_materie_mancanti.json e .md.
"""
import itertools, json, os, random, statistics, sys
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
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRIGLIA = [OrderedDict([('rip', r), ('phi', f), ('sigma_post', s)]) for r, f, s in itertools.product((1.0, 0.5, 0.3), (0.0, 0.05, 0.1), (0.09, 0.06, 0.04))]
SEME_SCELTA, SEMI_VERIFICA = 1, (7, 8, 9)
GREZZI = ('identiche_vs_riga', 'verticale', 'spazio_spiegato', 'V3_R', 'somiglianza_riga', 'somiglianza_6_righe', 'h2', 'hapax_34000')


def genera_m(c, prm, seme):
    """Come e232.genera ('gamma', 'fisica', 'delta'), con in piu' 'kappa' (modifiche medie MU * (2 r)^kappa, r = rango
    percentile della parola di base) e 'chi' (con questa probabilita' la seconda candidata e' una variante della parola
    precedente della riga)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rip = prm.get('rip', 1.0)
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
                    if rip != 1.0 and x == riga[-1]:
                        p *= rip
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


def nome(x):
    return 'rip %.1f, phi %.2f, sigma %.2f' % (x['rip'], x['phi'], x['sigma_post'])


def lavoro(args):
    tipo, i, seme = args
    x = GRIGLIA[i] if i >= 0 else OrderedDict([('rip', 1.0), ('phi', 0.0), ('sigma_post', 0.09)])
    k = e251._prepara()
    e233.SIGMA_POST = x['sigma_post']
    prm = dict(e251.CONF, gamma=0.0, rip=x['rip'], phi=x['phi'])
    rr = e236.dopo(genera_m(k['c2'], prm, seme), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(k['c'], rr)
    out = OrderedDict([('configurazione', nome(x)), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('grezzi', OrderedDict((g, pg['valori'].get(g)) for g in GREZZI)),
                       ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    if tipo == 'verifica':
        out['AUC_e231'] = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']
    return args, out


def tutti(lavori):
    ris = {}
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        for a, x in pool.imap_unordered(lavoro, lavori):
            ris[a] = x
            print('%s %-32s seme %d: pagella %d riga %s mancano %s | AUC e266 %.3f%s | ripet. %.2f vert. %.3f spazio %.3f' % (
                a[0], x['configurazione'], a[2], x['pagella'], x['riga'], x['mancano'], x['AUC_e266'],
                (' e231 %.3f' % x['AUC_e231']) if 'AUC_e231' in x else '', x['grezzi']['identiche_vs_riga'] or 0, x['grezzi']['verticale'] or 0,
                x['grezzi']['spazio_spiegato'] or 0), flush=True)
    return ris


def main():
    k = e251._prepara()
    identico = genera_m(k['c2'], dict(e251.CONF, gamma=0.0, rip=1.0, phi=0.0), SEME_SCELTA) == e233.genera(k['c2'], dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), SEME_SCELTA)
    print("rip 1, phi 0 identico all'e241: %s" % identico, flush=True)
    sc = tutti([('scelta', i, SEME_SCELTA) for i in range(len(GRIGLIA))])
    base1 = next(sc[('scelta', i, SEME_SCELTA)] for i, x in enumerate(GRIGLIA) if x['rip'] == 1.0 and x['phi'] == 0.0 and x['sigma_post'] == 0.09)
    cand = [i for i in range(len(GRIGLIA)) if sc[('scelta', i, SEME_SCELTA)]['riga'] or not base1['riga']] or list(range(len(GRIGLIA)))
    scelta = min(cand, key=lambda i: (-sc[('scelta', i, SEME_SCELTA)]['pagella'], sc[('scelta', i, SEME_SCELTA)]['AUC_e266'], i))
    print('scelta: %s' % nome(GRIGLIA[scelta]), flush=True)
    vv = tutti([('verifica', i, s) for s in SEMI_VERIFICA for i in (-1, scelta)])
    br = {'e241': [vv[('verifica', -1, s)] for s in SEMI_VERIFICA], 'scelta': [vv[('verifica', scelta, s)] for s in SEMI_VERIFICA]}
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in xs)), ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in xs)),
                             ('mancano', dict(Counter(m for x in xs for m in x['mancano'])))]) for n, xs in br.items()}
    mb, ms = medie['e241'], medie['scelta']
    migliore = ms['pagella_somma'] >= mb['pagella_somma'] + 3 and ms['semi_con_riga'] >= mb['semi_con_riga'] and ms['AUC_e266_media'] <= mb['AUC_e266_media'] + 0.01
    pieno = migliore and all(x['pagella'] == 18 and x['riga'] for x in br['scelta'])
    esito = 'non valido' if not identico else ('18/18' if pieno else ('migliore' if migliore else 'non migliore'))
    out = OrderedDict([('validita_identico_e241', identico), ('scelta_seme_1', [sc[('scelta', i, SEME_SCELTA)] for i in range(len(GRIGLIA))]),
                       ('scelta', nome(GRIGLIA[scelta])), ('parametri_scelti', GRIGLIA[scelta]), ('verifica', br), ('medie', medie), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e288_materie_mancanti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e288 — Le materie che il generatore manca: ripetizione, verticale, spazio', '',
          'Copia di e233.genera con penalità rip per le ripetizioni immediate, φ (copia per indice dalla riga sopra) e σ di `dopo`. Validità: %s. '
          'Preregistrazione: `preregistrazioni/e288.md`.' % ('sì' if identico else 'NO'), '',
          '| configurazione (seme 1) | pagella | riga | mancano | AUC e266 | ripetizione | verticale | spazio |', '|---|---|---|---|---|---|---|---|']
    for x in sorted(out['scelta_seme_1'], key=lambda x: (-x['pagella'], x['AUC_e266'])):
        g = x['grezzi']
        md.append('| %s | %d | %s | %s | %.3f | %.2f | %.3f | %.3f |' % (x['configurazione'], x['pagella'], 'sì' if x['riga'] else 'no', ', '.join(x['mancano']) or '—',
                                                                     x['AUC_e266'], g['identiche_vs_riga'] or 0, g['verticale'] or 0, g['spazio_spiegato'] or 0))
    md += ['', 'Voynich: ripetizione 1,01, verticale 1,028, spazio 0,664. Scelta: **%s**.' % nome(GRIGLIA[scelta]), '',
           '| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |', '|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('e241', 'scelta'):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f |' % (s, x['configurazione'], x['pagella'], 'sì' if x['riga'] else 'no', ', '.join(x['mancano']) or '—',
                                                                   x['AUC_e231'], x['AUC_e266']))
    md += ['', 'Medie: e241 pagella %d (somma), riga in %d semi, AUC %.3f / %.3f; scelta pagella %d, riga in %d semi, AUC %.3f / %.3f.' % (
        mb['pagella_somma'], mb['semi_con_riga'], mb['AUC_e231_media'], mb['AUC_e266_media'], ms['pagella_somma'], ms['semi_con_riga'], ms['AUC_e231_media'], ms['AUC_e266_media']),
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e288_materie_mancanti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
