# -*- coding: utf-8 -*-
"""Esperimento 153: generatore di righe in ordine (e152) con tema piu' debole (theta), tema che passa alla riga dopo (c)
e preferenza ch/sh nella seconda parola.

Preregistrazione: preregistrazioni/e153.md. Scrive risultati/e153_righe_rifinite.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
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
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e152_righe_in_ordine as e152
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEMI = (1, 2, 3)
K, MU, LAM, BANCO = 3, 0.5, 1.0, 2.0
CONFIG = [('theta %.1f, c %.1f' % (t, c), t, c) for t in (0.3, 0.6) for c in (0.0, 0.5)]
_MOD = None


def variante(w, mu, mod, rnd):
    u = tuple(D(w))
    for _ in range(generatori.poisson(rnd, mu)):
        v = mod.modifica(u, rnd)
        if mod.valida(v):
            u = v
    return ''.join(u)


def genera(P, starts, q, L, theta, c, mod, seme):
    rnd = random.Random(seme)
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in P.items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        prima_sopra = None
        tema = [rnd.choice(pool) for _ in range(K)]
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            tema = [t if rnd.random() < c else rnd.choice(pool) for t in tema]
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or D(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            for pos in range(1, len(ps)):
                cand = [variante(rnd.choice(tema) if rnd.random() < theta else rnd.choice(pool), MU, mod, rnd) for _ in range(e152.CANDIDATE)]
                ultimo = D(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, D(x)[0]), 0.05) ** LAM) if ultimo else 1.0
                    if pos == 1 and D(x)[0] in ('ch', 'sh'):
                        p *= BANCO
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga, h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = D(riga[0])[0]
            righe.append((pag, ini, riga))
    return righe


def una(args):
    global _MOD
    nome, theta, c, seme, P, starts, q, L, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    if _MOD is None:
        _MOD = generatori.Modifiche(voy, D)
    rr = genera(P, starts, q, L, theta, c, _MOD, seme)
    righe = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(righe, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in e145.SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, kk = [], 0
    for pag, ini, ps in rr:
        kk += ini
        par.append((pag, kk, ps))
    r['r_righe_consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    return (nome, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    lavori = [(n, t, c, s, P, starts, q, L, voy, soglia_ab, v, vb) for n, t, c in CONFIG for s in SEMI]
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
        R = mm['R_riga'] if mm.get('R_riga') is not None else 1
        mm['riga_riprodotta'] = (mm['S1'] <= 0.7 and R < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3 and abs(mm['r_righe_consecutive'] - e145.VOY_R1) <= 0.07)
        mm['completo'] = (sum(esiti.values()) >= 12 and R < 0.1 and mm['S1'] <= 0.7 and mm['copia_prima'] <= 1.1 and mm['copia_seconda'] > 1.15
                          and mm['e94_pos2'] >= 1.2 and mm['A'] >= 1.0)
        medie[nome] = mm
        print('%-20s %d/18 | riga e pagina %d/12 | R %.2f S1 %.2f A %.3f | scelte %.1f | r %.3f | copia %.2f/%.2f e94 %.2f | omog %.3f | riga %s completo %s | mancano: %s' % (
            nome, sum(esiti.values()), sum(mm['di_riga'].values()), mm.get('R_riga') or 0, mm['S1'], mm['A'], mm['scelte_per_riga'], mm['r_righe_consecutive'],
            mm['copia_prima'], mm['copia_seconda'], mm['e94_pos2'], mm['somiglianza_riga'], mm['riga_riprodotta'], mm['completo'],
            ', '.join([p for p, x in esiti.items() if not x] + [p for p, x in mm['di_riga'].items() if not x and p not in esiti])), flush=True)
    riferimento = [n for n in medie if medie[n]['riga_riprodotta'] and medie[n]['completo']]
    migliore = max(medie, key=lambda n: (sum(medie[n]['esiti'].values()), sum(medie[n]['di_riga'].values())))
    print('modello di riferimento:', riferimento or 'nessuno', '| migliore per pagella:', migliore)
    with open(os.path.join(RISULTATI, 'e153_righe_rifinite.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'riferimento': riferimento, 'migliore': migliore}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e153 — Generatore di righe in ordine, rifinito', '', 'Come e152 (k 3, μ 0,5) con tema più debole (θ), tema che passa alla riga dopo (c), ch/sh favoriti in seconda '
           'posizione (×2). Medie su tre semi. Preregistrazione: `preregistrazioni/e153.md`.', '',
           '| combinazione | pagella | riga e pagina | R | S(1) | A | scelte | r | copia 1ª / 2ª | e94 | riga | completo |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %d/12 | %.2f | %.2f | %.3f | %.1f | %.3f | %.2f / %.2f | %.2f | %s | %s |' % (
            nome, sum(m['esiti'].values()), sum(m['di_riga'].values()), m.get('R_riga') or 0, m['S1'], m['A'], m['scelte_per_riga'], m['r_righe_consecutive'],
            m['copia_prima'], m['copia_seconda'], m['e94_pos2'], 'sì' if m['riga_riprodotta'] else 'no', 'sì' if m['completo'] else 'no'))
    out += ['', '| combinazione | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if isinstance(m.get(e61.VALORI.get(p)), (int, float)) else '') for p in props)))
    out += ['', 'Modello di riferimento (riga riprodotta e completo): **%s**. Migliore per pagella: **%s**.' % (', '.join(riferimento) or 'nessuno', migliore)]
    with open(os.path.join(RISULTATI, 'e153_righe_rifinite.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
