# -*- coding: utf-8 -*-
"""Esperimento e3b84: nelle parole riprese dalla riga sopra, quando la scelta della fonte e quella delle parole appena
scritte nella riga sono in conflitto, quale segue lo scriba?

Preregistrazione: preregistrazioni/e3b84.md. Scrive risultati/e3b84_copia_contro_memoria.json e .md.
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
MIN_CONFLITTI = 100


def casi_paragrafo(par, f):
    """[(conflitto?, segue la fonte?)] per un paragrafo (lista di righe di parole)."""
    out = []
    vv = [[f(w) for w in r] for r in par]
    for i in range(1, len(par)):
        sopra = defaultdict(Counter)
        for x in vv[i - 1]:
            if x:
                sopra[x[1]][x[0]] += 1
        riga = vv[i]
        for j in range(2, len(riga)):
            x = riga[j]
            if not x or x[1] not in sopra:
                continue
            cc = sopra[x[1]]
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
    rnd = random.Random(3284)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        per_pag = []
        for pars in pd.values():
            casi = []
            for par in pars:
                pp = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
                pp = [r for r in pp if r]
                for f in e3b62.CV.values():
                    casi += casi_paragrafo(pp, f)
            if casi:
                per_pag.append(casi)

        def quote(pp):
            conf = [s for p in pp for c, s in p if c]
            acc = [s for p in pp for c, s in p if not c]
            return (sum(conf) / len(conf) if conf else None), len(conf), (sum(acc) / len(acc) if acc else None), len(acc)
        qf, nc, qa, na = quote(per_pag)
        boot = sorted(x for x in (quote([per_pag[rnd.randrange(len(per_pag))] for _ in per_pag])[0] for _ in range(BOOT)) if x is not None)
        ris[q] = OrderedDict([('conflitti', nc), ('segue_la_fonte', qf), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]),
                              ('accordi', na), ('uguale_a_fonte_e_memoria', qa)])
        print(q, json.dumps(ris[q]), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['conflitti'] < MIN_CONFLITTI:
        esito = 'dati insufficienti'
    elif z['IC95'][0] > 0.5 and it['segue_la_fonte'] > 0.5:
        esito = 'tiene la grafia della fonte'
    elif z['IC95'][1] < 0.5 and it['segue_la_fonte'] < 0.5:
        esito = 'adatta alle scelte del momento'
    elif z['IC95'][0] <= 0.5 <= z['IC95'][1]:
        esito = 'pari'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b84_copia_contro_memoria.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b84 — Parola ripresa dalla riga sopra: grafia della fonte o scelte del momento?', '', 'Preregistrazione: `preregistrazioni/e3b84.md`.', '',
          '| trascrizione | conflitti | quota che segue la fonte (IC 95%) | senza conflitto: quota uguale a fonte e memoria (casi) |', '|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %.3f (%.3f – %.3f) | %.3f (%d) |' % (q, x['conflitti'], x['segue_la_fonte'], x['IC95'][0], x['IC95'][1], x['uguale_a_fonte_e_memoria'], x['accordi']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b84_copia_contro_memoria.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
