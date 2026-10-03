# -*- coding: utf-8 -*-
"""Esperimento 243b (passo 1 del piano 18/18, rifatto): il generatore dell'e242 (e241 + ell_r) con copia verticale fisica a
distanza (distanze del Voynich) e penalita' per la ripetizione immediata. Scelta di phi con il discriminatore dell'e266;
verifica sui semi 7-9 con pagella, discriminatori dell'e231 e dell'e266, profilo di riuso, parole rare.

Preregistrazione: preregistrazioni/e243b.md. Scrive risultati/e243b_riuso_su_vocabolario.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

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
import e242_ripetizioni_lunghezza as e242
import e243_riuso_esplicito as e243
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
PHI, RIP, SEME_SCELTA, SEMI_VERIFICA = (0.1, 0.25), 0.3, 1, (7, 8, 9)
frequenti_voynich = e242.frequenti_voynich


def genera(c, prm, seme):
    """Come e242.genera, con in piu' 'distanza' (copia verticale fisica da una riga a distanza d sopra, d dalla distribuzione
    data, parola scelta con peso exp(-|dx|/3)) e 'rip' (peso delle candidate uguali alla parola precedente)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rango = e233.ranghi(c)
    tau, ell_r = prm.get('tau', 0.0), prm.get('ell_r', 0.0)
    distanza, rip = prm.get('distanza'), prm.get('rip', 1.0)
    frequenti = frequenti_voynich(c)
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
        prima_sopra, sopra, ultime = None, None, []
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
                    da_tema = False
                    if fisica:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi']
                    else:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra)
                    if copia and fisica and distanza:
                        x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                        d = rnd.choices(*distanza)[0]
                        fonte = ultime[-d] if d <= len(ultime) and ultime[-d] else sopra
                        centri, acc = [], 0
                        for w in fonte:
                            centri.append(acc + len(Dv(w)) / 2)
                            acc += len(Dv(w)) + 1
                        base = rnd.choices(fonte, [math.exp(-abs(cc - x0) / 3.0) for cc in centri])[0]
                    elif copia and fisica:
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
                        da_tema = rnd.random() < 0.3
                        base = rnd.choice(tema) if da_tema else estrai()
                    w = e224.variante(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv)
                    if tau and da_tema and w == base and rnd.random() < tau:
                        w = e234.forza_variante(base, mod, rnd, prm['nu'], att, Dv)
                    cand.append(w)
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    if ell_r and x not in frequenti:
                        p *= (len(Dv(x)) / media) ** ell_r
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
            ultime = (ultime + [[w for w in riga if trascrizione.pulita(w)]])[-6:]
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe




def righe_ini(rr):
    out = OrderedDict()
    for pag, ini, ps in rr:
        out.setdefault(pag, []).append((bool(ini), ps))
    return out


def ripetizioni_immediate(gp):
    cp = [(a, b) for rr in gp.values() for r in rr for a, b in zip(r, r[1:])]
    return sum(a == b for a, b in cp) / len(cp)


def misura(c, c2, vpag, rif, vt266, rif266, freq, prm, seme, completa):
    rr = e236.dopo(genera(c2, prm, seme), freq, 100 + seme)
    gp = e232.pagine_di(rr)
    r = OrderedDict([('AUC_e266', e266.confronto(vt266, e266.tabella(righe_ini(rr), rif266))['AUC'])])
    if completa:
        d231 = e231.confronto(vpag, gp, rif)
        r['AUC_e231'] = d231['AUC']
        r['piu_pesanti_e231'] = d231['piu_pesanti']
        r['pagella_e224'] = e236.pagella(c, rr)
        r['profilo'] = e237.profilo(gp)
        r['R_parole_rare'] = e243.R_rare(rr)
        r['ripetizioni_immediate'] = ripetizioni_immediate(gp)
    return r


def main():
    c, c2, freq, vpag, rif, pv = e251.contesto()
    vi = e266.voynich_ini()
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    dist = e243.distanze_voynich(pv)
    ds = [d for d in range(1, e243.D_MAX + 1)]
    ws = [dist['R'][1][d] + dist['V'][1][d] for d in ds]
    base = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2, ell_r=1.0, tau=0.0)
    identico = genera(c2, base, SEME_SCELTA) == e242.genera(c2, base, SEME_SCELTA)
    print("identico all'e242 con phi 0 e senza penalita': %s" % identico, flush=True)
    scelta = OrderedDict()
    for phi in PHI:
        prm = dict(base, phi=phi, fisica=True, distanza=(ds, ws), rip=RIP)
        scelta['phi %.2f' % phi] = misura(c, c2, vpag, rif, vt266, rif266, freq, prm, SEME_SCELTA, False)
        print('phi %.2f (seme 1): AUC e266 %.3f' % (phi, scelta['phi %.2f' % phi]['AUC_e266']), flush=True)
    phi = min(PHI, key=lambda f: (scelta['phi %.2f' % f]['AUC_e266'], f))
    prm = dict(base, phi=phi, fisica=True, distanza=(ds, ws), rip=RIP)
    ver = []
    for s in SEMI_VERIFICA:
        r = misura(c, c2, vpag, rif, vt266, rif266, freq, prm, s, True)
        ver.append(r)
        print('seme %d: pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f | R rare %.1f | ripetizioni immediate %.4f' % (
            s, r['pagella_e224']['pagella'], r['pagella_e224']['riga'], r['pagella_e224']['mancano'], r['AUC_e231'], r['AUC_e266'],
            r['R_parole_rare'], r['ripetizioni_immediate']), flush=True)
    pag = statistics.mean(x['pagella_e224']['pagella'] for x in ver)
    riga = all(x['pagella_e224']['riga'] for x in ver)
    a231 = statistics.mean(x['AUC_e231'] for x in ver)
    a266 = statistics.mean(x['AUC_e266'] for x in ver)
    esito = 'non valido' if not identico else ('passo superato' if pag >= 17 and riga and a231 <= 0.85 else 'non superato')
    ris = OrderedDict([('validita_identico_e242', identico), ('scelta_seme_1', scelta), ('phi', phi), ('rip', RIP), ('verifica', ver),
                       ('pagella_media', pag), ('riga_in_tutti', riga), ('AUC_e231_media', a231), ('AUC_e266_media', a266),
                       ('mancano', dict(Counter(m for x in ver for m in x['pagella_e224']['mancano']))), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e243b_riuso_su_vocabolario.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    v = e237.profilo(e232.pagine_di([(p, True, r) for p, rr in pv.items() for r in rr]))
    md = ['# e243b — Passo 1 del piano 18/18, rifatto: riuso sopra un vocabolario vero', '',
          "Generatore dell'e242 (e241 + ℓr 1) con copia verticale fisica a distanza (φ %.2f, scelto sul seme 1 con l'AUC dell'e266) e penalità %.1f per "
          "la ripetizione immediata. Validità (φ 0, senza penalità = e242): %s. Preregistrazione: `preregistrazioni/e243b.md`." % (phi, RIP, 'sì' if identico else 'NO'), '',
          '| seme | pagella | riga | mancano | AUC e231 | AUC e266 | R | V | N | R parole rare | ripetizioni immediate |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for s, x in zip(SEMI_VERIFICA, ver):
        md.append('| %d | %d/18 | %s | %s | %.3f | %.3f | %.1f%% | %.1f%% | %.1f%% | %.1f | %.2f%% |' % (
            s, x['pagella_e224']['pagella'], 'sì' if x['pagella_e224']['riga'] else 'no', ', '.join(x['pagella_e224']['mancano']) or '—', x['AUC_e231'],
            x['AUC_e266'], 100 * x['profilo']['R'], 100 * x['profilo']['V'], 100 * x['profilo']['N'], x['R_parole_rare'], 100 * x['ripetizioni_immediate']))
    md += ['', 'Medie: pagella %.1f/18, AUC e231 %.3f, AUC e266 %.3f. Riferimenti: e241 16/18 (un seme), AUC e231 0,874, AUC e266 0,937; Voynich: R %.1f%%, V %.1f%%, '
           'N %.1f%%, parole rare 1,96, ripetizioni immediate 0,97%%.' % (pag, a231, a266, 100 * v['R'], 100 * v['V'], 100 * v['N']), '',
           'Caratteristiche più pesanti del discriminatore dell\'e231 (seme 7; positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in ver[0]['piu_pesanti_e231']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e243b_riuso_su_vocabolario.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
