# -*- coding: utf-8 -*-
"""Esperimento 110: alternanza nella riga, A = somiglianza a distanza 2 / somiglianza a distanza 1 fra parole interne.

Preregistrazione: preregistrazioni/e110.md. Scrive risultati/e110_alternanza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_PAROLE = 110, 200, 6
D = misure.divisore(misure.GLIFI_EVA)


def sims(righe, con_identiche=False):
    s = {1: [0.0, 0], 2: [0.0, 0], 3: [0.0, 0]}
    for u in righe:
        for k in (1, 2, 3):
            for i in range(len(u) - k):
                if con_identiche or u[i] != u[i + k]:
                    s[k][0] += 1 - misure._dist_norm(u[i], u[i + k])
                    s[k][1] += 1
    return {k: (a / n if n else None) for k, (a, n) in s.items()}


def una(args):
    nome, righe, quale = args
    dividi = e71.lettere if quale == 'lettere' else D
    rr = [[tuple(dividi(w)) for w in ps[1:-1]] for ps in righe
          if len(ps) >= MIN_PAROLE and all(trascrizione.pulita(w) for w in ps)]
    out = OrderedDict([('righe', len(rr))])
    for etichetta, ci in (('senza identiche', False), ('con identiche', True)):
        s = sims(rr, ci)
        A = s[2] / s[1]
        rnd = random.Random(SEME)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            mes = []
            for u in rr:
                u = list(u)
                rnd.shuffle(u)
                mes.append(u)
            x = sims(mes, ci)
            nulli.append(x[2] / x[1])
        m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
        out[etichetta] = OrderedDict([('sim1', s[1]), ('sim2', s[2]), ('sim3', s[3]), ('A', A), ('nullo', m), ('z', (A - m) / sd if sd else None)])
    return nome, out


def righe_v(quale='ZL', lingua=None, mano=None):
    return [list(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi(quale), lingua=lingua, mano=mano) if r.parole]


def da_file(percorso):
    return [ps for _, ps in e71.righe_file(percorso)]


def main():
    import e98_versi_latini as e98
    import e99_macer as e99
    import e73_bordo_interno as e73
    C = e71.CACHE
    t = OrderedDict()
    t['Voynich ZL'] = (righe_v(), 'eva')
    t['Voynich IT'] = (righe_v('IT'), 'eva')
    t['Voynich, lingua A'] = (righe_v(lingua='A'), 'eva')
    t['Voynich, lingua B'] = (righe_v(lingua='B'), 'eva')
    for m in ('1', '2', '3'):
        t['Voynich, mano %s' % m] = (righe_v(mano=m), 'eva')
    for s in (19, 1, 2):
        t['Timm e Schinner, seme %d' % s] = (da_file(os.path.join(C, 'seme_%d' % s, 'generate', 'generated_text.txt')), 'eva')
    t['+ giunture (e23), seme 19'] = (da_file(os.path.join(C, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt')), 'eva')
    t['e51, seme 19'] = (da_file(os.path.join(C, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt')), 'eva')
    for s in (19, 1, 2):
        p = os.path.join(C, 'procedimento_versi', 'eta_1_seme_%d' % s, 'generate', 'generated_text.txt')
        if os.path.exists(p):
            t['base e106 (e69), seme %d' % s] = (da_file(p), 'eva')
    for chiave, nome in (('Latin', 'latina'), ('Italian', 'italiana'), ('English', 'inglese'), ('German', 'tedesca')):
        ps = lingue.parole(chiave)[:35000]
        t['Bibbia %s' % nome] = ([ps[i:i + 9] for i in range(0, len(ps), 9)], 'lettere')
    t['Ovidio, Metamorfosi'] = (e98.versi(e98.TESTI['Ovidio, Metamorfosi']), 'lettere')
    t['Macer'] = ([ps for c in e99.capitoli() for ps in c], 'lettere')
    t['Plinio, a capo'] = ([ps for _, ps in e73.testi()['Plinio, a capo'][0]], 'lettere')
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in t.items()]):
            ris[nome] = r
            x = r['senza identiche']
            print('%-30s righe %5d | sim1 %.4f sim2 %.4f sim3 %.4f | A %.3f (nullo %.3f, z %.1f) | con identiche A %.3f (z %.1f)' % (
                nome, r['righe'], x['sim1'], x['sim2'], x['sim3'], x['A'], x['nullo'], x['z'] or 0,
                r['con identiche']['A'], r['con identiche']['z'] or 0), flush=True)
    conf = all(ris[n]['senza identiche']['A'] > 1 and (ris[n]['senza identiche']['z'] or 0) > 4
               for n in ('Voynich ZL', 'Voynich IT', 'Voynich, lingua A', 'Voynich, lingua B'))
    gen = [n for n in ris if n.startswith(('Timm', '+ giunture', 'e51', 'base e106'))]
    contro = all(ris[n]['senza identiche']['A'] < 1 for n in gen)
    ris['alternanza_confermata'], ris['generatori_sotto_1'] = conf, contro
    print('alternanza confermata:', conf, '| tutti i generatori sotto 1:', contro)
    with open(os.path.join(RISULTATI, 'e110_alternanza.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e110 — Alternanza nella riga', '',
           'A = somiglianza fra parole interne a distanza 2 / a distanza 1 (coppie non identiche); nullo: parole interne '
           'rimescolate nella riga (%d volte). Preregistrazione: `preregistrazioni/e110.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | sim 1 | sim 2 | sim 3 | A | z | A con identiche |', '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        x = r['senza identiche']
        out.append('| %s | %d | %.4f | %.4f | %.4f | %.3f | %.1f | %.3f |' % (nome, r['righe'], x['sim1'], x['sim2'], x['sim3'], x['A'], x['z'] or 0, r['con identiche']['A']))
    out += ['', 'Alternanza confermata: **%s**; tutti i generatori sotto 1: **%s**.' % ('sì' if conf else 'no', 'sì' if contro else 'no')]
    with open(os.path.join(RISULTATI, 'e110_alternanza.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
