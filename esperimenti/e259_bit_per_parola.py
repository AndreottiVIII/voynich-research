# -*- coding: utf-8 -*-
"""Esperimento 259: bit per parola con un modello che conosce la copia (mistura di bigramma di parole con modello di
lettere, cache esatta delle ultime righe, cache di varianti a distanza 1, modello di lettere), Voynich contro testi veri.
Addestramento sulle unita' pari, misura sulle dispari; pesi della mistura per EM su una parte tenuta da parte.

Preregistrazione: preregistrazioni/e259.md. Scrive risultati/e259_bit_per_parola.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e99_macer as e99
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
DV = misure.divisore(misure.GLIFI_EVA)
RIGHE_CACHE, PAROLE_RIGA, RIGHE_PAGINA, ITER_EM = 3, 8, 25, 30


def voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            per.setdefault(r.pagina, []).append(ps)
    return list(per.values()), lambda w: tuple(DV(w))


def a_pagine(parole, n):
    parole = parole[:n]
    righe = [parole[i:i + PAROLE_RIGA] for i in range(0, len(parole), PAROLE_RIGA)]
    return [righe[i:i + RIGHE_PAGINA] for i in range(0, len(righe), RIGHE_PAGINA)]


def lettere(w):
    return tuple(w)


class Modello:
    def __init__(self, pagine, unita):
        self.unita = unita
        toks = [w for p in pagine for r in p for w in r]
        self.alfabeto = sorted({x for w in set(toks) for x in unita(w)})
        A = len(self.alfabeto) + 1
        # modello di lettere a trigrammi con Witten-Bell, fine parola '$'
        self.c3, self.c2, self.c1 = Counter(), Counter(), Counter()
        self.f2, self.f1 = defaultdict(set), defaultdict(set)
        for w in toks:
            u = ('^', '^') + unita(w) + ('$',)
            for i in range(2, len(u)):
                self.c3[u[i - 2:i + 1]] += 1
                self.c2[u[i - 1:i + 1]] += 1
                self.c1[u[i]] += 1
                self.f2[u[i - 2:i]].add(u[i])
                self.f1[u[i - 1:i]].add(u[i])
        self.n1 = sum(self.c1.values())
        self.A = A
        self.ctx2, self.ctx1 = Counter(), Counter()
        for k, v in self.c3.items():
            self.ctx2[k[:2]] += v
        for k, v in self.c2.items():
            self.ctx1[k[:1]] += v
        # parole: unigramma e bigramma con Witten-Bell sul modello di lettere
        self.cu = Counter(toks)
        self.N, self.T = len(toks), len(self.cu)
        self.cb, self.cv, self.tv = Counter(), Counter(), defaultdict(set)
        for p in pagine:
            for r in p:
                prec = '<s>'
                for w in r:
                    self.cb[(prec, w)] += 1
                    self.cv[prec] += 1
                    self.tv[prec].add(w)
                    prec = w
        self._spell = {}

    def p_lettera(self, a, b, x):
        p1 = (self.c1[x] + 1) / (self.n1 + self.A)
        t1 = len(self.f1[(b,)])
        n1 = self.ctx1[(b,)]
        p2 = (self.c2[(b, x)] + t1 * p1) / (n1 + t1) if n1 else p1
        t2 = len(self.f2[(a, b)])
        n2 = self.ctx2[(a, b)]
        return (self.c3[(a, b, x)] + t2 * p2) / (n2 + t2) if n2 else p2

    def p_spell(self, w):
        if w not in self._spell:
            u = ('^', '^') + self.unita(w) + ('$',)
            p = 1.0
            for i in range(2, len(u)):
                p *= self.p_lettera(u[i - 2], u[i - 1], u[i])
            self._spell[w] = p
        return self._spell[w]

    def p_base(self, prec, w):
        pu = (self.cu[w] + self.T * self.p_spell(w)) / (self.N + self.T)
        n = self.cv[prec]
        if not n:
            return pu
        t = len(self.tv[prec])
        return (self.cb[(prec, w)] + t * pu) / (n + t)


def dist1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def componenti(m, pagine):
    """Per ogni parola: (p_base, p_cache_esatta, p_cache_varianti, p_lettere)."""
    out = []
    A = len(m.alfabeto)
    for p in pagine:
        for k, r in enumerate(p):
            prec = '<s>'
            for j, w in enumerate(r):
                cache = [x for rr in p[max(0, k - RIGHE_CACHE):k] for x in rr] + r[:j]
                u = m.unita(w)
                if cache:
                    pe = sum(1 for x in cache if x == w) / len(cache)
                    pv = 0.0
                    for x in cache:
                        ux = m.unita(x)
                        if dist1(ux, u):
                            L = len(ux)
                            pv += 1.0 / (L + L * (A - 1) + (L + 1) * A)
                    pv /= len(cache)
                else:
                    pe = pv = 0.0
                out.append((m.p_base(prec, w), pe, pv, m.p_spell(w)))
                prec = w
    return out


def em(comp, attivi):
    lam = [1.0 / len(attivi) if i in attivi else 0.0 for i in range(4)]
    for _ in range(ITER_EM):
        acc = [0.0] * 4
        for c in comp:
            tot = sum(lam[i] * c[i] for i in range(4)) or 1e-300
            for i in range(4):
                acc[i] += lam[i] * c[i] / tot
        lam = [a / len(comp) for a in acc]
    return lam


def bit(comp, lam):
    return sum(-math.log2(max(1e-300, sum(lam[i] * c[i] for i in range(4)))) for c in comp) / len(comp)


def prova(nome, pagine, unita):
    pari, dispari = pagine[0::2], pagine[1::2]
    k = int(len(pari) * 0.8)
    m_parz = Modello(pari[:k], unita)
    comp_val = componenti(m_parz, pari[k:])
    lam_base = em(comp_val, {0, 3})
    lam_tutto = em(comp_val, {0, 1, 2, 3})
    m = Modello(pari, unita)
    comp = componenti(m, dispari)
    b_base, b_tutto = bit(comp, lam_base), bit(comp, lam_tutto)
    parole = sum(len(r) for p in pagine for r in p)
    r = OrderedDict([('parole', parole), ('parole_misurate', len(comp)), ('pesi_base', lam_base), ('pesi_mistura', lam_tutto),
                     ('bit_base', b_base), ('bit_mistura', b_tutto), ('riduzione', b_base - b_tutto), ('bit_totali_stimati', b_tutto * parole)])
    print('%s: base %.2f bit/parola, mistura %.2f (riduzione %.2f), pesi %s, totale %.0f bit' % (
        nome, b_base, b_tutto, b_base - b_tutto, [round(x, 3) for x in lam_tutto], b_tutto * parole), flush=True)
    return r


def main():
    vp, vu = voynich()
    n = sum(len(r) for p in vp for r in p)
    testi = OrderedDict([('Voynich', (vp, vu))])
    pl = [w for _, ps in plinio() for w in ps]
    testi['Plinio XX–XXVII (latino tecnico)'] = (a_pagine(pl, n), lettere)
    testi['Macer floridus (versi)'] = ([[ps for ps in c] for c in e99.capitoli()], lettere)
    testi['Bibbia latina'] = (a_pagine(lingue.parole('Latin'), n), lettere)
    testi['Bibbia italiana'] = (a_pagine(lingue.parole('Italian'), n), lettere)
    ris = OrderedDict()
    for nome, (pag, un) in testi.items():
        ris[nome] = prova(nome, pag, un)
    veri = [r for k, r in ris.items() if k != 'Voynich']
    v = ris['Voynich']
    poco = v['bit_mistura'] < (2 / 3) * min(r['bit_mistura'] for r in veri) and v['riduzione'] >= 2 * max(r['riduzione'] for r in veri)
    ris['lettura'] = ('il Voynich "dice poco per parola"' if poco else 'informazione per parola paragonabile a una lingua')
    ris['nota'] = 'Operativizzazione di "molto piu\'" (fissata scrivendo il codice, prima dei risultati): riduzione almeno doppia della massima fra i testi veri.'
    json.dump(ris, open(os.path.join(RISULTATI, 'e259_bit_per_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e259 — Quanto può dire il Voynich: bit per parola con un modello che copia', '',
          'Base: bigramma di parole con interpolazione di Witten-Bell e modello di lettere per le parole nuove; mistura: base + cache esatta delle '
          'ultime %d righe + cache di varianti a distanza 1 + solo lettere. Pesi per EM su una parte dell\'addestramento; addestramento sulle unità '
          'pari, misura sulle dispari. Preregistrazione: `preregistrazioni/e259.md`.' % RIGHE_CACHE, '',
          '| testo | parole | bit/parola, base | bit/parola, mistura | riduzione | pesi (base, cache, varianti, lettere) | bit totali stimati |',
          '|---|---|---|---|---|---|---|']
    for nome, r in list(ris.items())[:len(testi)]:
        md.append('| %s | %d | %.2f | %.2f | %.2f | %s | %.0f |' % (nome, r['parole'], r['bit_base'], r['bit_mistura'], r['riduzione'],
                                                                ', '.join('%.2f' % x for x in r['pesi_mistura']), r['bit_totali_stimati']))
    md += ['', 'Lettura: **%s**. %s' % (ris['lettura'], ris['nota'])]
    open(os.path.join(RISULTATI, 'e259_bit_per_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
