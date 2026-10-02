# -*- coding: utf-8 -*-
"""Esperimento 143: l'inizio e la fine della stessa riga sono legati? IM fra classe del primo segno e ultimo segno della
riga, contro il rimescolamento delle fini fra righe della stessa pagina e classe di lunghezza.

Preregistrazione: preregistrazioni/e143.md. Scrive risultati/e143_cornice_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 143, 1000
D = misure.divisore(misure.GLIFI_EVA)
B = {'ch', 'sh', 'ckh', 'cth', 'cph', 'cfh'}
G = {'k', 't', 'p', 'f'}


def classe_inizio(w):
    g = D(w)[0]
    if g in ('y', 'd', 's', 'o', 'q'):
        return g
    return 'G' if g in G else 'B' if g in B else 'altro'


def righe_voynich():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = list(r.parole)
        if r.inizio_par or len(ps) < 3 or not (trascrizione.pulita(ps[0]) and trascrizione.pulita(ps[-1])):
            continue
        out.append((r.pagina, ps))
    return out


def righe_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    return [(i // 29, ps) for i, (ini, ps) in enumerate(rr) if not ini and len(ps) >= 3]


def coppie(righe):
    lun = sorted(len(ps) for _, ps in righe)
    t1, t2 = lun[len(lun) // 3], lun[2 * len(lun) // 3]
    out = []
    for pag, ps in righe:
        n = len(ps)
        out.append(((pag, 0 if n <= t1 else 1 if n <= t2 else 2), classe_inizio(ps[0]), D(ps[-1])[-1]))
    return out


def valuta(cc, rnd):
    reale = misure.informazione_mutua([(a, b) for _, a, b in cc])
    per = defaultdict(list)
    for i, (st, _, _) in enumerate(cc):
        per[st].append(i)
    fini = [b for _, _, b in cc]
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        x = fini[:]
        for idx in per.values():
            v = [x[i] for i in idx]
            rnd.shuffle(v)
            for i, c in zip(idx, v):
                x[i] = c
        nulli.append(misure.informazione_mutua([(a, b) for (_, a, _), b in zip(cc, x)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    ci, cf = Counter(a for _, a, _ in cc), Counter(b for _, _, b in cc)
    cp = Counter((a, b) for _, a, b in cc)
    n = len(cc)
    celle = OrderedDict()
    for (a, b), o in sorted(cp.items(), key=lambda kv: -kv[1]):
        att = ci[a] * cf[b] / n
        if att >= 30:
            celle['%s ... %s' % (a, b)] = round(o / att, 3)
    return OrderedDict([('righe', n), ('im', reale), ('nullo', m), ('z', (reale - m) / s if s else None), ('celle', celle)])


def main():
    rnd = random.Random(SEME)
    cv = coppie(righe_voynich())
    r2 = random.Random(SEME + 1)
    cpos = [(st, a, ('m' if a == 's' and r2.random() < 0.3 else b)) for st, a, b in cv]
    ris = OrderedDict()
    for nome, cc in (('Voynich ZL', cv), ('controllo positivo: s ... m imposto (0,3)', cpos), ('Timm e Schinner, seme 19', coppie(righe_ts()))):
        ris[nome] = r = valuta(cc, rnd)
        print('%-42s righe %5d | IM %.4f (nullo %.4f, z %.1f) | celle piu lontane da 1: %s' % (
            nome, r['righe'], r['im'], r['nullo'], r['z'] or 0,
            ', '.join('%s %.2f' % kv for kv in sorted(r['celle'].items(), key=lambda kv: -abs(kv[1] - 1))[:8])), flush=True)
    z = lambda n: ris[n]['z'] or 0
    valido = z('controllo positivo: s ... m imposto (0,3)') > 10
    cornice = z('Voynich ZL') > 4 and z('Voynich ZL') > z('Timm e Schinner, seme 19')
    ris['valido'], ris['cornice'] = valido, cornice
    print('controllo valido:', valido, '| cornice di riga:', cornice)
    with open(os.path.join(RISULTATI, 'e143_cornice_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e143 — L\'inizio e la fine della stessa riga sono scelti insieme?', '', 'IM fra classe d\'inizio e ultimo segno della riga; nullo: %d rimescolamenti delle fini fra righe '
           'della stessa pagina e classe di lunghezza. Preregistrazione: `preregistrazioni/e143.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | IM | nullo | z |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.4f | %.4f | %.1f |' % (nome, r['righe'], r['im'], r['nullo'], r['z'] or 0))
    out += ['', '### Voynich: osservato / atteso (celle con almeno 30 attese)', '', '| inizio ... fine | rapporto |', '|---|---|']
    for k, v in sorted(ris['Voynich ZL']['celle'].items(), key=lambda kv: -abs(kv[1] - 1)):
        out.append('| %s | %.2f |' % (k, v))
    out += ['', 'Controllo valido: **%s**. Cornice di riga: **%s**.' % ('sì' if valido else 'no', 'sì' if cornice else 'no')]
    with open(os.path.join(RISULTATI, 'e143_cornice_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
