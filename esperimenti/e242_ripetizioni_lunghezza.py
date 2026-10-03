# -*- coding: utf-8 -*-
"""Esperimento 242: generatore dell'e241 (operatore di variante condizionato ai segni vicini, kappa 1, chi 0,2, eta 1,
spezzature e prefissi dopo la generazione) con tau (tema variato) e ell_r (preferenza per le parole lunghe solo fra quelle
non frequenti). Metrica: il discriminatore dell'e231.

Preregistrazione: preregistrazioni/e242.md. Scrive risultati/e242_ripetizioni_lunghezza.json e .md.
"""
import json, os, random, statistics, sys
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
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
TAU, ELL_R, SEME_SCELTA, SEMI_VERIFICA, RIFERIMENTO = (0.0, 0.5), (0.0, 1.0), 1, (2, 3), 0.874
_FREQ = set()


def frequenti_voynich(c):
    if not _FREQ:
        _FREQ.update(w for w, _ in Counter(c['voy']).most_common(200))
    return _FREQ


def genera(c, prm, seme):
    """Come e234.genera, ma 'ell_r' moltiplica per (lunghezza / media)^ell_r solo il peso delle candidate che non sono fra
    le 200 parole piu' frequenti del Voynich."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    kappa, chi = prm.get('kappa', 0.0), prm.get('chi', 0.0)
    rango = e233.ranghi(c)
    tau, ell_r = prm.get('tau', 0.0), prm.get('ell_r', 0.0)
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



def prova(c2, c, vpag, rif, freq, prm, seme, indice, con_pagella=False):
    rr = e236.dopo(genera(c2, prm, seme), freq, indice)
    gp = e232.pagine_di(rr)
    r = e231.confronto(vpag, gp, rif)
    r.update(e234.descrittive(gp))
    r['profilo'] = e237.profilo(gp)
    if con_pagella:
        r['pagella_e224'] = e236.pagella(c, rr)
    return r


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    conf = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2)
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    ris = OrderedDict([('Voynich', e234.descrittive(pv)), ('profilo_Voynich', e237.profilo(pv))])
    scelta, i = OrderedDict(), 0
    for t in TAU:
        for l in ELL_R:
            nome = 'tau %.1f, ell_r %.1f' % (t, l)
            scelta[nome] = prova(c2, c, vpag, rif, freq, dict(conf, tau=t, ell_r=l), SEME_SCELTA, i)
            i += 1
            r = scelta[nome]
            print('%s: AUC %.3f %s R %.3f N %.3f' % (nome, r['AUC'], ' '.join('%s %.3f' % (k, r[k]) for k in cols), r['profilo']['R'], r['profilo']['N']), flush=True)
    migliore = min(scelta, key=lambda n: (scelta[n]['AUC'], n))
    t, l = (float(x.split()[1]) for x in migliore.split(', '))
    verifica = [prova(c2, c, vpag, rif, freq, dict(conf, tau=t, ell_r=l), s, 100 + s, con_pagella=(s == SEMI_VERIFICA[0])) for s in SEMI_VERIFICA]
    auc = statistics.mean(x['AUC'] for x in verifica)
    esito = 'indistinguibile' if auc <= 0.6 else 'migliore' if auc <= RIFERIMENTO - 0.05 else 'non migliore'
    pg = verifica[0]['pagella_e224']
    print('scelta %s: verifica %s (media %.3f) | pagella %d/18 riga %s mancano %s -> %s' % (
        migliore, [round(x['AUC'], 3) for x in verifica], auc, pg['pagella'], pg['riga'], pg['mancano'], esito), flush=True)
    ris.update([('scelta_seme_1', scelta), ('migliore', migliore), ('verifica', verifica), ('AUC_verifica', auc), ('riferimento_e241', RIFERIMENTO), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e242_ripetizioni_lunghezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v, pv_ = ris['Voynich'], ris['profilo_Voynich']
    md = ['# e242 — Meno ripetizioni e parole rare più lunghe, sopra l\'e241', '',
          "Generatore dell'e241 con τ (tema variato) e ℓr (preferenza per le parole lunghe solo fra le non frequenti). AUC del discriminatore "
          "dell'e231; riferimento (e241) %.3f. Preregistrazione: `preregistrazioni/e242.md`." % RIFERIMENTO, '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | N |',
          '|---|---|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s | %.1f%% | %.1f%% |' % (' | '.join('%.3f' % v[k] for k in cols), 100 * pv_['R'], 100 * pv_['N'])]
    for n, r in scelta.items():
        md.append('| %s, seme 1 | %.3f | %s | %.1f%% | %.1f%% |' % (n, r['AUC'], ' | '.join('%.3f' % r[k] for k in cols), 100 * r['profilo']['R'], 100 * r['profilo']['N']))
    md.append('| %s, semi 2–3 | %.3f | %s | %.1f%% | %.1f%% |' % (migliore, auc, ' | '.join('%.3f' % statistics.mean(x[k] for x in verifica) for k in cols),
                                                               100 * statistics.mean(x['profilo']['R'] for x in verifica), 100 * statistics.mean(x['profilo']['N'] for x in verifica)))
    md += ['', 'Pagella dell\'e224 sulla scelta (seme 2): %d/18, riga riprodotta: %s; mancano: %s.' % (pg['pagella'], 'sì' if pg['riga'] else 'no', ', '.join(pg['mancano']) or 'nessuna'),
           '', 'Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e242_ripetizioni_lunghezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
