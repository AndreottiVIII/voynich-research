# -*- coding: utf-8 -*-
"""Esperimento e3b19: memoria corta (differenza vicino - lontano dell'accordo, e3b06/e3b08) per altre scelte di grafia:
k/t, ckh/cth, iii/ii, a/o iniziale, ai/aii.

Preregistrazione: preregistrazioni/e3b19.md. Scrive risultati/e3b19_altre_scelte.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def kt(w):
    k, t = 'k' in w.replace('ckh', ''), 't' in w.replace('cth', '')
    return 1 if k and not t else (0 if t and not k else None)


def ckh(w):
    a, b = 'ckh' in w, 'cth' in w
    return 1 if a and not b else (0 if b and not a else None)


def iii(w):
    if 'aiiin' in w or 'aiiir' in w:
        return 1
    if 'aiin' in w or 'aiir' in w:
        return 0
    return None


def ao(w):
    if w[:2] in ('ar', 'al'):
        return 1
    if w[:2] in ('or', 'ol'):
        return 0
    return None


def aii(w):
    if 'aii' in w:
        return 0
    if 'ain' in w or 'air' in w:
        return 1
    return None


CLASSI = OrderedDict([('k/t', kt), ('ckh/cth', ckh), ('iii/ii', iii), ('a/o iniziale', ao), ('ai/aii', aii)])


def coppie(pagine, f):
    out = []
    rid = 0
    for righe in pagine:
        val = [[f(w) for w in r] for r in righe]
        tot = [sum(1 for v in vv if v is not None) for vv in val]
        uno = [sum(1 for v in vv if v == 1) for vv in val]
        T, U = sum(tot), sum(uno)
        for i, vv in enumerate(val):
            t, u = T - tot[i], U - uno[i]
            if t < 5:
                continue
            p = u / t
            att = p * p + (1 - p) * (1 - p)
            for a in range(len(vv)):
                if vv[a] is None:
                    continue
                for d in e3b06.VICINO + e3b06.LONTANO:
                    b = a + d
                    if b < len(vv) and vv[b] is not None:
                        out.append((rid + i, 'vicino' if d in e3b06.VICINO else 'lontano', int(vv[a] == vv[b]), att))
        rid += len(righe)
    return out


def diff(cc):
    acc = defaultdict(lambda: [0.0, 0])
    for _, g, ok, att in cc:
        acc[g][0] += ok - att
        acc[g][1] += 1
    if not acc['vicino'][1] or not acc['lontano'][1]:
        return None, acc
    return acc['vicino'][0] / acc['vicino'][1] - acc['lontano'][0] / acc['lontano'][1], acc


def main():
    rnd = random.Random(3219)
    pagine = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        pagine.append([r for r in righe if r])
    ris = OrderedDict()
    for nome, f in CLASSI.items():
        cc = coppie(pagine, f)
        d, acc = diff(cc)
        n_v, n_l = acc['vicino'][1], acc['lontano'][1]
        if n_l < 200 or d is None:
            ris[nome] = OrderedDict([('coppie_vicine', n_v), ('coppie_lontane', n_l), ('esito', 'dati insufficienti')])
        else:
            per = defaultdict(list)
            for x in cc:
                per[x[0]].append(x)
            chiavi = list(per)
            b = []
            for _ in range(BOOT):
                v, _ = diff([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])
                if v is not None:
                    b.append(v)
            b.sort()
            ic = [b[int(0.025 * len(b))], b[int(0.975 * len(b)) - 1]]
            ris[nome] = OrderedDict([('coppie_vicine', n_v), ('coppie_lontane', n_l), ('eccesso_vicino', acc['vicino'][0] / n_v), ('eccesso_lontano', acc['lontano'][0] / n_l),
                                     ('differenza', d), ('IC95', ic), ('esito', 'memoria corta' if ic[0] > 0 else 'nessuna memoria')])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b19_altre_scelte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b19 — Quali altre scelte di grafia hanno la memoria corta?', '', 'Preregistrazione: `preregistrazioni/e3b19.md`. Già note (e3b06–e3b08): qo/o, -ey/-dy, sh/ch, ee/e sì; -l/-r no.', '',
          '| classe | coppie vicine | coppie lontane | eccesso vicino | eccesso lontano | differenza | IC 95% | esito |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if 'differenza' in x:
            md.append('| %s | %d | %d | %+.4f | %+.4f | %+.4f | %+.4f – %+.4f | %s |' % (k, x['coppie_vicine'], x['coppie_lontane'], x['eccesso_vicino'], x['eccesso_lontano'], x['differenza'], x['IC95'][0], x['IC95'][1], x['esito']))
        else:
            md.append('| %s | %d | %d | – | – | – | – | %s |' % (k, x['coppie_vicine'], x['coppie_lontane'], x['esito']))
    open(os.path.join(RISULTATI, 'e3b19_altre_scelte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
