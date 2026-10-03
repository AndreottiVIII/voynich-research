# -*- coding: utf-8 -*-
"""Esperimento 257: righe gemelle. G = lunghezza della piu' lunga catena di corrispondenze (uguali o a distanza 1)
crescente in entrambe le righe, diviso per le parole della riga; gemella se G >= 0,5. Voynich contro nullo (riga sopra
presa da un'altra pagina della stessa sezione) e contro il generatore e241.

Preregistrazione: preregistrazioni/e257.md. Scrive risultati/e257_righe_gemelle.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE, SOGLIA, MIN_PAROLE = 257, 200, 0.5, 4
D = e237.D


class Gemelle:
    def __init__(self, pagine):
        tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
        self.inventario = sorted({x for w in tutte for x in D(w)})
        self.vic = {}

    def V(self, u):
        if u not in self.vic:
            self.vic[u] = e237.vicini(u, self.inventario) | {u}
        return self.vic[u]

    def G(self, riga, sopra):
        su = [tuple(D(w)) for w in sopra]
        best = [0] * (len(su) + 1)          # best[t] = catena piu' lunga che finisce entro la colonna t
        for w in riga:
            vic = self.V(tuple(D(w)))
            nuovo = best[:]
            for t, x in enumerate(su):
                if x in vic:
                    nuovo[t + 1] = max(nuovo[t + 1], best[t] + 1)
            for t in range(1, len(nuovo)):
                nuovo[t] = max(nuovo[t], nuovo[t - 1])
            best = nuovo
        return best[-1] / len(riga)


def coppie_di(pagine):
    return [(p, rr[k], rr[k - 1]) for p, rr in pagine.items() for k in range(1, len(rr)) if len(rr[k]) >= MIN_PAROLE and len(rr[k - 1]) >= MIN_PAROLE]


def main():
    rnd = random.Random(SEME)
    c = e224.contesto()
    vp = e231.voynich()
    vpag = OrderedDict((p, rr) for p, (_, rr) in vp.items())
    sez = {r.pagina: r.sezione for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(vpag))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(vpag)))
    gpag = e232.pagine_di(e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102))
    ris = OrderedDict()
    for nome, pag in (('Voynich', vpag), ('generatore e241', gpag)):
        g = Gemelle(pag)
        cp = coppie_di(pag)
        Gs = [g.G(r, s) for _, r, s in cp]
        quota = sum(x >= SOGLIA for x in Gs) / len(Gs)
        per_sez = defaultdict(list)
        for p, rr in pag.items():
            per_sez[sez.get(p)] += [(p, r) for r in rr if len(r) >= MIN_PAROLE]
        nulli = []
        for _ in range(REPLICHE):
            xs = []
            for p, r, _ in cp:
                cand = [x for q, x in per_sez[sez.get(p)] if q != p] or [x for q, x in per_sez[sez.get(p)]]
                xs.append(g.G(r, rnd.choice(cand)) >= SOGLIA)
            nulli.append(sum(xs) / len(xs))
        mu, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        ris[nome] = OrderedDict([('coppie', len(cp)), ('quota_gemelle', quota), ('nullo', mu), ('z', (quota - mu) / sd if sd else None),
                                 ('G_medio', statistics.mean(Gs)), ('distribuzione_G', dict(sorted(Counter(round(x, 1) for x in Gs).items())))])
        print(nome, {k: v for k, v in ris[nome].items() if k != 'distribuzione_G'}, flush=True)
    v, g = ris['Voynich'], ris['generatore e241']
    esito = 'righe gemelle' if (v['z'] or 0) > 3 and v['quota_gemelle'] >= 1.5 * g['quota_gemelle'] else 'nessun eccesso'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e257_righe_gemelle.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e257 — Righe gemelle', '',
          'G = catena più lunga di corrispondenze (uguali o a distanza 1) nello stesso ordine fra una riga e quella sopra, / parole della riga; gemella se '
          'G ≥ %.1f. Nullo: riga sopra presa da un\'altra pagina della stessa sezione, %d repliche. Preregistrazione: `preregistrazioni/e257.md`.' % (SOGLIA, REPLICHE), '',
          '| testo | coppie di righe | G medio | quota gemelle | nullo | z |', '|---|---|---|---|---|---|']
    for nome in ('Voynich', 'generatore e241'):
        r = ris[nome]
        md.append('| %s | %d | %.3f | %.3f | %.3f | %.1f |' % (nome, r['coppie'], r['G_medio'], r['quota_gemelle'], r['nullo'], r['z'] or 0))
    md += ['', 'Distribuzione di G nel Voynich: %s.' % v['distribuzione_G'], '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e257_righe_gemelle.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
