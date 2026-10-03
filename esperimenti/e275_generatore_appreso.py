# -*- coding: utf-8 -*-
"""Esperimento 275: generatore "appreso". Si campiona dalla mistura dell'e259b (bigramma di parole, cache esatta, cache di
varianti pesata, lettere, lettere della pagina) stimata su tutto il Voynich, con la struttura vera di pagine e righe;
(a) puro, (b) con la riscrittura delle cinque scelte (e145) e la fine riga (eta 1). Verifica sui semi 7-9.

Preregistrazione: preregistrazioni/e275.md. Scrive risultati/e275_generatore_appreso.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e243_riuso_esplicito as e243
import e243b_riuso_su_vocabolario as e243b
import e259_bit_per_parola as e259
import e259b_varianti_pesate as e259b
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI, MAX_UNITA, CANDIDATE_FINE = (7, 8, 9), 15, 8


class Campionatore:
    def __init__(self, pagine, unita, pesi):
        self.m = e259b.Modello2(pagine, unita)
        self.unita = unita
        self.pesi = pesi
        self.lettere = list(self.m.alfabeto) + ['$']
        self.uni = (list(self.m.cu), [self.m.cu[w] for w in self.m.cu])
        foll = defaultdict(Counter)
        for (a, b), n in self.m.cb.items():
            foll[a][b] += n
        self.foll = {a: (list(c), list(c.values())) for a, c in foll.items()}

    def lettere_parola(self, rnd, c3=None, c2=None):
        a, b, out = '^', '^', []
        while len(out) < MAX_UNITA:
            ps = []
            for x in self.lettere:
                g = self.m.p_lettera(a, b, x)
                if c3 is not None:
                    g = 0.5 * g + 0.5 * (c3[(a, b, x)] + g) / (c2[(a, b)] + 1)
                ps.append(g)
            x = rnd.choices(self.lettere, ps)[0]
            if x == '$':
                break
            out.append(x)
            a, b = b, x
        return ''.join(out) if out else rnd.choices(*self.uni)[0]

    def base(self, rnd, prec):
        n, t = self.m.cv[prec], len(self.m.tv[prec])
        if n and rnd.random() < n / (n + t):
            return rnd.choices(*self.foll[prec])[0]
        if rnd.random() < self.m.N / (self.m.N + self.m.T):
            return rnd.choices(*self.uni)[0]
        return self.lettere_parola(rnd)

    def variante(self, rnd, s):
        vs = list(self.m.vicini(self.unita(s)))
        return ''.join(rnd.choices(vs, [self.m.p_u(v) for v in vs])[0])

    def parola(self, rnd, prec, cache, c3, c2):
        k = rnd.choices(range(5), self.pesi)[0]
        if k in (1, 2) and not cache:
            k = 0
        if k == 0:
            return self.base(rnd, prec)
        if k == 1:
            return rnd.choice(cache)
        if k == 2:
            return self.variante(rnd, rnd.choice(cache))
        if k == 3:
            return self.lettere_parola(rnd)
        return self.lettere_parola(rnd, c3, c2)


def genera(cmp, c, seme, regole):
    rnd = random.Random(seme)
    Dv = c['D']
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in c['P'].items():
        c3, c2 = Counter(), Counter()
        ultime = []
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            n = len(ps)
            riga, prec = [], '<s>'
            for j in range(n):
                cache = [w for r in ultime for w in r] + riga
                if regole and j == n - 1 and n > 1:
                    cand = [cmp.parola(rnd, prec, cache, c3, c2) for _ in range(CANDIDATE_FINE)]
                    w = rnd.choices(cand, [c['rapporto'].get(Dv(x)[-1], 1.0) if x else 1.0 for x in cand])[0]
                else:
                    w = cmp.parola(rnd, prec, cache, c3, c2)
                riga.append(w)
                v = ('^', '^') + tuple(Dv(w)) + ('$',)
                for i in range(2, len(v)):
                    c3[v[i - 2:i + 1]] += 1
                    c2[v[i - 2:i]] += 1
                prec = w
            if regole:
                riga = e145.riscrivi(riga, h, c['q'], rnd)
            ultime = (ultime + [riga])[-3:]
            righe.append((pag, ini, riga))
    return righe


def main():
    c = e224.contesto()
    vp, vu = e259.voynich()
    pesi = list(json.load(open(os.path.join(RISULTATI, 'e259b_varianti_pesate.json'), encoding='utf-8'))['Voynich']['pesi_completo'].values())
    cmp = Campionatore(vp, vu, pesi)
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    vi = e266.voynich_ini()
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    ris = OrderedDict([('pesi', pesi)])
    for nome, regole in (('(a) campionamento puro', False), ('(b) con scelte di riga e fine riga', True)):
        ver = []
        for s in SEMI:
            rr = [(p, ini, [w for w in ps if w]) for p, ini, ps in genera(cmp, c, s, regole)]
            rr = [x for x in rr if x[2]]
            gp = e232.pagine_di(rr)
            r = OrderedDict([('AUC_e231', e231.confronto(vpag, gp, rif)['AUC']), ('AUC_e266', e266.confronto(vt266, e266.tabella(e243b.righe_ini(rr), rif266))['AUC']),
                             ('pagella_e224', e236.pagella(c, rr)), ('profilo', e237.profilo(gp)), ('R_parole_rare', e243.R_rare(rr)),
                             ('esempio', [' '.join(ps) for _, _, ps in rr[:3]])])
            ver.append(r)
            print('%s seme %d: pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f | R rare %.1f | %s' % (
                nome, s, r['pagella_e224']['pagella'], r['pagella_e224']['riga'], r['pagella_e224']['mancano'], r['AUC_e231'], r['AUC_e266'],
                r['R_parole_rare'], r['esempio'][0][:60]), flush=True)
        ris[nome] = OrderedDict([('verifica', ver), ('pagella_media', statistics.mean(x['pagella_e224']['pagella'] for x in ver)),
                                 ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in ver)), ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in ver))])
    promettente = any(ris[k]['pagella_media'] >= 16 or ris[k]['AUC_e266_media'] < 0.937 for k in ('(a) campionamento puro', '(b) con scelte di riga e fine riga'))
    ris['esito'] = 'promettente' if promettente else 'non promettente'
    json.dump(ris, open(os.path.join(RISULTATI, 'e275_generatore_appreso.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e275 — Un generatore "appreso" dal modello a mistura dell\'e259b', '',
          'Pesi (base, cache, varianti, lettere, lettere della pagina): %s. Preregistrazione: `preregistrazioni/e275.md`.' % ', '.join('%.2f' % x for x in pesi), '',
          '| variante | seme | pagella | riga | mancano | AUC e231 | AUC e266 | R | V | N | R parole rare |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome in ('(a) campionamento puro', '(b) con scelte di riga e fine riga'):
        for s, x in zip(SEMI, ris[nome]['verifica']):
            md.append('| %s | %d | %d/18 | %s | %s | %.3f | %.3f | %.1f%% | %.1f%% | %.1f%% | %.1f |' % (
                nome, s, x['pagella_e224']['pagella'], 'sì' if x['pagella_e224']['riga'] else 'no', ', '.join(x['pagella_e224']['mancano']) or '—',
                x['AUC_e231'], x['AUC_e266'], 100 * x['profilo']['R'], 100 * x['profilo']['V'], 100 * x['profilo']['N'], x['R_parole_rare']))
    md += ['', 'Medie: ' + '; '.join('%s: pagella %.1f, AUC e231 %.3f, e266 %.3f' % (k, ris[k]['pagella_media'], ris[k]['AUC_e231_media'], ris[k]['AUC_e266_media'])
                                     for k in ('(a) campionamento puro', '(b) con scelte di riga e fine riga')) + '.', '',
           'Esempio (b, seme 7): %s' % ' / '.join(ris['(b) con scelte di riga e fine riga']['verifica'][0]['esempio']), '', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e275_generatore_appreso.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
