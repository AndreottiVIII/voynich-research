# -*- coding: utf-8 -*-
"""Esperimento 233: generatore dell'e232 (delta 0, eta 1) con variazione secondo la frequenza (kappa) e copia della parola
precedente (chi); dopo la generazione, spezzature e prefissi staccati come nell'e227d. Metrica: il discriminatore
dell'e231.

Preregistrazione: preregistrazioni/e233.md. Scrive risultati/e233_frequenti_esatte.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e227d_prefissi_staccati as e227d
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231
import e232_meno_pagina as e232

RISULTATI = os.path.join(QUI, '..', 'risultati')
KAPPA, CHI, SEME_SCELTA, SEMI_VERIFICA = (0.0, 0.5, 1.0), (0.0, 0.1, 0.2), 1, (2, 3)
SIGMA_POST, PI_POST = 0.09, 0.30
_RANGO = {}


def ranghi(c):
    """Rango percentile pesato per occorrenze: 0 per le parole piu' frequenti, verso 1 per le uniche."""
    if not _RANGO:
        cnt = Counter(c['voy'])
        tot = sum(cnt.values())
        acc = 0
        for w, n in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])):
            _RANGO[w] = (acc + n / 2) / tot
            acc += n
    return _RANGO


def genera(c, prm, seme):
    """Come e232.genera ('gamma', 'fisica', 'delta'), con in piu' 'kappa' (modifiche medie MU * (2 r)^kappa, r = rango
    percentile della parola di base) e 'chi' (con questa probabilita' la seconda candidata e' una variante della parola
    precedente della riga)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rango = ranghi(c)
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


def descrittive(pag):
    d = e232.descrittive(pag)
    tutte = Counter(w for rr in pag.values() for r in rr for w in r)
    ws = [w for rr in pag.values() for r in rr for w in r]
    d['uniche_nel_testo'] = sum(tutte[w] == 1 for w in ws) / len(ws)
    D = misure.divisore(misure.GLIFI_EVA)
    sims = [1 - misure._dist_norm(tuple(D(a)), tuple(D(b))) for rr in pag.values() for r in rr for a, b in zip(r, r[1:])]
    d['somiglianza_vicine'] = statistics.mean(sims)
    return d


def prova(c, vpag, rif, freq, prm, seme, indice):
    gp = e232.pagine_di(genera(c, prm, seme))
    nomi = list(gp)
    trasf = e227d.trasforma([gp[p] for p in nomi], freq, SIGMA_POST, PI_POST, random.Random(2272 + indice))
    gp = OrderedDict(zip(nomi, trasf))
    r = e231.confronto(vpag, gp, rif)
    r.update(descrittive(gp))
    return r


def main():
    c = e224.contesto()
    conf = dict(e224.BASE, eta=1.0)
    identico = genera(c, dict(conf, kappa=0.0, chi=0.0), SEME_SCELTA) == e232.genera(c, conf, SEME_SCELTA)
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    freq = Counter(c['voy'])
    ris = OrderedDict([('configurazione', {k: (list(v) if isinstance(v, tuple) else v) for k, v in conf.items()}), ('validita_identico_e232', identico),
                       ('Voynich', descrittive(OrderedDict((p, rr) for p, (_, rr) in vpag.items())))])
    print("identico all'e232 con kappa 0 e chi 0: %s; Voynich %s" % (identico, {k: round(v, 3) for k, v in ris['Voynich'].items()}), flush=True)
    scelta, i = OrderedDict(), 0
    for kp in KAPPA:
        for ch in CHI:
            nome = 'kappa %.1f, chi %.1f' % (kp, ch)
            scelta[nome] = prova(c, vpag, rif, freq, dict(conf, kappa=kp, chi=ch), SEME_SCELTA, i)
            i += 1
            r = scelta[nome]
            print('%s: AUC %.3f, fra le 100 %.3f, uniche %.3f, vicine %.3f, tipi/parole %.3f' % (
                nome, r['AUC'], r['fra_le_100'], r['uniche_nel_testo'], r['somiglianza_vicine'], r['tipi_su_parole_pagina']), flush=True)
    migliore = min(scelta, key=lambda n: (scelta[n]['AUC'], n))
    kp, ch = (float(x.split()[1].rstrip(',')) for x in migliore.split(', '))
    verifica = OrderedDict()
    for n, (a, b) in (('kappa 0.0, chi 0.0', (0.0, 0.0)), (migliore, (kp, ch))):
        if n in verifica:
            continue
        verifica[n] = [prova(c, vpag, rif, freq, dict(conf, kappa=a, chi=b), s, 100 + s) for s in SEMI_VERIFICA]
        print('verifica %s: AUC %s' % (n, [round(x['AUC'], 3) for x in verifica[n]]), flush=True)
    auc = {k: statistics.mean(x['AUC'] for x in v) for k, v in verifica.items()}
    a0, am = auc['kappa 0.0, chi 0.0'], auc[migliore]
    esito = ('non valido' if not identico else 'indistinguibile' if am <= 0.6 else 'aiuta' if am <= a0 - 0.05 else 'non aiuta abbastanza')
    ris.update([('scelta_seme_1', scelta), ('migliore', migliore), ('verifica', verifica), ('AUC_verifica', auc), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e233_frequenti_esatte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = ris['Voynich']
    md = ['# e233 — Parole frequenti esatte, rare variate, e copia della parola precedente', '',
          "Generatore dell'e232 (η 1, δ 0) con κ (modifiche medie MU·(2r)^κ) e χ (seconda candidata variante della parola precedente); dopo la "
          "generazione σ 0,09 e prefissi staccati π 0,30 (e227d). AUC del discriminatore dell'e231. Validità (κ 0, χ 0 = e232): %s. "
          'Preregistrazione: `preregistrazioni/e233.md`.' % ('sì' if identico else 'NO'), '',
          '| | AUC | fra le 100 | uniche nel testo | somiglianza vicine | tipi su parole (pagina) |', '|---|---|---|---|---|---|',
          '| **Voynich** | | %.3f | %.3f | %.3f | %.3f |' % (v['fra_le_100'], v['uniche_nel_testo'], v['somiglianza_vicine'], v['tipi_su_parole_pagina'])]
    for n, r in scelta.items():
        md.append('| %s, seme 1 | %.3f | %.3f | %.3f | %.3f | %.3f |' % (n, r['AUC'], r['fra_le_100'], r['uniche_nel_testo'], r['somiglianza_vicine'], r['tipi_su_parole_pagina']))
    for n, rr in verifica.items():
        md.append('| %s, semi 2–3 | %.3f | %.3f | %.3f | %.3f | %.3f |' % (n, auc[n], *(statistics.mean(x[q] for x in rr) for q in (
            'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'tipi_su_parole_pagina'))))
    md += ['', 'Caratteristiche più pesanti che restano (%s, seme 2; coefficiente positivo = più nel generatore):' % migliore, '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[migliore][0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e233_frequenti_esatte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
