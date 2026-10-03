# -*- coding: utf-8 -*-
"""Esperimento 357: la quota di parole uniche per bifoglio varia oltre sezione e lingua? E' fatta di "errori" (a una
modifica da parole frequenti) o di forme nuove? Legami descrittivi con lunghezza delle parole e posizione nel libro.

Preregistrazione: preregistrazioni/e357.md. Scrive risultati/e357_inventiva.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def main():
    rnd = random.Random(357)
    testa = e308.intestazioni()
    tok, strato = [], {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole and testa.get(r.pagina, {}).get('Q'):
            for w in r.parole:
                if trascrizione.pulita(w):
                    tok.append((r.pagina, w))
            strato.setdefault(r.pagina, '%s-%s' % (r.sezione or '?', r.lingua or '?'))
    freq = Counter(w for _, w in tok)
    sim = e350.simili_globali(set(freq))
    tipo = {}
    for w, n in freq.items():
        if n == 1:
            tipo[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
    bif = defaultdict(list)
    for p, w in tok:
        bif[(testa[p]['Q'], testa[p]['B'])].append((p, w))
    grandi = [b for b, ws in bif.items() if len(ws) >= 150]
    st_b = {b: Counter(strato[p] for p, _ in bif[b]).most_common(1)[0][0] for b in grandi}
    per_st = defaultdict(list)
    for b in grandi:
        per_st[st_b[b]].append(b)

    def quote(etich):
        """etich: {bifoglio: lista di categorie per parola} -> {bifoglio: (uniche, errori, nuove)}."""
        out = {}
        for b, cs in etich.items():
            n = len(cs)
            out[b] = (sum(c != '-' for c in cs) / n, sum(c == 'errore' for c in cs) / n, sum(c == 'nuova' for c in cs) / n)
        return out

    def var_scarti(q, k):
        tot = []
        for st, bs in per_st.items():
            if len(bs) < 2:
                continue
            m = statistics.mean(q[b][k] for b in bs)
            tot += [q[b][k] - m for b in bs]
        return statistics.mean(x * x for x in tot)
    etich = {b: [tipo.get(w, '-') for _, w in bif[b]] for b in grandi}
    q0 = quote(etich)
    vero = [var_scarti(q0, k) for k in range(3)]
    nul = [[] for _ in range(3)]
    for _ in range(PERM):
        e2 = {}
        for st, bs in per_st.items():
            tutte = [c for b in bs for c in etich[b]]
            rnd.shuffle(tutte)
            i = 0
            for b in bs:
                n = len(etich[b])
                e2[b] = tutte[i:i + n]
                i += n
        q2 = quote(e2)
        for k in range(3):
            nul[k].append(var_scarti(q2, k))
    res = OrderedDict()
    for k, nome in enumerate(('uniche', 'errori', 'forme nuove')):
        m, sd = statistics.mean(nul[k]), statistics.pstdev(nul[k])
        res[nome] = OrderedDict([('varianza_scarti', vero[k]), ('nullo', m), ('rapporto', vero[k] / m if m else None), ('z', (vero[k] - m) / sd if sd else 0.0)])
    zi = res['uniche']['z']
    esito_i = 'inventiva oltre la sezione' if zi > 3 else ('solo sezione e lingua' if zi < 2 else 'incerto')
    ze, zn = res['errori']['z'], res['forme nuove']['z']
    esito_ii = 'tutte e due' if (ze > 3 and zn > 3) else ('fatta di errori' if ze > 3 else ('fatta di forme nuove' if zn > 3 else 'nessuna delle due'))
    from scipy.stats import spearmanr
    lun = {b: statistics.mean(len(D(w)) for _, w in bif[b]) for b in grandi}
    pos = {b: statistics.mean(testa[p]['ordine'] for p, _ in bif[b]) for b in grandi}
    xs = [q0[b][0] for b in grandi]
    desc = OrderedDict([('spearman_uniche_lunghezza', spearmanr(xs, [lun[b] for b in grandi]).correlation),
                        ('spearman_uniche_posizione', spearmanr(xs, [pos[b] for b in grandi]).correlation)])
    estremi = sorted(grandi, key=lambda b: -q0[b][0])
    elenco = [('%s-%s' % b, st_b[b], round(q0[b][0], 3), round(q0[b][1], 3), round(q0[b][2], 3)) for b in estremi[:6] + estremi[-6:]]
    out = OrderedDict([('bifogli', len(grandi)), ('i_ii', res), ('esito_i', esito_i), ('esito_ii', esito_ii), ('descrittive', desc), ('piu_e_meno_inventivi', elenco)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:1200], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e357_inventiva.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e357 — Che cosa rende "inventiva" una sessione', '', 'Preregistrazione: `preregistrazioni/e357.md`. %d bifogli con almeno 150 parole.' % len(grandi), '',
          '| quota | varianza degli scarti dallo strato | nullo | rapporto | z |', '|---|---|---|---|---|']
    for k, v in res.items():
        md.append('| %s | %.7f | %.7f | %.2f | %.1f |' % (k, v['varianza_scarti'], v['nullo'], v['rapporto'], v['z']))
    md += ['', 'Esito (i): **%s**. Esito (ii): **%s**.' % (esito_i, esito_ii), '',
           'Spearman fra quota di uniche e lunghezza media delle parole %.2f; e posizione nel libro %.2f.' % (desc['spearman_uniche_lunghezza'], desc['spearman_uniche_posizione']), '',
           'I bifogli più e meno inventivi (bifoglio, strato, uniche, errori, forme nuove): %s.' % '; '.join('%s %s %.3f/%.3f/%.3f' % x for x in elenco)]
    open(os.path.join(RISULTATI, 'e357_inventiva.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
