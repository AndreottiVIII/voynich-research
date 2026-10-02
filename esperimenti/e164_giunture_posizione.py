# -*- coding: utf-8 -*-
"""Esperimento 164: il legame fra fine e inizio di parole adiacenti resta se il nullo conserva la posizione nella riga,
la riga nel paragrafo e la sezione? (Feaster 2022 contro Smith e Ponzi 2019.)

Preregistrazione: preregistrazioni/e164.md. Scrive risultati/e164_giunture_posizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERMUTAZIONI, SEME, TETTO = 200, 164, 6


def righe_voynich():
    """(sezione, inizio paragrafo, fine paragrafo, parole) per le righe della ZL."""
    rr = [r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    out = []
    for k, r in enumerate(rr):
        fine = k + 1 == len(rr) or rr[k + 1].pagina != r.pagina or bool(rr[k + 1].inizio_par)
        out.append((r.sezione, bool(r.inizio_par), fine, list(r.parole)))
    return out


def righe_plinio():
    import e73_bordo_interno as e73
    base = e73.testi()['Plinio, a capo'][0]
    out = []
    for k, (ini, ps) in enumerate(base):
        fine = k + 1 == len(base) or base[k + 1][0]
        out.append((None, bool(ini), fine, list(ps)))
    return out


def strato(livello, sez, ini, fine, i, n):
    pos = (min(i, TETTO), min(n - 1 - i, TETTO))
    if livello == 1:
        return pos
    return pos + ('prima' if ini else ('ultima' if fine else 'altra'), sez)


def coppie(righe):
    out = []
    pulita = trascrizione.pulita
    for sez, ini, fine, ps in righe:
        n = len(ps)
        for i in range(1, n - 2):
            a, b = ps[i], ps[i + 1]
            if pulita(a) and pulita(b):
                out.append((e71.D(a)[-1], e71.D(b)[0], {l: strato(l, sez, ini, fine, i, n) for l in (1, 2)}))
    return out


def eccesso(cc, livello, rnd):
    vera = misure.informazione_mutua([(a, b) for a, b, _ in cc])
    gruppi = defaultdict(list)
    for k, (_, _, s) in enumerate(cc):
        gruppi[s[livello] if livello else 0].append(k)
    nulli = []
    for _ in range(PERMUTAZIONI):
        sec = [b for _, b, _ in cc]
        for idx in gruppi.values():
            vals = [sec[k] for k in idx]
            rnd.shuffle(vals)
            for k, v in zip(idx, vals):
                sec[k] = v
        nulli.append(misure.informazione_mutua([(a, s) for (a, _, _), s in zip(cc, sec)]))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('im', vera), ('nullo', m), ('eccesso', vera - m), ('z', (vera - m) / s if s else None), ('n', len(cc))])


def solo_posizione(righe, rnd):
    """Rimescola le parole fra tutte le righe, ma solo fra posizioni dello stesso strato N2."""
    posti = defaultdict(list)
    for r, (sez, ini, fine, ps) in enumerate(righe):
        for i in range(len(ps)):
            posti[strato(2, sez, ini, fine, i, len(ps))].append((r, i))
    nuove = [list(ps) for _, _, _, ps in righe]
    for pp in posti.values():
        parole = [righe[r][3][i] for r, i in pp]
        rnd.shuffle(parole)
        for (r, i), w in zip(pp, parole):
            nuove[r][i] = w
    return [(sez, ini, fine, ps) for (sez, ini, fine, _), ps in zip(righe, nuove)]


def main():
    rnd = random.Random(SEME)
    voy = righe_voynich()
    testi = OrderedDict([('Voynich', voy), ('controllo lingua: Plinio a capo', righe_plinio()),
                         ('controllo solo posizione: Voynich rimescolato negli strati', solo_posizione(voy, rnd))])
    ris = OrderedDict()
    for nome, rr in testi.items():
        cc = coppie(rr)
        r = OrderedDict((('N%d' % l), eccesso(cc, l, rnd)) for l in (0, 1, 2))
        for l in (1, 2):
            r['ritenzione_N%d' % l] = r['N%d' % l]['eccesso'] / r['N0']['eccesso'] if r['N0']['eccesso'] > 0 else None
        ris[nome] = r
        print('%-58s N0 %.4f (z %.0f) | N1 %.4f (z %.0f) | N2 %.4f (z %.0f) | ritenzione N1 %s N2 %s | n %d' % (
            nome, r['N0']['eccesso'], r['N0']['z'] or 0, r['N1']['eccesso'], r['N1']['z'] or 0, r['N2']['eccesso'], r['N2']['z'] or 0,
            '%.2f' % r['ritenzione_N1'] if r['ritenzione_N1'] is not None else '-', '%.2f' % r['ritenzione_N2'] if r['ritenzione_N2'] is not None else '-', r['N0']['n']), flush=True)
    v, p, s = ris['Voynich'], ris['controllo lingua: Plinio a capo'], ris['controllo solo posizione: Voynich rimescolato negli strati']
    valido = (p['ritenzione_N2'] or 0) >= 0.7 and (s['ritenzione_N2'] is None or s['ritenzione_N2'] < 0.2)
    rv = v['ritenzione_N2'] or 0
    esito = 'legame alle giunture vero' if (rv >= 0.5 and (v['N2']['z'] or 0) > 10) else ('legame posizionale' if rv < 0.2 else 'misto')
    ris['quota_N0_riprodotta_dalla_posizione'] = s['N0']['eccesso'] / v['N0']['eccesso'] if v['N0']['eccesso'] > 0 else None
    ris['controllo_valido'], ris['esito'] = valido, esito
    print('posizione sola riproduce %.0f%% dell\'eccesso N0 del Voynich | controllo valido: %s | esito: %s' % (100 * (ris['quota_N0_riprodotta_dalla_posizione'] or 0), valido, esito))
    with open(os.path.join(RISULTATI, 'e164_giunture_posizione.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e164 — Il legame alle giunture è un effetto di posizione?', '',
           'Eccesso d\'informazione mutua (bit) fra ultimo segno di una parola interna e primo della successiva, contro %d permutazioni: '
           'N0 fra tutte le coppie; N1 nello stesso strato di posizione nella riga; N2 anche riga nel paragrafo e sezione. '
           'Preregistrazione: `preregistrazioni/e164.md`.' % PERMUTAZIONI, '',
           '| testo | N0 | N1 | N2 | ritenzione N1 | ritenzione N2 |', '|---|---|---|---|---|---|']
    for nome in testi:
        r = ris[nome]
        out.append('| %s | %.4f (z %.0f) | %.4f (z %.0f) | %.4f (z %.0f) | %s | %s |' % (nome, r['N0']['eccesso'], r['N0']['z'] or 0, r['N1']['eccesso'], r['N1']['z'] or 0,
                   r['N2']['eccesso'], r['N2']['z'] or 0, '%.2f' % r['ritenzione_N1'] if r['ritenzione_N1'] is not None else '–',
                   '%.2f' % r['ritenzione_N2'] if r['ritenzione_N2'] is not None else '–'))
    out += ['', 'La sola posizione riproduce il %.0f%% dell\'eccesso N0 del Voynich.' % (100 * (ris['quota_N0_riprodotta_dalla_posizione'] or 0)), '',
            'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e164_giunture_posizione.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
