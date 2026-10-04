# -*- coding: utf-8 -*-
"""Esperimento e3b34: contrasto B - A dell'eccesso di accordo delle scelte di grafia con 10-19 lettere in mezzo (e a 0
lettere), con intervalli bootstrap sulle righe; ZL e IT.

Preregistrazione: preregistrazioni/e3b34.md. Scrive risultati/e3b34_memoria_ab_contrasto.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b14_memoria_profilo as e3b14

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def eventi(pagine):
    """[(id riga, finestra, accordo - atteso)] con finestra '0' o '10-19'."""
    out = []
    rid = 0
    for righe in pagine:
        for c, f in e3b14.CLASSI.items():
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
                r = righe[i]
                for a in range(len(vv)):
                    if vv[a] is None:
                        continue
                    for d in range(1, 11):
                        b = a + d
                        if b < len(vv) and vv[b] is not None:
                            l = sum(len(w) for w in r[a + 1:b])
                            fin = '0' if l == 0 else ('10-19' if 10 <= l <= 19 else None)
                            if fin:
                                out.append((rid + i, fin, int(vv[a] == vv[b]) - att))
        rid += len(righe)
    return out


def medie(ev):
    acc = defaultdict(lambda: [0.0, 0])
    for _, fin, x in ev:
        acc[fin][0] += x
        acc[fin][1] += 1
    return {k: s / n for k, (s, n) in acc.items()}


def contrasto(per_l, rnd):
    ev = {lg: eventi(pg) for lg, pg in per_l.items()}
    m = {lg: medie(e) for lg, e in ev.items()}
    righe = {}
    for lg, e in ev.items():
        g = defaultdict(list)
        for x in e:
            g[x[0]].append(x)
        righe[lg] = list(g.values())
    b = {'0': [], '10-19': []}
    for _ in range(BOOT):
        mb = {lg: medie([x for blk in (rnd.choice(rr) for _ in rr) for x in blk]) for lg, rr in righe.items()}
        for k in b:
            b[k].append(mb['B'][k] - mb['A'][k])
    ic = {k: [sorted(v)[int(0.025 * BOOT)], sorted(v)[int(0.975 * BOOT) - 1]] for k, v in b.items()}
    return OrderedDict((k, OrderedDict([('A', m['A'][k]), ('B', m['B'][k]), ('B_meno_A', m['B'][k] - m['A'][k]), ('IC95', ic[k])])) for k in ('0', '10-19'))


def main():
    rnd = random.Random(3234)
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    ris = OrderedDict()
    for quale in ('ZL', 'IT'):
        per = defaultdict(lambda: defaultdict(list))
        for r in trascrizione.testo_corrente(trascrizione.leggi(quale)):
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                per[lingua.get(r.pagina)][r.pagina].append(ws)
        ris[quale] = contrasto({lg: list(per[lg].values()) for lg in ('A', 'B')}, rnd)
        print(quale, json.dumps(ris[quale]), flush=True)
    esito = 'B ricorda più a lungo' if all(ris[q]['10-19']['IC95'][0] > 0 for q in ris) else 'nessuna differenza dimostrata'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b34_memoria_ab_contrasto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b34 — B ricorda più a lungo di A? (contrasto a 10–19 lettere, con intervallo)', '', 'Preregistrazione: `preregistrazioni/e3b34.md` (finestra scelta dopo aver visto i profili, dichiarato).', '',
          '| trascrizione | lettere in mezzo | A | B | B − A | IC 95% |', '|---|---|---|---|---|---|']
    for q in ('ZL', 'IT'):
        for k in ('0', '10-19'):
            x = ris[q][k]
            md.append('| %s | %s | %+.4f | %+.4f | %+.4f | %+.4f – %+.4f |' % (q, k, x['A'], x['B'], x['B_meno_A'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b34_memoria_ab_contrasto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
