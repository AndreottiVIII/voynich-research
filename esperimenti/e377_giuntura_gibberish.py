# -*- coding: utf-8 -*-
"""Esperimento 377: informazione mutua fra l'ultimo segno di una parola e il primo della seguente (giuntura) nel
Voynich, nel gibberish scritto a mano, nei testi sensati (Gaskell e Bowern) e in Timm e Schinner; nullo con l'ordine
delle parole rimescolato dentro la riga.

Preregistrazione: preregistrazioni/e377.md. Scrive risultati/e377_giuntura_gibberish.json e .md.
"""
import json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e337_posizione as e337
import e375_coppie as e375

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def coppie(righe):
    return Counter((a[-1], b[0]) for r in righe for a, b in zip(r, r[1:]))


def mi(c):
    n = sum(c.values())
    if not n:
        return 0.0
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k
    return sum(k / n * math.log2(k * n / (sa[a] * sb[b])) for (a, b), k in c.items())


def prova(righe, rnd, perm):
    righe = [r for r in righe if len(r) >= 2]
    c = coppie(righe)
    vero = mi(c)
    nul, somma = [], Counter()
    for _ in range(perm):
        cn = coppie([rnd.sample(r, len(r)) for r in righe])
        nul.append(mi(cn))
        somma.update(cn)
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    ecc = sorted(((c[k] - somma[k] / perm) / math.sqrt(somma[k] / perm + 1), k) for k in c)[::-1][:8]
    return OrderedDict([('righe', len(righe)), ('parole', sum(len(r) for r in righe)), ('I', vero), ('nullo', m), ('E', vero - m),
                        ('z', (vero - m) / sd if sd else 0.0), ('coppie_in_eccesso', ['-%s %s-' % k for _, k in ecc])])


def sottoinsiemi(righe, n_parole, rnd):
    out = []
    buone = [r for r in righe if len(r) >= 2]
    for _ in range(20):
        ordine = rnd.sample(buone, len(buone))
        prese, n = [], 0
        for r in ordine:
            if n >= n_parole:
                break
            prese.append(r)
            n += len(r)
        out.append(prova(prese, rnd, 100))
    return OrderedDict([('E_mediana', statistics.median(x['E'] for x in out)), ('z_mediana', statistics.median(x['z'] for x in out))])


def main():
    rnd = random.Random(377)
    voy = [r for p in e375.voynich() for r in p]
    n_voy = sum(len(r) for r in voy)
    sens = e375.testi_zip('meaningful.zip', lambda n: '/texts/' in n or n.startswith('texts/'))
    gib = e375.testi_zip('gibberish_transcriptions.zip', lambda n: True)
    corpi = OrderedDict([('Voynich', voy)])
    for cat in ('Historical', 'Modern', 'Conlangs'):
        tt = [t for k, t in sens.items() if k.startswith(cat)]
        corpi['testi sensati: %s' % cat] = [r for p in e375.a_pagine(tt, quota=n_voy / len(tt)) for r in p]
    corpi['gibberish umano'] = [r for t in gib.values() for r in t]
    corpi['Timm e Schinner, seme 1'] = [[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]
    per_autore = defaultdict(list)
    for k, t in gib.items():
        m = re.search(r'-\s*([A-Za-z]{2})', k)
        per_autore[m.group(1) if m else '?'] += t
    for a in sorted(per_autore):
        corpi['gibberish, autore %s' % a] = per_autore[a]
    ris = OrderedDict()
    for nome, righe in corpi.items():
        ris[nome] = prova(righe, rnd, 1000)
        print(nome, json.dumps(ris[nome], ensure_ascii=False, default=float), flush=True)
    n_gib = ris['gibberish umano']['parole']
    for nome in ('Voynich', 'testi sensati: Historical', 'testi sensati: Modern', 'testi sensati: Conlangs', 'Timm e Schinner, seme 1'):
        ris[nome]['a_parita_col_gibberish'] = sottoinsiemi(corpi[nome], n_gib, rnd)
        print(nome, 'a parità', json.dumps(ris[nome]['a_parita_col_gibberish'], default=float), flush=True)
    G, Vp = ris['gibberish umano'], ris['Voynich']['a_parita_col_gibberish']
    if G['z'] > 3:
        esito = 'la giuntura c\'è anche nel gibberish umano' if G['E'] >= 0.5 * Vp['E_mediana'] else 'giuntura più debole nel gibberish umano'
    elif G['z'] < 2 and Vp['z_mediana'] > 3:
        esito = 'la giuntura è propria del Voynich'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e377_giuntura_gibberish.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e377 — La giuntura fra parole nel gibberish scritto a mano', '', 'Preregistrazione: `preregistrazioni/e377.md`. I = informazione mutua (bit) fra ultimo segno di una parola e primo della seguente; nullo: parole rimescolate nella riga.', '',
          '| testo | parole | I | nullo | E | z | a parità col gibberish: E | z | coppie in eccesso |', '|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        p = x.get('a_parita_col_gibberish')
        md.append('| %s | %d | %.4f | %.4f | %.4f | %.1f | %s | %s | %s |' % (k, x['parole'], x['I'], x['nullo'], x['E'], x['z'],
                  '%.4f' % p['E_mediana'] if p else '', '%.1f' % p['z_mediana'] if p else '', ', '.join(x['coppie_in_eccesso'])))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e377_giuntura_gibberish.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
