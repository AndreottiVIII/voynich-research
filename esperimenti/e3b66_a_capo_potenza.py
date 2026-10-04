# -*- coding: utf-8 -*-
"""Esperimento e3b66: e3b65 con coppie a distanza 2-4, controllo = media di riga sopra e due sotto, ZL e IT, pagine
normali.

Preregistrazione: preregistrazioni/e3b66.md. Scrive risultati/e3b66_a_capo_potenza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a86_ripetizioni_riga as e3a86
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b65_a_capo_controllo as e3b65

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
DIST = (2, 3, 4)


def coppie_cavallo(a, b):
    seq = a + b
    n = len(a)
    out = []
    for i in range(n):
        for d in DIST:
            j = i + d
            if j < n or j >= len(seq) or not e3b64.classe(seq[i]) or not e3b64.classe(seq[j]):
                continue
            if any(seq[k] == e3b64.ILL for k in range(i + 1, j)):
                continue
            if seq[i][1] == seq[j][1] or e3a86.una_modifica(seq[i][1], seq[j][1]):
                continue
            out.append((seq[i][0], seq[j][0]))
    return out


def coppie_dentro(seg):
    out = []
    for i in range(len(seg)):
        for d in DIST:
            j = i + d
            if j >= len(seg) or not e3b64.classe(seg[i]) or not e3b64.classe(seg[j]) or any(seg[k] == e3b64.ILL for k in range(i + 1, j)):
                continue
            if seg[i][1] == seg[j][1] or e3a86.una_modifica(seg[i][1], seg[j][1]):
                continue
            out.append((seg[i][0], seg[j][0]))
    return out


def somme(per_pagina, quote, chiave):
    out = {}
    for pg, cc in per_pagina.items():
        o = a = n = 0.0
        for c, f in e3b62.CV.items():
            if (c, pg) not in quote:
                continue
            p = quote[(c, pg)]
            for prima, altri in cc:
                if chiave == 'dentro':
                    pp = [x for s in (prima, altri['sotto']) for x in coppie_dentro(e3b64.valori(s, f))]
                elif altri.get(chiave) is None:
                    continue
                else:
                    pp = coppie_cavallo(e3b64.valori(prima, f), e3b64.valori(altri[chiave], f))
                s = e3b64.somma_pagina(pp, p)
                o, a, n = o + s[0], a + s[1], n + s[2]
        out[pg] = (o, a, n)
    return out


def analisi(quale, sezione, rnd):
    righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(quale) if sezione.get(pg) != 'T']
    quote = e3b64.quote_pagine(righe, e3b62.CV)
    casi = e3b65.casi_capo(righe)
    sm = {k: somme(casi, quote, k) for k in ('sotto', 'sopra', 'due', 'dentro')}
    pagine = list(casi)

    def dd(pp):
        ks = {k: e3b64.kappa([sm[k][pg] for pg in pp])[0] for k in ('sotto', 'sopra', 'due')}
        if None in ks.values():
            return None
        return ks['sotto'] - (ks['sopra'] + ks['due']) / 2
    d = dd(pagine)
    boot = sorted(x for x in (dd([rnd.choice(pagine) for _ in pagine]) for _ in range(BOOT)) if x is not None)
    ks = OrderedDict((k, OrderedDict([('K', e3b64.kappa([sm[k][pg] for pg in pagine])[0]), ('coppie', int(sum(sm[k][pg][2] for pg in pagine)))])) for k in sm)
    return OrderedDict([('pagine', len(pagine)), ('K', ks), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])


def main():
    rnd = random.Random(3266)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    ris = OrderedDict((q, analisi(q, sezione, rnd)) for q in ('ZL', 'IT'))
    for q, x in ris.items():
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    z, it = ris['ZL'], ris['IT']
    dentro = z['K']['dentro']['K']
    if z['IC95'][0] > 0 and it['D'] > 0:
        esito = "la memoria passa l'a capo (almeno in parte)"
    elif z['IC95'][0] <= 0 <= z['IC95'][1] and z['IC95'][1] < dentro / 3:
        esito = "l'a capo azzera la memoria"
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b66_a_capo_potenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b66 — La memoria delle scelte passa l\'a capo? Più coppie, due trascrizioni', '', 'Preregistrazione: `preregistrazioni/e3b66.md`. Pagine normali; coppie a distanza 2–4; D = K(continuazione) − media di K(sopra) e K(due sotto).', '',
          '| trascrizione | pagine | K dentro i tratti (coppie) | K continuazione (coppie) | K riga sopra (coppie) | K due sotto (coppie) | D (IC 95%) |', '|---|---|---|---|---|---|---|']
    for q, x in ris.items():
        k = x['K']
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) |' % (q, x['pagine'], k['dentro']['K'], k['dentro']['coppie'], k['sotto']['K'], k['sotto']['coppie'],
                                                                                              k['sopra']['K'], k['sopra']['coppie'], k['due']['K'], k['due']['coppie'], x['D'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b66_a_capo_potenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
