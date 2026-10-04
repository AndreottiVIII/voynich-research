# -*- coding: utf-8 -*-
"""Esperimento e3b07: e3b06 con la trascrizione IT, e senza le coppie di parole simili (uguali o a una modifica).

Preregistrazione: preregistrazioni/e3b07.md. Scrive risultati/e3b07_scelte_memoria_controlli.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')


def pagine(quale):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi(quale)):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if ws:
            per.setdefault(r.pagina, []).append(ws)
    return list(per.values())


def coppie_senza_simili(pg):
    """Come e3b06.coppie ma esclude le coppie di parole simili."""
    out = []
    rid = 0
    for righe in pg:
        val = {c: [[f(w) for w in r] for r in righe] for c, f in e3b06.CLASSI.items()}
        for c in e3b06.CLASSI:
            tot = [sum(1 for v in vv if v is not None) for vv in val[c]]
            uno = [sum(1 for v in vv if v == 1) for vv in val[c]]
            T, U = sum(tot), sum(uno)
            for i, vv in enumerate(val[c]):
                t, u = T - tot[i], U - uno[i]
                if t < 5:
                    continue
                p = u / t
                att = p * p + (1 - p) * (1 - p)
                r = righe[i]
                for a in range(len(vv)):
                    if vv[a] is None:
                        continue
                    for d in e3b06.VICINO + e3b06.LONTANO:
                        b = a + d
                        if b < len(vv) and vv[b] is not None and not (r[a] == r[b] or e3a86.una_modifica(tuple(r[a]), tuple(r[b]))):
                            out.append((rid + i, c, d, int(vv[a] == vv[b]), att))
        rid += len(righe)
    return out


def analizza(cc, rnd):
    e = e3b06.eccessi(cc)
    per_riga = defaultdict(list)
    for x in cc:
        per_riga[x[0]].append(x)
    chiavi = list(per_riga)
    boot = defaultdict(list)
    for _ in range(e3b06.BOOT):
        bb = [x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per_riga[k]]
        for k, (v, _) in e3b06.eccessi(bb).items():
            boot[k].append(v)
    ic = {k: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for k, v in boot.items()}
    return OrderedDict([('vicino', e['tutte', 'vicino'][0]), ('IC_vicino', ic['tutte', 'vicino']), ('coppie_vicino', e['tutte', 'vicino'][1]),
                        ('lontano', e['tutte', 'lontano'][0]), ('IC_lontano', ic['tutte', 'lontano']), ('coppie_lontano', e['tutte', 'lontano'][1])])


def main():
    rnd = random.Random(3207)
    zl = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        zl.append([r for r in righe if r])
    it = pagine('IT')
    ris = OrderedDict()
    ris['IT, tutte le coppie'] = analizza(e3b06.coppie(it), rnd)
    ris['ZL, senza parole simili'] = analizza(coppie_senza_simili(zl), rnd)
    ris['IT, senza parole simili'] = analizza(coppie_senza_simili(it), rnd)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    a = ris['IT, tutte le coppie']
    es_a = 'regge' if a['IC_vicino'][0] > 0 and a['lontano'] < 0.25 * a['vicino'] else 'non regge'
    es_b = OrderedDict()
    for k in ('ZL, senza parole simili', 'IT, senza parole simili'):
        es_b[k] = 'memoria delle scelte' if ris[k]['IC_vicino'][0] > 0 else 'era solo ripetizione di parole'
    out = OrderedDict([('risultati', ris), ('esito_a', es_a), ('esito_b', es_b)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b07_scelte_memoria_controlli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b07 — La memoria corta delle scelte di grafia regge con Takahashi e senza le parole ripetute?', '', 'Preregistrazione: `preregistrazioni/e3b07.md`. ZL con tutte le coppie (e3b06): vicino +0,031, lontano −0,001.', '',
          '| versione | coppie vicine | eccesso vicino (d 2–3) | IC 95% | coppie lontane | eccesso lontano (d 6–10) | IC 95% |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.4f – %+.4f | %d | %+.4f | %+.4f – %+.4f |' % (k, x['coppie_vicino'], x['vicino'], x['IC_vicino'][0], x['IC_vicino'][1], x['coppie_lontano'], x['lontano'], x['IC_lontano'][0], x['IC_lontano'][1]) for k, x in ris.items()]
    md += ['', 'Esito (a), IT: **%s**. Esito (b): %s.' % (es_a, '; '.join('%s: **%s**' % kv for kv in es_b.items()))]
    open(os.path.join(RISULTATI, 'e3b07_scelte_memoria_controlli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
