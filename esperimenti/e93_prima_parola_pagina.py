# -*- coding: utf-8 -*-
"""Esperimento 93: la prima parola di riga e' legata al vocabolario della pagina come le altre?

Preregistrazione: preregistrazioni/e93.md. Scrive risultati/e93_prima_parola_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 93, 200
CLASSI = ('prima', 'seconda', 'interne', 'ultima')


def classi_riga(ini, ps):
    out = []
    n = len(ps)
    for i, w in enumerate(ps):
        if not trascrizione.pulita(w):
            continue
        if i == 0:
            c = None if ini else 'prima'
        elif i == n - 1:
            c = 'ultima'
        elif i == 1:
            c = 'seconda'
        elif 2 <= i <= n - 3:
            c = 'interne'
        else:
            c = None
        out.append((c, w))
    return out


def quote(pagine):
    """pagine: liste di (ini, parole). -> {classe: quota di occorrenze il cui tipo compare in un'altra riga della pagina}."""
    acc = defaultdict(lambda: [0, 0])
    for righe in pagine:
        conti = [Counter(w for w in ps if trascrizione.pulita(w)) for _, ps in righe]
        totale = Counter()
        for c in conti:
            totale.update(c)
        for (ini, ps), c_riga in zip(righe, conti):
            for c, w in classi_riga(ini, ps):
                if c is None:
                    continue
                acc[c][0] += (totale[w] - c_riga[w]) > 0
                acc[c][1] += 1
    return {c: a[0] / a[1] for c, a in acc.items()}


def misura(pagine, rnd):
    reale = quote(pagine)
    righe = [r for p in pagine for r in p]
    dim = [len(p) for p in pagine]
    nulli = defaultdict(list)
    for _ in range(RIMESCOLAMENTI):
        rr = righe[:]
        rnd.shuffle(rr)
        nuove, i = [], 0
        for d in dim:
            nuove.append(rr[i:i + d])
            i += d
        for c, x in quote(nuove).items():
            nulli[c].append(x)
    out = OrderedDict()
    for c in CLASSI:
        m, s = statistics.mean(nulli[c]), statistics.pstdev(nulli[c])
        out[c] = OrderedDict([('reale', reale[c]), ('attesa', m), ('legame', reale[c] / m), ('z', (reale[c] - m) / s if s else None)])
    return out


def pagine_voynich(lingua=None):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        if r.parole:
            per.setdefault(r.pagina, []).append((bool(r.inizio_par), list(r.parole)))
    return list(per.values())


def main():
    t = OrderedDict()
    t['Voynich'] = pagine_voynich()
    t['Voynich A'] = pagine_voynich('A')
    t['Voynich B'] = pagine_voynich('B')
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    t['Timm e Schinner, seme 19'] = [ts[i:i + 29] for i in range(0, len(ts), 29)]
    ris = OrderedDict()
    for nome, pagine in t.items():
        r = misura(pagine, random.Random(SEME))
        ris[nome] = r
        print('%-28s %s' % (nome, ' | '.join('%s %.3f/%.3f = %.2f (z %.1f)' % (c, r[c]['reale'], r[c]['attesa'], r[c]['legame'], r[c]['z'] or 0)
                                             for c in CLASSI)), flush=True)
    with open(os.path.join(RISULTATI, 'e93_prima_parola_pagina.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e93 — La prima parola di riga è legata alla pagina?', '',
           'Legame alla pagina = quota di occorrenze il cui tipo compare in un\'altra riga della stessa pagina, divisa per '
           'l\'attesa (%d rimescolamenti delle righe fra le pagine); z fra parentesi. Preregistrazione: '
           '`preregistrazioni/e93.md`.' % RIMESCOLAMENTI, '',
           '| testo | prima | seconda | interne | ultima |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %s |' % (nome, ' | '.join('%.2f (%.1f)' % (r[c]['legame'], r[c]['z'] or 0) for c in CLASSI)))
    with open(os.path.join(RISULTATI, 'e93_prima_parola_pagina.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
