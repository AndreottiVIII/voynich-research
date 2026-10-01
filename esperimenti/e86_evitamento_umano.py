# -*- coding: utf-8 -*-
"""Esperimento 86: nel gibberish scritto a mano (Gaskell e Bowern 2022) le righe consecutive evitano di cominciare
con la stessa lettera, come nel Voynich?

Preregistrazione: preregistrazioni/e86.md. Scrive risultati/e86_evitamento_umano.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e41_gibberish as e41
import e83_evitamento_inizi as e83

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 86, 500


def coppie(docs, pos):
    out = []
    for righe in docs:
        for a, b in zip(righe, righe[1:]):
            if len(a) > pos and len(b) > pos:
                out.append((a[pos][0], b[pos][0]))
    return out


def misura(docs, pos, rnd):
    reale = coppie(docs, pos)
    q = sum(a == b for a, b in reale) / len(reale)
    nulli = []
    for _ in range(PERMUTAZIONI):
        mes = []
        for righe in docs:
            rr = list(righe)
            rnd.shuffle(rr)
            mes.append(rr)
        cc = coppie(mes, pos)
        nulli.append(sum(a == b for a, b in cc) / len(cc))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(reale)), ('osservata', q), ('attesa', m), ('S', q / m), ('z', (q - m) / s if s else None)])


def main():
    docs = e41.gibberish()
    testi = OrderedDict()
    testi['gibberish (38 documenti)'] = list(docs.values())
    for lingua, nome in (('English', 'Bibbia inglese, stessa impaginazione'), ('Latin', 'Bibbia latina, stessa impaginazione')):
        testi[nome] = list(e41.impagina_come(docs, lingua).values())
    ris = OrderedDict()
    for nome, dd in testi.items():
        r1 = misura(dd, 0, random.Random(SEME))
        r2 = misura(dd, 1, random.Random(SEME))
        ris[nome] = OrderedDict([('prima_parola', r1), ('seconda_parola', r2)])
        print('%-40s prima: n %4d S %.2f (z %.1f) | seconda: n %4d S %.2f (z %.1f)' % (
            nome, r1['n'], r1['S'], r1['z'] or 0, r2['n'], r2['S'], r2['z'] or 0), flush=True)
    v = e83.misura(e83.pagine('ZL'), 1, e83.primo_eva, random.Random(SEME))
    ris['Voynich (ZL, primo segno; e83)'] = OrderedDict([('prima_parola', v)])
    print('Voynich: S %.2f (z %.1f)' % (v['S'], v['z']), flush=True)
    with open(os.path.join(RISULTATI, 'e86_evitamento_umano.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e86 — Chi inventa un testo evita di cominciare due righe allo stesso modo?', '',
           'S = quota di righe consecutive con la stessa prima lettera, divisa per l\'attesa (%d rimescolamenti delle righe nel '
           'documento). Preregistrazione: `preregistrazioni/e86.md`.' % PERMUTAZIONI, '',
           '| testo | prima parola: coppie | S (z) | seconda parola: coppie | S (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        a = r['prima_parola']
        b = r.get('seconda_parola')
        out.append('| %s | %d | %.2f (%.1f) | %s | %s |' % (nome, a['n'], a['S'], a['z'] or 0, b['n'] if b else '–',
                                                         '%.2f (%.1f)' % (b['S'], b['z'] or 0) if b else '–'))
    with open(os.path.join(RISULTATI, 'e86_evitamento_umano.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
