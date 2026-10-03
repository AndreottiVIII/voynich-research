# -*- coding: utf-8 -*-
"""Esperimento 234: generatore dell'e233 (kappa 1, chi 0,2, eta 1) con il tema sempre modificato (tau) e una preferenza per
le candidate lunghe (ell); dopo la generazione, spezzature e prefissi staccati come nell'e227d. Metrica: il discriminatore
dell'e231.

Preregistrazione: preregistrazioni/e234.md. Scrive risultati/e234_tema_variato.json e .md.
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
import e233_frequenti_esatte as e233

RISULTATI = os.path.join(QUI, '..', 'risultati')
TAU, ELL, SEME_SCELTA, SEMI_VERIFICA = (0.0, 0.5, 1.0), (0.0, 1.5), 1, (2, 3)
BASE_E233 = dict(kappa=1.0, chi=0.2)


def forza_variante(base, mod, rnd, nu, att, Dv):
    """Prima modifica ammissibile (attestata, o ben formata e accettata con probabilita' nu) entro 10 tentativi."""
    u = tuple(Dv(base))
    for _ in range(10):
        x = mod.modifica(u, rnd)
        if ''.join(x) != base and (''.join(x) in att or (mod.valida(x) and rnd.random() < nu)):
            return ''.join(x)
    return base


def genera(c, prm, seme):
    """Come e233.genera ('gamma', 'fisica', 'delta', 'kappa', 'chi'), con in piu' 'tau' (una candidata dal tema rimasta
    uguale si modifica una volta con questa probabilita') e 'ell' (peso delle candidate * (lunghezza / media)^ell)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rango = e233.ranghi(c)
    tau, ell = prm.get('tau', 0.0), prm.get('ell', 0.0)
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
                    da_tema = False
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
                        da_tema = rnd.random() < 0.3
                        base = rnd.choice(tema) if da_tema else estrai()
                    w = e224.variante(base, e153.MU * fattore(base), mod, rnd, prm['nu'], att, Dv)
                    if tau and da_tema and w == base and rnd.random() < tau:
                        w = forza_variante(base, mod, rnd, prm['nu'], att, Dv)
                    cand.append(w)
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    if ell:
                        p *= (len(Dv(x)) / media) ** ell
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
    d = e233.descrittive(pag)
    D = misure.divisore(misure.GLIFI_EVA)
    ws = [w for rr in pag.values() for r in rr for w in r]
    d['lunghezza_media'] = statistics.mean(len(D(w)) for w in ws)
    return d


def prova(c, vpag, rif, freq, prm, seme, indice):
    gp = e232.pagine_di(genera(c, prm, seme))
    nomi = list(gp)
    trasf = e227d.trasforma([gp[p] for p in nomi], freq, e233.SIGMA_POST, e233.PI_POST, random.Random(2272 + indice))
    gp = OrderedDict(zip(nomi, trasf))
    r = e231.confronto(vpag, gp, rif)
    r.update(descrittive(gp))
    return r


def main():
    c = e224.contesto()
    conf = dict(e224.BASE, eta=1.0, **BASE_E233)
    identico = genera(c, dict(conf, tau=0.0, ell=0.0), SEME_SCELTA) == e233.genera(c, conf, SEME_SCELTA)
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    freq = Counter(c['voy'])
    ris = OrderedDict([('configurazione', {k: (list(v) if isinstance(v, tuple) else v) for k, v in conf.items()}), ('validita_identico_e233', identico),
                       ('Voynich', descrittive(OrderedDict((p, rr) for p, (_, rr) in vpag.items())))])
    print("identico all'e233 con tau 0 e ell 0: %s; Voynich %s" % (identico, {k: round(v, 3) for k, v in ris['Voynich'].items()}), flush=True)
    scelta, i = OrderedDict(), 0
    for t in TAU:
        for l in ELL:
            nome = 'tau %.1f, ell %.1f' % (t, l)
            scelta[nome] = prova(c, vpag, rif, freq, dict(conf, tau=t, ell=l), SEME_SCELTA, i)
            i += 1
            r = scelta[nome]
            print('%s: AUC %.3f, tipi pagina %.3f, fra le 100 %.3f, uniche %.3f, vicine %.3f, lunghezza %.2f' % (
                nome, r['AUC'], r['tipi_su_parole_pagina'], r['fra_le_100'], r['uniche_nel_testo'], r['somiglianza_vicine'], r['lunghezza_media']), flush=True)
    migliore = min(scelta, key=lambda n: (scelta[n]['AUC'], n))
    t, l = (float(x.split()[1]) for x in migliore.split(', '))
    verifica = OrderedDict()
    for n, (a, b) in (('tau 0.0, ell 0.0', (0.0, 0.0)), (migliore, (t, l))):
        if n in verifica:
            continue
        verifica[n] = [prova(c, vpag, rif, freq, dict(conf, tau=a, ell=b), s, 100 + s) for s in SEMI_VERIFICA]
        print('verifica %s: AUC %s' % (n, [round(x['AUC'], 3) for x in verifica[n]]), flush=True)
    auc = {k: statistics.mean(x['AUC'] for x in v) for k, v in verifica.items()}
    a0, am = auc['tau 0.0, ell 0.0'], auc[migliore]
    esito = ('non valido' if not identico else 'indistinguibile' if am <= 0.6 else 'aiuta' if am <= a0 - 0.05 else 'non aiuta abbastanza')
    ris.update([('scelta_seme_1', scelta), ('migliore', migliore), ('verifica', verifica), ('AUC_verifica', auc), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e234_tema_variato.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = ris['Voynich']
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    md = ['# e234 — Omogeneità fatta di varianti: il tema si scrive sempre modificato', '',
          "Generatore dell'e233 (κ 1, χ 0,2, η 1) con τ (candidata dal tema rimasta uguale: modificata una volta con probabilità τ) e ℓ "
          "(peso · (lunghezza/media)^ℓ); dopo la generazione σ 0,09 e prefissi staccati π 0,30. AUC del discriminatore dell'e231. "
          'Validità (τ 0, ℓ 0 = e233): %s. Preregistrazione: `preregistrazioni/e234.md`.' % ('sì' if identico else 'NO'), '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media |', '|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s |' % ' | '.join('%.3f' % v[q] for q in cols)]
    for n, r in scelta.items():
        md.append('| %s, seme 1 | %.3f | %s |' % (n, r['AUC'], ' | '.join('%.3f' % r[q] for q in cols)))
    for n, rr in verifica.items():
        md.append('| %s, semi 2–3 | %.3f | %s |' % (n, auc[n], ' | '.join('%.3f' % statistics.mean(x[q] for x in rr) for q in cols)))
    md += ['', 'Caratteristiche più pesanti che restano (%s, seme 2; coefficiente positivo = più nel generatore):' % migliore, '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[migliore][0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e234_tema_variato.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
