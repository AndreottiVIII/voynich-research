# -*- coding: utf-8 -*-
"""Esperimento 131: procedimento "per riga" completo. Griglia dell'e129 (combinazione migliore) piu' colonna d'inizio,
evitamento dell'inizio della riga precedente e grafia ch/sh decisa per riga.

Preregistrazione: preregistrazioni/e131.md. Scrive risultati/e131_procedimento_riga.json e .md.
"""
import json, os, random, re, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e123b_origine_dipendenza as e123b
import e124_tavola_griglia as e124
import e129_griglia_ricca as e129
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
AA = (0.5, 0.9)
GRAFIA = (True, False)
SEMI = (1, 2, 3)
QUOTA_MEDIA = 0.30
D = misure.divisore(misure.GLIFI_EVA)


def base_e129():
    j = json.load(open(os.path.join(RISULTATI, 'e129_griglia_ricca.json'), encoding='utf-8'))
    m = re.match(r'R (\d+), m ([\d.]+), T (\d+)', j['migliore'])
    return int(m.group(1)), float(m.group(2)), int(m.group(3)), j['migliore']


def inizi():
    """Per lingua: parole d'inizio delle righe non di paragrafo e d'inizio paragrafo, con frequenza."""
    out = {}
    for lingua in ('A', 'B'):
        ini, par = Counter(), Counter()
        for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
            if r.parole and trascrizione.pulita(r.parole[0]):
                (par if r.inizio_par else ini)[r.parole[0]] += 1
        out[lingua] = ((list(ini), list(ini.values())), (list(par), list(par.values())))
    return out


def quote_sh():
    righe = [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    per = defaultdict(list)
    for o in e123b.occorrenze(righe):
        per[o['riga']].append(o['scelta'])
    return [sum(v) / len(v) for v in per.values() if len(v) >= 3]


def grafia(ps, q, rnd):
    n = len(ps)
    out = []
    for i, w in enumerate(ps):
        pos = 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'
        p = min(1.0, q * e106.SH[pos] / QUOTA_MEDIA)
        u = [('sh' if rnd.random() < p else 'ch') if g in ('ch', 'sh') else g for g in D(w)]
        out.append(''.join(u))
    return out


def genera(strut, pools, starts, quote, R, m, T, a, con_grafia, seme):
    rnd = random.Random(seme)
    righe = []
    celle = scarti = col_inizio = None
    for n, pag in enumerate(strut):
        lingua = pag['lingua'] if pag['lingua'] in pools else 'B'
        if n % T == 0 or celle is None:
            celle, scarti = e129.tavola(pools[lingua], R, rnd)
            col_inizio = [rnd.choices(*starts[lingua][0])[0] for _ in range(R)]
        prima_sopra = None
        for ini, quante in pag['righe']:
            k = rnd.randrange(e129.K)
            d1, d2 = scarti[k]
            s = rnd.randrange(R)
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = col_inizio[s]
                for _ in range(10):
                    if prima_sopra is None or D(w0)[0] != prima_sopra or rnd.random() >= a:
                        break
                    s = rnd.randrange(R)
                    w0 = col_inizio[s]
            riga = [w0]
            p = s + 1
            tentativi = 0
            while len(riga) < quante and tentativi < 10 * quante:
                tentativi += 1
                terne = [k, k, k]
                if rnd.random() < m:
                    terne[rnd.randrange(3)] = rnd.choice([x for x in range(e129.K) if x != k])
                w = celle[terne[0]][0][p % R] + celle[terne[1]][1][(p + d1) % R] + celle[terne[2]][2][(p + d2) % R]
                p += 1
                if w:
                    riga.append(w)
            if con_grafia:
                riga = grafia(riga, rnd.choice(quote), rnd)
            prima_sopra = D(riga[0])[0]
            righe.append((ini, riga))
    return righe


def una(args):
    a, con_grafia, seme, base, strut, pools, starts, quote, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    R, m, T = base
    rr = genera(strut, pools, starts, quote, R, m, T, a, con_grafia, seme)
    r = e106.misura(rr, voy, soglia_ab, v, vb)
    _, al = e110.una(('x', [ps for _, ps in rr], 'eva'))
    r['A'] = al['senza identiche']['A']
    return (a, con_grafia, seme), r


def main():
    R, m, T, nome_base = base_e129()
    print('base dall\'e129: %s' % nome_base, flush=True)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    strut, pools, starts, quote = e124.struttura(), e129.serbatoi(), inizi(), quote_sh()
    lavori = [(a, g, s, (R, m, T), strut, pools, starts, quote, voy, soglia_ab, v, vb) for a in AA for g in GRAFIA for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(una, lavori):
            per[k[:2]].append(r)
    medie = OrderedDict()
    for chiave in [(a, g) for a in AA for g in GRAFIA]:
        gruppo = per[chiave]
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        mm = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(mm, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= mm['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= mm['bordo_fine'] <= 2 * vb[1]
        mm['esiti'] = esiti
        mm['completo'] = (sum(esiti.values()) >= 12 and mm['R_riga'] < 0.1 and mm['S1'] <= 0.7 and mm['copia_prima'] <= 1.1
                          and mm['copia_seconda'] > 1.15 and mm['e94_pos2'] >= 1.2 and mm['A'] >= 1.0)
        mm['di_riga'] = e129.di_riga(mm)
        nome = 'a %.1f, grafia per riga %s' % (chiave[0], 'sì' if chiave[1] else 'no')
        medie[nome] = mm
        print('%-30s %d/18 | riga e pagina %d/12 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | bordo %.2f/%.2f | completo %s | mancano: %s' % (
            nome, sum(esiti.values()), sum(mm['di_riga'].values()), mm['R_riga'] or 0, mm['S1'], mm['copia_prima'], mm['copia_seconda'],
            mm['e94_pos2'], mm['A'], mm['bordo_inizio'], mm['bordo_fine'], mm['completo'],
            ', '.join([p for p, x in esiti.items() if not x] + [p for p, x in mm['di_riga'].items() if not x and p not in esiti])), flush=True)
    completi = [n for n in medie if medie[n]['completo']]
    migliore = max(medie, key=lambda n: (sum(medie[n]['di_riga'].values()), sum(medie[n]['esiti'].values())))
    tutte = list(e61.BANDE) + ['bordo di riga'] + ['chiusura R', 'S(1)', 'copia', 'e94', 'A']
    mai = [p for p in tutte if not any((medie[n]['esiti'].get(p) if p in medie[n]['esiti'] else medie[n]['di_riga'].get(p)) for n in medie)]
    print('completi: %s | migliore: %s | mai ottenute: %s' % (completi or 'nessuno', migliore, ', '.join(mai) or 'nessuna'))
    with open(os.path.join(RISULTATI, 'e131_procedimento_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump({'base': nome_base, 'medie': medie, 'completi': completi, 'migliore': migliore, 'mai_ottenute': mai}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e131 — Un procedimento "per riga" completo', '', 'Base: e129, %s; più colonna d\'inizio, evitamento con probabilità a, grafia ch/sh per riga. '
           'Medie su tre semi. Preregistrazione: `preregistrazioni/e131.md`. Voynich: R 0,006, S(1) 0,52, copia 1,03/1,47, e94 1,43, A 1,044.' % nome_base, '',
           '| combinazione | pagella | riga e pagina | R | S(1) | copia 1ª / 2ª | e94 | A | completo |', '|---|---|---|---|---|---|---|---|---|']
    for nome, mm in medie.items():
        out.append('| %s | %d/18 | %d/12 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f | %s |' % (nome, sum(mm['esiti'].values()), sum(mm['di_riga'].values()), mm['R_riga'] or 0,
                                                                                mm['S1'], mm['copia_prima'], mm['copia_seconda'], mm['e94_pos2'], mm['A'], 'sì' if mm['completo'] else 'no'))
    out += ['', '| combinazione | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, mm in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if mm['esiti'][p] else '· ') + ('%.3g' % mm[e61.VALORI[p]] if e61.VALORI.get(p) in mm else '') for p in props)))
    out += ['', 'Completi: **%s**. Migliore: **%s**. Mai ottenute: %s.' % (', '.join(completi) or 'nessuno', migliore, ', '.join(mai) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e131_procedimento_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
