# -*- coding: utf-8 -*-
"""Esperimento e3b85: e3b84 con la "fonte" presa dalla riga sopra (vicina) o da righe lontane dello stesso paragrafo
(distanza 3 o più); differenza delle quote che seguono la fonte nei conflitti.

Preregistrazione: preregistrazioni/e3b85.md. Scrive risultati/e3b85_copia_controllo.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def casi_paragrafo(par, f, fonte):
    """[(conflitto?, segue la fonte?)]; fonte 'vicina' = riga sopra, 'lontana' = righe a distanza 3 o più."""
    out = []
    vv = [[f(w) for w in r] for r in par]
    for i in range(len(par)):
        if fonte == 'vicina':
            righe = [i - 1] if i >= 1 else []
        else:
            righe = [k for k in range(len(par)) if abs(k - i) >= 3]
        if not righe:
            continue
        sorg = defaultdict(Counter)
        for k in righe:
            for x in vv[k]:
                if x:
                    sorg[x[1]][x[0]] += 1
        riga = vv[i]
        for j in range(2, len(riga)):
            x = riga[j]
            if not x or x[1] not in sorg:
                continue
            cc = sorg[x[1]]
            if len(cc) == 2 and cc[0] == cc[1]:
                continue
            X = cc.most_common(1)[0][0]
            Y = None
            for d in (2, 3):
                k = j - d
                if k >= 0 and riga[k] and riga[k][1] != x[1]:
                    Y = riga[k][0]
                    break
            if Y is None:
                continue
            out.append((X != Y, x[0] == X))
    return out


def main():
    rnd = random.Random(3285)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        per_pag = []
        for pars in pd.values():
            casi = {'vicina': [], 'lontana': []}
            for par in pars:
                pp = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
                pp = [r for r in pp if r]
                for f in e3b62.CV.values():
                    for k in casi:
                        casi[k] += casi_paragrafo(pp, f, k)
            if casi['vicina'] or casi['lontana']:
                per_pag.append(casi)

        def quote(pp):
            out = {}
            for k in ('vicina', 'lontana'):
                conf = [s for p in pp for c, s in p[k] if c]
                out[k] = (sum(conf) / len(conf) if conf else None, len(conf))
            return out
        qq = quote(per_pag)
        boot = []
        for _ in range(BOOT):
            b = quote([per_pag[rnd.randrange(len(per_pag))] for _ in per_pag])
            if b['vicina'][0] is not None and b['lontana'][0] is not None:
                boot.append(b['vicina'][0] - b['lontana'][0])
        boot.sort()
        ris[q] = OrderedDict([('vicina', qq['vicina']), ('lontana', qq['lontana']), ('D', qq['vicina'][0] - qq['lontana'][0]),
                              ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])
        print(q, json.dumps(ris[q]), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95'][0] > 0 and it['D'] > 0:
        esito = 'è copia dalla riga sopra'
    elif z['IC95'][0] <= 0 <= z['IC95'][1]:
        esito = 'è preferenza della parola'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b85_copia_controllo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b85 — Copia dalla riga sopra o preferenza della parola? Controllo con righe lontane', '', 'Preregistrazione: `preregistrazioni/e3b85.md`.', '',
          '| trascrizione | fonte vicina: segue la fonte (conflitti) | fonte lontana: segue la fonte (conflitti) | D (IC 95%) |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %.3f (%d) | %.3f (%d) | %+.3f (%+.3f – %+.3f) |' % (q, x['vicina'][0], x['vicina'][1], x['lontana'][0], x['lontana'][1], x['D'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b85_copia_controllo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
