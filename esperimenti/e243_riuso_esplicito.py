# -*- coding: utf-8 -*-
"""Esperimento 243 (passo 1 del piano 18/18): generatore con modulo di riuso esplicito. Candidate per classe (R, V, F, A,
N); fonti di R e V a distanza di righe come nel Voynich e, nella riga scelta, per posizione fisica; varianti con
l'operatore condizionato dell'e241; quote tarate sull'uscita (seme 1); verifica sui semi 7-9.

Preregistrazione: preregistrazioni/e243.md. Scrive risultati/e243_riuso_esplicito.json e .md.
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
import e211_parole_proprie as e211
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e238_profilo_riuso as e238
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
CLASSI = ('R', 'V', 'F', 'A', 'N')
K, LAM, ETA, NU, ELL_R, D_MAX, SCALA_X = 8, 1.0, 1.0, 0.4, 1.0, 6, 3.0
SEME_RICERCA, SEMI_VERIFICA, ITERAZIONI = 1, (7, 8, 9), 4
D = e237.D


def distanze_voynich(pagine):
    """Distribuzioni della distanza in righe (0..D_MAX) dalla fonte piu' recente, per R e V."""
    tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
    inventario = sorted({x for w in tutte for x in D(w)})
    dist = {'R': Counter(), 'V': Counter()}
    for rr in pagine.values():
        sulla = {}
        primo = True
        for k, r in enumerate(rr):
            for w in r:
                u = tuple(D(w))
                if not primo:
                    if u in sulla:
                        dist['R'][min(D_MAX, k - sulla[u])] += 1
                    else:
                        v = [sulla[x] for x in e237.vicini(u, inventario) if x in sulla]
                        if v:
                            dist['V'][min(D_MAX, k - max(v))] += 1
                primo = False
                sulla[u] = k
    return {c: ([d for d in range(D_MAX + 1)], [dist[c][d] + 0.5 for d in range(D_MAX + 1)]) for c in dist}


def centri(riga, Dv):
    out, acc = [], 0
    for w in riga:
        out.append(acc + len(Dv(w)) / 2)
        acc += len(Dv(w)) + 1
    return out


def fonte(rnd, dd, riga, ultime, x0, Dv):
    d = rnd.choices(*dd)[0]
    if d == 0 or d > len(ultime):
        cand = [w for w in riga if trascrizione.pulita(w)]
        return rnd.choice(cand) if cand else None
    sopra = ultime[-d]
    if not sopra:
        return None
    cc = centri(sopra, Dv)
    return rnd.choices(sopra, [math.exp(-abs(c - x0) / SCALA_X) for c in cc])[0]


def genera(c, quote, dist, seme):
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    frequenti = {w for w, _ in Counter(c['voy']).most_common(200)}
    classi, pesi_classi = list(CLASSI), [quote[x] for x in CLASSI]
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in c['P'].items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        gt, gp = e232.globali(c, lingua, 1.0)
        ft, fp = e238.frequenti(c, lingua)
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        prima_sopra, ultime = None, []
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
                x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                cand = []
                for _ in range(K):
                    cl = rnd.choices(classi, pesi_classi)[0]
                    w = None
                    if cl in ('R', 'V'):
                        s = fonte(rnd, dist[cl], riga, ultime, x0, Dv)
                        if s is not None:
                            w = s if cl == 'R' else e234.forza_variante(s, mod, rnd, NU, att, Dv)
                        else:
                            cl = 'F'
                    if cl == 'F':
                        w = rnd.choices(ft, fp)[0]
                    elif cl == 'A':
                        w = rnd.choices(gt, gp)[0]
                    elif cl == 'N':
                        w = e234.forza_variante(rnd.choices(gt, gp)[0], mod, rnd, NU, att, Dv)
                    cand.append(w)
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** LAM) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** ETA
                    if x not in frequenti:
                        p *= (len(Dv(x)) / media) ** ELL_R
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            ultime = (ultime + [[w for w in riga if trascrizione.pulita(w)]])[-D_MAX:]
            righe.append((pag, ini, riga))
    return righe


def R_rare(rr):
    sez = {x.pagina: x.sezione for x in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    herb = defaultdict(list)
    for pag, _, ps in rr:
        herb[pag] += [w for w in ps if trascrizione.pulita(w)]
    unita = [v for p, v in herb.items() if len(v) >= 60 and sez.get(p) == 'H']
    return e211.prova(unita, random.Random(211))['R']


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    bersaglio = e237.profilo(pv)
    dist = distanze_voynich(pv)
    quote = OrderedDict((x, bersaglio[x]) for x in CLASSI)
    taratura = []
    for it in range(ITERAZIONI):
        gp = e232.pagine_di(e236.dopo(genera(c2, quote, dist, SEME_RICERCA), freq, 0))
        prof = e237.profilo(gp)
        taratura.append(OrderedDict([('quote', dict(quote)), ('profilo', {x: prof[x] for x in CLASSI})]))
        print('taratura %d: quote %s -> profilo %s' % (it, {x: round(v, 3) for x, v in quote.items()}, {x: round(prof[x], 3) for x in CLASSI}), flush=True)
        if it < ITERAZIONI - 1:
            nuove = {x: quote[x] * bersaglio[x] / max(prof[x], 1e-3) for x in CLASSI}
            s = sum(nuove.values())
            quote = OrderedDict((x, nuove[x] / s) for x in CLASSI)
    verifica = []
    for s in SEMI_VERIFICA:
        rr = e236.dopo(genera(c2, quote, dist, s), freq, 100 + s)
        gp = e232.pagine_di(rr)
        r = e231.confronto(vpag, gp, rif)
        r.update(e234.descrittive(gp))
        r['profilo'] = e237.profilo(gp)
        r['pagella_e224'] = e236.pagella(c, rr)
        r['R_parole_rare'] = R_rare(rr)
        verifica.append(r)
        print('seme %d: AUC %.3f | pagella %d/18 riga %s mancano %s | R rare %.1f | profilo %s' % (
            s, r['AUC'], r['pagella_e224']['pagella'], r['pagella_e224']['riga'], r['pagella_e224']['mancano'], r['R_parole_rare'],
            {x: round(r['profilo'][x], 3) for x in CLASSI}), flush=True)
    auc = statistics.mean(x['AUC'] for x in verifica)
    pag = statistics.mean(x['pagella_e224']['pagella'] for x in verifica)
    riga = all(x['pagella_e224']['riga'] for x in verifica)
    esito = 'passo superato' if pag >= 17 and riga and auc <= 0.85 else 'non superato'
    mancano = Counter(m for x in verifica for m in x['pagella_e224']['mancano'])
    ris = OrderedDict([('quote_finali', quote), ('distanze', dist), ('taratura', taratura), ('bersaglio', {x: bersaglio[x] for x in CLASSI}),
                       ('verifica', verifica), ('AUC_media', auc), ('pagella_media', pag), ('riga_in_tutti', riga), ('mancano_conteggio', dict(mancano)), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e243_riuso_esplicito.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    v = e234.descrittive(pv)
    md = ['# e243 — Passo 1 del piano 18/18: modulo di riuso esplicito', '',
          'Quote di classe tarate sull\'uscita (seme 1): %s. Verifica sui semi 7–9. Preregistrazione: `preregistrazioni/e243.md`.' % (
              ', '.join('%s %.3f' % kv for kv in quote.items())), '',
          '| | AUC | pagella | riga | R parole rare | R | V | N | tipi su parole (pagina) | fra le 100 | uniche | vicine | lunghezza |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich** | | 18/18 | sì | 1,96 | %.1f%% | %.1f%% | %.1f%% | %s |' % (100 * bersaglio['R'], 100 * bersaglio['V'], 100 * bersaglio['N'], ' | '.join('%.3f' % v[k] for k in cols))]
    for s, r in zip(SEMI_VERIFICA, verifica):
        md.append('| seme %d | %.3f | %d/18 | %s | %.1f | %.1f%% | %.1f%% | %.1f%% | %s |' % (
            s, r['AUC'], r['pagella_e224']['pagella'], 'sì' if r['pagella_e224']['riga'] else 'no', r['R_parole_rare'],
            100 * r['profilo']['R'], 100 * r['profilo']['V'], 100 * r['profilo']['N'], ' | '.join('%.3f' % r[k] for k in cols)))
    md += ['', 'Media: AUC %.3f, pagella %.1f/18. Proprietà mancanti (quante volte su 3 semi): %s.' % (auc, pag, dict(mancano)), '',
           'Caratteristiche più pesanti del discriminatore (seme 7; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e243_riuso_esplicito.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
