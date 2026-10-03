# -*- coding: utf-8 -*-
"""Esperimento e3a01: coppie (a, b) con a ripresa dalla riga sopra (tronco, finale -l/-r) e b uguale a una parola della
riga sopra; quando le fonti violano la regola -l/-r, la finale di a cambia piu' spesso? (lo scriba guarda avanti)

Preregistrazione: preregistrazioni/e3a01.md. Scrive risultati/e3a01_guarda_avanti.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a', 'o', 'y'}
PERM = 10000


def main():
    rnd = random.Random(3101)
    par = OrderedDict()
    for st, pag, npar, ws, seps in e386.righe():
        par.setdefault((pag, npar), []).append((ws, seps))
    ev = []    # (conflitto, cambia_a)
    for righe in par.values():
        for i in range(1, len(righe)):
            sopra = [x for x in righe[i - 1][0] if x]
            tronchi = defaultdict(set)
            for x in sopra:
                f = e380.fin_lr(x)
                if f:
                    tronchi[f[0]].add(f[1])
            insieme = set(sopra)
            ws, seps = righe[i]
            for j in range(len(ws) - 1):
                a, b = ws[j], ws[j + 1]
                if not a or not b or seps[j] != '.':
                    continue
                f = e380.fin_lr(a)
                if not f or len(tronchi.get(f[0], ())) != 1 or b not in insieme:
                    continue
                if b[0] in K:
                    cb = 'K'
                elif b[0] in A:
                    cb = 'A'
                else:
                    continue
                fa = next(iter(tronchi[f[0]]))
                conflitto = (fa == 'l' and cb == 'A') or (fa == 'r' and cb == 'K')
                ev.append((conflitto, f[1] != fa))
    n_conf = sum(1 for c, _ in ev if c)

    def diff(et):
        a = [x for c, (_, x) in zip(et, ev) if c]
        b = [x for c, (_, x) in zip(et, ev) if not c]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else 0.0
    et = [c for c, _ in ev]
    d = diff(et)
    e2 = list(et)
    nul = []
    for _ in range(PERM):
        rnd.shuffle(e2)
        nul.append(diff(e2))
    p = sum(x >= d for x in nul) / PERM
    qc = [x for c, x in ev if c]
    qa = [x for c, x in ev if not c]
    if n_conf < 30:
        esito = 'non decidibile (meno di 30 conflitti)'
    elif d > 0 and p < 0.01:
        esito = 'lo scriba guarda avanti: la finale si adatta alla parola che verrà'
    elif p > 0.1:
        esito = 'non guarda avanti'
    else:
        esito = 'incerto'
    out = OrderedDict([('coppie', len(ev)), ('conflitti', n_conf), ('cambia_a_nei_conflitti', sum(qc) / len(qc) if qc else None),
                       ('cambia_a_negli_accordi', sum(qa) / len(qa) if qa else None), ('differenza', d), ('p', p), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a01_guarda_avanti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a01 — Per -l/-r lo scriba guarda avanti?', '', 'Preregistrazione: `preregistrazioni/e3a01.md`.', '',
          'Coppie: %d, di cui in conflitto %d. La finale di a cambia rispetto alla fonte: %s nei conflitti, %s negli accordi; differenza %+.3f, p %.4f.' % (
              len(ev), n_conf, '%.2f' % out['cambia_a_nei_conflitti'] if qc else 'n.d.', '%.2f' % out['cambia_a_negli_accordi'] if qa else 'n.d.', d, p), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a01_guarda_avanti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
