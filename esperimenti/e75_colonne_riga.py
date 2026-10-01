# -*- coding: utf-8 -*-
"""Esperimento 75: struttura interna della riga per posizione relativa (parole interne).

Eccesso d'informazione mutua fra caratteristica della parola (primo segno, ultimo segno, lunghezza,
tipo) e classe di posizione relativa, contro 200 rimescolamenti dentro la riga.
Preregistrazione: preregistrazioni/e75.md. Scrive risultati/e75_colonne_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERMUTAZIONI, SEME, MIN_PAROLE, CLASSI, TIPI = 200, 75, 6, 4, 100
CARATTERISTICHE = ('primo', 'ultimo', 'lunghezza', 'tipo')


def interne(righe):
    """Liste di parole interne delle righe utili (le impure restano al loro posto come None)."""
    out = []
    for inizio, ps in righe:
        if len(ps) >= MIN_PAROLE and not inizio:
            out.append([w if trascrizione.pulita(w) else None for w in ps[1:-1]])
    return out


def caratteristica(nome, w, dividi, frequenti):
    u = dividi(w)
    if nome == 'primo':
        return u[0]
    if nome == 'ultimo':
        return u[-1]
    if nome == 'lunghezza':
        return min(len(u), 7)
    return w if w in frequenti else '·altro'


def coppie(righe_int, nome, dividi, frequenti):
    out = []
    for r in righe_int:
        n = len(r)
        for i, w in enumerate(r):
            if w is not None:
                out.append((caratteristica(nome, w, dividi, frequenti), min(CLASSI - 1, i * CLASSI // n)))
    return out


def una(args):
    nome_testo, righe, quale = args
    dividi = e71.lettere if quale == 'lettere' else e71.D
    ri = interne(righe)
    frequenti = {w for w, _ in Counter(w for r in ri for w in r if w).most_common(TIPI)}
    rnd = random.Random(SEME)
    reali = {c: misure.informazione_mutua(coppie(ri, c, dividi, frequenti)) for c in CARATTERISTICHE}
    nulli = {c: [] for c in CARATTERISTICHE}
    for _ in range(PERMUTAZIONI):
        mescolate = []
        for r in ri:
            r = r[:]
            rnd.shuffle(r)
            mescolate.append(r)
        for c in CARATTERISTICHE:
            nulli[c].append(misure.informazione_mutua(coppie(mescolate, c, dividi, frequenti)))
    ris = OrderedDict([('righe', len(ri))])
    for c in CARATTERISTICHE:
        m, s = statistics.mean(nulli[c]), statistics.pstdev(nulli[c])
        ris[c] = OrderedDict([('im', reali[c]), ('nullo', m), ('eccesso', reali[c] - m), ('z', (reali[c] - m) / s if s else None)])
    # descrittivo: valori piu' sbilanciati fra prima e ultima classe
    sbil = OrderedDict()
    for c in ('primo', 'ultimo', 'lunghezza'):
        cc = coppie(ri, c, dividi, frequenti)
        prima = Counter(v for v, b in cc if b == 0)
        ultima = Counter(v for v, b in cc if b == CLASSI - 1)
        n0, n1 = sum(prima.values()), sum(ultima.values())
        r = {v: (ultima[v] / n1) / (prima[v] / n0) for v in set(prima) | set(ultima) if prima[v] >= 30 and ultima[v] >= 30}
        ordine = sorted(r.items(), key=lambda kv: kv[1])
        sbil[c] = {'piu_all_inizio': [(str(v), round(x, 2)) for v, x in ordine[:3]],
                   'piu_alla_fine': [(str(v), round(x, 2)) for v, x in ordine[::-1][:3]]}
    ris['sbilanciati'] = sbil
    return nome_testo, ris


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    for nome in ('Voynich', 'Voynich A', 'Voynich B', 'Plinio, a capo', 'Plinio codificato, a capo', 'Naibbe, a capo'):
        t[nome] = base[nome]
    rc = base['Plinio codificato, a capo'][0]
    rnd = random.Random(SEME)
    ordinata = []
    for inizio, ps in rc:
        if len(ps) >= 3 and rnd.random() < 0.5:
            ps = [ps[0]] + sorted(ps[1:-1], key=lambda w: (len(e71.D(w)), w)) + [ps[-1]]
        ordinata.append((inizio, ps))
    t['controllo: interne ordinate per lunghezza (metà righe)'] = (ordinata, 'eva')
    for s in (19, 1, 2):
        t['Timm e Schinner, seme %d' % s] = base['Timm e Schinner, seme %d' % s]
    t['+ giunture (e23), seme 19'] = (e71.righe_file(os.path.join(e71.CACHE, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt')), 'eva')
    t['modello e51, seme 19'] = base['modello e51, seme 19']
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in t.items()]):
            ris[nome] = r
            print('%-52s righe %4d | %s' % (nome, r['righe'], ' | '.join(
                '%s %.4f (z %.1f)' % (c, r[c]['eccesso'], r[c]['z'] or 0) for c in CARATTERISTICHE)), flush=True)
            print('    %s' % r['sbilanciati'], flush=True)
    with open(os.path.join(RISULTATI, 'e75_colonne_riga.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e75 — La riga ha colonne?', '',
           'Eccesso d\'informazione mutua (bit) fra caratteristica delle parole interne e classe di posizione relativa (%d '
           'classi), contro %d rimescolamenti dentro la riga; z fra parentesi. Righe di almeno %d parole. '
           'Preregistrazione: `preregistrazioni/e75.md`.' % (CLASSI, PERMUTAZIONI, MIN_PAROLE), '',
           '| testo | righe | primo segno | ultimo segno | lunghezza | tipo |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %d | %s |' % (nome, r['righe'], ' | '.join('%.4f (z %.1f)' % (r[c]['eccesso'], r[c]['z'] or 0)
                                                                        for c in CARATTERISTICHE)))
    out += ['', 'Valori più sbilanciati (frequenza nell\'ultima classe / nella prima):', '']
    for nome, r in ris.items():
        out.append('- **%s**: %s' % (nome, '; '.join('%s: inizio %s, fine %s' % (c, x['piu_all_inizio'], x['piu_alla_fine'])
                                                     for c, x in r['sbilanciati'].items())))
    with open(os.path.join(RISULTATI, 'e75_colonne_riga.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
