# -*- coding: utf-8 -*-
"""Esperimento 149: le etichette sono parole del testo con un prefisso? Attestazione nel testo delle etichette e delle
etichette senza il primo segno, contro parole del testo appaiate per sezione e lunghezza.

Preregistrazione: preregistrazioni/e149.md. Scrive risultati/e149_etichette_prefisso.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, ESTRAZIONI = 149, 1000
D = misure.divisore(misure.GLIFI_EVA)
G = {'k', 't', 'p', 'f'}


def classe_iniziale(w):
    g = D(w)[0]
    return 'o' if g == 'o' else 'y/d/s' if g in ('y', 'd', 's') else 'gallow' if g in G else 'altro'


def main():
    rnd = random.Random(SEME)
    zl = trascrizione.leggi('ZL')
    testo = [(r.sezione, w) for r in zl if r.tipo and r.tipo[0] == 'P' for w in r.parole if trascrizione.pulita(w)]
    freq = Counter(w for _, w in testo)
    etich = [(r.sezione, r.parole[0]) for r in zl if r.tipo and r.tipo[0] == 'L' and r.parole and trascrizione.pulita(r.parole[0])]

    def a(w, propria):
        return 1.0 if freq[w] - (1 if propria else 0) > 0 else 0.0

    def b(w, propria):
        if a(w, propria):
            return None
        u = D(w)
        if len(u) < 3:
            return None
        resto = ''.join(u[1:])
        return 1.0 if freq[resto] > 0 else 0.0

    per_chiave = defaultdict(list)
    for s, w in testo:
        per_chiave[len(D(w))].append(w)
    sezioni = ['tutte'] + sorted({s for s, _ in etich if s})
    ris = OrderedDict()
    for sez in sezioni:
        ee = [(s, w) for s, w in etich if sez == 'tutte' or s == sez]
        ee = [(s, w) for s, w in ee if per_chiave[len(D(w))]]
        if len(ee) < 30:
            continue
        ra = statistics.mean(a(w, False) for _, w in ee)
        bb = [b(w, False) for _, w in ee]
        bb = [x for x in bb if x is not None]
        rb = statistics.mean(bb) if bb else None
        na, nb = [], []
        for _ in range(ESTRAZIONI):
            cc = [rnd.choice(per_chiave[len(D(w))]) for s, w in ee]
            na.append(statistics.mean(a(c, True) for c in cc))
            xb = [b(c, True) for c in cc]
            xb = [x for x in xb if x is not None]
            nb.append(statistics.mean(xb) if xb else 0)
        ma, sa = statistics.mean(na), statistics.pstdev(na)
        mb, sb = statistics.mean(nb), statistics.pstdev(nb)
        ci_e = Counter(classe_iniziale(w) for _, w in ee)
        ci_t = Counter(classe_iniziale(w) for s, w in testo if sez == 'tutte' or s == sez)
        ne, nt = sum(ci_e.values()), sum(ci_t.values())
        ris[sez] = OrderedDict([('etichette', len(ee)),
                                ('a_attestate', ra), ('a_confronto', ma), ('a_z', (ra - ma) / sa if sa else None),
                                ('b_attestate_senza_primo_segno', rb), ('b_confronto', mb), ('b_z', (rb - mb) / sb if sb and rb is not None else None), ('b_n', len(bb)),
                                ('iniziali_etichette', {k: round(v / ne, 3) for k, v in ci_e.items()}),
                                ('iniziali_testo', {k: round(v / nt, 3) for k, v in ci_t.items()})])
        r = ris[sez]
        print('%-6s etichette %4d | (a) %.3f vs %.3f (z %.1f) | (b) %.3f vs %.3f (z %.1f, n %d) | iniziali etichette %s testo %s' % (
            sez, r['etichette'], ra, ma, r['a_z'] or 0, rb or 0, mb, r['b_z'] or 0, len(bb), r['iniziali_etichette'], r['iniziali_testo']), flush=True)
    zb = lambda s: (ris[s]['b_z'] or 0) if s in ris else 0
    sez_grandi = [s for s in ris if s != 'tutte']
    prefisso = zb('tutte') > 4 and sum(zb(s) > 4 for s in sez_grandi) >= 2
    a_sotto = (ris['tutte']['a_z'] or 0) < -4
    lessico = a_sotto and not zb('tutte') > 4
    ris['etichette_testo_piu_prefisso'], ris['lessico_a_se'] = prefisso, lessico
    print('etichette = testo + prefisso: %s | lessico a se\': %s' % (prefisso, lessico))
    with open(os.path.join(RISULTATI, 'e149_etichette_prefisso.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e149 — Le etichette sono parole del testo con un prefisso?', '', '(a) attestate nel testo; (b) fra le non attestate, attestate togliendo il primo segno. Confronto: parole del testo '
           'appaiate per lunghezza (%d estrazioni). Preregistrazione: `preregistrazioni/e149.md`.' % ESTRAZIONI, '',
           '| sezione | etichette | (a) etichette / confronto (z) | (b) etichette / confronto (z) | iniziali etichette | iniziali testo |', '|---|---|---|---|---|---|']
    for s, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.3f / %.3f (%.1f) | %.3f / %.3f (%.1f) | %s | %s |' % (s, r['etichette'], r['a_attestate'], r['a_confronto'], r['a_z'] or 0,
                                                                                r['b_attestate_senza_primo_segno'] or 0, r['b_confronto'], r['b_z'] or 0,
                                                                                ', '.join('%s %.2f' % kv for kv in sorted(r['iniziali_etichette'].items())),
                                                                                ', '.join('%s %.2f' % kv for kv in sorted(r['iniziali_testo'].items()))))
    out += ['', 'Etichette = testo + prefisso: **%s**. Lessico a sé: **%s**.' % ('sì' if prefisso else 'no', 'sì' if lessico else 'no')]
    with open(os.path.join(RISULTATI, 'e149_etichette_prefisso.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
