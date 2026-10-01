# -*- coding: utf-8 -*-
"""Esperimento 85: la parita' della riga nel paragrafo dice qualcosa sul primo segno, sull'ultimo segno,
sul numero di parole? (struttura a distici)

Preregistrazione: preregistrazioni/e85.md. Scrive risultati/e85_parita_righe.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e77_versi_sandhi as e77

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 85, 500
CARATTERISTICHE = ('primo', 'ultimo', 'parole')


def classe_parole(n):
    return '1-4' if n <= 4 else '5-7' if n <= 7 else '8-10' if n <= 10 else '11+'


def voci(paragrafi, dividi):
    """paragrafi: liste di righe (liste di parole). -> (paragrafo, parita', {caratteristiche})."""
    out = []
    for k, par in enumerate(paragrafi):
        for j, ps in enumerate(par):
            if j == 0 or not ps:
                continue
            c = {'parole': classe_parole(len(ps))}
            c['primo'] = dividi(ps[0])[0] if trascrizione.pulita(ps[0]) else None
            c['ultimo'] = dividi(ps[-1])[-1] if trascrizione.pulita(ps[-1]) else None
            out.append((k, j % 2, c))
    return out


def eccesso(vv, car, rnd):
    dati = [(k, p, c[car]) for k, p, c in vv if c[car] is not None]
    vera = misure.informazione_mutua([(x, p) for _, p, x in dati])
    per = defaultdict(list)
    for i, (k, _, _) in enumerate(dati):
        per[k].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        par = [p for _, p, _ in dati]
        for idx in per.values():
            v = [par[i] for i in idx]
            rnd.shuffle(v)
            for i, x in zip(idx, v):
                par[i] = x
        nulli.append(misure.informazione_mutua([(x, p) for (_, _, x), p in zip(dati, par)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(dati)), ('eccesso', vera - m), ('z', (vera - m) / s if s else None)])


def paragrafi_voynich(lingua=None):
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        if not r.parole:
            continue
        if r.inizio_par or not out:
            out.append([])
        out[-1].append(list(r.parole))
    return out


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = (paragrafi_voynich(), e71.D)
    t['Voynich A'] = (paragrafi_voynich('A'), e71.D)
    t['Voynich B'] = (paragrafi_voynich('B'), e71.D)
    f, sha = e77.TESTI['Manusmṛti']
    versi = e77.mezzi_versi(f, sha)
    t['controllo positivo: Manusmṛti, 5 śloka per paragrafo'] = ([versi[i:i + 10] for i in range(0, len(versi), 10)], e71.lettere)
    rc = [ps for _, ps in base['Plinio codificato, a capo'][0]]
    t['controllo negativo: Plinio codificato'] = ([rc[i:i + 20] for i in range(0, len(rc), 20)], e71.D)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    pts = []
    for ini, ps in ts:
        if ini or not pts:
            pts.append([])
        pts[-1].append(ps)
    t['Timm e Schinner, seme 19'] = (pts, e71.D)
    ris = OrderedDict()
    for nome, (pars, dividi) in t.items():
        vv = voci(pars, dividi)
        rnd = random.Random(SEME)
        r = OrderedDict((c, eccesso(vv, c, rnd)) for c in CARATTERISTICHE)
        ris[nome] = r
        print('%-52s %s' % (nome, ' | '.join('%s n %d %.4f (z %.1f)' % (c, r[c]['n'], r[c]['eccesso'], r[c]['z'] or 0)
                                             for c in CARATTERISTICHE)), flush=True)
    with open(os.path.join(RISULTATI, 'e85_parita_righe.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e85 — Distici? La parità della riga nel paragrafo', '',
           'Eccesso d\'informazione mutua (bit) fra la parità della riga nel paragrafo e: primo segno, ultimo segno, numero di '
           'parole; contro %d permutazioni nel paragrafo. Preregistrazione: `preregistrazioni/e85.md`.' % PERMUTAZIONI, '',
           '| testo | primo segno (z) | ultimo segno (z) | numero di parole (z) |', '|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %s |' % (nome, ' | '.join('%.4f (%.1f)' % (r[c]['eccesso'], r[c]['z'] or 0) for c in CARATTERISTICHE)))
    with open(os.path.join(RISULTATI, 'e85_parita_righe.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
