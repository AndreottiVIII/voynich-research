# -*- coding: utf-8 -*-
"""Esperimento e3b27: la prima riga di una pagina riprende l'ultima riga della pagina precedente (rispetto alle altre
righe di quella pagina)? Coppie "stesso foglio" (r -> v) e "affiancate" (v -> r seguente); confronto fra paragrafi.

Preregistrazione: preregistrazioni/e3b27.md. Scrive risultati/e3b27_ripresa_pagine.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def foglio(pg):
    m = re.fullmatch(r'f(\d+)([rv])\d*', pg)
    return (int(m.group(1)), m.group(2)) if m else None


def eccesso(prima, ultima, altre):
    """quota di parole (>= 3 segni) di 'prima' con una simile in 'ultima', meno la media con le 'altre' righe."""
    tutte = [prima, ultima] + altre
    sim = e385.simili_unita(tutte)
    bers = [w for w in prima if len(w) >= 3]
    if not bers or not altre:
        return None
    q = lambda r: sum(1 for w in bers if sim[w] & set(r)) / len(bers)
    return q(ultima) - statistics.mean(q(r) for r in altre)


def main():
    rnd = random.Random(3227)
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    pagine = []
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pagine.append((pg, [par for par in pp if par]))
    coppie = {'stesso foglio': [], 'affiancate': []}
    for (p, pp), (q, qq) in zip(pagine, pagine[1:]):
        fp, fq = foglio(p), foglio(q)
        if not fp or not fq or lingua.get(p) != lingua.get(q) or lingua.get(p) not in ('A', 'B'):
            continue
        righe_p = [r for par in pp for r in par]
        righe_q = [r for par in qq for r in par]
        if len(righe_p) < 4 or len(righe_q) < 4:
            continue
        if fp[0] == fq[0] and fp[1] == 'r' and fq[1] == 'v':
            tipo = 'stesso foglio'
        elif fq[0] == fp[0] + 1 and fp[1] == 'v' and fq[1] == 'r':
            tipo = 'affiancate'
        else:
            continue
        e = eccesso(righe_q[0], righe_p[-1], righe_p[:-1])
        if e is not None:
            coppie[tipo].append(e)
    dentro = []
    for _, pp in pagine:
        for a, b in zip(pp, pp[1:]):
            if len(a) >= 3:
                e = eccesso(b[0], a[-1], a[:-1])
                if e is not None:
                    dentro.append(e)

    def ic(xs):
        b = sorted(statistics.mean(rnd.choices(xs, k=len(xs))) for _ in range(BOOT))
        return [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]]
    tutte = coppie['stesso foglio'] + coppie['affiancate']
    ris = OrderedDict()
    for k, xs in (('tutte le coppie di pagine', tutte), ('stesso foglio (r → v)', coppie['stesso foglio']), ('affiancate (v → r)', coppie['affiancate']), ('fra paragrafi della stessa pagina', dentro)):
        ris[k] = OrderedDict([('coppie', len(xs)), ('eccesso', statistics.mean(xs) if xs else None), ('IC95', ic(xs) if len(xs) > 5 else None)])
    a, s = coppie['affiancate'], coppie['stesso foglio']
    bd = sorted(statistics.mean(rnd.choices(a, k=len(a))) - statistics.mean(rnd.choices(s, k=len(s))) for _ in range(BOOT))
    icd = [bd[int(0.025 * BOOT)], bd[int(0.975 * BOOT) - 1]]
    esito = 'la ripresa passa la pagina' if ris['tutte le coppie di pagine']['IC95'][0] > 0 else 'la pagina interrompe la ripresa'
    out = OrderedDict([('risultati', ris), ('differenza_affiancate_meno_stesso_foglio', statistics.mean(a) - statistics.mean(s)), ('IC95_differenza', icd), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b27_ripresa_pagine.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b27 — La ripresa passa da una pagina alla successiva? Di più fra pagine affiancate?', '', 'Preregistrazione: `preregistrazioni/e3b27.md`. Eccesso = quota di parole della prima riga con una simile nell\'ultima riga della pagina (o paragrafo) prima, meno la media con le altre righe.', '',
          '| confronto | coppie | eccesso | IC 95% |', '|---|---|---|---|']
    md += ['| %s | %d | %s | %s |' % (k, x['coppie'], '%+.4f' % x['eccesso'] if x['eccesso'] is not None else 'n.d.', '%+.4f – %+.4f' % tuple(x['IC95']) if x['IC95'] else 'n.d.') for k, x in ris.items()]
    md += ['', 'Differenza affiancate − stesso foglio: %+.4f, IC 95%% %+.4f – %+.4f.' % (out['differenza_affiancate_meno_stesso_foglio'], icd[0], icd[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b27_ripresa_pagine.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
