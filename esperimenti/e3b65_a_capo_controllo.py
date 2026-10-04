# -*- coding: utf-8 -*-
"""Esperimento e3b65: accordo delle scelte fra la fine di una riga e l'inizio della riga sotto, contro l'inizio della riga
sopra e di due righe sotto (controllo della somiglianza fra righe vicine); per il salto del disegno, secondo tratto
della stessa riga contro quello della riga con salto precedente.

Preregistrazione: preregistrazioni/e3b65.md. Scrive risultati/e3b65_a_capo_controllo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e386_salto_disegno as e386
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def casi_capo(righe):
    """{pagina: [(prima, {'sotto': tratto, 'sopra': tratto, 'due': tratto o None})]}."""
    out = defaultdict(list)
    for k in range(1, len(righe) - 1):
        a, b, c = righe[k - 1], righe[k], righe[k + 1]
        if not (a[0] == b[0] == c[0] and a[1] == b[1] == c[1]):
            continue
        due = None
        if k + 2 < len(righe) and righe[k + 2][0] == b[0] and righe[k + 2][1] == b[1]:
            due = e3b64.tratti(righe[k + 2][2], righe[k + 2][3])[0]
        out[b[0]].append((e3b64.tratti(b[2], b[3])[-1], OrderedDict([('sotto', e3b64.tratti(c[2], c[3])[0]), ('sopra', e3b64.tratti(a[2], a[3])[0]), ('due', due)])))
    return out


def casi_salto(righe):
    out = defaultdict(list)
    prec = {}
    for pg, npar, ws, seps in righe:
        tt = e3b64.tratti(ws, seps)
        if len(tt) < 2:
            continue
        if pg in prec:
            out[pg].append((tt[0], OrderedDict([('stessa', tt[1]), ('precedente', prec[pg])])))
        prec[pg] = tt[1]
    return out


def somme(per_pagina, quote, chiave):
    """{pagina: (accordi, attesi, coppie)} per l'abbinamento 'chiave'."""
    out = {}
    for pg, cc in per_pagina.items():
        o = a = n = 0.0
        for c, f in e3b62.CV.items():
            if (c, pg) not in quote:
                continue
            p = quote[(c, pg)]
            for prima, altri in cc:
                if altri.get(chiave) is None:
                    continue
                s = e3b64.somma_pagina(e3b64.coppie_cavallo(e3b64.valori(prima, f), e3b64.valori(altri[chiave], f)), p)
                o, a, n = o + s[0], a + s[1], n + s[2]
        out[pg] = (o, a, n)
    return out


def k_di(sm, pagine):
    return e3b64.kappa([sm[pg] for pg in pagine])[0]


def confronto(per_pagina, quote, vero, controlli, rnd):
    sm = {k: somme(per_pagina, quote, k) for k in (vero,) + controlli}
    pagine = list(per_pagina)
    ks = OrderedDict((k, OrderedDict([('K', k_di(sm[k], pagine)), ('coppie', int(sum(sm[k][pg][2] for pg in pagine)))])) for k in sm)
    d = ks[vero]['K'] - ks[controlli[0]]['K']
    boot = []
    for _ in range(BOOT):
        bb = [rnd.choice(pagine) for _ in pagine]
        x, y = k_di(sm[vero], bb), k_di(sm[controlli[0]], bb)
        if x is not None and y is not None:
            boot.append(x - y)
    boot.sort()
    return OrderedDict([('K', ks), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]), ('pagine', len(pagine))])


def main():
    rnd = random.Random(3265)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e386.righe()]
    quote = e3b64.quote_pagine(righe, e3b62.CV)
    capo = casi_capo(righe)
    ris = OrderedDict()
    ris['a capo, pagine normali'] = confronto({pg: v for pg, v in capo.items() if sezione.get(pg) != 'T'}, quote, 'sotto', ('sopra', 'due'), rnd)
    ris['a capo, pagine di solo testo'] = confronto({pg: v for pg, v in capo.items() if sezione.get(pg) == 'T'}, quote, 'sotto', ('sopra', 'due'), rnd)
    ris['salto del disegno'] = confronto(casi_salto(righe), quote, 'stessa', ('precedente',), rnd)
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    es = OrderedDict()
    for k, x in ris.items():
        if x['IC95'][0] > 0:
            es[k] = 'la memoria passa il confine'
        elif x['IC95'][0] <= 0 <= x['IC95'][1] and ('due' not in x['K'] or (x['K']['sopra']['K'] or 0) > (x['K']['due']['K'] or 0)):
            es[k] = 'righe vicine che si somigliano, non memoria'
        else:
            es[k] = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b65_a_capo_controllo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b65 — Memoria che passa l\'a capo, o righe vicine che si somigliano?', '', 'Preregistrazione: `preregistrazioni/e3b65.md`. K con l\'atteso della pagina; D = K(continuazione) − K(controllo vicino).', '',
          '| gruppo | pagine | K continuazione (coppie) | K controllo vicino (coppie) | K due sotto (coppie) | D (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        kk = list(x['K'].items())
        terzo = '%+.4f (%d)' % (kk[2][1]['K'], kk[2][1]['coppie']) if len(kk) > 2 and kk[2][1]['K'] is not None else '—'
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %s | %+.4f (%+.4f – %+.4f) |' % (k, x['pagine'], kk[0][1]['K'], kk[0][1]['coppie'], kk[1][1]['K'], kk[1][1]['coppie'], terzo, x['D'], x['IC95'][0], x['IC95'][1]))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b65_a_capo_controllo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
