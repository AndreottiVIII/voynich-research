# -*- coding: utf-8 -*-
"""Esperimento 252 (passo 3 del piano 18/18, integrazione del 3/10/2026): la base del passo 2 (e241 + gamma_per_e252 dal
json dell'e251) con i 12 interruttori di riga dell'e206b: stato AR(1) per classe (RHO/2 a inizio pagina, RHO a ogni
riga), applicato con e251.applica_interruttori subito dopo e145.riscrivi, in una copia di e233.genera (genera_ii). Verifica
sui semi 7, 8, 9 contro il braccio di base; l'e206b sull'uscita del seme 7.

Preregistrazione: preregistrazioni/e252.md (integrazione in fondo). Scrive risultati/e252_interruttori_riga.json e .md.
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
import e206_segni_facoltativi as e206
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
RIMESCOLAMENTI, SEME_TEST = 100, 2521
SEMI_VERIFICA, TOLL_AUC = (7, 8, 9), 0.001
BASE_JSON = os.path.join(RISULTATI, 'e251_lessico_sezione.json')


def test_classi(rr, classi):
    """Come l'e206b sul testo dato (righe (pagina, inizio, parole)), con RIMESCOLAMENTI rimescolamenti: z per classe."""
    rnd = random.Random(SEME_TEST)
    righe = [(p, ini, [w for w in ps if trascrizione.pulita(w)]) for p, ini, ps in rr]
    freq = Counter(w for _, _, ps in righe for w in ps)
    cl = e206.classi_di(freq)
    occ = defaultdict(list)
    for k, (pag, ini, ps) in enumerate(righe):
        for j, w in enumerate(ps):
            pos = 0 if j == 0 else (2 if j == len(ps) - 1 else 1)
            for c, v in cl.get(w, {}).items():
                nome = '%s %s' % c
                if nome in classi:
                    occ[nome].append(((pag, ini, pos), k, v))
    out = OrderedDict()
    for nome in classi:
        oo = occ.get(nome, [])
        if len(oo) < 100:
            out[nome] = None
            continue
        per_riga = defaultdict(list)
        for _, k, v in oo:
            per_riga[k].append(v)
        vero = e206.accordo(per_riga)
        strati = defaultdict(list)
        for i, (s, _, _) in enumerate(oo):
            strati[s].append(i)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            vals = [v for _, _, v in oo]
            for idx in strati.values():
                x = [vals[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vals[i] = y
            pr = defaultdict(list)
            for (_, k, _), v in zip(oo, vals):
                pr[k].append(v)
            nulli.append(e206.accordo(pr))
        sd = statistics.pstdev(nulli)
        out[nome] = (vero - statistics.mean(nulli)) / sd if sd else None
    return out


def genera_ii(c, prm, seme, inter=None):
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
    stato = {kk: 0.0 for kk in (inter[0] if inter else {})}
    righe, storia = [], []
    for pag, d in c['P'].items():
        s_pag = sez.get(pag)
        nuove_pag = []
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        if inter:
            for kk in stato:
                stato[kk] = (e152.RHO / 2) * stato[kk] + rnd.gauss(0, e152.SIGMA)
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
            if inter:
                for kk in stato:
                    stato[kk] = e152.RHO * stato[kk] + rnd.gauss(0, e152.SIGMA)
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
                    pesi.append(p)
                x = rnd.choices(cand, pesi)[0]
                if prm['sigma'] and pos < n - 1 and len(Dv(x)) >= 4 and rnd.random() < prm['sigma']:
                    s = e224.spezza(x, att, Dv, rnd)
                    if s:
                        riga += s
                        continue
                riga.append(x)
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if inter:
                riga = e251.applica_interruttori(riga, stato, inter, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe


# ------------------------------------------------------------------ lavori (anche in parallelo)

_INT = {}


def base_e_interruttori():
    if not _INT:
        j = json.load(open(BASE_JSON, encoding='utf-8'))
        classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
        _INT.update(j=j, gamma=j['gamma_per_e252'], classi=classi, inter=e251.interruttori_voynich(classi))
    return _INT


def righe_ii(k, gamma, seme, inter):
    grezzo = genera_ii(k['c2'], dict(e251.CONF, gamma=gamma), seme, inter)
    return grezzo, e236.dopo(grezzo, k['freq'], 100 + seme)


def lavoro(args):
    braccio, seme = args
    k, b = e251._prepara(), base_e_interruttori()
    c = k['c']
    _, rr = righe_ii(k, b['gamma'], seme, b['inter'] if braccio == 'interruttori' else None)
    gp = e232.pagine_di(rr)
    d231 = e231.confronto(k['vpag'], gp, k['rif'])
    out = OrderedDict([('braccio', braccio), ('seme', seme), ('pagella', e251.pagella_grezza(c, rr)), ('R_parole_rare', e251.R_completo(rr, controllo=False)),
                       ('AUC_e231', d231['AUC']), ('piu_pesanti_e231', d231['piu_pesanti']),
                       ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC']),
                       ('profilo', e237.profilo(gp)), ('ripetizioni_immediate', e251.ripetizioni_immediate(gp))])
    if seme == SEMI_VERIFICA[0]:
        out['classi_z'] = test_classi(rr, b['classi'])
    return args, out


def tutti(lavori):
    n = int(os.environ.get('PROCESSI', '1'))
    if n <= 1:
        return dict(lavoro(a) for a in lavori)
    with Pool(n) as pool:
        return dict(pool.imap_unordered(lavoro, lavori))


def main():
    b = base_e_interruttori()
    j = b['j']
    if j['esito'].startswith('non valido'):
        sys.exit('il passo 2 non ha un esito valido: %s' % j['esito'])
    gamma, classi = b['gamma'], b['classi']
    print('base: gamma %.2f (esito del passo 2: %s); tassi di forma lunga %s' % (gamma, j['esito'], {x: round(v, 3) for x, v in b['inter'][0].items()}), flush=True)
    k = e251._prepara()
    # validita' 1: con gli interruttori spenti, identico a e233.genera
    identico = genera_ii(k['c2'], dict(e251.CONF, gamma=gamma), 1, None) == e233.genera(k['c2'], dict(e251.CONF, gamma=gamma), 1)
    print('interruttori spenti identico a e233.genera: %s' % identico, flush=True)
    ris = tutti([(br, s) for s in SEMI_VERIFICA for br in ('base', 'interruttori')])
    # validita' 2: il braccio di base riproduce il passo 2
    braccio_251 = 'gamma' if gamma else 'base'
    det = OrderedDict()
    for v in j['verifica']:
        x, y = v[braccio_251], ris[('base', v['seme'])]
        det['seme %d' % v['seme']] = (x['pagella']['pagella'] == y['pagella']['pagella'] and x['pagella']['riga'] == y['pagella']['riga']
                                      and x['pagella']['mancano'] == y['pagella']['mancano']
                                      and abs(x['AUC_e231'] - y['AUC_e231']) <= TOLL_AUC and abs(x['AUC_e266'] - y['AUC_e266']) <= TOLL_AUC)
    for s in SEMI_VERIFICA:
        for br in ('base', 'interruttori'):
            x = ris[(br, s)]
            print('seme %d %-12s: pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f | R rare %s' % (
                s, br, x['pagella']['pagella'], x['pagella']['riga'], x['pagella']['mancano'], x['AUC_e231'], x['AUC_e266'], x['R_parole_rare']['R']), flush=True)
    z = ris[('interruttori', SEMI_VERIFICA[0])]['classi_z']
    z0 = ris[('base', SEMI_VERIFICA[0])]['classi_z']
    ritrovate = [c for c, v in z.items() if (v or 0) > 3]
    somma = {br: sum(ris[(br, s)]['pagella']['pagella'] for s in SEMI_VERIFICA) for br in ('base', 'interruttori')}
    righe_ok = {br: sum(bool(ris[(br, s)]['pagella']['riga']) for s in SEMI_VERIFICA) for br in ('base', 'interruttori')}
    medie = {br: OrderedDict([('pagella_media', somma[br] / 3), ('semi_con_riga', righe_ok[br]),
                              ('AUC_e231_media', statistics.mean(ris[(br, s)]['AUC_e231'] for s in SEMI_VERIFICA)),
                              ('AUC_e266_media', statistics.mean(ris[(br, s)]['AUC_e266'] for s in SEMI_VERIFICA))]) for br in ('base', 'interruttori')}
    motivi = []
    if len(ritrovate) < 10:
        motivi.append('classi')
    if somma['interruttori'] < somma['base']:
        motivi.append('pagella')
    if righe_ok['interruttori'] < righe_ok['base']:
        motivi.append('riga')
    if not identico:
        esito = 'non valido'
    elif not all(det.values()):
        esito = 'non valido: non determinismo'
    else:
        esito = 'passo superato' if not motivi else 'non superato: ' + ' + '.join(motivi)
    out = OrderedDict([('gamma_base', gamma), ('esito_passo_2', j['esito']), ('validita_identico_e233', identico), ('determinismo', det),
                       ('tassi', b['inter'][0]), ('verifica', [OrderedDict([('seme', s), ('base', ris[('base', s)]), ('interruttori', ris[('interruttori', s)])]) for s in SEMI_VERIFICA]),
                       ('classi_z_seme_7', z), ('classi_z_seme_7_base', z0), ('classi_ritrovate', ritrovate), ('medie', medie),
                       ('esito', esito), ('motivo', motivi)])
    json.dump(out, open(os.path.join(RISULTATI, 'e252_interruttori_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    f = lambda x: '%.1f' % x if x is not None else '—'
    md = ['# e252 — Passo 3 del piano 18/18: dodici interruttori di riga', '',
          "Base del passo 2: e241 con γ %.2f (esito del passo 2: %s). Le 12 classi dell'e206b come interruttori di riga (AR(1), ripartenza a pagina). "
          'Preregistrazione: `preregistrazioni/e252.md` (integrazione in fondo).' % (gamma, j['esito']), '',
          'Validità: interruttori spenti = e233.genera: %s; base = passo 2 sui semi 7–9: %s.' % ('sì' if identico else 'NO', ', '.join('%s %s' % (s, 'sì' if v else 'NO') for s, v in det.items())), '',
          '| seme | braccio | pagella | riga | mancano | AUC e231 | AUC e266 | R rare |', '|---|---|---|---|---|---|---|---|']
    for s in SEMI_VERIFICA:
        for br in ('base', 'interruttori'):
            x = ris[(br, s)]
            md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f | %s |' % (s, br, x['pagella']['pagella'], 'sì' if x['pagella']['riga'] else 'no',
                                                                       ', '.join(x['pagella']['mancano']) or '—', x['AUC_e231'], x['AUC_e266'], f(x['R_parole_rare']['R'])))
    md += ['', '| classe | z con gli interruttori (seme 7) | z della base (seme 7) |', '|---|---|---|']
    for c in classi:
        md.append('| %s | %s | %s |' % (c, f(z.get(c)), f(z0.get(c))))
    md += ['', 'Classi ritrovate con z > 3: %d su %d.' % (len(ritrovate), len(classi)), '',
           'Medie: base pagella %.2f, riga in %d semi, AUC %.3f / %.3f; interruttori pagella %.2f, riga in %d semi, AUC %.3f / %.3f.' % (
               medie['base']['pagella_media'], medie['base']['semi_con_riga'], medie['base']['AUC_e231_media'], medie['base']['AUC_e266_media'],
               medie['interruttori']['pagella_media'], medie['interruttori']['semi_con_riga'], medie['interruttori']['AUC_e231_media'], medie['interruttori']['AUC_e266_media']),
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e252_interruttori_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
