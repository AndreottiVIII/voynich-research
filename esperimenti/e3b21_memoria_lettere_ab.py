# -*- coding: utf-8 -*-
"""Esperimento e3b21: eccesso di accordo delle scelte di grafia (-ey/-dy, sh/ch, ee/e) in funzione delle lettere scritte
fra le due parole, lingua A e B; mezza vita in lettere.

Preregistrazione: preregistrazioni/e3b21.md. Scrive risultati/e3b21_memoria_lettere_ab.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b14_memoria_profilo as e3b14

RISULTATI = os.path.join(QUI, '..', 'risultati')
CLASSI_L = ((0, 0, '0'), (1, 4, '1–4'), (5, 9, '5–9'), (10, 14, '10–14'), (15, 19, '15–19'), (20, 29, '20–29'), (30, 10 ** 6, '30+'))


def classe_l(n):
    for a, b, nome in CLASSI_L:
        if a <= n <= b:
            return nome


def profilo(pagine):
    acc = defaultdict(lambda: [0.0, 0])
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
                            k = classe_l(sum(len(w) for w in r[a + 1:b]))
                            acc[k][0] += int(vv[a] == vv[b]) - att
                            acc[k][1] += 1
    return OrderedDict((nome, (acc[nome][0] / acc[nome][1] if acc[nome][1] else None, acc[nome][1])) for _, _, nome in CLASSI_L)


def mezza(pr):
    nomi = [n for _, _, n in CLASSI_L]
    e0 = pr['0'][0]
    for j, n in enumerate(nomi[1:], 1):
        if pr[n][0] is not None and pr[n][1] >= 200 and pr[n][0] < 0.5 * e0:
            return j, n
    return None, None


def main():
    lingua = {}
    for r in trascrizione.leggi('ZL'):
        lingua.setdefault(r.pagina, r.lingua)
    per_l = defaultdict(list)
    for pg, pars in e341.pagine().items():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        per_l[lingua.get(pg)].append([r for r in righe if r])
    ris = OrderedDict()
    for lg in ('A', 'B'):
        pr = profilo(per_l[lg])
        j, n = mezza(pr)
        lung = statistics.mean(len(w) for p in per_l[lg] for r in p for w in r)
        ris['lingua ' + lg] = OrderedDict([('profilo', OrderedDict((k, OrderedDict([('eccesso', v[0]), ('coppie', v[1])])) for k, v in pr.items())),
                                           ('mezza_vita_classe', n), ('indice', j), ('lunghezza_media_parola', lung)])
        print(lg, json.dumps(ris['lingua ' + lg], ensure_ascii=False), flush=True)
    ja, jb = ris['lingua A']['indice'], ris['lingua B']['indice']
    if ja is None or jb is None:
        esito = 'n.d.'
    elif abs(ja - jb) <= 1:
        esito = 'stessa memoria in lettere'
    elif jb >= ja + 2:
        esito = 'B ricorda più a lungo anche in lettere'
    else:
        esito = 'A ricorda più a lungo in lettere'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b21_memoria_lettere_ab.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda x: '%+.4f (%d)' % (x['eccesso'], x['coppie']) if x['eccesso'] is not None else '– (0)'
    md = ['# e3b21 — Misurata in lettere, la memoria dura uguale in lingua A e B?', '', 'Preregistrazione: `preregistrazioni/e3b21.md`.', '',
          '| lettere in mezzo | lingua A: eccesso (coppie) | lingua B: eccesso (coppie) |', '|---|---|---|']
    for _, _, n in CLASSI_L:
        md.append('| %s | %s | %s |' % (n, f(ris['lingua A']['profilo'][n]), f(ris['lingua B']['profilo'][n])))
    md += ['', 'Lunghezza media delle parole: A %.2f, B %.2f lettere. Mezza vita in lettere: A %s, B %s.' % (ris['lingua A']['lunghezza_media_parola'], ris['lingua B']['lunghezza_media_parola'], ris['lingua A']['mezza_vita_classe'], ris['lingua B']['mezza_vita_classe']),
           '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b21_memoria_lettere_ab.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
