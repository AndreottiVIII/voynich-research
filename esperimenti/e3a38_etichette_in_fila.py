# -*- coding: utf-8 -*-
"""Esperimento e3a38: etichette consecutive nella stessa pagina simili (uguali o a una modifica) piu' del caso? Confronto:
parole vicine nelle righe dei paragrafi.

Preregistrazione: preregistrazioni/e3a38.md. Scrive risultati/e3a38_etichette_in_fila.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def lev1(a, b):
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


def quota(gruppi):
    s = u = m = t = 0
    for g in gruppi:
        for a, b in zip(g, g[1:]):
            if len(a) < 3 or len(b) < 3:
                continue
            t += 1
            if a == b:
                u += 1
                s += 1
            elif lev1(a, b):
                m += 1
                s += 1
    return (s / t, u / t, m / t, t) if t else (0, 0, 0, 0)


def prova(gruppi, mescola, rnd):
    vero = quota(gruppi)
    nul = [quota(mescola(gruppi)) for _ in range(1000)]
    out = OrderedDict([('coppie', vero[3])])
    for k, nome in enumerate(('simili', 'uguali', 'a una modifica')):
        xs = [n[k] for n in nul]
        mm, sd = statistics.mean(xs), statistics.pstdev(xs)
        out[nome] = OrderedDict([('osservata', vero[k]), ('nullo', mm), ('rapporto', vero[k] / mm if mm else None), ('z', (vero[k] - mm) / sd if sd else 0.0)])
    return out


def main():
    rnd = random.Random(3138)
    per_pag, sez = OrderedDict(), {}
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.ETICHETTA:
            continue
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per_pag.setdefault(r.pagina, []).append(ws[0])
            sez[r.pagina] = r.sezione or '?'
    pagine = [v for v in per_pag.values() if len(v) >= 4]
    ris = OrderedDict()
    ris['etichette consecutive'] = prova(pagine, lambda gg: [rnd.sample(g, len(g)) for g in gg], rnd)
    # confronto: parole vicine nella riga, nullo nella pagina
    righe_pag = []
    for pp in e341.pagine().values():
        righe_pag.append([[w for w in (tuple(D(x)) for x in r) if w] for par in pp for r in par])

    def mescola_pagina(pp_list):
        out = []
        for righe in pp_list:
            tutte = [w for r in righe for w in r]
            rnd.shuffle(tutte)
            i = 0
            for r in righe:
                out.append(tutte[i:i + len(r)])
                i += len(r)
        return out
    righe_flat = [r for righe in righe_pag for r in righe]
    vero = quota(righe_flat)
    nul = [quota(mescola_pagina(righe_pag)) for _ in range(200)]
    conf = OrderedDict([('coppie', vero[3])])
    for k, nome in enumerate(('simili', 'uguali', 'a una modifica')):
        xs = [n[k] for n in nul]
        mm, sd = statistics.mean(xs), statistics.pstdev(xs)
        conf[nome] = OrderedDict([('osservata', vero[k]), ('nullo', mm), ('rapporto', vero[k] / mm if mm else None), ('z', (vero[k] - mm) / sd if sd else 0.0)])
    ris['parole vicine nella riga (confronto)'] = conf
    E = ris['etichette consecutive']['simili']
    esito = 'le etichette si copiano in fila' if E['rapporto'] and E['rapporto'] > 1.2 and E['z'] > 3 else ('nessuna copia in fila' if abs(E['z']) < 2 else 'incerto')
    coppie = Counter()
    for g in pagine:
        for a, b in zip(g, g[1:]):
            if len(a) >= 3 and len(b) >= 3 and lev1(a, b):
                coppie['%s / %s' % (''.join(a), ''.join(b))] += 1
    out = OrderedDict([('pagine', len(pagine)), ('etichette', sum(len(g) for g in pagine)), ('sezioni', dict(Counter(sez[p] for p, v in per_pag.items() if len(v) >= 4))),
                       ('misure', ris), ('coppie_simili', coppie.most_common(15)), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:2000], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a38_etichette_in_fila.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a38 — Le etichette consecutive si somigliano più del caso?', '', 'Preregistrazione: `preregistrazioni/e3a38.md`. %d pagine con almeno 4 etichette (%d etichette); sezioni: %s.' % (
        len(pagine), out['etichette'], ', '.join('%s %d' % kv for kv in out['sezioni'].items())), '',
          '| confronto | coppie | misura | osservata | nullo | rapporto | z |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        for m in ('simili', 'uguali', 'a una modifica'):
            v = x[m]
            md.append('| %s | %d | %s | %.3f | %.3f | %s | %.1f |' % (k, x['coppie'], m, v['osservata'], v['nullo'], '%.2f' % v['rapporto'] if v['rapporto'] else '', v['z']))
    md += ['', 'Coppie consecutive simili più frequenti: ' + '; '.join('%s (%d)' % kv for kv in coppie.most_common(15)) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a38_etichette_in_fila.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
