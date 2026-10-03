# -*- coding: utf-8 -*-
"""Esperimento 259b: come l'e259, con la cache di varianti pesata dal modello di lettere (P(w) / somma sui vicini di s) e
un modello di lettere della pagina (trigrammi delle parole gia' scritte nella pagina, interpolato con quello generale).

Preregistrazione: preregistrazioni/e259b.md. Scrive risultati/e259b_varianti_pesate.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e99_macer as e99
import e259_bit_per_parola as e259
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
NC = 5
NOMI = ('base', 'cache esatta', 'cache varianti pesata', 'lettere', 'lettere della pagina')


class Modello2(e259.Modello):
    def __init__(self, pagine, unita):
        super().__init__(pagine, unita)
        self._pu, self._Z = {}, {}

    def p_u(self, u):
        if u not in self._pu:
            v = ('^', '^') + u + ('$',)
            p = 1.0
            for i in range(2, len(v)):
                p *= self.p_lettera(v[i - 2], v[i - 1], v[i])
            self._pu[u] = p
        return self._pu[u]

    def vicini(self, u):
        out = set()
        for i in range(len(u)):
            if len(u) > 1:
                out.add(u[:i] + u[i + 1:])
            for x in self.alfabeto:
                if x != u[i]:
                    out.add(u[:i] + (x,) + u[i + 1:])
        for i in range(len(u) + 1):
            for x in self.alfabeto:
                out.add(u[:i] + (x,) + u[i:])
        return out

    def Z(self, s):
        if s not in self._Z:
            self._Z[s] = sum(self.p_u(v) for v in self.vicini(s)) or 1e-300
        return self._Z[s]


def componenti(m, pagine):
    out = []
    for p in pagine:
        c3, c2 = Counter(), Counter()
        for k, r in enumerate(p):
            prec = '<s>'
            for j, w in enumerate(r):
                cache = [x for rr in p[max(0, k - e259.RIGHE_CACHE):k] for x in rr] + r[:j]
                u = m.unita(w)
                pe = pv = 0.0
                if cache:
                    pe = sum(1 for x in cache if x == w) / len(cache)
                    pu = m.p_u(u)
                    for x in cache:
                        ux = m.unita(x)
                        if e259.dist1(ux, u):
                            pv += pu / m.Z(ux)
                    pv /= len(cache)
                v = ('^', '^') + u + ('$',)
                pp = 1.0
                for i in range(2, len(v)):
                    g = m.p_lettera(v[i - 2], v[i - 1], v[i])
                    loc = (c3[v[i - 2:i + 1]] + g) / (c2[v[i - 2:i]] + 1)
                    pp *= 0.5 * g + 0.5 * loc
                for i in range(2, len(v)):
                    c3[v[i - 2:i + 1]] += 1
                    c2[v[i - 2:i]] += 1
                out.append((m.p_base(prec, w), pe, pv, m.p_spell(w), pp))
                prec = w
    return out


def em(comp, attivi, iterazioni=e259.ITER_EM):
    lam = [1.0 / len(attivi) if i in attivi else 0.0 for i in range(NC)]
    for _ in range(iterazioni):
        acc = [0.0] * NC
        for c in comp:
            tot = sum(lam[i] * c[i] for i in range(NC)) or 1e-300
            for i in range(NC):
                acc[i] += lam[i] * c[i] / tot
        lam = [a / len(comp) for a in acc]
    return lam


def bit(comp, lam):
    return sum(-math.log2(max(1e-300, sum(lam[i] * c[i] for i in range(NC)))) for c in comp) / len(comp)


def prova(nome, pagine, unita):
    pari, dispari = pagine[0::2], pagine[1::2]
    k = int(len(pari) * 0.8)
    comp_val = componenti(Modello2(pari[:k], unita), pari[k:])
    pesi = OrderedDict([('base + lettere', em(comp_val, {0, 3})), ('+ cache', em(comp_val, {0, 1, 2, 3})), ('+ cache + lettere della pagina', em(comp_val, set(range(NC))))])
    comp = componenti(Modello2(pari, unita), dispari)
    bits = OrderedDict((n, bit(comp, l)) for n, l in pesi.items())
    parole = sum(len(r) for p in pagine for r in p)
    r = OrderedDict([('parole', parole), ('bit', bits), ('pesi_completo', dict(zip(NOMI, pesi['+ cache + lettere della pagina']))),
                     ('riduzione', bits['base + lettere'] - bits['+ cache + lettere della pagina']),
                     ('bit_totali_stimati', bits['+ cache + lettere della pagina'] * parole)])
    print('%s: %s; pesi %s; riduzione %.2f' % (nome, {n: round(b, 2) for n, b in bits.items()},
                                               {n: round(x, 3) for n, x in r['pesi_completo'].items()}, r['riduzione']), flush=True)
    return r


def main():
    vp, vu = e259.voynich()
    n = sum(len(r) for p in vp for r in p)
    pl = [w for _, ps in plinio() for w in ps]
    testi = OrderedDict([('Voynich', (vp, vu)), ('Plinio XX–XXVII (latino tecnico)', (e259.a_pagine(pl, n), e259.lettere)),
                         ('Macer floridus (versi)', ([[ps for ps in c] for c in e99.capitoli()], e259.lettere)),
                         ('Bibbia latina', (e259.a_pagine(lingue.parole('Latin'), n), e259.lettere)),
                         ('Bibbia italiana', (e259.a_pagine(lingue.parole('Italian'), n), e259.lettere))])
    ris = OrderedDict((nome, prova(nome, pag, un)) for nome, (pag, un) in testi.items())
    veri = [r for k, r in ris.items() if k != 'Voynich']
    v = ris['Voynich']
    fin = lambda r: r['bit']['+ cache + lettere della pagina']
    poco = fin(v) < (2 / 3) * min(fin(r) for r in veri) and v['riduzione'] >= 2 * max(r['riduzione'] for r in veri)
    ris['lettura'] = 'il Voynich "dice poco per parola"' if poco else 'informazione per parola paragonabile a una lingua'
    json.dump(ris, open(os.path.join(RISULTATI, 'e259b_varianti_pesate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e259b — Bit per parola con una cache di varianti realistica', '',
          "Come l'e259, con la cache di varianti pesata dal modello di lettere e un modello di lettere della pagina. Preregistrazione: "
          '`preregistrazioni/e259b.md`.', '',
          '| testo | base + lettere | + cache | + cache + lettere della pagina | riduzione | pesi (base, cache, varianti, lettere, pagina) | bit totali |',
          '|---|---|---|---|---|---|---|']
    for nome in testi:
        r = ris[nome]
        md.append('| %s | %.2f | %.2f | %.2f | %.2f | %s | %.0f |' % (nome, r['bit']['base + lettere'], r['bit']['+ cache'], r['bit']['+ cache + lettere della pagina'],
                                                                   r['riduzione'], ', '.join('%.2f' % x for x in r['pesi_completo'].values()), r['bit_totali_stimati']))
    md += ['', 'Lettura: **%s**.' % ris['lettura']]
    open(os.path.join(RISULTATI, 'e259b_varianti_pesate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
