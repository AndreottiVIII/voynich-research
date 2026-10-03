# -*- coding: utf-8 -*-
"""Esperimento 245: le etichette (loci L) ripetono o variano parole dei paragrafi della stessa pagina piu' che di altre
pagine della stessa sezione, e piu' di quanto una riga di testo e' legata alla sua pagina?

Preregistrazione: preregistrazioni/e245.md. Scrive risultati/e245_etichette_testo.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE = 245, 200
D = e237.D
MISURE = ('esatto', 'variante', 'raro esatto')


def dati():
    lab, par, sez = defaultdict(list), defaultdict(list), {}
    for r in trascrizione.leggi('ZL'):
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        if not ws or not r.tipo:
            continue
        sez.setdefault(r.pagina, r.sezione)
        if r.tipo.startswith('L'):
            lab[r.pagina] += [w for w in ws if len(D(w)) >= 2]
        elif r.tipo.startswith('P'):
            par[r.pagina].append(ws)
    return lab, par, sez


def legami(w, testo, testo_u, vic, raro):
    """testo: set di parole; testo_u: set di tuple di unita'."""
    e = w in testo
    v = e or bool(vic & testo_u)
    return e, v, (e if raro else None)


def main():
    rnd = random.Random(SEME)
    lab, par, sez = dati()
    freq = Counter(w for rr in par.values() for r in rr for w in r)
    inventario = sorted({x for w in freq for x in D(w)} | {x for ws in lab.values() for w in ws for x in D(w)})
    pagine = [p for p in par if par[p]]
    per_sez = defaultdict(list)
    for p in pagine:
        per_sez[sez[p]].append(p)
    testo = {p: {w for r in par[p] for w in r} for p in pagine}
    testo_u = {p: {tuple(D(w)) for w in testo[p]} for p in pagine}

    # --- etichette ---
    etichette = [(p, w) for p in pagine for w in lab.get(p, []) if len(per_sez[sez[p]]) > 1]
    vic = {w: e237.vicini(tuple(D(w)), inventario) for _, w in etichette}
    raro = {w: 1 <= freq[w] <= 10 for _, w in etichette}
    vere = [legami(w, testo[p], testo_u[p], vic[w], raro[w]) for p, w in etichette]

    def quote(ls):
        out = OrderedDict()
        for i, m in enumerate(MISURE):
            xs = [x[i] for x in ls if x[i] is not None]
            out[m] = sum(xs) / len(xs) if xs else None
        return out

    q_vere = quote(vere)
    nulli = defaultdict(list)
    for _ in range(REPLICHE):
        ls = []
        for p, w in etichette:
            q = rnd.choice([x for x in per_sez[sez[p]] if x != p])
            ls.append(legami(w, testo[q], testo_u[q], vic[w], raro[w]))
        for m, x in quote(ls).items():
            nulli[m].append(x)
    etich = OrderedDict()
    for m in MISURE:
        mu, sd = statistics.mean(nulli[m]), statistics.pstdev(nulli[m])
        etich[m] = OrderedDict([('vera', q_vere[m]), ('nulla', mu), ('R', q_vere[m] / mu if mu else None), ('z', (q_vere[m] - mu) / sd if sd else None)])

    # --- righe del testo: una riga a caso per pagina contro il resto della pagina ---
    rapporti = defaultdict(list)
    for _ in range(REPLICHE):
        proprie, altre = [], []
        for p in pagine:
            if len(par[p]) < 3 or len(per_sez[sez[p]]) < 2:
                continue
            k = rnd.randrange(len(par[p]))
            resto = {w for j, r in enumerate(par[p]) if j != k for w in r}
            resto_u = {tuple(D(w)) for w in resto}
            q = rnd.choice([x for x in per_sez[sez[p]] if x != p])
            for w in par[p][k]:
                if len(D(w)) < 2:
                    continue
                vv = e237.vicini(tuple(D(w)), inventario)
                r_ = 2 <= freq[w] <= 11
                proprie.append(legami(w, resto, resto_u, vv, r_))
                altre.append(legami(w, testo[q], testo_u[q], vv, r_))
        qp, qa = quote(proprie), quote(altre)
        for m in MISURE:
            rapporti[m].append(qp[m] / qa[m] if qa[m] else None)
    testo_R = OrderedDict((m, statistics.mean(x for x in rapporti[m] if x is not None)) for m in MISURE)

    r_lab, r_txt, z = etich['raro esatto']['R'], testo_R['raro esatto'], etich['raro esatto']['z'] or 0
    esito = ('le etichette richiamano il testo' if z > 3 and r_lab > r_txt else 'come il testo' if z > 3
             else 'nessun legame' if z <= 2 else 'incerto')
    ris = OrderedDict([('etichette', len(etichette)), ('etichette_rare', sum(1 for _, w in etichette if raro[w])), ('pagine', len(pagine)),
                       ('etichette_misure', etich), ('righe_di_testo_R', testo_R), ('esito', esito)])
    print(json.dumps(ris, ensure_ascii=False, default=float)[:1500], flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e245_etichette_testo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e245 — Le etichette richiamano il testo della loro pagina?', '',
          'Etichette (loci L, ≥ 2 unità): %d, di cui rare (1–10 volte nei paragrafi) %d. Nullo: testo di un\'altra pagina della stessa sezione, '
          '%d repliche. R_testo: una riga a caso contro il resto della sua pagina, rispetto a un\'altra pagina. Preregistrazione: '
          '`preregistrazioni/e245.md`.' % (ris['etichette'], ris['etichette_rare'], REPLICHE), '',
          '| legame | etichette: vera | nulla | R | z | righe di testo: R |', '|---|---|---|---|---|---|']
    for m in MISURE:
        e = etich[m]
        md.append('| %s | %.3f | %.3f | %.2f | %.1f | %.2f |' % (m, e['vera'], e['nulla'], e['R'] or 0, e['z'] or 0, testo_R[m]))
    md += ['', 'Esito (legame raro esatto): **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e245_etichette_testo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
