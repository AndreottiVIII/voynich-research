# -*- coding: utf-8 -*-
"""Esperimento 227: unioni e legame. (A) Due parole vicine unite danno una parola attestata piu' di quanto spieghi la
giuntura (stesso ultimo segno, stessi ultimi due segni)? (B) Il legame fra fine e inizio di parole vicine vale anche
nelle coppie di parole che compaiono una volta sola?

Preregistrazione: preregistrazioni/e227.md. Scrive risultati/e227_unioni_e_legame.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEME, ESTRAZIONI, QUOTA_SPEZZATE = 227, 200, 0.06


def generatore_pagine(seme=1):
    """Testo del generatore e192 (nu 0,4) con la struttura delle pagine vere, come nell'e211, su tutte le pagine."""
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    per = OrderedDict()
    for pag, _, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), seme, None):
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            per.setdefault(pag, []).append(ps)
    return list(per.values())


def spezza(pagine, attestate, rnd):
    """Controllo positivo: una parola di almeno 4 unita' su QUOTA_SPEZZATE si spezza in due parti attestate."""
    out = []
    for p in pagine:
        nuova = []
        for r in p:
            nr = []
            for w in r:
                u = D(w)
                if len(u) >= 4 and rnd.random() < QUOTA_SPEZZATE:
                    tagli = [c for c in range(1, len(u)) if ''.join(u[:c]) in attestate and ''.join(u[c:]) in attestate]
                    if tagli:
                        c = rnd.choice(tagli)
                        nr += [''.join(u[:c]), ''.join(u[c:])]
                        continue
                nr.append(w)
            nuova.append(nr)
        out.append(nuova)
    return out


def unioni(pagine, rnd):
    righe = [r for p in pagine for r in p]
    voc = Counter(w for r in righe for w in r)
    coppie = [(a, b) for r in righe for a, b in zip(r, r[1:])]
    U = sum(1 for a, b in coppie if voc[a + b]) / len(coppie)
    prime = [a for a, _ in coppie]
    fine = {a: tuple(D(a)) for a in set(prime)}
    gruppi = {1: defaultdict(list), 2: defaultdict(list)}
    for a in prime:
        for k in (1, 2):
            gruppi[k][fine[a][-k:]].append(a)
    out = OrderedDict([('coppie', len(coppie)), ('U', U)])
    for nome, k in (('N0', None), ('N1', 1), ('N2', 2)):
        valori = []
        for _ in range(ESTRAZIONI):
            n = 0
            for a, b in coppie:
                a2 = rnd.choice(prime) if k is None else rnd.choice(gruppi[k][fine[a][-k:]])
                n += voc[a2 + b] > 0
            valori.append(n / len(coppie))
        m, s = statistics.mean(valori), statistics.pstdev(valori)
        out[nome] = OrderedDict([('nullo', m), ('rapporto', U / m if m else None), ('z', (U - m) / s if s else None)])
    return out


def legame(pagine):
    """Eccesso d'informazione mutua fine -> inizio sulle parole interne (come misure.confine con solo_interne),
    su tutte le coppie e sulle sole coppie di parole che compaiono una volta."""
    righe = [[tuple(D(w)) for w in r] for p in pagine for r in p if len(r) > 1]
    righe = [r[1:-1] for r in righe if len(r) > 3]
    rnd = random.Random(0)
    mescolate = [[rnd.sample(r, len(r)) for r in righe] for _ in range(5)]

    def coppie(rr, solo_uniche):
        cp = [(a, b) for r in rr for a, b in zip(r, r[1:])]
        if solo_uniche:
            c = Counter(cp)
            cp = [x for x in cp if c[x] == 1]
        return [(a[-1], b[0]) for a, b in cp]

    out = OrderedDict()
    for nome, solo in (('tutte', False), ('uniche', True)):
        vera = misure.informazione_mutua(coppie(righe, solo))
        base = statistics.mean(misure.informazione_mutua(coppie(m, solo)) for m in mescolate)
        out[nome] = OrderedDict([('coppie', len(coppie(righe, solo))), ('vera', vera), ('nulla', base), ('eccesso', vera - base)])
    out['Q'] = out['uniche']['eccesso'] / out['tutte']['eccesso'] if out['tutte']['eccesso'] else None
    return out


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    attestate = set(trascrizione.parole(corrente))
    gen = generatore_pagine(1)
    testi = OrderedDict([('Voynich', pagine_voynich(corrente)),
                         ('generatore e192 (controllo negativo)', gen),
                         ('generatore con parole spezzate (controllo positivo)', spezza(gen, attestate, random.Random(SEME)))])
    ris = OrderedDict()
    for nome, pagine in testi.items():
        ris[nome] = OrderedDict([('A', unioni(pagine, random.Random(SEME))), ('B', legame(pagine))])
        a, b = ris[nome]['A'], ris[nome]['B']
        print('%s: U %.4f, U/N0 %.2f, U/N1 %.2f, U/N2 %.2f (z %.1f); legame %.3f, uniche %.3f, Q %.2f' % (
            nome, a['U'], a['N0']['rapporto'], a['N1']['rapporto'], a['N2']['rapporto'], a['N2']['z'],
            b['tutte']['eccesso'], b['uniche']['eccesso'], b['Q']), flush=True)
    v, neg, pos = (ris[n] for n in testi)
    valida_a = pos['A']['N2']['rapporto'] >= 1.3 and pos['A']['N2']['z'] > 3 and 0.85 <= neg['A']['N2']['rapporto'] <= 1.15
    r2, z2 = v['A']['N2']['rapporto'], v['A']['N2']['z']
    esito_a = ('non valido' if not valida_a else 'unioni spiegate dal legame' if r2 <= 1.15
               else 'un meccanismo a sé' if r2 >= 1.3 and z2 > 3 else 'incerto')
    valida_b = neg['B']['Q'] is not None and neg['B']['Q'] >= 0.8
    q = v['B']['Q']
    esito_b = 'non valido' if not valida_b else 'regola dei segni' if q >= 0.8 else 'coppie memorizzate' if q <= 0.5 else 'misto'
    ris['esiti'] = OrderedDict([('A', esito_a), ('B', esito_b)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e227_unioni_e_legame.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e227 — Unioni e legame: regola dei segni o coppie memorizzate?', '',
          'Preregistrazione: `preregistrazioni/e227.md`. %d estrazioni per nullo.' % ESTRAZIONI, '',
          '## A. Unioni contro nulli che conservano la giuntura', '',
          '| testo | coppie | U | U/N0 | U/N1 | U/N2 | z (N2) |', '|---|---|---|---|---|---|---|']
    for nome in testi:
        a = ris[nome]['A']
        md.append('| %s | %d | %.2f%% | %.2f | %.2f | %.2f | %.1f |' % (nome, a['coppie'], 100 * a['U'], a['N0']['rapporto'],
                                                                     a['N1']['rapporto'], a['N2']['rapporto'], a['N2']['z']))
    md += ['', 'Esito A: **%s**.' % esito_a, '', '## B. Legame su tutte le coppie e sulle coppie uniche', '',
           '| testo | coppie interne | legame (tutte) | coppie uniche | legame (uniche) | Q |', '|---|---|---|---|---|---|']
    for nome in testi:
        b = ris[nome]['B']
        md.append('| %s | %d | %.3f | %d | %.3f | %.2f |' % (nome, b['tutte']['coppie'], b['tutte']['eccesso'], b['uniche']['coppie'],
                                                            b['uniche']['eccesso'], b['Q']))
    md += ['', 'Esito B: **%s**.' % esito_b]
    open(os.path.join(RISULTATI, 'e227_unioni_e_legame.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(ris['esiti'])


if __name__ == '__main__':
    main()
