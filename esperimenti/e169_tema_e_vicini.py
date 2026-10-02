# -*- coding: utf-8 -*-
"""Esperimento 169: generatore e153 con tema piu' debole (theta) e penalita' beta per le parole quasi uguali alla
precedente; pagella, riga, T1-T4.

Preregistrazione: preregistrazioni/e169.md. Scrive risultati/e169_tema_e_vicini.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e162.D
GRIGLIA = [(t, b) for t in (0.0, 0.15, 0.3) for b in (1.0, 0.5)]
VOY_T3, VOY_T4R = -0.5, -4.0
_BETA = 1.0


def vicine(a, b):
    """Distanza di modifica <= 1 fra le unita' EVA di a e b."""
    u, v = D(a), D(b)
    if abs(len(u) - len(v)) > 1:
        return False
    if len(u) == len(v):
        return sum(x != y for x, y in zip(u, v)) <= 1
    if len(u) > len(v):
        u, v = v, u
    for i in range(len(v)):
        if v[:i] + v[i + 1:] == u:
            return True
    return False


def genera(P, starts, q, L, mod, seme, flusso):
    """e162.genera con temi a caso (flusso None) e penalita' _BETA per le candidate vicine alla parola precedente."""
    rnd = random.Random(seme)
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in P.items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        prima_sopra = None
        tema = [rnd.choice(pool) for _ in range(e153.K)]
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            tema = [rnd.choice(pool) for _ in tema]
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
                cand = [e153.variante(rnd.choice(tema) if rnd.random() < e162.THETA else rnd.choice(pool), e153.MU, mod, rnd) for _ in range(e152.CANDIDATE)]
                ultimo = D(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, D(x)[0]), 0.05) ** e153.LAM) if ultimo else 1.0
                    if pos == 1 and D(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if _BETA != 1.0 and trascrizione.pulita(riga[-1]) and trascrizione.pulita(x) and vicine(x, riga[-1]):
                        p *= _BETA
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga, h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = D(riga[0])[0]
            righe.append((pag, ini, riga))
    return righe


def una(args):
    global _BETA
    (theta, beta), seme, rest = args[0], args[1], args[2:]
    e162.THETA, _BETA = theta, beta
    e162.genera = genera
    _, r = e162.una(('x', seme, None) + tuple(rest))
    return (theta, beta), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    lavori = [(g, s, P, starts, q, L, voy, soglia_ab, v, vb) for g in GRIGLIA for s in e162.SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for g, r in pool.imap(una, lavori):
            per[g].append(r)
    medie = OrderedDict()
    for g in GRIGLIA:
        gruppo = per[g]
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(y.get(k), (int, float)) for y in gruppo)]
        mm = {k: sum(y[k] for y in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(mm, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= mm['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= mm['bordo_fine'] <= 2 * vb[1]
        mm['esiti'] = esiti
        R = mm['R_riga'] if mm.get('R_riga') is not None else 1
        mm['riga_riprodotta'] = (mm['S1'] <= 0.7 and R < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3 and abs(mm['r_righe_consecutive'] - e145.VOY_R1) <= 0.07)
        mm['corregge'] = (mm['riga_riprodotta'] and sum(esiti.values()) >= 9 and abs(mm.get('grezzo T3', 99) - VOY_T3) <= 2 and mm.get('ripulito T4', 99) < 0)
        medie['θ %g, β %g' % g] = mm
    base = medie['θ 0.3, β 1']['esiti']
    for n, mm in medie.items():
        mm['guadagnate'] = [k for k in base if mm['esiti'][k] and not base[k]]
        mm['perse'] = [k for k in base if base[k] and not mm['esiti'][k]]
        print('%-14s %d/18 | riga %s | T3 %.1f T4r %.1f | A %.3f | corregge %s | +%s -%s' % (n, sum(mm['esiti'].values()), mm['riga_riprodotta'],
              mm.get('grezzo T3', 0), mm.get('ripulito T4', 0), mm['A'], mm['corregge'], mm['guadagnate'], mm['perse']), flush=True)
    with open(os.path.join(RISULTATI, 'e169_tema_e_vicini.json'), 'w', encoding='utf-8') as fo:
        json.dump(medie, fo, ensure_ascii=False, indent=1, default=str)
    misure_t = [k for k in medie['θ 0.3, β 1'] if isinstance(k, str) and k.startswith(('grezzo', 'ripulito'))]
    out = ['# e169 — Tema di riga più debole e parole vicine che si evitano', '', 'Generatore e153 con temi a caso; medie su tre semi. Voynich: T3 grezzo −0,5, '
           'T4 ripulito −4,0. Preregistrazione: `preregistrazioni/e169.md`.', '',
           '| θ, β | pagella | riga | A | ' + ' | '.join(misure_t) + ' | corregge | guadagnate | perse |', '|---|---|---|---|' + '---|' * len(misure_t) + '---|---|---|']
    for n, mm in medie.items():
        out.append('| %s | %d/18 | %s | %.3f | %s | %s | %s | %s |' % (n, sum(mm['esiti'].values()), 'sì' if mm['riga_riprodotta'] else 'no', mm['A'],
                   ' | '.join('%.1f' % (mm.get(k) or 0) for k in misure_t), 'sì' if mm['corregge'] else 'no', ', '.join(mm['guadagnate']) or '–', ', '.join(mm['perse']) or '–'))
    with open(os.path.join(RISULTATI, 'e169_tema_e_vicini.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
