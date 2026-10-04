# -*- coding: utf-8 -*-
"""Esperimento e3b74: tipo della modifica fra etichette consecutive a una modifica, contro tutte le coppie a una
modifica fra etichette della stessa pagina; descrittivo per le parole vicine nella riga.

Preregistrazione: preregistrazioni/e3b74.md. Scrive risultati/e3b74_etichette_modifiche.json e .md.
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

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000
SCELTE = ('k/t', 'sh/ch', 'e/ee', 'qo/o', '-dy/-ey')
MIN_CONS = 40


def tipo(a, b):
    """Tipo della modifica fra due parole a una modifica (tuple di segni)."""
    if len(a) == len(b):
        i = next(k for k in range(len(a)) if a[k] != b[k])
        x, y = sorted((a[i], b[i]))
        if (x, y) == ('k', 't'):
            return 'k/t'
        if (x, y) == ('ch', 'sh'):
            return 'sh/ch'
        if (x, y) == ('d', 'e') and i == len(a) - 2 and a[-1] == 'y':
            return '-dy/-ey'
        return 'altro'
    if len(a) > len(b):
        a, b = b, a
    i = next((k for k in range(len(a)) if a[k] != b[k]), len(a))
    s = b[i]
    vicini = [b[k] for k in (i - 1, i + 1) if 0 <= k < len(b)]
    if s == 'e' and 'e' in vicini:
        return 'e/ee'
    if s == 'i' and 'i' in vicini:
        return 'numero di i'
    if s == 'q' and i == 0 and len(b) > 1 and b[1] == 'o':
        return 'qo/o'
    return 'altro'


def modifica(a, b):
    return len(a) >= 3 and len(b) >= 3 and a != b and e3a86.una_modifica(a, b)


def quota_scelte(cc):
    n = sum(cc.values())
    return sum(cc[s] for s in SCELTE) / n if n else None


def main():
    rnd = random.Random(3274)
    per_pag = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.ETICHETTA:
            continue
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per_pag.setdefault(r.pagina, []).append(ws[0])
    pagine = OrderedDict((pg, v) for pg, v in per_pag.items() if len(v) >= 4)
    cons, rif = OrderedDict(), OrderedDict()
    for pg, ee in pagine.items():
        c1, c2 = Counter(), Counter()
        for i in range(len(ee)):
            for j in range(i + 1, len(ee)):
                if modifica(ee[i], ee[j]):
                    (c1 if j == i + 1 else c2)[tipo(ee[i], ee[j])] += 1
        cons[pg], rif[pg] = c1, c2
    tc, tr = sum(cons.values(), Counter()), sum(rif.values(), Counter())
    qc, qr = quota_scelte(tc), quota_scelte(tr)
    chiavi = list(pagine)
    boot = []
    for _ in range(BOOT):
        bb = [rnd.choice(chiavi) for _ in chiavi]
        a, b = quota_scelte(sum((cons[k] for k in bb), Counter())), quota_scelte(sum((rif[k] for k in bb), Counter()))
        if a is not None and b is not None:
            boot.append(a - b)
    boot.sort()
    ic = [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]
    testo = Counter()
    for pars in e341.pagine().values():
        for par in pars:
            for r in par:
                ws = [w for w in (tuple(D(x)) for x in r) if w]
                for i in range(len(ws)):
                    for d in (1, 2, 3):
                        if i + d < len(ws) and modifica(ws[i], ws[i + d]):
                            testo[tipo(ws[i], ws[i + d])] += 1
    n_cons = sum(tc.values())
    if n_cons < MIN_CONS:
        esito = 'dati insufficienti'
    elif ic[0] > 0:
        esito = 'le etichette si variano sulle scelte'
    elif ic[1] < 0:
        esito = 'al contrario'
    else:
        esito = 'nessuna preferenza'
    out = OrderedDict([('pagine', len(pagine)), ('consecutive', dict(tc)), ('riferimento', dict(tr)), ('testo_vicine', dict(testo)),
                       ('quota_scelte_consecutive', qc), ('quota_scelte_riferimento', qr), ('quota_scelte_testo', quota_scelte(testo)),
                       ('differenza', qc - qr), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b74_etichette_modifiche.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tipi = list(SCELTE) + ['numero di i', 'altro']
    md = ['# e3b74 — Quando un\'etichetta copia la precedente, che cosa cambia?', '', 'Preregistrazione: `preregistrazioni/e3b74.md`. Pagine con almeno 4 etichette: %d.' % len(pagine), '',
          '| tipo di modifica | etichette consecutive | etichette non consecutive (riferimento) | parole vicine nella riga (descrittivo) |', '|---|---|---|---|']
    for t in tipi:
        md.append('| %s | %d | %d | %d |' % (t, tc[t], tr[t], testo[t]))
    md.append('| **quota "scelta"** | **%.3f** (%d coppie) | **%.3f** (%d) | **%.3f** (%d) |' % (qc, n_cons, qr, sum(tr.values()), quota_scelte(testo), sum(testo.values())))
    md += ['', 'Differenza consecutive − riferimento: **%+.3f** (IC 95%% %+.3f – %+.3f).' % (qc - qr, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b74_etichette_modifiche.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
