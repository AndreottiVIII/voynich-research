# -*- coding: utf-8 -*-
"""Esperimento 204: le parole d'erbario confinate su una sola pagina ricompaiono nelle ricette (sezione S) piu' di
parole ugualmente frequenti ma sparse?

Preregistrazione: preregistrazioni/e204.md. Scrive risultati/e204_rimandi_ricette.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, ESTRAZIONI = 204, 2000


def main():
    rnd = random.Random(SEME)
    pagine_h = defaultdict(set)
    freq_h = Counter()
    vocab = defaultdict(set)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        for w in r.parole:
            if not trascrizione.pulita(w):
                continue
            vocab[r.sezione].add(w)
            if r.sezione == 'H':
                freq_h[w] += 1
                pagine_h[w].add(r.pagina)
    locali = [w for w, c in freq_h.items() if c >= 2 and len(pagine_h[w]) == 1]
    per_freq = defaultdict(list)
    for w, c in freq_h.items():
        if c >= 2 and len(pagine_h[w]) >= 2:
            per_freq[c].append(w)
    locali = [w for w in locali if per_freq.get(freq_h[w])]
    ris = OrderedDict([('parole_locali', len(locali))])
    for sez in ('S', 'P'):
        vero = sum(w in vocab[sez] for w in locali) / len(locali)
        nulli = []
        for _ in range(ESTRAZIONI):
            usate, q = set(), 0
            for w in locali:
                cand = [x for x in per_freq[freq_h[w]] if x not in usate] or per_freq[freq_h[w]]
                x = rnd.choice(cand)
                usate.add(x)
                q += x in vocab[sez]
            nulli.append(q / len(locali))
        m = statistics.mean(nulli)
        p = (1 + sum(n >= vero for n in nulli)) / (1 + ESTRAZIONI)
        ris[sez] = OrderedDict([('quota_locali', vero), ('quota_controllo', m), ('rapporto', vero / m if m else None), ('p_una_coda', p)])
        print('%s: locali %.3f, controllo %.3f, rapporto %.2f, p %.4f' % (sez, vero, m, vero / m if m else 0, p), flush=True)
    s = ris['S']
    if s['p_una_coda'] < 0.01 and (s['rapporto'] or 0) >= 1.5:
        esito = 'rimandi alle piante'
    elif s['p_una_coda'] > 0.05 or s['quota_locali'] < s['quota_controllo']:
        esito = 'nessun rimando'
    else:
        esito = 'incerto'
    ris['esito'] = esito
    print('%d parole locali | %s' % (len(locali), esito))
    with open(os.path.join(RISULTATI, 'e204_rimandi_ricette.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e204 — Le ricette rimandano alle piante?', '', '%d parole d\'erbario confinate su una sola pagina, contro parole di pari frequenza sparse. '
           'Preregistrazione: `preregistrazioni/e204.md`.' % len(locali), '', '| sezione | quota locali | quota controllo | rapporto | p |', '|---|---|---|---|---|']
    for sez, nome in (('S', 'ricette (S)'), ('P', 'farmacia (P)')):
        r = ris[sez]
        out.append('| %s | %.3f | %.3f | %.2f | %.4f |' % (nome, r['quota_locali'], r['quota_controllo'], r['rapporto'] or 0, r['p_una_coda']))
    out += ['', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e204_rimandi_ricette.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
