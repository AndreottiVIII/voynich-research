# -*- coding: utf-8 -*-
"""Esperimento 95: allografi posizionali? Somiglianza dei corpi delle parole per coppie di primi segni e
dipendenza della scelta dalla posizione nella riga e nel paragrafo.

Preregistrazione: preregistrazioni/e95.md. Scrive risultati/e95_allografi.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from itertools import combinations
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, DIVISIONI, PERMUTAZIONI, MINIMO, SOGLIA = 95, 100, 500, 150, 1.5
D = e71.D


def occorrenze():
    """(primo segno, corpo, classe di posizione nella riga, prima riga del paragrafo?) per ogni parola pulita."""
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = r.parole
        n = len(ps)
        for i, w in enumerate(ps):
            if not trascrizione.pulita(w):
                continue
            u = D(w)
            if len(u) < 2:
                continue
            c = 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'
            out.append((u[0], ''.join(u[1:]), c, bool(r.inizio_par)))
    return out


def jsd(a, b):
    return e71.jsd(a, b)


def indice(args):
    x, y, corpi_x, corpi_y = args
    vera = jsd(Counter(corpi_x), Counter(corpi_y))
    tutti = corpi_x + corpi_y
    rnd = random.Random(SEME)
    nulli = []
    for _ in range(DIVISIONI):
        rnd.shuffle(tutti)
        nulli.append(jsd(Counter(tutti[:len(corpi_x)]), Counter(tutti[len(corpi_x):])))
    m = statistics.mean(nulli)
    return (x, y), OrderedDict([('n_x', len(corpi_x)), ('n_y', len(corpi_y)), ('jsd', vera), ('jsd_nullo', m), ('A', vera / m)])


def posizione(occ, x, y, chiave, rnd):
    """Eccesso d'IM fra scelta (x/y) e una chiave di posizione; nullo: permutazione della scelta fra parole
    con lo stesso corpo."""
    dati = [(g, corpo, chiave(o)) for o in occ for g, corpo in [(o[0], o[1])] if g in (x, y)]
    vera = misure.informazione_mutua([(g, k) for g, _, k in dati])
    per = defaultdict(list)
    for i, (_, corpo, _) in enumerate(dati):
        per[corpo].append(i)
    nulli = []
    for _ in range(PERMUTAZIONI):
        gs = [g for g, _, _ in dati]
        for idx in per.values():
            v = [gs[i] for i in idx]
            rnd.shuffle(v)
            for i, g in zip(idx, v):
                gs[i] = g
        nulli.append(misure.informazione_mutua([(g, k) for g, (_, _, k) in zip(gs, dati)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    quote = OrderedDict()
    for k in sorted({k for _, _, k in dati}, key=str):
        sel = [g for g, _, kk in dati if kk == k]
        quote[str(k)] = round(sum(g == y for g in sel) / len(sel), 3)
    return OrderedDict([('n', len(dati)), ('eccesso', vera - m), ('z', (vera - m) / s if s else None), ('quota_%s' % y, quote)])


def main():
    occ = occorrenze()
    corpi = defaultdict(list)
    for g, corpo, _, _ in occ:
        corpi[g].append(corpo)
    segni = sorted(g for g, v in corpi.items() if len(v) >= MINIMO)
    lavori = [(x, y, corpi[x], corpi[y]) for x, y in combinations(segni, 2)]
    ris = OrderedDict([('segni', {g: len(corpi[g]) for g in segni})])
    coppie = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(indice, lavori):
            coppie['%s/%s' % k] = r
    ordinate = sorted(coppie.items(), key=lambda kv: kv[1]['A'])
    print('coppie (A = JSD / nullo), le prime 15:')
    for k, r in ordinate[:15]:
        print('  %-10s A %.2f (JSD %.3f, nullo %.3f, n %d/%d)' % (k, r['A'], r['jsd'], r['jsd_nullo'], r['n_x'], r['n_y']))
    candidate = [k for k, r in ordinate if r['A'] <= SOGLIA]
    print('candidate (A <= %.1f):' % SOGLIA, candidate)
    ris['coppie'] = OrderedDict(ordinate)
    ris['candidate'] = candidate
    da_provare = list(dict.fromkeys(candidate + ['ch/sh']))
    pos = OrderedDict()
    for k in da_provare:
        x, y = k.split('/')
        rnd = random.Random(SEME)
        pos[k] = OrderedDict([('riga', posizione(occ, x, y, lambda o: o[2], rnd)),
                              ('paragrafo', posizione(occ, x, y, lambda o: o[3], rnd))])
        print('  %-8s riga: eccesso %.4f (z %.1f) quote %s | prima riga del paragrafo: eccesso %.4f (z %.1f) quote %s' % (
            k, pos[k]['riga']['eccesso'], pos[k]['riga']['z'] or 0, dict(pos[k]['riga']['quota_%s' % y]),
            pos[k]['paragrafo']['eccesso'], pos[k]['paragrafo']['z'] or 0, dict(pos[k]['paragrafo']['quota_%s' % y])), flush=True)
    ris['posizione'] = pos
    chsh = coppie.get('ch/sh')
    ris['ch_sh_allografi'] = bool(chsh and chsh['A'] <= SOGLIA and (pos['ch/sh']['riga']['z'] or 0) > 4)
    print('ch/sh allografi:', ris['ch_sh_allografi'])
    with open(os.path.join(RISULTATI, 'e95_allografi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e95 — Allografi posizionali?', '',
           'A = JSD fra i corpi delle parole che cominciano con X e con Y, diviso per la JSD di %d divisioni casuali. '
           'Candidate: A ≤ %.1f. Dipendenza della scelta dalla posizione: eccesso d\'IM con nullo per permutazione fra parole '
           'con lo stesso corpo. Preregistrazione: `preregistrazioni/e95.md`.' % (DIVISIONI, SOGLIA), '',
           '| coppia | parole | A | JSD | nullo |', '|---|---|---|---|---|']
    for k, r in ordinate[:20]:
        out.append('| %s | %d / %d | %.2f | %.3f | %.3f |' % (k, r['n_x'], r['n_y'], r['A'], r['jsd'], r['jsd_nullo']))
    out += ['', '| coppia | posizione nella riga: eccesso (z) | quota del secondo segno per posizione | prima riga del paragrafo: eccesso (z) |',
            '|---|---|---|---|']
    for k, p in pos.items():
        y = k.split('/')[1]
        out.append('| %s | %.4f (%.1f) | %s | %.4f (%.1f) |' % (k, p['riga']['eccesso'], p['riga']['z'] or 0,
                                                            ', '.join('%s %.2f' % kv for kv in p['riga']['quota_%s' % y].items()),
                                                            p['paragrafo']['eccesso'], p['paragrafo']['z'] or 0))
    out += ['', 'ch/sh allografi secondo il criterio: **%s**.' % ('sì' if ris['ch_sh_allografi'] else 'no')]
    with open(os.path.join(RISULTATI, 'e95_allografi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
