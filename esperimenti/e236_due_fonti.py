# -*- coding: utf-8 -*-
"""Esperimento 236: generatore a due fonti (parole del manoscritto esatte con probabilita' g, altrimenti varianti nuove
di parole vicine o del manoscritto), senza serbatoio di pagina; spezzature e prefissi staccati dopo la generazione.
Metrica: il discriminatore dell'e231; pagella dell'e224 sulla scelta.

Preregistrazione: preregistrazioni/e236.md. Scrive risultati/e236_due_fonti.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e135_stato_riga as e135
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e227d_prefissi_staccati as e227d
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234

RISULTATI = os.path.join(QUI, '..', 'risultati')
G, RHO, SEME_SCELTA, SEMI_VERIFICA = (0.6, 0.75, 0.9), (0.5, 0.9), 1, (2, 3)
K, LAM, ETA, NU, RIFERIMENTO = 8, 1.0, 1.0, 0.4, 0.889


def genera(c, prm, seme):
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    g, rho = prm['g'], prm['rho']
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in c['P'].items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        gt, gp = e232.globali(c, lingua, 1.0)
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        prima_sopra, recenti, ultime = None, [], []
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
                cand = []
                for _ in range(K):
                    if rnd.random() < g:
                        cand.append(rnd.choices(gt, gp)[0])
                    else:
                        fonte = recenti + riga
                        seme_v = rnd.choice(fonte) if fonte and rnd.random() < rho else rnd.choices(gt, gp)[0]
                        cand.append(e234.forza_variante(seme_v, mod, rnd, NU, att, Dv))
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** LAM) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** ETA
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            ultime = (ultime + [[w for w in riga if trascrizione.pulita(w)]])[-2:]
            recenti = [w for r in ultime for w in r]
            righe.append((pag, ini, riga))
    return righe


def dopo(rr, freq, indice):
    """Spezzature e prefissi staccati (e227d) sulle parole pulite, conservando pagine e inizi di paragrafo."""
    per = OrderedDict()
    for pag, ini, ps in rr:
        per.setdefault(pag, []).append((ini, [w for w in ps if trascrizione.pulita(w)]))
    nomi = list(per)
    trasf = e227d.trasforma([[ps for _, ps in per[p]] for p in nomi], freq, e233.SIGMA_POST, e233.PI_POST, random.Random(2272 + indice))
    out = []
    for p, righe in zip(nomi, trasf):
        for (ini, _), ps in zip(per[p], righe):
            if ps:
                out.append((p, ini, ps))
    return out


def pagella(c, rr):
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
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
    esiti, riga = e224.valuta(r, c)
    return OrderedDict([('pagella', sum(esiti.values())), ('riga', riga), ('mancano', [k for k, x in esiti.items() if not x])])


def prova(c, vpag, rif, freq, prm, seme, indice, con_pagella=False):
    rr = dopo(genera(c, prm, seme), freq, indice)
    gp = e232.pagine_di(rr)
    r = e231.confronto(vpag, gp, rif)
    r.update(e234.descrittive(gp))
    if con_pagella:
        r['pagella_e224'] = pagella(c, rr)
    return r


def main():
    c = e224.contesto()
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    freq = Counter(c['voy'])
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    ris = OrderedDict([('Voynich', e234.descrittive(OrderedDict((p, rr) for p, (_, rr) in vpag.items())))])
    scelta, i = OrderedDict(), 0
    for g in G:
        for rho in RHO:
            nome = 'g %.2f, rho %.1f' % (g, rho)
            scelta[nome] = prova(c, vpag, rif, freq, {'g': g, 'rho': rho}, SEME_SCELTA, i)
            i += 1
            r = scelta[nome]
            print('%s: AUC %.3f %s' % (nome, r['AUC'], ' '.join('%s %.3f' % (q, r[q]) for q in cols)), flush=True)
    migliore = min(scelta, key=lambda n: (scelta[n]['AUC'], n))
    g, rho = (float(x.split()[1]) for x in migliore.split(', '))
    verifica = [prova(c, vpag, rif, freq, {'g': g, 'rho': rho}, s, 100 + s, con_pagella=(s == SEMI_VERIFICA[0])) for s in SEMI_VERIFICA]
    auc = statistics.mean(x['AUC'] for x in verifica)
    esito = 'indistinguibile' if auc <= 0.6 else 'architettura migliore' if auc <= RIFERIMENTO - 0.05 else 'non migliore'
    pg = verifica[0]['pagella_e224']
    print('scelta %s: verifica AUC %s (media %.3f) | pagella %d/18, riga %s, mancano %s -> %s' % (
        migliore, [round(x['AUC'], 3) for x in verifica], auc, pg['pagella'], pg['riga'], pg['mancano'], esito), flush=True)
    ris.update([('scelta_seme_1', scelta), ('migliore', migliore), ('verifica', verifica), ('AUC_verifica', auc), ('riferimento_e235', RIFERIMENTO), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e236_due_fonti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = ris['Voynich']
    md = ['# e236 — Generatore a due fonti: parole frequenti esatte e varianti nuove', '',
          'Candidate esatte dalle frequenze del manoscritto con probabilità g, altrimenti varianti con almeno una modifica di parole delle righe '
          'recenti (probabilità ρ) o del manoscritto; niente serbatoio di pagina; σ 0,09 e prefissi π 0,30 dopo la generazione. AUC del '
          "discriminatore dell'e231. Riferimento (e235): %.3f. Preregistrazione: `preregistrazioni/e236.md`." % RIFERIMENTO, '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media |', '|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s |' % ' | '.join('%.3f' % v[q] for q in cols)]
    for n, r in scelta.items():
        md.append('| %s, seme 1 | %.3f | %s |' % (n, r['AUC'], ' | '.join('%.3f' % r[q] for q in cols)))
    md.append('| %s, semi 2–3 | %.3f | %s |' % (migliore, auc, ' | '.join('%.3f' % statistics.mean(x[q] for x in verifica) for q in cols)))
    md += ['', 'Pagella dell\'e224 sulla scelta (seme 2): %d/18, riga riprodotta: %s; mancano: %s.' % (pg['pagella'], 'sì' if pg['riga'] else 'no', ', '.join(pg['mancano']) or 'nessuna'),
           '', 'Caratteristiche più pesanti che restano (seme 2; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e236_due_fonti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
