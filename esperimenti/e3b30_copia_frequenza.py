# -*- coding: utf-8 -*-
"""Esperimento e3b30: eccesso di ripresa dalla riga sopra (e3a79) per classe di frequenza della parola.

Preregistrazione: preregistrazioni/e3b30.md. Scrive risultati/e3b30_copia_frequenza.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 1000
CLASSI = ('unica', 'rara', 'media', 'frequente')


def classe(n):
    return 'unica' if n == 1 else ('rara' if n <= 9 else ('media' if n <= 49 else 'frequente'))


def paragrafo(par, freq):
    sim = e385.simili_unita(par)
    insiemi = [set(r) for r in par]
    out = defaultdict(lambda: [0.0, 0.0, 0])
    for i in range(1, len(par)):
        altre = [j for j in range(len(par)) if j not in (i, i - 1)]
        if not altre:
            continue
        for w in par[i]:
            if len(w) < 3:
                continue
            c = classe(freq[w])
            x = out[c]
            x[0] += bool(sim[w] & insiemi[i - 1])
            x[1] += sum(bool(sim[w] & insiemi[j]) for j in altre) / len(altre)
            x[2] += 1
    return out


def somma(blocchi):
    tot = defaultdict(lambda: [0.0, 0.0, 0])
    for b in blocchi:
        for c, (o, a, n) in b.items():
            t = tot[c]
            t[0] += o
            t[1] += a
            t[2] += n
    return {c: ((o - a) / n if n else None, (o / a - 1) if a else None, n) for c, (o, a, n) in tot.items()}


def main():
    rnd = random.Random(3230)
    pars = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            rr = [r for r in rr if r]
            if len(rr) >= 3:
                pars.append(rr)
    freq = Counter(w for par in pars for r in par for w in r)
    blocchi = [paragrafo(p, freq) for p in pars]
    s = somma(blocchi)
    boot = defaultdict(list)
    for _ in range(BOOT):
        sb = somma([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi])
        for c, v in sb.items():
            if v[1] is not None:
                boot[c].append(v[1])
    ic = {c: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for c, v in boot.items()}
    ris = OrderedDict((c, OrderedDict([('parole', s[c][2]), ('eccesso', s[c][0]), ('eccesso_relativo', s[c][1]), ('IC95_relativo', ic.get(c))])) for c in CLASSI if c in s)
    r, f = ris.get('rara'), ris.get('frequente')
    if r and f and r['IC95_relativo'][0] > f['IC95_relativo'][1]:
        esito = 'la copia favorisce le parole rare'
    elif r and f and f['IC95_relativo'][0] > r['IC95_relativo'][1]:
        esito = 'favorisce le frequenti'
    else:
        esito = 'nessuna preferenza'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b30_copia_frequenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b30 — Dalla riga sopra si riprendono di più le parole rare o quelle frequenti?', '', 'Preregistrazione: `preregistrazioni/e3b30.md`.', '',
          '| classe di frequenza | parole | eccesso per parola | eccesso relativo | IC 95% relativo |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.2f | %+.2f – %+.2f |' % (c, x['parole'], x['eccesso'], x['eccesso_relativo'], x['IC95_relativo'][0], x['IC95_relativo'][1]) for c, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b30_copia_frequenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
