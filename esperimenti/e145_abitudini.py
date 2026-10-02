# -*- coding: utf-8 -*-
"""Esperimento 145: modello minimo ad "abitudini che derivano". Parole vere della pagina rimescolate fra le righe,
regola d'inizio riga (e131), cinque preferenze di grafia che derivano riga per riga (AR(1), ripartenza parziale a
ogni pagina). Proprieta' di riga e pagella.

Preregistrazione: preregistrazioni/e145.md. Scrive risultati/e145_abitudini.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import OrderedDict, defaultdict
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
import e129_griglia_ricca as e129
import e131_procedimento_riga as e131
import e135_stato_riga as e135
import e146_deriva_preferenze as e146
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEMI = (1, 2, 3)
CONFIG = [('rho %.2f, sigma %.1f' % (r, s), r, s, True) for r in (0.6, 0.85) for s in (0.4, 0.8)] + [
    ('solo regola d\'inizio (sigma 0)', 0.6, 0.0, True), ('riferimento: niente abitudini ne\' regola', 0.6, 0.0, False)]
GALLOWS = {'k', 't', 'p', 'f'}
SCELTE = (0, 1, 2, 4, 6)
VOY_R1 = 0.207


def pagine():
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            out.setdefault(r.pagina, {'lingua': r.lingua or 'B', 'righe': []})['righe'].append((bool(r.inizio_par), list(r.parole)))
    return out


def quote():
    righe = [('x', list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    acc = defaultdict(lambda: [0, 0])
    for f, _, st, v in e135.occorrenze(righe):
        if f in SCELTE:
            acc[(f, st[1:])][0] += v
            acc[(f, st[1:])][1] += 1
    return {k: (a + 0.5) / (n + 1) for k, (a, n) in acc.items()}


def riscrivi(ps, h, q, rnd):
    n = len(ps)
    out = []
    for i, w in enumerate(ps):
        if not trascrizione.pulita(w):
            out.append(w)
            continue
        u = D(w)
        pr = e135.pos_riga(i, n)
        L = len(u)

        def sceglie(f, ctx):
            p0 = q.get((f, ctx))
            if p0 is None:
                return None
            z = math.log(p0 / (1 - p0)) + h[f]
            return rnd.random() < 1 / (1 + math.exp(-z))
        for j, g in enumerate(u):
            dopo = u[j + 1] if j + 1 < L else '$'
            prima = u[j - 1] if j > 0 else '^'
            if g in ('ch', 'sh'):
                c = sceglie(0, (pr, j == 0, dopo))
                if c is not None:
                    u[j] = 'sh' if c else 'ch'
            elif g in ('k', 't'):
                c = sceglie(1, (prima, dopo, pr))
                if c is not None:
                    u[j] = 't' if c else 'k'
        if L >= 2 and u[-1] in ('l', 'r') and u[-2] in ('o', 'a'):
            c = sceglie(2, (u[-2], 0 if L <= 3 else 1 if L <= 5 else 2))
            if c is not None:
                u[-1] = 'r' if c else 'l'
        if L >= 3 and u[0] == 'q' and u[1] == 'o' and u[2] in GALLOWS:
            c = sceglie(4, (u[2], pr))
            if c is not None and not c:
                u = u[1:]
        elif L >= 2 and u[0] == 'o' and u[1] in GALLOWS:
            c = sceglie(4, (u[1], pr))
            if c:
                u = ['q'] + u
        if len(u) >= 2 and u[-1] == 'y' and u[-2] in ('d', 'e'):
            c = sceglie(6, (u[-3] if len(u) >= 3 else '^',))
            if c is not None:
                u[-2] = 'd' if c else 'e'
        out.append(''.join(u))
    return out


def genera(P, starts, q, rho, sigma, regola, seme):
    rnd = random.Random(seme)
    h = {f: 0.0 for f in SCELTE}
    righe = []
    for pag, d in P.items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in SCELTE:
            h[f] = (rho / 2) * h[f] + rnd.gauss(0, sigma)
        corpo = [w for _, ps in d['righe'] for w in (ps[1:] if regola else ps)]
        rnd.shuffle(corpo)
        it = iter(corpo)
        prima_sopra = None
        for ini, ps in d['righe']:
            for f in SCELTE:
                h[f] = rho * h[f] + rnd.gauss(0, sigma)
            n_corpo = len(ps) - 1 if regola else len(ps)
            riga = [next(it) for _ in range(n_corpo)]
            if regola:
                if ini:
                    w0 = rnd.choices(*starts[lingua][1])[0]
                else:
                    w0 = rnd.choices(*starts[lingua][0])[0]
                    for _ in range(10):
                        if prima_sopra is None or D(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                            break
                        w0 = rnd.choices(*starts[lingua][0])[0]
                riga = [w0] + riga
            if not riga:
                continue
            riga = riscrivi(riga, h, q, rnd) if sigma > 0 else riga
            if trascrizione.pulita(riga[0]):
                prima_sopra = D(riga[0])[0]
            righe.append((pag, ini, riga))
    return righe


def una(args):
    nome, rho, sigma, regola, seme, P, starts, q, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    rr = genera(P, starts, q, rho, sigma, regola, seme)
    righe = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(righe, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for ps in (x[1] for x in righe)], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, k = [], 0
    for pag, ini, ps in rr:
        k += ini
        par.append((pag, k, ps))
    res = e146.residui(par)
    g = e146.gruppi_coppie(par)
    r['r_righe_consecutive'] = e146.corr(g['dentro la pagina, d=1'], res)
    return (nome, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q = pagine(), e131.inizi(), quote()
    lavori = [(n, r, s, g, seme, P, starts, q, voy, soglia_ab, v, vb) for n, r, s, g in CONFIG for seme in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for (nome, seme), r in pool.imap(una, lavori):
            per[nome].append(r)
    medie = OrderedDict()
    for nome, *_ in CONFIG:
        gruppo = per[nome]
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
        mm['di_riga'] = e129.di_riga(mm)
        mm['basta_per_la_riga'] = (mm['S1'] <= 0.7 and (mm['R_riga'] or 1) < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3
                                   and abs(mm['r_righe_consecutive'] - VOY_R1) <= 0.07)
        medie[nome] = mm
        print('%-44s %d/18 | riga e pagina %d/12 | R %.2f S1 %.2f A %.3f | scelte per riga %.1f | r consecutive %.3f | copia %.2f/%.2f e94 %.2f | basta %s | mancano: %s' % (
            nome, sum(esiti.values()), sum(mm['di_riga'].values()), mm['R_riga'] or 0, mm['S1'], mm['A'], mm['scelte_per_riga'], mm['r_righe_consecutive'],
            mm['copia_prima'], mm['copia_seconda'], mm['e94_pos2'], mm['basta_per_la_riga'],
            ', '.join([p for p, x in esiti.items() if not x] + [p for p, x in mm['di_riga'].items() if not x and p not in esiti])), flush=True)
    basta = [n for n in medie if medie[n]['basta_per_la_riga']]
    print('combinazioni che bastano per la riga:', basta or 'nessuna')
    with open(os.path.join(RISULTATI, 'e145_abitudini.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'bastano': basta}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e145 — Un modello ad "abitudini che derivano"', '', 'Parole vere della pagina rimescolate fra le righe, regola d\'inizio (e131, a = 0,5), 5 preferenze AR(1) per riga con '
           'ripartenza parziale a ogni pagina. Medie su tre semi. Preregistrazione: `preregistrazioni/e145.md`. Voynich: S(1) 0,52, R 0,006, A 1,044, '
           'scelte per riga 5, r consecutive 0,207 (e146).', '',
           '| combinazione | pagella | riga e pagina | R | S(1) | A | scelte per riga | r consecutive | copia 1ª / 2ª | e94 | basta per la riga |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %d/12 | %.2f | %.2f | %.3f | %.1f | %.3f | %.2f / %.2f | %.2f | %s |' % (
            nome, sum(m['esiti'].values()), sum(m['di_riga'].values()), m['R_riga'] or 0, m['S1'], m['A'], m['scelte_per_riga'], m['r_righe_consecutive'],
            m['copia_prima'], m['copia_seconda'], m['e94_pos2'], 'sì' if m['basta_per_la_riga'] else 'no'))
    out += ['', '| combinazione | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if isinstance(m.get(e61.VALORI.get(p)), (int, float)) else '') for p in props)))
    out += ['', 'Combinazioni che bastano per la riga: **%s**.' % (', '.join(basta) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e145_abitudini.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
