# -*- coding: utf-8 -*-
"""Esperimento 118: le proprieta' di riga per sezione, e testi dello stesso genere.

Preregistrazione: preregistrazioni/e118.md. Scrive risultati/e118_sezioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e83_evitamento_inizi as e83
import e110_alternanza as e110
import e116_ripetizioni as e116

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 118
D = e71.D
SEZIONI = OrderedDict([('erbario', {'H'}), ('biologia', {'B'}), ('farmacia', {'P'}), ('ricette', {'S'})])


def righe_sezione(sez, esclusa=False):
    out, par = [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if (r.sezione in sez) == esclusa or not r.parole:
            continue
        par += bool(r.inizio_par)
        out.append((r.pagina, par, bool(r.inizio_par), list(r.parole)))
    return out


def misura(righe, dividi, quale):
    """righe: (pagina, paragrafo, inizio, parole)."""
    rnd = random.Random(SEME)
    ris = OrderedDict([('righe', len(righe))])
    d, a = e74.coppie([(p, i, ps) for p, _, i, ps in righe], dividi)
    x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
    ris['R'] = y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None
    ris['R_z_a_capo'] = y['z']
    per = OrderedDict()
    for p, par, ini, ps in righe:
        w = ps[0] if trascrizione.pulita(ps[0]) else None
        per.setdefault(p, []).append((par, ini, w))
    s1 = e83.misura(per, 1, (lambda w: w[0]) if quale == 'lettere' else e83.primo_eva, random.Random(SEME))
    ris['S1'], ris['S1_z'] = s1['S'], s1['z']
    _, alt = e110.una(('x', [ps for _, _, _, ps in righe], quale))
    ris['A'], ris['A_z'] = alt['senza identiche']['A'], alt['senza identiche']['z']
    b = e71.una(('x', [(i, ps) for _, _, i, ps in righe], quale))[1]
    ris['bordo_inizio'] = b['jsd_inizio']['rapporto'] if isinstance(b['jsd_inizio'], dict) else None
    ris['bordo_fine'] = b['jsd_fine']['rapporto'] if isinstance(b['jsd_fine'], dict) else None
    ris['ripetizione'] = e116.rapporto_riga([[w for w in ps if trascrizione.pulita(w)] for _, _, _, ps in righe])
    return ris


def main():
    e83.PERMUTAZIONI = 300
    e110.RIMESCOLAMENTI = 100
    e71.RIMESCOLAMENTI = 100
    import e99_macer as e99
    import e73_bordo_interno as e73
    import e76_righe_piene as e76
    from e65_aperture_ricette import paragrafi_apicio
    t = OrderedDict()
    t['Voynich, tutto'] = (righe_sezione(set(), esclusa=True), 'eva')
    for nome, sez in SEZIONI.items():
        t['Voynich, ' + nome] = (righe_sezione(sez), 'eva')
    t['Voynich, altre sezioni'] = (righe_sezione({'H', 'B', 'P', 'S'}, esclusa=True), 'eva')
    caps = e99.capitoli()
    t['Macer (erbario in versi)'] = ([(k, k, j == 0, ps) for k, c in enumerate(caps) for j, ps in enumerate(c)], 'lettere')
    pl = e73.testi()['Plinio, a capo'][0]
    t['Plinio (erbario in prosa)'] = ([(i // 20, i // 20, i % 20 == 0, ps) for i, (_, ps) in enumerate(pl)], 'lettere')
    rs = e76.righe_sezione('S')
    voy = [w for _, _, ps in rs for w in ps if trascrizione.pulita(w)]
    import statistics as st
    larg = st.median(sum(len(D(w)) for w in ps) + len(ps) - 1 for _, _, ps in rs)
    api = paragrafi_apicio()
    media_a = sum(len(w) for v in api for w in v) / sum(len(v) for v in api)
    media_v = sum(len(D(w)) for w in voy) / len(voy)
    ra = e76.a_capo_per_voce(api, e71.lettere, larg * (media_a + 1) / (media_v + 1))
    t['Apicio (ricette)'] = ([(k, k, primo, ps) for k, primo, ps in ra], 'lettere')
    ris = OrderedDict()
    for nome, (rr, q) in t.items():
        r = misura(rr, e71.lettere if q == 'lettere' else D, q)
        ris[nome] = r
        print('%-28s righe %4d | R %s (z a capo %.1f) | S1 %.2f (z %.1f) | A %.3f (z %.1f) | bordo %.1f/%.1f | rip %.2f' % (
            nome, r['righe'], '%.2f' % r['R'] if r['R'] is not None else '-', r['R_z_a_capo'] or 0, r['S1'], r['S1_z'] or 0,
            r['A'], r['A_z'] or 0, r['bordo_inizio'] or 0, r['bordo_fine'] or 0, r['ripetizione'] or 0), flush=True)
    tutto = ris['Voynich, tutto']
    scosti = OrderedDict()
    for nome in [n for n in ris if n.startswith('Voynich, ') and n != 'Voynich, tutto']:
        r = ris[nome]
        f = []
        for chiave in ('S1_z', 'A_z'):
            zt, zs = tutto[chiave] or 0, r[chiave] or 0
            if abs(zt) > 4 and ((zs * zt < 0) or (abs(zs) < 1 and r['righe'] >= 300)):
                f.append(chiave)
        if r['R'] is not None and r['R'] > 0.3:
            f.append('R')
        scosti[nome] = f
    ris['sezioni_che_si_discostano'] = scosti
    print('sezioni che si discostano:', dict(scosti))
    with open(os.path.join(RISULTATI, 'e118_sezioni.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e118 — Sezione per sezione', '', 'Preregistrazione: `preregistrazioni/e118.md`.', '',
           '| testo | righe | R | S(1) (z) | A (z) | bordo ini/fin | ripetizione |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'righe' in r:
            out.append('| %s | %d | %s | %.2f (%.1f) | %.3f (%.1f) | %.1f / %.1f | %.2f |' % (
                nome, r['righe'], '%.2f' % r['R'] if r['R'] is not None else '–', r['S1'], r['S1_z'] or 0, r['A'], r['A_z'] or 0,
                r['bordo_inizio'] or 0, r['bordo_fine'] or 0, r['ripetizione'] or 0))
    out += ['', 'Sezioni che si discostano: %s.' % (', '.join('%s (%s)' % (k, ', '.join(v)) for k, v in scosti.items() if v) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e118_sezioni.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
