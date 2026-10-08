# -*- coding: utf-8 -*-
"""Esperimento e3c85: la "catena di segni" sopravvive a un nullo che riproduce la grammatica della parola?

Nota A7 del revisore: lo spazio prevedibile, i tagli che danno parole vere e il vocabolario che riempie le forme
potrebbero venire solo dalla forma delle parole (grammatica della parola: iniziali e finali tipiche, vocabolario
concentrato), non da un legame fra parole. Si misurano le proprietà della scoperta 1 sul Voynich e su tre nulli costruiti
dallo stesso sottoinsieme (stesse righe, stesse lunghezze in parole):

- N1 "parole indipendenti": ogni parola estratta a caso dalle parole del sottoinsieme (stesso vocabolario e frequenze,
  nessun legame fra parole);
- N2 "rimescolate nella riga": le parole di ogni riga in ordine casuale;
- N3 "grammatica della parola": parole nuove generate da una catena di segni di ordine 2 dentro la parola (inizio e
  fine inclusi), addestrata sulle parole del sottoinsieme, una parola indipendente dall'altra.

Misure (codice degli esperimenti originali): F1 dello spazio (e3a58), attestazione dei tagli sbagliati (e3a67),
riempimento delle forme (e3a61), ρ dentro/fra le parole (e3a49), ρ frequenza–forma (e3a55), giuntura E (e377).
Parte 2, descrittiva: le stesse statistiche nelle 24 lingue naturali contro l'entropia condizionata h2, e il residuo del
Voynich.

Preregistrazione: preregistrazioni/e3c85.md. Scrive risultati/e3c85_nullo_grammatica_parola.json e .md.
SOLO_CONTROLLI=1: prova del codice su testi di controllo (latino, una catena vera, parole indipendenti), niente Voynich.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e377_giuntura_gibberish as e377
import e381_parole_intere as e381
import e3a49_dentro_fra as e3a49
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58
import e3a61_forme_riempite as e3a61
import e3a67_spazi_rifatti as e3a67
import e3c84_confronti_per_lingua as e3c84

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
PERM = 50
STAT = ('spazio', 'attestazione', 'riempimento', 'rispecchiamento', 'frequenza_forma', 'giuntura')


class Grammatica:
    """Catena di segni di ordine 2 dentro la parola, addestrata sulle parole (occorrenze)."""

    def __init__(self, parole):
        self.t = defaultdict(Counter)
        for w in parole:
            s = ('^', '^') + tuple(w) + ('$',)
            for i in range(2, len(s)):
                self.t[s[i - 2], s[i - 1]][s[i]] += 1
        self.cum = {k: (list(c), np.cumsum(list(c.values()))) for k, c in self.t.items()}

    def parola(self, rnd):
        while True:
            a, b, w = '^', '^', []
            while len(w) < 15:
                segni, cum = self.cum[a, b]
                x = segni[int(np.searchsorted(cum, rnd.random() * cum[-1], side='right'))]
                if x == '$':
                    break
                w.append(x)
                a, b = b, x
            if w and len(w) < 15:
                return tuple(w)


def nulli(righe, rnd):
    parole = [w for r in righe for w in r]
    g = Grammatica(parole)
    return OrderedDict([('N1 parole indipendenti', [[rnd.choice(parole) for _ in r] for r in righe]),
                        ('N2 rimescolate nella riga', [rnd.sample(r, len(r)) for r in righe]),
                        ('N3 grammatica della parola', [[g.parola(rnd) for _ in r] for r in righe])])


def misura(righe, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    parole = [w for r in righe for w in r]
    return OrderedDict([('spazio', e3a58.f1(righe)), ('attestazione', e3a67.attestazione(righe, rnd)[0]),
                        ('riempimento', e3a61.riempimento(parole)[0]), ('rispecchiamento', e3a49.rho(righe)[0]),
                        ('frequenza_forma', e3a55.rho(parole)), ('giuntura', e377.prova(righe, rnd, PERM)['E'])])


def mediane(lista):
    return OrderedDict((k, statistics.median(x[k] for x in lista if x[k] is not None)) for k in STAT)


# sotto queste soglie il valore del testo è rumore e il confronto con il nullo non ha senso
MINIMO = {'spazio': 0.0, 'attestazione': 0.0, 'riempimento': 0.0, 'rispecchiamento': 0.2, 'frequenza_forma': 0.2, 'giuntura': 0.02}


def verdetto(v, n, s):
    if v is None or n is None or v <= MINIMO[s]:
        return 'non applicabile'
    r = n / v
    return 'spiegata dal nullo' if r >= 0.8 else ('in parte' if r >= 0.5 else 'non spiegata')


def confronto(nome, campioni, rnd):
    """campioni: lista di testi (liste di righe). Misura il testo e i tre nulli di ciascuno; mediane e verdetti."""
    vero, nul = [], defaultdict(list)
    for righe in campioni:
        vero.append(misura(righe, rnd))
        for k, t in nulli(righe, rnd).items():
            nul[k].append(misura(t, rnd))
        print(nome, json.dumps(vero[-1], default=float), flush=True)
    V = mediane(vero)
    out = OrderedDict([('testo', V)])
    for k, lst in nul.items():
        N = mediane(lst)
        out[k] = OrderedDict((s, OrderedDict([('valore', N[s]), ('rapporto', (N[s] / V[s]) if V[s] else None), ('verdetto', verdetto(V[s], N[s], s))])) for s in STAT)
    return out


# --------------------------------------------------------------------------- parte 2: h2
def h2(righe):
    """Entropia condizionata del segno dato il precedente, sul testo corrente con lo spazio come segno."""
    c2, c1 = Counter(), Counter()
    for r in righe:
        s = ['_']
        for w in r:
            s += list(w) + ['_']
        for a, b in zip(s, s[1:]):
            c2[a, b] += 1
            c1[a] += 1
    n = sum(c2.values())
    return -sum(k / n * math.log2(k / c1[a]) for (a, b), k in c2.items())


def residui(voy_h2, voy_val, lingue_h2, lingue_val):
    ks = [k for k in lingue_h2 if k in lingue_val and lingue_val[k] is not None]
    x = np.array([lingue_h2[k] for k in ks])
    y = np.array([lingue_val[k] for k in ks])
    b, a = np.polyfit(x, y, 1)
    res = y - (a + b * x)
    sd = float(np.std(res, ddof=2))
    rv = voy_val - (a + b * voy_h2)
    return OrderedDict([('lingue', len(ks)), ('pendenza', float(b)), ('r', float(np.corrcoef(x, y)[0, 1])),
                        ('previsto_al_h2_del_voynich', float(a + b * voy_h2)), ('residuo_voynich', float(rv)),
                        ('residuo_in_sd', rv / sd if sd else None), ('lingue_con_residuo_maggiore', int(np.sum(res > rv)))])


def parte2(voy_campioni, V, rnd):
    testi = OrderedDict((k.replace('.txt', ''), e3a58.righe_prime(t)) for k, t in e381.testi().items())
    h = {k: h2(t) for k, t in testi.items()}
    val = OrderedDict()
    pre = e3c84.parte_a()
    for s, chiave in (('spazio', 'spazio'), ('attestazione', 'attestazione'), ('riempimento', 'riempimento'),
                      ('rispecchiamento', 'rispecchiamento'), ('frequenza_forma', 'frequenza_forma')):
        val[s] = pre[chiave][1]
    # la giuntura per testo non è salvata nell'e3c84 (solo per lingua): si ricalcola qui con la stessa misura
    val['giuntura'] = {k: e377.prova(t, rnd, PERM)['E'] for k, t in testi.items()}

    def per_lingua(d):
        g = defaultdict(list)
        for t, v in d.items():
            cat, ling = e3c84.etichetta(t)
            if cat != 'Conlangs' and v is not None:
                g[ling].append(v)
        return {k: statistics.median(v) for k, v in g.items()}
    hl = per_lingua(h)
    vh = statistics.median(h2(c) for c in voy_campioni)
    out = OrderedDict([('h2_voynich', vh), ('h2_lingue', OrderedDict(sorted(hl.items(), key=lambda kv: kv[1])))])
    for s in STAT:
        out[s] = residui(vh, V[s], hl, per_lingua(val[s]))
    return out


# --------------------------------------------------------------------------- controlli (prova del codice)
def catena_vera(righe, rnd, spazio_fisso=None):
    """Testo con una vera catena di segni attraverso lo spazio: un flusso continuo di segni (catena di ordine 1 stimata
    sul testo senza spazi) in cui lo spazio si mette fra due segni con la probabilità che ha quella coppia nel testo di
    partenza (regola dell'e3a58). Righe con le stesse lunghezze in parole."""
    c = defaultdict(Counter)
    for r in righe:
        s = [x for w in r for x in w]
        for a, b in zip(s, s[1:]):
            c[a][b] += 1
    cum = {a: (list(x), np.cumsum(list(x.values()))) for a, x in c.items()}
    reg = e3a58.Regola(e3a58.posizioni(righe))
    out = []
    a = righe[0][0][0]
    for r in righe:
        riga, w = [], [a]
        while len(riga) < len(r):
            segni, cs = cum[a]
            x = segni[int(np.searchsorted(cs, rnd.random() * cs[-1], side='right'))]
            if rnd.random() < (spazio_fisso if spazio_fisso is not None else reg.p(a, x)):
                riga.append(tuple(w))
                w = [x]
            else:
                w.append(x)
            a = x
        out.append(riga)
    return out


def main():
    rnd = random.Random(3385)
    if SOLO_CONTROLLI:
        lat = e3a58.righe_prime(e381.testi()['Historical - Latin - Literary - NT (Vulgate).txt'])
        ris = OrderedDict()
        ris['latino'] = confronto('latino', [lat], rnd)
        ris['catena vera (dal latino)'] = confronto('catena', [catena_vera(lat, rnd)], rnd)
        ris['catena con spazi a caso (dal latino)'] = confronto('catena', [catena_vera(lat, rnd, 0.18)], rnd)
        ris['parole indipendenti (dal latino)'] = confronto('indip', [[[rnd.choice([w for r in lat for w in r]) for _ in r] for r in lat]], rnd)
        for k, x in ris.items():
            print('==', k, json.dumps(x['testo'], default=float))
            for n in ('N1 parole indipendenti', 'N3 grammatica della parola'):
                print('   ', n, {s: (round(x[n][s]['valore'], 3) if x[n][s]['valore'] is not None else None, x[n][s]['verdetto']) for s in STAT})
        return
    campioni = e3c84.voynich_sottoinsiemi(rnd)
    ris = confronto('Voynich', campioni, rnd)
    p2 = parte2(campioni, ris['testo'], rnd)
    # esito della scoperta 1: legame fra parole (ρ dentro/fra e giuntura) contro proprietà della forma delle parole
    legame = all(ris[n][s]['verdetto'] == 'non spiegata' for n in ('N1 parole indipendenti', 'N3 grammatica della parola') for s in ('rispecchiamento', 'giuntura'))
    forma = OrderedDict((s, ris['N3 grammatica della parola'][s]['verdetto']) for s in ('spazio', 'attestazione', 'riempimento'))
    esito = OrderedDict([('legame_fra_parole', 'non è un effetto della grammatica della parola' if legame else 'in parte o del tutto spiegato dalla grammatica della parola'),
                         ('proprieta_di_forma_sotto_N3', forma)])
    out = OrderedDict([('voynich_e_nulli', ris), ('h2', p2), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c85_nullo_grammatica_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c85 — La catena di segni regge a un nullo con la grammatica della parola?', '',
          'Preregistrazione: `preregistrazioni/e3c85.md`. Mediane su 5 sottoinsiemi di 10.000 parole; per ogni nullo: valore, rapporto nullo/Voynich, verdetto (≥ 0,8 spiegata; 0,5–0,8 in parte; < 0,5 non spiegata).', '',
          '| statistica | Voynich | N1 parole indipendenti | N2 rimescolate nella riga | N3 grammatica della parola |', '|---|---|---|---|---|']
    for s in STAT:
        celle = []
        for n in ('N1 parole indipendenti', 'N2 rimescolate nella riga', 'N3 grammatica della parola'):
            x = ris[n][s]
            celle.append('%.3f (%s, %s)' % (x['valore'], '%.2f' % x['rapporto'] if x['rapporto'] is not None else '–', x['verdetto']))
        md.append('| %s | %.3f | %s |' % (s, ris['testo'][s], ' | '.join(celle)))
    md += ['', '## A parità di h2 (24 lingue naturali, descrittiva)', '', 'h2 del Voynich %.2f; lingue da %.2f a %.2f.' % (p2['h2_voynich'], min(p2['h2_lingue'].values()), max(p2['h2_lingue'].values())), '',
           '| statistica | r con h2 nelle lingue | previsto al h2 del Voynich | Voynich | residuo (sd) | lingue con residuo maggiore |', '|---|---|---|---|---|---|']
    for s in STAT:
        x = p2[s]
        md.append('| %s | %.2f | %.3f | %.3f | %s | %d |' % (s, x['r'], x['previsto_al_h2_del_voynich'], ris['testo'][s], '%.1f' % x['residuo_in_sd'] if x['residuo_in_sd'] is not None else '–', x['lingue_con_residuo_maggiore']))
    md += ['', 'Esito: legame fra parole **%s**; proprietà di forma sotto N3: %s.' % (esito['legame_fra_parole'], ', '.join('%s %s' % kv for kv in forma.items()))]
    open(os.path.join(RISULTATI, 'e3c85_nullo_grammatica_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(esito, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
