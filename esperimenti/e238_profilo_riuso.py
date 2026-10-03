# -*- coding: utf-8 -*-
"""Esperimento 238: generatore le cui candidate seguono il profilo di riuso della pagina misurato nell'e237 (R
ripetizione dalla pagina, V variante di una parola della pagina, F frequente, A attestata, N nuova); spezzature e
prefissi staccati dopo la generazione. Discriminatore dell'e231, profilo dell'e237, pagella dell'e224.

Preregistrazione: preregistrazioni/e238.md. Scrive risultati/e238_profilo_riuso.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUOTE = OrderedDict([('R', 0.319), ('V', 0.375), ('F', 0.072), ('A', 0.091), ('N', 0.143)])
SEMI, RIGHE_INDIETRO, K, LAM, ETA, NU, RIFERIMENTO = (2, 3), 3, 8, 1.0, 1.0, 0.4, 0.889
_TOP = {}


def frequenti(c, lingua):
    if lingua not in _TOP:
        gt, gp = e232.globali(c, lingua, 1.0)
        coppie = sorted(zip(gp, gt), reverse=True)[:200]
        _TOP[lingua] = ([w for _, w in coppie], [p for p, _ in coppie])
    return _TOP[lingua]


def genera(c, seme):
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    classi, pesi_classi = list(QUOTE), list(QUOTE.values())
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in c['P'].items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        gt, gp = e232.globali(c, lingua, 1.0)
        ft, fp = frequenti(c, lingua)
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
                pagina = [w for r in ultime for w in r] + [w for w in riga if trascrizione.pulita(w)]
                cand = []
                for _ in range(K):
                    cl = rnd.choices(classi, pesi_classi)[0]
                    if cl in ('R', 'V') and not pagina:
                        cl = 'F'
                    if cl == 'R':
                        cand.append(rnd.choice(pagina))
                    elif cl == 'V':
                        cand.append(e234.forza_variante(rnd.choice(pagina), mod, rnd, NU, att, Dv))
                    elif cl == 'F':
                        cand.append(rnd.choices(ft, fp)[0])
                    elif cl == 'A':
                        cand.append(rnd.choices(gt, gp)[0])
                    else:
                        cand.append(e234.forza_variante(rnd.choices(gt, gp)[0], mod, rnd, NU, att, Dv))
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
            ultime = (ultime + [[w for w in riga if trascrizione.pulita(w)]])[-RIGHE_INDIETRO:]
            righe.append((pag, ini, riga))
    return righe


def main():
    c = e224.contesto()
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    freq = Counter(c['voy'])
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    ris = OrderedDict([('Voynich', e234.descrittive(OrderedDict((p, rr) for p, (_, rr) in vpag.items()))),
                       ('profilo_Voynich', e237.profilo(OrderedDict((p, rr) for p, (_, rr) in vpag.items())))])
    verifica = []
    for s in SEMI:
        rr = e236.dopo(genera(c, s), freq, 100 + s)
        gp = e232.pagine_di(rr)
        r = e231.confronto(vpag, gp, rif)
        r.update(e234.descrittive(gp))
        r['profilo'] = e237.profilo(gp)
        if s == SEMI[0]:
            r['pagella_e224'] = e236.pagella(c, rr)
        verifica.append(r)
        print('seme %d: AUC %.3f %s | profilo %s' % (s, r['AUC'], ' '.join('%s %.3f' % (k, r[k]) for k in cols),
                                                   {k: round(v, 3) for k, v in r['profilo'].items() if k in e237.CLASSI}), flush=True)
    auc = statistics.mean(x['AUC'] for x in verifica)
    esito = 'indistinguibile' if auc <= 0.6 else 'migliore' if auc <= RIFERIMENTO - 0.05 else 'non migliore'
    pg = verifica[0]['pagella_e224']
    ris.update([('quote', QUOTE), ('verifica', verifica), ('AUC_verifica', auc), ('riferimento_e235', RIFERIMENTO), ('esito', esito)])
    print('AUC media %.3f | pagella %d/18 riga %s mancano %s -> %s' % (auc, pg['pagella'], pg['riga'], pg['mancano'], esito), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e238_profilo_riuso.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v, pv = ris['Voynich'], ris['profilo_Voynich']
    md = ['# e238 — Un generatore che segue il profilo di riuso della pagina', '',
          "Candidate estratte con le quote dell'e237 (R %.3f, V %.3f, F %.3f, A %.3f, N %.3f), fonti dalle ultime %d righe; σ 0,09 e prefissi "
          "π 0,30 dopo la generazione. AUC del discriminatore dell'e231 sui semi 2–3; riferimento (e235) %.3f. Preregistrazione: "
          '`preregistrazioni/e238.md`.' % (tuple(QUOTE.values()) + (RIGHE_INDIETRO, RIFERIMENTO)), '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s | %s |' % (' | '.join('%.3f' % v[k] for k in cols), ' | '.join('%.1f%%' % (100 * pv[k]) for k in e237.CLASSI))]
    for s, r in zip(SEMI, verifica):
        md.append('| seme %d | %.3f | %s | %s |' % (s, r['AUC'], ' | '.join('%.3f' % r[k] for k in cols),
                                                  ' | '.join('%.1f%%' % (100 * r['profilo'][k]) for k in e237.CLASSI)))
    md += ['', 'AUC media: %.3f. Pagella dell\'e224 (seme 2): %d/18, riga riprodotta: %s; mancano: %s.' % (
        auc, pg['pagella'], 'sì' if pg['riga'] else 'no', ', '.join(pg['mancano']) or 'nessuna'), '',
           'Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e238_profilo_riuso.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
