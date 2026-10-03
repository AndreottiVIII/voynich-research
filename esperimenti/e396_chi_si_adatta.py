# -*- coding: utf-8 -*-
"""Esperimento 396: coppie (a, b) entrambe con fonte nella riga sopra; quando le fonti violano la regola di qo- (fonte
di a in C con fonte di b qo, o fonte di a in V con fonte di b o), cambia piu' spesso b (la forma qo/o) o a (la classe
della finale)?

Preregistrazione: preregistrazioni/e396.md. Scrive risultati/e396_chi_si_adatta.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 10000


def classe(s):
    return 'V' if s in V else ('C' if s in C else None)


def main():
    rnd = random.Random(396)
    par = OrderedDict()
    for st, pag, npar, ws, seps in e386.righe():
        par.setdefault((pag, npar), []).append((ws, seps))
    ev = []    # (conflitto, cambia_a, cambia_b)
    for righe in par.values():
        for i in range(1, len(righe)):
            nuclei, tronchi = defaultdict(set), defaultdict(set)
            for x in righe[i - 1][0]:
                if not x:
                    continue
                q = e380.ini_qo(x)
                if q:
                    nuclei[q[0]].add(q[1])
                if len(x) >= 2 and classe(x[-1]):
                    tronchi[x[:-1]].add(classe(x[-1]))
            ws, seps = righe[i]
            for j in range(len(ws) - 1):
                a, b = ws[j], ws[j + 1]
                if not a or not b or seps[j] != '.' or len(a) < 2:
                    continue
                q = e380.ini_qo(b)
                ca = classe(a[-1])
                if not q or not ca or len(nuclei.get(q[0], ())) != 1 or len(tronchi.get(a[:-1], ())) != 1:
                    continue
                fb = next(iter(nuclei[q[0]]))
                fa = next(iter(tronchi[a[:-1]]))
                conflitto = (fa == 'C' and fb == 'qo') or (fa == 'V' and fb == 'o')
                ev.append((conflitto, ca != fa, q[1] != fb))
    n_conf = sum(1 for e in ev if e[0])

    def diff(etich, k):
        a = [e[k] for c, e in zip(etich, ev) if c]
        b = [e[k] for c, e in zip(etich, ev) if not c]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else 0.0
    et = [e[0] for e in ev]
    ris = OrderedDict()
    for nome, k in (('cambia a (finale della parola prima)', 1), ('cambia b (qo/o della parola dopo)', 2)):
        d = diff(et, k)
        nul = []
        e2 = list(et)
        for _ in range(PERM):
            rnd.shuffle(e2)
            nul.append(diff(e2, k))
        qc = [e[k] for e in ev if e[0]]
        qa = [e[k] for e in ev if not e[0]]
        ris[nome] = OrderedDict([('quota_conflitto', sum(qc) / len(qc) if qc else None), ('quota_accordo', sum(qa) / len(qa) if qa else None), ('differenza', d), ('p', sum(x >= d for x in nul) / PERM)])
    pa, pb = ris['cambia a (finale della parola prima)']['p'], ris['cambia b (qo/o della parola dopo)']['p']
    if n_conf < 30:
        esito = 'non decidibile (meno di 30 conflitti)'
    elif pb < 0.01 and pa < 0.01:
        esito = 'tutte e due'
    elif pb < 0.01:
        esito = 'si adatta la parola dopo (si scrive guardando quel che c\'è già)'
    elif pa < 0.01:
        esito = 'si adatta la parola prima (lo scriba pianifica in avanti)'
    else:
        esito = 'non deciso'
    out = OrderedDict([('coppie', len(ev)), ('conflitti', n_conf), ('misure', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e396_chi_si_adatta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e396 — Chi si adatta a chi: la parola dopo o quella prima?', '', 'Preregistrazione: `preregistrazioni/e396.md`. Coppie con entrambe le parole riprese dalla riga sopra: %d, di cui in conflitto %d.' % (len(ev), n_conf), '',
          '| misura | quota nei conflitti | quota negli accordi | differenza | p |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %s | %s | %+.3f | %.4f |' % (k, '%.2f' % x['quota_conflitto'] if x['quota_conflitto'] is not None else '', '%.2f' % x['quota_accordo'] if x['quota_accordo'] is not None else '', x['differenza'], x['p']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e396_chi_si_adatta.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
