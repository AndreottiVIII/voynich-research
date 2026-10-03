# -*- coding: utf-8 -*-
"""Esperimento 356: (a) lingua A/B e mano omogenee nel bifoglio piu' del caso (dentro il fascicolo)?; (b) ripresa dalle
2 righe sopra per posizione della parola nella riga; (c) nelle coppie con la stessa forma normalizzata, le righe vicine
hanno piu' spesso le stesse scelte di grafia delle righe lontane?

Preregistrazione: preregistrazioni/e356.md. Scrive risultati/e356_eredita.json e .md.
"""
import json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e308_libro_fisico as e308
import e328_livelli as e328
import e337_posizione as e337
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCELTE = ['ch/sh', 'k/t', '-l/-r', 'o-/qo-', '-dy/-ey']


def intestazioni_complete():
    percorso = os.path.join(trascrizione.CARTELLA, trascrizione.FILE['ZL'])
    out = OrderedDict()
    for linea in open(percorso, encoding='latin-1'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', linea)
        if m:
            out[m.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', m.group(2)))
    return out


def parte_a(rnd):
    h = intestazioni_complete()
    out = OrderedDict()
    for nome, chiave in (('lingua', 'L'), ('mano', 'H')):
        pp = [p for p, v in h.items() if v.get(chiave) and v.get(chiave) != '?' and v.get('Q') and v.get('B')]
        bif = defaultdict(list)
        for p in pp:
            bif[(h[p]['Q'], h[p]['B'])].append(p)
        bif = {b: ps for b, ps in bif.items() if len(ps) >= 2}
        per_q = defaultdict(list)
        for b, ps in bif.items():
            per_q[b[0]] += ps

        def omog(lab):
            return statistics.mean(len({lab[p] for p in ps}) == 1 for ps in bif.values())
        lab = {p: h[p][chiave] for p in pp}
        vero = omog(lab)
        nul = []
        for _ in range(1000):
            l2 = dict(lab)
            for q, ps in per_q.items():
                v = [lab[p] for p in ps]
                rnd.shuffle(v)
                l2.update(zip(ps, v))
            nul.append(omog(l2))
        sd = statistics.pstdev(nul)
        z = (vero - statistics.mean(nul)) / sd if sd else 0.0
        out[nome] = OrderedDict([('bifogli', len(bif)), ('omogenei', vero), ('nullo', statistics.mean(nul)), ('z', z),
                                 ('esito', '%s di sessione' % nome if z > 3 else ('no' if z < 2 else 'incerto')),
                                 ('misti', ['%s-%s: %s' % (b[0], b[1], ', '.join('%s %s' % (p, lab[p]) for p in ps)) for b, ps in bif.items() if len({lab[p] for p in ps}) > 1])])
    return out


def posizione(j, n):
    return 'prima' if j == 0 else ('ultima' if j == n - 1 else ('seconda' if j == 1 else ('penultima' if j == n - 2 else 'mezzo')))


def parte_b(pars, rnd):
    def conta(ordini):
        si, tot = Counter(), Counter()
        for par, o in zip(pars, ordini):
            rr = [par[k] for k in o]
            for i in range(2, len(rr)):
                sopra = rr[i - 1] + rr[i - 2]
                n = len(rr[i])
                for j, w in enumerate(rr[i]):
                    ps = posizione(j, n)
                    tot[ps] += 1
                    si[ps] += e341.ha_fonte(w, sopra)
        return {k: si[k] / tot[k] for k in tot}, tot
    base = [list(range(len(p))) for p in pars]
    vero, tot = conta(base)
    nul = [conta([rnd.sample(b, len(b)) for b in base])[0] for _ in range(100)]
    out = OrderedDict()
    for k in ('prima', 'seconda', 'mezzo', 'penultima', 'ultima'):
        xs = [n[k] for n in nul]
        m, sd = statistics.mean(xs), statistics.pstdev(xs)
        out[k] = OrderedDict([('parole', tot[k]), ('quota', vero[k]), ('nullo', m), ('eccesso', vero[k] - m), ('z', (vero[k] - m) / sd if sd else 0.0)])
    return out


def scelte_parola(w):
    s = {}
    for k, y in e337.posti(w):
        s.setdefault(k, y)
    return s


def parte_c(pars):
    vic, lon = [[0, 0] for _ in range(5)], [[0, 0] for _ in range(5)]
    for par in pars:
        norm = [[e328.normalizza(w) for w in r] for r in par]
        for i in range(len(par)):
            for k in range(i):
                d = i - k
                if d not in (1, 2) and d < 3:
                    continue
                gruppo = vic if d <= 2 else lon
                for a, na in zip(par[i], norm[i]):
                    for b, nb in zip(par[k], norm[k]):
                        if na == nb:
                            sa, sb = scelte_parola(a), scelte_parola(b)
                            for c in set(sa) & set(sb):
                                gruppo[c][1] += 1
                                gruppo[c][0] += sa[c] == sb[c]
    out = OrderedDict()
    for c in range(5):
        (sv, nv), (sl, nl) = vic[c], lon[c]
        if nv < 30 or nl < 30:
            continue
        pv, pl = sv / nv, sl / nl
        z = (pv - pl) / math.sqrt(pl * (1 - pl) / nv) if 0 < pl < 1 else 0.0
        out[SCELTE[c]] = OrderedDict([('coppie_vicine', nv), ('stessa_forma_vicine', pv), ('coppie_lontane', nl), ('stessa_forma_lontane', pl), ('z', z)])
    forti = [k for k, v in out.items() if v['z'] > 3]
    return out, ('la copia eredita la grafia' if len(forti) >= 3 else ('no' if not forti else 'in parte: ' + ', '.join(forti)))


def main():
    rnd = random.Random(356)
    a = parte_a(rnd)
    print('a', {k: (v['bifogli'], round(v['omogenei'], 3), round(v['nullo'], 3), round(v['z'], 1)) for k, v in a.items()}, flush=True)
    pars = [p for pp in e341.pagine().values() for p in pp if len(p) >= 4]
    c, esito_c = parte_c(pars)
    print('c', esito_c, {k: (round(v['stessa_forma_vicine'], 3), round(v['stessa_forma_lontane'], 3), round(v['z'], 1)) for k, v in c.items()}, flush=True)
    b = parte_b(pars, random.Random(3561))
    print('b', {k: (round(v['eccesso'], 4), round(v['z'], 1)) for k, v in b.items()}, flush=True)
    json.dump(OrderedDict([('a', a), ('b', b), ('c', c), ('esito_c', esito_c)]), open(os.path.join(RISULTATI, 'e356_eredita.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e356 — Lingua e mano per sessione; dove si riprende nella riga; la grafia ereditata', '', 'Preregistrazione: `preregistrazioni/e356.md`.', '', '## (a)', '',
          '| etichetta | bifogli | omogenei | nullo (dentro il fascicolo) | z | esito |', '|---|---|---|---|---|---|']
    for k, v in a.items():
        md.append('| %s | %d | %.3f | %.3f | %.1f | %s |' % (k, v['bifogli'], v['omogenei'], v['nullo'], v['z'], v['esito']))
    for k, v in a.items():
        md.append('')
        md.append('Bifogli misti per %s: %s.' % (k, '; '.join(v['misti']) or 'nessuno'))
    md += ['', '## (b) ripresa dalle 2 righe sopra per posizione nella riga', '', '| posizione | parole | quota | nullo | eccesso | z |', '|---|---|---|---|---|---|']
    for k, v in b.items():
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %.1f |' % (k, v['parole'], v['quota'], v['nullo'], v['eccesso'], v['z']))
    md += ['', '## (c) stessa scelta di grafia nelle coppie con la stessa forma normalizzata', '', '| scelta | coppie vicine | stessa forma | coppie lontane | stessa forma | z |', '|---|---|---|---|---|---|']
    for k, v in c.items():
        md.append('| %s | %d | %.3f | %d | %.3f | %.1f |' % (k, v['coppie_vicine'], v['stessa_forma_vicine'], v['coppie_lontane'], v['stessa_forma_lontane'], v['z']))
    md += ['', 'Esito (c): **%s**.' % esito_c]
    open(os.path.join(RISULTATI, 'e356_eredita.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
