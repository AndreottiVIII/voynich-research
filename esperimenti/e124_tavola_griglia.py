# -*- coding: utf-8 -*-
"""Esperimento 124: procedimento "tavola e griglia" alla Rugg (ricostruzione semplificata) sulle proprieta' di parola e
di riga.

Preregistrazione: preregistrazioni/e124.md. Scrive risultati/e124_tavola_griglia.json e .md.
"""
import json, os, random, sys
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
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
R = 40
BB = (0.15, 0.30)
INIZI = ('continua', 'riparte')
TT = (1, 4)
SEMI = (1, 2, 3)
D = misure.divisore(misure.GLIFI_EVA)


def parti(u):
    if len(u) >= 3 and u[0] == 'q' and u[1] == 'o':
        pre, resto = 'qo', u[2:]
    else:
        pre, resto = u[0], u[1:]
    if len(u) >= 4:
        suf, nuc = ''.join(resto[-2:]), ''.join(resto[:-2])
    else:
        suf, nuc = ''.join(resto[-1:]), ''.join(resto[:-1])
    return pre, nuc, suf


def distribuzioni():
    out = {}
    for lingua in ('A', 'B'):
        c = [Counter(), Counter(), Counter()]
        for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua)):
            for k, p in enumerate(parti(D(w))):
                c[k][p] += 1
        out[lingua] = [(list(x), list(x.values())) for x in c]
    return out


def struttura():
    pagine = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            pagine.setdefault(r.pagina, {'lingua': r.lingua or 'B', 'righe': []})['righe'].append((bool(r.inizio_par), len(ps)))
    return list(pagine.values())


def genera(strut, dist, b, inizio, T, seme):
    rnd = random.Random(seme)
    righe = []
    tavola = None
    for k, pag in enumerate(strut):
        if k % T == 0 or tavola is None:
            d = dist[pag['lingua'] if pag['lingua'] in dist else 'B']
            tavola = [[('' if rnd.random() < b else rnd.choices(d[c][0], d[c][1])[0]) for c in range(3)] for _ in range(R)]
            d1, d2 = rnd.randint(1, 4), rnd.randint(1, 4)
            p = rnd.randrange(R)
        for ini, n in pag['righe']:
            if inizio == 'riparte':
                p = rnd.randrange(R)
            riga = []
            tentativi = 0
            while len(riga) < n and tentativi < 10 * n:
                tentativi += 1
                w = tavola[p % R][0] + tavola[(p + d1) % R][1] + tavola[(p + d2) % R][2]
                p += 1
                if w:
                    riga.append(w)
            righe.append((ini, riga))
    return righe


def una(args):
    b, inizio, T, seme, strut, dist, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    rr = genera(strut, dist, b, inizio, T, seme)
    r = e106.misura(rr, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for _, ps in rr], 'eva'))
    r['A'] = a['senza identiche']['A']
    return (b, inizio, T, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    strut, dist = struttura(), distribuzioni()
    lavori = [(b, i, T, s, strut, dist, voy, soglia_ab, v, vb) for b in BB for i in INIZI for T in TT for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(una, lavori):
            per[k[:3]].append(r)
    medie = OrderedDict()
    for chiave in [(b, i, T) for b in BB for i in INIZI for T in TT]:
        gruppo = per[chiave]
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(m, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= m['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= m['bordo_fine'] <= 2 * vb[1]
        m['esiti'] = esiti
        m['completo'] = (sum(esiti.values()) >= 12 and m['R_riga'] < 0.1 and m['S1'] <= 0.7 and m['copia_prima'] <= 1.1
                         and m['copia_seconda'] > 1.15 and m['e94_pos2'] >= 1.2 and m['A'] >= 1.0)
        nome = 'b %.2f, %s, T %d' % chiave
        medie[nome] = m
        print('%-26s %d/18 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | h2 %.2f tipi %.3f uniche %.2f rip %.2f omog %.3f | completo %s' % (
            nome, sum(esiti.values()), m['R_riga'] or 0, m['S1'], m['copia_prima'], m['copia_seconda'], m['e94_pos2'], m['A'],
            m['h2'], m['tipi_su_parole'], m['hapax_34000'], m['identiche_vs_riga'], m['somiglianza_riga'], m['completo']), flush=True)
    with open(os.path.join(RISULTATI, 'e124_tavola_griglia.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e124 — Tavola e griglia (alla Rugg)', '', 'Ricostruzione semplificata, R = %d, medie su tre semi. Preregistrazione: '
           '`preregistrazioni/e124.md`. Voynich: R 0,006, S(1) 0,52, copia 1,03/1,47, e94 1,43, A 1,044.' % R, '',
           '| combinazione | pagella | R | S(1) | copia 1ª / 2ª | e94 | A | completo |', '|---|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f | %s |' % (nome, sum(m['esiti'].values()), m['R_riga'] or 0, m['S1'], m['copia_prima'],
                                                                            m['copia_seconda'], m['e94_pos2'], m['A'], 'sì' if m['completo'] else 'no'))
    out += ['', '| combinazione | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e124_tavola_griglia.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
