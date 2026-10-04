# -*- coding: utf-8 -*-
"""Esperimento e3b06: accordo delle scelte di grafia facoltative fra parole della stessa riga in funzione della distanza
(vicino d 2-3, lontano d 6-10), rispetto all'atteso dalla pagina senza la riga.

Preregistrazione: preregistrazioni/e3b06.md. Scrive risultati/e3b06_scelte_riga_distanza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 1000
VICINO, LONTANO = (2, 3), tuple(range(6, 11))


def qo(w):
    if w[:3] in ('qok', 'qot', 'qop', 'qof'):
        return 1
    if w[:2] in ('ok', 'ot', 'op', 'of'):
        return 0
    return None


def eydy(w):
    return 1 if w.endswith('ey') else (0 if w.endswith('dy') else None)


def shch(w):
    return 1 if w.startswith('sh') else (0 if w.startswith('ch') else None)


def ee(w):
    if w.endswith('eedy') or w.endswith('eey'):
        return 1
    if (w.endswith('edy') and not w.endswith('eedy')) or (w.endswith('ey') and not w.endswith('eey')):
        return 0
    return None


def lr(w):
    return 1 if w.endswith('l') else (0 if w.endswith('r') else None)


CLASSI = OrderedDict([('qo/o', qo), ('-ey/-dy', eydy), ('sh/ch', shch), ('ee/e', ee), ('-l/-r', lr)])


def coppie(pagine):
    """[(id riga, classe, d, accordo, atteso)]."""
    out = []
    rid = 0
    for righe in pagine:
        val = {c: [[f(w) for w in r] for r in righe] for c, f in CLASSI.items()}
        for c in CLASSI:
            tot = [sum(1 for v in vv if v is not None) for vv in val[c]]
            uno = [sum(1 for v in vv if v == 1) for vv in val[c]]
            T, U = sum(tot), sum(uno)
            for i, vv in enumerate(val[c]):
                t, u = T - tot[i], U - uno[i]
                if t < 5:
                    continue
                p = u / t
                att = p * p + (1 - p) * (1 - p)
                for a in range(len(vv)):
                    if vv[a] is None:
                        continue
                    for d in VICINO + LONTANO:
                        b = a + d
                        if b < len(vv) and vv[b] is not None:
                            out.append((rid + i, c, d, int(vv[a] == vv[b]), att))
        rid += len(righe)
    return out


def eccessi(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, c, d, ok, att in cc:
        g = 'vicino' if d in VICINO else 'lontano'
        for k in ((c, g), ('tutte', g)):
            acc[k][0] += ok - att
            acc[k][1] += 1
    return {k: (s / n, n) for k, (s, n) in acc.items()}


def main():
    rnd = random.Random(3206)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    cc = coppie(pagine)
    e = eccessi(cc)
    per_riga = defaultdict(list)
    for x in cc:
        per_riga[x[0]].append(x)
    chiavi = list(per_riga)
    boot = defaultdict(list)
    for _ in range(BOOT):
        bb = [x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per_riga[k]]
        eb = eccessi(bb)
        for k, (v, _) in eb.items():
            boot[k].append(v)
    ic = {k: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for k, v in boot.items()}
    ris = OrderedDict()
    for c in list(CLASSI) + ['tutte']:
        if (c, 'vicino') in e and (c, 'lontano') in e:
            ris[c] = OrderedDict([('vicino', e[c, 'vicino'][0]), ('coppie_vicino', e[c, 'vicino'][1]), ('IC_vicino', ic[c, 'vicino']),
                                  ('lontano', e[c, 'lontano'][0]), ('coppie_lontano', e[c, 'lontano'][1]), ('IC_lontano', ic[c, 'lontano'])])
    t = ris['tutte']
    if t['lontano'] >= 0.5 * t['vicino'] and t['IC_lontano'][0] > 0:
        esito = 'scelta di riga (costante)'
    elif t['lontano'] < 0.25 * t['vicino']:
        esito = 'memoria corta (cala)'
    else:
        esito = 'in mezzo'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b06_scelte_riga_distanza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b06 — Le "scelte di grafia per riga" sono scelte della riga o memoria corta?', '', 'Preregistrazione: `preregistrazioni/e3b06.md`. Eccesso di accordo rispetto alla pagina senza la riga.', '',
          '| classe | coppie vicine (d 2–3) | eccesso vicino | IC 95% | coppie lontane (d 6–10) | eccesso lontano | IC 95% |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.4f – %+.4f | %d | %+.4f | %+.4f – %+.4f |' % (c, x['coppie_vicino'], x['vicino'], x['IC_vicino'][0], x['IC_vicino'][1], x['coppie_lontano'], x['lontano'], x['IC_lontano'][0], x['IC_lontano'][1]) for c, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b06_scelte_riga_distanza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
