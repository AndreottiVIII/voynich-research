# -*- coding: utf-8 -*-
"""Esperimento 256: le operazioni di variante e le loro inverse (+e/-e, k->t/t->k) sono equilibrate? E nelle catene
w1 -> w2 -> w3 si torna a w1 (oscillazione)? Nullo: righe rimescolate dentro la pagina. Riferimento: generatore e241.

Preregistrazione: preregistrazioni/e256.md. Scrive risultati/e256_genealogie.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e239_operatore_variante as e239
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE, MINIMO = 256, 200, 50
D = e237.D


def inversa(o):
    op, pos = o.rsplit(' ', 1)
    if op.startswith('+'):
        return '−' + op[1:] + ' ' + pos
    if op.startswith('−'):
        return '+' + op[1:] + ' ' + pos
    a, b = op.split('→')
    return '%s→%s %s' % (b, a, pos)


class Misuratore:
    def __init__(self, pagine):
        tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
        self.inventario = sorted({x for w in tutte for x in D(w)})
        self.vic = {}

    def V(self, u):
        if u not in self.vic:
            self.vic[u] = e237.vicini(u, self.inventario)
        return self.vic[u]

    def misura(self, pagine):
        ops = Counter()
        catene = osc = 0
        for rr in pagine.values():
            sulla, genitore = OrderedDict(), {}
            for k, r in enumerate(rr):
                for w in r:
                    u = tuple(D(w))
                    if sulla and u not in sulla:
                        vic = self.V(u)
                        fonti = [x for x in sulla if x in vic]
                        if fonti:
                            m = max(sulla[x] for x in fonti)
                            s = next(x for x in fonti if sulla[x] == m)
                            ops[e239.operazione(s, u)[1]] += 1
                            if genitore.get(s) is not None:
                                catene += 1
                                osc += genitore[s] == u
                            genitore[u] = s
                        else:
                            genitore[u] = None
                    else:
                        genitore[u] = None
                    sulla[u] = k
                    sulla.move_to_end(u)
        return ops, catene, osc


def squilibri(ops, coppie):
    return {c: (ops[c[0]] - ops[c[1]]) / (ops[c[0]] + ops[c[1]]) for c in coppie}


def prova(nome, pagine, rnd):
    mis = Misuratore(pagine)
    ops, catene, osc = mis.misura(pagine)
    coppie = sorted({tuple(sorted((o, inversa(o)))) for o in ops if ops[o] + ops[inversa(o)] >= MINIMO})
    vere = squilibri(ops, coppie)
    q_osc = osc / catene if catene else 0.0
    nulli, nulli_osc = {c: [] for c in coppie}, []
    for _ in range(REPLICHE):
        mesc = OrderedDict()
        for p, rr in pagine.items():
            rr2 = list(rr)
            rnd.shuffle(rr2)
            mesc[p] = rr2
        o2, c2, s2 = mis.misura(mesc)
        for c, x in squilibri(o2, coppie).items():
            nulli[c].append(x)
        nulli_osc.append(s2 / c2 if c2 else 0.0)
    out = OrderedDict()
    for c in coppie:
        mu, sd = statistics.mean(nulli[c]), statistics.pstdev(nulli[c])
        out['%s / %s' % c] = OrderedDict([('n', ops[c[0]] + ops[c[1]]), ('squilibrio', vere[c]), ('nullo', mu), ('z', (vere[c] - mu) / sd if sd else None)])
    mu, sd = statistics.mean(nulli_osc), statistics.pstdev(nulli_osc)
    r = OrderedDict([('coppie', out), ('catene', catene), ('oscillazione', q_osc), ('oscillazione_nullo', mu), ('oscillazione_z', (q_osc - mu) / sd if sd else None)])
    forti = [(k, v['z']) for k, v in out.items() if abs(v['z'] or 0) > 3]
    print('%s: coppie %d, |z|>3: %s; oscillazione %.3f (nullo %.3f, z %.1f)' % (nome, len(out), forti, q_osc, mu, r['oscillazione_z'] or 0), flush=True)
    return r


def main():
    rnd = random.Random(SEME)
    c = e224.contesto()
    vpag = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(vpag))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(vpag)))
    gp = e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102))
    ris = OrderedDict([('Voynich', prova('Voynich', vpag, rnd)), ('generatore e241', prova('generatore e241', gp, rnd))])
    v = ris['Voynich']
    forti = [k for k, x in v['coppie'].items() if abs(x['z'] or 0) > 3]
    esiti = ['deriva direzionale (%s)' % ', '.join(forti) if len(forti) >= 3 else 'nessuna deriva direzionale',
             'oscillazione' if (v['oscillazione_z'] or 0) > 3 else 'nessuna oscillazione']
    ris['esito'] = '; '.join(esiti)
    json.dump(ris, open(os.path.join(RISULTATI, 'e256_genealogie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e256 — Le genealogie delle parole hanno una direzione?', '',
          'Squilibrio con segno (n(prima) − n(seconda)) / totale per coppie di operazioni inverse con almeno %d occorrenze; nullo: righe rimescolate '
          'nella pagina, %d repliche. Preregistrazione: `preregistrazioni/e256.md`.' % (MINIMO, REPLICHE), '',
          '| coppia | n | squilibrio | nullo | z | generatore: squilibrio, z |', '|---|---|---|---|---|---|']
    g = ris['generatore e241']['coppie']
    for k, x in sorted(v['coppie'].items(), key=lambda kv: -abs(kv[1]['z'] or 0)):
        gx = g.get(k)
        md.append('| %s | %d | %+.3f | %+.3f | %.1f | %s |' % (k, x['n'], x['squilibrio'], x['nullo'], x['z'] or 0,
                                                            '%+.3f, %.1f' % (gx['squilibrio'], gx['z'] or 0) if gx else '–'))
    gg = ris['generatore e241']
    md += ['', 'Oscillazione (w3 = w1 nelle catene w1 → w2 → w3): Voynich %.3f su %d catene (nullo %.3f, z %.1f); generatore %.3f (z %.1f).' % (
        v['oscillazione'], v['catene'], v['oscillazione_nullo'], v['oscillazione_z'] or 0, gg['oscillazione'], gg['oscillazione_z'] or 0), '',
           'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e256_genealogie.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
