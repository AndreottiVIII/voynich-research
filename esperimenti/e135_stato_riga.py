# -*- coding: utf-8 -*-
"""Esperimento 135: uno "stato di riga" comune a piu' scelte di grafia? Varianza per riga di 7 scelte binarie e
accoppiamento dei loro residui fra righe, contro rimescolamenti dentro gli strati (pagina + contesto).

Preregistrazione: preregistrazioni/e135.md. Scrive risultati/e135_stato_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERM = 135, 300
D = misure.divisore(misure.GLIFI_EVA)
SCELTE = ('F1 ch/sh', 'F2 k/t', 'F3 -l/-r', 'F4 e/ee', 'F5 qo-/o-', 'F6 ain/aiin', 'F7 -dy/-ey')
GALLOWS = {'k', 't', 'p', 'f'}
BANCHI = {'ch', 'sh', 'k', 't', 'ckh', 'cth'}


def pos_riga(i, n):
    return 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'


def occorrenze(righe):
    """righe: (pagina, parole). -> lista di (scelta, riga, strato, valore)."""
    out = []
    for k, (pag, ps) in enumerate(righe):
        n = len(ps)
        for i, w in enumerate(ps):
            if not trascrizione.pulita(w):
                continue
            u = D(w)
            pr = pos_riga(i, n)
            L = len(u)
            for j, g in enumerate(u):
                dopo = u[j + 1] if j + 1 < L else '$'
                prima = u[j - 1] if j > 0 else '^'
                if g in ('ch', 'sh'):
                    out.append((0, k, (pag, pr, j == 0, dopo), 1 if g == 'sh' else 0))
                if g in ('k', 't'):
                    out.append((1, k, (pag, prima, dopo, pr), 1 if g == 't' else 0))
                if g in BANCHI and dopo == 'e':
                    m = j + 1
                    while m < L and u[m] == 'e':
                        m += 1
                    out.append((3, k, (pag, g, u[m] if m < L else '$'), 1 if m - j - 1 >= 2 else 0))
            if L >= 2 and u[-1] in ('l', 'r') and u[-2] in ('o', 'a'):
                out.append((2, k, (pag, u[-2], 0 if L <= 3 else 1 if L <= 5 else 2), 1 if u[-1] == 'r' else 0))
            if L >= 3 and u[0] == 'q' and u[1] == 'o' and u[2] in GALLOWS:
                out.append((4, k, (pag, u[2], pr), 1))
            elif L >= 2 and u[0] == 'o' and u[1] in GALLOWS:
                out.append((4, k, (pag, u[1], pr), 0))
            if L >= 4 and u[-4:] == ['a', 'i', 'i', 'n']:
                out.append((5, k, (pag, u[-5] if L >= 5 else '^'), 1))
            elif L >= 3 and u[-3:] == ['a', 'i', 'n']:
                out.append((5, k, (pag, u[-4] if L >= 4 else '^'), 0))
            if L >= 2 and u[-1] == 'y' and u[-2] in ('d', 'e'):
                out.append((6, k, (pag, u[-3] if L >= 3 else '^'), 1 if u[-2] == 'd' else 0))
    return out


def gruppi(occ):
    g = defaultdict(list)
    for i, (f, _, st, _) in enumerate(occ):
        g[(f, st)].append(i)
    return list(g.values())


def statistiche(occ, valori):
    quota = {}
    somma = defaultdict(lambda: [0, 0])
    for (f, _, st, _), v in zip(occ, valori):
        somma[(f, st)][0] += v
        somma[(f, st)][1] += 1
    for k, (a, n) in somma.items():
        quota[k] = a / n
    per_riga = defaultdict(lambda: defaultdict(list))
    for (f, r, st, _), v in zip(occ, valori):
        per_riga[f][r].append((v, v - quota[(f, st)]))
    var = {}
    for f in range(len(SCELTE)):
        q = [sum(x for x, _ in l) / len(l) for l in per_riga[f].values() if len(l) >= 2]
        var[f] = statistics.pvariance(q) if len(q) >= 2 else None
    res = {f: {r: sum(y for _, y in l) / len(l) for r, l in per_riga[f].items()} for f in range(len(SCELTE))}
    cor = {}
    for a in range(len(SCELTE)):
        for b in range(a + 1, len(SCELTE)):
            comuni = [r for r in res[a] if r in res[b]]
            if len(comuni) >= 30:
                x = [res[a][r] for r in comuni]
                y = [res[b][r] for r in comuni]
                mx, my = statistics.mean(x), statistics.mean(y)
                sx = sum((v - mx) ** 2 for v in x) ** 0.5
                sy = sum((v - my) ** 2 for v in y) ** 0.5
                cor[(a, b)] = sum((p - mx) * (q - my) for p, q in zip(x, y)) / (sx * sy) if sx and sy else 0.0
    C = statistics.mean(cor.values()) if cor else None
    return var, cor, C


def permuta(valori, gg, rnd):
    x = valori[:]
    for idx in gg:
        v = [x[i] for i in idx]
        rnd.shuffle(v)
        for i, c in zip(idx, v):
            x[i] = c
    return x


def una(args):
    nome, righe, imposto = args
    rnd = random.Random(SEME)
    occ = occorrenze(righe)
    valori = [v for *_, v in occ]
    if imposto:
        stato = defaultdict(lambda: rnd.randrange(2))
        valori = [(stato[r] if rnd.random() < 0.3 else v) for (_, r, _, _), v in zip(occ, valori)]
    gg = gruppi(occ)
    var, cor, C = statistiche(occ, valori)
    nv, nC, ncor = defaultdict(list), [], defaultdict(list)
    for _ in range(PERM):
        v2, c2, C2 = statistiche(occ, permuta(valori, gg, rnd))
        for f, x in v2.items():
            if x is not None:
                nv[f].append(x)
        for k, x in c2.items():
            ncor[k].append(x)
        nC.append(C2)
    out = OrderedDict([('occorrenze', {SCELTE[f]: sum(1 for o in occ if o[0] == f) for f in range(len(SCELTE))})])
    out['varianza_per_riga'] = OrderedDict()
    for f in range(len(SCELTE)):
        if var[f] is not None and nv[f]:
            m, s = statistics.mean(nv[f]), statistics.pstdev(nv[f])
            out['varianza_per_riga'][SCELTE[f]] = OrderedDict([('rapporto', var[f] / m if m else None), ('z', (var[f] - m) / s if s else None)])
    m, s = statistics.mean(nC), statistics.pstdev(nC)
    out['C'] = OrderedDict([('reale', C), ('nullo', m), ('z', (C - m) / s if s else None)])
    out['correlazioni'] = OrderedDict(('%s ~ %s' % (SCELTE[a], SCELTE[b]), OrderedDict([
        ('r', c), ('z', (c - statistics.mean(ncor[(a, b)])) / statistics.pstdev(ncor[(a, b)]) if statistics.pstdev(ncor[(a, b)]) else None)]))
        for (a, b), c in cor.items())
    return nome, out


def main():
    voy = [(r.pagina, list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    ts = [(i // 29, ps) for i, (_, ps) in enumerate(e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')))]
    lavori = [('Voynich ZL', voy, False), ('controllo positivo: stato di riga imposto (0,3)', voy, True), ('Timm e Schinner, seme 19', ts, False)]
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, lavori):
            ris[nome] = r
            print('%-48s | varianza per riga: %s | C %.4f (nullo %.4f, z %.1f)' % (
                nome, ' '.join('%s %.2f (z %.1f)' % (k.split()[0], v['rapporto'] or 0, v['z'] or 0) for k, v in r['varianza_per_riga'].items()),
                r['C']['reale'], r['C']['nullo'], r['C']['z'] or 0), flush=True)
    v, p, t = ris['Voynich ZL'], ris['controllo positivo: stato di riga imposto (0,3)'], ris['Timm e Schinner, seme 19']
    valido = (p['C']['z'] or 0) > 10
    per_riga = sum((x['z'] or 0) > 3 for x in v['varianza_per_riga'].values())
    stato = per_riga >= 3 and (v['C']['z'] or 0) > 4 and v['C']['reale'] > t['C']['reale']
    ris['valido'], ris['scelte_per_riga'], ris['stato_di_riga'] = valido, per_riga, stato
    print('controllo valido %s | scelte decise per riga %d | stato di riga comune %s' % (valido, per_riga, stato))
    for k, x in v['correlazioni'].items():
        print('   %-30s r %+.3f (z %.1f)' % (k, x['r'], x['z'] or 0))
    with open(os.path.join(RISULTATI, 'e135_stato_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e135 — Esiste uno "stato di riga" comune a più scelte di grafia?', '', 'Nullo: %d rimescolamenti dentro gli strati (pagina + contesto). '
           'Preregistrazione: `preregistrazioni/e135.md`.' % PERM, '', '## Scelte decise per riga (varianza della quota per riga / nullo)', '',
           '| testo | ' + ' | '.join(SCELTE) + ' |', '|---|' + '---|' * len(SCELTE)]
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %s |' % (nome, ' | '.join('%.2f (z %.1f; n %d)' % (r['varianza_per_riga'][f]['rapporto'] or 0, r['varianza_per_riga'][f]['z'] or 0, r['occorrenze'][f])
                                                         if f in r['varianza_per_riga'] else '–' for f in SCELTE)))
    out += ['', '## Accoppiamento fra scelte (media delle correlazioni dei residui di riga)', '', '| testo | C | nullo | z |', '|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %.4f | %.4f | %.1f |' % (nome, r['C']['reale'], r['C']['nullo'], r['C']['z'] or 0))
    out += ['', '### Coppie nel Voynich', '', '| coppia | r | z |', '|---|---|---|']
    for k, x in v['correlazioni'].items():
        out.append('| %s | %+.3f | %.1f |' % (k, x['r'], x['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Scelte decise per riga (z > 3): **%d**. Stato di riga comune: **%s**.' % ('sì' if valido else 'no', per_riga, 'sì' if stato else 'no')]
    with open(os.path.join(RISULTATI, 'e135_stato_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
