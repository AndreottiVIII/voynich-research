# -*- coding: utf-8 -*-
"""Esperimento 390: quota della giuntura spiegata dalle due regole di raccordo (qo- contato come o-; -l e -r fusi) e
contributi delle singole coppie di segni all'informazione mutua, oltre il nullo.

Preregistrazione: preregistrazioni/e390.md. Scrive risultati/e390_scomposizione.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e377_giuntura_gibberish as e377
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 200


def contributi(c):
    n = sum(c.values())
    sa, sb = Counter(), Counter()
    for (a, b), k in c.items():
        sa[a] += k
        sb[b] += k
    return {(a, b): k / n * math.log2(k * n / (sa[a] * sb[b])) for (a, b), k in c.items()}


def prova(per_pag, rnd, dettaglio=False):
    vero_c = Counter(x for xs in per_pag.values() for x in xs)
    vero = e377.mi(vero_c)
    nul, somma = [], defaultdict(float)
    for _ in range(PERM):
        c = Counter()
        for xs in per_pag.values():
            dx = [b for _, b in xs]
            rnd.shuffle(dx)
            c.update((a, b) for (a, _), b in zip(xs, dx))
        nul.append(e377.mi(c))
        if dettaglio:
            for k, v in contributi(c).items():
                somma[k] += v / PERM
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    out = OrderedDict([('coppie', sum(vero_c.values())), ('E', vero - m), ('z', (vero - m) / sd if sd else 0.0)])
    if dettaglio:
        cv = contributi(vero_c)
        ecc = sorted(((cv[k] - somma.get(k, 0.0), k) for k in cv), key=lambda t: -abs(t[0]))[:20]
        out['contributi'] = [['-%s %s-' % k, round(v, 5), vero_c[k]] for v, k in ecc]
    return out


def main():
    rnd = random.Random(390)
    vero, neutra = defaultdict(list), defaultdict(list)
    for st, pag, par, ws, seps in e386.righe():
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            vero[pag].append((a[-1], b[0]))
            fa = 'l|r' if a[-1] in ('l', 'r') else a[-1]
            q = e380.ini_qo(b)
            fb = 'o' if q and q[1] == 'qo' else b[0]
            neutra[pag].append((fa, fb))
    V = prova(vero, rnd, dettaglio=True)
    N = prova(neutra, rnd)
    quota = 1 - N['E'] / V['E']
    esito = 'le due regole sono il grosso della giuntura' if quota > 0.5 else ('la giuntura è fatta anche di molte altre preferenze' if quota < 0.2 else 'una parte importante')
    out = OrderedDict([('vera', V), ('neutralizzata', N), ('quota_spiegata', quota), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e390_scomposizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e390 — Quanta parte della giuntura spiegano le due regole di raccordo?', '', 'Preregistrazione: `preregistrazioni/e390.md`.', '',
          'Giuntura vera: E %.4f (z %.1f, %d coppie). Neutralizzata (*qo*- come *o*-, -*l* e -*r* fusi): E %.4f (z %.1f). Quota spiegata dalle due regole: **%.2f**.' % (V['E'], V['z'], V['coppie'], N['E'], N['z'], quota), '',
          '## Coppie di segni che contano di più (contributo osservato meno atteso, bit)', '', '| coppia | contributo | quante |', '|---|---|---|']
    md += ['| %s | %+.5f | %d |' % tuple(c) for c in V['contributi']]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e390_scomposizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
