# -*- coding: utf-8 -*-
"""Esperimento 94: la seconda parola di riga preferisce ch/sh oltre quanto prevedono le giunture?

Preregistrazione: preregistrazioni/e94.md. Scrive risultati/e94_seconda_posizione.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RICAMPIONI, MIN_PAROLE = 94, 1000, 5
BANCHI = {'ch', 'sh'}
D = e71.D


def righe_utili(righe):
    return [ps for ini, ps in righe if not ini and len(ps) >= MIN_PAROLE]


def tabella(righe):
    t = defaultdict(Counter)
    for ps in righe:
        for a, b in zip(ps[2:-3], ps[3:-2]):
            if trascrizione.pulita(a) and trascrizione.pulita(b):
                t[D(a)[-1]][D(b)[0]] += 1
    return t


def voci(righe, t, k):
    """Per ogni riga: (1 se la parola in posizione k comincia per ch/sh, probabilita' prevista)."""
    out = []
    for ps in righe:
        a, b = ps[k - 2], ps[k - 1]
        if not (trascrizione.pulita(a) and trascrizione.pulita(b)):
            continue
        fin = D(a)[-1]
        tot = sum(t[fin].values())
        if not tot:
            continue
        out.append((D(b)[0] in BANCHI, sum(t[fin][g] for g in BANCHI) / tot))
    return out


def rapporto(vv):
    return sum(o for o, _ in vv) / sum(p for _, p in vv)


def misura(righe):
    rr = righe_utili(righe)
    t = tabella(rr)
    out = OrderedDict()
    for k in (2, 3):
        vv = voci(rr, t, k)
        rnd = random.Random(SEME)
        boot = sorted(rapporto([vv[rnd.randrange(len(vv))] for _ in vv]) for _ in range(RICAMPIONI))
        out['posizione %d' % k] = OrderedDict([
            ('n', len(vv)), ('osservata', sum(o for o, _ in vv) / len(vv)), ('prevista', sum(p for _, p in vv) / len(vv)),
            ('rapporto', rapporto(vv)), ('ic95', (boot[int(0.025 * RICAMPIONI)], boot[int(0.975 * RICAMPIONI) - 1]))])
    return out


def voynich(quale='ZL', lingua=None):
    return [(bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi(quale), lingua=lingua) if r.parole]


def main():
    t = OrderedDict()
    t['Voynich ZL'] = voynich('ZL')
    t['Voynich IT'] = voynich('IT')
    t['Voynich ZL, lingua A'] = voynich('ZL', 'A')
    t['Voynich ZL, lingua B'] = voynich('ZL', 'B')
    t['Timm e Schinner, seme 19'] = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    ris = OrderedDict()
    for nome, righe in t.items():
        r = misura(righe)
        ris[nome] = r
        print('%-28s %s' % (nome, ' | '.join('%s: oss %.3f prev %.3f rapporto %.2f [%.2f, %.2f] (n %d)' % (
            k, x['osservata'], x['prevista'], x['rapporto'], x['ic95'][0], x['ic95'][1], x['n']) for k, x in r.items())), flush=True)
    conferma = all(ris[n]['posizione 2']['ic95'][0] > 1.15 and
                   (ris[n]['posizione 3']['ic95'][0] <= 1 <= ris[n]['posizione 3']['ic95'][1] or ris[n]['posizione 3']['ic95'][1] < 1.1)
                   for n in ('Voynich ZL', 'Voynich IT'))
    ris['confermato'] = conferma
    print('confermato:', conferma)
    with open(os.path.join(RISULTATI, 'e94_seconda_posizione.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e94 — La seconda parola preferisce ch/sh oltre le giunture?', '',
           'Quota di parole in ch/sh osservata e prevista dalla tabella delle giunture (fine della parola precedente); '
           'intervallo bootstrap al 95%%. Preregistrazione: `preregistrazioni/e94.md`.', '',
           '| testo | posizione | n | osservata | prevista | rapporto | IC 95% |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        for k, x in r.items():
            out.append('| %s | %s | %d | %.3f | %.3f | %.2f | %.2f–%.2f |' % (nome, k, x['n'], x['osservata'], x['prevista'], x['rapporto'], x['ic95'][0], x['ic95'][1]))
    out += ['', 'Confermato: **%s**.' % ('sì' if conferma else 'no')]
    with open(os.path.join(RISULTATI, 'e94_seconda_posizione.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
