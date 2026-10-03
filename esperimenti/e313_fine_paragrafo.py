# -*- coding: utf-8 -*-
"""Esperimento 313: (A) l'ultima riga del paragrafo ha un registro suo? (B) le righe sono regolate sul margine destro
oltre il normale andare a capo?

Preregistrazione: preregistrazioni/e313.md (con la correzione della parte B). Scrive risultati/e313_fine_paragrafo.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e302_cinque_misure as e302

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM, NULLI_B = 1000, 200


def parte_A(righe, rnd):
    """righe: (pagina, inizio, fine, parole). Ultime (non prime) contro interne, permutazioni dentro la pagina."""
    per_pag = defaultdict(list)
    for p, ini, fine, ws in righe:
        if ini:
            continue
        f, n, tot = e302.caratteristiche_riga(ws)
        f['numero di parole'] = float(n)
        f['coppie identiche'] = sum(a == b for a, b in zip(ws, ws[1:])) / max(1, n - 1)
        per_pag[p].append((fine, f, n, tot))
    rr = [x for v in per_pag.values() for x in v]
    nomi = list(rr[0][1])

    def diff(et):
        out = {}
        for k in nomi:
            if k == 'numero di parole':
                peso = lambda r: 1
            elif k.startswith('segno'):
                peso = lambda r: r[3]
            else:
                peso = lambda r: r[2]
            a = [(r[1][k], peso(r)) for r, e in zip(rr, et) if e]
            b = [(r[1][k], peso(r)) for r, e in zip(rr, et) if not e]
            out[k] = sum(v * w for v, w in a) / sum(w for _, w in a) - sum(v * w for v, w in b) / sum(w for _, w in b)
        return out
    vero = diff([r[0] for r in rr])
    nulli = defaultdict(list)
    for _ in range(PERM):
        et = []
        for v in per_pag.values():
            x = [r[0] for r in v]
            rnd.shuffle(x)
            et += x
        for k, d in diff(et).items():
            nulli[k].append(d)
    out = OrderedDict()
    for k in nomi:
        sd = statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('differenza', vero[k]), ('z', (vero[k] - statistics.mean(nulli[k])) / sd if sd else 0.0)])
    forti = [k for k, v in out.items() if abs(v['z']) > 3 and k != 'numero di parole']
    return out, forti


def var_pagina(linee, rnd, lung):
    """log(varianza dei segni per riga / media della varianza con le parole rimescolate fra le righe, stesso numero di
    parole per riga) e la stessa cosa per (ultima parola - media delle altre della riga)."""
    tot = lambda ls: [sum(lung(w) for w in l) for l in ls]
    ult = lambda ls: statistics.mean(lung(l[-1]) - statistics.mean(lung(w) for w in l[:-1]) for l in ls if len(l) >= 2)
    v = statistics.pvariance(tot(linee))
    u = ult(linee)
    tutte = [w for l in linee for w in l]
    nv, nu = [], []
    for _ in range(NULLI_B):
        rnd.shuffle(tutte)
        ls, i = [], 0
        for l in linee:
            ls.append(tutte[i:i + len(l)])
            i += len(l)
        nv.append(statistics.pvariance(tot(ls)))
        nu.append(ult(ls))
    return (math.log(v / statistics.mean(nv)) if v > 0 and statistics.mean(nv) > 0 else None), u - statistics.mean(nu)


def a_capo(parole, larghezza, lung):
    out, cur, n = [], [], 0
    for w in parole:
        if cur and n + lung(w) > larghezza:
            out.append(cur)
            cur, n = [], 0
        cur.append(w)
        n += lung(w)
    if cur:
        out.append(cur)
    return out


def parte_B(righe, rnd):
    lung = lambda w: len(D(w))
    per_pag = defaultdict(list)
    for p, ini, fine, ws in righe:
        if not ini and not fine and len(ws) >= 2:
            per_pag[p].append(ws)
    vere, rifatte, ultime = [], [], []
    for p, linee in per_pag.items():
        if len(linee) < 5:
            continue
        W = statistics.median(sum(lung(w) for w in l) for l in linee)
        r1, u1 = var_pagina(linee, rnd, lung)
        lin2 = [l for l in a_capo([w for l in linee for w in l], W, lung) if len(l) >= 2]
        if len(lin2) < 5 or r1 is None:
            continue
        r2, _ = var_pagina(lin2, rnd, lung)
        if r2 is None:
            continue
        vere.append(r1)
        rifatte.append(r2)
        ultime.append(u1)
    d = [a - b for a, b in zip(vere, rifatte)]
    z = statistics.mean(d) / (statistics.pstdev(d) / math.sqrt(len(d)))
    zu = statistics.mean(ultime) / (statistics.pstdev(ultime) / math.sqrt(len(ultime)))
    lat = [w.lower() for w in lingue.parole('Latin', max_caratteri=200000) if w.isalpha()]
    ll = a_capo(lat, 40, len)
    rl = []
    for i in range(0, len(ll) - 20, 20):
        x, _ = var_pagina([l for l in ll[i:i + 20] if len(l) >= 2], rnd, len)
        if x is not None:
            rl.append(x)
    esito = 'righe regolate oltre il normale a capo' if z < -3 else ('righe meno regolate di un normale a capo' if z > 3 else ('come un normale a capo' if abs(z) < 2 else 'incerto'))
    return OrderedDict([('pagine', len(d)), ('log_rapporto_Voynich', statistics.mean(vere)), ('log_rapporto_a_capo_fisso', statistics.mean(rifatte)),
                        ('log_rapporto_latino_40', statistics.mean(rl)), ('differenza', statistics.mean(d)), ('z', z), ('esito', esito),
                        ('ultima_parola_meno_altre_oltre_il_nullo', statistics.mean(ultime)), ('z_ultima_parola', zu)])


def main():
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append((r.pagina, bool(r.inizio_par), bool(r.fine_par), ws))
    A, forti = parte_A(righe, random.Random(313))
    print('A', {k: (round(v['differenza'], 4), round(v['z'], 1)) for k, v in A.items() if abs(v['z']) > 3}, flush=True)
    esitoA = 'registro dell\'ultima riga' if len(forti) >= 3 else 'nessun registro proprio'
    B = parte_B(righe, random.Random(3131))
    print('B', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in B.items()}, flush=True)
    json.dump(OrderedDict([('A', A), ('A_forti', forti), ('A_esito', esitoA), ('B', B)]), open(os.path.join(RISULTATI, 'e313_fine_paragrafo.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    md = ['# e313 — L\'ultima riga del paragrafo e il margine destro', '', 'Preregistrazione: `preregistrazioni/e313.md` (con la correzione della parte B).', '',
          '## A — Ultime righe contro righe interne (|z| > 3)', '', '| caratteristica | differenza | z |', '|---|---|---|']
    for k, v in A.items():
        if abs(v['z']) > 3:
            md.append('| %s | %+.4f | %.1f |' % (k, v['differenza'], v['z']))
    md += ['', 'Esito A: **%s** (%d caratteristiche oltre al numero di parole).' % (esitoA, len(forti)), '', '## B — Righe e margine destro', '',
           'Log del rapporto fra la varianza dei segni per riga e quella con le parole rimescolate fra le righe (stesso numero di parole per riga), media sulle %d pagine:' % B['pagine'],
           '', '- Voynich vero: %+.3f' % B['log_rapporto_Voynich'], '- le stesse parole a capo a larghezza fissa: %+.3f' % B['log_rapporto_a_capo_fisso'],
           '- latino a capo a 40 lettere: %+.3f' % B['log_rapporto_latino_40'], '',
           'Differenza appaiata vero − a capo fisso %+.3f, z %.1f: **%s**.' % (B['differenza'], B['z'], B['esito']), '',
           'Ultima parola della riga meno la media delle altre della stessa riga, oltre il nullo: %+.3f segni (z %.1f).' % (B['ultima_parola_meno_altre_oltre_il_nullo'], B['z_ultima_parola'])]
    open(os.path.join(RISULTATI, 'e313_fine_paragrafo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
