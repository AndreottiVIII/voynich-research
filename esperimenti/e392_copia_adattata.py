# -*- coding: utf-8 -*-
"""Esperimento 392: una parola qo/o + gallows ripresa dalla riga sopra (stesso nucleo) segue la forma della fonte o la
regola della nuova vicina (ultimo segno della parola prima)?

Preregistrazione: preregistrazioni/e392.md. Scrive risultati/e392_copia_adattata.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
PERM = 10000


def effetto(ev, chiave, gruppo):
    """Media pesata, dentro ogni gruppo, di P(qo | chiave vera) - P(qo | chiave falsa)."""
    per = defaultdict(list)
    for e in ev:
        per[e[gruppo]].append(e)
    num = den = 0.0
    for xs in per.values():
        a = [e[2] for e in xs if e[chiave]]
        b = [e[2] for e in xs if not e[chiave]]
        if a and b:
            num += len(xs) * (sum(a) / len(a) - sum(b) / len(b))
            den += len(xs)
    return num / den if den else 0.0


def nullo(ev, chiave, gruppo, rnd):
    per = defaultdict(list)
    for i, e in enumerate(ev):
        per[e[gruppo]].append(i)
    out = []
    for _ in range(PERM):
        ev2 = [list(e) for e in ev]
        for idx in per.values():
            vals = [ev[i][chiave] for i in idx]
            rnd.shuffle(vals)
            for i, v in zip(idx, vals):
                ev2[i][chiave] = v
        out.append(effetto(ev2, chiave, gruppo))
    return out


def main():
    rnd = random.Random(392)
    par = OrderedDict()
    for st, pag, npar, ws, seps in e386.righe():
        par.setdefault((pag, npar), []).append((ws, seps))
    ev = []    # (vicina in V, fonte qo, w qo)
    for righe in par.values():
        for i in range(1, len(righe)):
            sopra = defaultdict(set)
            for x in righe[i - 1][0]:
                q = e380.ini_qo(x) if x else None
                if q:
                    sopra[q[0]].add(q[1])
            ws, seps = righe[i]
            for j in range(1, len(ws)):
                w, a = ws[j], ws[j - 1]
                if not w or not a or seps[j - 1] != '.':
                    continue
                q = e380.ini_qo(w)
                if not q or len(sopra.get(q[0], ())) != 1:
                    continue
                if a[-1] in V:
                    cl = True
                elif a[-1] in C:
                    cl = False
                else:
                    continue
                ev.append((cl, next(iter(sopra[q[0]])) == 'qo', q[1] == 'qo'))
    tab = Counter((e[1], e[0], e[2]) for e in ev)
    righe_tab = OrderedDict()
    for fonte in (True, False):
        for vic in (True, False):
            n = tab[(fonte, vic, True)] + tab[(fonte, vic, False)]
            righe_tab['fonte %s, vicina %s' % ('qo' if fonte else 'o', 'V' if vic else 'C')] = OrderedDict([('eventi', n), ('P_qo', tab[(fonte, vic, True)] / n if n else None)])
    e_vic = effetto(ev, 0, 1)
    p_vic = sum(x >= e_vic for x in nullo(ev, 0, 1, rnd)) / PERM
    e_fon = effetto(ev, 1, 0)
    p_fon = sum(x >= e_fon for x in nullo(ev, 1, 0, rnd)) / PERM
    if p_vic < 0.01 and p_fon < 0.01:
        esito = 'entrambe le cose'
    elif p_vic < 0.01:
        esito = 'la copia si adatta alla nuova vicina: la regola si applica scrivendo'
    elif p_fon < 0.01:
        esito = 'la copia conserva la forma della fonte'
    else:
        esito = 'non deciso'
    out = OrderedDict([('eventi', len(ev)), ('tabella', righe_tab), ('effetto_vicina', e_vic), ('p_vicina', p_vic), ('effetto_fonte', e_fon), ('p_fonte', p_fon), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e392_copia_adattata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e392 — Una parola copiata dalla riga sopra si adatta alla nuova vicina?', '', 'Preregistrazione: `preregistrazioni/e392.md`. V = parola prima in -y/-o/-d; C = in -n/-r/-s/-m.', '',
          '| fonte nella riga sopra | vicina | eventi | P(qo) |', '|---|---|---|---|']
    for k, x in righe_tab.items():
        f, v = k.split(', ')
        md.append('| %s | %s | %d | %s |' % (f, v, x['eventi'], '%.2f' % x['P_qo'] if x['P_qo'] is not None else ''))
    md += ['', 'Effetto della vicina (a parità di fonte): %+.3f, p %.4f. Effetto della fonte (a parità di vicina): %+.3f, p %.4f.' % (e_vic, p_vic, e_fon, p_fon), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e392_copia_adattata.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
