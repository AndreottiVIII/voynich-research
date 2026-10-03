# -*- coding: utf-8 -*-
"""Esperimento 394: una parola in -l/-r ripresa dalla riga sopra (stesso tronco) segue la finale della fonte o quella
voluta dalla parola che la segue nella nuova riga?

Preregistrazione: preregistrazioni/e394.md. Scrive risultati/e394_fine_adattata.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386
import e392_copia_adattata as e392

RISULTATI = os.path.join(QUI, '..', 'risultati')
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a', 'o', 'y'}


def main():
    rnd = random.Random(394)
    par = OrderedDict()
    for st, pag, npar, ws, seps in e386.righe():
        par.setdefault((pag, npar), []).append((ws, seps))
    ev = []    # (dopo in K, fonte -l, w -l)
    for righe in par.values():
        for i in range(1, len(righe)):
            sopra = defaultdict(set)
            for x in righe[i - 1][0]:
                f = e380.fin_lr(x) if x else None
                if f:
                    sopra[f[0]].add(f[1])
            ws, seps = righe[i]
            for j in range(len(ws) - 1):
                w, b = ws[j], ws[j + 1]
                if not w or not b or seps[j] != '.':
                    continue
                f = e380.fin_lr(w)
                if not f or len(sopra.get(f[0], ())) != 1:
                    continue
                if b[0] in K:
                    cl = True
                elif b[0] in A:
                    cl = False
                else:
                    continue
                ev.append((cl, next(iter(sopra[f[0]])) == 'l', f[1] == 'l'))
    tab = Counter((e[1], e[0], e[2]) for e in ev)
    righe_tab = OrderedDict()
    for fonte in (True, False):
        for dopo in (True, False):
            n = tab[(fonte, dopo, True)] + tab[(fonte, dopo, False)]
            righe_tab['fonte %s, dopo %s' % ('-l' if fonte else '-r', 'K' if dopo else 'A')] = OrderedDict([('eventi', n), ('P_l', tab[(fonte, dopo, True)] / n if n else None)])
    e_dopo = e392.effetto(ev, 0, 1)
    p_dopo = sum(x >= e_dopo for x in e392.nullo(ev, 0, 1, rnd)) / e392.PERM
    e_fon = e392.effetto(ev, 1, 0)
    p_fon = sum(x >= e_fon for x in e392.nullo(ev, 1, 0, rnd)) / e392.PERM
    if p_dopo < 0.01 and p_fon < 0.01:
        esito = 'entrambe le cose'
    elif p_dopo < 0.01:
        esito = 'la fine si adatta alla parola dopo: lo scriba pianifica in avanti'
    elif p_fon < 0.01:
        esito = 'la copia conserva la finale della fonte'
    else:
        esito = 'non deciso'
    out = OrderedDict([('eventi', len(ev)), ('tabella', righe_tab), ('effetto_parola_dopo', e_dopo), ('p_parola_dopo', p_dopo), ('effetto_fonte', e_fon), ('p_fonte', p_fon), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e394_fine_adattata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e394 — La fine di una parola copiata si adatta alla parola che viene dopo?', '', 'Preregistrazione: `preregistrazioni/e394.md`. K = parola dopo in k/t/d/l/s/q; A = in a/o/y.', '',
          '| fonte nella riga sopra | parola dopo | eventi | P(-l) |', '|---|---|---|---|']
    for k, x in righe_tab.items():
        f, d = k.split(', ')
        md.append('| %s | %s | %d | %s |' % (f, d, x['eventi'], '%.2f' % x['P_l'] if x['P_l'] is not None else ''))
    md += ['', 'Effetto della parola dopo (a parità di fonte): %+.3f, p %.4f. Effetto della fonte (a parità di parola dopo): %+.3f, p %.4f.' % (e_dopo, p_dopo, e_fon, p_fon), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e394_fine_adattata.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
