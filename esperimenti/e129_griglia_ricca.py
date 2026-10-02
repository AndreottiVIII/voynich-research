# -*- coding: utf-8 -*-
"""Esperimento 129: tavola e griglia piu' ricca (tre terne di colonne riempite con parti di parole vere, griglia che
riparte a ogni riga e a volte si sposta di una colonna) sulle proprieta' di riga e di pagina.

Preregistrazione: preregistrazioni/e129.md. Scrive risultati/e129_griglia_ricca.json e .md.
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
import e124_tavola_griglia as e124
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
RR = (36, 72)
MM = (0.2, 0.5)
TT = (1, 4)
SEMI = (1, 2, 3)
B, K = 0.10, 3
D = misure.divisore(misure.GLIFI_EVA)
DI_RIGA = ('ripetizione', 'omogeneità', 'gradiente', 'profilo pagina', 'formule', 'bordo di riga', 'legame')


def serbatoi():
    out = {}
    for lingua in ('A', 'B'):
        c = Counter(w for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua)) if trascrizione.pulita(w))
        out[lingua] = (list(c), list(c.values()))
    return out


def tavola(pool, R, rnd):
    celle = [[[''] * R for _ in range(3)] for _ in range(K)]  # celle[k][parte][riga]
    scarti = []
    for k in range(K):
        d1 = rnd.randint(1, 4)
        d2 = rnd.randint(1, 4)
        scarti.append((d1, d2))
        for p in range(R):
            w = rnd.choices(pool[0], pool[1])[0]
            parti = e124.parti(D(w))
            for j, off in enumerate((0, d1, d2)):
                celle[k][j][(p + off) % R] = '' if rnd.random() < B else parti[j]
    return celle, scarti


def genera(strut, pools, R, m, T, seme):
    rnd = random.Random(seme)
    righe = []
    celle = scarti = None
    for n, pag in enumerate(strut):
        if n % T == 0 or celle is None:
            celle, scarti = tavola(pools[pag['lingua'] if pag['lingua'] in pools else 'B'], R, rnd)
        for ini, quante in pag['righe']:
            k = rnd.randrange(K)
            p = rnd.randrange(R)
            d1, d2 = scarti[k]
            riga, tentativi = [], 0
            while len(riga) < quante and tentativi < 10 * quante:
                tentativi += 1
                terne = [k, k, k]
                if rnd.random() < m:
                    terne[rnd.randrange(3)] = rnd.choice([x for x in range(K) if x != k])
                w = celle[terne[0]][0][p % R] + celle[terne[1]][1][(p + d1) % R] + celle[terne[2]][2][(p + d2) % R]
                p += 1
                if w:
                    riga.append(w)
            righe.append((ini, riga))
    return righe


def di_riga(m):
    e = m['esiti']
    out = OrderedDict((p, bool(e[p])) for p in DI_RIGA)
    out['chiusura R'] = (m['R_riga'] or 1) < 0.1
    out['S(1)'] = m['S1'] <= 0.7
    out['copia'] = m['copia_prima'] <= 1.1 and m['copia_seconda'] > 1.15
    out['e94'] = m['e94_pos2'] >= 1.2
    out['A'] = m['A'] >= 1.0
    return out


def una(args):
    R, m, T, seme, strut, pools, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    rr = genera(strut, pools, R, m, T, seme)
    r = e106.misura(rr, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for _, ps in rr], 'eva'))
    r['A'] = a['senza identiche']['A']
    return (R, m, T, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    strut, pools = e124.struttura(), serbatoi()
    lavori = [(R, m, T, s, strut, pools, voy, soglia_ab, v, vb) for R in RR for m in MM for T in TT for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(una, lavori):
            per[k[:3]].append(r)
    medie = OrderedDict()
    for chiave in [(R, m, T) for R in RR for m in MM for T in TT]:
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
        mm['di_riga'] = di_riga(mm)
        nome = 'R %d, m %.1f, T %d' % chiave
        medie[nome] = mm
        print('%-20s %d/18 | riga e pagina %d/12 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | h2 %.2f tipi %.3f uniche %.2f rip %.2f omog %.3f | completo %s | mancano: %s' % (
            nome, sum(esiti.values()), sum(mm['di_riga'].values()), mm['R_riga'] or 0, mm['S1'], mm['copia_prima'], mm['copia_seconda'],
            mm['e94_pos2'], mm['A'], mm['h2'], mm['tipi_su_parole'], mm['hapax_34000'], mm['identiche_vs_riga'], mm['somiglianza_riga'],
            mm['completo'], ', '.join(p for p, x in mm['di_riga'].items() if not x)), flush=True)
    migliore = max(medie, key=lambda n: (sum(medie[n]['di_riga'].values()), sum(medie[n]['esiti'].values())))
    mb = medie[migliore]
    avvicina = sum(mb['di_riga'].values()) >= 8 and (mb['R_riga'] or 1) < 0.1 and mb['A'] >= 1.0
    mai = [p for p in list(DI_RIGA) + ['chiusura R', 'S(1)', 'copia', 'e94', 'A'] if not any(medie[n]['di_riga'][p] for n in medie)]
    print('migliore: %s | avvicinamento %s | mai ottenute: %s' % (migliore, avvicina, ', '.join(mai)))
    with open(os.path.join(RISULTATI, 'e129_griglia_ricca.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'migliore': migliore, 'avvicinamento': avvicina, 'mai_ottenute': mai}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e129 — Tavola e griglia più ricca', '', 'Tre terne di colonne riempite con parti di parole vere, griglia che riparte a ogni riga, '
           'spostamento di colonna con probabilità m; medie su tre semi. Preregistrazione: `preregistrazioni/e129.md`. '
           'Voynich: R 0,006, S(1) 0,52, copia 1,03/1,47, e94 1,43, A 1,044.', '',
           '| combinazione | pagella | riga e pagina | R | S(1) | copia 1ª / 2ª | e94 | A | completo |', '|---|---|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %d/12 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f | %s |' % (nome, sum(m['esiti'].values()), sum(m['di_riga'].values()), m['R_riga'] or 0,
                                                                                m['S1'], m['copia_prima'], m['copia_seconda'], m['e94_pos2'], m['A'], 'sì' if m['completo'] else 'no'))
    out += ['', '| combinazione | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    out += ['', 'Migliore: **%s**. Avvicinamento: **%s**. Proprietà di riga e di pagina mai ottenute: %s.' % (migliore, 'sì' if avvicina else 'no', ', '.join(mai) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e129_griglia_ricca.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
