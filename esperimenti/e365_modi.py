# -*- coding: utf-8 -*-
"""Esperimento 365: nelle righe con forme nuove, le altre parole riprendono meno dalle 2 righe sopra? (correlazione fra
righe, nullo con le forme nuove rimescolate fra le righe del paragrafo). Descrittiva: posizione delle forme nuove.

Preregistrazione: preregistrazioni/e365.md. Scrive risultati/e365_modi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e350_sessioni as e350
import e356_eredita as e356

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(365)
    from scipy.stats import spearmanr
    pag = e341.pagine()
    pars = [p for pp in pag.values() for p in pp]
    freq = Counter(w for p in pars for r in p for w in r)
    sim = e350.simili_globali(set(freq))
    nuova = {w for w, n in freq.items() if n == 1 and not any(freq[v] >= 20 for v in sim[w] if v != w)}
    dati = []    # (paragrafo, numero di forme nuove, ripresa delle altre)
    pos_n, pos_a = Counter(), Counter()
    for k, par in enumerate(pars):
        for i, r in enumerate(par):
            n = len(r)
            for j, w in enumerate(r):
                (pos_n if w in nuova else pos_a)[e356.posizione(j, n)] += 1
            if i < 2 or n < 4:
                continue
            sopra = par[i - 1] + par[i - 2]
            altre = [w for w in r if freq[w] > 1]
            if not altre:
                continue
            dati.append((k, sum(w in nuova for w in r), statistics.mean(e341.ha_fonte(w, sopra) for w in altre)))
    xs, ys = [d[1] for d in dati], [d[2] for d in dati]
    rho = spearmanr(xs, ys).correlation
    per_par = {}
    for i, d in enumerate(dati):
        per_par.setdefault(d[0], []).append(i)
    nul = []
    for _ in range(1000):
        x2 = list(xs)
        for idx in per_par.values():
            v = [xs[i] for i in idx]
            rnd.shuffle(v)
            for i, val in zip(idx, v):
                x2[i] = val
        nul.append(spearmanr(x2, ys).correlation)
    z = (rho - statistics.mean(nul)) / statistics.pstdev(nul)
    esito = 'due modi di scrittura' if z < -3 else ('nessun legame' if abs(z) < 2 else 'incerto')
    media = lambda c: {k: c[k] / sum(c.values()) for k in ('prima', 'seconda', 'mezzo', 'penultima', 'ultima')}
    out = OrderedDict([('righe', len(dati)), ('spearman', rho), ('nullo', statistics.mean(nul)), ('z', z), ('esito', esito),
                       ('posizione_forme_nuove', media(pos_n)), ('posizione_altre_parole', media(pos_a)),
                       ('ripresa_media_righe_senza_forme_nuove', statistics.mean(y for x, y in zip(xs, ys) if x == 0)),
                       ('ripresa_media_righe_con_2_o_piu', statistics.mean(y for x, y in zip(xs, ys) if x >= 2) if any(x >= 2 for x in xs) else None)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e365_modi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e365 — Due modi di scrittura per riga: copiare o inventare?', '', 'Preregistrazione: `preregistrazioni/e365.md`.', '',
          '- %d righe. Spearman fra numero di forme nuove e ripresa delle altre parole: %.3f (nullo %.3f), z %.1f.' % (len(dati), rho, statistics.mean(nul), z),
          '- Ripresa media delle altre parole: righe senza forme nuove %.3f; righe con 2 o più %s.' % (out['ripresa_media_righe_senza_forme_nuove'],
                                                                                                      ('%.3f' % out['ripresa_media_righe_con_2_o_piu']) if out['ripresa_media_righe_con_2_o_piu'] is not None else '–'),
          '- Posizione nella riga (forme nuove / altre): %s.' % ', '.join('%s %.3f/%.3f' % (k, out['posizione_forme_nuove'][k], out['posizione_altre_parole'][k]) for k in out['posizione_forme_nuove']),
          '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e365_modi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
