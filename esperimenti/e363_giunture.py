# -*- coding: utf-8 -*-
"""Esperimento 363: (a) quanto le parole uniche non varianti ("forme nuove") sono fuori dalle regole dei segni nel
Voynich rispetto a latino e italiano; (b) le forme nuove contengono coppie di segni tipiche del confine fra due parole?

Preregistrazione: preregistrazioni/e363.md. Scrive risultati/e363_giunture.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
ALFA, N_PAROLE = 0.1, 32000


def transizioni(u):
    s = ('^', '^') + tuple(u) + ('$',)
    return [((s[i - 2], s[i - 1]), s[i]) for i in range(2, len(s))]


def simili(tipi, U):
    piano, jolly, canc = defaultdict(set), defaultdict(set), defaultdict(set)
    for w in tipi:
        u = U[w]
        piano[u].add(w)
        for i in range(len(u)):
            jolly[u[:i] + ('*',) + u[i + 1:]].add(w)
            canc[u[:i] + u[i + 1:]].add(w)
    out = {}
    for w in tipi:
        u = U[w]
        s = set(piano[u]) | canc[u]
        for i in range(len(u)):
            s |= jolly[u[:i] + ('*',) + u[i + 1:]]
            s |= piano.get(u[:i] + u[i + 1:], set())
        out[w] = s
    return out


def analizza(righe, segni, rnd):
    tok = [w for r in righe for w in r]
    freq = Counter(tok)
    U = {w: tuple(segni(w)) for w in freq}
    sim = simili(set(freq), U)
    nuove = [w for w, n in freq.items() if n == 1 and len(U[w]) >= 3 and not any(freq[v] >= 20 for v in sim[w] if v != w)]
    comuni = defaultdict(list)
    for w, n in freq.items():
        if n >= 5 and len(U[w]) >= 3:
            comuni[len(U[w])].append(w)
    ctx, tr = Counter(), Counter()
    for w in tok:
        if freq[w] >= 2:
            for c, g in transizioni(U[w]):
                ctx[c] += 1
                tr[(c, g)] += 1
    V = len({g for w in freq for g in U[w]}) + 1

    def ll(w, togli=0):
        t = transizioni(U[w])
        ct, cc = Counter(t), Counter(c for c, _ in t)
        return sum(math.log((tr[(c, g)] - togli * ct[(c, g)] + ALFA) / (ctx[c] - togli * cc[c] + ALFA * V)) for c, g in t) / len(t)
    # coppie di confine
    fra, dentro = Counter(), Counter()
    for r in righe:
        for a, b in zip(r, r[1:]):
            fra[(U[a][-1], U[b][0])] += 1
    for w in tok:
        if freq[w] >= 2:
            u = U[w]
            for i in range(len(u) - 1):
                dentro[(u[i], u[i + 1])] += 1
    nf, nd = sum(fra.values()), sum(dentro.values())
    confine = {k for k, c in fra.items() if c >= 20 and (c / nf) >= 5 * ((dentro[k] + 0.5) / nd)}

    def ha_giuntura(w):
        u = U[w]
        return any((u[i], u[i + 1]) in confine for i in range(1, len(u) - 2))
    lens = [len(U[w]) for w in nuove]
    llc = {w: ll(w, togli=freq[w]) for L in comuni for w in comuni[L]}
    v_ll = statistics.mean(ll(w) for w in nuove)
    v_g = statistics.mean(ha_giuntura(w) for w in nuove)
    r_ll, r_g = [], []
    for _ in range(1000):
        camp = []
        for L in lens:
            pool = comuni.get(L) or comuni.get(L - 1) or comuni.get(L + 1) or list(llc)
            camp.append(rnd.choice(pool))
        r_ll.append(statistics.mean(llc[w] for w in camp))
        r_g.append(statistics.mean(ha_giuntura(w) for w in camp))
    return OrderedDict([('parole', len(tok)), ('forme_nuove', len(nuove)), ('coppie_di_confine', len(confine)),
                        ('ll_forme_nuove', v_ll), ('ll_comuni', statistics.mean(r_ll)), ('delta_ll', v_ll - statistics.mean(r_ll)),
                        ('giunture_forme_nuove', v_g), ('giunture_comuni', statistics.mean(r_g)), ('differenza_giunture', v_g - statistics.mean(r_g)),
                        ('z_giunture', (v_g - statistics.mean(r_g)) / (statistics.pstdev(r_g) or 1)),
                        ('esempi_confine', sorted(('%s|%s' % k for k in confine))[:15])])


def righe_lingua(nome):
    ws = [w for w in lingue.parole(nome, max_caratteri=400000) if w.isalpha()][:N_PAROLE]
    return [ws[i:i + 8] for i in range(0, len(ws), 8)]


def main():
    rnd = random.Random(363)
    voy = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                voy.append(ws)
    ris = OrderedDict([('Voynich', analizza(voy, D, rnd))])
    for nome in ('Latin', 'Italian'):
        ris[nome] = analizza(righe_lingua(nome), list, rnd)
    for k, v in ris.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items() if a != 'esempi_confine'}, flush=True)
    dv = ris['Voynich']['delta_ll']
    dl = min(ris['Latin']['delta_ll'], ris['Italian']['delta_ll'])
    esito_a = 'le forme nuove del Voynich sono più fuori regola degli hapax di una lingua' if dv < dl - 0.3 else ('come in una lingua' if abs(dv - dl) < 0.1 else 'intermedio')
    gv = ris['Voynich']['differenza_giunture']
    esito_b = 'le forme nuove contengono giunture di parola' if (ris['Voynich']['z_giunture'] > 3 and gv > max(ris['Latin']['differenza_giunture'], ris['Italian']['differenza_giunture'])) \
        else ('no' if ris['Voynich']['z_giunture'] < 2 else 'incerto')
    json.dump(OrderedDict([('testi', ris), ('esito_a', esito_a), ('esito_b', esito_b)]), open(os.path.join(RISULTATI, 'e363_giunture.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e363 — Forme nuove: fuori regola rispetto a una lingua vera? Giunture di parola?', '', 'Preregistrazione: `preregistrazioni/e363.md`.', '',
          '| testo | forme nuove | ll per segno forme nuove | comuni a pari lunghezza | Δ | con giuntura: forme nuove | comuni | differenza | z |', '|---|---|---|---|---|---|---|---|---|']
    for k, v in ris.items():
        md.append('| %s | %d | %.3f | %.3f | %+.3f | %.3f | %.3f | %+.3f | %.1f |' % (k, v['forme_nuove'], v['ll_forme_nuove'], v['ll_comuni'], v['delta_ll'],
                                                                              v['giunture_forme_nuove'], v['giunture_comuni'], v['differenza_giunture'], v['z_giunture']))
    md += ['', 'Esito (a): **%s**. Esito (b): **%s**.' % (esito_a, esito_b), '', 'Coppie di confine del Voynich (esempi): %s.' % ', '.join(ris['Voynich']['esempi_confine'])]
    open(os.path.join(RISULTATI, 'e363_giunture.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
