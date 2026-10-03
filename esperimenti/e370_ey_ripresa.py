# -*- coding: utf-8 -*-
"""Esperimento 370: la crescita della quota di -ey (rispetto a -dy) dalla meta' alta alla meta' bassa delle righe interne
della pagina, separata fra parole riprese dalle 2 righe sopra e parole non riprese.

Preregistrazione: preregistrazioni/e370.md. Scrive risultati/e370_ey_ripresa.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e328_livelli as e328
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e341.D


def main():
    rnd = random.Random(370)
    pag = e328.carica()
    diffs = {'riprese': [], 'non riprese': []}
    for p, pars in pag.items():
        voci = []    # (indice riga interna nella pagina, gruppo, e' -ey)
        k = 0
        for par in pars:
            righe = [ws for _, ws in par]
            tipi = [t for t, _ in par]
            for i, (t, ws) in enumerate(par):
                if t != 'interna':
                    continue
                sopra = (righe[i - 1] if i >= 1 else []) + (righe[i - 2] if i >= 2 else [])
                for w in ws:
                    u = D(w)
                    if len(u) >= 2 and u[-1] == 'y' and u[-2] in ('d', 'e'):
                        g = 'riprese' if e341.ha_fonte(w, sopra) else 'non riprese'
                        voci.append((k, g, u[-2] == 'e'))
                k += 1
        if k < 12:
            continue
        h = k // 2
        for g in diffs:
            alta = [e for r, gg, e in voci if gg == g and r < h]
            bassa = [e for r, gg, e in voci if gg == g and r >= h]
            if len(alta) >= 3 and len(bassa) >= 3:
                diffs[g].append(statistics.mean(bassa) - statistics.mean(alta))
    out = OrderedDict()
    for g, d in diffs.items():
        v, z = e341.segno_flip(d, rnd)
        out[g] = OrderedDict([('pagine', len(d)), ('bassa_meno_alta', v), ('z', z)])
    zr, zn = out['riprese']['z'], out['non riprese']['z']
    if zr > 3 and abs(zn) < 2:
        esito = 'la crescita viene dalla ripresa'
    elif zn > 3:
        esito = 'non viene dalla ripresa'
    else:
        esito = 'incerto'
    res = OrderedDict([('gruppi', out), ('esito', esito)])
    print(json.dumps(res, ensure_ascii=False), flush=True)
    json.dump(res, open(os.path.join(RISULTATI, 'e370_ey_ripresa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e370 — La crescita di -ey scendendo nella pagina viene dalla ripresa?', '', 'Preregistrazione: `preregistrazioni/e370.md`.', '',
          '| parole in -dy/-ey | pagine | quota di -ey, metà bassa − metà alta | z |', '|---|---|---|---|']
    for g, v in out.items():
        md.append('| %s | %d | %+.4f | %.1f |' % (g, v['pagine'], v['bassa_meno_alta'], v['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e370_ey_ripresa.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
