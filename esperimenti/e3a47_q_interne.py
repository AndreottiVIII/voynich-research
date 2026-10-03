# -*- coding: utf-8 -*-
"""Esperimento e3a47: il segno prima di una q interna nelle parole uniche e' una finale V (-y, -o, -d) piu' spesso della
quota di finali V fra parole separate? Test binomiale.

Preregistrazione: preregistrazioni/e3a47.md. Scrive risultati/e3a47_q_interne.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

from scipy.stats import binomtest

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}


def main():
    righe = []
    tok = Counter()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        righe.append(ws)
        tok.update(ws)
    uniche = [w for w, n in tok.items() if n == 1]
    prima = Counter()
    esempi = []
    for w in uniche:
        for i in range(1, len(w)):
            if w[i] == 'q':
                prima[w[i - 1]] += 1
                if w[i - 1] in V or w[i - 1] in C:
                    esempi.append(''.join(w))
    k = sum(prima[s] for s in V)
    n = k + sum(prima[s] for s in C)
    fa = Counter()
    fb = Counter()
    for ws in righe:
        for a, b in zip(ws, ws[1:]):
            fa[a[-1]] += 1
            if b[0] == 'q':
                fb[a[-1]] += 1
    qa = sum(fa[s] for s in V) / (sum(fa[s] for s in V) + sum(fa[s] for s in C))
    qb = sum(fb[s] for s in V) / (sum(fb[s] for s in V) + sum(fb[s] for s in C))
    if n < 15:
        esito = 'non decidibile (meno di 15 q interne dopo V o C)'
        p = None
    else:
        p = binomtest(k, n, qa, alternative='greater').pvalue
        esito = 'le unioni interne seguono il raccordo' if p < 0.01 else ('no' if p > 0.1 else 'incerto')
    out = OrderedDict([('parole_uniche', len(uniche)), ('q_interne_per_segno_prima', dict(prima.most_common())), ('k_dopo_V', k), ('n_dopo_V_o_C', n),
                       ('quota_interna_V', k / n if n else None), ('riferimento_A', qa), ('riferimento_B', qb), ('p', p), ('esempi', esempi[:25]), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a47_q_interne.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a47 — Le q dentro le parole uniche seguono la regola di raccordo?', '', 'Preregistrazione: `preregistrazioni/e3a47.md`.', '',
          'Parole uniche: %d. Segno prima delle q interne: %s.' % (len(uniche), ', '.join('%s %d' % kv for kv in prima.most_common())), '',
          'q interne dopo V o C: %d, di cui dopo V %d (%.0f%%). Riferimento A (quota di V fra le finali, tutte le coppie): %.0f%%. Riferimento B (davanti a q-): %.0f%%. Test binomiale contro A: p %s.' % (
              n, k, 100 * k / n if n else 0, 100 * qa, 100 * qb, '%.2g' % p if p is not None else 'n.d.'), '',
          'Esempi: %s.' % ', '.join(esempi[:25]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a47_q_interne.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
