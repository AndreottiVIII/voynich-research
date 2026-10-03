# -*- coding: utf-8 -*-
"""Esperimento e3a58: prevedibilita' dello spazio dalla coppia di segni vicini (F1 sulla seconda meta' delle righe);
probabilita' di spazio negli spazi incerti della ZL.

Preregistrazione: preregistrazioni/e3a58.md. Scrive risultati/e3a58_spazi_prevedibili.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e386_salto_disegno as e386
import e3a55_frequenza_forma as e3a55

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def posizioni(righe):
    """[(prima, dopo, spazio)] per ogni punto fra due segni consecutivi della stessa riga."""
    out = []
    for r in righe:
        s, conf = [], set()
        for w in r:
            if s:
                conf.add(len(s))
            s += list(w)
        out += [(s[i - 1], s[i], i in conf) for i in range(1, len(s))]
    return out


class Regola:
    def __init__(self, pos):
        self.c2, self.c1, self.g = Counter(), Counter(), [0, 0]
        self.n2, self.n1 = Counter(), Counter()
        for a, b, y in pos:
            self.c2[a, b] += y
            self.n2[a, b] += 1
            self.c1[a] += y
            self.n1[a] += 1
            self.g[0] += y
            self.g[1] += 1

    def p(self, a, b):
        if self.n2[a, b]:
            return self.c2[a, b] / self.n2[a, b]
        if self.n1[a]:
            return self.c1[a] / self.n1[a]
        return self.g[0] / self.g[1]


def f1(righe):
    righe = [r for r in righe if r]
    m = len(righe) // 2
    reg = Regola(posizioni(righe[:m]))
    tp = fp = fn = 0
    for a, b, y in posizioni(righe[m:]):
        pr = reg.p(a, b) > 0.5
        tp += pr and y
        fp += pr and not y
        fn += (not pr) and y
    if tp == 0:
        return 0.0
    prec, ric = tp / (tp + fp), tp / (tp + fn)
    return 2 * prec * ric / (prec + ric)


def righe_prime(righe, n=10000):
    out, k = [], 0
    for r in righe:
        if k >= n:
            break
        out.append(list(r))
        k += len(r)
    return out


def incerti():
    """Parte 2: probabilita' media di spazio nelle posizioni con ',', con '.' e senza separatore."""
    posiz = []   # (prima, dopo, tipo) tipo in '.', ',', ''
    for _, _, _, ws, seps in e386.righe():
        # spezza la riga ai salti del disegno; le parole illeggibili interrompono la catena
        blocchi, cur, curs = [], [], []
        for i, w in enumerate(ws):
            sep = seps[i - 1] if i else None
            if w is None or sep == '|':
                if cur:
                    blocchi.append((cur, curs))
                cur, curs = ([], []) if w is None else ([w], [])
                continue
            if cur:
                curs.append(sep)
            cur.append(w)
        if cur:
            blocchi.append((cur, curs))
        for bw, bs in blocchi:
            s, tipo = [], {}
            for j, w in enumerate(bw):
                if s:
                    tipo[len(s)] = bs[j - 1]
                s += list(w)
            posiz += [(s[i - 1], s[i], tipo.get(i, '')) for i in range(1, len(s))]
    reg = Regola([(a, b, t == '.') for a, b, t in posiz if t != ','])
    medie = OrderedDict()
    for t, nome in (('.', 'spazio (.)', ), (',', 'spazio incerto (,)'), ('', 'nessuno spazio')):
        ps = [reg.p(a, b) for a, b, tt in posiz if tt == t]
        medie[nome] = OrderedDict([('posizioni', len(ps)), ('p_media', float(np.mean(ps))),
                                   ('quota_fra_0.3_e_0.7', float(np.mean([0.3 <= p <= 0.7 for p in ps])))])
    m = medie['spazio incerto (,)']['p_media']
    es = 'gli spazi incerti cadono dove la regola è incerta' if 0.3 <= m <= 0.7 else ('come spazi veri' if m > 0.7 else 'come non-spazi')
    return medie, es


def main():
    rnd = random.Random(3158)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(f1(prese))
    ris = OrderedDict([('Voynich', OrderedDict([('f1_sub', sub), ('f1', statistics.median(sub))]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    ris['gibberish umano'] = OrderedDict([('f1', f1(gib))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            rr = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
            ris[k] = OrderedDict([('f1', f1(righe_prime(rr)))])
    ris['Timm e Schinner, seme 1'] = OrderedDict([('f1', f1(righe_prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])))])
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        sens[k.replace('.txt', '')] = f1(righe_prime(t))
    vals = sorted(sens.values())
    m = ris['Voynich']['f1']
    p10, p90 = float(np.percentile(vals, 10)), float(np.percentile(vals, 90))
    es1 = 'spazi più prevedibili che nelle lingue' if m > p90 else ('come le lingue' if m >= p10 else 'meno prevedibili')
    sopra = sum(1 for v in vals if v < m) / len(vals)
    medie, es2 = incerti()
    print(json.dumps(medie, ensure_ascii=False), es1, '/', es2, flush=True)
    out = OrderedDict([('parte1', OrderedDict([('altri', ris), ('lingue', OrderedDict([('minimo', vals[0]), ('p10', p10), ('mediana', float(np.median(vals))), ('p90', p90), ('massimo', vals[-1]), ('quota_lingue_sotto_il_voynich', sopra)])),
                                               ('testi_sensati', OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]))), ('esito', es1)])),
                       ('parte2', OrderedDict([('medie', medie), ('esito', es2)]))])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a58_spazi_prevedibili.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a58 — Dove cade lo spazio si indovina dai due segni vicini? E gli spazi incerti?', '', 'Preregistrazione: `preregistrazioni/e3a58.md`.', '',
          '## Parte 1 — F1 della regola "coppia di segni" sugli spazi', '',
          'Testi sensati: minimo %.3f, 10° percentile %.3f, mediana %.3f, 90° percentile %.3f, massimo %.3f. Il Voynich supera il %.0f%% dei testi sensati.' % (vals[0], p10, float(np.median(vals)), p90, vals[-1], 100 * sopra), '',
          '| testo | F1 |', '|---|---|']
    md += ['| %s | %.3f%s |' % (k, x['f1'], ' (sottoinsiemi: %s)' % ', '.join('%.3f' % v for v in x['f1_sub']) if 'f1_sub' in x else '') for k, x in ris.items()]
    md += ['', '| testo sensato | F1 |', '|---|---|'] + ['| %s | %.3f |' % kv for kv in out['parte1']['testi_sensati'].items()]
    md += ['', 'Esito parte 1: **%s**.' % es1, '', '## Parte 2 — Spazi incerti (ZL)', '', '| posizioni | quante | probabilità media di spazio | quota fra 0,3 e 0,7 |', '|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.3f |' % (k, x['posizioni'], x['p_media'], x['quota_fra_0.3_e_0.7']) for k, x in medie.items()]
    md += ['', 'Esito parte 2: **%s**.' % es2]
    open(os.path.join(RISULTATI, 'e3a58_spazi_prevedibili.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
