# -*- coding: utf-8 -*-
"""Esperimento 250: le righe con poca affinita' di copia con le righe vicine (sopra e sotto) sono fisicamente diverse
(scuro dell'inchiostro, altezza dei riquadri, come z dentro la pagina)?

Preregistrazione: preregistrazioni/e250.md. Scrive risultati/e250_righe_isolate.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from difflib import SequenceMatcher

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146
import e166_intinte as e166
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, REPLICHE, QUOTA, FINESTRA = 250, 1000, 0.10, 3
D = e237.D


def altezze(righe, ks, pag):
    percorso = os.path.join(e34.RIQUADRI, pag + '.js')
    if not os.path.exists(percorso):
        return {}
    d = json.load(open(percorso, encoding='utf-8'))
    voc = [v[0] for v in d[0]]
    vt = [voc[e[0]] for e in d[1]]
    hh = [e[4] for e in d[1]]
    zt = [(k, j, w) for k in ks for j, w in enumerate(righe[k][2])]
    sm = SequenceMatcher(a=[e34.fondi(w) for w in vt], b=[e34.fondi(w) for _, _, w in zt], autojunk=False)
    out = {}
    for i0, j0, n in sm.get_matching_blocks():
        for t in range(n):
            out[(zt[j0 + t][0], zt[j0 + t][1])] = hh[i0 + t]
    return out


def main():
    rnd = random.Random(SEME)
    righe, scuri = e166.pagine()          # righe: (pagina, paragrafo, parole); scuri: pagina -> [(k, [scuro])]
    sez = {r.pagina: r.sezione for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    tutte = Counter(w for _, _, ps in righe for w in ps if trascrizione.pulita(w))
    inventario = sorted({x for w in tutte for x in D(w)})
    per_pag = defaultdict(list)
    for k, (p, par, ps) in enumerate(righe):
        per_pag[p].append(k)
    prima_par = set()
    visti = set()
    for k, (p, par, ps) in enumerate(righe):
        if (p, par) not in visti:
            prima_par.add(k)
            visti.add((p, par))
    dati = []                              # (pagina, k, affinita', z scuro, z altezza)
    for p, ks in per_pag.items():
        if p not in scuri:
            continue
        sc = {k: v for k, v in scuri[p]}
        alt = altezze(righe, ks, p)
        tup = {k: [tuple(D(w)) for w in righe[k][2] if trascrizione.pulita(w)] for k in ks}
        fis = {}
        for k in ks:
            s = [x for x in sc.get(k, []) if x is not None]
            a = [alt[(k, j)] for j in range(len(righe[k][2])) if (k, j) in alt]
            fis[k] = (statistics.mean(s) if s else None, statistics.mean(a) if a else None)

        def zeta(i):
            vals = [fis[k][i] for k in ks if fis[k][i] is not None]
            if len(vals) < 5:
                return {}
            m, sd = statistics.mean(vals), statistics.pstdev(vals) or 1.0
            return {k: (fis[k][i] - m) / sd for k in ks if fis[k][i] is not None}

        zs, za = zeta(0), zeta(1)
        for t, k in enumerate(ks):
            if k in prima_par or len(tup[k]) < 4:
                continue
            sopra = {x for kk in ks[max(0, t - FINESTRA):t] for x in tup[kk]}
            sotto = [ks[tt] for tt in range(t + 1, min(len(ks), t + 1 + FINESTRA))]
            parti = []
            if sopra:
                parti.append(sum(1 for u in tup[k] if u in sopra or e237.vicini(u, inventario) & sopra) / len(tup[k]))
            if sotto:
                qui = set(tup[k])
                ws = [u for kk in sotto for u in tup[kk]]
                if ws:
                    parti.append(sum(1 for u in ws if u in qui or e237.vicini(u, inventario) & qui) / len(ws))
            if parti and (k in zs or k in za):
                dati.append((p, k, statistics.mean(parti), zs.get(k), za.get(k)))
    isolate = set()
    per_sez = defaultdict(list)
    for x in dati:
        per_sez[sez.get(x[0])].append(x)
    for s, xs in per_sez.items():
        xs = sorted(xs, key=lambda x: x[2])
        isolate |= {(x[0], x[1]) for x in xs[:max(1, int(QUOTA * len(xs)))]}
    ris = OrderedDict([('righe', len(dati)), ('isolate', len(isolate))])
    per_pag_dati = defaultdict(list)
    for x in dati:
        per_pag_dati[x[0]].append(x)
    for nome, i in (('scuro', 3), ('altezza', 4)):
        vere = [abs(x[i]) for x in dati if (x[0], x[1]) in isolate and x[i] is not None]
        quante = Counter(x[0] for x in dati if (x[0], x[1]) in isolate and x[i] is not None)
        nulli = []
        for _ in range(REPLICHE):
            vs = []
            for p, n in quante.items():
                cand = [x for x in per_pag_dati[p] if x[i] is not None]
                vs += [abs(x[i]) for x in rnd.sample(cand, min(n, len(cand)))]
            nulli.append(statistics.mean(vs))
        m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        segno = statistics.mean(x[i] for x in dati if (x[0], x[1]) in isolate and x[i] is not None)
        ris[nome] = OrderedDict([('righe_isolate_misurate', len(vere)), ('media_abs_z', statistics.mean(vere)), ('nulla', m),
                                 ('z', (statistics.mean(vere) - m) / sd if sd else None), ('media_z_con_segno', segno)])
        print(nome, dict(ris[nome]), flush=True)
    zz = [ris[n]['z'] or 0 for n in ('scuro', 'altezza')]
    esito = 'aggiunte riconoscibili' if max(zz) > 3 else ('nessuna differenza fisica' if max(zz) <= 2 else 'incerto')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e250_righe_isolate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e250 — Righe che non copiano e non sono copiate: aggiunte successive?', '',
          'Righe di paragrafo (escluse le prime) con affinità di copia (ripetizioni e varianti con le %d righe sopra e sotto); isolate = il %d%% '
          'più basso per sezione. Misure fisiche come z dentro la pagina; nullo: %d scelte casuali nelle stesse pagine. Preregistrazione: '
          '`preregistrazioni/e250.md`.' % (FINESTRA, int(100 * QUOTA), REPLICHE), '',
          '| misura | righe isolate | media \\|z\\| | nulla | z | media z (segno) |', '|---|---|---|---|---|---|']
    for n in ('scuro', 'altezza'):
        r = ris[n]
        md.append('| %s | %d | %.3f | %.3f | %.1f | %+.2f |' % (n, r['righe_isolate_misurate'], r['media_abs_z'], r['nulla'], r['z'] or 0, r['media_z_con_segno']))
    md += ['', 'Righe: %d; isolate: %d. Esito: **%s**.' % (len(dati), len(isolate), esito)]
    open(os.path.join(RISULTATI, 'e250_righe_isolate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
