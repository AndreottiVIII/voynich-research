# -*- coding: utf-8 -*-
"""Esperimento 105: che cosa predice la classe d'inizio di una riga, oltre all'inizio della riga sopra?

Preregistrazione: preregistrazioni/e105.md. Scrive risultati/e105_cosa_decide_inizio.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 105, 300
D = misure.divisore(misure.GLIFI_EVA)
FAMIGLIE = {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'k': 'G', 't': 'G', 'p': 'G', 'f': 'G', 'd': 'D', 'r': 'D', 's': 'D'}
PRINCIPALI = ('q', 'o', 'y', 'B', 'G', 'D')
CANDIDATI = ('inizio di L', 'fine di L', 'classi presenti in L', 'inizio di L-1', 'posizione nel paragrafo',
             'parole di L+1', 'parole di L', 'seconda parola di L+1')


def classe(w):
    if not w or not trascrizione.pulita(w):
        return None
    g = D(w)[0]
    return FAMIGLIE.get(g, g)


def classe_n(n):
    return '1-5' if n <= 5 else '6-8' if n <= 8 else '9-11' if n <= 11 else '12+'


def righe_per_pagina():
    per = OrderedDict()
    par = 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        par += bool(r.inizio_par)
        per.setdefault(r.pagina, []).append((par, bool(r.inizio_par), list(r.parole)))
    return per


def caratteristiche(rr):
    """Per una pagina (lista di righe nell'ordine dato): voci (pagina-locale) con classe di L+1 e candidati."""
    out = []
    j_par = 0
    for k, (par, ini, ps) in enumerate(rr):
        j_par = 0 if ini else j_par + 1
        if k == 0 or ini:
            continue
        p0, _, L = rr[k - 1]
        if p0 != par:
            continue
        y = classe(ps[0])
        if y is None:
            continue
        cl = Counter(classe(w) for w in L)
        presenti = tuple(c for c in PRINCIPALI if cl[c] > 1)
        Lm1 = classe(rr[k - 2][2][0]) if k >= 2 and rr[k - 2][0] == par and not rr[k - 1][1] else None
        ult = L[-1] if L and trascrizione.pulita(L[-1]) else None
        out.append({'y': y,
                    'inizio di L': classe(L[0]),
                    'fine di L': D(ult)[-1] if ult else None,
                    'classi presenti in L': presenti,
                    'inizio di L-1': Lm1,
                    'posizione nel paragrafo': min(j_par, 5),
                    'parole di L+1': classe_n(len(ps)),
                    'parole di L': classe_n(len(L)),
                    'seconda parola di L+1': classe(ps[1]) if len(ps) > 1 else None})
    return out


def im(voci, c):
    return misure.informazione_mutua([(v['y'], v[c]) for v in voci if v[c] is not None])


def im_cond(voci, c):
    per = defaultdict(list)
    for v in voci:
        if v[c] is not None and v['inizio di L'] is not None:
            per[v['inizio di L']].append((v['y'], v[c]))
    n = sum(len(x) for x in per.values())
    return sum(len(x) / n * misure.informazione_mutua(x) for x in per.values() if len(x) > 1)


def main():
    pagine = righe_per_pagina()
    voci = [v for rr in pagine.values() for v in caratteristiche(rr)]
    rnd = random.Random(SEME)
    reale = {c: im(voci, c) for c in CANDIDATI}
    reale_c = {c: im_cond(voci, c) for c in CANDIDATI if c != 'inizio di L'}
    nulli = defaultdict(list)
    for _ in range(PERMUTAZIONI):
        vv = []
        for rr in pagine.values():
            # rimescola le righe non d'inizio paragrafo della pagina tenendo fissi gli inizi di paragrafo
            idx = [i for i, (_, ini, _) in enumerate(rr) if not ini]
            contenuti = [rr[i][2] for i in idx]
            rnd.shuffle(contenuti)
            nuova = list(rr)
            for i, ps in zip(idx, contenuti):
                nuova[i] = (rr[i][0], False, ps)
            vv.extend(caratteristiche(nuova))
        for c in CANDIDATI:
            nulli[c].append(im(vv, c))
    # nullo condizionato: permutazione del candidato dentro (pagina, classe di L)
    pag_di = []
    for p, rr in pagine.items():
        pag_di.extend([p] * len(caratteristiche(rr)))
    nulli_c = defaultdict(list)
    for c in reale_c:
        gruppi = defaultdict(list)
        for i, v in enumerate(voci):
            gruppi[(pag_di[i], v['inizio di L'])].append(i)
        for _ in range(PERMUTAZIONI):
            valori = [v[c] for v in voci]
            for idx in gruppi.values():
                x = [valori[i] for i in idx]
                rnd.shuffle(x)
                for i, val in zip(idx, x):
                    valori[i] = val
            nulli_c[c].append(im_cond([dict(v, **{c: val}) for v, val in zip(voci, valori)], c))
    ris = OrderedDict([('righe', len(voci))])
    for c in CANDIDATI:
        m, s = statistics.mean(nulli[c]), statistics.pstdev(nulli[c])
        r = OrderedDict([('eccesso', reale[c] - m), ('z', (reale[c] - m) / s if s else None)])
        if c in reale_c:
            mc, sc = statistics.mean(nulli_c[c]), statistics.pstdev(nulli_c[c])
            r['eccesso_condizionato'] = reale_c[c] - mc
            r['z_condizionato'] = (reale_c[c] - mc) / sc if sc else None
        ris[c] = r
        print('%-26s eccesso %.4f (z %.1f) | condizionato all\'inizio di L: %s' % (
            c, r['eccesso'], r['z'] or 0, '%.4f (z %.1f)' % (r['eccesso_condizionato'], r['z_condizionato'] or 0) if 'eccesso_condizionato' in r else '-'), flush=True)
    rilevanti = [c for c in CANDIDATI if (ris[c].get('z_condizionato') or 0) > 4]
    ris['rilevanti'] = rilevanti
    print('rilevanti oltre la riga sopra:', rilevanti)
    for c in rilevanti:
        conti = Counter((v['y'], v[c]) for v in voci if v[c] is not None)
        ny, nc = Counter(v['y'] for v in voci if v[c] is not None), Counter(v[c] for v in voci if v[c] is not None)
        n = sum(conti.values())
        tab = sorted(((conti[(a, b)] / (ny[a] * nc[b] / n), a, str(b), conti[(a, b)]) for a, b in conti if conti[(a, b)] >= 20), reverse=True)
        ris['tabella ' + c] = [(round(x, 2), a, b, k) for x, a, b, k in tab[:8] + tab[-6:]]
        print('  %s: piu\' frequenti del caso %s | meno %s' % (c, tab[:6], tab[-4:]))
    with open(os.path.join(RISULTATI, 'e105_cosa_decide_inizio.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e105 — Che cosa decide l\'inizio di riga?', '',
           'Eccesso d\'informazione mutua fra la classe d\'inizio della riga e ciascun candidato; condizionato = oltre la classe '
           'd\'inizio della riga sopra. %d righe. Preregistrazione: `preregistrazioni/e105.md`.' % len(voci), '',
           '| candidato | eccesso (z) | condizionato all\'inizio di L (z) |', '|---|---|---|']
    for c in CANDIDATI:
        r = ris[c]
        out.append('| %s | %.4f (%.1f) | %s |' % (c, r['eccesso'], r['z'] or 0, '%.4f (%.1f)' % (r['eccesso_condizionato'], r['z_condizionato'] or 0) if 'eccesso_condizionato' in r else '–'))
    out += ['', 'Rilevanti oltre la riga sopra: %s.' % (', '.join(rilevanti) or 'nessuno')]
    for c in rilevanti:
        out.append('- %s (osservato/atteso, classe di L+1, valore, n): %s' % (c, ris['tabella ' + c]))
    with open(os.path.join(RISULTATI, 'e105_cosa_decide_inizio.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
