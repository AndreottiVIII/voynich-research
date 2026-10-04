# -*- coding: utf-8 -*-
"""Esperimento e3b86: accordo delle scelte fra occorrenze della stessa parola (tipo coperto) contro parole diverse,
dentro il paragrafo (righe a distanza 2 o più) e fra pagine della stessa mano; contrasto.

Preregistrazione: preregistrazioni/e3b86.md. Scrive risultati/e3b86_grafia_sessione.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def dati_pagina(pars, f):
    """Somme dentro il paragrafo [stesso: acc, n; diverso: acc, n] e conteggi per tipo {tipo: [n0, n1]}."""
    dentro = [0, 0, 0, 0]
    tipi = defaultdict(lambda: [0, 0])
    for par in pars:
        occ = []
        for nr, r in enumerate(par):
            for w in r:
                x = f(w)
                if x:
                    occ.append((nr, x[0], x[1]))
                    tipi[x[1]][x[0]] += 1
        for a in range(len(occ)):
            for b in range(a + 1, len(occ)):
                ra, va, ta = occ[a]
                rb, vb, tb = occ[b]
                if abs(ra - rb) < 2:
                    continue
                if ta == tb:
                    dentro[0] += va == vb
                    dentro[1] += 1
                elif not e3a86.una_modifica(ta, tb):
                    dentro[2] += va == vb
                    dentro[3] += 1
    return dentro, dict(tipi)


def fra_pagine(pagine, pesi):
    """D_fra dai conteggi per pagina (pagine = [(mano, {(classe, tipo): [n0, n1]})], pesi = molteplicità del bootstrap).
    Le coppie si contano dentro la stessa classe e la stessa mano."""
    gruppi = defaultdict(list)
    for (mano, tipi), w in zip(pagine, pesi):
        if not w:
            continue
        per_classe = defaultdict(dict)
        for (c, t), v in tipi.items():
            per_classe[c][t] = v
        for c, tt in per_classe.items():
            gruppi[(mano, c)].append((tt, w))
    s_same = p_same = s_all = p_all = 0.0
    for lista in gruppi.values():
        N0 = N1 = Q0 = Q1 = Qn = 0.0
        per_tipo = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0.0])
        for tt, w in lista:
            a0 = sum(v[0] for v in tt.values())
            a1 = sum(v[1] for v in tt.values())
            N0 += w * a0
            N1 += w * a1
            Q0 += w * a0 * a0
            Q1 += w * a1 * a1
            Qn += w * (a0 + a1) ** 2
            for t, (n0, n1) in tt.items():
                q = per_tipo[t]
                q[0] += w * n0
                q[1] += w * n1
                q[2] += w * n0 * n0
                q[3] += w * n1 * n1
                q[4] += w * (n0 + n1) ** 2
        s_all += (N0 ** 2 - Q0) + (N1 ** 2 - Q1)
        p_all += (N0 + N1) ** 2 - Qn
        for q in per_tipo.values():
            s_same += (q[0] ** 2 - q[2]) + (q[1] ** 2 - q[3])
            p_same += (q[0] + q[1]) ** 2 - q[4]
    if p_same <= 0 or p_all - p_same <= 0:
        return None
    return s_same / p_same - (s_all - s_same) / (p_all - p_same)


def d_dentro(dentro, pesi):
    t = [sum(w * d[k] for d, w in zip(dentro, pesi)) for k in range(4)]
    if not t[1] or not t[3]:
        return None
    return t[0] / t[1] - t[2] / t[3]


def main():
    rnd = random.Random(3286)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        dentro, pagine = [], []
        for pg, pars in pd.items():
            if not mano.get(pg):
                continue
            pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
            pp = [[r for r in par if r] for par in pp]
            tot_d = [0, 0, 0, 0]
            tot_t = defaultdict(lambda: [0, 0])
            for c, f in e3b62.CV.items():
                d, t = dati_pagina(pp, f)
                tot_d = [a + b for a, b in zip(tot_d, d)]
                for k, v in t.items():
                    tot_t[(c, k)][0] += v[0]
                    tot_t[(c, k)][1] += v[1]
            dentro.append(tot_d)
            pagine.append((mano[pg], dict(tot_t)))
        n = len(pagine)
        uno = [1] * n
        dw, db = d_dentro(dentro, uno), fra_pagine(pagine, uno)
        boot = []
        for _ in range(BOOT):
            cnt = Counter(rnd.randrange(n) for _ in range(n))
            pesi = [cnt[i] for i in range(n)]
            a, b = d_dentro(dentro, pesi), fra_pagine(pagine, pesi)
            if a is not None and b is not None:
                boot.append(a - b)
        boot.sort()
        ris[q] = OrderedDict([('pagine', n), ('D_dentro', dw), ('D_fra', db), ('contrasto', dw - db),
                              ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]),
                              ('coppie_dentro_stesso_tipo', sum(d[1] for d in dentro))])
        print(q, json.dumps(ris[q]), flush=True)
    z, it = ris['ZL'], ris['IT']
    if z['IC95'][0] > 0 and it['contrasto'] > 0:
        esito = 'grafia della parola legata al momento'
    elif z['IC95'][0] <= 0 <= z['IC95'][1]:
        esito = 'preferenza fissa della parola' if z['D_fra'] >= 0.01 else 'nessuna grafia propria'
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b86_grafia_sessione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b86 — La stessa parola si scrive allo stesso modo nella stessa sessione più che fra pagine?', '', 'Preregistrazione: `preregistrazioni/e3b86.md`. D = accordo fra occorrenze della stessa parola − accordo fra parole diverse.', '',
          '| trascrizione | pagine | D dentro il paragrafo (righe a 2+) | D fra pagine della stessa mano | contrasto (IC 95%) | coppie stessa parola dentro |', '|---|---|---|---|---|---|']
    for q, x in ris.items():
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) | %d |' % (q, x['pagine'], x['D_dentro'], x['D_fra'], x['contrasto'], x['IC95'][0], x['IC95'][1], x['coppie_dentro_stesso_tipo']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b86_grafia_sessione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
