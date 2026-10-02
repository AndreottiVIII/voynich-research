# -*- coding: utf-8 -*-
"""Esperimento 123b: da dove viene la dipendenza fra le scelte ch/sh dell'e123? Strato riga, scomposizione della
distanza 1, fase e lunghezza del blocco.

Preregistrazione: preregistrazioni/e123b.md. Scrive risultati/e123b_origine_dipendenza.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e71_bordo_riga as e71
import e123_canale_varianti as e123

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 1232, 300
LL = (3, 4, 5, 6, 8)
TIPI = ('stessa parola', 'parole adiacenti', 'piu lontane nella riga', 'fra due righe')


def occorrenze(righe):
    """-> lista di dict: strato (come e123), riga, parola, scelta."""
    out = []
    for k, (pag, prima, ps) in enumerate(righe):
        n = len(ps)
        for i, w in enumerate(ps):
            if not trascrizione.pulita(w):
                continue
            u = e123.D(w)
            pos = 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'
            for j, g in enumerate(u):
                if g in ('ch', 'sh'):
                    dopo = u[j + 1] if j + 1 < len(u) else '$'
                    out.append({'strato': (pag, prima, pos, j == 0, dopo), 'riga': k, 'parola': i, 'scelta': 1 if g == 'sh' else 0})
    return out


def entropia(blocchi):
    c = Counter(blocchi)
    n = sum(c.values())
    return -sum(k / n * math.log2(k / n) for k in c.values())


def blocchi(s, L, fase):
    return [tuple(s[i:i + L]) for i in range(fase, len(s) - L + 1, L)]


def tipi_coppie(occ):
    t = []
    for a, b in zip(occ, occ[1:]):
        if a['riga'] != b['riga']:
            t.append(3)
        elif a['parola'] == b['parola']:
            t.append(0)
        elif b['parola'] - a['parola'] == 1:
            t.append(1)
        else:
            t.append(2)
    return t


def statistiche(s, tipi):
    out = {}
    for L in LL:
        for f in range(L):
            out[('h', L, f)] = entropia(blocchi(s, L, f))
    uguali, tot = [0] * 4, [0] * 4
    for (a, b), t in zip(zip(s, s[1:]), tipi):
        tot[t] += 1
        uguali[t] += a == b
    for t in range(4):
        out[('u', t)] = uguali[t] / tot[t] if tot[t] else float('nan')
    return out


def permuta(s, gruppi, rnd):
    x = s[:]
    for idx in gruppi:
        v = [x[i] for i in idx]
        rnd.shuffle(v)
        for i, c in zip(idx, v):
            x[i] = c
    return x


def gruppi_di(occ, modo):
    """modo: 'base' (strati dell'e123), 'riga' (riga + iniziale di parola), 'fine' (riga + tutto il contesto)."""
    per = defaultdict(list)
    for i, o in enumerate(occ):
        k = {'base': o['strato'], 'riga': (o['riga'], o['strato'][3]), 'fine': (o['strato'], o['riga'])}[modo]
        per[k].append(i)
    return list(per.values())


def confronto(s, tipi, gruppi, rnd):
    reale = statistiche(s, tipi)
    nulli = defaultdict(list)
    for _ in range(PERMUTAZIONI):
        for k, v in statistiche(permuta(s, gruppi, rnd), tipi).items():
            nulli[k].append(v)
    out = OrderedDict()
    # blocchi: deficit per fase, z alla fase migliore (stessa regola per reale e nullo)
    for L in LL:
        deficit = [statistics.mean(nulli[('h', L, f)]) - reale[('h', L, f)] for f in range(L)]
        migliore = max(range(L), key=lambda f: deficit[f])
        nullo_migliore = [max(statistics.mean(nulli[('h', L, f)]) - nulli[('h', L, f)][p] for f in range(L)) for p in range(PERMUTAZIONI)]
        m, sd = statistics.mean(nullo_migliore), statistics.pstdev(nullo_migliore)
        z0 = deficit[0] / statistics.pstdev(nulli[('h', L, 0)]) if statistics.pstdev(nulli[('h', L, 0)]) else None
        out['L%d' % L] = OrderedDict([('deficit_per_fase', deficit), ('fase_migliore', migliore), ('z_fase0', z0),
                                      ('z_fase_migliore', (deficit[migliore] - m) / sd if sd else None)])
    d5 = out['L5']['deficit_per_fase']
    out['indice_di_fase'] = (max(d5) - min(d5)) / statistics.mean(d5) if statistics.mean(d5) > 0 else None
    for t in range(4):
        m, sd = statistics.mean(nulli[('u', t)]), statistics.pstdev(nulli[('u', t)])
        out[TIPI[t]] = OrderedDict([('coppie', tipi.count(t)), ('uguale', reale[('u', t)]), ('eccesso', reale[('u', t)] - m),
                                    ('z', (reale[('u', t)] - m) / sd if sd else None)])
    return out


def segno_di_blocco(r):
    z = {L: r['L%d' % L]['z_fase_migliore'] or 0 for L in LL}
    massimo_a_5 = z[5] > z[4] and z[5] > z[6]
    massimo_a_10 = False  # blocchi di 10 non misurati: troppo pochi blocchi per l'entropia
    return (r['indice_di_fase'] or 0) > 0.5 or massimo_a_5 or massimo_a_10


def main():
    rv = e123.righe_voynich()
    occ = occorrenze(rv)
    rnd = random.Random(SEME)
    testi = OrderedDict()
    s = [o['scelta'] for o in occ]
    testi['Voynich'] = (occ, s)
    lat = ''.join(c for c in ''.join(lingue.parole('Latin')[:20000]).replace('j', 'i').replace('v', 'u').replace('w', 'uu') if c in e123.BACONE)
    bit = [int(b) for c in lat for b in format(e123.BACONE.index(c), '05b')]
    testi['controllo positivo: latino nel canale'] = (occ, [bit[i] if i < len(bit) else c for i, c in enumerate(s)])
    testi['controllo di (P): quota per riga, ordine casuale'] = (occ, permuta(s, gruppi_di(occ, 'fine'), random.Random(SEME + 1)))
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    occ_ts = occorrenze([(i // 29, ini, ps) for i, (ini, ps) in enumerate(ts)])
    testi['Timm e Schinner, seme 19'] = (occ_ts, [o['scelta'] for o in occ_ts])
    ris = OrderedDict()
    for nome, (oc, sc) in testi.items():
        tipi = tipi_coppie(oc)
        r = OrderedDict()
        for nn, modo in (('nullo e123', 'base'), ('nullo con riga', 'riga')):
            r[nn] = confronto(sc, tipi, gruppi_di(oc, modo), rnd)
            x = r[nn]
            print('%-48s %-15s | z blocchi %s | fase %s | %s' % (
                nome, nn, ' '.join('%d:%.1f' % (L, x['L%d' % L]['z_fase_migliore'] or 0) for L in LL),
                '%.2f' % x['indice_di_fase'] if x['indice_di_fase'] is not None else '-',
                ' '.join('%s %+.3f (z %.1f)' % (t.split()[0] + ('-' + t.split()[1] if len(t.split()) > 1 else ''), x[t]['eccesso'], x[t]['z'] or 0) for t in TIPI)), flush=True)
        r['sopravvive_alla_riga'] = (r['nullo con riga']['L5']['z_fase_migliore'] or 0) > 4
        r['segno_di_blocco'] = segno_di_blocco(r['nullo con riga'])
        r['M_in_piedi'] = r['sopravvive_alla_riga'] and r['segno_di_blocco']
        print('   sopravvive alla riga %s | segno di blocco %s | (M) in piedi %s' % (r['sopravvive_alla_riga'], r['segno_di_blocco'], r['M_in_piedi']), flush=True)
        ris[nome] = r
    valido = ris['controllo positivo: latino nel canale']['M_in_piedi'] and not ris['controllo di (P): quota per riga, ordine casuale']['M_in_piedi']
    ris['valido'] = valido
    print('controllo valido:', valido, '| (M) resta in piedi nel Voynich:', ris['Voynich']['M_in_piedi'])
    with open(os.path.join(RISULTATI, 'e123b_origine_dipendenza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e123b — Da dove viene la dipendenza fra le scelte ch/sh?', '', 'Preregistrazione: `preregistrazioni/e123b.md`. %d permutazioni per nullo. '
           'z dei blocchi alla fase migliore (stessa regola nel nullo); eccesso = P(stessa scelta) osservata meno nullo.' % PERMUTAZIONI, '',
           '| testo | nullo | ' + ' | '.join('z blocchi %d' % L for L in LL) + ' | indice di fase | ' + ' | '.join(TIPI) + ' |',
           '|---|---|' + '---|' * len(LL) + '---|' + '---|' * len(TIPI)]
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        for nn in ('nullo e123', 'nullo con riga'):
            x = r[nn]
            out.append('| %s | %s | %s | %s | %s |' % (nome, nn, ' | '.join('%.1f' % (x['L%d' % L]['z_fase_migliore'] or 0) for L in LL),
                                                     '%.2f' % x['indice_di_fase'] if x['indice_di_fase'] is not None else '–',
                                                     ' | '.join('%+.3f (%.1f; n %d)' % (x[t]['eccesso'], x[t]['z'] or 0, x[t]['coppie']) for t in TIPI)))
    out += ['']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('- %s: sopravvive alla riga **%s**, segno di blocco **%s**, (M) in piedi **%s**.' % (
                nome, 'sì' if r['sopravvive_alla_riga'] else 'no', 'sì' if r['segno_di_blocco'] else 'no', 'sì' if r['M_in_piedi'] else 'no'))
    out += ['', 'Controllo valido: **%s**.' % ('sì' if valido else 'no')]
    with open(os.path.join(RISULTATI, 'e123b_origine_dipendenza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
